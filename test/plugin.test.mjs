import assert from "node:assert/strict";
import { existsSync } from "node:fs";
import { mkdtemp, mkdir, readFile, rm, stat, writeFile } from "node:fs/promises";
import { tmpdir, homedir } from "node:os";
import { join } from "node:path";
import { Context } from "@deepseek-ai/cordis";
import {
	anchorRoots,
	apply,
	clearCredentials,
	Config,
	credentialsPath,
	inject,
	name,
	nextTriggerDate,
	parseAnchorDates,
	readCredentials,
	renderAnchorHits,
	runAnchorCheck,
	scanAnchorDir,
	validateTushareToken,
	writeCredentials,
} from "../lib/index.js";

const MS_PER_DAY = 86_400_000;
const pad = (n) => String(n).padStart(2, "0");
const iso = (d) => `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
const md = (d) => `${d.getMonth() + 1}/${d.getDate()}`;

// ── 1. 纯函数：日期解析 ────────────────────────────────────────────────────
{
	const today = new Date(2026, 7, 13); // 2026-08-13
	assert.deepEqual(
		parseAnchorDates("更新触发器：2026-08-25 半年报；9/1 另一次", today).map(iso),
		["2026-08-25", "2026-09-01"],
	);
	// 错过触发日后保持 overdue，不得静默滚到下一年或消失
	assert.deepEqual(parseAnchorDates("8/12 已过期", today).map(iso), ["2026-08-12"]);
	assert.deepEqual(parseAnchorDates("2026-08-12 已过期", today).map(iso), ["2026-08-12"]);
	assert.deepEqual(parseAnchorDates("2026/08/25", today).map(iso), ["2026-08-25"]);
	assert.equal(iso(nextTriggerDate("## 锚 1\n- 更新触发器：2026-08-12 半年报", today)), "2026-08-12");
	// JS Date 会自动归一化 2/31；解析器必须拒绝这种伪日期
	assert.deepEqual(parseAnchorDates("2026-02-31", today), []);
	// 中文日期
	assert.deepEqual(parseAnchorDates("2026年8月25日 中报", today).map(iso), ["2026-08-25"]);
	// 失效锚不参与
	const text = `## 锚 1：有效\n- 更新触发器：2026-08-25\n\n## 锚 2：[失效] 已推翻\n- 更新触发器：2026-08-13\n`;
	assert.equal(iso(nextTriggerDate(text, today)), "2026-08-25");
}

// ── 2. 纯函数：扫描与渲染 ──────────────────────────────────────────────────
{
	const dir = await mkdtemp(join(tmpdir(), "resanity-scan-"));
	try {
		await mkdir(join(dir, "anchors"));
		const due = new Date(); // 今天 → due
		const overdue = new Date(Date.now() - 2 * MS_PER_DAY); // 前天 → 仍需提醒
		const near = new Date(Date.now() + 2 * MS_PER_DAY); // 后天 → near（窗口 3）
		const far = new Date(Date.now() + 20 * MS_PER_DAY); // 20 天后 → 窗口外
		await writeFile(join(dir, "anchors", "算力链.md"), `## 锚 1\n\n- 更新触发器：${md(due)} 半年报\n`);
		await writeFile(join(dir, "anchors", "逾期锚.md"), `## 锚 1\n\n- 更新触发器：${iso(overdue)} 财报\n`);
		await writeFile(join(dir, "anchors", "光伏.md"), `## 锚 1\n\n- 更新触发器：${iso(near)} 互动易\n`);
		await writeFile(join(dir, "anchors", "远方.md"), `## 锚 1\n\n- 更新触发器：${iso(far)} 远期\n`);
		await writeFile(join(dir, "anchors", "_template.md"), `## 锚 1\n\n- 更新触发器：${md(due)}\n`);
		await writeFile(join(dir, "anchors", "example.md"), `## 锚 1\n\n- 更新触发器：${md(due)}\n`);
		await writeFile(join(dir, "anchors", "index.md"), `# 仪表盘\n\n| 主题 | 活跃锚数 |\n`);
		await writeFile(join(dir, "anchors", "README.md"), `# 说明\n`);

		const hits = await scanAnchorDir(join(dir, "anchors"), { windowDays: 3 });
		assert.equal(hits.length, 3, "应扫到 overdue + due + near，模板/示例/索引跳过");
		assert.equal(hits.filter((h) => h.kind === "due").length, 2);
		assert.equal(hits.filter((h) => h.kind === "near").length, 1);

		const lines = renderAnchorHits(hits);
		assert.ok(lines.some((l) => l.includes("锚触发已到") && l.includes("算力链")));
		assert.ok(lines.some((l) => l.includes("锚触发已到") && l.includes("逾期锚")));
		assert.ok(lines.some((l) => l.includes("锚触发临近") && l.includes("光伏") && l.includes("还有 2 天")));
		assert.ok(!lines.some((l) => l.includes("远方")), "窗口外不提醒");
	} finally {
		await rm(dir, { recursive: true, force: true });
	}
}

// ── 3. 插件装配：provider / 命令 / 定时器 ──────────────────────────────────
{
	const root = new Context();
	const providers = [];
	const commands = [];
	const intervals = [];
	const timeouts = [];
	const workdir = await mkdtemp(join(tmpdir(), "resanity-plugin-"));
	try {
		await mkdir(join(workdir, "anchors"));
		const due = new Date();
		await writeFile(join(workdir, "anchors", "算力链.md"), `## 锚 1\n\n- 更新触发器：${md(due)} 半年报\n`);
		const near = new Date(Date.now() + 2 * MS_PER_DAY);
		await writeFile(join(workdir, "anchors", "光伏.md"), `## 锚 1\n\n- 更新触发器：${iso(near)} 互动易\n`);

		root.provide("skills", { registerProvider: (factory) => providers.push(factory()) });
		root.provide("timer", {
			interval: (fn, ms) => intervals.push({ fn, ms }),
			timeout: (fn, ms) => timeouts.push({ fn, ms }),
		});
		root.provide("commands", { register: (def) => commands.push(def) });
		let agentList = [{ session: { header: { cwd: workdir } } }];
		root.provide("agents", { list: () => agentList });

		await root.plugin({ apply, inject, name, Config }, {
			checkIntervalHours: 6,
			reminderWindowDays: 3,
			systemNotifications: false,
			anchorsDirs: [],
		});

		// provider
		assert.equal(providers.length, 1);
		const candidates = await providers[0].list();
		assert.equal(candidates.length, 1);
		assert.equal(candidates[0].name, "resanity");
		assert.equal(candidates[0].rank, 600);
		assert.ok(candidates[0].description.includes("散户研究心法"));
		const definition = await providers[0].get(candidates[0]);
		assert.ok(definition.content.startsWith("# reSanity"), "正文不含 frontmatter");
		assert.ok(definition.content.includes("路径约定"));
		assert.ok(definition.content.includes("否定承重主张必须直读裁决文件"));
		assert.ok(definition.content.includes("闭合对象只能是声明过的公开检索边界"));
		assert.ok(definition.content.includes("否定结论使用双边界契约"));
		assert.ok(definition.content.includes("检索结论：截至 [as-of]"));
		assert.ok(definition.content.includes("现实边界：这不证明现实中不存在"));
		assert.ok(definition.content.includes("沉默不是官方否定"));
		assert.ok(definition.content.includes("下一份文件继续沉默称为“第二次官方否定”"));
		assert.ok(definition.content.includes("它不得猜测或自报 token"));
		assert.equal(existsSync(join(definition.resourceBase.path, "scripts")), true);
		assert.equal(existsSync(join(definition.resourceBase.path, "SKILL.md")), true);

		// 命令
		const command = commands.find((c) => c.name === "resanity-check");
		assert.ok(command, "/resanity-check 已注册");
		const result = await command.handler({
			rawInput: "",
			agent: { session: { header: { cwd: workdir } } },
		});
		assert.equal(result.kind, "success");
		assert.ok(result.text.includes("锚触发已到"), result.text);
		assert.ok(result.text.includes("锚触发临近"), result.text);
		agentList = [];
		const empty = await command.handler({ rawInput: "", agent: { session: { header: { cwd: join(workdir, "nope") } } } });
		assert.equal(empty.text, "⚓ 锚体检：无到期触发器");
		agentList = [{ session: { header: { cwd: workdir } } }];

		// 定时器注册与执行逻辑
		assert.equal(intervals.length, 1);
		assert.equal(intervals[0].ms, 6 * 3_600_000);
		assert.equal(timeouts.length, 1);
		assert.equal(timeouts[0].ms, 30_000);
		await intervals[0].fn(); // 不抛异常；systemNotifications: false 不弹通知
		const checkCtx = { get: (service) => (service === "agents" ? { list: () => agentList } : undefined) };
		const check = await runAnchorCheck(checkCtx, {
			anchorsDirs: [],
			reminderWindowDays: 3,
		});
		assert.equal(check.hits.length, 2);
		assert.ok(check.roots.includes(join(workdir, "anchors")));

		// anchorRoots：env + config + 会话 cwd 三来源去重
		const roots = anchorRoots({
			env: { RESANITY_ANCHORS: "/tmp/from-env" },
			config: { anchorsDirs: ["/tmp/from-env"] },
			agents: { list: () => [{ session: { header: { cwd: "/tmp/from-session" } } }] },
		});
		assert.deepEqual(roots, ["/tmp/from-env", "/tmp/from-session/anchors"]);
	} finally {
		await rm(workdir, { recursive: true, force: true });
	}
}

// ── 4. DSH 失败路径回归提示 ────────────────────────────────────────────────
{
	const prompt = await readFile(
		new URL("../validation/dsh-pilot/prompts/C04F-T-unreadable.md", import.meta.url),
		"utf8",
	);
	assert.ok(prompt.includes("./decision-document.pdf"));
	assert.ok(prompt.includes("禁止 Web、外部检索和模型记忆补全"));
	assert.ok(prompt.includes("不得重试同一路径或换命令重复读取"));
	assert.ok(prompt.includes("底层血缘仍为 `[E2]`"));
}

// ── 5. tushare 凭据：纯函数 + 命令全路径 ───────────────────────────────────
{
	// credentialsPath 解析优先级
	assert.equal(credentialsPath({ RESANITY_CREDENTIALS: "/x/y.json" }), "/x/y.json");
	assert.equal(
		credentialsPath({ DSH_HOME: "/home/u/.dsh" }),
		"/home/u/.dsh/resanity/credentials.json",
	);
	assert.equal(
		credentialsPath({ DSH_HOME: undefined }),
		join(homedir(), ".dsh", "resanity", "credentials.json"),
	);

	// 在线校验：网络失败 → NETWORK
	const realFetch = globalThis.fetch;
	const TOKEN = "a".repeat(40);
	const dir = await mkdtemp(join(tmpdir(), "resanity-tushare-"));
	const credEnv = { RESANITY_CREDENTIALS: join(dir, "creds", "credentials.json") };
	try {
		globalThis.fetch = async () => {
			throw new Error("offline");
		};
		assert.equal((await validateTushareToken(TOKEN)).code, "NETWORK");

		// 写入/读取/清除
		const path = await writeCredentials(TOKEN, credEnv);
		assert.equal(path, credEnv.RESANITY_CREDENTIALS);
		const mode = (await stat(path)).mode & 0o777;
		assert.equal(mode, 0o600, "凭据文件 600 权限");
		assert.equal((await readCredentials(credEnv)).token, TOKEN);
		await clearCredentials(credEnv);
		assert.equal((await readCredentials(credEnv)).token, "");
	} finally {
		globalThis.fetch = realFetch;
		await rm(dir, { recursive: true, force: true });
	}
}

// ── 6. 插件装配：tushare 命令 ───────────────────────────────────────────────
{
	const root = new Context();
	const commands = [];
	root.provide("skills", { registerProvider: () => {} });
	root.provide("timer", { interval: () => {}, timeout: () => {} });
	root.provide("commands", { register: (def) => commands.push(def) });
	await root.plugin({ apply, inject, name, Config }, {});

	const tushare = commands.find((c) => c.name === "resanity-tushare");
	assert.ok(tushare, "/resanity-tushare 已注册");
	assert.equal(tushare.recordInput, false, "token 不进 command/run 日志");

	const realFetch = globalThis.fetch;
	const savedCredEnv = process.env.RESANITY_CREDENTIALS;
	const dir = await mkdtemp(join(tmpdir(), "resanity-tushare-cmd-"));
	process.env.RESANITY_CREDENTIALS = join(dir, "credentials.json");
	const TOKEN = "a".repeat(40);
	const agent = { session: { header: { cwd: dir } } };
	try {
		// 空输入 / 未知子命令：给出行级用法
		const empty = await tushare.handler({ rawInput: "", agent });
		assert.ok(empty.text.includes("缺少子命令"), empty.text);
		const unknown = await tushare.handler({ rawInput: "help", agent });
		assert.ok(unknown.text.includes("不认识的子命令「help」"), unknown.text);

		// set：不校验长度/格式，保存后自动在线校验
		globalThis.fetch = async () =>
			new Response(JSON.stringify({ code: 0 }), {
				status: 200,
				headers: { "Content-Type": "application/json" },
			});
		const saved = await tushare.handler({ rawInput: `set ${TOKEN}`, agent });
		assert.equal(saved.kind, "success");
		assert.ok(saved.text.includes("自动在线校验通过"), saved.text);
		assert.ok(saved.text.includes("…aaaa"), saved.text);
		assert.ok(!saved.text.includes(TOKEN), "完整 token 不得出现在输出");

		// 非 40 位 hex 也原样保存（无格式门槛）
		const odd = await tushare.handler({ rawInput: "set not-a-token", agent });
		assert.equal(odd.kind, "success", odd.text);
		assert.equal((await readCredentials()).token, "not-a-token");

		// 仅去掉不可见零宽字符，可见字符（引号/横线）原样保留
		const noisy = `set "aaaa-\u200ba${"b".repeat(35)}"`;
		const cleaned = await tushare.handler({ rawInput: noisy, agent });
		assert.equal(cleaned.kind, "success");
		assert.ok(cleaned.text.includes("不可见字符"), cleaned.text);
		assert.equal((await readCredentials()).token, `"aaaa-a${"b".repeat(35)}"`);

		// 恢复 TOKEN，供 status/test 断言
		await tushare.handler({ rawInput: `set ${TOKEN}`, agent });

		// status 脱敏
		const status = await tushare.handler({ rawInput: "status", agent });
		assert.ok(status.text.includes("已配置（…aaaa）"), status.text);
		assert.ok(!status.text.includes(TOKEN));

		// test 通过
		const test = await tushare.handler({ rawInput: "test", agent });
		assert.ok(test.text.includes("在线校验通过"), test.text);

		// 自动在线校验失败：已保存 + 明确反馈（error）
		globalThis.fetch = async () =>
			new Response(JSON.stringify({ code: -2002, msg: "token不正确" }), {
				status: 200,
				headers: { "Content-Type": "application/json" },
			});
		const warned = await tushare.handler({ rawInput: `set ${"b".repeat(40)}`, agent });
		assert.equal(warned.kind, "error");
		assert.ok(warned.text.includes("自动在线校验未通过"), warned.text);
		assert.ok(warned.text.includes("-2002"), warned.text);

		// 网络不可用：已保存 + 提示稍后 test
		globalThis.fetch = async () => {
			throw new Error("offline");
		};
		const offline = await tushare.handler({ rawInput: `set ${"c".repeat(40)}`, agent });
		assert.equal(offline.kind, "success");
		assert.ok(offline.text.includes("未能在线校验"), offline.text);

		// clear → status 未配置
		const cleared = await tushare.handler({ rawInput: "clear", agent });
		assert.ok(cleared.text.includes("已清除"));
		const after = await tushare.handler({ rawInput: "status", agent });
		assert.ok(after.text.includes("未配置"));
	} finally {
		globalThis.fetch = realFetch;
		if (savedCredEnv === undefined) delete process.env.RESANITY_CREDENTIALS;
		else process.env.RESANITY_CREDENTIALS = savedCredEnv;
		await rm(dir, { recursive: true, force: true });
	}
}

console.log("resanity plugin tests: all passed");

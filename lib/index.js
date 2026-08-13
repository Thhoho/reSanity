import { chmod, mkdir, readFile, readdir, rm, writeFile } from "node:fs/promises";
import { spawnSync } from "node:child_process";
import { delimiter, dirname, join, resolve } from "node:path";
import { homedir } from "node:os";
import { fileURLToPath } from "node:url";
import z from "@deepseek-ai/schemastery";
import { BUNDLED_SKILL_RANK } from "@deepseek-ai/dsh-skill";

/**
 * reSanity 散修 — DSH plugin.
 *
 * Three capabilities, each activated only when its service is composed:
 *   1. Bundled `resanity` skill provider on `ctx.skills` (rank 600, so any
 *      local/project copy of the skill shadows it by name).
 *   2. `ctx.timer` anchor check: scans every live session's `<cwd>/anchors`
 *      plus configured roots, notifies (system + log) when a trigger is due
 *      or within the reminder window.
 *   3. `/resanity-check` command on `ctx.commands`: on-demand anchor check
 *      for the receiving session's workspace.
 *
 * @module resanity
 */

const name = "resanity";
const inject = ["skills"];
const PROVIDER_NAME = "resanity";

const SKILL_FILE = new URL("../SKILL.md", import.meta.url);
const RESOURCE_BASE = {
	kind: "directory",
	path: fileURLToPath(new URL("..", import.meta.url)),
};

const Config = z.object({
	/** Hours between background anchor checks. */
	checkIntervalHours: z.number().default(6),
	/** Days before a trigger to start reminding. */
	reminderWindowDays: z.number().default(3),
	/** Send OS notifications (macOS osascript / Linux notify-send). */
	systemNotifications: z.boolean().default(true),
	/** Extra anchor roots; live-session `<cwd>/anchors` and `$RESANITY_ANCHORS` are always scanned. */
	anchorsDirs: z.array(z.string()).default([]),
});

// ── skill provider ─────────────────────────────────────────────────────────

const SKIP_NAMES = new Set(["README.md", "index.md", "example.md"]);

/**
 * Parse the shipped SKILL.md frontmatter with a minimal extraction instead of
 * a YAML dependency: the file is package-controlled and single-line scalars.
 * Returns null when the frontmatter cannot be trusted.
 */
async function readSkillDefinition() {
	const raw = await readFile(SKILL_FILE, "utf8");
	const match = raw.match(/^---\r?\n([\s\S]*?)\r?\n---\r?\n?/);
	if (!match) return null;
	const frontmatter = match[1];
	const nameMatch = frontmatter.match(/^name:\s*(\S+)\s*$/mu);
	const descriptionMatch = frontmatter.match(/^description:\s*(.+)$/mu);
	if (!nameMatch || !descriptionMatch) return null;
	return {
		name: nameMatch[1],
		description: descriptionMatch[1].trim(),
		content: raw.slice(match[0].length).replace(/^\r?\n+/, ""),
	};
}

const provider = {
	name: PROVIDER_NAME,
	async list() {
		const definition = await readSkillDefinition();
		if (!definition) return [];
		return [
			{
				name: definition.name,
				description: definition.description,
				invocation: { modelInvocable: true, userInvocable: true },
				provider: PROVIDER_NAME,
				source: "bundled",
				resourceBase: RESOURCE_BASE,
				rank: BUNDLED_SKILL_RANK,
				locator: SKILL_FILE,
			},
		];
	},
	async get(_candidate) {
		const definition = await readSkillDefinition();
		if (!definition) throw new TypeError("resanity SKILL.md frontmatter is unreadable");
		return {
			name: definition.name,
			description: definition.description,
			invocation: { modelInvocable: true, userInvocable: true },
			provider: PROVIDER_NAME,
			source: "bundled",
			resourceBase: RESOURCE_BASE,
			content: definition.content,
		};
	},
};

// ── anchor trigger scan (port of tools/anchor_check.py) ────────────────────

const DATE_PATTERNS = [
	/(20\d{2})[-/](\d{1,2})[-/](\d{1,2})/gu,
	/(20\d{2})年(\d{1,2})月(\d{1,2})日/gu,
	/(?<![0-9])(\d{1,2})\/(\d{1,2})(?![0-9/])/gu,
];

function startOfDay(today) {
	return new Date(today.getFullYear(), today.getMonth(), today.getDate());
}

/** Dates in `text` that fall on or after today (bare M/D rolls to the next occurrence). */
export function parseAnchorDates(text, today = new Date()) {
	const found = [];
	for (const pattern of DATE_PATTERNS) {
		for (const match of text.matchAll(pattern)) {
			let year;
			let month;
			let day;
			if (pattern === DATE_PATTERNS[2]) {
				month = Number(match[1]);
				day = Number(match[2]);
				year =
					month > today.getMonth() + 1 ||
					(month === today.getMonth() + 1 && day >= today.getDate())
						? today.getFullYear()
						: today.getFullYear() + 1;
			} else {
				year = Number(match[1]);
				month = Number(match[2]);
				day = Number(match[3]);
			}
			const parsed = new Date(year, month - 1, day);
			if (Number.isNaN(parsed.getTime())) continue;
			if (parsed >= startOfDay(today)) found.push(parsed);
		}
	}
	return found;
}

/** Earliest trigger date in one anchor file, or null. */
export function nextTriggerDate(text, today = new Date()) {
	const blocks = text.split(/^## /mu).slice(1);
	const dates = [];
	for (const block of blocks) {
		const header = block.split("\n")[0] ?? "";
		if (header.includes("失效")) continue;
		const trigger = block.match(/更新触发器[:：]([^\n]*)/u);
		if (!trigger) continue;
		dates.push(...parseAnchorDates(trigger[1], today));
	}
	if (dates.length === 0) return null;
	return new Date(Math.min(...dates.map((date) => date.getTime())));
}

/** `{ theme, when, days, kind: "due" | "near" }` hits for one anchors directory. */
export async function scanAnchorDir(dir, { today = new Date(), windowDays = 3 } = {}) {
	let entries;
	try {
		entries = await readdir(dir, { withFileTypes: true });
	} catch {
		return [];
	}
	const hits = [];
	for (const entry of entries) {
		if (!entry.isFile() || !entry.name.endsWith(".md")) continue;
		if (SKIP_NAMES.has(entry.name) || entry.name.startsWith("_")) continue;
		let text;
		try {
			text = await readFile(join(dir, entry.name), "utf8");
		} catch {
			continue;
		}
		const when = nextTriggerDate(text, today);
		if (when === null) continue;
		const theme = entry.name.replace(/\.md$/u, "");
		const days = Math.round((when.getTime() - startOfDay(today).getTime()) / 86_400_000);
		if (days <= 0) hits.push({ theme, when, days, kind: "due" });
		else if (days <= windowDays) hits.push({ theme, when, days, kind: "near" });
	}
	return hits;
}

function formatDate(date) {
	const year = date.getFullYear();
	const month = String(date.getMonth() + 1).padStart(2, "0");
	const day = String(date.getDate()).padStart(2, "0");
	return `${year}-${month}-${day}`;
}

/** Human lines in the same shape as tools/anchor_check.py output. */
export function renderAnchorHits(hits) {
	const lines = [];
	for (const hit of hits) {
		if (hit.kind === "due") {
			lines.push(`${hit.theme}：锚触发已到（${formatDate(hit.when)}）——说「更新锚」即可`);
		} else {
			lines.push(`${hit.theme}：锚触发临近（${formatDate(hit.when)}，还有 ${hit.days} 天）`);
		}
	}
	return lines;
}

/** Every anchor root: `$RESANITY_ANCHORS`, configured dirs, live-session `<cwd>/anchors`. */
export function anchorRoots({ env = process.env, config = {}, agents = undefined } = {}) {
	const roots = new Set();
	const envDir = env.RESANITY_ANCHORS;
	if (envDir) {
		for (const part of envDir.split(delimiter)) {
			if (part.trim()) roots.add(resolve(part.trim()));
		}
	}
	for (const dir of config.anchorsDirs ?? []) roots.add(resolve(dir));
	const list = typeof agents?.list === "function" ? agents.list() : [];
	for (const agent of list) {
		const cwd = agent?.session?.header?.cwd;
		if (typeof cwd === "string" && cwd) roots.add(join(cwd, "anchors"));
	}
	return [...roots];
}

/** Scan all roots, one line per due/near hit. */
export async function runAnchorCheck(ctx, config, { extraRoots = [], windowDays = undefined } = {}) {
	const today = new Date();
	const window = windowDays ?? config.reminderWindowDays ?? 3;
	const roots = [...new Set([...anchorRoots({ config, agents: ctx.get("agents") }), ...extraRoots])];
	const hits = [];
	for (const root of roots) {
		const dirHits = await scanAnchorDir(root, { today, windowDays: window });
		for (const hit of dirHits) hits.push({ ...hit, root });
	}
	return { roots, hits, today, window };
}

function systemNotify(ctx, message) {
	if (message === "") return;
	if (process.platform === "darwin") {
		const escaped = message.replaceAll('"', '\\"');
		try {
			spawnSync("osascript", ["-e", `display notification "${escaped}" with title "⚓ 锚体检"`]);
		} catch (error) {
			ctx.logger.warn("resanity notification failed:", error);
		}
	} else if (process.platform === "linux") {
		try {
			spawnSync("notify-send", ["⚓ 锚体检", message]);
		} catch (error) {
			ctx.logger.warn("resanity notification failed:", error);
		}
	}
	// 其他平台：仅日志，不弹系统通知
}

/** Register the background anchor check when `ctx.timer` is composed. */
function mountTimer(ctx, config) {
	const timer = ctx.get("timer");
	if (!timer) return;
	const check = async () => {
		try {
			const { roots, hits, window } = await runAnchorCheck(ctx, config);
			const lines = renderAnchorHits(hits);
			ctx.logger.info(`resanity anchor check: ${roots.length} root(s), window ${window}d, ${lines.length} hit(s)`);
			if (lines.length > 0 && config.systemNotifications) systemNotify(ctx, lines.join("；"));
		} catch (error) {
			ctx.logger.warn("resanity anchor check failed:", error);
		}
	};
	const intervalMs = Math.max(1, (config.checkIntervalHours ?? 6) * 3_600_000);
	timer.interval(() => check(), intervalMs);
	// 启动 30 秒后先跑一次，避免等满一个周期
	timer.timeout(() => check(), 30_000);
}

/** Register the `/resanity-check` command when `ctx.commands` is composed. */
function mountCommand(ctx, config) {
	const commands = ctx.get("commands");
	if (!commands) return;
	commands.register({
		name: "resanity-check",
		description: "检查工作区认知锚的到期/临近触发器（reSanity 锚体检）",
		input: { hint: "[--window N]" },
		handler: async (invocation) => {
			try {
				const windowMatch = invocation.rawInput.match(/--window\s+(\d+)/u);
				const windowDays = windowMatch ? Math.max(1, Number(windowMatch[1])) : undefined;
				const cwd = invocation.agent?.session?.header?.cwd;
				const extraRoots = typeof cwd === "string" && cwd ? [join(cwd, "anchors")] : [];
				const { hits } = await runAnchorCheck(ctx, config, { extraRoots, windowDays });
				const lines = renderAnchorHits(hits);
				if (lines.length === 0) {
					return { kind: "success", text: "⚓ 锚体检：无到期触发器" };
				}
				return { kind: "success", text: lines.join("\n") };
			} catch (error) {
				return { kind: "error", text: `锚体检失败：${error?.message ?? error}` };
			}
		},
	});
}

// ── tushare credentials（/resanity-tushare）────────────────────────────────

/** 凭据文件位置：`$RESANITY_CREDENTIALS` 优先，否则 `<DSH_HOME|~/.dsh>/resanity/credentials.json`。 */
export function credentialsPath(env = process.env) {
	if (env.RESANITY_CREDENTIALS) return resolve(env.RESANITY_CREDENTIALS);
	const dshHome = env.DSH_HOME || join(homedir(), ".dsh");
	return join(dshHome, "resanity", "credentials.json");
}

/** `{ token, path }`；文件缺失或格式错误视为未配置。 */
export async function readCredentials(env = process.env) {
	const path = credentialsPath(env);
	try {
		const parsed = JSON.parse(await readFile(path, "utf8"));
		const token = typeof parsed?.tushareToken === "string" ? parsed.tushareToken.trim() : "";
		return { token, path };
	} catch {
		return { token: "", path };
	}
}

/** 写凭据文件（600 权限），返回路径。 */
export async function writeCredentials(token, env = process.env) {
	const path = credentialsPath(env);
	await mkdir(dirname(path), { recursive: true });
	await writeFile(path, `${JSON.stringify({ tushareToken: token }, null, 2)}\n`, { mode: 0o600 });
	await chmod(path, 0o600).catch(() => {});
	return path;
}

export async function clearCredentials(env = process.env) {
	await rm(credentialsPath(env), { force: true });
}

const TOKEN_PATTERN = /^[0-9a-f]{40}$/iu;

/** Tushare Pro 在线校验：code 0 = 有效；网络失败返回 `{ code: "NETWORK" }`。 */
export async function validateTushareToken(token, fetchImpl = globalThis.fetch) {
	let response;
	try {
		response = await fetchImpl("http://api.tushare.pro", {
			method: "POST",
			headers: { "Content-Type": "application/json" },
			body: JSON.stringify({
				api_name: "trade_cal",
				token,
				params: { exchange: "SSE", start_date: "20260101", end_date: "20260110" },
				fields: "exchange,cal_date,is_open",
			}),
			signal: AbortSignal.timeout(15_000),
		});
	} catch {
		return { ok: false, code: "NETWORK", msg: "网络不可用" };
	}
	if (!response.ok) return { ok: false, code: `HTTP ${response.status}`, msg: "" };
	const body = await response.json().catch(() => ({}));
	return { ok: body?.code === 0, code: body?.code, msg: body?.msg ?? "" };
}

const TUSHARE_USAGE = "用法：/resanity-tushare set <token> | status | clear | test";

/** Register the `/resanity-tushare` command when `ctx.commands` is composed. */
function mountTushareCommand(ctx, config) {
	const commands = ctx.get("commands");
	if (!commands) return;
	commands.register({
		name: "resanity-tushare",
		description: "配置 reSanity 价格锚的 Tushare token（set/status/clear/test）",
		input: { hint: "[set <token>|status|clear|test]" },
		// token 出现在 rawInput 里，绝不能落进 command/run 生命周期日志
		recordInput: false,
		handler: async (invocation) => {
			const [verb, ...rest] = invocation.rawInput.trim().split(/\s+/u);
			const action = (verb ?? "").toLowerCase();
			try {
				switch (action) {
					case "set": {
						const token = rest.join("").trim();
						if (!token) return { kind: "error", text: `${TUSHARE_USAGE}（token 共 40 位十六进制）` };
						if (!TOKEN_PATTERN.test(token)) {
							return { kind: "error", text: "token 格式不对：应为 40 位十六进制字符串" };
						}
						const check = await validateTushareToken(token);
						const path = await writeCredentials(token);
						const suffix = `…${token.slice(-4)}`;
						if (check.ok) {
							return { kind: "success", text: `Tushare token 已保存（${suffix}），在线校验通过\n凭据文件：${path}` };
						}
						if (check.code === "NETWORK") {
							return { kind: "success", text: `Tushare token 已保存（${suffix}，离线，未在线校验）\n凭据文件：${path}` };
						}
						return {
							kind: "success",
							text: `Tushare token 已保存（${suffix}），但在线校验未通过（code ${check.code}${check.msg ? `：${check.msg}` : ""}）——可稍后 /resanity-tushare test\n凭据文件：${path}`,
						};
					}
					case "status": {
						const { token, path } = await readCredentials();
						if (!token) {
							return { kind: "success", text: `未配置 Tushare token。运行 /resanity-tushare set <token>\n凭据文件：${path}` };
						}
						return { kind: "success", text: `已配置（…${token.slice(-4)}）\n凭据文件：${path}` };
					}
					case "clear":
						await clearCredentials();
						return { kind: "success", text: "已清除 Tushare token" };
					case "test": {
						const { token } = await readCredentials();
						if (!token) return { kind: "error", text: `未配置 token，先 /resanity-tushare set <token>` };
						const check = await validateTushareToken(token);
						if (check.ok) return { kind: "success", text: `在线校验通过（…${token.slice(-4)}）` };
						return {
							kind: "error",
							text: `在线校验失败（code ${check.code}${check.msg ? `：${check.msg}` : ""}）`,
						};
					}
					default:
						return { kind: "error", text: TUSHARE_USAGE };
				}
			} catch (error) {
				return { kind: "error", text: `操作失败：${error?.message ?? error}` };
			}
		},
	});
}

function apply(ctx, config = {}) {
	ctx.skills.registerProvider(() => provider);
	// 条件注入：timer/commands 是懒激活服务，必须 inject 触发激活
	//（ctx.get 只会看到已经活跃的实现，宿主启动时 commands 通常还没被激活）
	ctx.inject(["timer"], (timerCtx) => mountTimer(timerCtx, config));
	ctx.inject(["commands"], (commandsCtx) => {
		mountCommand(commandsCtx, config);
		mountTushareCommand(commandsCtx, config);
	});
}

export { apply, Config, inject, name, provider };

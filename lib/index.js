import { chmod, mkdir, readFile, readdir, rename, rm, writeFile } from "node:fs/promises";
import { spawnSync } from "node:child_process";
import { delimiter, dirname, join, resolve } from "node:path";
import { homedir } from "node:os";
import { fileURLToPath } from "node:url";
import z from "@deepseek-ai/schemastery";
import { BUNDLED_SKILL_RANK } from "@deepseek-ai/dsh-skill";

/**
 * Resanity — DSH plugin.
 *
 * Mechanical capabilities, each activated only when its service is composed:
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
	/** Send OS notifications (opt-in; macOS osascript / Linux notify-send). */
	systemNotifications: z.boolean().default(false),
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
	/(?<![0-9/])(\d{1,2})\/(\d{1,2})(?![0-9/])/gu,
];

function startOfDay(today) {
	return new Date(today.getFullYear(), today.getMonth(), today.getDate());
}

/**
 * Calendar dates in `text`.
 *
 * Bare M/D belongs to the current year. A missed trigger stays overdue until
 * the anchor is updated; silently rolling it into next year would hide the
 * exact event the reminder exists to surface.
 */
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
				year = today.getFullYear();
			} else {
				year = Number(match[1]);
				month = Number(match[2]);
				day = Number(match[3]);
			}
			const parsed = new Date(year, month - 1, day);
			if (
				Number.isNaN(parsed.getTime()) ||
				parsed.getFullYear() !== year ||
				parsed.getMonth() !== month - 1 ||
				parsed.getDate() !== day
			) continue;
			found.push(parsed);
		}
	}
	return [...new Map(found.map((date) => [date.getTime(), date])).values()];
}

/** Lifecycle declared by the model/user. Missing status keeps v1 anchors active. */
export function anchorStatus(block) {
	const header = block.split("\n")[0] ?? "";
	if (header.includes("失效") || /\[(?:refuted|realized|archived)\]/iu.test(header)) {
		if (header.includes("失效") || /\[refuted\]/iu.test(header)) return "refuted";
		if (/\[realized\]/iu.test(header)) return "realized";
		return "archived";
	}
	const match = block.match(/^\s*-\s*(?:状态|status)\s*[:：]\s*(active|refuted|realized|archived)\s*$/imu);
	return match ? match[1].toLowerCase() : "active";
}

/** Earliest trigger date among active anchors in one file, or null. */
export function nextTriggerDate(text, today = new Date()) {
	const blocks = text.split(/^## /mu).slice(1);
	const dates = [];
	for (const block of blocks) {
		if (anchorStatus(block) !== "active") continue;
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
			if (lines.length > 0 && config.systemNotifications === true) systemNotify(ctx, lines.join("；"));
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
		description: "检查工作区认知锚的到期/临近触发器（Resanity 锚体检）",
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
	const temporary = `${path}.${process.pid}.${Date.now()}.tmp`;
	try {
		await writeFile(temporary, `${JSON.stringify({ tushareToken: token }, null, 2)}\n`, { mode: 0o600 });
		await chmod(temporary, 0o600).catch(() => {});
		await rename(temporary, path);
		await chmod(path, 0o600).catch(() => {});
	} catch (error) {
		await rm(temporary, { force: true }).catch(() => {});
		throw error;
	}
	return path;
}

export async function clearCredentials(env = process.env) {
	await rm(credentialsPath(env), { force: true });
}

/**
 * 仅去掉粘贴时混入的不可见零宽字符（U+200B/U+2060 等，肉眼看不见、但会导致
 * 服务器校验失败）；其余内容原样保留——不限制 token 的长度和字符格式，
 * 有效性交给在线校验判断。
 */
function stripInvisibleChars(raw) {
	return raw.replace(/[\u200b-\u200f\u2060\ufeff]/gu, "");
}

/** Tushare Pro 在线校验：code 0 = 有效；网络失败返回 `{ code: "NETWORK" }`。 */
export async function validateTushareToken(token, fetchImpl = globalThis.fetch) {
	let response;
	try {
		response = await fetchImpl("https://api.tushare.pro", {
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

const TUSHARE_USAGE = [
	"用法：",
	"  /resanity-tushare set <token> —— 保存并自动在线校验",
	"  /resanity-tushare status —— 查看是否已配置",
	"  /resanity-tushare test —— 在线校验已保存的 token",
	"  /resanity-tushare clear —— 删除已保存的 token",
].join("\n");

/** Register the `/resanity-tushare` command when `ctx.commands` is composed. */
function mountTushareCommand(ctx, config) {
	const commands = ctx.get("commands");
	if (!commands) return;
	commands.register({
		name: "resanity-tushare",
		description: "配置 Resanity 价格锚的 Tushare token（set/status/clear/test）",
		input: { hint: "[set <token>|status|clear|test]" },
		// token 出现在 rawInput 里，绝不能落进 command/run 生命周期日志
		recordInput: false,
		handler: async (invocation) => {
			const [verb, ...rest] = invocation.rawInput.trim().split(/\s+/u);
			const action = (verb ?? "").toLowerCase();
			try {
				switch (action) {
					case "set": {
						const raw = rest.join("").trim();
						if (!raw) return { kind: "error", text: `缺少 token。${TUSHARE_USAGE}` };
						// 不猜 token 格式；先在线校验，再原子地替换旧凭据。
						const token = stripInvisibleChars(raw);
						const suffix = token.length > 4 ? `…${token.slice(-4)}` : `…${token}`;
						const note = token.length !== raw.length ? "（已去掉粘贴混入的不可见字符）" : "";
						const check = await validateTushareToken(token);
						if (check.ok) {
							const path = await writeCredentials(token);
							return { kind: "success", text: `Tushare token 已保存（${suffix}）${note}，自动在线校验通过 ✓\n凭据文件：${path}` };
						}
						if (check.code === "NETWORK") {
							return { kind: "error", text: `当前网络不可用，token 未保存，原凭据未改变——可稍后重试 /resanity-tushare set` };
						}
						return {
							kind: "error",
							text: `Tushare token 自动在线校验未通过（code ${check.code}${check.msg ? `：${check.msg}` : ""}），未保存，原凭据未改变`,
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
						return {
							kind: "error",
							text: action === "" ? `缺少子命令。${TUSHARE_USAGE}` : `不认识的子命令「${verb}」。${TUSHARE_USAGE}`,
						};
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

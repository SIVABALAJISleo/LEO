import { c as leoJson, t as LeoError } from "./leo-client-D7U1wpIv.mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/chat-history-D5ztPwzC.js
var MERGE_EVENT = "leo:chat-merged";
function emitMerge(summary) {
	if (typeof window === "undefined") return;
	window.dispatchEvent(new CustomEvent(MERGE_EVENT, { detail: summary }));
}
function onChatMerged(handler) {
	if (typeof window === "undefined") return () => {};
	const listener = (e) => handler(e.detail);
	window.addEventListener(MERGE_EVENT, listener);
	return () => window.removeEventListener(MERGE_EVENT, listener);
}
function messageKey(m) {
	return `${m.role}|${m.ts}|${m.content.length}`;
}
function diffMessages(before, after) {
	const beforeKeys = new Set(before.map(messageKey));
	const afterKeys = new Set(after.map(messageKey));
	let added = 0;
	let removed = 0;
	for (const k of afterKeys) if (!beforeKeys.has(k)) added += 1;
	for (const k of beforeKeys) if (!afterKeys.has(k)) removed += 1;
	return {
		added,
		removed
	};
}
var KEY = "leo.chat.sessions";
var SYNC_FLAG = "leo.chat.sync";
var SYNC_PATH_KEY = "leo.chat.sync_path";
var DEFAULT_SYNC_PATH = "/api/v1/chat/sessions";
var MAX_SESSIONS = 5e3;
function isSyncEnabled() {
	if (typeof window === "undefined") return false;
	return window.localStorage.getItem(SYNC_FLAG) === "on";
}
function setSyncEnabled(on) {
	if (typeof window === "undefined") return;
	window.localStorage.setItem(SYNC_FLAG, on ? "on" : "off");
}
function getSyncPath() {
	if (typeof window === "undefined") return DEFAULT_SYNC_PATH;
	return window.localStorage.getItem(SYNC_PATH_KEY) || DEFAULT_SYNC_PATH;
}
function setSyncPath(path) {
	if (typeof window === "undefined") return;
	const clean = path.trim() || DEFAULT_SYNC_PATH;
	window.localStorage.setItem(SYNC_PATH_KEY, clean);
}
function normalize(s) {
	return {
		id: s.id,
		title: s.title ?? "New chat",
		createdAt: s.createdAt ?? Date.now(),
		updatedAt: s.updatedAt ?? Date.now(),
		version: typeof s.version === "number" && s.version > 0 ? s.version : 1,
		lastSyncedVersion: s.lastSyncedVersion,
		messages: s.messages
	};
}
function safeParse(raw) {
	if (!raw) return [];
	try {
		const arr = JSON.parse(raw);
		if (!Array.isArray(arr)) return [];
		return arr.filter((s) => s && typeof s.id === "string" && Array.isArray(s.messages)).map(normalize);
	} catch {
		return [];
	}
}
function listSessions() {
	if (typeof window === "undefined") return [];
	return safeParse(window.localStorage.getItem(KEY)).sort((a, b) => b.updatedAt - a.updatedAt);
}
function getSession(id) {
	return listSessions().find((s) => s.id === id) ?? null;
}
function writeAll(sessions) {
	if (typeof window === "undefined") return;
	const trimmed = sessions.length > MAX_SESSIONS ? sessions.slice(0, MAX_SESSIONS) : sessions;
	window.localStorage.setItem(KEY, JSON.stringify(trimmed));
}
/**
* Save locally. Auto-bumps `version` relative to the existing local copy so
* callers never have to manage it. Returns the persisted session.
*/
function saveSessionLocal(session) {
	const all = listSessions();
	const idx = all.findIndex((s) => s.id === session.id);
	const existingVersion = idx >= 0 ? all[idx].version : 0;
	const next = {
		...session,
		version: Math.max(session.version ?? 0, existingVersion + 1),
		lastSyncedVersion: session.lastSyncedVersion ?? (idx >= 0 ? all[idx].lastSyncedVersion : void 0)
	};
	if (idx >= 0) all[idx] = next;
	else all.unshift(next);
	writeAll(all);
	return next;
}
function deleteSessionLocal(id) {
	writeAll(listSessions().filter((s) => s.id !== id));
}
/**
* Merge a local and remote copy of the same session id. When both sides have
* moved past the last synced version, we union their messages by a stable
* per-message key so neither device's edits are lost.
*
* Exported for tests.
*/
function mergeSession(local, remote) {
	if (!local) return remote;
	if (!remote) return local;
	const baseline = local.lastSyncedVersion ?? 0;
	const localChanged = local.version > baseline;
	const remoteChanged = remote.version > baseline;
	if (!localChanged || !remoteChanged) {
		if (remote.version > local.version || remote.updatedAt > local.updatedAt) return {
			...remote,
			lastSyncedVersion: remote.version
		};
		return {
			...local,
			lastSyncedVersion: Math.max(baseline, remote.version)
		};
	}
	const mergedMessages = [];
	const messagesEqual = (a, b) => {
		if (a.clientMessageId && b.clientMessageId) return a.clientMessageId === b.clientMessageId;
		return a.role === b.role && a.content === b.content && Math.abs(a.ts - b.ts) < 15e3;
	};
	for (const m of [...local.messages, ...remote.messages]) {
		const idx = mergedMessages.findIndex((existing) => messagesEqual(existing, m));
		if (idx < 0) mergedMessages.push(m);
		else {
			const existing = mergedMessages[idx];
			if (m.meta && !existing.meta || m.content.length > existing.content.length) mergedMessages[idx] = m;
		}
	}
	const messages = mergedMessages.sort((a, b) => a.ts - b.ts);
	const nextVersion = Math.max(local.version, remote.version) + 1;
	const newer = remote.updatedAt > local.updatedAt ? remote : local;
	return {
		id: local.id,
		title: newer.title,
		createdAt: Math.min(local.createdAt, remote.createdAt),
		updatedAt: Date.now(),
		version: nextVersion,
		lastSyncedVersion: Math.max(local.version, remote.version),
		messages
	};
}
async function saveSession(session) {
	const persisted = saveSessionLocal(session);
	if (!isSyncEnabled()) return;
	try {
		const res = await leoJson(getSyncPath(), {
			method: "POST",
			body: JSON.stringify({
				session: persisted,
				expectedVersion: persisted.lastSyncedVersion ?? 0
			})
		});
		const echoed = res?.session ?? (res?.id ? res : void 0);
		if (echoed && echoed.id === persisted.id) {
			const remote = normalize(echoed);
			const merged = mergeSession(persisted, remote);
			if (merged) {
				merged.lastSyncedVersion = Math.max(merged.version, remote.version);
				saveSessionLocal(merged);
				const diff = diffMessages(persisted.messages, merged.messages);
				if (diff.added > 0 || diff.removed > 0) emitMerge({
					id: merged.id,
					title: merged.title,
					addedFromRemote: diff.added,
					removedFromLocal: diff.removed,
					remoteVersion: remote.version,
					mergedVersion: merged.version,
					kind: "background"
				});
			}
		} else {
			persisted.lastSyncedVersion = persisted.version;
			saveSessionLocal(persisted);
		}
	} catch (err) {
		if (err instanceof LeoError && err.status === 409) {
			const remoteRaw = err.body?.session;
			if (remoteRaw && remoteRaw.id === persisted.id) {
				const remote = normalize(remoteRaw);
				const merged = mergeSession(persisted, remote);
				if (merged) {
					merged.lastSyncedVersion = Math.max(merged.version, remote.version);
					const saved = saveSessionLocal(merged);
					const diff = diffMessages(persisted.messages, saved.messages);
					emitMerge({
						id: saved.id,
						title: saved.title,
						addedFromRemote: diff.added,
						removedFromLocal: diff.removed,
						remoteVersion: remote.version,
						mergedVersion: saved.version,
						kind: "conflict-rollback"
					});
					try {
						await leoJson(getSyncPath(), {
							method: "POST",
							body: JSON.stringify({
								session: saved,
								expectedVersion: saved.lastSyncedVersion ?? 0
							})
						});
					} catch {}
					return;
				}
			}
		}
		console.warn("[LEO chat] server sync save failed", err);
	}
}
async function deleteSession(id) {
	deleteSessionLocal(id);
	if (!isSyncEnabled()) return;
	try {
		await leoJson(`${getSyncPath()}/${encodeURIComponent(id)}`, { method: "DELETE" });
	} catch (err) {
		console.warn("[LEO chat] server sync delete failed", err);
	}
}
function normalizeListResponse(res) {
	if (Array.isArray(res)) return { sessions: res.filter(Boolean).map(normalize) };
	return {
		sessions: (res.sessions ?? res.items ?? []).filter((s) => s && typeof s.id === "string" && Array.isArray(s.messages)).map(normalize),
		nextCursor: res.nextCursor ?? void 0
	};
}
/**
* Fetch one page of sessions from the server (`?cursor=&limit=`) and merge
* into local storage. Returns the merged page plus the server-provided cursor
* for the next page (undefined when there are no more).
*
* When sync is disabled, falls back to paginating the local store by
* `updatedAt` — the panel UX stays identical.
*/
async function pullPage(opts = {}) {
	const limit = opts.limit ?? 50;
	if (!isSyncEnabled()) {
		const all = listSessions();
		const startIdx = opts.cursor ? Number(opts.cursor) || 0 : 0;
		return {
			sessions: all.slice(startIdx, startIdx + limit),
			nextCursor: startIdx + limit < all.length ? String(startIdx + limit) : void 0
		};
	}
	try {
		const qs = new URLSearchParams();
		qs.set("limit", String(limit));
		if (opts.cursor) qs.set("cursor", opts.cursor);
		const { sessions: remote, nextCursor } = normalizeListResponse(await leoJson(`${getSyncPath()}?${qs.toString()}`, { method: "GET" }));
		const local = listSessions();
		const byId = new Map(local.map((s) => [s.id, s]));
		for (const r of remote) {
			const localBefore = byId.get(r.id);
			const merged = mergeSession(localBefore, r);
			if (merged) {
				merged.lastSyncedVersion = Math.max(merged.lastSyncedVersion ?? 0, r.version);
				byId.set(r.id, merged);
				if (localBefore) {
					const diff = diffMessages(localBefore.messages, merged.messages);
					if (diff.added > 0 || diff.removed > 0) emitMerge({
						id: merged.id,
						title: merged.title,
						addedFromRemote: diff.added,
						removedFromLocal: diff.removed,
						remoteVersion: r.version,
						mergedVersion: merged.version,
						kind: "background"
					});
				}
			}
		}
		writeAll(Array.from(byId.values()).sort((a, b) => b.updatedAt - a.updatedAt));
		return {
			sessions: remote.map((r) => byId.get(r.id)).filter((s) => Boolean(s)),
			nextCursor
		};
	} catch (err) {
		console.warn("[LEO chat] server sync page pull failed", err);
		const all = listSessions();
		const startIdx = opts.cursor ? Number(opts.cursor) || 0 : 0;
		return {
			sessions: all.slice(startIdx, startIdx + limit),
			nextCursor: startIdx + limit < all.length ? String(startIdx + limit) : void 0
		};
	}
}
/**
* Legacy full pull — pulls the first page and merges. Kept for callers that
* just want "sync now" behaviour on toggle-on.
*/
async function pullAndMerge() {
	await pullPage({ limit: 200 });
	return listSessions();
}
/**
* Walk every cursor page from the server (or local slice fallback when sync
* is disabled), merging each into local storage, and return the complete
* de-duplicated set of sessions sorted by `updatedAt`. Guards against a
* runaway backend by capping at `maxPages` iterations.
*/
async function fetchAllSessions(opts = {}) {
	const limit = opts.limit ?? 100;
	const maxPages = opts.maxPages ?? 100;
	let cursor;
	let pages = 0;
	do {
		cursor = (await pullPage({
			cursor,
			limit
		})).nextCursor;
		pages += 1;
	} while (cursor && pages < maxPages);
	return listSessions();
}
function newSessionId() {
	return `s_${Date.now().toString(36)}_${Math.random().toString(36).slice(2, 8)}`;
}
function deriveTitle(messages) {
	const firstUser = messages.find((m) => m.role === "user");
	if (!firstUser) return "New chat";
	const text = firstUser.content.replace(/\s+/g, " ").trim();
	return text.length > 60 ? `${text.slice(0, 60)}…` : text || "New chat";
}
function searchSessions(query) {
	const q = query.trim().toLowerCase();
	if (!q) return listSessions();
	return listSessions().filter((s) => {
		if (s.title.toLowerCase().includes(q)) return true;
		return s.messages.some((m) => m.content.toLowerCase().includes(q));
	});
}
function exportSessionsAsJson(sessions) {
	return JSON.stringify({
		exported_at: (/* @__PURE__ */ new Date()).toISOString(),
		sessions
	}, null, 2);
}
/**
* Export sessions as a CSV. One row per session; message counts and a
* flattened transcript are included so downstream tools can pivot without
* needing to parse JSON. De-duplicated by session id so a session that
* appears on multiple cursor pages only emits one row.
*/
function exportSessionsAsCsv(sessions) {
	const seen = /* @__PURE__ */ new Set();
	const unique = [];
	for (const s of sessions) {
		if (seen.has(s.id)) continue;
		seen.add(s.id);
		unique.push(s);
	}
	const header = [
		"id",
		"title",
		"created_at",
		"updated_at",
		"version",
		"message_count",
		"transcript"
	];
	const escape = (v) => {
		const s = v == null ? "" : String(v);
		if (/[",\n\r]/.test(s)) return `"${s.replace(/"/g, "\"\"")}"`;
		return s;
	};
	const rows = unique.map((s) => {
		const transcript = s.messages.map((m) => `${m.role}: ${m.content}`).join("\n");
		return [
			s.id,
			s.title,
			new Date(s.createdAt).toISOString(),
			new Date(s.updatedAt).toISOString(),
			s.version,
			s.messages.length,
			transcript
		].map(escape).join(",");
	});
	return [header.join(","), ...rows].join("\n") + "\n";
}
function downloadJson(filename, jsonText) {
	downloadBlob(filename, jsonText, "application/json");
}
function downloadCsv(filename, csvText) {
	downloadBlob(filename, csvText, "text/csv;charset=utf-8");
}
function downloadBlob(filename, text, mime) {
	if (typeof window === "undefined") return;
	const blob = new Blob([text], { type: mime });
	const url = URL.createObjectURL(blob);
	const a = document.createElement("a");
	a.href = url;
	a.download = filename;
	document.body.appendChild(a);
	a.click();
	a.remove();
	setTimeout(() => URL.revokeObjectURL(url), 1e3);
}
//#endregion
export { searchSessions as _, exportSessionsAsCsv as a, getSession as c, listSessions as d, newSessionId as f, saveSession as g, pullPage as h, downloadJson as i, getSyncPath as l, pullAndMerge as m, deriveTitle as n, exportSessionsAsJson as o, onChatMerged as p, downloadCsv as r, fetchAllSessions as s, deleteSession as t, isSyncEnabled as u, setSyncEnabled as v, setSyncPath as y };

// Local persistence + optional server-side sync for chat conversation logs.
// Local store lives in `leo.chat.sessions`. When server sync is enabled
// (leo.chat.sync = "on"), sessions are pushed to and pulled from the LEO
// backend at the configured sync path (default /api/v1/chat/sessions).
//
// Conflict resolution: each ChatSession carries a monotonically increasing
// `version` that bumps on every local edit, plus `lastSyncedVersion` — the
// version we last observed on the server. When we pull a remote copy that
// diverges from the local copy (both sides changed since the last sync),
// we merge messages by (role|ts|length), sort by timestamp, and bump the
// version. Neither device silently overwrites the other.
import { leoJson, LeoError } from "./leo-client";

// -------- Merge / conflict events --------
// Fired on `window` whenever a background pull, a server echo, or a POST
// conflict merges local + remote state. UI subscribes to show a banner.
export type MergeSummary = {
  id: string;
  title: string;
  addedFromRemote: number;
  removedFromLocal: number;
  remoteVersion: number;
  mergedVersion: number;
  /** "background" = came from pullPage; "conflict-rollback" = 409 from POST */
  kind: "background" | "conflict-rollback";
};

const MERGE_EVENT = "leo:chat-merged";

function emitMerge(summary: MergeSummary) {
  if (typeof window === "undefined") return;
  window.dispatchEvent(new CustomEvent<MergeSummary>(MERGE_EVENT, { detail: summary }));
}

export function onChatMerged(handler: (s: MergeSummary) => void): () => void {
  if (typeof window === "undefined") return () => {};
  const listener = (e: Event) => handler((e as CustomEvent<MergeSummary>).detail);
  window.addEventListener(MERGE_EVENT, listener);
  return () => window.removeEventListener(MERGE_EVENT, listener);
}

function messageKey(m: ChatHistoryMessage): string {
  return `${m.role}|${m.ts}|${m.content.length}`;
}

function diffMessages(
  before: ChatHistoryMessage[],
  after: ChatHistoryMessage[],
): { added: number; removed: number } {
  const beforeKeys = new Set(before.map(messageKey));
  const afterKeys = new Set(after.map(messageKey));
  let added = 0;
  let removed = 0;
  for (const k of afterKeys) if (!beforeKeys.has(k)) added += 1;
  for (const k of beforeKeys) if (!afterKeys.has(k)) removed += 1;
  return { added, removed };
}

export type ChatHistoryMeta = {
  resolved_by?: string;
  latency_ms?: number;
  compute_avoided?: boolean;
  gpu_watts_saved?: number;
  avoidance_rate_pct?: number;
};

export type ChatHistoryMessage = {
  role: "user" | "assistant";
  content: string;
  meta?: ChatHistoryMeta;
  ts: number;
  clientMessageId?: string;
};

export type ChatSession = {
  id: string;
  title: string;
  createdAt: number;
  updatedAt: number;
  /** Bumped on every local edit. Used for conflict resolution. */
  version: number;
  /** Version we last observed on the server (0 if never synced). */
  lastSyncedVersion?: number;
  messages: ChatHistoryMessage[];
};

const KEY = "leo.chat.sessions";
const SYNC_FLAG = "leo.chat.sync";
const SYNC_PATH_KEY = "leo.chat.sync_path";
const DEFAULT_SYNC_PATH = "/api/v1/chat/sessions";
const MAX_SESSIONS = 5000;

// -------- Sync configuration --------

export function isSyncEnabled(): boolean {
  if (typeof window === "undefined") return false;
  return window.localStorage.getItem(SYNC_FLAG) === "on";
}

export function setSyncEnabled(on: boolean) {
  if (typeof window === "undefined") return;
  window.localStorage.setItem(SYNC_FLAG, on ? "on" : "off");
}

export function getSyncPath(): string {
  if (typeof window === "undefined") return DEFAULT_SYNC_PATH;
  return window.localStorage.getItem(SYNC_PATH_KEY) || DEFAULT_SYNC_PATH;
}

export function setSyncPath(path: string) {
  if (typeof window === "undefined") return;
  const clean = path.trim() || DEFAULT_SYNC_PATH;
  window.localStorage.setItem(SYNC_PATH_KEY, clean);
}

// -------- Local persistence --------

function normalize(
  s: Partial<ChatSession> & { id: string; messages: ChatHistoryMessage[] },
): ChatSession {
  return {
    id: s.id,
    title: s.title ?? "New chat",
    createdAt: s.createdAt ?? Date.now(),
    updatedAt: s.updatedAt ?? Date.now(),
    version: typeof s.version === "number" && s.version > 0 ? s.version : 1,
    lastSyncedVersion: s.lastSyncedVersion,
    messages: s.messages,
  };
}

function safeParse(raw: string | null): ChatSession[] {
  if (!raw) return [];
  try {
    const arr = JSON.parse(raw);
    if (!Array.isArray(arr)) return [];
    return arr
      .filter((s) => s && typeof s.id === "string" && Array.isArray(s.messages))
      .map(normalize);
  } catch {
    return [];
  }
}

export function listSessions(): ChatSession[] {
  if (typeof window === "undefined") return [];
  return safeParse(window.localStorage.getItem(KEY)).sort((a, b) => b.updatedAt - a.updatedAt);
}

export function getSession(id: string): ChatSession | null {
  return listSessions().find((s) => s.id === id) ?? null;
}

function writeAll(sessions: ChatSession[]) {
  if (typeof window === "undefined") return;
  const trimmed = sessions.length > MAX_SESSIONS ? sessions.slice(0, MAX_SESSIONS) : sessions;
  window.localStorage.setItem(KEY, JSON.stringify(trimmed));
}

/**
 * Save locally. Auto-bumps `version` relative to the existing local copy so
 * callers never have to manage it. Returns the persisted session.
 */
export function saveSessionLocal(session: ChatSession): ChatSession {
  const all = listSessions();
  const idx = all.findIndex((s) => s.id === session.id);
  const existingVersion = idx >= 0 ? all[idx].version : 0;
  const next: ChatSession = {
    ...session,
    version: Math.max(session.version ?? 0, existingVersion + 1),
    lastSyncedVersion:
      session.lastSyncedVersion ?? (idx >= 0 ? all[idx].lastSyncedVersion : undefined),
  };
  if (idx >= 0) all[idx] = next;
  else all.unshift(next);
  writeAll(all);
  return next;
}

export function deleteSessionLocal(id: string): void {
  writeAll(listSessions().filter((s) => s.id !== id));
}

// -------- Conflict resolution --------

/**
 * Merge a local and remote copy of the same session id. When both sides have
 * moved past the last synced version, we union their messages by a stable
 * per-message key so neither device's edits are lost.
 *
 * Exported for tests.
 */
export function mergeSession(
  local: ChatSession | undefined,
  remote: ChatSession | undefined,
): ChatSession | undefined {
  if (!local) return remote;
  if (!remote) return local;

  const baseline = local.lastSyncedVersion ?? 0;
  const localChanged = local.version > baseline;
  const remoteChanged = remote.version > baseline;

  // No divergence — take whichever claims a higher version / newer updatedAt.
  if (!localChanged || !remoteChanged) {
    if (remote.version > local.version || remote.updatedAt > local.updatedAt) {
      return { ...remote, lastSyncedVersion: remote.version };
    }
    return { ...local, lastSyncedVersion: Math.max(baseline, remote.version) };
  }

  // Divergence — merge messages, bump version.
  const mergedMessages: ChatHistoryMessage[] = [];
  const messagesEqual = (a: ChatHistoryMessage, b: ChatHistoryMessage) => {
    if (a.clientMessageId && b.clientMessageId) {
      return a.clientMessageId === b.clientMessageId;
    }
    return a.role === b.role && a.content === b.content && Math.abs(a.ts - b.ts) < 15000;
  };

  for (const m of [...local.messages, ...remote.messages]) {
    const idx = mergedMessages.findIndex((existing) => messagesEqual(existing, m));
    if (idx < 0) {
      mergedMessages.push(m);
    } else {
      const existing = mergedMessages[idx];
      const preferNew = (m.meta && !existing.meta) || m.content.length > existing.content.length;
      if (preferNew) {
        mergedMessages[idx] = m;
      }
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
    messages,
  };
}

// -------- Combined save/delete (local + optional server) --------

export async function saveSession(session: ChatSession): Promise<void> {
  const persisted = saveSessionLocal(session);
  if (!isSyncEnabled()) return;
  try {
    const res = await leoJson<{ session?: ChatSession } | ChatSession>(getSyncPath(), {
      method: "POST",
      body: JSON.stringify({
        session: persisted,
        expectedVersion: persisted.lastSyncedVersion ?? 0,
      }),
    });
    // Backend may echo back a merged/canonical copy (e.g. if another device
    // wrote first). Fold it in so this device converges.
    const echoed: ChatSession | undefined =
      (res as { session?: ChatSession })?.session ??
      ((res as ChatSession)?.id ? (res as ChatSession) : undefined);
    if (echoed && echoed.id === persisted.id) {
      const remote = normalize(echoed);
      const merged = mergeSession(persisted, remote);
      if (merged) {
        merged.lastSyncedVersion = Math.max(merged.version, remote.version);
        saveSessionLocal(merged);
        const diff = diffMessages(persisted.messages, merged.messages);
        if (diff.added > 0 || diff.removed > 0) {
          emitMerge({
            id: merged.id,
            title: merged.title,
            addedFromRemote: diff.added,
            removedFromLocal: diff.removed,
            remoteVersion: remote.version,
            mergedVersion: merged.version,
            kind: "background",
          });
        }
      }
    } else {
      persisted.lastSyncedVersion = persisted.version;
      saveSessionLocal(persisted);
    }
  } catch (err) {
    // 409 = server detected a version conflict. Body should carry the
    // canonical remote session so we can merge + roll back optimistic writes
    // that the server refused.
    if (err instanceof LeoError && err.status === 409) {
      const body = err.body as { session?: ChatSession } | undefined;
      const remoteRaw = body?.session;
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
            kind: "conflict-rollback",
          });
          // Retry once with the newly-agreed baseline. Prevents endless
          // spinning on this write while still surfacing the merge to the UI.
          try {
            await leoJson(getSyncPath(), {
              method: "POST",
              body: JSON.stringify({
                session: saved,
                expectedVersion: saved.lastSyncedVersion ?? 0,
              }),
            });
          } catch {
            /* swallowed — local state is still consistent */
          }
          return;
        }
      }
    }

    console.warn("[LEO chat] server sync save failed", err);
  }
}

export async function deleteSession(id: string): Promise<void> {
  deleteSessionLocal(id);
  if (!isSyncEnabled()) return;
  try {
    await leoJson(`${getSyncPath()}/${encodeURIComponent(id)}`, {
      method: "DELETE",
    });
  } catch (err) {
    console.warn("[LEO chat] server sync delete failed", err);
  }
}

export function clearAllSessions(): void {
  writeAll([]);
}

// -------- Server pull, pagination + merge --------

type ServerListResponse =
  | { sessions?: ChatSession[]; items?: ChatSession[]; nextCursor?: string | null }
  | ChatSession[];

function normalizeListResponse(res: ServerListResponse): {
  sessions: ChatSession[];
  nextCursor?: string;
} {
  if (Array.isArray(res)) return { sessions: res.filter(Boolean).map(normalize) };
  const raw = res.sessions ?? res.items ?? [];
  return {
    sessions: raw
      .filter((s) => s && typeof s.id === "string" && Array.isArray(s.messages))
      .map(normalize),
    nextCursor: res.nextCursor ?? undefined,
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
export async function pullPage(
  opts: { cursor?: string; limit?: number } = {},
): Promise<{ sessions: ChatSession[]; nextCursor?: string }> {
  const limit = opts.limit ?? 50;

  if (!isSyncEnabled()) {
    const all = listSessions();
    const startIdx = opts.cursor ? Number(opts.cursor) || 0 : 0;
    const slice = all.slice(startIdx, startIdx + limit);
    const nextCursor = startIdx + limit < all.length ? String(startIdx + limit) : undefined;
    return { sessions: slice, nextCursor };
  }

  try {
    const qs = new URLSearchParams();
    qs.set("limit", String(limit));
    if (opts.cursor) qs.set("cursor", opts.cursor);
    const res = await leoJson<ServerListResponse>(`${getSyncPath()}?${qs.toString()}`, {
      method: "GET",
    });
    const { sessions: remote, nextCursor } = normalizeListResponse(res);

    // Merge each remote session against its local counterpart.
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
          if (diff.added > 0 || diff.removed > 0) {
            emitMerge({
              id: merged.id,
              title: merged.title,
              addedFromRemote: diff.added,
              removedFromLocal: diff.removed,
              remoteVersion: r.version,
              mergedVersion: merged.version,
              kind: "background",
            });
          }
        }
      }
    }
    const combined = Array.from(byId.values()).sort((a, b) => b.updatedAt - a.updatedAt);
    writeAll(combined);
    // Return the merged versions of the page we just pulled.
    return {
      sessions: remote.map((r) => byId.get(r.id)).filter((s): s is ChatSession => Boolean(s)),
      nextCursor,
    };
  } catch (err) {
    console.warn("[LEO chat] server sync page pull failed", err);
    // Fall back to local slice so the panel still shows something.
    const all = listSessions();
    const startIdx = opts.cursor ? Number(opts.cursor) || 0 : 0;
    const slice = all.slice(startIdx, startIdx + limit);
    return {
      sessions: slice,
      nextCursor: startIdx + limit < all.length ? String(startIdx + limit) : undefined,
    };
  }
}

/**
 * Legacy full pull — pulls the first page and merges. Kept for callers that
 * just want "sync now" behaviour on toggle-on.
 */
export async function pullAndMerge(): Promise<ChatSession[]> {
  await pullPage({ limit: 200 });
  return listSessions();
}

/**
 * Walk every cursor page from the server (or local slice fallback when sync
 * is disabled), merging each into local storage, and return the complete
 * de-duplicated set of sessions sorted by `updatedAt`. Guards against a
 * runaway backend by capping at `maxPages` iterations.
 */
export async function fetchAllSessions(
  opts: { limit?: number; maxPages?: number } = {},
): Promise<ChatSession[]> {
  const limit = opts.limit ?? 100;
  const maxPages = opts.maxPages ?? 100;
  let cursor: string | undefined;
  let pages = 0;
  do {
    const page = await pullPage({ cursor, limit });
    cursor = page.nextCursor;
    pages += 1;
  } while (cursor && pages < maxPages);
  return listSessions();
}

// -------- Utilities --------

export function newSessionId(): string {
  return `s_${Date.now().toString(36)}_${Math.random().toString(36).slice(2, 8)}`;
}

export function deriveTitle(messages: ChatHistoryMessage[]): string {
  const firstUser = messages.find((m) => m.role === "user");
  if (!firstUser) return "New chat";
  const text = firstUser.content.replace(/\s+/g, " ").trim();
  return text.length > 60 ? `${text.slice(0, 60)}…` : text || "New chat";
}

export function searchSessions(query: string): ChatSession[] {
  const q = query.trim().toLowerCase();
  if (!q) return listSessions();
  return listSessions().filter((s) => {
    if (s.title.toLowerCase().includes(q)) return true;
    return s.messages.some((m) => m.content.toLowerCase().includes(q));
  });
}

export function exportSessionsAsJson(sessions: ChatSession[]): string {
  return JSON.stringify({ exported_at: new Date().toISOString(), sessions }, null, 2);
}

/**
 * Export sessions as a CSV. One row per session; message counts and a
 * flattened transcript are included so downstream tools can pivot without
 * needing to parse JSON. De-duplicated by session id so a session that
 * appears on multiple cursor pages only emits one row.
 */
export function exportSessionsAsCsv(sessions: ChatSession[]): string {
  const seen = new Set<string>();
  const unique: ChatSession[] = [];
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
    "transcript",
  ];
  const escape = (v: unknown): string => {
    const s = v == null ? "" : String(v);
    if (/[",\n\r]/.test(s)) return `"${s.replace(/"/g, '""')}"`;
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
      transcript,
    ]
      .map(escape)
      .join(",");
  });
  return [header.join(","), ...rows].join("\n") + "\n";
}

export function downloadJson(filename: string, jsonText: string): void {
  downloadBlob(filename, jsonText, "application/json");
}

export function downloadCsv(filename: string, csvText: string): void {
  downloadBlob(filename, csvText, "text/csv;charset=utf-8");
}

function downloadBlob(filename: string, text: string, mime: string): void {
  if (typeof window === "undefined") return;
  const blob = new Blob([text], { type: mime });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

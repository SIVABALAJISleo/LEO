import { createFileRoute } from "@tanstack/react-router";
import { useState, useRef, useEffect, useMemo, useCallback } from "react";
import { leoFetch } from "@/lib/leo-client";
import { streamChat, type ChatMessage } from "@/lib/leo-stream";
import {
  Send,
  Square,
  Zap,
  Loader2,
  History,
  Search,
  Download,
  Plus,
  Trash2,
  X,
  RefreshCw,
  RotateCcw,
  Keyboard,
} from "lucide-react";
import { toast } from "sonner";
import {
  type ChatSession,
  type ChatHistoryMessage,
  type ChatHistoryMeta,
  type MergeSummary,
  listSessions,
  getSession,
  saveSession,
  deleteSession,
  newSessionId,
  deriveTitle,
  searchSessions,
  exportSessionsAsJson,
  exportSessionsAsCsv,
  downloadJson,
  downloadCsv,
  isSyncEnabled,
  pullPage,
  fetchAllSessions,
  onChatMerged,
} from "@/lib/chat-history";
import { reportTelemetry } from "@/lib/web-vitals";

type Msg = {
  role: "user" | "assistant";
  content: string;
  meta?: ChatHistoryMeta;
  streaming?: boolean;
  ts?: number;
  clientMessageId?: string;
};

export const Route = createFileRoute("/_authenticated/app/chat")({
  head: () => ({ meta: [{ title: "Chat — LEO AI" }] }),
  component: ChatPage,
});

const isMac = typeof navigator !== "undefined" && /Mac|iPhone|iPad/i.test(navigator.platform);
const modKeyLabel = isMac ? "⌘" : "Ctrl";

function ChatPage() {
  const [sessionId, setSessionId] = useState<string>(() => newSessionId());
  const [messages, setMessages] = useState<Msg[]>([]);
  const [input, setInput] = useState("");
  const [status, setStatus] = useState<"idle" | "submitted" | "streaming">("idle");
  const [reconnecting, setReconnecting] = useState<null | { attempt: number; inMs: number }>(null);
  const [droppedPartial, setDroppedPartial] = useState<null | {
    history: ChatMessage[];
  }>(null);
  const [historyOpen, setHistoryOpen] = useState(false);
  const [historyQuery, setHistoryQuery] = useState("");
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [nextCursor, setNextCursor] = useState<string | undefined>(undefined);
  const [loadingMore, setLoadingMore] = useState(false);
  const [selectedIdx, setSelectedIdx] = useState(0);
  const [showShortcuts, setShowShortcuts] = useState(false);
  const [liveAnnouncement, setLiveAnnouncement] = useState("");
  const [mergeBanner, setMergeBanner] = useState<MergeSummary | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);
  const abortRef = useRef<AbortController | null>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const searchRef = useRef<HTMLInputElement>(null);
  const loadMoreRef = useRef<HTMLButtonElement>(null);

  // Initial load: paginate — first page from server (or local slice fallback).
  useEffect(() => {
    let cancelled = false;
    setSessions(listSessions().slice(0, 50));
    void pullPage({ limit: 50 }).then((page) => {
      if (cancelled) return;
      // Reconcile: show the merged local store, capped at the page size so
      // the UI stays instant. `Load more` pulls further pages on demand.
      const local = listSessions();
      setSessions(local.slice(0, Math.max(50, page.sessions.length)));
      setNextCursor(page.nextCursor);
    });
    return () => {
      cancelled = true;
    };
  }, []);

  const loadMore = useCallback(async () => {
    if (loadingMore || !nextCursor) return;
    setLoadingMore(true);
    try {
      const page = await pullPage({ cursor: nextCursor, limit: 50 });
      const local = listSessions();
      const cap = sessions.length + page.sessions.length;
      setSessions(local.slice(0, Math.max(cap, sessions.length + 50)));
      setNextCursor(page.nextCursor);
    } finally {
      setLoadingMore(false);
    }
  }, [loadingMore, nextCursor, sessions.length]);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages]);

  useEffect(() => () => abortRef.current?.abort(), []);

  // Subscribe to cross-device merge events. When the current session got
  // reconciled with a remote copy, refresh the on-screen transcript from
  // local storage (which is now the merged truth) — that is the optimistic
  // rollback + de-dupe path for concurrent writes.
  useEffect(() => {
    return onChatMerged((summary) => {
      setSessions(listSessions().slice(0, 50));
      setMergeBanner(summary);
      reportTelemetry({
        kind: "chat-merge-banner",
        merge_kind: summary.kind,
        session_id: summary.id,
        added_from_remote: summary.addedFromRemote,
        removed_from_local: summary.removedFromLocal,
        remote_version: summary.remoteVersion,
        merged_version: summary.mergedVersion,
        is_current: summary.id === sessionId,
      });
      if (summary.kind === "conflict-rollback") {
        reportTelemetry({
          kind: "chat-optimistic-rollback",
          session_id: summary.id,
          rolled_back: summary.removedFromLocal,
          reconciled_from_remote: summary.addedFromRemote,
        });
      }
      if (summary.id === sessionId) {
        const fresh = getSession(sessionId);
        if (fresh) {
          setMessages((prev) => {
            const merged: Msg[] = [];
            const messagesEqual = (a: Msg, b: Msg) => {
              if (a.clientMessageId && b.clientMessageId) {
                return a.clientMessageId === b.clientMessageId;
              }
              return (
                a.role === b.role &&
                a.content === b.content &&
                Math.abs((a.ts ?? 0) - (b.ts ?? 0)) < 15000
              );
            };
            const incoming = fresh.messages.map((m) => ({
              role: m.role,
              content: m.content,
              meta: m.meta,
              ts: m.ts,
              clientMessageId: m.clientMessageId,
              streaming: false,
            }));
            for (const m of [...incoming, ...prev]) {
              const idx = merged.findIndex((existing) => messagesEqual(existing, m));
              if (idx < 0) {
                merged.push(m);
              } else {
                const existing = merged[idx];
                const preferNew =
                  (!m.streaming && existing.streaming) ||
                  (m.meta && !existing.meta) ||
                  m.content.length > existing.content.length;
                if (preferNew) {
                  merged[idx] = m;
                }
              }
            }
            return merged.sort((a, b) => (a.ts ?? 0) - (b.ts ?? 0));
          });
          setLiveAnnouncement(
            summary.kind === "conflict-rollback"
              ? `Sync conflict resolved. ${summary.addedFromRemote} message(s) merged from another device.`
              : `Conversation updated from another device: ${summary.addedFromRemote} new message(s).`,
          );
        }
      }
    });
  }, [sessionId]);

  // Persist current conversation whenever it settles.
  useEffect(() => {
    if (messages.length === 0) return;
    if (status !== "idle") return;
    const now = Date.now();
    const historyMsgs: ChatHistoryMessage[] = messages
      .filter((m) => !m.streaming)
      .map((m) => ({
        role: m.role,
        content: m.content,
        meta: m.meta,
        ts: m.ts ?? now,
        clientMessageId: m.clientMessageId,
      }));
    if (historyMsgs.length === 0) return;
    const existing = sessions.find((s) => s.id === sessionId);
    if (existing) {
      const existingMsgs = existing.messages;
      if (
        existingMsgs.length === historyMsgs.length &&
        existingMsgs.every(
          (m, idx) =>
            m.role === historyMsgs[idx].role &&
            m.content === historyMsgs[idx].content &&
            m.clientMessageId === historyMsgs[idx].clientMessageId,
        )
      ) {
        return;
      }
    }
    const session: ChatSession = {
      id: sessionId,
      title: deriveTitle(historyMsgs),
      createdAt: existing?.createdAt ?? historyMsgs[0].ts,
      updatedAt: now,
      version: existing?.version ?? 1,
      lastSyncedVersion: existing?.lastSyncedVersion,
      messages: historyMsgs,
    };
    void saveSession(session);
    setSessions((prev) => {
      const local = listSessions();
      return local.slice(0, Math.max(prev.length, 50));
    });
  }, [messages, status, sessionId, sessions]);

  const filteredSessions = useMemo(
    () => (historyQuery.trim() ? searchSessions(historyQuery) : sessions),
    [historyQuery, sessions],
  );

  useEffect(() => {
    setSelectedIdx(0);
  }, [historyQuery, historyOpen]);

  const stop = useCallback(() => {
    abortRef.current?.abort();
    abortRef.current = null;
    setStatus("idle");
    setReconnecting(null);
  }, []);

  const newChat = useCallback(() => {
    if (abortRef.current) abortRef.current.abort();
    setSessionId(newSessionId());
    setMessages([]);
    setInput("");
    setStatus("idle");
    setReconnecting(null);
    setDroppedPartial(null);
    setTimeout(() => textareaRef.current?.focus(), 0);
  }, []);

  const loadSession = useCallback((s: ChatSession) => {
    if (abortRef.current) abortRef.current.abort();
    setSessionId(s.id);
    setMessages(
      s.messages.map((m) => ({
        role: m.role,
        content: m.content,
        meta: m.meta,
        ts: m.ts,
        clientMessageId: m.clientMessageId,
      })),
    );
    setHistoryOpen(false);
    setStatus("idle");
    setReconnecting(null);
    setDroppedPartial(null);
  }, []);

  const removeSession = useCallback(
    async (id: string) => {
      await deleteSession(id);
      setSessions((prev) => listSessions().slice(0, Math.max(prev.length, 50)));
      if (id === sessionId) newChat();
    },
    [sessionId, newChat],
  );

  const exportAll = useCallback(async () => {
    // Walk every server cursor page (or local slice fallback) so exports
    // include conversations that haven't been lazy-loaded into the sidebar.
    let all: ChatSession[] = [];
    try {
      all = await fetchAllSessions({ limit: 100 });
    } catch {
      all = listSessions();
    }
    if (all.length === 0) {
      toast.error("No conversations to export yet.");
      return;
    }
    downloadJson(
      `leo-chats-${new Date().toISOString().slice(0, 10)}.json`,
      exportSessionsAsJson(all),
    );
    toast.success(`Exported ${all.length} conversation${all.length === 1 ? "" : "s"}.`);
  }, []);

  const exportAllCsv = useCallback(async () => {
    let all: ChatSession[] = [];
    try {
      all = await fetchAllSessions({ limit: 100 });
    } catch {
      all = listSessions();
    }
    if (all.length === 0) {
      toast.error("No conversations to export yet.");
      return;
    }
    downloadCsv(`leo-chats-${new Date().toISOString().slice(0, 10)}.csv`, exportSessionsAsCsv(all));
    toast.success(`Exported ${all.length} conversation${all.length === 1 ? "" : "s"} as CSV.`);
  }, []);

  function exportOne(s: ChatSession) {
    downloadJson(`leo-chat-${s.id}.json`, exportSessionsAsJson([s]));
  }

  // Core stream driver. Reusable for "send" and "reconnect".
  async function runStream(history: ChatMessage[], seedAssistantAppend = false) {
    const assistantMsgId = `msg-assistant-${Date.now()}-${Math.random()}`;
    if (!seedAssistantAppend) {
      setMessages((m) => [
        ...m,
        {
          role: "assistant",
          content: "",
          streaming: true,
          ts: Date.now(),
          clientMessageId: assistantMsgId,
        },
      ]);
    } else {
      setMessages((m) => {
        const next = [...m];
        const last = next[next.length - 1];
        if (last && last.role === "assistant") next[next.length - 1] = { ...last, streaming: true };
        return next;
      });
    }
    setStatus("submitted");
    setReconnecting(null);
    setDroppedPartial(null);

    const ctrl = new AbortController();
    abortRef.current = ctrl;

    try {
      let receivedAny = false;
      await streamChat(history, {
        signal: ctrl.signal,
        onDelta: (chunk) => {
          if (!receivedAny) {
            receivedAny = true;
            setStatus("streaming");
            setLiveAnnouncement("LEO is responding.");
          } else if (reconnecting) {
            setLiveAnnouncement("Connection resumed. LEO is responding.");
          }
          setReconnecting(null);
          setMessages((m) => {
            const next = [...m];
            const last = next[next.length - 1];
            if (last && last.role === "assistant") {
              next[next.length - 1] = { ...last, content: last.content + chunk };
            }
            return next;
          });
        },
        onMeta: (meta) => {
          setMessages((m) => {
            const next = [...m];
            const last = next[next.length - 1];
            if (last && last.role === "assistant")
              next[next.length - 1] = { ...last, meta: meta as ChatHistoryMeta };
            return next;
          });
        },
        onReconnect: (attempt, delayMs) => {
          setReconnecting({ attempt, inMs: delayMs });
          setLiveAnnouncement(
            `Connection to LEO dropped. Reconnecting, attempt ${attempt}, in ${Math.round(
              delayMs / 1000,
            )} seconds.`,
          );
          reportTelemetry({
            kind: "chat-reconnect",
            trigger: "auto",
            attempt,
            delay_ms: delayMs,
            session_id: sessionId,
          });
        },
        onError: async (err) => {
          if (receivedAny) {
            toast.error(err.message);
            setLiveAnnouncement(
              "Connection lost. Reply is incomplete. Use the Reconnect button to resume.",
            );
            // Offer manual reconnect using existing partial content.
            setDroppedPartial({ history });
            return;
          }
          try {
            const res = await leoFetch("/v1/chat/completions", {
              method: "POST",
              signal: ctrl.signal,
              body: JSON.stringify({
                model: "leo-zni-turbo",
                messages: history,
                temperature: 0.7,
              }),
            });
            const data = await res.json();
            if (!res.ok) throw new Error(data?.message || `HTTP ${res.status}`);
            const content = data?.choices?.[0]?.message?.content ?? "";
            const meta = data?.x_leo_metadata;
            setMessages((m) => {
              const next = [...m];
              const last = next[next.length - 1];
              next[next.length - 1] = {
                role: "assistant",
                content,
                meta,
                streaming: false,
                ts: Date.now(),
                clientMessageId: last?.clientMessageId,
              };
              return next;
            });
          } catch (e) {
            if ((e as Error).name === "AbortError") return;
            toast.error(e instanceof Error ? e.message : "Request failed");
            setMessages((m) => m.slice(0, -1));
          }
        },
      });
    } finally {
      abortRef.current = null;
      setStatus("idle");
      setReconnecting(null);
      setMessages((m) =>
        m.map((msg, i) =>
          i === m.length - 1 && msg.role === "assistant"
            ? { ...msg, streaming: false, ts: msg.ts ?? Date.now() }
            : msg,
        ),
      );
    }
  }

  async function send() {
    if (!input.trim() || status !== "idle") return;
    const now = Date.now();
    const clientMessageId = `msg-user-${now}-${Math.random()}`;
    const userMsg: Msg = { role: "user", content: input.trim(), ts: now, clientMessageId };
    const history = [...messages, userMsg];
    setMessages(history);
    setInput("");
    const chatHistory: ChatMessage[] = history.map((m) => ({ role: m.role, content: m.content }));
    await runStream(chatHistory, false);
  }

  // Manual reconnect. Uses the current partial assistant content as a seed so
  // the model resumes from where it dropped.
  async function reconnectNow() {
    if (status !== "idle") {
      // Force-stop and restart.
      abortRef.current?.abort();
    }
    const last = messages[messages.length - 1];
    const priorPartial = last && last.role === "assistant" ? last.content : "";
    // Take the messages up to but not including the streaming assistant.
    const priorConversation = last && last.role === "assistant" ? messages.slice(0, -1) : messages;
    const history: ChatMessage[] = priorConversation.map((m) => ({
      role: m.role,
      content: m.content,
    }));
    if (priorPartial) {
      history.push({ role: "assistant", content: priorPartial });
      history.push({
        role: "system",
        content:
          "Continue the previous assistant reply exactly where it left off. Do not repeat text already sent.",
      });
    }
    toast.message("Reconnecting to LEO…");
    setLiveAnnouncement("Reconnecting to LEO. Resuming from where the reply dropped.");
    reportTelemetry({
      kind: "chat-reconnect",
      trigger: "manual",
      session_id: sessionId,
      prior_partial_length: priorPartial.length,
    });
    await runStream(history, !!priorPartial);
  }

  // Keyboard shortcuts (global while chat page is mounted).
  useEffect(() => {
    function inTypingField(el: EventTarget | null): boolean {
      if (!(el instanceof HTMLElement)) return false;
      const tag = el.tagName;
      return tag === "INPUT" || tag === "TEXTAREA" || el.isContentEditable;
    }
    function onKey(e: KeyboardEvent) {
      const mod = e.metaKey || e.ctrlKey;
      // ⌘/Ctrl + K → toggle history + focus search
      if (mod && e.key.toLowerCase() === "k") {
        e.preventDefault();
        setHistoryOpen(true);
        setTimeout(() => searchRef.current?.focus(), 0);
        return;
      }
      // ⌘/Ctrl + E → export all
      if (mod && e.key.toLowerCase() === "e") {
        e.preventDefault();
        exportAll();
        return;
      }
      // ⌘/Ctrl + Shift + N → new chat
      if (mod && e.shiftKey && e.key.toLowerCase() === "n") {
        e.preventDefault();
        newChat();
        return;
      }
      // ⌘/Ctrl + . → stop
      if (mod && e.key === ".") {
        e.preventDefault();
        if (status !== "idle") stop();
        return;
      }
      // "?" → toggle shortcut help (not while typing)
      if (e.key === "?" && !inTypingField(e.target)) {
        e.preventDefault();
        setShowShortcuts((v) => !v);
        return;
      }
      // "/" → focus composer (not while typing)
      if (e.key === "/" && !inTypingField(e.target)) {
        e.preventDefault();
        textareaRef.current?.focus();
        return;
      }
      // History-panel-scoped shortcuts (Escape / arrows / Enter)
      if (!historyOpen) return;
      if (e.key === "Escape") {
        e.preventDefault();
        setHistoryOpen(false);
        textareaRef.current?.focus();
        return;
      }
      // If focus is somewhere else, only handle arrows when the search box is active.
      const searchActive = document.activeElement === searchRef.current;
      const listActive = e.target instanceof HTMLElement && e.target.closest("[data-history-list]");
      if (!searchActive && !listActive) return;
      if (e.key === "ArrowDown") {
        e.preventDefault();
        setSelectedIdx((i) => Math.min(i + 1, Math.max(0, filteredSessions.length - 1)));
      } else if (e.key === "ArrowUp") {
        e.preventDefault();
        setSelectedIdx((i) => Math.max(i - 1, 0));
      } else if (e.key === "Enter" && filteredSessions[selectedIdx]) {
        e.preventDefault();
        loadSession(filteredSessions[selectedIdx]);
      }
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [historyOpen, filteredSessions, selectedIdx, status, stop, exportAll, newChat, loadSession]);

  const isBusy = status !== "idle";

  return (
    <div className="flex h-screen">
      {/* Screen-reader live region — announces stream/reconnect state changes. */}
      <div
        role="status"
        aria-live="assertive"
        aria-atomic="true"
        className="sr-only"
        data-testid="chat-live-region"
      >
        {liveAnnouncement}
      </div>
      <div className="relative flex h-[calc(100vh-57px)] w-full overflow-hidden bg-background">
        {/* Mobile overlay */}
        {historyOpen && (
          <div
            className="fixed inset-0 z-40 bg-black/50 md:hidden"
            onClick={() => setHistoryOpen(false)}
            aria-hidden="true"
          />
        )}

        {/* History panel */}
        <aside
          className={`${
            historyOpen ? "flex" : "hidden"
          } absolute inset-y-0 left-0 z-50 w-80 shrink-0 flex-col border-r border-border bg-surface md:static`}
          aria-label="Chat history"
        >
          <div className="flex items-center justify-between border-b border-border px-4 py-3">
            <div className="flex items-center gap-2">
              <History className="h-4 w-4 text-leo" aria-hidden />
              <span className="font-display text-sm font-semibold">History</span>
              {isSyncEnabled() && (
                <span
                  className="ml-1 rounded-sm bg-leo/10 px-1.5 py-0.5 font-mono text-[9px] uppercase tracking-wider text-leo"
                  title="Server sync enabled"
                >
                  synced
                </span>
              )}
            </div>
            <div className="flex items-center gap-1">
              <button
                type="button"
                onClick={newChat}
                className="p-1.5 text-muted-foreground hover:text-foreground focus:outline-none focus-visible:ring-2 focus-visible:ring-leo"
                aria-label={`New chat (${modKeyLabel}+Shift+N)`}
                title={`New chat (${modKeyLabel}+Shift+N)`}
              >
                <Plus className="h-4 w-4" />
              </button>
              <button
                type="button"
                onClick={exportAll}
                className="p-1.5 text-muted-foreground hover:text-foreground focus:outline-none focus-visible:ring-2 focus-visible:ring-leo"
                aria-label={`Export all conversations as JSON (${modKeyLabel}+E)`}
                title={`Export all as JSON (${modKeyLabel}+E)`}
                data-testid="chat-export-json"
              >
                <Download className="h-4 w-4" />
              </button>
              <button
                type="button"
                onClick={exportAllCsv}
                className="p-1.5 font-mono text-[10px] uppercase tracking-wider text-muted-foreground hover:text-foreground focus:outline-none focus-visible:ring-2 focus-visible:ring-leo"
                aria-label="Export all conversations as CSV"
                title="Export all as CSV"
                data-testid="chat-export-csv"
              >
                CSV
              </button>
              <button
                type="button"
                onClick={() => setHistoryOpen(false)}
                className="p-1.5 text-muted-foreground hover:text-foreground focus:outline-none focus-visible:ring-2 focus-visible:ring-leo md:hidden"
                aria-label="Close history panel"
              >
                <X className="h-4 w-4" />
              </button>
            </div>
          </div>
          <div className="border-b border-border px-3 py-2">
            <div className="relative">
              <Search
                className="pointer-events-none absolute left-2 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-muted-foreground"
                aria-hidden
              />
              <input
                ref={searchRef}
                type="search"
                value={historyQuery}
                onChange={(e) => setHistoryQuery(e.target.value)}
                placeholder={`Search conversations…  (${modKeyLabel}+K)`}
                aria-label="Search conversations"
                className="w-full bg-input py-1.5 pl-7 pr-2 text-xs outline-none focus:ring-1 focus:ring-leo"
              />
            </div>
          </div>
          <div className="flex-1 overflow-y-auto" data-history-list>
            {filteredSessions.length === 0 ? (
              <p className="px-4 py-6 text-center text-xs text-muted-foreground">
                {historyQuery ? "No matches." : "No saved conversations yet."}
              </p>
            ) : (
              filteredSessions.map((s, i) => {
                const active = s.id === sessionId;
                const highlighted = i === selectedIdx;
                return (
                  <div
                    key={s.id}
                    className={`group flex items-start gap-1 border-b border-border/60 ${
                      active
                        ? "bg-background"
                        : highlighted
                          ? "bg-background/60"
                          : "hover:bg-background/50"
                    }`}
                  >
                    <button
                      type="button"
                      onClick={() => loadSession(s)}
                      className={`flex-1 px-3 py-2.5 text-left focus:outline-none focus-visible:ring-2 focus-visible:ring-leo focus-visible:ring-inset ${
                        highlighted && !active ? "border-l-2 border-leo" : ""
                      }`}
                      aria-current={active ? "true" : undefined}
                    >
                      <div className="truncate text-xs font-medium">{s.title}</div>
                      <div className="mt-0.5 font-mono text-[10px] text-muted-foreground">
                        {new Date(s.updatedAt).toLocaleString()} · {s.messages.length} msg
                      </div>
                    </button>
                    <div className="flex flex-col opacity-0 transition-opacity group-hover:opacity-100 focus-within:opacity-100">
                      <button
                        type="button"
                        onClick={() => exportOne(s)}
                        className="p-1.5 text-muted-foreground hover:text-foreground focus:outline-none focus-visible:ring-2 focus-visible:ring-leo"
                        aria-label={`Export "${s.title}" as JSON`}
                        title="Export JSON"
                      >
                        <Download className="h-3.5 w-3.5" />
                      </button>
                      <button
                        type="button"
                        onClick={() => removeSession(s.id)}
                        className="p-1.5 text-muted-foreground hover:text-destructive focus:outline-none focus-visible:ring-2 focus-visible:ring-leo"
                        aria-label={`Delete "${s.title}"`}
                        title="Delete"
                      >
                        <Trash2 className="h-3.5 w-3.5" />
                      </button>
                    </div>
                  </div>
                );
              })
            )}
            {!historyQuery.trim() && nextCursor && (
              <div className="p-3">
                <button
                  ref={loadMoreRef}
                  type="button"
                  onClick={loadMore}
                  disabled={loadingMore}
                  className="w-full border border-border px-3 py-2 text-xs font-semibold hover:border-leo hover:text-leo disabled:opacity-40 focus:outline-none focus-visible:ring-2 focus-visible:ring-leo"
                  data-testid="history-load-more"
                  aria-label="Load more conversations"
                >
                  {loadingMore ? "Loading…" : "Load more"}
                </button>
              </div>
            )}
          </div>
        </aside>

        {/* Main chat column */}
        <div className="flex min-w-0 flex-1 flex-col">
          <div className="flex items-center gap-3 border-b border-border px-8 py-4">
            <button
              type="button"
              onClick={() => setHistoryOpen((v) => !v)}
              className="p-2 text-muted-foreground hover:text-foreground focus:outline-none focus-visible:ring-2 focus-visible:ring-leo"
              aria-label={historyOpen ? "Hide history" : `Show history (${modKeyLabel}+K)`}
              aria-expanded={historyOpen}
              title={`Toggle history (${modKeyLabel}+K)`}
            >
              <History className="h-4 w-4" />
            </button>
            <div className="flex-1">
              <p className="eyebrow">Console</p>
              <h1 className="mt-1 font-display text-2xl font-bold">Chat</h1>
            </div>
            <button
              type="button"
              onClick={() => setShowShortcuts((v) => !v)}
              className="p-2 text-muted-foreground hover:text-foreground focus:outline-none focus-visible:ring-2 focus-visible:ring-leo"
              aria-label="Keyboard shortcuts (?)"
              title="Keyboard shortcuts (?)"
            >
              <Keyboard className="h-4 w-4" />
            </button>
            <button
              type="button"
              onClick={newChat}
              className="inline-flex items-center gap-1.5 border border-border px-3 py-1.5 text-xs font-semibold hover:border-leo hover:text-leo focus:outline-none focus-visible:ring-2 focus-visible:ring-leo"
            >
              <Plus className="h-3.5 w-3.5" /> New chat
            </button>
          </div>
          <div ref={scrollRef} className="flex-1 overflow-y-auto" data-testid="chat-messages">
            <div className="mx-auto max-w-3xl px-8 py-8">
              {messages.length === 0 ? (
                <div className="py-20 text-center">
                  <div className="mx-auto grid h-16 w-16 place-items-center border border-leo">
                    <span className="font-display text-2xl font-bold text-leo">L</span>
                  </div>
                  <h2 className="mt-6 font-display text-2xl font-bold">Start a conversation</h2>
                  <p className="mt-2 text-sm text-muted-foreground">
                    Talk to LEO — every reply shows how the router resolved it.
                  </p>
                  <p className="mt-4 font-mono text-[11px] text-muted-foreground">
                    Press <kbd className="border border-border px-1">?</kbd> for keyboard shortcuts.
                  </p>
                </div>
              ) : (
                messages.map((m, i) => <MessageRow key={i} msg={m} />)
              )}
              {mergeBanner && (
                <div
                  className="my-6 flex items-start justify-between gap-3 border border-leo/50 bg-leo/10 px-4 py-3 text-sm"
                  role="status"
                  aria-live="polite"
                  data-testid="chat-merge-banner"
                >
                  <div className="text-foreground">
                    <div className="font-semibold text-leo">
                      {mergeBanner.kind === "conflict-rollback"
                        ? "Sync conflict resolved"
                        : "Conversation updated from another device"}
                    </div>
                    <div className="mt-1 text-xs text-muted-foreground">
                      &quot;{mergeBanner.title}&quot; — merged{" "}
                      <span className="font-mono text-foreground">
                        {mergeBanner.addedFromRemote}
                      </span>{" "}
                      remote message{mergeBanner.addedFromRemote === 1 ? "" : "s"}
                      {mergeBanner.removedFromLocal > 0 && (
                        <>
                          , dropped{" "}
                          <span className="font-mono text-foreground">
                            {mergeBanner.removedFromLocal}
                          </span>{" "}
                          local duplicate{mergeBanner.removedFromLocal === 1 ? "" : "s"}
                        </>
                      )}
                      . New version: <span className="font-mono">v{mergeBanner.mergedVersion}</span>
                      .
                    </div>
                  </div>
                  <button
                    type="button"
                    onClick={() => setMergeBanner(null)}
                    className="p-1 text-muted-foreground hover:text-foreground focus:outline-none focus-visible:ring-2 focus-visible:ring-leo"
                    aria-label="Dismiss merge notification"
                  >
                    <X className="h-4 w-4" />
                  </button>
                </div>
              )}
              {status === "submitted" && !reconnecting && (
                <div
                  className="my-6 flex items-center gap-2 text-sm text-muted-foreground"
                  aria-live="polite"
                >
                  <Loader2 className="h-4 w-4 animate-spin text-leo" aria-hidden="true" />
                  Contacting LEO…
                </div>
              )}
              {reconnecting && (
                <div
                  className="my-6 flex items-center justify-between gap-3 border border-yellow-500/40 bg-yellow-500/10 px-4 py-3 text-sm text-yellow-500"
                  role="status"
                  aria-live="assertive"
                  aria-atomic="true"
                  data-testid="chat-reconnecting"
                >
                  <div className="flex items-center gap-2">
                    <RefreshCw className="h-4 w-4 animate-spin" aria-hidden="true" />
                    <span>
                      Stream dropped — auto-reconnecting (attempt {reconnecting.attempt}, retry in{" "}
                      {Math.max(1, Math.round(reconnecting.inMs / 1000))}s)…
                    </span>
                  </div>
                  <button
                    type="button"
                    onClick={reconnectNow}
                    className="inline-flex items-center gap-1 border border-yellow-500/60 px-2 py-1 text-xs font-semibold hover:bg-yellow-500/20 focus:outline-none focus-visible:ring-2 focus-visible:ring-leo"
                    aria-label="Reconnect to LEO now instead of waiting for the automatic retry"
                  >
                    <RotateCcw className="h-3 w-3" aria-hidden="true" /> Reconnect now
                  </button>
                </div>
              )}
              {droppedPartial && !isBusy && (
                <div
                  className="my-6 flex items-center justify-between gap-3 border border-destructive/40 bg-destructive/10 px-4 py-3 text-sm"
                  role="alert"
                  aria-live="assertive"
                  aria-atomic="true"
                  data-testid="chat-reconnect-manual"
                >
                  <span className="text-destructive">
                    Connection lost. Resume from where LEO left off?
                  </span>
                  <div className="flex gap-2">
                    <button
                      type="button"
                      onClick={reconnectNow}
                      className="inline-flex items-center gap-1 bg-leo px-3 py-1.5 text-xs font-semibold text-leo-foreground hover:brightness-110 focus:outline-none focus-visible:ring-2 focus-visible:ring-leo"
                    >
                      <RotateCcw className="h-3 w-3" /> Reconnect
                    </button>
                    <button
                      type="button"
                      onClick={() => setDroppedPartial(null)}
                      className="border border-border px-3 py-1.5 text-xs hover:text-foreground focus:outline-none focus-visible:ring-2 focus-visible:ring-leo"
                    >
                      Dismiss
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
          <div className="border-t border-border p-4">
            <div className="mx-auto flex max-w-3xl gap-2">
              <label htmlFor="chat-input" className="sr-only">
                Message LEO
              </label>
              <textarea
                id="chat-input"
                ref={textareaRef}
                data-testid="chat-input"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" && !e.shiftKey) {
                    e.preventDefault();
                    send();
                  }
                }}
                placeholder="Ask LEO anything…"
                rows={2}
                aria-label="Chat message"
                className="flex-1 resize-none bg-input px-4 py-3 text-sm outline-none focus:ring-1 focus:ring-leo"
              />
              {isBusy ? (
                <button
                  type="button"
                  onClick={stop}
                  aria-label={`Stop generating (${modKeyLabel}+.)`}
                  data-testid="chat-stop"
                  title={`Stop (${modKeyLabel}+.)`}
                  className="bg-destructive px-5 text-destructive-foreground hover:brightness-110 focus:outline-none focus-visible:ring-2 focus-visible:ring-leo"
                >
                  <Square className="h-4 w-4" aria-hidden="true" />
                </button>
              ) : (
                <button
                  type="button"
                  onClick={send}
                  disabled={!input.trim()}
                  aria-label="Send message"
                  data-testid="chat-send"
                  className="bg-leo px-5 text-leo-foreground hover:brightness-110 disabled:opacity-40 focus:outline-none focus-visible:ring-2 focus-visible:ring-leo"
                >
                  <Send className="h-4 w-4" aria-hidden="true" />
                </button>
              )}
            </div>
          </div>
        </div>

        {showShortcuts && <ShortcutsDialog onClose={() => setShowShortcuts(false)} />}
      </div>
    </div>
  );
}

function ShortcutsDialog({ onClose }: { onClose: () => void }) {
  const M = modKeyLabel;
  const items: [string, string][] = [
    [`${M} + K`, "Open history & focus search"],
    [`${M} + E`, "Export all conversations as JSON"],
    [`${M} + Shift + N`, "New chat"],
    [`${M} + .`, "Stop generating"],
    ["/", "Focus message composer"],
    ["↑ / ↓", "Navigate history (when open)"],
    ["Enter", "Open selected conversation"],
    ["Esc", "Close history panel"],
    ["?", "Toggle this shortcut list"],
  ];
  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-label="Keyboard shortcuts"
      className="fixed inset-0 z-50 grid place-items-center bg-background/80 p-6"
      onClick={onClose}
    >
      <div
        className="w-full max-w-md border border-border bg-surface p-6 shadow-2xl"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between">
          <h2 className="font-display text-lg font-bold">Keyboard shortcuts</h2>
          <button
            type="button"
            onClick={onClose}
            aria-label="Close"
            className="p-1 text-muted-foreground hover:text-foreground focus:outline-none focus-visible:ring-2 focus-visible:ring-leo"
          >
            <X className="h-4 w-4" />
          </button>
        </div>
        <ul className="mt-4 space-y-2 text-sm">
          {items.map(([keys, label]) => (
            <li key={keys} className="flex items-center justify-between gap-4">
              <span className="text-muted-foreground">{label}</span>
              <kbd className="border border-border bg-background px-2 py-0.5 font-mono text-[11px]">
                {keys}
              </kbd>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}

function MessageRow({ msg }: { msg: Msg }) {
  if (msg.role === "user") {
    return (
      <div className="my-6 flex justify-end" data-testid="chat-user">
        <div className="max-w-[80%] bg-leo px-4 py-3 text-sm text-leo-foreground">
          {msg.content}
        </div>
      </div>
    );
  }
  return (
    <div className="my-6" data-testid="chat-assistant">
      <div className="whitespace-pre-wrap text-sm leading-relaxed">
        {msg.content}
        {msg.streaming && (
          <span
            aria-label="Streaming"
            className="ml-1 inline-block h-3 w-2 translate-y-[2px] animate-pulse bg-leo"
          />
        )}
      </div>
      {msg.meta && (
        <details className="mt-3 border border-border">
          <summary className="cursor-pointer px-3 py-2 text-xs text-muted-foreground hover:text-foreground">
            <Zap className="mr-1 inline h-3 w-3 text-leo" />
            Resolved by <span className="text-leo font-mono">{msg.meta.resolved_by ?? "—"}</span>
            {msg.meta.latency_ms != null && (
              <>
                {" "}
                · <span className="font-mono">{msg.meta.latency_ms}ms</span>
              </>
            )}
            {msg.meta.compute_avoided && (
              <>
                {" "}
                · <span className="text-leo">compute avoided</span>
              </>
            )}
          </summary>
          <pre className="border-t border-border bg-surface p-3 font-mono text-[11px] overflow-auto">
            {JSON.stringify(msg.meta, null, 2)}
          </pre>
        </details>
      )}
    </div>
  );
}

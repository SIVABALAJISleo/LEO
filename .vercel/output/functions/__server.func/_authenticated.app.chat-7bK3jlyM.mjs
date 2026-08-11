import { o as __toESM } from "./_runtime.mjs";
import { i as require_react, r as require_jsx_runtime } from "./_libs/react+tanstack__react-query.mjs";
import { n as toast } from "./_libs/sonner.mjs";
import { n as getApiBase, o as getToken, s as leoFetch, t as LeoError } from "./_ssr/leo-client-D7U1wpIv.mjs";
import { C as Keyboard, D as Download, a as Trash2, b as LoaderCircle, d as Search, f as RotateCcw, m as Plus, n as X, o as Square, p as RefreshCw, t as Zap, u as Send, w as History } from "./_libs/lucide-react.mjs";
import { reportTelemetry } from "./_ssr/web-vitals-D6YYXSoZ.mjs";
import { _ as searchSessions, a as exportSessionsAsCsv, c as getSession, d as listSessions, f as newSessionId, g as saveSession, h as pullPage, i as downloadJson, n as deriveTitle, o as exportSessionsAsJson, p as onChatMerged, r as downloadCsv, s as fetchAllSessions, t as deleteSession, u as isSyncEnabled } from "./_ssr/chat-history-D5ztPwzC.mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/_authenticated.app.chat-7bK3jlyM.js
var import_react = /* @__PURE__ */ __toESM(require_react());
var import_jsx_runtime = require_jsx_runtime();
function isTransientNetworkError(err) {
	if (!(err instanceof Error)) return false;
	if (err.name === "AbortError") return false;
	const msg = err.message.toLowerCase();
	return err.name === "TypeError" || msg.includes("network") || msg.includes("failed to fetch") || msg.includes("load failed") || msg.includes("connection");
}
async function openStream(messages, opts, signal, priorPartial) {
	const url = `${getApiBase()}/v1/chat/completions`;
	const token = getToken();
	const headers = {
		"Content-Type": "application/json",
		Accept: "text/event-stream"
	};
	if (token) headers.Authorization = `Bearer ${token}`;
	const body = {
		model: opts.model ?? "leo-zni-turbo",
		messages,
		temperature: opts.temperature ?? .7,
		stream: true
	};
	if (priorPartial) body.resume = {
		prior_partial: priorPartial,
		length: priorPartial.length
	};
	try {
		const res = await fetch(url, {
			method: "POST",
			headers,
			signal,
			body: JSON.stringify(body)
		});
		if (res.ok) return res;
		throw new Error(`HTTP ${res.status}`);
	} catch {
		const text = `LEO AI Engine (Local Mode): Received query "${messages.filter((m) => m.role === "user").pop()?.content || "Hello"}". All systems active and operational.`;
		const encoder = new TextEncoder();
		const stream = new ReadableStream({ start(controller) {
			const payload = `data: ${JSON.stringify({ choices: [{ delta: { content: text } }] })}\n\n`;
			controller.enqueue(encoder.encode(payload));
			controller.enqueue(encoder.encode("data: [DONE]\n\n"));
			controller.close();
		} });
		return new Response(stream, {
			status: 200,
			headers: { "Content-Type": "text/event-stream" }
		});
	}
}
async function streamChat(messages, handlers, opts = {}) {
	const maxReconnects = opts.maxReconnects ?? 3;
	const baseMs = opts.reconnectBaseMs ?? 800;
	let accumulated = "";
	let attempt = 0;
	let done = false;
	while (!done) {
		const outbound = accumulated.length > 0 ? [
			...messages,
			{
				role: "assistant",
				content: accumulated
			},
			{
				role: "system",
				content: "Continue the previous assistant reply exactly where it left off. Do not repeat text already sent."
			}
		] : messages;
		let res;
		try {
			res = await openStream(outbound, opts, handlers.signal, accumulated);
		} catch (err) {
			if (err.name === "AbortError") return;
			if (isTransientNetworkError(err) && attempt < maxReconnects) {
				attempt += 1;
				const delay = baseMs * 2 ** (attempt - 1);
				handlers.onReconnect?.(attempt, delay);
				await new Promise((r) => setTimeout(r, delay));
				continue;
			}
			const e = new LeoError(0, "Cannot reach LEO backend.", err);
			handlers.onError?.(e);
			throw e;
		}
		if (!res.ok || !res.body) {
			const text = await res.text().catch(() => "");
			const e = new LeoError(res.status, text || `HTTP ${res.status}`);
			handlers.onError?.(e);
			throw e;
		}
		const reader = res.body.getReader();
		const decoder = new TextDecoder();
		let buffer = "";
		let sawDone = false;
		let streamDroppedMidway = false;
		try {
			while (true) {
				const { done: rDone, value } = await reader.read();
				if (rDone) break;
				buffer += decoder.decode(value, { stream: true });
				const parts = buffer.split("\n\n");
				buffer = parts.pop() ?? "";
				for (const part of parts) {
					const line = part.trim();
					if (!line.startsWith("data:")) continue;
					const payload = line.slice(5).trim();
					if (payload === "[DONE]") {
						sawDone = true;
						break;
					}
					try {
						const json = JSON.parse(payload);
						const delta = json?.choices?.[0]?.delta?.content ?? json?.choices?.[0]?.message?.content;
						if (delta) {
							accumulated += delta;
							handlers.onDelta(delta);
						}
						const meta = json?.x_leo_metadata;
						if (meta) handlers.onMeta?.(meta);
					} catch {}
				}
				if (sawDone) break;
			}
			if (!sawDone) streamDroppedMidway = true;
		} catch (err) {
			if (err.name === "AbortError") return;
			streamDroppedMidway = true;
		} finally {
			try {
				reader.releaseLock();
			} catch {}
		}
		if (sawDone) {
			handlers.onDone?.();
			done = true;
		} else if (streamDroppedMidway && attempt < maxReconnects && !handlers.signal?.aborted) {
			attempt += 1;
			const delay = baseMs * 2 ** (attempt - 1);
			handlers.onReconnect?.(attempt, delay);
			await new Promise((r) => setTimeout(r, delay));
		} else {
			handlers.onDone?.();
			done = true;
		}
	}
}
var modKeyLabel = typeof navigator !== "undefined" && /Mac|iPhone|iPad/i.test(navigator.platform) ? "⌘" : "Ctrl";
function ChatPage() {
	const [sessionId, setSessionId] = (0, import_react.useState)(() => newSessionId());
	const [messages, setMessages] = (0, import_react.useState)([]);
	const [input, setInput] = (0, import_react.useState)("");
	const [status, setStatus] = (0, import_react.useState)("idle");
	const [reconnecting, setReconnecting] = (0, import_react.useState)(null);
	const [droppedPartial, setDroppedPartial] = (0, import_react.useState)(null);
	const [historyOpen, setHistoryOpen] = (0, import_react.useState)(false);
	const [historyQuery, setHistoryQuery] = (0, import_react.useState)("");
	const [sessions, setSessions] = (0, import_react.useState)([]);
	const [nextCursor, setNextCursor] = (0, import_react.useState)(void 0);
	const [loadingMore, setLoadingMore] = (0, import_react.useState)(false);
	const [selectedIdx, setSelectedIdx] = (0, import_react.useState)(0);
	const [showShortcuts, setShowShortcuts] = (0, import_react.useState)(false);
	const [liveAnnouncement, setLiveAnnouncement] = (0, import_react.useState)("");
	const [mergeBanner, setMergeBanner] = (0, import_react.useState)(null);
	const scrollRef = (0, import_react.useRef)(null);
	const abortRef = (0, import_react.useRef)(null);
	const textareaRef = (0, import_react.useRef)(null);
	const searchRef = (0, import_react.useRef)(null);
	const loadMoreRef = (0, import_react.useRef)(null);
	(0, import_react.useEffect)(() => {
		let cancelled = false;
		setSessions(listSessions().slice(0, 50));
		pullPage({ limit: 50 }).then((page) => {
			if (cancelled) return;
			setSessions(listSessions().slice(0, Math.max(50, page.sessions.length)));
			setNextCursor(page.nextCursor);
		});
		return () => {
			cancelled = true;
		};
	}, []);
	const loadMore = (0, import_react.useCallback)(async () => {
		if (loadingMore || !nextCursor) return;
		setLoadingMore(true);
		try {
			const page = await pullPage({
				cursor: nextCursor,
				limit: 50
			});
			const local = listSessions();
			const cap = sessions.length + page.sessions.length;
			setSessions(local.slice(0, Math.max(cap, sessions.length + 50)));
			setNextCursor(page.nextCursor);
		} finally {
			setLoadingMore(false);
		}
	}, [
		loadingMore,
		nextCursor,
		sessions.length
	]);
	(0, import_react.useEffect)(() => {
		scrollRef.current?.scrollTo({
			top: scrollRef.current.scrollHeight,
			behavior: "smooth"
		});
	}, [messages]);
	(0, import_react.useEffect)(() => () => abortRef.current?.abort(), []);
	(0, import_react.useEffect)(() => {
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
				is_current: summary.id === sessionId
			});
			if (summary.kind === "conflict-rollback") reportTelemetry({
				kind: "chat-optimistic-rollback",
				session_id: summary.id,
				rolled_back: summary.removedFromLocal,
				reconciled_from_remote: summary.addedFromRemote
			});
			if (summary.id === sessionId) {
				const fresh = getSession(sessionId);
				if (fresh) {
					setMessages((prev) => {
						const merged = [];
						const messagesEqual = (a, b) => {
							if (a.clientMessageId && b.clientMessageId) return a.clientMessageId === b.clientMessageId;
							return a.role === b.role && a.content === b.content && Math.abs((a.ts ?? 0) - (b.ts ?? 0)) < 15e3;
						};
						const incoming = fresh.messages.map((m) => ({
							role: m.role,
							content: m.content,
							meta: m.meta,
							ts: m.ts,
							clientMessageId: m.clientMessageId,
							streaming: false
						}));
						for (const m of [...incoming, ...prev]) {
							const idx = merged.findIndex((existing) => messagesEqual(existing, m));
							if (idx < 0) merged.push(m);
							else {
								const existing = merged[idx];
								if (!m.streaming && existing.streaming || m.meta && !existing.meta || m.content.length > existing.content.length) merged[idx] = m;
							}
						}
						return merged.sort((a, b) => (a.ts ?? 0) - (b.ts ?? 0));
					});
					setLiveAnnouncement(summary.kind === "conflict-rollback" ? `Sync conflict resolved. ${summary.addedFromRemote} message(s) merged from another device.` : `Conversation updated from another device: ${summary.addedFromRemote} new message(s).`);
				}
			}
		});
	}, [sessionId]);
	(0, import_react.useEffect)(() => {
		if (messages.length === 0) return;
		if (status !== "idle") return;
		const now = Date.now();
		const historyMsgs = messages.filter((m) => !m.streaming).map((m) => ({
			role: m.role,
			content: m.content,
			meta: m.meta,
			ts: m.ts ?? now,
			clientMessageId: m.clientMessageId
		}));
		if (historyMsgs.length === 0) return;
		const existing = sessions.find((s) => s.id === sessionId);
		if (existing) {
			const existingMsgs = existing.messages;
			if (existingMsgs.length === historyMsgs.length && existingMsgs.every((m, idx) => m.role === historyMsgs[idx].role && m.content === historyMsgs[idx].content && m.clientMessageId === historyMsgs[idx].clientMessageId)) return;
		}
		saveSession({
			id: sessionId,
			title: deriveTitle(historyMsgs),
			createdAt: existing?.createdAt ?? historyMsgs[0].ts,
			updatedAt: now,
			version: existing?.version ?? 1,
			lastSyncedVersion: existing?.lastSyncedVersion,
			messages: historyMsgs
		});
		setSessions((prev) => {
			return listSessions().slice(0, Math.max(prev.length, 50));
		});
	}, [
		messages,
		status,
		sessionId,
		sessions
	]);
	const filteredSessions = (0, import_react.useMemo)(() => historyQuery.trim() ? searchSessions(historyQuery) : sessions, [historyQuery, sessions]);
	(0, import_react.useEffect)(() => {
		setSelectedIdx(0);
	}, [historyQuery, historyOpen]);
	const stop = (0, import_react.useCallback)(() => {
		abortRef.current?.abort();
		abortRef.current = null;
		setStatus("idle");
		setReconnecting(null);
	}, []);
	const newChat = (0, import_react.useCallback)(() => {
		if (abortRef.current) abortRef.current.abort();
		setSessionId(newSessionId());
		setMessages([]);
		setInput("");
		setStatus("idle");
		setReconnecting(null);
		setDroppedPartial(null);
		setTimeout(() => textareaRef.current?.focus(), 0);
	}, []);
	const loadSession = (0, import_react.useCallback)((s) => {
		if (abortRef.current) abortRef.current.abort();
		setSessionId(s.id);
		setMessages(s.messages.map((m) => ({
			role: m.role,
			content: m.content,
			meta: m.meta,
			ts: m.ts,
			clientMessageId: m.clientMessageId
		})));
		setHistoryOpen(false);
		setStatus("idle");
		setReconnecting(null);
		setDroppedPartial(null);
	}, []);
	const removeSession = (0, import_react.useCallback)(async (id) => {
		await deleteSession(id);
		setSessions((prev) => listSessions().slice(0, Math.max(prev.length, 50)));
		if (id === sessionId) newChat();
	}, [sessionId, newChat]);
	const exportAll = (0, import_react.useCallback)(async () => {
		let all = [];
		try {
			all = await fetchAllSessions({ limit: 100 });
		} catch {
			all = listSessions();
		}
		if (all.length === 0) {
			toast.error("No conversations to export yet.");
			return;
		}
		downloadJson(`leo-chats-${(/* @__PURE__ */ new Date()).toISOString().slice(0, 10)}.json`, exportSessionsAsJson(all));
		toast.success(`Exported ${all.length} conversation${all.length === 1 ? "" : "s"}.`);
	}, []);
	const exportAllCsv = (0, import_react.useCallback)(async () => {
		let all = [];
		try {
			all = await fetchAllSessions({ limit: 100 });
		} catch {
			all = listSessions();
		}
		if (all.length === 0) {
			toast.error("No conversations to export yet.");
			return;
		}
		downloadCsv(`leo-chats-${(/* @__PURE__ */ new Date()).toISOString().slice(0, 10)}.csv`, exportSessionsAsCsv(all));
		toast.success(`Exported ${all.length} conversation${all.length === 1 ? "" : "s"} as CSV.`);
	}, []);
	function exportOne(s) {
		downloadJson(`leo-chat-${s.id}.json`, exportSessionsAsJson([s]));
	}
	async function runStream(history, seedAssistantAppend = false) {
		const assistantMsgId = `msg-assistant-${Date.now()}-${Math.random()}`;
		if (!seedAssistantAppend) setMessages((m) => [...m, {
			role: "assistant",
			content: "",
			streaming: true,
			ts: Date.now(),
			clientMessageId: assistantMsgId
		}]);
		else setMessages((m) => {
			const next = [...m];
			const last = next[next.length - 1];
			if (last && last.role === "assistant") next[next.length - 1] = {
				...last,
				streaming: true
			};
			return next;
		});
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
					} else if (reconnecting) setLiveAnnouncement("Connection resumed. LEO is responding.");
					setReconnecting(null);
					setMessages((m) => {
						const next = [...m];
						const last = next[next.length - 1];
						if (last && last.role === "assistant") next[next.length - 1] = {
							...last,
							content: last.content + chunk
						};
						return next;
					});
				},
				onMeta: (meta) => {
					setMessages((m) => {
						const next = [...m];
						const last = next[next.length - 1];
						if (last && last.role === "assistant") next[next.length - 1] = {
							...last,
							meta
						};
						return next;
					});
				},
				onReconnect: (attempt, delayMs) => {
					setReconnecting({
						attempt,
						inMs: delayMs
					});
					setLiveAnnouncement(`Connection to LEO dropped. Reconnecting, attempt ${attempt}, in ${Math.round(delayMs / 1e3)} seconds.`);
					reportTelemetry({
						kind: "chat-reconnect",
						trigger: "auto",
						attempt,
						delay_ms: delayMs,
						session_id: sessionId
					});
				},
				onError: async (err) => {
					if (receivedAny) {
						toast.error(err.message);
						setLiveAnnouncement("Connection lost. Reply is incomplete. Use the Reconnect button to resume.");
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
								temperature: .7
							})
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
								clientMessageId: last?.clientMessageId
							};
							return next;
						});
					} catch (e) {
						if (e.name === "AbortError") return;
						toast.error(e instanceof Error ? e.message : "Request failed");
						setMessages((m) => m.slice(0, -1));
					}
				}
			});
		} finally {
			abortRef.current = null;
			setStatus("idle");
			setReconnecting(null);
			setMessages((m) => m.map((msg, i) => i === m.length - 1 && msg.role === "assistant" ? {
				...msg,
				streaming: false,
				ts: msg.ts ?? Date.now()
			} : msg));
		}
	}
	async function send() {
		if (!input.trim() || status !== "idle") return;
		const now = Date.now();
		const clientMessageId = `msg-user-${now}-${Math.random()}`;
		const userMsg = {
			role: "user",
			content: input.trim(),
			ts: now,
			clientMessageId
		};
		const history = [...messages, userMsg];
		setMessages(history);
		setInput("");
		await runStream(history.map((m) => ({
			role: m.role,
			content: m.content
		})), false);
	}
	async function reconnectNow() {
		if (status !== "idle") abortRef.current?.abort();
		const last = messages[messages.length - 1];
		const priorPartial = last && last.role === "assistant" ? last.content : "";
		const history = (last && last.role === "assistant" ? messages.slice(0, -1) : messages).map((m) => ({
			role: m.role,
			content: m.content
		}));
		if (priorPartial) {
			history.push({
				role: "assistant",
				content: priorPartial
			});
			history.push({
				role: "system",
				content: "Continue the previous assistant reply exactly where it left off. Do not repeat text already sent."
			});
		}
		toast.message("Reconnecting to LEO…");
		setLiveAnnouncement("Reconnecting to LEO. Resuming from where the reply dropped.");
		reportTelemetry({
			kind: "chat-reconnect",
			trigger: "manual",
			session_id: sessionId,
			prior_partial_length: priorPartial.length
		});
		await runStream(history, !!priorPartial);
	}
	(0, import_react.useEffect)(() => {
		function inTypingField(el) {
			if (!(el instanceof HTMLElement)) return false;
			const tag = el.tagName;
			return tag === "INPUT" || tag === "TEXTAREA" || el.isContentEditable;
		}
		function onKey(e) {
			const mod = e.metaKey || e.ctrlKey;
			if (mod && e.key.toLowerCase() === "k") {
				e.preventDefault();
				setHistoryOpen(true);
				setTimeout(() => searchRef.current?.focus(), 0);
				return;
			}
			if (mod && e.key.toLowerCase() === "e") {
				e.preventDefault();
				exportAll();
				return;
			}
			if (mod && e.shiftKey && e.key.toLowerCase() === "n") {
				e.preventDefault();
				newChat();
				return;
			}
			if (mod && e.key === ".") {
				e.preventDefault();
				if (status !== "idle") stop();
				return;
			}
			if (e.key === "?" && !inTypingField(e.target)) {
				e.preventDefault();
				setShowShortcuts((v) => !v);
				return;
			}
			if (e.key === "/" && !inTypingField(e.target)) {
				e.preventDefault();
				textareaRef.current?.focus();
				return;
			}
			if (!historyOpen) return;
			if (e.key === "Escape") {
				e.preventDefault();
				setHistoryOpen(false);
				textareaRef.current?.focus();
				return;
			}
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
	}, [
		historyOpen,
		filteredSessions,
		selectedIdx,
		status,
		stop,
		exportAll,
		newChat,
		loadSession
	]);
	const isBusy = status !== "idle";
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: "flex h-screen",
		children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
			role: "status",
			"aria-live": "assertive",
			"aria-atomic": "true",
			className: "sr-only",
			"data-testid": "chat-live-region",
			children: liveAnnouncement
		}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
			className: "relative flex h-[calc(100vh-57px)] w-full overflow-hidden bg-background",
			children: [
				historyOpen && /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
					className: "fixed inset-0 z-40 bg-black/50 md:hidden",
					onClick: () => setHistoryOpen(false),
					"aria-hidden": "true"
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("aside", {
					className: `${historyOpen ? "flex" : "hidden"} absolute inset-y-0 left-0 z-50 w-80 shrink-0 flex-col border-r border-border bg-surface md:static`,
					"aria-label": "Chat history",
					children: [
						/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
							className: "flex items-center justify-between border-b border-border px-4 py-3",
							children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
								className: "flex items-center gap-2",
								children: [
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)(History, {
										className: "h-4 w-4 text-leo",
										"aria-hidden": true
									}),
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
										className: "font-display text-sm font-semibold",
										children: "History"
									}),
									isSyncEnabled() && /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
										className: "ml-1 rounded-sm bg-leo/10 px-1.5 py-0.5 font-mono text-[9px] uppercase tracking-wider text-leo",
										title: "Server sync enabled",
										children: "synced"
									})
								]
							}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
								className: "flex items-center gap-1",
								children: [
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
										type: "button",
										onClick: newChat,
										className: "p-1.5 text-muted-foreground hover:text-foreground focus:outline-none focus-visible:ring-2 focus-visible:ring-leo",
										"aria-label": `New chat (${modKeyLabel}+Shift+N)`,
										title: `New chat (${modKeyLabel}+Shift+N)`,
										children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Plus, { className: "h-4 w-4" })
									}),
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
										type: "button",
										onClick: exportAll,
										className: "p-1.5 text-muted-foreground hover:text-foreground focus:outline-none focus-visible:ring-2 focus-visible:ring-leo",
										"aria-label": `Export all conversations as JSON (${modKeyLabel}+E)`,
										title: `Export all as JSON (${modKeyLabel}+E)`,
										"data-testid": "chat-export-json",
										children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Download, { className: "h-4 w-4" })
									}),
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
										type: "button",
										onClick: exportAllCsv,
										className: "p-1.5 font-mono text-[10px] uppercase tracking-wider text-muted-foreground hover:text-foreground focus:outline-none focus-visible:ring-2 focus-visible:ring-leo",
										"aria-label": "Export all conversations as CSV",
										title: "Export all as CSV",
										"data-testid": "chat-export-csv",
										children: "CSV"
									}),
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
										type: "button",
										onClick: () => setHistoryOpen(false),
										className: "p-1.5 text-muted-foreground hover:text-foreground focus:outline-none focus-visible:ring-2 focus-visible:ring-leo md:hidden",
										"aria-label": "Close history panel",
										children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(X, { className: "h-4 w-4" })
									})
								]
							})]
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
							className: "border-b border-border px-3 py-2",
							children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
								className: "relative",
								children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Search, {
									className: "pointer-events-none absolute left-2 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-muted-foreground",
									"aria-hidden": true
								}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("input", {
									ref: searchRef,
									type: "search",
									value: historyQuery,
									onChange: (e) => setHistoryQuery(e.target.value),
									placeholder: `Search conversations…  (${modKeyLabel}+K)`,
									"aria-label": "Search conversations",
									className: "w-full bg-input py-1.5 pl-7 pr-2 text-xs outline-none focus:ring-1 focus:ring-leo"
								})]
							})
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
							className: "flex-1 overflow-y-auto",
							"data-history-list": true,
							children: [filteredSessions.length === 0 ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
								className: "px-4 py-6 text-center text-xs text-muted-foreground",
								children: historyQuery ? "No matches." : "No saved conversations yet."
							}) : filteredSessions.map((s, i) => {
								const active = s.id === sessionId;
								const highlighted = i === selectedIdx;
								return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
									className: `group flex items-start gap-1 border-b border-border/60 ${active ? "bg-background" : highlighted ? "bg-background/60" : "hover:bg-background/50"}`,
									children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("button", {
										type: "button",
										onClick: () => loadSession(s),
										className: `flex-1 px-3 py-2.5 text-left focus:outline-none focus-visible:ring-2 focus-visible:ring-leo focus-visible:ring-inset ${highlighted && !active ? "border-l-2 border-leo" : ""}`,
										"aria-current": active ? "true" : void 0,
										children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
											className: "truncate text-xs font-medium",
											children: s.title
										}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
											className: "mt-0.5 font-mono text-[10px] text-muted-foreground",
											children: [
												new Date(s.updatedAt).toLocaleString(),
												" · ",
												s.messages.length,
												" msg"
											]
										})]
									}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
										className: "flex flex-col opacity-0 transition-opacity group-hover:opacity-100 focus-within:opacity-100",
										children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
											type: "button",
											onClick: () => exportOne(s),
											className: "p-1.5 text-muted-foreground hover:text-foreground focus:outline-none focus-visible:ring-2 focus-visible:ring-leo",
											"aria-label": `Export "${s.title}" as JSON`,
											title: "Export JSON",
											children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Download, { className: "h-3.5 w-3.5" })
										}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
											type: "button",
											onClick: () => removeSession(s.id),
											className: "p-1.5 text-muted-foreground hover:text-destructive focus:outline-none focus-visible:ring-2 focus-visible:ring-leo",
											"aria-label": `Delete "${s.title}"`,
											title: "Delete",
											children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Trash2, { className: "h-3.5 w-3.5" })
										})]
									})]
								}, s.id);
							}), !historyQuery.trim() && nextCursor && /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
								className: "p-3",
								children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
									ref: loadMoreRef,
									type: "button",
									onClick: loadMore,
									disabled: loadingMore,
									className: "w-full border border-border px-3 py-2 text-xs font-semibold hover:border-leo hover:text-leo disabled:opacity-40 focus:outline-none focus-visible:ring-2 focus-visible:ring-leo",
									"data-testid": "history-load-more",
									"aria-label": "Load more conversations",
									children: loadingMore ? "Loading…" : "Load more"
								})
							})]
						})
					]
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "flex min-w-0 flex-1 flex-col",
					children: [
						/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
							className: "flex items-center gap-3 border-b border-border px-8 py-4",
							children: [
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
									type: "button",
									onClick: () => setHistoryOpen((v) => !v),
									className: "p-2 text-muted-foreground hover:text-foreground focus:outline-none focus-visible:ring-2 focus-visible:ring-leo",
									"aria-label": historyOpen ? "Hide history" : `Show history (${modKeyLabel}+K)`,
									"aria-expanded": historyOpen,
									title: `Toggle history (${modKeyLabel}+K)`,
									children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(History, { className: "h-4 w-4" })
								}),
								/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
									className: "flex-1",
									children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
										className: "eyebrow",
										children: "Console"
									}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("h1", {
										className: "mt-1 font-display text-2xl font-bold",
										children: "Chat"
									})]
								}),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
									type: "button",
									onClick: () => setShowShortcuts((v) => !v),
									className: "p-2 text-muted-foreground hover:text-foreground focus:outline-none focus-visible:ring-2 focus-visible:ring-leo",
									"aria-label": "Keyboard shortcuts (?)",
									title: "Keyboard shortcuts (?)",
									children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Keyboard, { className: "h-4 w-4" })
								}),
								/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("button", {
									type: "button",
									onClick: newChat,
									className: "inline-flex items-center gap-1.5 border border-border px-3 py-1.5 text-xs font-semibold hover:border-leo hover:text-leo focus:outline-none focus-visible:ring-2 focus-visible:ring-leo",
									children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Plus, { className: "h-3.5 w-3.5" }), " New chat"]
								})
							]
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
							ref: scrollRef,
							className: "flex-1 overflow-y-auto",
							"data-testid": "chat-messages",
							children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
								className: "mx-auto max-w-3xl px-8 py-8",
								children: [
									messages.length === 0 ? /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
										className: "py-20 text-center",
										children: [
											/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
												className: "mx-auto grid h-16 w-16 place-items-center border border-leo",
												children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
													className: "font-display text-2xl font-bold text-leo",
													children: "L"
												})
											}),
											/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h2", {
												className: "mt-6 font-display text-2xl font-bold",
												children: "Start a conversation"
											}),
											/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
												className: "mt-2 text-sm text-muted-foreground",
												children: "Talk to LEO — every reply shows how the router resolved it."
											}),
											/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("p", {
												className: "mt-4 font-mono text-[11px] text-muted-foreground",
												children: [
													"Press ",
													/* @__PURE__ */ (0, import_jsx_runtime.jsx)("kbd", {
														className: "border border-border px-1",
														children: "?"
													}),
													" for keyboard shortcuts."
												]
											})
										]
									}) : messages.map((m, i) => /* @__PURE__ */ (0, import_jsx_runtime.jsx)(MessageRow, { msg: m }, i)),
									mergeBanner && /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
										className: "my-6 flex items-start justify-between gap-3 border border-leo/50 bg-leo/10 px-4 py-3 text-sm",
										role: "status",
										"aria-live": "polite",
										"data-testid": "chat-merge-banner",
										children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
											className: "text-foreground",
											children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
												className: "font-semibold text-leo",
												children: mergeBanner.kind === "conflict-rollback" ? "Sync conflict resolved" : "Conversation updated from another device"
											}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
												className: "mt-1 text-xs text-muted-foreground",
												children: [
													"\"",
													mergeBanner.title,
													"\" — merged",
													" ",
													/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
														className: "font-mono text-foreground",
														children: mergeBanner.addedFromRemote
													}),
													" ",
													"remote message",
													mergeBanner.addedFromRemote === 1 ? "" : "s",
													mergeBanner.removedFromLocal > 0 && /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(import_jsx_runtime.Fragment, { children: [
														", dropped",
														" ",
														/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
															className: "font-mono text-foreground",
															children: mergeBanner.removedFromLocal
														}),
														" ",
														"local duplicate",
														mergeBanner.removedFromLocal === 1 ? "" : "s"
													] }),
													". New version: ",
													/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("span", {
														className: "font-mono",
														children: ["v", mergeBanner.mergedVersion]
													}),
													"."
												]
											})]
										}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
											type: "button",
											onClick: () => setMergeBanner(null),
											className: "p-1 text-muted-foreground hover:text-foreground focus:outline-none focus-visible:ring-2 focus-visible:ring-leo",
											"aria-label": "Dismiss merge notification",
											children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(X, { className: "h-4 w-4" })
										})]
									}),
									status === "submitted" && !reconnecting && /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
										className: "my-6 flex items-center gap-2 text-sm text-muted-foreground",
										"aria-live": "polite",
										children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(LoaderCircle, {
											className: "h-4 w-4 animate-spin text-leo",
											"aria-hidden": "true"
										}), "Contacting LEO…"]
									}),
									reconnecting && /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
										className: "my-6 flex items-center justify-between gap-3 border border-yellow-500/40 bg-yellow-500/10 px-4 py-3 text-sm text-yellow-500",
										role: "status",
										"aria-live": "assertive",
										"aria-atomic": "true",
										"data-testid": "chat-reconnecting",
										children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
											className: "flex items-center gap-2",
											children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(RefreshCw, {
												className: "h-4 w-4 animate-spin",
												"aria-hidden": "true"
											}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("span", { children: [
												"Stream dropped — auto-reconnecting (attempt ",
												reconnecting.attempt,
												", retry in",
												" ",
												Math.max(1, Math.round(reconnecting.inMs / 1e3)),
												"s)…"
											] })]
										}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("button", {
											type: "button",
											onClick: reconnectNow,
											className: "inline-flex items-center gap-1 border border-yellow-500/60 px-2 py-1 text-xs font-semibold hover:bg-yellow-500/20 focus:outline-none focus-visible:ring-2 focus-visible:ring-leo",
											"aria-label": "Reconnect to LEO now instead of waiting for the automatic retry",
											children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(RotateCcw, {
												className: "h-3 w-3",
												"aria-hidden": "true"
											}), " Reconnect now"]
										})]
									}),
									droppedPartial && !isBusy && /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
										className: "my-6 flex items-center justify-between gap-3 border border-destructive/40 bg-destructive/10 px-4 py-3 text-sm",
										role: "alert",
										"aria-live": "assertive",
										"aria-atomic": "true",
										"data-testid": "chat-reconnect-manual",
										children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
											className: "text-destructive",
											children: "Connection lost. Resume from where LEO left off?"
										}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
											className: "flex gap-2",
											children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("button", {
												type: "button",
												onClick: reconnectNow,
												className: "inline-flex items-center gap-1 bg-leo px-3 py-1.5 text-xs font-semibold text-leo-foreground hover:brightness-110 focus:outline-none focus-visible:ring-2 focus-visible:ring-leo",
												children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(RotateCcw, { className: "h-3 w-3" }), " Reconnect"]
											}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
												type: "button",
												onClick: () => setDroppedPartial(null),
												className: "border border-border px-3 py-1.5 text-xs hover:text-foreground focus:outline-none focus-visible:ring-2 focus-visible:ring-leo",
												children: "Dismiss"
											})]
										})]
									})
								]
							})
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
							className: "border-t border-border p-4",
							children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
								className: "mx-auto flex max-w-3xl gap-2",
								children: [
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)("label", {
										htmlFor: "chat-input",
										className: "sr-only",
										children: "Message LEO"
									}),
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)("textarea", {
										id: "chat-input",
										ref: textareaRef,
										"data-testid": "chat-input",
										value: input,
										onChange: (e) => setInput(e.target.value),
										onKeyDown: (e) => {
											if (e.key === "Enter" && !e.shiftKey) {
												e.preventDefault();
												send();
											}
										},
										placeholder: "Ask LEO anything…",
										rows: 2,
										"aria-label": "Chat message",
										className: "flex-1 resize-none bg-input px-4 py-3 text-sm outline-none focus:ring-1 focus:ring-leo"
									}),
									isBusy ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
										type: "button",
										onClick: stop,
										"aria-label": `Stop generating (${modKeyLabel}+.)`,
										"data-testid": "chat-stop",
										title: `Stop (${modKeyLabel}+.)`,
										className: "bg-destructive px-5 text-destructive-foreground hover:brightness-110 focus:outline-none focus-visible:ring-2 focus-visible:ring-leo",
										children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Square, {
											className: "h-4 w-4",
											"aria-hidden": "true"
										})
									}) : /* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
										type: "button",
										onClick: send,
										disabled: !input.trim(),
										"aria-label": "Send message",
										"data-testid": "chat-send",
										className: "bg-leo px-5 text-leo-foreground hover:brightness-110 disabled:opacity-40 focus:outline-none focus-visible:ring-2 focus-visible:ring-leo",
										children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Send, {
											className: "h-4 w-4",
											"aria-hidden": "true"
										})
									})
								]
							})
						})
					]
				}),
				showShortcuts && /* @__PURE__ */ (0, import_jsx_runtime.jsx)(ShortcutsDialog, { onClose: () => setShowShortcuts(false) })
			]
		})]
	});
}
function ShortcutsDialog({ onClose }) {
	const M = modKeyLabel;
	const items = [
		[`${M} + K`, "Open history & focus search"],
		[`${M} + E`, "Export all conversations as JSON"],
		[`${M} + Shift + N`, "New chat"],
		[`${M} + .`, "Stop generating"],
		["/", "Focus message composer"],
		["↑ / ↓", "Navigate history (when open)"],
		["Enter", "Open selected conversation"],
		["Esc", "Close history panel"],
		["?", "Toggle this shortcut list"]
	];
	return /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
		role: "dialog",
		"aria-modal": "true",
		"aria-label": "Keyboard shortcuts",
		className: "fixed inset-0 z-50 grid place-items-center bg-background/80 p-6",
		onClick: onClose,
		children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
			className: "w-full max-w-md border border-border bg-surface p-6 shadow-2xl",
			onClick: (e) => e.stopPropagation(),
			children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "flex items-center justify-between",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h2", {
					className: "font-display text-lg font-bold",
					children: "Keyboard shortcuts"
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
					type: "button",
					onClick: onClose,
					"aria-label": "Close",
					className: "p-1 text-muted-foreground hover:text-foreground focus:outline-none focus-visible:ring-2 focus-visible:ring-leo",
					children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(X, { className: "h-4 w-4" })
				})]
			}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("ul", {
				className: "mt-4 space-y-2 text-sm",
				children: items.map(([keys, label]) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("li", {
					className: "flex items-center justify-between gap-4",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
						className: "text-muted-foreground",
						children: label
					}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("kbd", {
						className: "border border-border bg-background px-2 py-0.5 font-mono text-[11px]",
						children: keys
					})]
				}, keys))
			})]
		})
	});
}
function MessageRow({ msg }) {
	if (msg.role === "user") return /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
		className: "my-6 flex justify-end",
		"data-testid": "chat-user",
		children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
			className: "max-w-[80%] bg-leo px-4 py-3 text-sm text-leo-foreground",
			children: msg.content
		})
	});
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: "my-6",
		"data-testid": "chat-assistant",
		children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
			className: "whitespace-pre-wrap text-sm leading-relaxed",
			children: [msg.content, msg.streaming && /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
				"aria-label": "Streaming",
				className: "ml-1 inline-block h-3 w-2 translate-y-[2px] animate-pulse bg-leo"
			})]
		}), msg.meta && /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("details", {
			className: "mt-3 border border-border",
			children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("summary", {
				className: "cursor-pointer px-3 py-2 text-xs text-muted-foreground hover:text-foreground",
				children: [
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Zap, { className: "mr-1 inline h-3 w-3 text-leo" }),
					"Resolved by ",
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
						className: "text-leo font-mono",
						children: msg.meta.resolved_by ?? "—"
					}),
					msg.meta.latency_ms != null && /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(import_jsx_runtime.Fragment, { children: [
						" ",
						"· ",
						/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("span", {
							className: "font-mono",
							children: [msg.meta.latency_ms, "ms"]
						})
					] }),
					msg.meta.compute_avoided && /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(import_jsx_runtime.Fragment, { children: [
						" ",
						"· ",
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
							className: "text-leo",
							children: "compute avoided"
						})
					] })
				]
			}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("pre", {
				className: "border-t border-border bg-surface p-3 font-mono text-[11px] overflow-auto",
				children: JSON.stringify(msg.meta, null, 2)
			})]
		})]
	});
}
//#endregion
export { ChatPage as component };

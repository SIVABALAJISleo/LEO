// Persisted timeline of HealthDegradationAlert transitions.
// Each event records when a warn/critical episode started, its reasons, and
// when it resolved. Feeds the /benchmarks alert timeline panel.
import { useEffect, useState } from "react";

export type AlertLevel = "warn" | "critical";

export interface AlertEvent {
  id: string;
  level: AlertLevel;
  startedAt: number;
  endedAt: number | null;
  startReasons: string[];
  peakLevel: AlertLevel;
  lastReasons: string[];
}

const KEY = "leo.health_alert_timeline_v1";
const EVENT = "leo:health-alert-timeline-changed";
const MAX = 200;

function load(): AlertEvent[] {
  if (typeof window === "undefined") return [];
  try {
    const raw = window.localStorage.getItem(KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? parsed.slice(-MAX) : [];
  } catch {
    return [];
  }
}

function persist(events: AlertEvent[]) {
  if (typeof window === "undefined") return;
  try {
    window.localStorage.setItem(KEY, JSON.stringify(events.slice(-MAX)));
    window.dispatchEvent(new CustomEvent(EVENT));
  } catch {
    /* ignore quota */
  }
}

export function getAlertTimeline(): AlertEvent[] {
  return load();
}

export function clearAlertTimeline() {
  persist([]);
}

/** Called by HealthDegradationAlert whenever the level transitions. */
export function recordAlertTransition(nextLevel: "ok" | AlertLevel, reasons: string[]) {
  const events = load();
  const open =
    events.length && events[events.length - 1].endedAt === null ? events[events.length - 1] : null;

  if (nextLevel === "ok") {
    if (open) {
      open.endedAt = Date.now();
      open.lastReasons = reasons.length ? reasons : open.lastReasons;
      persist(events);
    }
    return;
  }

  if (open) {
    // Same episode — update peak/reasons only.
    if (nextLevel === "critical" && open.peakLevel !== "critical") {
      open.peakLevel = "critical";
    }
    open.lastReasons = reasons;
    persist(events);
    return;
  }

  events.push({
    id: `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
    level: nextLevel,
    startedAt: Date.now(),
    endedAt: null,
    startReasons: reasons,
    peakLevel: nextLevel,
    lastReasons: reasons,
  });
  persist(events);
}

export function useAlertTimeline(): AlertEvent[] {
  const [events, setEvents] = useState<AlertEvent[]>(() => load());
  useEffect(() => {
    const handler = () => setEvents(load());
    window.addEventListener(EVENT, handler);
    window.addEventListener("storage", handler);
    return () => {
      window.removeEventListener(EVENT, handler);
      window.removeEventListener("storage", handler);
    };
  }, []);
  return events;
}

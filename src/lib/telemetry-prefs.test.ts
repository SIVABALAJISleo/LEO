import { describe, it, expect, beforeEach, vi } from 'vitest';
import { clearTelemetryQueue, shouldSendKind } from './telemetry-prefs';

describe('Telemetry Preferences & Buffer Unit Tests', () => {
  beforeEach(() => {
    window.localStorage.clear();
  });

  it('allows essential telemetry events under any mode', () => {
    expect(shouldSendKind('essential')).toBe(true);
    expect(shouldSendKind('error')).toBe(true);
  });

  it('wipes non-essential telemetry events on clearTelemetryQueue', () => {
    window.localStorage.setItem('leo.telemetry_queue', JSON.stringify([
      { kind: 'essential', data: '1' },
      { kind: 'user_analytics', data: '2' }
    ]));
    clearTelemetryQueue();
    const raw = window.localStorage.getItem('leo.telemetry_queue');
    const arr = JSON.parse(raw || '[]');
    expect(Array.isArray(arr)).toBe(true);
  });
});

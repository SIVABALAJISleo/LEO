/**
 * Module 8: Multi Camera Analytics
 * Path: ui_core/src/camera/cameraGovernor.ts
 * Purpose: Optimizes camera video feed processing by running frame scene change difference maps.
 */

export interface CameraEvent {
  eventId: string;
  cameraName: string;
  eventType: "intrusion" | "loitering" | "unauthorized_entry" | "crowd_formation";
  timestamp: number;
  confidence: number;
}

export interface CameraAnalyticsReport {
  cameraName: string;
  totalFramesAnalyzed: number;
  framesProcessedCount: number; // Only frames with changes are processed
  sceneChangeDetected: boolean;
  activeEvents: CameraEvent[];
  processingSavingsPct: number; // computation savings
}

export class CameraGovernor {
  private frameCount = 0;

  /**
   * Evaluates camera frames, applying scene change thresholds to bypass duplicate processing.
   */
  public processCameraFeed(cameraName: string, simulatedFrameDiffPct: number): CameraAnalyticsReport {
    this.frameCount += 30; // simulate 30 frames analyzed
    
    // Scene change filter optimization
    const sceneChangeDetected = simulatedFrameDiffPct >= 5.0; // 5% diff threshold
    
    const activeEvents: CameraEvent[] = [];
    let framesProcessedCount = 1;

    if (sceneChangeDetected) {
      framesProcessedCount = 12; // process keyframe sequence
      if (simulatedFrameDiffPct >= 20.0) {
        activeEvents.push({
          eventId: "cam-evt-" + Math.floor(Math.random() * 1000),
          cameraName,
          eventType: "intrusion",
          timestamp: Date.now(),
          confidence: 0.94
        });
      }
    } else {
      framesProcessedCount = 0; // skip fully due to static frame similarity
    }

    // Savings = (1 - (processed / total)) * 100
    const processingSavingsPct = parseFloat(((1 - (framesProcessedCount / 30)) * 100).toFixed(2));

    return {
      cameraName,
      totalFramesAnalyzed: 30,
      framesProcessedCount,
      sceneChangeDetected,
      activeEvents,
      processingSavingsPct
    };
  }
}

// LEO AI V36 — Sensor Fusion V2
// Merges redundant signals from Camera, GPS, and IMU targets.

export interface SensorReadings {
  gpsLat: number;
  gpsLng: number;
  imuOrientation: number;
  cameraObstacleFound: boolean;
}

export class SensorFusionV2 {
  public fuseTelemetry(
    readings: SensorReadings,
    gpsConfidence: number,
    cameraConfidence: number,
  ): { fusedConfidence: number; calculatedObstacle: boolean } {
    const fusedConfidence = parseFloat((gpsConfidence * 0.4 + cameraConfidence * 0.6).toFixed(3));
    return {
      fusedConfidence,
      calculatedObstacle: readings.cameraObstacleFound && cameraConfidence > 0.5,
    };
  }
}

// LEO AI V32 — Phase 6 Sensor Uncertainty Modeling Engine
// Capabilities: probabilistic sensor fusion, confidence weighting, anomaly detection.
// Purpose: Reduce sensor noise, blur, dust, occlusion, GPS drift, localization errors.

export interface SensorReading {
  sensorName: "LiDAR" | "StereoCamera" | "IMU" | "GPS";
  rawSignal: number[];
  noiseStdDev: number;
  anomalyDetected: boolean;
}

export interface FusedState {
  fusedPosition: number[]; // x, y, z
  overallConfidence: number; // 0 to 1
  filteredAnomaliesCount: number;
}

export class SensorUncertaintyEngine {
  fuseReadings(readings: SensorReading[]): FusedState {
    let sumX = 0,
      sumY = 0,
      sumZ = 0;
    let weightSum = 0;
    let filteredAnomaliesCount = 0;

    readings.forEach((r) => {
      // Anomaly detection: if values deviate too far, skip or flag
      const hasExtremeValue = r.rawSignal.some((v) => Math.abs(v) > 500);
      if (hasExtremeValue || r.anomalyDetected) {
        filteredAnomaliesCount++;
        return; // Filter out anomalous sensor readings
      }

      // Weight is inversely proportional to standard deviation (lower variance = higher confidence)
      const weight = 1.0 / (r.noiseStdDev * r.noiseStdDev || 0.01);

      sumX += r.rawSignal[0] * weight;
      sumY += r.rawSignal[1] * weight;
      sumZ += (r.rawSignal[2] || 0) * weight;

      weightSum += weight;
    });

    const finalWeight = weightSum || 1;
    const fusedPosition = [
      parseFloat((sumX / finalWeight).toFixed(3)),
      parseFloat((sumY / finalWeight).toFixed(3)),
      parseFloat((sumZ / finalWeight).toFixed(3)),
    ];

    // Compute overall confidence score
    const avgNoise = readings.reduce((acc, r) => acc + r.noiseStdDev, 0) / (readings.length || 1);
    const overallConfidence = parseFloat(
      Math.max(0.1, 1.0 - avgNoise * 0.12 - filteredAnomaliesCount * 0.1).toFixed(2),
    );

    return {
      fusedPosition,
      overallConfidence,
      filteredAnomaliesCount,
    };
  }
}

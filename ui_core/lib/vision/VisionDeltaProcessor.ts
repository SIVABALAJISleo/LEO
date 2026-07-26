/**
 * Vision Delta Processor
 * Process only changed regions between frames to minimize vision compute.
 */

export interface BoundingBox {
  x: number;
  y: number;
  width: number;
  height: number;
}

export interface DeltaResult {
  changeDetected: boolean;
  changeMagnitude: number;
  changedRegions: BoundingBox[];
}

export class VisionDeltaProcessor {
  private static instance: VisionDeltaProcessor;
  private previousFrame: ImageData | null = null;
  private readonly CHANGE_THRESHOLD = 0.1; // 10% pixel difference

  private constructor() {}

  static getInstance(): VisionDeltaProcessor {
    if (!VisionDeltaProcessor.instance) {
      VisionDeltaProcessor.instance = new VisionDeltaProcessor();
    }
    return VisionDeltaProcessor.instance;
  }

  /**
   * Detect changes between current and previous frame
   */
  detectDelta(currentFrame: ImageData): DeltaResult {
    if (!this.previousFrame) {
      // First frame - full processing needed
      this.previousFrame = this.cloneImageData(currentFrame);
      return {
        changeDetected: true,
        changeMagnitude: 1.0,
        changedRegions: [
          {
            x: 0,
            y: 0,
            width: currentFrame.width,
            height: currentFrame.height,
          },
        ],
      };
    }

    const diff = this.computeDifference(this.previousFrame, currentFrame);
    this.previousFrame = this.cloneImageData(currentFrame);

    if (diff.changeMagnitude < this.CHANGE_THRESHOLD) {
      console.log("[VisionDelta] No significant change - reusing cache");
      return {
        changeDetected: false,
        changeMagnitude: diff.changeMagnitude,
        changedRegions: [],
      };
    }

    console.log(`[VisionDelta] Change detected: ${(diff.changeMagnitude * 100).toFixed(1)}%`);
    return diff;
  }

  private computeDifference(prev: ImageData, curr: ImageData): DeltaResult {
    const width = prev.width;
    const height = prev.height;
    let totalDiff = 0;

    // Pixel-wise difference
    for (let i = 0; i < prev.data.length; i += 4) {
      const rDiff = Math.abs(prev.data[i] - curr.data[i]);
      const gDiff = Math.abs(prev.data[i + 1] - curr.data[i + 1]);
      const bDiff = Math.abs(prev.data[i + 2] - curr.data[i + 2]);
      totalDiff += (rDiff + gDiff + bDiff) / (3 * 255);
    }

    const changeMagnitude = totalDiff / (width * height);

    // Simplified: return full frame if changed
    // Real implementation would find bounding boxes
    const changedRegions: BoundingBox[] =
      changeMagnitude > this.CHANGE_THRESHOLD ? [{ x: 0, y: 0, width, height }] : [];

    return {
      changeDetected: changeMagnitude > this.CHANGE_THRESHOLD,
      changeMagnitude,
      changedRegions,
    };
  }

  private cloneImageData(imageData: ImageData): ImageData {
    return new ImageData(new Uint8ClampedArray(imageData.data), imageData.width, imageData.height);
  }

  reset(): void {
    this.previousFrame = null;
  }
}

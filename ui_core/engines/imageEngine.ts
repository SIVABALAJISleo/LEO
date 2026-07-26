import { runCpuJob } from "./cpuEngine";
import { runGpuJob, runWebGpuUpscale, WebGpuUpscalePayload } from "./gpuEngine";

export interface ImageJobPayload {
  // When provided, we will try to run real WebGPU upscaling on this image.
  // You can obtain ImageData from a canvas 2D context on the frontend.
  imageData?: ImageData;
  scale?: number;
  description?: string;
}

export interface ImageJobResult {
  jobId: string;
  cpuDurationMs: number;
  gpuNote: string;
  upscaled?: {
    width: number;
    height: number;
    data: Uint8ClampedArray;
  };
  note: string;
}

// Image engine: runs the demo CPU job and, if possible, executes a real WebGPU
// nearest-neighbor upscaler on provided image data.
export async function runImageJob(
  jobId: string,
  payload: ImageJobPayload,
): Promise<ImageJobResult> {
  const [cpuRes, gpuRes] = await Promise.all([
    runCpuJob(jobId, payload),
    runGpuJob(jobId, payload),
  ]);

  let upscaled:
    | {
        width: number;
        height: number;
        data: Uint8ClampedArray;
      }
    | undefined;

  if (payload.imageData) {
    const scale = payload.scale ?? 2;
    const img = payload.imageData;

    const upscalePayload: WebGpuUpscalePayload = {
      width: img.width,
      height: img.height,
      data: img.data,
      scale,
    };

    const upscaleRes = await runWebGpuUpscale(jobId, upscalePayload);

    if (upscaleRes.usedWebGPU && upscaleRes.data) {
      upscaled = {
        width: upscaleRes.width,
        height: upscaleRes.height,
        data: upscaleRes.data,
      };
    }
  }

  return {
    jobId,
    cpuDurationMs: cpuRes.durationMs,
    gpuNote: gpuRes.note,
    upscaled,
    note: upscaled
      ? "Image engine executed CPU demo work and WebGPU upscaling."
      : "Image engine executed CPU demo work; WebGPU upscaler skipped or unavailable.",
  };
}

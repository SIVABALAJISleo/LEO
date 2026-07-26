// GPU/iGPU “engine” using WebGPU when available.
// Contains a basic spatial upscaler implemented as a WebGPU compute shader.

export interface GpuJobResult {
  jobId: string;
  usedWebGPU: boolean;
  note: string;
}

export interface WebGpuUpscalePayload {
  width: number;
  height: number;
  data: Uint8ClampedArray; // RGBA input pixels
  scale: number; // e.g. 2 for 2x upscale
}

export interface WebGpuUpscaleResult {
  jobId: string;
  usedWebGPU: boolean;
  width: number;
  height: number;
  data: Uint8ClampedArray | null;
  note: string;
}

export async function runGpuJob(jobId: string, payload: unknown): Promise<GpuJobResult> {
  const hasWebGPU =
    typeof navigator !== "undefined" && typeof (navigator as any).gpu !== "undefined";

  if (!hasWebGPU) {
    return {
      jobId,
      usedWebGPU: false,
      note: "WebGPU not available; GPU engine fell back to no-op.",
    };
  }

  try {
    const adapter = await (navigator as any).gpu.requestAdapter();
    if (!adapter) {
      return {
        jobId,
        usedWebGPU: false,
        note: "WebGPU adapter not available.",
      };
    }

    const device = await adapter.requestDevice();
    device.queue.onSubmittedWorkDone();

    return {
      jobId,
      usedWebGPU: true,
      note: "WebGPU device acquired; basic GPU path available.",
    };
  } catch {
    return {
      jobId,
      usedWebGPU: false,
      note: "WebGPU initialization failed.",
    };
  }
}

// Basic nearest-neighbor spatial upscaler implemented as a WebGPU compute shader.
// This is a concrete “secret sauce” step: real compute work on the user’s GPU/iGPU.
export async function runWebGpuUpscale(
  jobId: string,
  payload: WebGpuUpscalePayload,
): Promise<WebGpuUpscaleResult> {
  const hasWebGPU =
    typeof navigator !== "undefined" && typeof (navigator as any).gpu !== "undefined";
  if (!hasWebGPU) {
    return {
      jobId,
      usedWebGPU: false,
      width: payload.width,
      height: payload.height,
      data: null,
      note: "WebGPU not available on this device.",
    };
  }

  const adapter = await (navigator as any).gpu.requestAdapter();
  if (!adapter) {
    return {
      jobId,
      usedWebGPU: false,
      width: payload.width,
      height: payload.height,
      data: null,
      note: "WebGPU adapter not available.",
    };
  }

  const device = await adapter.requestDevice();
  const scale = Math.max(1, Math.floor(payload.scale));
  const srcWidth = payload.width;
  const srcHeight = payload.height;
  const dstWidth = srcWidth * scale;
  const dstHeight = srcHeight * scale;

  // Pack RGBA8 into u32 for simpler storage handling in WGSL.
  const srcPixels = payload.data;
  const srcPacked = new Uint32Array(srcWidth * srcHeight);
  for (let i = 0; i < srcWidth * srcHeight; i++) {
    const r = srcPixels[i * 4 + 0] ?? 0;
    const g = srcPixels[i * 4 + 1] ?? 0;
    const b = srcPixels[i * 4 + 2] ?? 0;
    const a = srcPixels[i * 4 + 3] ?? 255;
    // Little-endian RGBA8
    srcPacked[i] = (a << 24) | (b << 16) | (g << 8) | r;
  }

  const srcBuffer = device.createBuffer({
    size: srcPacked.byteLength,
    usage: GPUBufferUsage.STORAGE | GPUBufferUsage.COPY_DST,
  });
  device.queue.writeBuffer(srcBuffer, 0, srcPacked.buffer);

  const dstBufferSize = dstWidth * dstHeight * 4; // bytes (RGBA8)
  const dstStorageBuffer = device.createBuffer({
    size: dstWidth * dstHeight * 4,
    usage: GPUBufferUsage.STORAGE | GPUBufferUsage.COPY_SRC,
  });

  const paramsBuffer = device.createBuffer({
    size: 12, // 3 * u32: srcWidth, srcHeight, scale
    usage: GPUBufferUsage.UNIFORM | GPUBufferUsage.COPY_DST,
  });
  const paramsArray = new Uint32Array([srcWidth, srcHeight, scale]);
  device.queue.writeBuffer(paramsBuffer, 0, paramsArray.buffer);

  const shaderModule = device.createShaderModule({
    code: `
      struct Params {
        srcWidth : u32,
        srcHeight : u32,
        scale : u32,
      };

      @group(0) @binding(0) var<storage, read> src : array<u32>;
      @group(0) @binding(1) var<storage, read_write> dst : array<u32>;
      @group(0) @binding(2) var<uniform> params : Params;

      // Unpack a packed RGBA8 u32 into vec4<f32> in 0..1 range.
      fn unpack_rgba(packed : u32) -> vec4<f32> {
        let r : f32 = f32(packed & 0xffu) / 255.0;
        let g : f32 = f32((packed >> 8u) & 0xffu) / 255.0;
        let b : f32 = f32((packed >> 16u) & 0xffu) / 255.0;
        let a : f32 = f32((packed >> 24u) & 0xffu) / 255.0;
        return vec4<f32>(r, g, b, a);
      }

      // Pack vec4<f32> in 0..1 range into RGBA8 u32.
      fn pack_rgba(color : vec4<f32>) -> u32 {
        let r : u32 = u32(clamp(color.r, 0.0, 1.0) * 255.0) & 0xffu;
        let g : u32 = u32(clamp(color.g, 0.0, 1.0) * 255.0) & 0xffu;
        let b : u32 = u32(clamp(color.b, 0.0, 1.0) * 255.0) & 0xffu;
        let a : u32 = u32(clamp(color.a, 0.0, 1.0) * 255.0) & 0xffu;
        return (a << 24u) | (b << 16u) | (g << 8u) | r;
      }

      fn luma(rgb : vec3<f32>) -> f32 {
        return dot(rgb, vec3<f32>(0.299, 0.587, 0.114));
      }

      // Simple edge-aware 3x3 bilateral upscaling:
      // For each dst pixel, map to fractional source coord, take a 3x3 neighborhood,
      // and weight taps by spatial + range (luma) distance.

      @compute @workgroup_size(8, 8)
      fn main(@builtin(global_invocation_id) gid : vec3<u32>) {
        let outX = gid.x;
        let outY = gid.y;

        let dstWidth = params.srcWidth * params.scale;
        let dstHeight = params.srcHeight * params.scale;

        if (outX >= dstWidth || outY >= dstHeight) {
          return;
        }

        // Map center of dst pixel back into src space.
        let scaleF : f32 = f32(params.scale);
        let srcXf : f32 = (f32(outX) + 0.5) / scaleF - 0.5;
        let srcYf : f32 = (f32(outY) + 0.5) / scaleF - 0.5;

        let baseX : i32 = i32(floor(srcXf));
        let baseY : i32 = i32(floor(srcYf));

        var accum : vec3<f32> = vec3<f32>(0.0, 0.0, 0.0);
        var wSum : f32 = 0.0;

        // Sigma values for bilateral weights.
        let sigmaSpatial : f32 = 1.0;
        let sigmaRange : f32 = 0.1;
        let twoSigmaSpatial2 : f32 = 2.0 * sigmaSpatial * sigmaSpatial;
        let twoSigmaRange2 : f32 = 2.0 * sigmaRange * sigmaRange;

        var centerLuma : f32 = 0.0;
        var centerSet : bool = false;

        // First pass: find center sample luma (nearest source pixel).
        let cx : i32 = clamp(baseX, 0, i32(params.srcWidth) - 1);
        let cy : i32 = clamp(baseY, 0, i32(params.srcHeight) - 1);
        let cIndex : u32 = u32(cy) * params.srcWidth + u32(cx);
        let cColor : vec4<f32> = unpack_rgba(src[cIndex]);
        centerLuma = luma(cColor.rgb);
        centerSet = true;

        // 3x3 neighborhood sampling with bilateral weights.
        for (var oy : i32 = -1; oy <= 1; oy = oy + 1) {
          for (var ox : i32 = -1; ox <= 1; ox = ox + 1) {
            let sx : i32 = clamp(baseX + ox, 0, i32(params.srcWidth) - 1);
            let sy : i32 = clamp(baseY + oy, 0, i32(params.srcHeight) - 1);
            let sIndex : u32 = u32(sy) * params.srcWidth + u32(sx);

            let color : vec4<f32> = unpack_rgba(src[sIndex]);
            let lum : f32 = luma(color.rgb);

            let dx : f32 = f32(ox);
            let dy : f32 = f32(oy);
            let dist2 : f32 = dx * dx + dy * dy;
            let spatialW : f32 = exp(-dist2 / twoSigmaSpatial2);

            let dl : f32 = lum - centerLuma;
            let rangeW : f32 = exp(-(dl * dl) / twoSigmaRange2);

            let w : f32 = spatialW * rangeW;
            accum += color.rgb * w;
            wSum += w;
          }
        }

        var outColor : vec4<f32>;
        if (wSum > 0.0) {
          outColor = vec4<f32>(accum / wSum, cColor.a);
        } else {
          outColor = cColor;
        }

        let dstIndex : u32 = outY * dstWidth + outX;
        dst[dstIndex] = pack_rgba(outColor);
      }
    `,
  });

  const pipeline = await device.createComputePipelineAsync({
    layout: "auto",
    compute: {
      module: shaderModule,
      entryPoint: "main",
    },
  });

  const bindGroup = device.createBindGroup({
    layout: pipeline.getBindGroupLayout(0),
    entries: [
      { binding: 0, resource: { buffer: srcBuffer } },
      { binding: 1, resource: { buffer: dstStorageBuffer } },
      { binding: 2, resource: { buffer: paramsBuffer } },
    ],
  });

  const commandEncoder = device.createCommandEncoder();
  const pass = commandEncoder.beginComputePass();
  pass.setPipeline(pipeline);
  pass.setBindGroup(0, bindGroup);

  const workgroupSize = 8;
  const workgroupsX = Math.ceil(dstWidth / workgroupSize);
  const workgroupsY = Math.ceil(dstHeight / workgroupSize);
  pass.dispatchWorkgroups(workgroupsX, workgroupsY);
  pass.end();

  // Read back result
  const readBuffer = device.createBuffer({
    size: dstStorageBuffer.size,
    usage: GPUBufferUsage.COPY_DST | GPUBufferUsage.MAP_READ,
  });

  commandEncoder.copyBufferToBuffer(dstStorageBuffer, 0, readBuffer, 0, dstStorageBuffer.size);
  const commandBuffer = commandEncoder.finish();
  device.queue.submit([commandBuffer]);

  await readBuffer.mapAsync(GPUMapMode.READ);
  const dstData = readBuffer.getMappedRange();
  const dstPacked = new Uint32Array(dstData.slice(0));

  const outPixels = new Uint8ClampedArray(dstWidth * dstHeight * 4);
  for (let i = 0; i < dstPacked.length; i++) {
    const pixel = dstPacked[i];
    const r = pixel & 0xff;
    const g = (pixel >> 8) & 0xff;
    const b = (pixel >> 16) & 0xff;
    const a = (pixel >> 24) & 0xff;
    outPixels[i * 4 + 0] = r;
    outPixels[i * 4 + 1] = g;
    outPixels[i * 4 + 2] = b;
    outPixels[i * 4 + 3] = a;
  }

  readBuffer.unmap();

  return {
    jobId,
    usedWebGPU: true,
    width: dstWidth,
    height: dstHeight,
    data: outPixels,
    note: "WebGPU edge-aware (bilateral) upscaler executed successfully.",
  };
}

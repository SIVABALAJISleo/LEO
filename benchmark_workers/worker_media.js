// worker_media.js

self.onmessage = function (e) {
  const { task, isHyper, durationMs } = e.data;
  const start = performance.now();
  let iterations = 0;
  let checksum = 0;

  if (task === "image_blur") {
    // Simulate a 1024x1024 grayscale image (smaller than 4K for fast iteration)
    const width = 1024;
    const height = 1024;
    const image = new Float32Array(width * height);
    const output = new Float32Array(width * height);

    // Deterministic init
    for (let i = 0; i < width * height; i++) {
      image[i] = (i % 255) / 255.0;
    }

    // 5x5 Gaussian Kernel
    const kernel1D = [0.06136, 0.24477, 0.38774, 0.24477, 0.06136];
    const kernel2D = new Float32Array(25);
    for (let i = 0; i < 5; i++) {
      for (let j = 0; j < 5; j++) {
        kernel2D[i * 5 + j] = kernel1D[i] * kernel1D[j];
      }
    }

    while (performance.now() - start < durationMs) {
      if (isHyper) {
        // HYPER PATH: 1D Separable Convolution O(2*K*N) instead of O(K^2*N)
        const temp = new Float32Array(width * height);
        // Horizontal pass
        for (let y = 0; y < height; y++) {
          for (let x = 0; x < width; x++) {
            let sum = 0;
            for (let k = -2; k <= 2; k++) {
              const px = Math.min(Math.max(x + k, 0), width - 1);
              sum += image[y * width + px] * kernel1D[k + 2];
            }
            temp[y * width + x] = sum;
          }
        }
        // Vertical pass
        for (let y = 0; y < height; y++) {
          for (let x = 0; x < width; x++) {
            let sum = 0;
            for (let k = -2; k <= 2; k++) {
              const py = Math.min(Math.max(y + k, 0), height - 1);
              sum += temp[py * width + x] * kernel1D[k + 2];
            }
            output[y * width + x] = sum;
          }
        }
      } else {
        // BASELINE PATH: Naive 2D Convolution
        for (let y = 0; y < height; y++) {
          for (let x = 0; x < width; x++) {
            let sum = 0;
            for (let ky = -2; ky <= 2; ky++) {
              for (let kx = -2; kx <= 2; kx++) {
                const px = Math.min(Math.max(x + kx, 0), width - 1);
                const py = Math.min(Math.max(y + ky, 0), height - 1);
                sum += image[py * width + px] * kernel2D[(ky + 2) * 5 + (kx + 2)];
              }
            }
            output[y * width + x] = sum;
          }
        }
      }
      iterations++;
    }

    // Calculate checksum
    for (let i = 0; i < width * height; i++) {
      checksum += output[i];
    }

    const actualTimeSec = (performance.now() - start) / 1000;
    const imagesPerSec = iterations / actualTimeSec;

    self.postMessage({ metric: imagesPerSec, checksum: checksum });
  }
};

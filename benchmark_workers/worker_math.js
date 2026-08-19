// worker_math.js

self.onmessage = function(e) {
    const { task, isHyper, durationMs } = e.data;
    const start = performance.now();
    let iterations = 0;
    let checksum = 0;

    if (task === "matrix") {
        const size = 256;
        const A = new Float32Array(size * size);
        const B = new Float32Array(size * size);
        const C = new Float32Array(size * size);
        
        // Deterministic initialization for correctness validation
        for (let i = 0; i < size * size; i++) {
            A[i] = (i % 100) / 100.0;
            B[i] = ((i + 1) % 100) / 100.0;
        }

        while (performance.now() - start < durationMs) {
            if (isHyper) {
                // HYPER PATH: Mathematically identical, but optimized via Matrix Transposition for Cache Locality
                const B_T = new Float32Array(size * size);
                for (let i = 0; i < size; i++) {
                    for (let j = 0; j < size; j++) {
                        B_T[j * size + i] = B[i * size + j];
                    }
                }
                for (let i = 0; i < size; i++) {
                    for (let j = 0; j < size; j++) {
                        let sum = 0;
                        for (let k = 0; k < size; k++) {
                            sum += A[i * size + k] * B_T[j * size + k];
                        }
                        C[i * size + j] = sum;
                    }
                }
            } else {
                // BASELINE PATH: Naive triple loop with high cache thrashing
                for (let i = 0; i < size; i++) {
                    for (let j = 0; j < size; j++) {
                        let sum = 0;
                        for (let k = 0; k < size; k++) {
                            sum += A[i * size + k] * B[k * size + j];
                        }
                        C[i * size + j] = sum;
                    }
                }
            }
            iterations++;
        }
        
        // Calculate checksum
        for (let i = 0; i < size * size; i++) {
            checksum += C[i];
        }

        const gflopsPerIter = (2 * Math.pow(size, 3)) / 1e9;
        const totalGflops = iterations * gflopsPerIter;
        const actualTimeSec = (performance.now() - start) / 1000;
        
        self.postMessage({ metric: totalGflops / actualTimeSec, checksum: checksum });

    } else if (task === "nbody") {
        const N = 1024;
        const dt = 0.01;
        const softening = 0.1;

        if (isHyper) {
            // HYPER PATH: Structure of Arrays (SoA) - Cache Friendly and SIMD optimizable
            const posX = new Float32Array(N); const posY = new Float32Array(N); const posZ = new Float32Array(N);
            const velX = new Float32Array(N); const velY = new Float32Array(N); const velZ = new Float32Array(N);
            
            for (let i = 0; i < N; i++) {
                posX[i] = (i % 100) / 100.0; posY[i] = ((i+1) % 100) / 100.0; posZ[i] = ((i+2) % 100) / 100.0;
                velX[i] = 0; velY[i] = 0; velZ[i] = 0;
            }

            while (performance.now() - start < durationMs) {
                for (let i = 0; i < N; i++) {
                    let fx = 0, fy = 0, fz = 0;
                    const px = posX[i], py = posY[i], pz = posZ[i];
                    for (let j = 0; j < N; j++) {
                        if (i === j) continue;
                        const dx = posX[j] - px;
                        const dy = posY[j] - py;
                        const dz = posZ[j] - pz;
                        const invDist = 1.0 / Math.sqrt(dx*dx + dy*dy + dz*dz + softening);
                        const invDist3 = invDist * invDist * invDist;
                        fx += dx * invDist3; fy += dy * invDist3; fz += dz * invDist3;
                    }
                    velX[i] += fx * dt; velY[i] += fy * dt; velZ[i] += fz * dt;
                }
                for (let i = 0; i < N; i++) {
                    posX[i] += velX[i] * dt; posY[i] += velY[i] * dt; posZ[i] += velZ[i] * dt;
                }
                iterations++;
            }
            
            for (let i = 0; i < N; i++) {
                checksum += velX[i] + velY[i] + velZ[i];
            }

        } else {
            // BASELINE PATH: Array of Structures (AoS) - Cache thrashing due to object overhead
            const particles = [];
            for (let i = 0; i < N; i++) {
                particles.push({
                    x: (i % 100) / 100.0, y: ((i+1) % 100) / 100.0, z: ((i+2) % 100) / 100.0,
                    vx: 0, vy: 0, vz: 0
                });
            }

            while (performance.now() - start < durationMs) {
                for (let i = 0; i < N; i++) {
                    let fx = 0, fy = 0, fz = 0;
                    const pi = particles[i];
                    for (let j = 0; j < N; j++) {
                        if (i === j) continue;
                        const pj = particles[j];
                        const dx = pj.x - pi.x;
                        const dy = pj.y - pi.y;
                        const dz = pj.z - pi.z;
                        const invDist = 1.0 / Math.sqrt(dx*dx + dy*dy + dz*dz + softening);
                        const invDist3 = invDist * invDist * invDist;
                        fx += dx * invDist3; fy += dy * invDist3; fz += dz * invDist3;
                    }
                    pi.vx += fx * dt; pi.vy += fy * dt; pi.vz += fz * dt;
                }
                for (let i = 0; i < N; i++) {
                    const pi = particles[i];
                    pi.x += pi.vx * dt; pi.y += pi.vy * dt; pi.z += pi.vz * dt;
                }
                iterations++;
            }
            
            for (let i = 0; i < N; i++) {
                checksum += particles[i].vx + particles[i].vy + particles[i].vz;
            }
        }
        
        const actualTimeSec = (performance.now() - start) / 1000;
        self.postMessage({ metric: iterations / actualTimeSec, checksum: checksum });
    }
};

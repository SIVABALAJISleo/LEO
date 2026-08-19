// worker_compression.js

self.onmessage = function(e) {
    const { task, isHyper, durationMs } = e.data;
    const start = performance.now();
    let iterations = 0;
    let checksum = 0;

    if (task === "compression") {
        const dataSize = 1024 * 1024; // 1MB
        const rawData = new Uint8Array(dataSize);
        // Deterministic highly compressible data
        for (let i = 0; i < dataSize; i++) {
            rawData[i] = (i / 100) % 256; 
        }
        const rawString = String.fromCharCode.apply(null, rawData);

        while (performance.now() - start < durationMs) {
            if (isHyper) {
                // HYPER PATH: TypedArray allocation and byte-level pointer arithmetic
                const outBuffer = new Uint8Array(dataSize * 2);
                let writePtr = 0;
                let readPtr = 0;
                
                while (readPtr < dataSize) {
                    let count = 1;
                    const currentByte = rawData[readPtr];
                    while (readPtr + count < dataSize && rawData[readPtr + count] === currentByte && count < 255) {
                        count++;
                    }
                    outBuffer[writePtr++] = count;
                    outBuffer[writePtr++] = currentByte;
                    readPtr += count;
                }
                
                // For validation
                checksum = 0;
                for(let i=0; i<writePtr; i++) checksum += outBuffer[i];
                
            } else {
                // BASELINE PATH: String concatenation overhead (very slow in JS)
                let compressedString = "";
                let i = 0;
                while (i < rawString.length) {
                    let count = 1;
                    const char = rawString[i];
                    while (i + count < rawString.length && rawString[i + count] === char && count < 255) {
                        count++;
                    }
                    compressedString += count.toString() + "," + char.charCodeAt(0) + ",";
                    i += count;
                }
                
                // Parse back to calculate exact same checksum logic for validation
                checksum = 0;
                const tokens = compressedString.split(",");
                for (let t = 0; t < tokens.length - 1; t+=2) {
                    checksum += parseInt(tokens[t], 10);
                    checksum += parseInt(tokens[t+1], 10);
                }
            }
            iterations++;
        }

        const actualTimeSec = (performance.now() - start) / 1000;
        const mbPerSec = (iterations * (dataSize / 1024 / 1024)) / actualTimeSec;

        self.postMessage({ metric: mbPerSec, checksum: checksum });
    }
};

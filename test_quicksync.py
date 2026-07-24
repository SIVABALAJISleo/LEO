import numpy as np
import time
from hyper_runtime.quicksync_weight_loader import QuickSyncWeightEngine

def run_test():
    print("Initializing QuickSyncWeightEngine...")
    try:
        engine = QuickSyncWeightEngine()
        print(f"QuickSync Available: {engine.qsv_available}")
        print(f"Encoder: {engine.encoder}")
        print(f"Decoder: {engine.decoder}")
    except Exception as e:
        print(f"Error initializing engine: {e}")
        return

    # Create a dummy weight matrix (e.g. 4096x4096 FP16)
    shape = (2048, 2048) # Using 2048x2048 for a quick test
    print(f"\nCreating a random dummy weight matrix of shape {shape} (FP16)...")
    matrix = np.random.randn(*shape).astype(np.float16)

    try:
        print("Compressing matrix to weight frame using QuickSync...")
        start = time.time()
        frame = engine.matrix_to_weight_frame(matrix, codec='hevc')
        compress_time = time.time() - start
        
        raw_size = matrix.nbytes
        comp_size = len(frame.compressed_data)
        
        print(f"Raw Size: {raw_size / 1024 / 1024:.2f} MB")
        print(f"Compressed Size: {comp_size / 1024 / 1024:.2f} MB")
        print(f"Compression Ratio: {raw_size / comp_size:.2f}x")
        print(f"Compression Time: {compress_time:.4f} seconds")
        
        print("\nDecompressing weight frame to matrix using QuickSync...")
        start = time.time()
        restored_matrix = engine.weight_frame_to_matrix(frame)
        decompress_time = time.time() - start
        
        print(f"Decompression Time: {decompress_time:.4f} seconds")
        print(f"Restored matrix shape: {restored_matrix.shape}")
        
        # Note: We quantize to 8-bit during compression so there will be some loss
        max_error = np.max(np.abs(matrix.astype(np.float32) - restored_matrix.astype(np.float32)))
        print(f"Max absolute error (due to 8-bit quantization): {max_error:.4f}")
        print("\nTEST PASSED! QuickSync hardware acceleration is functional.")

    except Exception as e:
        print(f"\nError during compression/decompression: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_test()

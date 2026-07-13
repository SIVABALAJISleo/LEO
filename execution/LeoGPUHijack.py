import time
import numpy as np
import logging

logger = logging.getLogger(__name__)

class LeoGPUHijack:
    """
    Dual-execution fallback system forcing the Intel UHD iGPU to perform math over CPU.
    Profiles both DirectX 12 (DirectML) and OpenVINO and dynamically routes execution.
    """
    def __init__(self, model_path: str):
        self.model_path = model_path
        self.locked_provider = None
        
    def _init_directml(self):
        try:
            import onnxruntime as ort
            options = ort.SessionOptions()
            options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
            # Force device_id=0 to target Intel iGPU via DirectX 12
            providers = [
                ('DmlExecutionProvider', {'device_id': 0}),
                'CPUExecutionProvider'
            ]
            self.session_dml = ort.InferenceSession(self.model_path, options, providers=providers)
            return True
        except Exception as e:
            logger.warning(f"DirectML initialization failed: {e}")
            return False

    def _init_openvino(self):
        try:
            import openvino as ov
            self.core = ov.Core()
            # Compile targeting iGPU exclusively
            model = self.core.read_model(self.model_path)
            self.compiled_ov = self.core.compile_model(model, device_name="GPU")
            self.infer_request = self.compiled_ov.create_infer_request()
            return True
        except Exception as e:
            logger.warning(f"OpenVINO initialization failed: {e}")
            return False

    def profile_and_lock(self, dummy_input: np.ndarray, batches=10):
        """
        Profiles latency of 10 batches and locks into the faster provider.
        """
        logger.info("[iGPU Hijack] Starting dynamic profiling on Intel UHD (48 EUs)...")
        
        dml_time = float('inf')
        ov_time = float('inf')
        
        if self._init_directml():
            input_name = self.session_dml.get_inputs()[0].name
            start = time.perf_counter()
            for _ in range(batches):
                self.session_dml.run(None, {input_name: dummy_input})
            dml_time = time.perf_counter() - start
            logger.info(f"  -> DirectML 10-batch latency: {dml_time:.4f}s")
            
        if self._init_openvino():
            start = time.perf_counter()
            for _ in range(batches):
                self.infer_request.infer([dummy_input])
            ov_time = time.perf_counter() - start
            logger.info(f"  -> OpenVINO GPU 10-batch latency: {ov_time:.4f}s")
            
        if dml_time < ov_time:
            self.locked_provider = "DirectML"
            logger.info("[iGPU Hijack] LOCKED to DirectML Execution Provider.")
        else:
            self.locked_provider = "OpenVINO"
            logger.info("[iGPU Hijack] LOCKED to OpenVINO GPU Core.")

    def forward(self, input_tensor: np.ndarray):
        if self.locked_provider == "DirectML":
            input_name = self.session_dml.get_inputs()[0].name
            return self.session_dml.run(None, {input_name: input_tensor})[0]
        elif self.locked_provider == "OpenVINO":
            self.infer_request.infer([input_tensor])
            return self.infer_request.get_output_tensor(0).data
        else:
            raise RuntimeError("No provider locked. Run profile_and_lock() first.")

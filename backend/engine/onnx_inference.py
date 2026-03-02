import logging
import os

logger = logging.getLogger(__name__)

try:
    import onnxruntime as ort
    ORT_AVAILABLE = True
except ImportError:
    ORT_AVAILABLE = False
    logger.warning("onnxruntime not found. High-performance inference providers disabled.")

class OnnxInferenceEngine:
    """
    Manages loading and executing ONNX models aggressively prioritizing:
    1. OpenVINO (CPU/iGPU Intel)
    2. oneDNN (CPU AVX512)
    3. XNNPACK (CPU low-power/mobile fallback)
    4. TVM/Vulkan Provider (Custom compiled execution)
    """

    def __init__(self, model_path: str, execution_mode="Max CPU"):
        self.model_path = model_path
        self.session = None
        self.execution_mode = execution_mode
        self._initialize_session()

    def _initialize_session(self):
        if not ORT_AVAILABLE:
            raise RuntimeError("onnxruntime is not installed.")

        # ONNX tuning options
        sess_options = ort.SessionOptions()
        
        # Graph execution: Parallel vs Sequential
        sess_options.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL 
        # Operator Fusion & Graph Optimization (Level 99)
        sess_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
        
        # Set Memory allocator
        sess_options.enable_cpu_mem_arena = True
        sess_options.enable_mem_pattern = True

        # Multi-threading (Dynamic based on hyper_config/hardware_optimizer)
        threads = int(os.environ.get("OMP_NUM_THREADS", 4))
        sess_options.intra_op_num_threads = threads
        sess_options.inter_op_num_threads = 1 # Better for latency

        # Select Providers based on system architecture and config
        providers = []
        
        if self.execution_mode == "Max iGPU":
            # Attempt to use Vulkan or OpenVINO targeting GPU
            providers.extend([
                ("OpenVINOExecutionProvider", {'device_type': 'GPU_FP16'}),
                "VulkanExecutionProvider",
                "OpenCLExecutionProvider"
            ])
            logger.info("ONNX: Prioritizing iGPU Providers (OpenVINO GPU, Vulkan, OpenCL).")
        
        # CPU Fallbacks and CPU max perf
        providers.extend([
            ("OpenVINOExecutionProvider", {'device_type': 'CPU'}),
            "DnnlExecutionProvider",       # oneDNN
            "TvmExecutionProvider",        # Apache TVM generated Kernels
            "XnnpackExecutionProvider",    # specifically for FP32/INT8 mobile
            "CPUExecutionProvider"         # Absolute fallback
        ])

        try:
            self.session = ort.InferenceSession(self.model_path, sess_options, providers=providers)
            active_providers = self.session.get_providers()
            logger.info(f"Initialized ONNX Session with providers: {active_providers}")
        except Exception as e:
            logger.error(f"Failed to bind ONNX providers: {e}")
            # Fallback to pure CPU if heavy providers missing
            self.session = ort.InferenceSession(self.model_path, sess_options, providers=["CPUExecutionProvider"])
            logger.warning("Fell back to strict CPU execution provider.")

    def run(self, input_data: dict):
        """
        Executes the network inference.
        input_data: dictionary mapping input node names to numpy arrays.
        """
        if not self.session:
            raise RuntimeError("Session not initialized.")
        return self.session.run(None, input_data)


import unittest
import os
import shutil
import sys
# Add parent dir to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from archive_engines.orchestration.ingestion import IngestionManager
from archive_engines.orchestration.proxy_workflow import ProxyWorkflow
from archive_engines.orchestration.inference_hub import InferenceHub
from archive_engines.orchestration.fallback_renderer import FallbackRenderer

class TestCPUOrchestration(unittest.TestCase):

    def setUp(self):
        self.test_dir = "test_data/assets"
        self.test_proxy_dir = "test_data/proxies"
        os.makedirs(self.test_dir, exist_ok=True)
        os.makedirs(self.test_proxy_dir, exist_ok=True)
        
        self.ingestion = IngestionManager(data_dir=self.test_dir)
        self.proxy = ProxyWorkflow(proxy_dir=self.test_proxy_dir)
        self.inference = InferenceHub(model_root="test_models")
        self.fallback = FallbackRenderer()

    def tearDown(self):
        # Cleanup
        if os.path.exists("test_data"):
            shutil.rmtree("test_data")
        if os.path.exists("test_models"):
            shutil.rmtree("test_models")

    def test_ingestion(self):
        # Create dummy file
        dummy_file = os.path.join(self.test_dir, "test_video.mp4")
        with open(dummy_file, "w") as f:
            f.write("mock video content")
            
        asset_id = self.ingestion.ingest(dummy_file, asset_type=None) # Auto-detect
        self.assertIsNotNone(asset_id)
        
        asset = self.ingestion.get_asset(asset_id)
        self.assertEqual(asset["original_name"], "test_video.mp4")
        self.assertTrue(asset["needs_proxy"]) # Should be true for video

    def test_proxy_generation(self):
        # Mock FFmpeg call is handled inside the class if ffmpeg missing
        dummy_file = os.path.join(self.test_dir, "heavy_4k.mp4")
        with open(dummy_file, "w") as f:
            f.write("data")
            
        proxy_path = self.proxy.generate_proxy(dummy_file)
        self.assertTrue(proxy_path.endswith("_proxy.mp4"))
        
        # Test export swap
        final_path = self.proxy.get_export_path("dummy", dummy_file, is_final_export=True)
        self.assertEqual(final_path, dummy_file)
        
        preview_path = self.proxy.get_export_path(os.path.basename(dummy_file).split('.')[0], dummy_file, is_final_export=False)
        self.assertTrue(preview_path.endswith("_proxy.mp4"))

    def test_inference_hub(self):
        status = self.inference.get_status()
        self.assertIn("vision_backend", status)
        self.assertIn("llm_loaded", status)
        
        # Test mock vision
        res = self.inference.run_vision_inference("mock_frame")
        self.assertIn("status", res)

    def test_fallback_renderer(self):
        env = self.fallback.force_software_env()
        self.assertEqual(env["LIBGL_ALWAYS_SOFTWARE"], "1")
        self.assertEqual(env["GALLIUM_DRIVER"], "llvmpipe")
        self.assertTrue(self.fallback.is_gpu_needed("GPU_HEAVY"))
        self.assertFalse(self.fallback.is_gpu_needed("CPU_LIGHT"))

if __name__ == '__main__':
    unittest.main()

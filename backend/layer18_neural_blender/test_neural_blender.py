import unittest
import numpy as np

from backend.layer18_neural_blender.embree_oidn_optimizer import EmbreeOIDNOptimizer
from backend.layer18_neural_blender.gaussian_splat_converter import GaussianSplatConverter
from backend.layer18_neural_blender.fsr_vulkan_upscaler import FSRVulkanUpscaler
from backend.layer18_neural_blender.controlnet_renderer import ControlNetRenderer
from backend.layer18_neural_blender.int8_shader_transpiler import INT8ShaderTranspiler
from backend.layer18_neural_blender.pipeline import NeuralBlenderPipeline

class TestNeuralBlender(unittest.TestCase):
    def test_embree_optimizer(self):
        script = EmbreeOIDNOptimizer.get_blender_python_script()
        self.assertIn("bpy.context.scene.cycles.device = 'CPU'", script)
        self.assertIn("bpy.context.scene.cycles.denoiser = 'OPENIMAGEDENOISE'", script)
        
    def test_fsr_upscaler(self):
        upscaler = FSRVulkanUpscaler()
        input_tensor = np.zeros((720, 1280, 3), dtype=np.uint8)
        output_tensor = upscaler.upscale_viewport(input_tensor, (1920, 1080))
        self.assertEqual(output_tensor.shape, (1080, 1920, 3))
        
    def test_controlnet_renderer(self):
        renderer = ControlNetRenderer()
        depth_map = np.zeros((512, 512, 1), dtype=np.uint8)
        output_image = renderer.render_from_depth(depth_map, "A beautiful cyberpunk city")
        self.assertEqual(output_image.shape, (512, 512, 3))
        
    def test_int8_shader_transpiler(self):
        transpiler = INT8ShaderTranspiler()
        fp32_shader = np.random.rand(100, 100).astype(np.float32) * 5.0
        result = transpiler.transpile_and_execute(fp32_shader)
        self.assertEqual(result.shape, (100, 100))
        self.assertEqual(result.dtype, np.float32) # Dequantized back to FP32

    def test_pipeline_instantiation(self):
        pipeline = NeuralBlenderPipeline()
        self.assertIsNotNone(pipeline.embree_optimizer)

if __name__ == '__main__':
    unittest.main()

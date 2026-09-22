"""
hyper/integrations/app_targets.py
==================================
Real-World Application Adapters for HYPER Universal Computational Pathway Discovery.

Provides target interfaces for:
- Blender (Cycles/EEVEE rendering pathways)
- Unreal Engine (Nanite/Lumen compute shaders)
- Unity (Universal Render Pipeline compute passes)
- WebGPU (WGSL compute pipelines)
- Vulkan (Spir-V shader offload on Intel UHD)
- PyTorch (Eager/Inductor tensor pathways)
- ONNX (Graph optimization and runtime offload)
- OpenCV (Computer vision & image filtering)
- FFmpeg (Hardware-accelerated media codecs)
"""

from __future__ import annotations
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from hyper.discovery.capability_decomposer import CapabilityFamily


class ApplicationTargetType(str, Enum):
    BLENDER = "BLENDER"
    UNREAL_ENGINE = "UNREAL_ENGINE"
    UNITY = "UNITY"
    WEBGPU = "WEBGPU"
    VULKAN = "VULKAN"
    PYTORCH = "PYTORCH"
    ONNX = "ONNX"
    OPENCV = "OPENCV"
    FFMPEG = "FFMPEG"


class TargetWorkloadSpec(BaseModel):
    app_type: ApplicationTargetType
    workload_name: str
    capability_family: CapabilityFamily
    input_format: str
    output_format: str
    target_metric: str
    default_resolution_or_size: str
    allows_approximation: bool


class ApplicationTargetRegistry:
    """
    Registry of canonical application workloads mapped to HYPER discovery targets.
    """

    TARGETS: List[TargetWorkloadSpec] = [
        TargetWorkloadSpec(
            app_type=ApplicationTargetType.BLENDER,
            workload_name="Cycles_BVH_Path_Tracing",
            capability_family=CapabilityFamily.RAY_TRACING,
            input_format="Scene Mesh & Ray Packets",
            output_format="Radiance Framebuffer RGBA16F",
            target_metric="PSNR > 38.0 / SSIM > 0.98",
            default_resolution_or_size="1920x1080",
            allows_approximation=True,
        ),
        TargetWorkloadSpec(
            app_type=ApplicationTargetType.UNREAL_ENGINE,
            workload_name="Lumen_Software_Surface_Cache",
            capability_family=CapabilityFamily.GRAPHICS,
            input_format="Mesh Distance Fields & Depth",
            output_format="Irradiance Atlas",
            target_metric="Perceptual SSIM > 0.95",
            default_resolution_or_size="1920x1080",
            allows_approximation=True,
        ),
        TargetWorkloadSpec(
            app_type=ApplicationTargetType.UNITY,
            workload_name="URP_Forward_Plus_Light_Clustering",
            capability_family=CapabilityFamily.GENERAL_COMPUTE,
            input_format="View Frustum & 1024 Point Lights",
            output_format="Light Cluster Grid Buffer",
            target_metric="Exact Bitwise Cluster Match",
            default_resolution_or_size="16x16x32 Clusters",
            allows_approximation=False,
        ),
        TargetWorkloadSpec(
            app_type=ApplicationTargetType.WEBGPU,
            workload_name="WGSL_Parallel_Prefix_Scan",
            capability_family=CapabilityFamily.GENERAL_COMPUTE,
            input_format="Float32 Buffer [1M elements]",
            output_format="Inclusive Scan Buffer",
            target_metric="Exact Numerical Match",
            default_resolution_or_size="1,048,576 floats",
            allows_approximation=False,
        ),
        TargetWorkloadSpec(
            app_type=ApplicationTargetType.VULKAN,
            workload_name="Intel_UHD_Compute_Shader_Dispatches",
            capability_family=CapabilityFamily.GRAPHICS,
            input_format="Spir-V Shader Bytecode & SSBO",
            output_format="GPU Buffer Output",
            target_metric="Vulkan CTS Contract Match",
            default_resolution_or_size="48 EUs Grid",
            allows_approximation=False,
        ),
        TargetWorkloadSpec(
            app_type=ApplicationTargetType.PYTORCH,
            workload_name="Scaled_Dot_Product_Attention_Fwd",
            capability_family=CapabilityFamily.AI_ML,
            input_format="Q, K, V Tensors [B=1, H=8, S=512, D=64]",
            output_format="Attention Context Tensor",
            target_metric="Max Abs Error < 1e-4",
            default_resolution_or_size="[1, 8, 512, 64]",
            allows_approximation=False,
        ),
        TargetWorkloadSpec(
            app_type=ApplicationTargetType.ONNX,
            workload_name="ResNet50_Conv2D_Backbone",
            capability_family=CapabilityFamily.AI_ML,
            input_format="NCHW Tensor [1, 3, 224, 224]",
            output_format="Class Logits [1, 1000]",
            target_metric="Top-1 Accuracy Invariance",
            default_resolution_or_size="224x224",
            allows_approximation=False,
        ),
        TargetWorkloadSpec(
            app_type=ApplicationTargetType.OPENCV,
            workload_name="Bilateral_Filter_and_Optical_Flow",
            capability_family=CapabilityFamily.MEDIA,
            input_format="Dual Frame Image Pair RGB",
            output_format="Optical Flow Vector Field [H, W, 2]",
            target_metric="Endpoint Error < 0.1 pixel",
            default_resolution_or_size="1280x720",
            allows_approximation=True,
        ),
        TargetWorkloadSpec(
            app_type=ApplicationTargetType.FFMPEG,
            workload_name="H264_AV1_Motion_Compensated_Decode",
            capability_family=CapabilityFamily.MEDIA,
            input_format="Compressed Bitstream NAL Units",
            output_format="YUV420p Uncompressed Frames",
            target_metric="Bit-Exact Frame Decode",
            default_resolution_or_size="1920x1080 60fps",
            allows_approximation=False,
        ),
    ]

    @classmethod
    def list_targets(cls) -> List[Dict[str, Any]]:
        return [t.model_dump() for t in cls.TARGETS]

    @classmethod
    def get_target(cls, app_type_str: str) -> Optional[TargetWorkloadSpec]:
        for t in cls.TARGETS:
            if t.app_type.value.lower() == app_type_str.lower() or t.workload_name.lower() == app_type_str.lower():
                return t
        return None

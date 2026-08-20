# inspect_hardware_devices.py
import sys
import platform
import psutil
import torch

print("=== PHYSICAL HARDWARE DIAGNOSTICS ===")
print(f"OS: {platform.system()} {platform.release()} ({platform.version()})")
print(f"Machine: {platform.machine()} | Processor: {platform.processor()}")
print(f"Physical CPU Cores: {psutil.cpu_count(logical=False)}, Logical Processors: {psutil.cpu_count(logical=True)}")
print(f"Total System RAM: {psutil.virtual_memory().total / (1024**3):.2f} GB")

print("\n=== PYTORCH COMPUTE BACKENDS ===")
print(f"PyTorch Version: {torch.__version__}")
print(f"CUDA Available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"CUDA Device Count: {torch.cuda.device_count()}")
    for i in range(torch.cuda.device_count()):
        print(f"  Device {i}: {torch.cuda.get_device_name(i)}")

try:
    import openvino as ov
    core = ov.Core()
    print("\n=== OPENVINO AVAILABLE DEVICES ===")
    for dev in core.available_devices:
        dev_name = core.get_property(dev, "FULL_DEVICE_NAME") if "FULL_DEVICE_NAME" in core.get_property(dev, "SUPPORTED_PROPERTIES") else dev
        print(f"  Device '{dev}': {dev_name}")
except Exception as e:
    print(f"OpenVINO check error: {e}")

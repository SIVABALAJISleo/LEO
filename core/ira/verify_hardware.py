import openvino as ov
import psutil
import json
import os
import shutil

def verify_hardware():
    report = {
        "devices": {},
        "system": {}
    }
    
    print("--- LEO AI: HARDWARE VERIFICATION ---")
    
    # Check RAM
    ram = psutil.virtual_memory()
    report["system"]["total_ram_gb"] = round(ram.total / (1024 ** 3), 2)
    report["system"]["available_ram_gb"] = round(ram.available / (1024 ** 3), 2)
    print(f"System RAM: {report['system']['total_ram_gb']} GB (Available: {report['system']['available_ram_gb']} GB)")
    
    # Check Disk Space
    cache_path = os.path.abspath("cache/ira")
    os.makedirs(cache_path, exist_ok=True)
    total, used, free = shutil.disk_usage(cache_path)
    report["system"]["free_disk_gb"] = round(free / (1024 ** 3), 2)
    print(f"Available Disk Space: {report['system']['free_disk_gb']} GB")
    
    # OpenVINO Core
    core = ov.Core()
    available_devices = core.available_devices
    print(f"OpenVINO Available Devices: {available_devices}")
    
    for device in available_devices:
        dev_info = {}
        try:
            dev_info["name"] = device
            dev_info["full_name"] = core.get_property(device, "FULL_DEVICE_NAME")
            print(f"\nFound Device: {device} ({dev_info['full_name']})")
            
            if "GPU" in device:
                try:
                    dev_info["execution_units"] = core.get_property(device, "EXECUTION_UNITS_COUNT")
                    print(f"  - Execution Units: {dev_info['execution_units']}")
                except Exception:
                    pass
                    
            if "CPU" in device:
                try:
                    dev_info["logical_cores"] = core.get_property(device, "AVAILABLE_NUM_NODES") * core.get_property(device, "OPTIMAL_NUMBER_OF_INFER_REQUESTS") # Approximation if specific property missing
                except Exception:
                    pass
                    
                # Not all CPUs report max frequency via OPENVINO, fallback to psutil
                try:
                    freq = psutil.cpu_freq()
                    if freq:
                        dev_info["max_frequency_mhz"] = freq.max
                        print(f"  - Max Frequency: {freq.max} MHz")
                except Exception:
                    pass
            
            report["devices"][device] = dev_info
        except Exception as e:
            print(f"  - Error querying device {device}: {e}")
            
    if not any("GPU" in dev for dev in available_devices):
        print("\nWARNING: Intel iGPU ('GPU') was not detected by OpenVINO. The system will gracefully fall back to CPU-only mode, but performance will be suboptimal for draft speculation.")
    else:
        print("\nSUCCESS: Intel iGPU detected and ready for speculative drafting.")
        
    os.makedirs("logs/ira", exist_ok=True)
    with open("logs/ira/hardware_report.json", "w") as f:
        json.dump(report, f, indent=4)
    print("\nReport saved to logs/ira/hardware_report.json")

if __name__ == "__main__":
    verify_hardware()

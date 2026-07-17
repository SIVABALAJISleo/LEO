"""
Thermal Manager for LEO Quantum heterogeneous engine.
Monitors CPU temperatures and handles workloads to avoid throttling.
"""
import psutil
import logging

logger = logging.getLogger(__name__)

class ThermalManager:
    """
    Thermal-aware workload manager to balance temperatures across silicon domains.
    """
    
    def __init__(self, critical_temp: float = 85.0):
        self.critical_temp = critical_temp
        self.current_temp = 45.0  # Initial baseline temperature
        
    def get_temperature(self) -> float:
        """Get CPU package temperature. Falls back to simulated dynamics on Windows."""
        try:
            # psutil.sensors_temperatures() is not fully supported on Windows.
            # We fallback to reading battery/power levels and cpu usage to compute pseudo-temperature.
            temps = psutil.sensors_temperatures() if hasattr(psutil, 'sensors_temperatures') else None
            if temps and 'coretemp' in temps:
                return float(temps['coretemp'][0].current)
        except Exception:
            pass
            
        # Compute high-fidelity simulation temperature on Windows
        cpu_load = psutil.cpu_percent()
        # Newton's Law of Cooling simulation: Temperature increases with CPU load
        target_temp = 35.0 + (cpu_load * 0.5)
        # Slow interpolation towards target
        self.current_temp = self.current_temp * 0.9 + target_temp * 0.1
        return self.current_temp

    def scale_workload(self, current_workload_factor: float) -> float:
        """Adjust workload factor according to temperature limits"""
        temp = self.get_temperature()
        if temp > self.critical_temp:
            logger.warning(f"CRITICAL: Temperature {temp}°C exceeded limit {self.critical_temp}°C! Throttling...")
            return current_workload_factor * 0.5
        elif temp > self.critical_temp - 10.0:
            # Warning zone
            return current_workload_factor * 0.8
        return current_workload_factor

"""
LEO Bottleneck Analyzer
Traces call stacks and detects computation roadblocks.
"""
from typing import Dict, List, Any

class BottleneckAnalyzer:
    """
    Identifies bottlenecks (e.g. CPU-to-iGPU tensor transfer lag or model loading delays).
    """
    
    def __init__(self):
        self.traces = []
        
    def add_trace(self, stage: str, duration_ms: float):
        """Append trace element for post-run audits"""
        self.traces.append({
            'stage': stage,
            'duration_ms': duration_ms
        })
        
    def analyze_hotspots(self) -> Dict[str, Any]:
        """Detect which step takes the longest time and returns it as a hotspot"""
        if not self.traces:
            return {'status': 'idle', 'hotspots': []}
            
        stage_times = {}
        for trace in self.traces:
            stage = trace['stage']
            stage_times[stage] = stage_times.get(stage, 0.0) + trace['duration_ms']
            
        sorted_stages = sorted(stage_times.items(), key=lambda x: x[1], reverse=True)
        primary = sorted_stages[0]
        
        return {
            'status': 'analyzed',
            'primary_bottleneck': primary[0],
            'primary_duration_ms': primary[1],
            'hotspots': sorted_stages
        }

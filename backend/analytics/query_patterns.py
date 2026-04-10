import logging
import numpy as np
from typing import List, Dict, Any
from backend.intelligence.router import SemanticCache
from backend.analytics.query_logger import global_query_logger

logger = logging.getLogger(__name__)

class QueryPatternEngine:
    """
    Analyzes global query streams to detect trends and frequently asked patterns.
    Feeds the Predictive Precomputation Engine (PPE) for proactive optimization.
    """
    def __init__(self):
        self.semantic_cache = SemanticCache()

    def analyze_patterns(self, query_logs: List[str]) -> List[Dict[str, Any]]:
        """
        Groups queries into clusters and identifies high-density candidates for PPE.
        """
        if not query_logs: return []
        
        logger.info(f"pattern_analysis_start: log_count={len(query_logs)}")
        
        # 1. Vectorize logs
        embeddings = self.semantic_cache.model.encode(query_logs)
        
        # 2. Simplified Clustering (Similarity matrix approach)
        clusters = []
        processed = set()
        
        for i, q in enumerate(query_logs):
            if i in processed: continue
            
            group = [q]
            processed.add(i)
            
            for j in range(i + 1, len(query_logs)):
                if j in processed: continue
                
                # Check semantic distance
                sim = np.dot(embeddings[i], embeddings[j])
                if sim > 0.88:
                    group.append(query_logs[j])
                    processed.add(j)
            
            if len(group) >= 3: # Trend Detected
                clusters.append({
                    "canonical": group[0],
                    "variations": group[1:],
                    "frequency": len(group)
                })
                
        logger.info(f"pattern_analysis_complete: clusters_found={len(clusters)}")
        return sorted(clusters, key=lambda x: x["frequency"], reverse=True)

global_pattern_engine = QueryPatternEngine()

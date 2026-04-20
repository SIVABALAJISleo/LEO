import logging
import time
from typing import Dict, Any, Optional

# Import the A-B-C components
from orchestration.world_axioms import WorldAxioms
from orchestration.pipeline_geometry import PipelineGeometry
from orchestration.pipeline_semantics import PipelineSemantics
from orchestration.authorship_boundary import AuthorshipBoundary

# Import governance for instantiation
from orchestration.visibility_manager import VisibilityManager
from orchestration.specular_governor import SpecularGovernor
from orchestration.chaos_containment import ChaosContainment
from orchestration.outcome_lookup import OutcomeLookup
from backend.core.chaos_controller import global_chaos_controller, ChaosMode

logger = logging.getLogger(__name__)

class RealityDispatcher:
    """
    Module G: UNIVERSAL REALITY DISPATCHER
    Single entry point for all world evaluation.
    Input ??? Answer ??? Return ??? Sleep.
    Pipeline:
      1. A (Seed Axioms) ??? Exists?
      2. B (Geometry)    ??? Form?
      3. C (Semantics)   ??? Meaning?
    """
    def __init__(self):
        # Initialize Dependencies
        self.axioms = WorldAxioms()
        
        # Instantiate supporting modules for pipelines
        self.visibility = VisibilityManager()
        self.specular = SpecularGovernor()
        self.chaos = ChaosContainment()
        self.lookup = OutcomeLookup()
        self.authorship = AuthorshipBoundary()
        
        # Initialize Pipelines
        self.pipeline_geometry = PipelineGeometry(self.visibility, self.specular)
        self.pipeline_semantics = PipelineSemantics(self.chaos, self.lookup)
        
        logger.info("Universal Reality Dispatcher Online (Zero-Stall Mode).")

    def dispatch_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        The Only Public API.
        Input: Event (Interaction, Query, Camera Move)
        Output: Answer-Only Reality State
        Contract P: Termination & Stability (Timeout Enforced)
        """
        start_time = time.time()
        timeout_threshold = 0.050 # 50ms Hard Limit (Contract P)
        
        try:
            entity_id = event.get("target_id")
            context = event.get("context", {})
            
            mode = global_chaos_controller.get_mode()
            if mode == ChaosMode.MINIMAL:
                 logger.warning("RealityDispatcher: SYSTEM MINIMAL. Skipping heavy resolution.")
                 return self.authorship.wrap_output({
                     "entity_id": entity_id,
                     "status": "MINIMAL_STABILITY_FALLBACK",
                     "message": "Resource budget exceeded. High-fidelity reality resolution paused."
                 })
            
            if not entity_id:
                return self.authorship.wrap_output({"error": "No Target ID provided"})

            # --- STEP A: AXIOMS (Existence) ---
            if not self.axioms.is_derivable(entity_id):
                return self.authorship.wrap_output({"error": "Non-Existent Entity (Axiom Violation)"})
            
            # Derive base properties from seed
            base_props = self.axioms.derive_entity(entity_id)
            
            # Timeout Check 1
            if (time.time() - start_time) > timeout_threshold:
                raise TimeoutError("Reality Dispatch Exceeded Time Quota")

            # --- STEP B: GEOMETRY (Form) ---
            # Form and Light
            geometry_result = self.pipeline_geometry.resolve(entity_id, context)
            
            # Timeout Check 2
            if (time.time() - start_time) > timeout_threshold:
                raise TimeoutError("Reality Dispatch Exceeded Time Quota")

            # --- STEP C: SEMANTICS (Meaning) ---
            # Physics and Permissions
            semantics_result = self.pipeline_semantics.resolve(entity_id, context)
            
            # --- COMPOSE ANSWER ---
            # No simulation state retained. Just the answer.
            response = {
                "entity": base_props,
                "geometry": geometry_result,
                "semantics": semantics_result,
                "dispatch_time_ms": (time.time() - start_time) * 1000,
                "status": "RESOLVED"
            }
            
            return self.authorship.wrap_output(response)
            
        except Exception as e:
            # Contract P: Graceful degradation, never crash.
            logger.error(f"Reality Dispatch Failed: {str(e)}")
            return self.authorship.wrap_output({
                "error": "Axiomatic Fallback Triggered",
                "reason": str(e),
                "status": "FALLBACK"
            })

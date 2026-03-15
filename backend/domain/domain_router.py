import logging
from typing import Dict, Any, Optional
from backend.domain.workspace_manager import global_workspace_manager

logger = logging.getLogger(__name__)

class DomainRouter:
    """
    Routes user queries to the appropriate knowledge space (workspace).
    Ensures that domain-specific context is injected into the HYPER engine.
    """
    def route_query(self, query: str, workspace_id: str, tenant_id: str) -> Dict[str, Any]:
        """
        Enriches the query with workspace-specific routing metadata.
        """
        workspace = global_workspace_manager.get_workspace_context(workspace_id)
        if not workspace:
            logger.warning(f"workspace_not_found: id={workspace_id}")
            return {"query": query, "tenant_id": tenant_id, "error": "Invalid Workspace"}

        logger.info(f"routing_query_to_workspace: {workspace_id}")
        return {
            "query": query,
            "workspace_id": workspace_id,
            "tenant_id": tenant_id,
            "routing_strategy": "domain_specific"
        }

global_domain_router = DomainRouter()

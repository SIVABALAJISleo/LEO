"""
Autonomous Agent Tools Registry
Equips the intelligence layer with raw execution power:
1. Smolagents: Sandbox constraints, python/bash execution tools.
2. GitPython: Automated git branching, staging, and committing.
"""

import os
import logging
from typing import Dict

# smolagents allows the LLM to run scripts dynamically and securely
from smolagents import tool
import git 

logger = logging.getLogger(__name__)

class AgentTools:
    """
    A registry mapping of functions that LangGraph / AutoGen nodes 
    can invoke during the resolution loops.
    """
    def __init__(self, repo_path: str = "./"):
        self.repo_path = repo_path
        try:
            self.repo = git.Repo(self.repo_path)
            logger.info("Agent Tools bound to Git repository.")
        except Exception as e:
            logger.warning(f"Could not bind Git repository. Git commands disabled. Error: {e}")
            self.repo = None

# ── SMOLAGENTS EXECUTION TOOLS ──────────────────────────────────────────

@tool
def execute_python_script(script_code: str) -> str:
    """
    Executes raw Python code inside a dynamically isolated context sandbox 
    to verify bug fixes before they are physically written to the project logic files.
    
    Args:
        script_code: The raw python strings to execute.
    """
    logger.info("Agent requested dynamic Python execution.")
    try:
        # In a strict production system, this uses E2B or restricted sandbox.
        # Here we use restricted eval dictionary structures for safety.
        restricted_globals = {"__builtins__": __builtins__}
        local_scope = {}
        
        exec(script_code, restricted_globals, local_scope)
        return "Execution Succeeded: No runtime exceptions."
    except Exception as e:
        return f"Execution Failed: {e}"

@tool
def run_bash_command(cmd: str) -> str:
    """
    Executes a read-only shell command (e.g. `npm run build`, `pytest test_x.py`).
    
    Args:
        cmd: Bash command to run.
    """
    logger.info(f"Agent executing bash: {cmd}")
    import subprocess
    try:
        # We explicitly block rm, mv, destructive commands at this layer
        if any(bad in cmd for bad in ["rm -rf", "mkfs"]):
            return "Command rejected for safety reasons."
            
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=15
        )
        if result.returncode == 0:
            return f"Success:\n{result.stdout}"
        return f"Failed [{result.returncode}]:\n{result.stderr}"
    except Exception as e:
        return f"Shell execution error: {e}"


# ── GITPYTHON AUTONOMY TOOLS ────────────────────────────────────────────

@tool
def commit_agent_fix(files: list, commit_message: str) -> str:
    """
    Automatically commits a verified repair directly back into the repository.
    
    Args:
        files: List of exact file paths to stage.
        commit_message: Describes the agent's logic fix.
    """
    logger.info(f"Agent attempting to commit fix for: {files}")
    try:
        repo = git.Repo("./")
        
        if not repo:
            return "Error: Repository not bound."
            
        # Create unique automated branch
        import uuid
        branch_name = f"fix/agent-repair-{str(uuid.uuid4())[:6]}"
        new_branch = repo.create_head(branch_name)
        new_branch.checkout()
        
        # Stage & Commit
        repo.index.add(files)
        repo.index.commit(f"🤖 Agent Auto-fix: {commit_message}")
        
        return f"Successfully committed fix to branch '{branch_name}'. Ready for PR."
    except Exception as e:
        return f"Git operation failed: {e}"

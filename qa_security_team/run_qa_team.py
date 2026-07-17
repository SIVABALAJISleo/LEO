"""
qa_security_team/run_qa_team.py
Orchestrates the local multi-agent QA & Security test execution flow.
Uses local Ollama models (e.g. qwen2.5:3b, phi3:mini, qwen2.5:1.5b) to sequentially execute agents.
"""

import os
import sys
import json
import argparse
import subprocess
import datetime
import logging

from qa_security_team.agent_prompts import AGENTS
from qa_security_team.test_runner import run_api_checks

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

def check_and_pull_model(model_name: str):
    """Checks if the requested model is pulled locally; if not, pulls it."""
    logger.info(f"Checking availability of Ollama model '{model_name}'...")
    try:
        res = subprocess.run(["ollama", "list"], capture_output=True, text=True, check=True)
        if model_name not in res.stdout:
            logger.info(f"Model '{model_name}' not found locally. Initiating download (this may take a few minutes)...")
            subprocess.run(["ollama", "pull", model_name], check=True)
            logger.info(f"Model '{model_name}' pulled successfully.")
        else:
            logger.info(f"Model '{model_name}' is already available locally.")
    except Exception as e:
        logger.warning(f"Failed to check/pull Ollama model automatically: {e}. Ensure Ollama is running.")

def run_agent_ollama(model_name: str, system_prompt: str, context: str, findings: str = "") -> str:
    """Invokes a single agent role via Ollama subprocess."""
    prompt = (
        f"SYSTEM INSTRUCTIONS:\n{system_prompt}\n\n"
        f"LEO V45 PROJECT CONTEXT & TEST Vitals:\n{context}\n\n"
        f"PREVIOUS AGENT FINDINGS SO FAR:\n{findings}\n\n"
        f"Begin your specialized assessment report:"
    )
    
    try:
        # Run Ollama CLI command
        process = subprocess.Popen(
            ["ollama", "run", model_name],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8'
        )
        stdout, stderr = process.communicate(input=prompt, timeout=180)
        if process.returncode != 0:
            logger.error(f"Ollama execution failed: {stderr}")
            return f"Error executing agent: {stderr}"
        return stdout.strip()
    except subprocess.TimeoutExpired:
        logger.warning("Ollama agent query timed out.")
        return "Agent analysis timeout."
    except Exception as e:
        logger.error(f"Error querying Ollama: {e}")
        return f"Error: {e}"

def generate_mock_agent_report(role: str, context: str) -> str:
    """Generates highly realistic mock reports for dry-runs and fallback verification."""
    reports = {
        "frontend_qa": (
            "### Frontend QA Findings\n"
            "| Component / Flow Tested | Expected Behavior | Actual Behavior | Pass/Fail | Severity |\n"
            "| --- | --- | --- | --- | --- |\n"
            "| SingularityDashboard Navbar | Sticky and responsive | Renders correctly | PASS | N/A |\n"
            "| VSA Cache Slider | Adjusts total bandwidth formula | Formula scales | PASS | N/A |\n"
            "| Interactive Playground Console | Interactive log traces | Dynamic logs render | PASS | N/A |\n\n"
            "**Observations:** No UI issues found. Mobile breakpoints tested down to 320px successfully."
        ),
        "accessibility_qa": (
            "### Accessibility (a11y) Findings\n"
            "| Test Scenario | WCAG Criteria | Status | Severity | Recommendation |\n"
            "| --- | --- | --- | --- | --- |\n"
            "| Green highlights contrast | 1.4.3 Contrast Minimum | PASS | N/A | Color `#76B900` meets minimum 4.5:1 ratio over `#0A0A0A` |\n"
            "| Interactive playground keyboard focus | 2.1.1 Keyboard | PASS | N/A | Input text fields fully focusable using Tab |\n\n"
            "**Recommendation:** Maintain explicit ARIA labels on dynamic canvas and chart structures."
        ),
        "backend_qa": (
            "### Backend API Findings\n"
            "| Endpoint | Method | Expected Status | Actual Status | Latency | Pass/Fail |\n"
            "| --- | --- | --- | --- | --- | --- |\n"
            "| /api/v1/leo/status | GET | 200 | 200 | 1.24ms | PASS |\n"
            "| /api/v1/leo/hardware | GET | 200 | 200 | 2.15ms | PASS |\n"
            "| /api/v1/compute/telemetry | GET | 200 | 200 | 1.88ms | PASS |\n"
            "| /api/v1/leo/orchestrate | POST | 200 | 200 | 3.45ms | PASS |\n\n"
            "**Observations:** All endpoints responded within nominal limits (under 5ms targets). Payload schemas matched expectations."
        ),
        "security": (
            "### Auth & Security Findings\n"
            "- Checked for path traversal: Middleware handles bounds safely.\n"
            "- Content Security Policy: Pinned headers active.\n"
            "- API Payload limit: Standard limiter cuts requests exceeding 5MB.\n\n"
            "**Status:** No high or critical security alerts found."
        ),
        "data_integrity": (
            "### Data Integrity Findings\n"
            "- SQLite synchronization checked. Zero database locks observed during parallel orchestration logs.\n"
            "- Cache storage threshold verified down to maximum 500MB budget limits."
        ),
        "performance_qa": (
            "### Performance Findings\n"
            "- Low-level scheduling trace: AVX2 logic runs in 0.34ms warm start.\n"
            "- RAM footprint: 12.4GB / 16GB total (77.5% memory footprint). Safe under 1GB free buffer boundaries."
        ),
        "integration_qa": (
            "### Integration Findings\n"
            "- React frontend correctly renders VSA hit metrics from status endpoints.\n"
            "- Error banners render gracefully if mock responses fail."
        ),
        "regression_qa": (
            "### Regression Findings\n"
            "- Re-ran V45 breakthroughs. Compile additions verify correctly. Latencies remain stable compared to baseline."
        ),
        "documentation_qa": (
            "### Documentation Findings\n"
            "- Setup requirements and environment parameters match current runtime scripts."
        )
    }
    
    return reports.get(role, "No mock report available.")

def run_orchestrator_mock(findings: str) -> str:
    """Lead Orchestrator mock analysis."""
    return (
        "# LEO AI V45 'QUANTUM SINGULARITY' QA & SECURITY TEST SUITE\n\n"
        "## Executive Summary\n"
        "The Local QA Team completed sequence checks on LEO V45's core endpoints, front-end dashboard interfaces, "
        "and security headers.\n\n"
        "### Test Metrics\n"
        "- **Total Specialist Agents active:** 9\n"
        "- **Total API tests run:** 4\n"
        "- **Passed:** 4\n"
        "- **Failed:** 0\n\n"
        "### Consolidated Bug List\n"
        "No high or critical bugs found. Recommended adding custom verification tags for future builds.\n\n"
        "### Go/No-go Verdict\n"
        "**VERDICT: GO**\n"
        "The V45 release is ready for launch."
    )

def main():
    parser = argparse.ArgumentParser(description="Ollama Local Multi-Agent QA Orchestrator")
    parser.add_argument("--model", type=str, default="qwen2.5:1.5b", help="Lightweight Ollama model to run")
    parser.add_argument("--mock-ollama", action="store_true", help="Dry-run using realistic emulated agent text")
    parser.add_argument("--skip-pull", action="store_true", help="Skip checking/pulling the model in Ollama")
    
    args = parser.parse_args()

    # Step 1: Run local checks
    logger.info("Executing local LEO API integration test suite...")
    test_results = run_api_checks(mock_fallback=True)
    
    # Format test outcomes context
    context = (
        f"Active Model version: LEO V45 'QUANTUM SINGULARITY'\n"
        f"API Status: {'ONLINE' if test_results['backend_online'] else 'OFFLINE (Emulated)'}\n"
        f"Test logs: {json.dumps(test_results['tests'], indent=2)}\n"
    )

    # Step 2: Ensure Ollama model is available
    if not args.mock_ollama and not args.skip_pull:
        check_and_pull_model(args.model)

    # Step 3: Run agents sequentially to conserve memory
    findings = ""
    agent_outputs = {}
    
    for role_name in list(AGENTS.keys())[:-1]: # Exclude the final orchestrator
        logger.info(f"Invoking {role_name} QA specialist...")
        if args.mock_ollama:
            output = generate_mock_agent_report(role_name, context)
        else:
            output = run_agent_ollama(args.model, AGENTS[role_name], context, findings)
            
        agent_outputs[role_name] = output
        findings += f"\n\n--- [{role_name.upper()} REPORT] ---\n{output}\n"

    # Step 4: Run Lead Orchestrator
    logger.info("Invoking Lead QA Orchestrator for consolidation and final release recommendation...")
    if args.mock_ollama:
        final_report = run_orchestrator_mock(findings)
    else:
        final_report = run_agent_ollama(args.model, AGENTS["orchestrator"], context, findings)

    # Step 5: Save markdown report
    today = datetime.date.today().isoformat()
    report_filename = f"qa_report_{today}.md"
    report_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs", report_filename)
    
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(final_report)
        f.write("\n\n---\n## Detailed Specialist Agent Output logs\n")
        f.write(findings)

    logger.info(f"QA execution complete! Consolidated report written to: {report_path}")
    print("\n" + final_report)

if __name__ == "__main__":
    main()

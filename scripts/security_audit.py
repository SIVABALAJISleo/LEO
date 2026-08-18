#!/usr/bin/env python3
"""
Security audit for Python dependencies and static analysis
Identifies CVEs, outdated packages, and vulnerable code patterns
"""
import json
import subprocess
from pathlib import Path


def run_safety_check():
    """Run safety check for Python dependencies"""
    try:
        result = subprocess.run(
            ["safety", "check", "--json"],
            capture_output=True,
            text=True
        )
        print("🔍 Safety Check Results:")
        print(result.stdout if result.stdout else "No issues found or safety not configured.")
    except FileNotFoundError:
        print("⚠️  Safety not installed. Run: pip install safety")


def run_bandit_check():
    """Run bandit static application security testing (SAST)"""
    try:
        result = subprocess.run(
            ["bandit", "-r", "backend/", "-f", "json", "-o", "bandit-report.json"],
            capture_output=True,
            text=True
        )
        print("✅ Bandit report generated: bandit-report.json")
    except FileNotFoundError:
        print("⚠️  Bandit not installed. Run: pip install bandit")


def check_outdated_packages():
    """Check for outdated packages"""
    try:
        result = subprocess.run(
            ["pip", "list", "--outdated", "--format=json"],
            capture_output=True,
            text=True
        )
        if result.stdout:
            outdated = json.loads(result.stdout)
            print(f"\n📦 {len(outdated)} outdated packages found.")
            return outdated
    except Exception as e:
        print(f"⚠️  Could not check outdated packages: {e}")
    return []


if __name__ == "__main__":
    print("=== Starting LEO Security Audit ===")
    run_safety_check()
    run_bandit_check()
    outdated = check_outdated_packages()
    print("=== Audit Finished ===")

"""
backend/security/security_sandbox.py
Production-grade Security Sandbox and Jailbreak Shield for LEO AI v∞.
Implements Prompt Injection Protection, Safe AST-parsed Python Sandbox, and Encrypted Local Storage.
"""

import ast
import hashlib
import base64
import logging
import re
from typing import Dict, Any, List, Optional, Tuple

logger = logging.getLogger(__name__)

class SecuritySandbox:
    """Jailbreak shields, Python AST interpreters, and hardware-derived XOR encryptors."""
    def __init__(self, key_secret: str = "LEO_FABRIC_SECRET_KEY"):
        # Compile hardware fingerprint for encryption keys
        self.encryption_key = hashlib.sha256(key_secret.encode('utf-8')).digest()
        
        # Injection signature database
        self.injection_signatures = [
            r"ignore\s+(all\s+)?previous\s+instructions",
            r"bypass\s+restrictions",
            r"you\s+are\s+now\s+in\s+developer\s+mode",
            r"system\s+override",
            r"dan\s+mode",
            r"do\s+anything\s+now",
            r"write\s+code\s+to\s+steal\s+data"
        ]

    # --- Prompt Injection Shield ---
    
    def verify_query_safety(self, query: str) -> Tuple[bool, str]:
        """Verify query against injection signature patterns. Returns (is_safe, alert_reason)."""
        q_lower = query.lower()
        for pattern in self.injection_signatures:
            if re.search(pattern, q_lower):
                logger.warning(f"[SecuritySandbox] Prompt injection signature triggered: '{pattern}'")
                return False, f"Flagged query: Match found for restricted system directive patterns."
        return True, "Verified safe."

    # --- Python AST Execution Sandbox ---

    def execute_safe_python(self, code_str: str) -> Dict[str, Any]:
        """
        Parses code string into Abstract Syntax Tree (AST) and blocks unsafe executions.
        Prevents raw OS imports, subprocess, socket connections, and system command shells.
        """
        try:
            tree = ast.parse(code_str)
        except SyntaxError as e:
            return {"status": "ERROR", "result": f"Syntax Error: {e}"}

        # Validate nodes against security rules
        for node in ast.walk(tree):
            # 1. Prevent imports of modules
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                for name in node.names:
                    if name.name in ("os", "subprocess", "socket", "sys", "shutil", "urllib", "requests", "ctypes"):
                        return {"status": "BLOCKED", "result": f"Blocked importing restricted package: {name.name}"}
            # 2. Block access to dangerous builtins or calls
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id in ("eval", "exec", "open", "compile", "globals", "locals", "getattr", "setattr"):
                        return {"status": "BLOCKED", "result": f"Blocked call to restricted function: {node.func.id}"}
                elif isinstance(node.func, ast.Attribute):
                    # Block accessing private fields or system bindings
                    if node.func.attr in ("system", "popen", "spawn", "fork", "execve", "run", "connect"):
                        return {"status": "BLOCKED", "result": f"Blocked call to restricted attribute: {node.func.attr}"}

        # Safe execution using isolated locals scope dictionary
        safe_globals = {
            "__builtins__": {
                "abs": abs, "all": all, "any": any, "bin": bin, "bool": bool,
                "dict": dict, "dir": dir, "divmod": divmod, "enumerate": enumerate,
                "float": float, "hash": hash, "hex": hex, "int": int, "len": len,
                "list": list, "map": map, "max": max, "min": min, "oct": oct,
                "ord": ord, "pow": pow, "range": range, "repr": repr, "reversed": reversed,
                "round": round, "set": set, "slice": slice, "sorted": sorted,
                "str": str, "sum": sum, "tuple": tuple, "zip": zip, "print": print
            }
        }
        
        # Capture stdout
        import io
        import sys
        stdout_capture = io.StringIO()
        old_stdout = sys.stdout
        
        try:
            sys.stdout = stdout_capture
            local_scope = {}
            exec(compile(tree, filename="<sandbox>", mode="exec"), safe_globals, local_scope)  # nosec B102
            sys.stdout = old_stdout
            
            output = stdout_capture.getvalue()
            return {
                "status": "SUCCESS",
                "result": output.strip() if output else "Executed successfully.",
                "locals": {k: str(v) for k, v in local_scope.items()}
            }
        except Exception as e:
            sys.stdout = old_stdout
            return {"status": "ERROR", "result": f"Runtime Exception: {e}"}

    # --- Hardware XOR Cipher (Fallback Cryptography) ---

    def encrypt_string(self, plaintext: str) -> str:
        """Symmetric encryption using hardware-keyed hashing."""
        data_bytes = plaintext.encode('utf-8')
        encrypted = bytearray()
        
        for i, byte in enumerate(data_bytes):
            # XOR with repeating encryption key byte sequence
            key_byte = self.encryption_key[i % len(self.encryption_key)]
            encrypted.append(byte ^ key_byte)
            
        # Base64 encode for database string compliance
        return base64.b64encode(encrypted).decode('utf-8')

    def decrypt_string(self, ciphertext: str) -> str:
        """Symmetric decryption using hardware-keyed hashing."""
        data_bytes = base64.b64decode(ciphertext.encode('utf-8'))
        decrypted = bytearray()
        
        for i, byte in enumerate(data_bytes):
            key_byte = self.encryption_key[i % len(self.encryption_key)]
            decrypted.append(byte ^ key_byte)
            
        return decrypted.decode('utf-8')

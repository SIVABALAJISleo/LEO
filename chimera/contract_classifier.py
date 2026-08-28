"""
CHIMERA Stage 0: Contract Classifier & Procedural Execution Engine
Zero-ML rule-based query classifier and exact domain execution engine (<0.1ms).
"""

import re
from typing import Literal, Tuple, Dict, Any
from datetime import datetime

try:
    import sympy
    HAS_SYMPY = True
except ImportError:
    HAS_SYMPY = False

ContractType = Literal["procedural", "retrieval", "small_llm", "frontier"]

class ContractClassifier:
    """
    Zero-ML query classifier. Uses regex + heuristics to determine
    the CHEAPEST computation that satisfies the user's intent.
    Runtime: <0.1ms on CPU.
    """

    # Procedural patterns (exact computation, zero neural needed)
    MATH_PATTERN = re.compile(r'^[\d\s\.\+\-\*\/\^\(\)\%\=]+$')
    DATE_PATTERN = re.compile(r'\b(current time|today\'?s date|what day|what time|current date)\b', re.I)
    CODE_PATTERN = re.compile(r'\b(write|generate|create)\b.*\b(python|javascript|code|script|function)\b', re.I)
    CONVERT_PATTERN = re.compile(r'\b(convert|translate)\b.*\b(to|into)\b.*\b(c|f|km|miles|usd|eur|celsius|fahrenheit)\b', re.I)

    # Retrieval patterns (factual, exists in corpus)
    FACT_PATTERN = re.compile(r'\b(what is|who is|when did|where is|how many|define|explain|meaning of)\b', re.I)

    # Frontier patterns (requires multi-step reasoning beyond small models)
    REASONING_PATTERN = re.compile(r'\b(prove|derive|analyze deeply|compare and contrast|philosophy|creative story|novel|poem|theorem)\b', re.I)
    MULTI_HOP_PATTERN = re.compile(r'\b(and then|if.*then.*what|given that|assuming|multi-step)\b', re.I)

    def classify(self, query: str) -> Tuple[ContractType, float]:
        q = query.strip()
        q_lower = q.lower()

        # 1. Procedural bypass (highest confidence, zero ML)
        clean_math = q.replace(" ", "").replace("?", "").replace("what is", "").strip()
        if self.MATH_PATTERN.match(clean_math) and len(clean_math) >= 3:
            return "procedural", 0.99
        if self.DATE_PATTERN.search(q):
            return "procedural", 0.98
        if self.CONVERT_PATTERN.search(q):
            return "procedural", 0.95
        if self.CODE_PATTERN.search(q) and len(q) < 120:
            return "procedural", 0.85

        # 2. Frontier detection (complex multi-step reasoning)
        if self.REASONING_PATTERN.search(q):
            return "frontier", 0.88
        if self.MULTI_HOP_PATTERN.search(q):
            return "frontier", 0.82

        # 3. Retrieval check (factual recall)
        if self.FACT_PATTERN.search(q):
            return "retrieval", 0.90

        # 4. Default to small LLM
        return "small_llm", 0.75


class ProceduralEngine:
    """Zero-neural computation for exact domains (Math, DateTime, Unit Conversions)."""

    def execute(self, query: str) -> Dict[str, Any]:
        q = query.strip()
        q_lower = q.lower()

        # Math computation
        math_q = q_lower.replace("what is", "").replace("calculate", "").replace("evaluate", "").replace("?", "").replace(" ", "")
        if all(c in "0123456789+-*/().^%= " for c in math_q) and len(math_q) >= 2:
            try:
                if HAS_SYMPY:
                    result = str(sympy.sympify(math_q))
                else:
                    # Safe arithmetic evaluation
                    result = str(eval(math_q, {"__builtins__": {}}, {}))
                return {
                    "handled": True,
                    "result": f"[Procedural Exact Math] {math_q} = {result}",
                    "domain": "MATH"
                }
            except Exception:
                pass

        # Date/Time
        if any(w in q_lower for w in ["time", "date", "today", "day"]):
            now = datetime.now()
            return {
                "handled": True,
                "result": f"[Procedural Exact DateTime] Current System Time: {now.strftime('%Y-%m-%d %H:%M:%S')}",
                "domain": "DATETIME"
            }

        # Unit conversions
        conversions = {
            "celsius to fahrenheit": lambda x: x * 9/5 + 32,
            "fahrenheit to celsius": lambda x: (x - 32) * 5/9,
            "km to miles": lambda x: x * 0.621371,
            "miles to km": lambda x: x * 1.60934,
            "kg to lbs": lambda x: x * 2.20462,
            "lbs to kg": lambda x: x / 2.20462,
        }
        for pattern, fn in conversions.items():
            if pattern in q_lower:
                nums = re.findall(r'\d+\.?\d*', q)
                if nums:
                    val = float(nums[0])
                    converted = fn(val)
                    return {
                        "handled": True,
                        "result": f"[Procedural Unit Conversion] {val} {pattern.split()[0]} = {converted:.2f} {pattern.split()[-1]}",
                        "domain": "CONVERSION"
                    }

        return {
            "handled": False,
            "result": "[Procedural] No exact domain match.",
            "domain": "UNKNOWN"
        }

if __name__ == "__main__":
    classifier = ContractClassifier()
    proc = ProceduralEngine()
    
    test_queries = [
        "2 + 2 * 10",
        "What is the current time?",
        "Convert 100 celsius to fahrenheit",
        "What is the capital of France?",
        "Prove Godel's incompleteness theorem mathematically"
    ]
    for tq in test_queries:
        contract, conf = classifier.classify(tq)
        print(f"Query: '{tq}' -> Contract: {contract} (Confidence: {conf:.2f})")
        if contract == "procedural":
            print(f"  -> {proc.execute(tq)['result']}")

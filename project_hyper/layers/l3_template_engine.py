import re
from typing import Optional

class TemplateEngine:
    """
    Layer 3: Template Engine
    Regex + rule-based responses with slot filling.
    """
    def __init__(self):
        self.templates = [
            {
                "pattern": r"what is the weather in (.*)\??",
                "response": "I cannot check live weather yet, but I can look up climate data for {0}."
            },
            {
                "pattern": r"hello|hi|hey",
                "response": "Hello! I am PROJECT HYPER, your ZERO-GPU AI system. How can I assist you?"
            }
        ]

    def match(self, query: str) -> Optional[str]:
        query = query.lower().strip()
        for t in self.templates:
            match = re.search(t["pattern"], query)
            if match:
                groups = match.groups()
                return t["response"].format(*groups) if groups else t["response"]
        return None

if __name__ == "__main__":
    te = TemplateEngine()
    print(te.match("Hi"))
    print(te.match("What is the weather in London?"))

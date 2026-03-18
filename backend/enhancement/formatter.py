"""
Formatter Module
Cleans up spacing, punctuation, and structural inconsistencies
so reconstructed answers look professionally generated.
"""
import re

class Formatter:
    def format(self, text: str) -> str:
        if not text:
            return ""

        # 1. Normalize spaces
        text = re.sub(r" +", " ", text)
        
        # 2. Fix punctuation spacing
        text = re.sub(r"\s+([.!,?;:])", r"\1", text)
        text = re.sub(r"([.!,?;:])(?=[A-Za-z])", r"\1 ", text)

        # 3. Ensure sentence casing (basic)
        sentences = re.split(r"(?<=[.!?]) +", text)
        capitalized = []
        for s in sentences:
            if s and len(s) > 0:
                capitalized.append(s[0].upper() + s[1:])
            elif s:
                capitalized.append(s)
        text = " ".join(capitalized)

        # 4. Standardize bullet points
        text = text.replace(" * ", "\n• ")
        text = text.replace(" - ", "\n• ")

        # 5. Clean up excessive newlines
        text = re.sub(r"\n{3,}", "\n\n", text)

        return text.strip()

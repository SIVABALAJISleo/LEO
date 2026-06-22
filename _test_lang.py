import sys
sys.path.insert(0, 'backend')
from layers.l15_multilingual import MultilingualSystemLayer

m = MultilingualSystemLayer()

cases = [
    ("Tamil",     "\u0ba4\u0bae\u0bbf\u0bb4\u0bcd", "ta"),
    ("Telugu",    "\u0c24\u0c46\u0c32\u0c41\u0c17\u0c41", "te"),
    ("Kannada",   "\u0cb9\u0cb2\u0ccb \u0ca8\u0cc0\u0cb5\u0cc1 \u0cb9\u0cc7\u0c97\u0cbf\u0ca6\u0ccd\u0ca6\u0cc0\u0cb0\u0cbf", "kn"),
    ("Malayalam", "\u0d39\u0d32\u0d4b", "ml"),
    ("Hindi",     "\u0928\u092e\u0938\u094d\u0924\u0947", "hi"),
    ("Arabic",    "\u0645\u0631\u062d\u0628\u0627", "ar"),
    ("Chinese",   "\u4f60\u597d", "zh"),
    ("English",   "Hello", "en"),
]

failures = []
for name, text, expected in cases:
    got = m.detect_language(text)
    status = "OK" if got == expected else "FAIL"
    print(f"[{status}] {name}: expected={expected!r}, got={got!r}")
    if got != expected:
        failures.append(name)

print()
if failures:
    print(f"FAILURES: {failures}")
    sys.exit(1)
else:
    print("ALL PASS")

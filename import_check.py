import traceback
import sys

print("Starting import test...")
try:
    from backend.routers import jepa
    print("jepa module imported successfully.")
except Exception as e:
    print(f"FAILED IMPORT: {e}")
    traceback.print_exc()
    sys.exit(1)

# tests/conftest.py
# Ensure tests can import the package from the repo's `src/` layout
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))


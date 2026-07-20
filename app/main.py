"""Streamlit application entry point."""

import sys
from pathlib import Path

# Ensure the project root is importable when Streamlit runs this file directly
# (e.g. `streamlit run app/main.py`), since it is not part of the `src` package.
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from src.presentation.app import render_app  # noqa: E402

if __name__ == "__main__":
    render_app()

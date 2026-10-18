"""Application Entry Point.

Executes the upgraded AI-Powered Outfit Recommendation Application.
Can be launched directly via: streamlit run main.py or streamlit run app.py
"""

import runpy
import os
import sys

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Execute app.py
if __name__ == "__main__" or "streamlit" in sys.modules:
    app_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app.py")
    runpy.run_path(app_path, run_name="__main__")

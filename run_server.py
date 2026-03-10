#!/usr/bin/env python3
"""
Simple script to run the ASK-Net API server for development.
"""

import uvicorn
import sys
import os

# Add ASKNet to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "ASKNet"))

if __name__ == "__main__":
    uvicorn.run(
        "api.main:app", host="0.0.0.0", port=8000, reload=True, log_level="info"
    )

#!/usr/bin/env python3
"""
Lightweight startup script for Raspberry Pi Zero deployment.
This script is optimized for resource-constrained environments.
"""

import os
import sys

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app

# Create the application with optimized settings for Pi Zero
app = create_app(
    {
        "SQLALCHEMY_ENGINE_OPTIONS": {
            "pool_pre_ping": True,
            "pool_recycle": 300,
            "pool_size": 2,  # Reduced pool size for Pi Zero
            "max_overflow": 0,
        }
    }
)

if __name__ == "__main__":
    # Run with optimized settings for Pi Zero
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=False,  # Always False in production
        threaded=False,  # Disable threading for Pi Zero
        processes=1,  # Use single process
    )

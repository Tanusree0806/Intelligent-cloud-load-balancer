# server/app.py
# This file is required for multi-mode deployment (OpenEnv spec)
# It re-exports the FastAPI app from the root server.py

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server import app

__all__ = ["app"]

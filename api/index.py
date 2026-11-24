"""Vercel Serverless Function entry point.

Directly imports the existing FastAPI application from backend.app.main without code duplication.
Ensures paths and models are seamlessly resolved in the serverless environment.
"""
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)

# Add root and backend to python path
sys.path.insert(0, root_dir)
sys.path.insert(0, os.path.join(root_dir, "backend"))

# Set VERCEL env var if not already present
os.environ.setdefault("VERCEL", "1")

from backend.app.main import app

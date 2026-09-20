"""
Vercel Serverless Function Entrypoint for Flask Application
"""
import sys
import os

# Add project root directory to sys.path so app and planner_engine can be imported
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app import app

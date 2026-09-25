"""
Vercel Serverless entry point for Snack Attack Flask Application.
"""
import os
import sys

# Ensure root directory is in sys.path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from app import app

# Vercel looks for 'app'
if __name__ == "__main__":
    app.run()

import sys
import os

# Append the root and backend directory to the path so Vercel can find the modules
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(os.path.join(os.path.dirname(__file__), "../backend"))

from backend.main import app

# This entry point is required for Vercel Python runtime
def handler(request):
    return app(request)

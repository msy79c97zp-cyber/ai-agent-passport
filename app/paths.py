"""
Filesystem paths used across the application.

Using absolute paths based on this file's location ensures templates and
other assets load correctly on Render, regardless of the process cwd.
"""

from pathlib import Path

# Directory containing this module (the `app/` package root).
APP_DIR = Path(__file__).resolve().parent

# HTML templates for the public storefront.
TEMPLATES_DIR = APP_DIR / "templates"

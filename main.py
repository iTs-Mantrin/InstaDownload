#!/usr/bin/env python3
"""
InstaDownload — Instagram & YouTube Downloader
================================================
A modern desktop application to download:
  • YouTube videos and audio (MP3)
  • Instagram posts, reels, and stories

Usage:
    python main.py
"""

import sys
import os

# Ensure the project root is on sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.gui import run

if __name__ == "__main__":
    run()

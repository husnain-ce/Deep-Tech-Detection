#!/usr/bin/env python3
"""
Ultimate Web Technology Detection System - Main Entry Point
===========================================================

This is the main entry point for the Ultimate Web Technology Detection System.
It provides a clean interface to all the detection capabilities.
"""

import sys
import asyncio
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.core.tech_detector import main as tech_detector_main

if __name__ == "__main__":
    asyncio.run(tech_detector_main())

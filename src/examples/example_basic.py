#!/usr/bin/env python3
"""
Basic Usage Example
==================
"""

import asyncio
import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.tech_detector import UltimateTechDetector

async def main():
    # Initialize detector
    detector = UltimateTechDetector()
    
    # Analyze a single URL
    result = await detector.analyze_url("https://example.com", {
        'use_whatweb': True,
        'use_wappalyzer': True,
        'min_confidence': 20
    })
    
    print(f"Detected {len(result.technologies)} technologies")
    for tech in result.technologies:
        print(f"- {tech.name} ({tech.confidence}%)")

if __name__ == "__main__":
    asyncio.run(main())

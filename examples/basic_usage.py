#!/usr/bin/env python3
"""
Basic Usage Example
Simple technology detection for a single URL
"""

import asyncio
from src.core.tech_detector import main as tech_detector_main

async def basic_detection():
    """Basic technology detection example"""
    url = "https://example.com"
    
    # Run detection with basic options
    result = await tech_detector_main([
        url,
        "--use-dataset",
        "--use-whatweb", 
        "--use-wappalyzer",
        "--output", "json",
        "--verbose"
    ])
    
    print(f"Detected {len(result.technologies)} technologies")
    for tech in result.technologies:
        print(f"- {tech.name} ({tech.category}) - {tech.confidence}%")

if __name__ == "__main__":
    asyncio.run(basic_detection())

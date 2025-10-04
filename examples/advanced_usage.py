#!/usr/bin/env python3
"""
Advanced Usage Example
Comprehensive technology detection with custom options
"""

import asyncio
from src.core.tech_detector import main as tech_detector_main

async def advanced_detection():
    """Advanced technology detection example"""
    urls = [
        "https://github.com",
        "https://stackoverflow.com", 
        "https://example.com"
    ]
    
    for url in urls:
        print(f"\nAnalyzing {url}...")
        
        # Run detection with advanced options
        result = await tech_detector_main([
            url,
            "--use-dataset",
            "--use-whatweb",
            "--use-wappalyzer", 
            "--user-agents", "5",
            "--preferred-browser", "chrome",
            "--min-confidence", "20",
            "--max-results", "100",
            "--timeout", "30",
            "--follow-redirects",
            "--output", "csv",
            "--save-report", f"report_{url.replace('https://', '').replace('/', '_')}.csv",
            "--verbose",
            "--whatweb-aggression", "1"
        ])
        
        print(f"Detected {len(result.technologies)} technologies")
        
        # Group by category
        by_category = {}
        for tech in result.technologies:
            category = tech.category
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(tech)
        
        for category, techs in by_category.items():
            print(f"  {category}: {len(techs)} technologies")

if __name__ == "__main__":
    asyncio.run(advanced_detection())

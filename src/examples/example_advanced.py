#!/usr/bin/env python3
"""
Advanced Usage Example
=====================
"""

import asyncio
import json
import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.tech_detector import UltimateTechDetector

async def main():
    # Initialize detector
    detector = UltimateTechDetector()
    
    # URLs to analyze
    urls = [
        "https://example.com",
        "https://github.com",
        "https://stackoverflow.com"
    ]
    
    # Advanced options
    options = {
        'use_whatweb': True,
        'use_wappalyzer': True,
        'min_confidence': 30,
        'max_results': 50,
        'preferred_browser': 'chrome',
        'user_agents': 5,
        'timeout': 60
    }
    
    # Analyze URLs
    results = await detector.analyze_batch(urls, options)
    
    # Process results
    for result in results:
        print(f"\nURL: {result.url}")
        print(f"Technologies: {len(result.technologies)}")
        print(f"Analysis Time: {result.analysis_time:.2f}s")
        print(f"User Agent: {result.successful_agent[:50] if result.successful_agent else 'N/A'}...")
        
        # Save detailed report
        report_file = f"report_{result.url.replace('https://', '').replace('/', '_')}.json"
        with open(report_file, 'w') as f:
            json.dump(result.__dict__, f, indent=2, default=str)
        print(f"Report saved: {report_file}")

if __name__ == "__main__":
    asyncio.run(main())

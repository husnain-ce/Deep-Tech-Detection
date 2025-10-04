#!/usr/bin/env python3
"""
Simple launcher for Ultimate Tech Detection System
Usage: python detect.py https://example.com
"""

import sys
import asyncio
from ultimate_tech_detector import UltimateTechDetector

async def main():
    if len(sys.argv) < 2:
        print("Usage: python detect.py <URL> [options]")
        print("Example: python detect.py https://example.com --verbose --max-results 500")
        sys.exit(1)
    
    url = sys.argv[1]
    options = {}
    
    # Parse simple options
    if '--verbose' in sys.argv:
        options['verbose'] = True
    
    if '--max-results' in sys.argv:
        try:
            idx = sys.argv.index('--max-results')
            options['max_results'] = int(sys.argv[idx + 1])
        except (ValueError, IndexError):
            options['max_results'] = 200
    else:
        options['max_results'] = 200
    
    if '--min-confidence' in sys.argv:
        try:
            idx = sys.argv.index('--min-confidence')
            options['min_confidence'] = int(sys.argv[idx + 1])
        except (ValueError, IndexError):
            options['min_confidence'] = 0
    else:
        options['min_confidence'] = 0
    
    # Initialize detector
    detector = UltimateTechDetector()
    
    # Run analysis
    result = await detector.analyze_url(url, options)
    
    # Print results
    print(f"\n🎯 Ultimate Tech Detection Results")
    print(f"URL: {result.url}")
    print(f"Final URL: {result.final_url}")
    print(f"Analysis Time: {result.analysis_time:.2f}s")
    print(f"Technologies Detected: {len(result.technologies)}")
    print(f"Categories: {result.metadata.get('categories_detected', 0)}")
    print(f"Dataset Utilization: {result.metadata.get('dataset_utilization', 'Unknown')}")
    
    if result.errors:
        print(f"\n❌ Errors: {', '.join(result.errors)}")
    
    print(f"\n📊 Confidence Distribution:")
    dist = result.metadata.get('confidence_distribution', {})
    for level, count in dist.items():
        print(f"  {level}: {count} technologies")
    
    print(f"\n🔍 Top Technologies:")
    # Sort by confidence and show top 10
    sorted_techs = sorted(result.technologies, key=lambda x: x.confidence, reverse=True)[:10]
    for i, tech in enumerate(sorted_techs, 1):
        print(f"  {i:2d}. {tech.name} ({tech.category}) - {tech.confidence}% confidence")
    
    if len(result.technologies) > 10:
        print(f"  ... and {len(result.technologies) - 10} more technologies")
    
    print(f"\n✅ Analysis Complete!")

if __name__ == "__main__":
    asyncio.run(main())

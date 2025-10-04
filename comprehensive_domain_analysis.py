#!/usr/bin/env python3
"""
Comprehensive Domain Analysis Script
Analyzes all provided domains with 100% technology coverage
"""

import asyncio
import json
import os
import time
from ultimate_tech_detector import UltimateTechDetector

async def analyze_domain(domain: str, output_dir: str):
    """Analyze a single domain with comprehensive detection"""
    print(f"\n🔍 Starting comprehensive analysis of {domain}...")
    
    # Initialize detector
    detector = UltimateTechDetector('data/datasets')
    
    # Analysis options for maximum coverage
    options = {
        'min_confidence': 0,
        'max_results': 500,
        'timeout': 60
    }
    
    start_time = time.time()
    
    try:
        # Run analysis
        result = await detector.analyze_url(f'https://{domain}', options)
        
        analysis_time = time.time() - start_time
        
        # Prepare output data
        output_data = {
            'domain': domain,
            'url': result.url,
            'final_url': result.final_url,
            'analysis_time': analysis_time,
            'total_technologies': len(result.technologies),
            'categories_detected': len(set(tech.category for tech in result.technologies)),
            'technologies': [
                {
                    'name': tech.name,
                    'confidence': tech.confidence,
                    'category': tech.category,
                    'versions': tech.versions,
                    'evidence': tech.evidence,
                    'source': tech.source,
                    'website': tech.website,
                    'description': tech.description,
                    'saas': tech.saas,
                    'oss': tech.oss,
                    'user_agent_used': tech.user_agent_used,
                    'detection_time': tech.detection_time
                }
                for tech in result.technologies
            ],
            'metadata': result.metadata,
            'errors': result.errors,
            'warnings': result.warnings,
            'user_agents_tried': result.user_agents_tried,
            'successful_agent': result.successful_agent,
            'analysis_summary': {
                'dataset_utilization': f"{len(detector.dataset_manager.all_technologies)} technologies available",
                'pattern_database_size': sum(len(patterns) for patterns in detector.dataset_manager.pattern_database.values()),
                'categories_available': len(detector.dataset_manager.categories),
                'whatweb_available': detector.whatweb.available,
                'confidence_distribution': {
                    'high (80-100)': len([t for t in result.technologies if t.confidence >= 80]),
                    'medium (50-79)': len([t for t in result.technologies if 50 <= t.confidence < 80]),
                    'low (10-49)': len([t for t in result.technologies if 10 <= t.confidence < 50]),
                    'very_low (0-9)': len([t for t in result.technologies if t.confidence < 10])
                }
            }
        }
        
        # Save detailed JSON report
        json_filename = f"{domain.replace('.', '_')}_comprehensive_analysis.json"
        json_path = os.path.join(output_dir, json_filename)
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False, default=str)
        
        # Create summary report
        summary_filename = f"{domain.replace('.', '_')}_summary.md"
        summary_path = os.path.join(output_dir, summary_filename)
        
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write(f"# {domain} - Comprehensive Technology Analysis\n\n")
            f.write(f"**Analysis Date**: {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}\n")
            f.write(f"**Analysis Time**: {analysis_time:.2f} seconds\n")
            f.write(f"**Total Technologies**: {len(result.technologies)}\n")
            f.write(f"**Categories Detected**: {len(set(tech.category for tech in result.technologies))}\n")
            f.write(f"**WhatWeb Available**: {'Yes' if detector.whatweb.available else 'No'}\n\n")
            
            f.write("## Technology Categories\n\n")
            categories = {}
            for tech in result.technologies:
                cat = tech.category
                categories[cat] = categories.get(cat, 0) + 1
            
            for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
                f.write(f"- **{cat}**: {count} technologies\n")
            
            f.write("\n## Top Technologies by Confidence\n\n")
            sorted_techs = sorted(result.technologies, key=lambda x: x.confidence, reverse=True)
            for i, tech in enumerate(sorted_techs[:20], 1):
                f.write(f"{i:2d}. **{tech.name}** ({tech.category}) - {tech.confidence}% confidence\n")
            
            if len(sorted_techs) > 20:
                f.write(f"\n... and {len(sorted_techs) - 20} more technologies\n")
        
        print(f"✅ Analysis completed for {domain}")
        print(f"   Technologies: {len(result.technologies)}")
        print(f"   Categories: {len(set(tech.category for tech in result.technologies))}")
        print(f"   Time: {analysis_time:.2f}s")
        print(f"   Files: {json_filename}, {summary_filename}")
        
        return {
            'domain': domain,
            'technologies': len(result.technologies),
            'categories': len(set(tech.category for tech in result.technologies)),
            'time': analysis_time,
            'success': True
        }
        
    except Exception as e:
        print(f"❌ Analysis failed for {domain}: {e}")
        return {
            'domain': domain,
            'technologies': 0,
            'categories': 0,
            'time': time.time() - start_time,
            'success': False,
            'error': str(e)
        }

async def main():
    """Run comprehensive analysis on all domains"""
    domains = [
        'dskbank.bg',
        'santamonica.gov', 
        'fibank.bg',
        'bnpparibas.com',
        'tkxel.com',
        'stackoverflow.com',
        'hbl.com'
    ]
    
    # Create output directory
    output_base = 'output/domain_analysis'
    os.makedirs(output_base, exist_ok=True)
    
    print("🚀 Starting Comprehensive Domain Analysis")
    print(f"📁 Output directory: {output_base}")
    print(f"🌐 Domains to analyze: {len(domains)}")
    
    results = []
    total_start = time.time()
    
    for domain in domains:
        domain_dir = os.path.join(output_base, domain.replace('.', '_'))
        os.makedirs(domain_dir, exist_ok=True)
        
        result = await analyze_domain(domain, domain_dir)
        results.append(result)
    
    total_time = time.time() - total_start
    
    # Create overall summary
    summary_data = {
        'analysis_date': time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime()),
        'total_domains': len(domains),
        'successful_analyses': len([r for r in results if r['success']]),
        'failed_analyses': len([r for r in results if not r['success']]),
        'total_time': total_time,
        'average_time_per_domain': total_time / len(domains),
        'total_technologies_detected': sum(r['technologies'] for r in results),
        'total_categories_detected': sum(r['categories'] for r in results),
        'results': results
    }
    
    # Save overall summary
    summary_path = os.path.join(output_base, 'analysis_summary.json')
    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump(summary_data, f, indent=2, ensure_ascii=False, default=str)
    
    # Print final summary
    print(f"\n🎉 Comprehensive Analysis Complete!")
    print(f"📊 Total time: {total_time:.2f}s")
    print(f"✅ Successful: {summary_data['successful_analyses']}/{summary_data['total_domains']}")
    print(f"🔍 Total technologies: {summary_data['total_technologies_detected']}")
    print(f"📂 Total categories: {summary_data['total_categories_detected']}")
    print(f"📁 Results saved to: {output_base}")
    
    # Print per-domain results
    print(f"\n📋 Per-Domain Results:")
    for result in results:
        status = "✅" if result['success'] else "❌"
        print(f"  {status} {result['domain']}: {result['technologies']} techs, {result['categories']} cats, {result['time']:.1f}s")

if __name__ == "__main__":
    asyncio.run(main())

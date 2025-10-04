#!/usr/bin/env python3
"""
Advanced Web Technology Matcher
==============================

Enterprise-grade web technology detection system that combines multiple detection
engines and datasets for maximum accuracy and coverage.

This is the main entry point that integrates:
- Custom dataset detection
- WhatWeb integration
- Wappalyzer integration
- Advanced pattern matching
- Parallel processing
- Multiple output formats
"""

import argparse
import asyncio
import json
import logging
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

# Import our modules
from advanced_tech_detector import AdvancedTechDetector, OutputFormatter
from integrations.whatweb_integration import WhatWebIntegration, merge_whatweb_results
from integrations.wappalyzer_integration import WappalyzerIntegration, merge_wappalyzer_results

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('webtech_matcher.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class WebTechMatcherAdvanced:
    """Advanced web technology matcher with multi-engine support"""
    
    def __init__(self, datasets_dir: str = "json_datasets"):
        self.datasets_dir = datasets_dir
        self.detector = AdvancedTechDetector(datasets_dir)
        self.whatweb = None
        self.wappalyzer = None
        self._initialize_engines()
    
    def _initialize_engines(self):
        """Initialize detection engines"""
        # Initialize WhatWeb
        try:
            self.whatweb = WhatWebIntegration()
            logger.info("WhatWeb integration initialized")
        except Exception as e:
            logger.warning(f"WhatWeb integration failed: {e}")
        
        # Initialize Wappalyzer
        try:
            wappalyzer_data_path = Path(self.datasets_dir) / "wappalyzer_technologies_clean.json"
            self.wappalyzer = WappalyzerIntegration(
                wappalyzer_data_path=str(wappalyzer_data_path) if wappalyzer_data_path.exists() else None
            )
            logger.info("Wappalyzer integration initialized")
        except Exception as e:
            logger.warning(f"Wappalyzer integration failed: {e}")
    
    async def analyze_url(self, url: str, options: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Analyze URL with all available engines
        
        Args:
            url: URL to analyze
            options: Analysis options
            
        Returns:
            Complete analysis result
        """
        options = options or {}
        start_time = time.time()
        
        logger.info(f"Starting analysis of {url}")
        
        # Get base analysis from dataset
        base_result = await self.detector.analyze_url(url, options)
        
        if not base_result.technologies:
            logger.warning(f"No technologies detected from dataset for {url}")
        
        # Merge WhatWeb results if enabled
        if options.get('use_whatweb', False) and self.whatweb:
            logger.info("Running WhatWeb analysis...")
            whatweb_result, whatweb_error = self.whatweb.analyze_url(url, options)
            
            if whatweb_error:
                logger.error(f"WhatWeb analysis failed: {whatweb_error}")
                base_result.errors.append(f"WhatWeb error: {whatweb_error}")
            elif whatweb_result:
                whatweb_technologies = self.whatweb.extract_technologies(whatweb_result)
                base_result.technologies = merge_whatweb_results(base_result.technologies, whatweb_technologies)
                base_result.metadata['whatweb'] = whatweb_result
                logger.info(f"WhatWeb detected {len(whatweb_technologies)} additional technologies")
        
        # Merge Wappalyzer results if enabled
        if options.get('use_wappalyzer', False) and self.wappalyzer:
            logger.info("Running Wappalyzer analysis...")
            wappalyzer_result, wappalyzer_error = self.wappalyzer.analyze_url(url, options)
            
            if wappalyzer_error:
                logger.error(f"Wappalyzer analysis failed: {wappalyzer_error}")
                base_result.errors.append(f"Wappalyzer error: {wappalyzer_error}")
            elif wappalyzer_result:
                wappalyzer_technologies = self.wappalyzer.extract_technologies(wappalyzer_result)
                base_result.technologies = merge_wappalyzer_results(base_result.technologies, wappalyzer_technologies)
                base_result.metadata['wappalyzer'] = wappalyzer_result
                logger.info(f"Wappalyzer detected {len(wappalyzer_technologies)} additional technologies")
        
        # Post-process results
        base_result = self._post_process_analysis(base_result, options)
        
        total_time = time.time() - start_time
        base_result.analysis_time = total_time
        
        logger.info(f"Analysis completed in {total_time:.2f}s - {len(base_result.technologies)} technologies detected")
        
        return base_result
    
    def _post_process_analysis(self, result, options: Dict[str, Any]) -> Any:
        """Post-process analysis results"""
        # Apply confidence threshold
        min_confidence = options.get('min_confidence', 10)
        result.technologies = [
            tech for tech in result.technologies 
            if tech.confidence >= min_confidence
        ]
        
        # Sort by confidence
        result.technologies.sort(key=lambda x: x.confidence, reverse=True)
        
        # Limit results
        max_results = options.get('max_results', 100)
        if len(result.technologies) > max_results:
            result.technologies = result.technologies[:max_results]
        
        # Add summary statistics
        result.metadata['summary'] = {
            'total_technologies': len(result.technologies),
            'by_source': self._count_by_source(result.technologies),
            'by_category': self._count_by_category(result.technologies),
            'confidence_distribution': self._get_confidence_distribution(result.technologies)
        }
        
        return result
    
    def _count_by_source(self, technologies: List[Any]) -> Dict[str, int]:
        """Count technologies by source"""
        counts = {}
        for tech in technologies:
            source = tech.source
            counts[source] = counts.get(source, 0) + 1
        return counts
    
    def _count_by_category(self, technologies: List[Any]) -> Dict[str, int]:
        """Count technologies by category"""
        counts = {}
        for tech in technologies:
            category = tech.category
            counts[category] = counts.get(category, 0) + 1
        return counts
    
    def _get_confidence_distribution(self, technologies: List[Any]) -> Dict[str, int]:
        """Get confidence score distribution"""
        distribution = {
            'high (80-100)': 0,
            'medium (50-79)': 0,
            'low (10-49)': 0
        }
        
        for tech in technologies:
            conf = tech.confidence
            if conf >= 80:
                distribution['high (80-100)'] += 1
            elif conf >= 50:
                distribution['medium (50-79)'] += 1
            else:
                distribution['low (10-49)'] += 1
        
        return distribution
    
    async def analyze_batch(self, urls: List[str], options: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Analyze multiple URLs in batch"""
        options = options or {}
        results = []
        
        logger.info(f"Starting batch analysis of {len(urls)} URLs")
        
        # Use asyncio for concurrent processing
        tasks = [self.analyze_url(url, options) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Error analyzing {urls[i]}: {result}")
                processed_results.append({
                    'url': urls[i],
                    'error': str(result),
                    'technologies': [],
                    'analysis_time': 0
                })
            else:
                processed_results.append(result)
        
        logger.info(f"Batch analysis completed - {len(processed_results)} results")
        return processed_results

def create_advanced_parser() -> argparse.ArgumentParser:
    """Create advanced argument parser"""
    parser = argparse.ArgumentParser(
        description="Advanced Web Technology Detection System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic analysis
  %(prog)s https://example.com
  
  # Full analysis with all engines
  %(prog)s https://example.com --use-whatweb --use-wappalyzer --output json
  
  # High confidence analysis
  %(prog)s https://example.com --min-confidence 50 --max-results 20
  
  # Batch analysis
  %(prog)s --batch urls.txt --output csv --workers 10
  
  # Custom output
  %(prog)s https://example.com --output html --save-report report.html
  
  # Debug mode
  %(prog)s https://example.com --verbose --debug --dump
        """
    )
    
    # URL arguments
    url_group = parser.add_mutually_exclusive_group(required=True)
    url_group.add_argument('url', nargs='?', help='URL to analyze')
    url_group.add_argument('--batch', help='File containing URLs to analyze (one per line)')
    
    # Detection engines
    engine_group = parser.add_argument_group('Detection Engines')
    engine_group.add_argument('--use-dataset', action='store_true', default=True, 
                            help='Use custom dataset detection (default: enabled)')
    engine_group.add_argument('--use-whatweb', action='store_true', 
                            help='Use WhatWeb detection')
    engine_group.add_argument('--use-wappalyzer', action='store_true', 
                            help='Use Wappalyzer detection')
    engine_group.add_argument('--whatweb-path', default='whatweb', 
                            help='Path to WhatWeb executable')
    engine_group.add_argument('--whatweb-aggression', type=int, choices=range(5), 
                            help='WhatWeb aggression level (0-4)')
    
    # Analysis options
    analysis_group = parser.add_argument_group('Analysis Options')
    analysis_group.add_argument('--min-confidence', type=int, default=10, 
                              help='Minimum confidence threshold (default: 10)')
    analysis_group.add_argument('--max-results', type=int, default=100, 
                              help='Maximum number of results (default: 100)')
    analysis_group.add_argument('--timeout', type=int, default=30, 
                              help='Request timeout in seconds (default: 30)')
    analysis_group.add_argument('--user-agent', 
                              default='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
                              help='User agent string')
    analysis_group.add_argument('--follow-redirects', action='store_true', default=True,
                              help='Follow redirects (default: enabled)')
    
    # Output options
    output_group = parser.add_argument_group('Output Options')
    output_group.add_argument('--output', choices=['json', 'xml', 'csv', 'html', 'text'], 
                            default='json', help='Output format (default: json)')
    output_group.add_argument('--save-report', help='Save report to file')
    output_group.add_argument('--pretty', action='store_true', 
                            help='Pretty print output')
    
    # Batch processing
    batch_group = parser.add_argument_group('Batch Processing')
    batch_group.add_argument('--workers', type=int, default=5, 
                           help='Number of parallel workers for batch processing (default: 5)')
    batch_group.add_argument('--delay', type=float, default=0.1, 
                           help='Delay between requests in seconds (default: 0.1)')
    
    # Debug options
    debug_group = parser.add_argument_group('Debug Options')
    debug_group.add_argument('--verbose', '-v', action='store_true', 
                           help='Verbose output')
    debug_group.add_argument('--debug', action='store_true', 
                           help='Debug mode')
    debug_group.add_argument('--dump', action='store_true', 
                           help='Dump raw data for debugging')
    debug_group.add_argument('--log-file', help='Log file path')
    
    # Advanced options
    advanced_group = parser.add_argument_group('Advanced Options')
    advanced_group.add_argument('--datasets-dir', default='json_datasets', 
                              help='Directory containing datasets (default: json_datasets)')
    advanced_group.add_argument('--cache', action='store_true', 
                              help='Enable caching')
    advanced_group.add_argument('--cache-ttl', type=int, default=3600, 
                              help='Cache TTL in seconds (default: 3600)')
    
    return parser

async def main():
    """Main function"""
    parser = create_advanced_parser()
    args = parser.parse_args()
    
    # Configure logging
    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.getLogger().setLevel(log_level)
    
    if args.log_file:
        file_handler = logging.FileHandler(args.log_file)
        file_handler.setLevel(log_level)
        logging.getLogger().addHandler(file_handler)
    
    # Initialize matcher
    matcher = WebTechMatcherAdvanced(args.datasets_dir)
    
    # Prepare options
    options = {
        'min_confidence': args.min_confidence,
        'max_results': args.max_results,
        'timeout': args.timeout,
        'user_agent': args.user_agent,
        'use_dataset': args.use_dataset,
        'use_whatweb': args.use_whatweb,
        'use_wappalyzer': args.use_wappalyzer,
        'follow_redirects': args.follow_redirects,
        'dump': args.dump
    }
    
    # Add WhatWeb specific options
    if args.use_whatweb:
        options['whatweb_path'] = args.whatweb_path
        if args.whatweb_aggression is not None:
            options['aggression'] = args.whatweb_aggression
    
    try:
        if args.batch:
            # Batch processing
            with open(args.batch, 'r') as f:
                urls = [line.strip() for line in f if line.strip()]
            
            logger.info(f"Processing {len(urls)} URLs...")
            results = await matcher.analyze_batch(urls, options)
            
            # Output results
            if args.output == 'json':
                output = json.dumps([result.__dict__ for result in results], indent=2 if args.pretty else None)
            else:
                # For other formats, process each result
                output = ""
                for result in results:
                    if args.output == 'xml':
                        output += OutputFormatter.to_xml(result) + "\n"
                    elif args.output == 'csv':
                        output += OutputFormatter.to_csv(result) + "\n"
                    elif args.output == 'html':
                        output += OutputFormatter.to_html(result) + "\n"
                    else:  # text
                        output += f"URL: {result.url}\n"
                        output += f"Technologies: {len(result.technologies)}\n"
                        for tech in result.technologies:
                            output += f"  - {tech.name} ({tech.confidence}%)\n"
                        output += "\n"
            
            print(output)
            
        else:
            # Single URL processing
            result = await matcher.analyze_url(args.url, options)
            
            # Format output
            if args.output == 'json':
                output = OutputFormatter.to_json(result)
            elif args.output == 'xml':
                output = OutputFormatter.to_xml(result)
            elif args.output == 'csv':
                output = OutputFormatter.to_csv(result)
            elif args.output == 'html':
                output = OutputFormatter.to_html(result)
            else:  # text
                output = f"URL: {result.url}\n"
                output += f"Final URL: {result.final_url}\n"
                output += f"Analysis Time: {result.analysis_time:.2f}s\n"
                output += f"Technologies Detected: {len(result.technologies)}\n\n"
                
                if result.technologies:
                    for tech in result.technologies:
                        output += f"{tech.name} ({tech.confidence}%) - {tech.category}\n"
                        if tech.versions:
                            output += f"  Versions: {', '.join(tech.versions)}\n"
                        if tech.evidence:
                            output += f"  Evidence: {tech.evidence[0].get('match', '')[:100]}...\n"
                        output += "\n"
                else:
                    output += "No technologies detected.\n"
            
            print(output)
            
            # Save report if requested
            if args.save_report:
                with open(args.save_report, 'w', encoding='utf-8') as f:
                    f.write(output)
                logger.info(f"Report saved to {args.save_report}")
    
    except KeyboardInterrupt:
        logger.info("Analysis interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())

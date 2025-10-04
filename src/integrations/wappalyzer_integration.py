#!/usr/bin/env python3
"""
Wappalyzer Integration Module
============================

Advanced integration with Wappalyzer for comprehensive technology detection.
Handles both python-Wappalyzer library and direct JSON dataset usage.
"""

import json
import logging
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

logger = logging.getLogger(__name__)

# Try to import Wappalyzer
try:
    from Wappalyzer import Wappalyzer as PyWappalyzer, WebPage as PyWebPage
    WAPPALYZER_AVAILABLE = True
except ImportError:
    WAPPALYZER_AVAILABLE = False
    logger.warning("python-Wappalyzer not available. Install with: pip install python-Wappalyzer")

class WappalyzerIntegration:
    """Advanced Wappalyzer integration with multiple detection methods"""
    
    def __init__(self, wappalyzer_data_path: Optional[str] = None, update_on_init: bool = False):
        self.wappalyzer_data_path = wappalyzer_data_path
        self.update_on_init = update_on_init
        self.wappalyzer_instance = None
        self.technologies_data = None
        self._initialize_wappalyzer()
    
    def _initialize_wappalyzer(self):
        """Initialize Wappalyzer instance"""
        if not WAPPALYZER_AVAILABLE:
            logger.error("python-Wappalyzer is not available")
            return
        
        try:
            if self.wappalyzer_data_path and Path(self.wappalyzer_data_path).exists():
                # Use custom dataset
                with open(self.wappalyzer_data_path, 'r', encoding='utf-8') as f:
                    self.technologies_data = json.load(f)
                # Extract categories and technologies from custom data
                categories = self.technologies_data.get('categories', {})
                technologies = self.technologies_data.get('technologies', {})
                self.wappalyzer_instance = PyWappalyzer(categories, technologies)
                logger.info(f"Loaded Wappalyzer from custom dataset: {self.wappalyzer_data_path}")
            else:
                # Use default Wappalyzer with latest data
                try:
                    if self.update_on_init:
                        self.wappalyzer_instance = PyWappalyzer.latest(update=True)
                        logger.info("Initialized Wappalyzer with latest data")
                    else:
                        self.wappalyzer_instance = PyWappalyzer.latest()
                        logger.info("Initialized Wappalyzer with bundled data")
                    
                    # Extract technologies data for direct access
                    if hasattr(self.wappalyzer_instance, 'technologies'):
                        self.technologies_data = self.wappalyzer_instance.technologies
                    else:
                        # Try to get from the dataset
                        self.technologies_data = self._get_technologies_from_dataset()
                        
                except Exception as e:
                    logger.warning(f"Failed to initialize with latest data: {e}")
                    # Fallback to empty technologies
                    self.technologies_data = {}
                    try:
                        self.wappalyzer_instance = PyWappalyzer({}, {})
                        logger.info("Initialized Wappalyzer with empty technologies")
                    except Exception as e2:
                        logger.error(f"Failed to initialize Wappalyzer even with empty technologies: {e2}")
                        self.wappalyzer_instance = None
        
        except Exception as e:
            logger.error(f"Failed to initialize Wappalyzer: {e}")
            self.wappalyzer_instance = None
    
    def _get_technologies_from_dataset(self) -> Optional[Dict[str, Any]]:
        """Get technologies data from Wappalyzer dataset"""
        try:
            # Try to load from our organized datasets
            datasets_dir = Path("json_datasets")
            wappalyzer_file = datasets_dir / "wappalyzer_technologies_clean.json"
            
            if wappalyzer_file.exists():
                with open(wappalyzer_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            
            # Fallback to online source
            import requests
            url = "https://raw.githubusercontent.com/wappalyzer/wappalyzer/master/src/technologies.json"
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            logger.error(f"Failed to get technologies data: {e}")
            return None
    
    def analyze_url(self, url: str, options: Dict[str, Any] = None) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Analyze URL with Wappalyzer
        
        Args:
            url: URL to analyze
            options: Analysis options
            
        Returns:
            Tuple of (results_dict, error_message)
        """
        options = options or {}
        
        if not self.wappalyzer_instance:
            return None, "Wappalyzer not initialized"
        
        try:
            start_time = time.time()
            
            # Create WebPage object
            headers = options.get('headers', {})
            if 'User-Agent' not in headers:
                headers['User-Agent'] = options.get('user_agent', 
                    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36')
            
            timeout = options.get('timeout', 30)
            
            # Create WebPage
            page = PyWebPage.new_from_url(
                url, 
                timeout=timeout
            )
            
            # Analyze with Wappalyzer
            if hasattr(self.wappalyzer_instance, 'analyze_with_versions_and_categories'):
                # Use the most comprehensive method
                results = self.wappalyzer_instance.analyze_with_versions_and_categories(page)
                analysis_method = 'versions_and_categories'
            elif hasattr(self.wappalyzer_instance, 'analyze_with_versions'):
                # Use version analysis
                versions = self.wappalyzer_instance.analyze_with_versions(page)
                results = {app: {'versions': list(versions.get(app, [])), 'categories': []} for app in versions}
                analysis_method = 'versions'
            else:
                # Use basic analysis
                apps = self.wappalyzer_instance.analyze(page)
                results = {app: {'versions': [], 'categories': []} for app in apps}
                analysis_method = 'basic'
            
            execution_time = time.time() - start_time
            
            # Format results
            formatted_results = {
                'url': url,
                'technologies': results,
                'analysis_method': analysis_method,
                'execution_time': execution_time,
                'timestamp': time.time(),
                'total_technologies': len(results)
            }
            
            return formatted_results, None
            
        except Exception as e:
            error_msg = f"Wappalyzer analysis failed: {str(e)}"
            logger.error(error_msg)
            return None, error_msg
    
    def analyze_html(self, html: str, url: str, options: Dict[str, Any] = None) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Analyze HTML content with Wappalyzer
        
        Args:
            html: HTML content to analyze
            url: Original URL
            options: Analysis options
            
        Returns:
            Tuple of (results_dict, error_message)
        """
        options = options or {}
        
        if not self.wappalyzer_instance:
            return None, "Wappalyzer not initialized"
        
        try:
            start_time = time.time()
            
            # Create WebPage from HTML
            headers = options.get('headers', {})
            if 'User-Agent' not in headers:
                headers['User-Agent'] = options.get('user_agent', 
                    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36')
            
            page = PyWebPage.new_from_html(html, url)
            
            # Analyze with Wappalyzer
            if hasattr(self.wappalyzer_instance, 'analyze_with_versions_and_categories'):
                results = self.wappalyzer_instance.analyze_with_versions_and_categories(page)
                analysis_method = 'versions_and_categories'
            elif hasattr(self.wappalyzer_instance, 'analyze_with_versions'):
                versions = self.wappalyzer_instance.analyze_with_versions(page)
                results = {app: {'versions': list(versions.get(app, [])), 'categories': []} for app in versions}
                analysis_method = 'versions'
            else:
                apps = self.wappalyzer_instance.analyze(page)
                results = {app: {'versions': [], 'categories': []} for app in apps}
                analysis_method = 'basic'
            
            execution_time = time.time() - start_time
            
            # Format results
            formatted_results = {
                'url': url,
                'technologies': results,
                'analysis_method': analysis_method,
                'execution_time': execution_time,
                'timestamp': time.time(),
                'total_technologies': len(results)
            }
            
            return formatted_results, None
            
        except Exception as e:
            error_msg = f"Wappalyzer HTML analysis failed: {str(e)}"
            logger.error(error_msg)
            return None, error_msg
    
    def extract_technologies(self, wappalyzer_result: Dict[str, Any]) -> List[Any]:
        """Extract technologies from Wappalyzer result"""
        technologies = []
        
        tech_data = wappalyzer_result.get('technologies', {})
        if not isinstance(tech_data, dict):
            return technologies
        
        for tech_name, tech_info in tech_data.items():
            if not tech_info:
                continue
            
            # Extract versions
            versions = tech_info.get('versions', [])
            if not isinstance(versions, list):
                versions = []
            
            # Extract categories
            categories = tech_info.get('categories', [])
            if not isinstance(categories, list):
                categories = []
            
            # Build evidence
            evidence = []
            if versions:
                evidence.append({
                    'field': 'wappalyzer',
                    'detail': 'version_detection',
                    'match': f"Versions: {', '.join(versions)}",
                    'confidence': 70,
                    'version': versions[0] if versions else None
                })
            
            if categories:
                evidence.append({
                    'field': 'wappalyzer',
                    'detail': 'category_detection',
                    'match': f"Categories: {', '.join(categories)}",
                    'confidence': 60,
                    'version': None
                })
            
            # Determine confidence
            confidence = 60
            if versions:
                confidence = 70
            if categories:
                confidence = max(confidence, 65)
            if len(evidence) > 1:
                confidence = 80
            
            # Get additional info from technologies data
            tech_details = self._get_technology_details(tech_name)
            
            # Create DetectionResult object
            from ..core.enhanced_tech_detector import DetectionResult
            
            detection_result = DetectionResult(
                name=tech_name,
                confidence=confidence,
                category=categories[0] if categories else tech_details.get('category', 'Unknown'),
                versions=versions,
                evidence=evidence,
                source='wappalyzer',
                website=tech_details.get('website'),
                description=tech_details.get('description'),
                saas=tech_details.get('saas'),
                oss=tech_details.get('oss')
            )
            technologies.append(detection_result)
        
        return technologies
    
    def _get_technology_details(self, tech_name: str) -> Dict[str, Any]:
        """Get additional details for a technology"""
        if not self.technologies_data:
            return {}
        
        tech_data = self.technologies_data.get('technologies', {}).get(tech_name, {})
        if not tech_data:
            return {}
        
        return {
            'category': self._get_category_name(tech_data.get('cats', [])),
            'website': tech_data.get('website'),
            'description': tech_data.get('description'),
            'saas': tech_data.get('saas'),
            'oss': tech_data.get('oss')
        }
    
    def _get_category_name(self, category_ids: List[Union[str, int]]) -> str:
        """Get category name from ID"""
        if not self.technologies_data or not category_ids:
            return 'Unknown'
        
        categories = self.technologies_data.get('categories', {})
        for cat_id in category_ids:
            cat_name = categories.get(str(cat_id))
            if cat_name:
                return cat_name
        
        return 'Unknown'
    
    def get_available_technologies(self) -> List[str]:
        """Get list of available technologies"""
        if not self.technologies_data:
            return []
        
        return list(self.technologies_data.get('technologies', {}).keys())
    
    def get_technology_info(self, tech_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a technology"""
        if not self.technologies_data:
            return None
        
        return self.technologies_data.get('technologies', {}).get(tech_name)
    
    def search_technologies(self, query: str, limit: int = 50) -> List[str]:
        """Search for technologies by name or description"""
        if not self.technologies_data:
            return []
        
        query_lower = query.lower()
        results = []
        
        technologies = self.technologies_data.get('technologies', {})
        for tech_name, tech_data in technologies.items():
            if len(results) >= limit:
                break
            
            if (query_lower in tech_name.lower() or 
                query_lower in tech_data.get('description', '').lower()):
                results.append(tech_name)
        
        return results
    
    def get_categories(self) -> Dict[str, str]:
        """Get all available categories"""
        if not self.technologies_data:
            return {}
        
        return self.technologies_data.get('categories', {})
    
    def update_technologies(self) -> bool:
        """Update technologies data from online source"""
        try:
            import requests
            
            url = "https://raw.githubusercontent.com/wappalyzer/wappalyzer/master/src/technologies.json"
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            self.technologies_data = response.json()
            
            # Reinitialize Wappalyzer with new data
            if self.technologies_data:
                self.wappalyzer_instance = PyWappalyzer(self.technologies_data)
                logger.info("Successfully updated Wappalyzer technologies")
                return True
            else:
                logger.error("Failed to update technologies: empty response")
                return False
                
        except Exception as e:
            logger.error(f"Failed to update technologies: {e}")
            return False

class WappalyzerBatchProcessor:
    """Batch processing for Wappalyzer analysis"""
    
    def __init__(self, wappalyzer_integration: WappalyzerIntegration, max_workers: int = 5):
        self.wappalyzer = wappalyzer_integration
        self.max_workers = max_workers
    
    def process_urls(self, urls: List[str], options: Dict[str, Any] = None) -> List[Tuple[str, Optional[Dict[str, Any]], Optional[str]]]:
        """Process multiple URLs with Wappalyzer"""
        from concurrent.futures import ThreadPoolExecutor, as_completed
        
        results = []
        options = options or {}
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_url = {
                executor.submit(self.wappalyzer.analyze_url, url, options): url 
                for url in urls
            }
            
            # Collect results
            for future in as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    result, error = future.result()
                    results.append((url, result, error))
                except Exception as e:
                    results.append((url, None, str(e)))
        
        return results

# Utility functions
def merge_wappalyzer_results(base_results: List[Any], wappalyzer_results: List[Dict[str, Any]]) -> List[Any]:
    """Merge Wappalyzer results with base detection results"""
    # Create lookup for existing results (handle both dict and DetectionResult objects)
    existing_names = set()
    for result in base_results:
        if hasattr(result, 'name'):
            existing_names.add(result.name.lower())
        elif isinstance(result, dict) and 'name' in result:
            existing_names.add(result['name'].lower())
    
    # Add Wappalyzer results that don't already exist
    merged_results = list(base_results)
    
    for wappalyzer_result in wappalyzer_results:
        if hasattr(wappalyzer_result, 'name'):
            wappalyzer_name = wappalyzer_result.name.lower()
        elif isinstance(wappalyzer_result, dict) and 'name' in wappalyzer_result:
            wappalyzer_name = wappalyzer_result['name'].lower()
        else:
            continue
            
        if wappalyzer_name and wappalyzer_name not in existing_names:
            merged_results.append(wappalyzer_result)
    
    # Sort by confidence (handle both dict and DetectionResult objects)
    def get_confidence(item):
        if hasattr(item, 'confidence'):
            return item.confidence
        elif isinstance(item, dict) and 'confidence' in item:
            return item['confidence']
        return 0
    
    merged_results.sort(key=get_confidence, reverse=True)
    
    return merged_results

def create_wappalyzer_summary(wappalyzer_result: Dict[str, Any]) -> Dict[str, Any]:
    """Create a summary of Wappalyzer analysis"""
    technologies = wappalyzer_result.get('technologies', {})
    
    # Count by category
    category_counts = {}
    for tech_name, tech_info in technologies.items():
        categories = tech_info.get('categories', [])
        for category in categories:
            category_counts[category] = category_counts.get(category, 0) + 1
    
    return {
        'total_technologies': len(technologies),
        'technologies_detected': list(technologies.keys()),
        'category_counts': category_counts,
        'analysis_method': wappalyzer_result.get('analysis_method', 'unknown'),
        'execution_time': wappalyzer_result.get('execution_time', 0),
        'timestamp': wappalyzer_result.get('timestamp', time.time())
    }

def create_technology_comparison(base_results: List[Dict[str, Any]], 
                                wappalyzer_results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Create a comparison between base and Wappalyzer results"""
    base_names = {result['name'].lower() for result in base_results}
    wappalyzer_names = {result['name'].lower() for result in wappalyzer_results}
    
    common = base_names.intersection(wappalyzer_names)
    base_only = base_names - wappalyzer_names
    wappalyzer_only = wappalyzer_names - base_names
    
    return {
        'common_technologies': list(common),
        'base_only': list(base_only),
        'wappalyzer_only': list(wappalyzer_only),
        'total_base': len(base_results),
        'total_wappalyzer': len(wappalyzer_results),
        'total_common': len(common),
        'overlap_percentage': len(common) / max(len(base_names), len(wappalyzer_names)) * 100 if base_names or wappalyzer_names else 0
    }

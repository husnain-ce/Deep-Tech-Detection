#!/usr/bin/env python3
"""
WhatWeb Integration Module
=========================

Robust integration with WhatWeb for additional technology detection.
Handles WhatWeb binary execution, output parsing, and result merging.
"""

import json
import logging
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

class WhatWebIntegration:
    """WhatWeb integration with advanced error handling and optimization"""
    
    def __init__(self, whatweb_path: str = "./WhatWeb/whatweb", timeout: int = 10):
        self.whatweb_path = whatweb_path
        self.timeout = timeout
        self._check_whatweb_availability()
    
    def _check_whatweb_availability(self) -> bool:
        """Check if WhatWeb is available and working"""
        try:
            result = subprocess.run(
                [self.whatweb_path, "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                logger.info(f"WhatWeb found: {result.stdout.strip()}")
                return True
            else:
                logger.warning(f"WhatWeb version check failed: {result.stderr}")
                return False
        except FileNotFoundError:
            logger.error(f"WhatWeb not found at path: {self.whatweb_path}")
            return False
        except subprocess.TimeoutExpired:
            logger.error("WhatWeb version check timed out")
            return False
        except Exception as e:
            logger.error(f"WhatWeb availability check failed: {e}")
            return False
    
    def analyze_url(self, url: str, options: Dict[str, Any] = None) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Analyze URL with WhatWeb
        
        Args:
            url: URL to analyze
            options: Analysis options
            
        Returns:
            Tuple of (results_dict, error_message)
        """
        options = options or {}
        
        try:
            # Build WhatWeb command
            cmd = self._build_command(url, options)
            logger.debug(f"Running WhatWeb command: {' '.join(cmd)}")
            
            # Execute WhatWeb
            start_time = time.time()
            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=self.timeout
                )
                execution_time = time.time() - start_time
            except subprocess.TimeoutExpired:
                execution_time = time.time() - start_time
                error_msg = f"WhatWeb command timed out after {self.timeout} seconds"
                logger.error(error_msg)
                return None, error_msg
            
            if result.returncode != 0:
                error_msg = f"WhatWeb execution failed (exit code {result.returncode}): {result.stderr}"
                logger.error(error_msg)
                return None, error_msg
            
            # Parse output
            parsed_result = self._parse_output(result.stdout, execution_time)
            if parsed_result is None:
                return None, "Failed to parse WhatWeb output"
            
            return parsed_result, None
            
        except subprocess.TimeoutExpired:
            error_msg = f"WhatWeb analysis timed out after {self.timeout} seconds"
            logger.error(error_msg)
            return None, error_msg
        except Exception as e:
            error_msg = f"WhatWeb analysis failed: {str(e)}"
            logger.error(error_msg)
            return None, error_msg
    
    def _build_command(self, url: str, options: Dict[str, Any]) -> List[str]:
        """Build WhatWeb command with options"""
        cmd = [self.whatweb_path, url, "--log-json=-"]
        
        # Aggression level (limit to max 1 to avoid timeouts)
        if 'aggression' in options:
            aggression = min(int(options['aggression']), 1)  # Cap at 1
            cmd.extend(["-a", str(aggression)])
        
        # User agent
        if 'user_agent' in options:
            cmd.extend(["-U", options['user_agent']])
        
        # Custom headers
        if 'headers' in options:
            for header, value in options['headers'].items():
                cmd.extend(["-H", f"{header}: {value}"])
        
        # Plugins
        if 'plugins' in options:
            cmd.extend(["-p", ",".join(options['plugins'])])
        
        # Exclude plugins
        if 'exclude_plugins' in options:
            cmd.extend(["-x", ",".join(options['exclude_plugins'])])
        
        # Follow redirects (WhatWeb follows redirects by default)
        # No need to add specific redirect parameters
        
        # Verbose output
        if options.get('verbose', False):
            cmd.append("--verbose")
        
        # Custom timeout (WhatWeb doesn't support --timeout parameter)
        # We'll handle timeout at the subprocess level
        
        return cmd
    
    def _parse_output(self, output: str, execution_time: float) -> Optional[Dict[str, Any]]:
        """Parse WhatWeb JSON output"""
        try:
            # Clean output - remove ANSI color codes and extra whitespace
            import re
            output = re.sub(r'\x1b\[[0-9;]*m', '', output)  # Remove ANSI color codes
            output = output.strip()
            if not output:
                logger.debug("WhatWeb output is empty")
                return None
            
            logger.debug(f"WhatWeb output length: {len(output)}")
            logger.debug(f"WhatWeb output first 200 chars: {repr(output[:200])}")
            
            # WhatWeb outputs an array of results, we want the first one
            try:
                data = json.loads(output)
                logger.debug(f"WhatWeb parsed as JSON successfully, type: {type(data)}")
                if isinstance(data, list) and len(data) > 0:
                    # Get the first result
                    result = data[0]
                    if isinstance(result, dict):
                        result['execution_time'] = execution_time
                        logger.debug(f"WhatWeb first result keys: {list(result.keys())}")
                        return result
                elif isinstance(data, dict):
                    data['execution_time'] = execution_time
                    logger.debug(f"WhatWeb single result keys: {list(data.keys())}")
                    return data
            except json.JSONDecodeError as e:
                logger.debug(f"WhatWeb JSON decode error: {e}")
                logger.debug(f"Problematic part: {output[max(0, e.pos-50):e.pos+50]}")
            
            # Try to parse line by line
            lines = output.split('\n')
            logger.debug(f"WhatWeb trying line-by-line parsing, {len(lines)} lines")
            for i, line in enumerate(lines):
                line = line.strip()
                if not line:
                    continue
                
                try:
                    data = json.loads(line)
                    if isinstance(data, list) and len(data) > 0:
                        result = data[0]
                        if isinstance(result, dict) and self._is_valid_whatweb_output(result):
                            result['execution_time'] = execution_time
                            logger.debug(f"WhatWeb line {i} parsed successfully")
                            return result
                    elif isinstance(data, dict) and self._is_valid_whatweb_output(data):
                        data['execution_time'] = execution_time
                        logger.debug(f"WhatWeb line {i} parsed successfully")
                        return data
                except json.JSONDecodeError:
                    continue
            
            logger.debug("WhatWeb parsing failed completely")
            return None
            
        except Exception as e:
            logger.error(f"Error parsing WhatWeb output: {e}")
            return None
    
    def _is_valid_whatweb_output(self, data: Dict[str, Any]) -> bool:
        """Check if data looks like valid WhatWeb output"""
        return any(key in data for key in ['plugins', 'http_status', 'plugins_count', 'target'])
    
    def extract_technologies(self, whatweb_result: Dict[str, Any]) -> List[Any]:
        """Extract technologies from WhatWeb result"""
        from ..core.enhanced_tech_detector import DetectionResult
        
        technologies = []
        
        plugins = whatweb_result.get('plugins', {})
        if not isinstance(plugins, dict):
            return technologies
        
        for plugin_name, plugin_data in plugins.items():
            if not plugin_data:
                continue
            
            # Handle different plugin data formats
            if isinstance(plugin_data, list):
                for item in plugin_data:
                    if isinstance(item, dict):
                        tech = self._extract_technology_from_plugin(plugin_name, item)
                        if tech:
                            # Convert to DetectionResult
                            detection_result = DetectionResult(
                                name=tech['name'],
                                confidence=tech['confidence'],
                                category=tech['category'],
                                versions=tech['versions'],
                                evidence=tech['evidence'],
                                source=tech['source'],
                                website=tech.get('website'),
                                description=tech.get('description'),
                                saas=tech.get('saas'),
                                oss=tech.get('oss'),
                                user_agent_used=tech.get('user_agent_used'),
                                detection_time=tech.get('detection_time', 0.0)
                            )
                            technologies.append(detection_result)
            elif isinstance(plugin_data, dict):
                tech = self._extract_technology_from_plugin(plugin_name, plugin_data)
                if tech:
                    # Convert to DetectionResult
                    detection_result = DetectionResult(
                        name=tech['name'],
                        confidence=tech['confidence'],
                        category=tech['category'],
                        versions=tech['versions'],
                        evidence=tech['evidence'],
                        source=tech['source'],
                        website=tech.get('website'),
                        description=tech.get('description'),
                        saas=tech.get('saas'),
                        oss=tech.get('oss'),
                        user_agent_used=tech.get('user_agent_used'),
                        detection_time=tech.get('detection_time', 0.0)
                    )
                    technologies.append(detection_result)
            else:
                # Simple string or other format
                detection_result = DetectionResult(
                    name=plugin_name,
                    confidence=60,
                    category='WhatWeb Plugin',
                    versions=[],
                    evidence=[{
                        'field': 'whatweb',
                        'detail': 'plugin',
                        'match': str(plugin_data),
                        'confidence': 60,
                        'version': None
                    }],
                    source='whatweb',
                    description=f"WhatWeb detected: {plugin_name}"
                )
                technologies.append(detection_result)
        
        return technologies
    
    def _extract_technology_from_plugin(self, plugin_name: str, plugin_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract technology information from plugin data"""
        try:
            # Extract version
            versions = []
            if 'version' in plugin_data:
                version = str(plugin_data['version'])
                if version and version != 'None':
                    versions.append(version)
            
            # Extract additional versions from string field
            if 'string' in plugin_data:
                string_data = str(plugin_data['string'])
                # Try to extract version from string
                version_match = self._extract_version_from_string(string_data)
                if version_match and version_match not in versions:
                    versions.append(version_match)
            
            # Build evidence
            evidence = []
            if 'string' in plugin_data:
                evidence.append({
                    'field': 'whatweb',
                    'detail': 'plugin_string',
                    'match': str(plugin_data['string']),
                    'confidence': 60,
                    'version': versions[0] if versions else None
                })
            
            if 'version' in plugin_data and plugin_data['version']:
                evidence.append({
                    'field': 'whatweb',
                    'detail': 'plugin_version',
                    'match': str(plugin_data['version']),
                    'confidence': 70,
                    'version': str(plugin_data['version'])
                })
            
            # Determine confidence based on evidence
            confidence = 60
            if versions:
                confidence = 70
            if len(evidence) > 1:
                confidence = 80
            
            return {
                'name': plugin_name,
                'confidence': confidence,
                'category': 'WhatWeb Plugin',
                'versions': versions,
                'evidence': evidence,
                'source': 'whatweb',
                'description': f"WhatWeb plugin: {plugin_name}"
            }
            
        except Exception as e:
            logger.debug(f"Error extracting technology from plugin {plugin_name}: {e}")
            return None
    
    def _extract_version_from_string(self, string_data: str) -> Optional[str]:
        """Extract version number from string data"""
        import re
        
        # Common version patterns
        version_patterns = [
            r'v?(\d+\.\d+\.\d+)',  # v1.2.3 or 1.2.3
            r'v?(\d+\.\d+)',       # v1.2 or 1.2
            r'version\s*:?\s*(\d+\.\d+\.\d+)',  # version: 1.2.3
            r'version\s*:?\s*(\d+\.\d+)',       # version: 1.2
        ]
        
        for pattern in version_patterns:
            match = re.search(pattern, string_data, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None
    
    def get_available_plugins(self) -> List[str]:
        """Get list of available WhatWeb plugins"""
        try:
            result = subprocess.run(
                [self.whatweb_path, "--list"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                plugins = []
                for line in result.stdout.split('\n'):
                    line = line.strip()
                    if line and not line.startswith('#'):
                        plugins.append(line)
                return plugins
            else:
                logger.warning(f"Failed to get plugin list: {result.stderr}")
                return []
                
        except Exception as e:
            logger.error(f"Error getting plugin list: {e}")
            return []
    
    def get_plugin_info(self, plugin_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific plugin"""
        try:
            result = subprocess.run(
                [self.whatweb_path, "--info", plugin_name],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                return {
                    'name': plugin_name,
                    'info': result.stdout.strip(),
                    'available': True
                }
            else:
                return {
                    'name': plugin_name,
                    'info': None,
                    'available': False,
                    'error': result.stderr.strip()
                }
                
        except Exception as e:
            return {
                'name': plugin_name,
                'info': None,
                'available': False,
                'error': str(e)
            }

class WhatWebBatchProcessor:
    """Batch processing for WhatWeb analysis"""
    
    def __init__(self, whatweb_integration: WhatWebIntegration, max_workers: int = 5):
        self.whatweb = whatweb_integration
        self.max_workers = max_workers
    
    def process_urls(self, urls: List[str], options: Dict[str, Any] = None) -> List[Tuple[str, Optional[Dict[str, Any]], Optional[str]]]:
        """Process multiple URLs with WhatWeb"""
        from concurrent.futures import ThreadPoolExecutor, as_completed
        
        results = []
        options = options or {}
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_url = {
                executor.submit(self.whatweb.analyze_url, url, options): url 
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
def merge_whatweb_results(base_results: List[Any], whatweb_results: List[Any]) -> List[Any]:
    """Merge WhatWeb results with base detection results"""
    # Create lookup for existing results (handle both dict and DetectionResult objects)
    existing_names = set()
    for result in base_results:
        if hasattr(result, 'name'):
            existing_names.add(result.name.lower())
        elif isinstance(result, dict) and 'name' in result:
            existing_names.add(result['name'].lower())
    
    # Add WhatWeb results that don't already exist
    merged_results = list(base_results)
    
    for whatweb_result in whatweb_results:
        if hasattr(whatweb_result, 'name'):
            whatweb_name = whatweb_result.name.lower()
        elif isinstance(whatweb_result, dict) and 'name' in whatweb_result:
            whatweb_name = whatweb_result['name'].lower()
        else:
            continue
            
        if whatweb_name not in existing_names:
            merged_results.append(whatweb_result)
    
    # Sort by confidence (handle both dict and DetectionResult objects)
    def get_confidence(item):
        if hasattr(item, 'confidence'):
            return item.confidence
        elif isinstance(item, dict) and 'confidence' in item:
            return item['confidence']
        return 0
    
    merged_results.sort(key=get_confidence, reverse=True)
    
    return merged_results

def create_whatweb_summary(whatweb_result: Dict[str, Any]) -> Dict[str, Any]:
    """Create a summary of WhatWeb analysis"""
    plugins = whatweb_result.get('plugins', {})
    
    return {
        'total_plugins': len(plugins),
        'plugins_detected': list(plugins.keys()),
        'http_status': whatweb_result.get('http_status'),
        'target': whatweb_result.get('target'),
        'execution_time': whatweb_result.get('execution_time', 0),
        'timestamp': whatweb_result.get('timestamp', time.time())
    }

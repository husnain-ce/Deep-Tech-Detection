#!/usr/bin/env python3
"""
Dynamic WhatWeb Integration with Adaptive Timeout
Automatically adjusts timeout based on site complexity and response patterns
"""

import subprocess
import json
import time
import logging
import re
from typing import Dict, List, Any, Optional, Tuple
from urllib.parse import urlparse
import requests
from pathlib import Path

logger = logging.getLogger(__name__)

class DynamicWhatWebIntegration:
    """WhatWeb integration with dynamic timeout based on site complexity"""
    
    def __init__(self, whatweb_path: str = "./WhatWeb/whatweb", base_timeout: int = 10):
        self.whatweb_path = whatweb_path
        self.base_timeout = base_timeout
        self.timeout_multipliers = {
            'simple': 1.0,      # Static sites, simple pages
            'medium': 2.0,      # Dynamic sites, moderate complexity
            'complex': 4.0,     # Enterprise sites, heavy frameworks
            'protected': 6.0    # Sites with anti-bot protection
        }
        self._check_whatweb_availability()
    
    def _check_whatweb_availability(self) -> bool:
        """Check if WhatWeb is available and working"""
        try:
            result = subprocess.run(
                [self.whatweb_path, "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                logger.info(f"WhatWeb found: {result.stdout.strip()}")
                return True
            else:
                logger.error(f"WhatWeb not available: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"WhatWeb check failed: {e}")
            return False
    
    def analyze_site_complexity(self, url: str) -> str:
        """Analyze site complexity to determine appropriate timeout"""
        try:
            # Parse URL
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            
            # Check for known complex domains
            complex_domains = [
                'github.com', 'stackoverflow.com', 'google.com', 'facebook.com',
                'amazon.com', 'microsoft.com', 'apple.com', 'netflix.com',
                'youtube.com', 'twitter.com', 'linkedin.com', 'instagram.com'
            ]
            
            if any(complex_domain in domain for complex_domain in complex_domains):
                return 'protected'
            
            # Quick site analysis
            try:
                response = requests.get(url, timeout=10, allow_redirects=True)
                content_length = len(response.content)
                response_time = response.elapsed.total_seconds()
                
                # Analyze headers for complexity indicators
                headers = response.headers
                complexity_indicators = 0
                
                # Check for CDN/proxy indicators
                if any(header in headers for header in ['cf-ray', 'x-served-by', 'x-cache']):
                    complexity_indicators += 1
                
                # Check for security headers
                if any(header in headers for header in ['x-frame-options', 'content-security-policy', 'strict-transport-security']):
                    complexity_indicators += 1
                
                # Check for framework indicators
                if any(header in headers for header in ['x-powered-by', 'server']):
                    complexity_indicators += 1
                
                # Check for anti-bot protection
                if any(header in headers for header in ['cf-bgj', 'cf-ray', 'x-bot-protection']):
                    complexity_indicators += 2
                
                # Determine complexity based on indicators
                if complexity_indicators >= 3 or content_length > 1000000 or response_time > 2:
                    return 'complex'
                elif complexity_indicators >= 1 or content_length > 100000 or response_time > 1:
                    return 'medium'
                else:
                    return 'simple'
                    
            except requests.RequestException:
                # If we can't analyze, assume medium complexity
                return 'medium'
                
        except Exception as e:
            logger.warning(f"Site complexity analysis failed: {e}")
            return 'medium'
    
    def calculate_dynamic_timeout(self, url: str, base_timeout: int = None) -> int:
        """Calculate dynamic timeout based on site complexity"""
        if base_timeout is None:
            base_timeout = self.base_timeout
        
        complexity = self.analyze_site_complexity(url)
        multiplier = self.timeout_multipliers.get(complexity, 2.0)
        
        dynamic_timeout = int(base_timeout * multiplier)
        
        logger.debug(f"Site complexity: {complexity}, timeout: {dynamic_timeout}s")
        return dynamic_timeout
    
    def build_command(self, url: str, options: Dict[str, Any]) -> List[str]:
        """Build WhatWeb command with dynamic options"""
        cmd = [self.whatweb_path, url, "--log-json=-"]
        
        # Aggression level (limit to max 1 for dynamic timeout)
        if 'aggression' in options:
            aggression = min(int(options['aggression']), 1)  # Cap at 1 for reliability
            cmd.extend(["-a", str(aggression)])
        
        # User agent
        if 'user_agent' in options:
            cmd.extend(["-U", options['user_agent']])
        
        # Verbose output
        if options.get('verbose', False):
            cmd.append("--verbose")
        
        return cmd
    
    def analyze_url(self, url: str, options: Dict[str, Any] = None) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """Analyze URL with dynamic timeout"""
        options = options or {}
        
        try:
            # Calculate dynamic timeout
            dynamic_timeout = self.calculate_dynamic_timeout(url, options.get('timeout'))
            
            # Build command
            cmd = self.build_command(url, options)
            logger.debug(f"Running WhatWeb command: {' '.join(cmd)} (timeout: {dynamic_timeout}s)")
            
            # Execute WhatWeb with dynamic timeout
            start_time = time.time()
            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=dynamic_timeout
                )
                execution_time = time.time() - start_time
            except subprocess.TimeoutExpired:
                execution_time = time.time() - start_time
                error_msg = f"WhatWeb command timed out after {dynamic_timeout} seconds"
                logger.warning(error_msg)
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
            
        except Exception as e:
            error_msg = f"WhatWeb analysis failed: {str(e)}"
            logger.error(error_msg)
            return None, error_msg
    
    def _parse_output(self, output: str, execution_time: float) -> Optional[Dict[str, Any]]:
        """Parse WhatWeb JSON output with enhanced error handling"""
        try:
            # Clean output - remove ANSI color codes and extra whitespace
            output = re.sub(r'\x1b\[[0-9;]*m', '', output)  # Remove ANSI color codes
            output = output.strip()
            if not output:
                logger.debug("WhatWeb output is empty")
                return None
            
            logger.debug(f"WhatWeb output length: {len(output)}")
            
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
            logger.error(f"Error extracting technology from plugin {plugin_name}: {e}")
            return None
    
    def _extract_version_from_string(self, string_data: str) -> Optional[str]:
        """Extract version number from string data"""
        # Simple version extraction patterns
        version_patterns = [
            r'v?(\d+\.\d+\.\d+)',
            r'version[:\s]+(\d+\.\d+\.\d+)',
            r'(\d+\.\d+\.\d+)',
            r'v?(\d+\.\d+)',
            r'(\d+\.\d+)'
        ]
        
        for pattern in version_patterns:
            match = re.search(pattern, string_data, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None


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
            
        if whatweb_name and whatweb_name not in existing_names:
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

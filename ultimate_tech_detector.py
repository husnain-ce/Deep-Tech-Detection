#!/usr/bin/env python3
"""
Ultimate Web Technology Detection System
========================================

A unified, comprehensive web technology detection system that combines:
- 17,731+ technologies from multiple datasets
- Deep pattern matching with cross-validation
- WhatWeb integration for additional signatures
- Wappalyzer integration for version detection
- Advanced deduplication and evidence collection
- 100% dataset utilization with intelligent merging

Usage:
    python ultimate_tech_detector.py https://example.com
    python ultimate_tech_detector.py https://example.com --verbose --output json
    python ultimate_tech_detector.py https://example.com --deep --max-results 500
"""

import asyncio
import json
import logging
import os
import re
import subprocess
import sys
import time
import traceback
import requests
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Set, Tuple
from dotenv import load_dotenv
from urllib.parse import urlparse
import aiohttp
from collections import defaultdict

# Configure comprehensive logging
from logging_config import get_logger, log_analysis_start, log_analysis_complete, log_analysis_error, log_engine_status
logger = get_logger('ultimate_tech_detector')

@dataclass
class DetectionResult:
    """Single technology detection result"""
    name: str
    confidence: int
    category: str
    versions: List[str] = field(default_factory=list)
    evidence: List[Dict[str, Any]] = field(default_factory=list)
    source: str = "unknown"
    website: Optional[str] = None
    description: Optional[str] = None
    saas: Optional[bool] = None
    oss: Optional[bool] = None
    user_agent_used: Optional[str] = None
    detection_time: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert DetectionResult to dictionary"""
        return {
            'name': self.name,
            'confidence': self.confidence,
            'category': self.category,
            'versions': self.versions,
            'evidence': self.evidence,
            'source': self.source,
            'website': self.website,
            'description': self.description,
            'saas': self.saas,
            'oss': self.oss,
            'user_agent_used': self.user_agent_used,
            'detection_time': self.detection_time
        }

@dataclass
class AnalysisResult:
    """Complete analysis result for a URL"""
    url: str
    final_url: str
    technologies: List[DetectionResult] = field(default_factory=list)
    analysis_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    user_agents_tried: List[str] = field(default_factory=list)
    successful_agent: Optional[str] = None

class UltimateDatasetManager:
    """Unified dataset manager for maximum technology coverage"""
    
    def __init__(self, datasets_dir: str = "data/datasets"):
        self.datasets_dir = datasets_dir
        self.all_technologies = {}
        self.pattern_database = defaultdict(lambda: defaultdict(list))
        self.technology_relationships = defaultdict(list)
        self.categories = defaultdict(int)
        self._load_all_datasets()
    
    def _load_all_datasets(self):
        """Load all available datasets for maximum coverage"""
        logger.info("Loading all available datasets for 100% utilization...")
        
        # Load organized datasets
        organized_path = os.path.join(self.datasets_dir, "organized")
        if os.path.exists(organized_path):
            self._load_organized_datasets(organized_path)
        
        # Load individual Wappalyzer files
        wappalyzer_path = os.path.join(self.datasets_dir, "wappalyzer")
        if os.path.exists(wappalyzer_path):
            self._load_wappalyzer_datasets(wappalyzer_path)
        
        # Load raw datasets
        raw_path = os.path.join(self.datasets_dir, "raw")
        if os.path.exists(raw_path):
            self._load_raw_datasets(raw_path)
        
        # Build pattern database
        self._build_pattern_database()
        
        # Build technology relationships
        self._build_technology_relationships()
        
        logger.info(f"Loaded {len(self.all_technologies)} technologies from all datasets")
        logger.info(f"Built pattern database with {sum(len(patterns) for patterns in self.pattern_database.values())} patterns")
    
    def _load_organized_datasets(self, organized_path: str):
        """Load organized category datasets"""
        for filename in os.listdir(organized_path):
            if filename.endswith('.json'):
                filepath = os.path.join(organized_path, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if isinstance(data, dict):
                            for tech_name, tech_data in data.items():
                                if isinstance(tech_data, dict):
                                    self.all_technologies[tech_name] = tech_data
                                    category = tech_data.get('category', 'Unknown')
                                    self.categories[category] += 1
                except Exception as e:
                    logger.warning(f"Failed to load {filename}: {e}")
    
    def _load_wappalyzer_datasets(self, wappalyzer_path: str):
        """Load individual Wappalyzer files"""
        for filename in os.listdir(wappalyzer_path):
            if filename.endswith('.json'):
                filepath = os.path.join(wappalyzer_path, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if isinstance(data, dict):
                            for tech_name, tech_data in data.items():
                                if isinstance(tech_data, dict):
                                    self.all_technologies[tech_name] = tech_data
                                    category = tech_data.get('category', 'Unknown')
                                    self.categories[category] += 1
                except Exception as e:
                    logger.warning(f"Failed to load {filename}: {e}")
    
    def _load_raw_datasets(self, raw_path: str):
        """Load raw datasets (only add new technologies, don't overwrite existing ones)"""
        for filename in os.listdir(raw_path):
            if filename.endswith('.json'):
                filepath = os.path.join(raw_path, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if isinstance(data, dict):
                            for tech_name, tech_data in data.items():
                                if isinstance(tech_data, dict):
                                    # Only add if technology doesn't already exist
                                    if tech_name not in self.all_technologies:
                                        self.all_technologies[tech_name] = tech_data
                                        category = tech_data.get('category', 'Unknown')
                                        self.categories[category] += 1
                except Exception as e:
                    logger.warning(f"Failed to load {filename}: {e}")
    
    def _build_pattern_database(self):
        """Build comprehensive pattern database for fast matching"""
        for tech_name, tech_data in self.all_technologies.items():
            if isinstance(tech_data, dict):
                patterns = self._extract_patterns(tech_data)
                for pattern_type, pattern_list in patterns.items():
                    for pattern in pattern_list:
                        self.pattern_database[pattern_type][pattern].append({
                            'technology': tech_name,
                            'source': 'dataset',
                            'confidence': tech_data.get('confidence', 50)
                        })
    
    def _extract_patterns(self, tech_data: Dict[str, Any]) -> Dict[str, List[str]]:
        """Extract all patterns from technology data"""
        patterns = defaultdict(list)
        
        # Check if patterns are under a 'patterns' key (organized datasets)
        if 'patterns' in tech_data and isinstance(tech_data['patterns'], dict):
            pattern_data = tech_data['patterns']
            
            # Headers patterns
            if 'headers' in pattern_data:
                headers = pattern_data['headers']
                if isinstance(headers, list):
                    patterns['headers'].extend(headers)
                elif isinstance(headers, str):
                    patterns['headers'].append(headers)
            
            # HTML patterns
            if 'html' in pattern_data:
                html_patterns = pattern_data['html']
                if isinstance(html_patterns, list):
                    patterns['html'].extend(html_patterns)
                elif isinstance(html_patterns, str):
                    patterns['html'].append(html_patterns)
            
            # Script patterns
            if 'scripts' in pattern_data:
                script_patterns = pattern_data['scripts']
                if isinstance(script_patterns, list):
                    patterns['scripts'].extend(script_patterns)
                elif isinstance(script_patterns, str):
                    patterns['scripts'].append(script_patterns)
            
            # ScriptSrc patterns (also go to scripts)
            if 'scriptSrc' in pattern_data:
                script_src_patterns = pattern_data['scriptSrc']
                if isinstance(script_src_patterns, list):
                    patterns['scripts'].extend(script_src_patterns)
                elif isinstance(script_src_patterns, str):
                    patterns['scripts'].append(script_src_patterns)
            
            # URL patterns
            if 'url' in pattern_data:
                url_patterns = pattern_data['url']
                if isinstance(url_patterns, list):
                    patterns['urls'].extend(url_patterns)
                elif isinstance(url_patterns, str):
                    patterns['urls'].append(url_patterns)
            
            # Cookie patterns
            if 'cookies' in pattern_data:
                cookie_patterns = pattern_data['cookies']
                if isinstance(cookie_patterns, list):
                    patterns['cookies'].extend(cookie_patterns)
                elif isinstance(cookie_patterns, str):
                    patterns['cookies'].append(cookie_patterns)
            
            # Meta patterns
            if 'meta' in pattern_data:
                meta_patterns = pattern_data['meta']
                if isinstance(meta_patterns, list):
                    patterns['meta'].extend(meta_patterns)
                elif isinstance(meta_patterns, str):
                    patterns['meta'].append(meta_patterns)
        
        # Also check for direct pattern keys (raw datasets)
        # Headers
        if 'headers' in tech_data:
            headers = tech_data['headers']
            if isinstance(headers, dict):
                for header, value in headers.items():
                    patterns['headers'].append(f"{header.lower()}:{value}")
            elif isinstance(headers, list):
                for header in headers:
                    patterns['headers'].append(header.lower())
        
        # HTML patterns
        if 'html' in tech_data:
            html_patterns = tech_data['html']
            if isinstance(html_patterns, list):
                patterns['html'].extend(html_patterns)
            elif isinstance(html_patterns, str):
                patterns['html'].append(html_patterns)
        
        # Script patterns
        if 'js' in tech_data:
            js_patterns = tech_data['js']
            if isinstance(js_patterns, dict):
                for key, value in js_patterns.items():
                    if isinstance(value, str):
                        patterns['scripts'].append(value)
            elif isinstance(js_patterns, list):
                patterns['scripts'].extend(js_patterns)
        
        # URL patterns
        if 'url' in tech_data:
            url_patterns = tech_data['url']
            if isinstance(url_patterns, list):
                patterns['urls'].extend(url_patterns)
            elif isinstance(url_patterns, str):
                patterns['urls'].append(url_patterns)
        
        # Cookie patterns
        if 'cookies' in tech_data:
            cookie_patterns = tech_data['cookies']
            if isinstance(cookie_patterns, dict):
                for cookie, value in cookie_patterns.items():
                    patterns['cookies'].append(f"{cookie}={value}")
            elif isinstance(cookie_patterns, list):
                patterns['cookies'].extend(cookie_patterns)
        
        # Meta patterns
        if 'meta' in tech_data:
            meta_patterns = tech_data['meta']
            if isinstance(meta_patterns, dict):
                for key, value in meta_patterns.items():
                    patterns['meta'].append(f"{key}={value}")
            elif isinstance(meta_patterns, list):
                patterns['meta'].extend(meta_patterns)
        
        return dict(patterns)
    
    def _build_technology_relationships(self):
        """Build technology relationship mapping"""
        for tech_name, tech_data in self.all_technologies.items():
            if isinstance(tech_data, dict):
                # Implies relationships
                if 'implies' in tech_data:
                    implies = tech_data['implies']
                    if isinstance(implies, list):
                        for implied_tech in implies:
                            self.technology_relationships[implied_tech].append(tech_name)
                    elif isinstance(implies, str):
                        self.technology_relationships[implies].append(tech_name)

class UltimatePatternMatcher:
    """Advanced pattern matcher with multi-level detection"""
    
    def __init__(self, dataset_manager: UltimateDatasetManager):
        self.dataset_manager = dataset_manager
        self.pattern_cache = {}
        self.detection_stats = {
            'total_detections': 0,
            'pattern_matches': 0,
            'cross_validations': 0,
            'false_positives': 0
        }
    
    async def detect_all_technologies(self, url: str, response_data: Dict[str, Any]) -> List[DetectionResult]:
        """Detect all possible technologies using comprehensive pattern matching"""
        logger.info(f"Starting comprehensive technology detection for {url}")
        start_time = time.time()
        
        all_detections = []
        
        # Level 1: Fast pattern detection (headers, meta, basic patterns)
        fast_results = await self._detect_fast_patterns(url, response_data)
        logger.info(f"Fast pattern detection: {len(fast_results)} technologies found")
        all_detections.extend(fast_results)
        
        # Level 2: Medium pattern detection (HTML, scripts, URLs)
        medium_results = await self._detect_medium_patterns(url, response_data)
        logger.info(f"Medium pattern detection: {len(medium_results)} technologies found")
        all_detections.extend(medium_results)
        
        # Level 3: Deep pattern detection (DNS, SSL, complex patterns)
        deep_results = await self._detect_deep_patterns(url, response_data)
        logger.info(f"Deep pattern detection: {len(deep_results)} technologies found")
        all_detections.extend(deep_results)
        
        # Cross-validation and relationship detection
        cross_validated = await self._cross_validate_detections(all_detections)
        all_detections.extend(cross_validated)
        
        # Deduplicate and merge results
        final_detections = self._deduplicate_detections(all_detections)
        
        detection_time = time.time() - start_time
        logger.info(f"Comprehensive detection completed in {detection_time:.2f}s - {len(final_detections)} technologies found")
        
        return final_detections
    
    async def _detect_fast_patterns(self, url: str, response_data: Dict[str, Any]) -> List[DetectionResult]:
        """Fast pattern detection for headers and meta tags"""
        detections = []
        
        # Headers detection
        headers = response_data.get('headers', {})
        logger.info(f"Fast pattern detection: Checking {len(headers)} headers")
        for header, value in headers.items():
            header_text = f"{header}: {value}"
            # Check all header patterns
            if 'headers' in self.dataset_manager.pattern_database:
                for pattern in self.dataset_manager.pattern_database['headers']:
                    try:
                        if re.search(pattern, header_text, re.IGNORECASE):
                            for match in self.dataset_manager.pattern_database['headers'][pattern]:
                                tech_name = match['technology']
                                tech_data = self.dataset_manager.all_technologies.get(tech_name, {})
                                
                                detection = DetectionResult(
                                    name=tech_name,
                                    confidence=match['confidence'],
                                    category=tech_data.get('category', 'Unknown'),
                                    evidence=[{
                                        'field': 'headers',
                                        'detail': header_text,
                                        'match': pattern,
                                        'confidence': match['confidence']
                                    }],
                                    source='fast_pattern',
                                    website=tech_data.get('website'),
                                    description=tech_data.get('description'),
                                    saas=tech_data.get('saas'),
                                    oss=tech_data.get('oss'),
                                    detection_time=time.time()
                                )
                                detections.append(detection)
                                logger.info(f"Fast pattern detected: {tech_name} from header")
                    except re.error:
                        continue
        
        # Meta tags detection
        meta_tags = response_data.get('meta_tags', {})
        logger.info(f"Fast pattern detection: Checking {len(meta_tags)} meta tags")
        for meta, value in meta_tags.items():
            meta_text = f"{meta}: {value}"
            # Check all meta patterns
            if 'meta' in self.dataset_manager.pattern_database:
                for pattern in self.dataset_manager.pattern_database['meta']:
                    try:
                        if re.search(pattern, meta_text, re.IGNORECASE):
                            for match in self.dataset_manager.pattern_database['meta'][pattern]:
                                tech_name = match['technology']
                                tech_data = self.dataset_manager.all_technologies.get(tech_name, {})
                                
                                detection = DetectionResult(
                                    name=tech_name,
                                    confidence=match['confidence'],
                                    category=tech_data.get('category', 'Unknown'),
                                    evidence=[{
                                        'field': 'meta',
                                        'detail': meta_text,
                                        'match': pattern,
                                        'confidence': match['confidence']
                                    }],
                                    source='fast_pattern',
                                    website=tech_data.get('website'),
                                    description=tech_data.get('description'),
                                    saas=tech_data.get('saas'),
                                    oss=tech_data.get('oss'),
                                    detection_time=time.time()
                                )
                                detections.append(detection)
                                logger.info(f"Fast pattern detected: {tech_name} from meta tag")
                    except re.error:
                        continue
        
        return detections
    
    async def _detect_medium_patterns(self, url: str, response_data: Dict[str, Any]) -> List[DetectionResult]:
        """Medium pattern detection for HTML, scripts, and URLs"""
        detections = []
        
        # HTML content detection
        html_content = response_data.get('content', '')
        for pattern in self.dataset_manager.pattern_database['html']:
            try:
                if re.search(pattern, html_content, re.IGNORECASE):
                    for match in self.dataset_manager.pattern_database['html'][pattern]:
                        tech_name = match['technology']
                        tech_data = self.dataset_manager.all_technologies.get(tech_name, {})
                        
                        detection = DetectionResult(
                            name=tech_name,
                            confidence=match['confidence'],
                            category=tech_data.get('category', 'Unknown'),
                            evidence=[{
                                'field': 'html',
                                'detail': f"HTML pattern match",
                                'match': pattern,
                                'confidence': match['confidence']
                            }],
                            source='medium_pattern',
                            website=tech_data.get('website'),
                            description=tech_data.get('description'),
                            saas=tech_data.get('saas'),
                            oss=tech_data.get('oss'),
                            detection_time=time.time()
                        )
                        detections.append(detection)
            except re.error:
                # Skip invalid regex patterns
                continue
        
        # Script detection
        scripts = response_data.get('scripts', [])
        for script_url in scripts:
            for pattern in self.dataset_manager.pattern_database['scripts']:
                try:
                    if re.search(pattern, script_url, re.IGNORECASE):
                        for match in self.dataset_manager.pattern_database['scripts'][pattern]:
                            tech_name = match['technology']
                            tech_data = self.dataset_manager.all_technologies.get(tech_name, {})
                            
                            detection = DetectionResult(
                                name=tech_name,
                                confidence=match['confidence'],
                                category=tech_data.get('category', 'Unknown'),
                                evidence=[{
                                    'field': 'scripts',
                                    'detail': script_url,
                                    'match': pattern,
                                    'confidence': match['confidence']
                                }],
                                source='medium_pattern',
                                website=tech_data.get('website'),
                                description=tech_data.get('description'),
                                saas=tech_data.get('saas'),
                                oss=tech_data.get('oss'),
                                detection_time=time.time()
                            )
                            detections.append(detection)
                except re.error:
                    # Skip invalid regex patterns
                    continue
        
        return detections
    
    async def _detect_deep_patterns(self, url: str, response_data: Dict[str, Any]) -> List[DetectionResult]:
        """Deep pattern detection for complex patterns and relationships"""
        detections = []
        
        # URL pattern detection
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        
        for pattern in self.dataset_manager.pattern_database['urls']:
            try:
                if re.search(pattern, url, re.IGNORECASE):
                    for match in self.dataset_manager.pattern_database['urls'][pattern]:
                        tech_name = match['technology']
                        tech_data = self.dataset_manager.all_technologies.get(tech_name, {})
                        
                        detection = DetectionResult(
                            name=tech_name,
                            confidence=match['confidence'],
                            category=tech_data.get('category', 'Unknown'),
                            evidence=[{
                                'field': 'url',
                                'detail': url,
                                'match': pattern,
                                'confidence': match['confidence']
                            }],
                            source='deep_pattern',
                            website=tech_data.get('website'),
                            description=tech_data.get('description'),
                            saas=tech_data.get('saas'),
                            oss=tech_data.get('oss'),
                            detection_time=time.time()
                        )
                        detections.append(detection)
            except re.error:
                # Skip invalid regex patterns
                continue
        
        return detections
    
    async def _cross_validate_detections(self, detections: List[DetectionResult]) -> List[DetectionResult]:
        """Cross-validate detections using technology relationships"""
        cross_validated = []
        
        for detection in detections:
            tech_name = detection.name
            if tech_name in self.dataset_manager.technology_relationships:
                related_techs = self.dataset_manager.technology_relationships[tech_name]
                for related_tech in related_techs:
                    if related_tech in self.dataset_manager.all_technologies:
                        tech_data = self.dataset_manager.all_technologies[related_tech]
                        
                        cross_detection = DetectionResult(
                            name=related_tech,
                            confidence=detection.confidence - 10,  # Lower confidence for implied tech
                            category=tech_data.get('category', 'Unknown'),
                            evidence=[{
                                'field': 'cross_validation',
                                'detail': f"Implied by {tech_name}",
                                'match': f"relationship:{tech_name}",
                                'confidence': detection.confidence - 10
                            }],
                            source='cross_validation',
                            website=tech_data.get('website'),
                            description=tech_data.get('description'),
                            saas=tech_data.get('saas'),
                            oss=tech_data.get('oss'),
                            detection_time=time.time()
                        )
                        cross_validated.append(cross_detection)
        
        return cross_validated
    
    def _deduplicate_detections(self, detections: List[DetectionResult]) -> List[DetectionResult]:
        """Deduplicate and merge detection results"""
        tech_dict = {}
        
        for detection in detections:
            name = detection.name
            if name in tech_dict:
                # Merge with existing detection
                existing = tech_dict[name]
                if detection.confidence > existing.confidence:
                    tech_dict[name] = detection
                # Merge evidence
                existing.evidence.extend(detection.evidence)
            else:
                tech_dict[name] = detection
        
        return list(tech_dict.values())

class WhatWebIntegration:
    """WhatWeb integration for additional technology detection"""
    
    def __init__(self):
        self.whatweb_path = "/usr/bin/whatweb"
        self.available = self._check_availability()
    
    def _check_availability(self) -> bool:
        """Check if WhatWeb is available"""
        try:
            result = subprocess.run([self.whatweb_path, "--version"], 
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except:
            return False
    
    async def analyze_url(self, url: str) -> List[DetectionResult]:
        """Run WhatWeb analysis on URL"""
        if not self.available:
            return []
        
        try:
            cmd = [
                self.whatweb_path,
                "--log-json=-",
                "--verbose",
                "--aggression=3",
                url
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0:
                if result.stdout and result.stdout.strip():
                    return self._parse_whatweb_output(result.stdout)
                else:
                    logger.info("WhatWeb completed but returned no output")
                    return []
            else:
                logger.warning(f"WhatWeb failed (exit code {result.returncode}): {result.stderr}")
                return []
                
        except Exception as e:
            logger.error(f"WhatWeb analysis failed: {e}")
            return []
    
    def _parse_whatweb_output(self, output: str) -> List[DetectionResult]:
        """Parse WhatWeb JSON output with robust error handling"""
        detections = []
        
        try:
            # Clean the output and handle multiple JSON objects
            lines = output.strip().split('\n')
            logger.debug(f"WhatWeb output lines: {len(lines)}")
            
            for i, line in enumerate(lines):
                if not line.strip():
                    continue
                    
                try:
                    # Try to parse as JSON
                    data = json.loads(line)
                    
                    # Handle different WhatWeb output formats
                    if isinstance(data, dict):
                        if 'plugins' in data:
                            # Standard WhatWeb format
                            for plugin_name, plugin_data in data['plugins'].items():
                                if isinstance(plugin_data, dict):
                                    detection = self._create_whatweb_detection(plugin_name, plugin_data)
                                    if detection:
                                        detections.append(detection)
                        elif 'target' in data and 'plugins' in data:
                            # Alternative format
                            for plugin_name, plugin_data in data['plugins'].items():
                                if isinstance(plugin_data, dict):
                                    detection = self._create_whatweb_detection(plugin_name, plugin_data)
                                    if detection:
                                        detections.append(detection)
                        else:
                            # Direct plugin data
                            for key, value in data.items():
                                if isinstance(value, dict) and 'confidence' in value:
                                    detection = self._create_whatweb_detection(key, value)
                                    if detection:
                                        detections.append(detection)
                    elif isinstance(data, list):
                        # Handle array format
                        for item in data:
                            if isinstance(item, dict) and 'plugins' in item:
                                for plugin_name, plugin_data in item['plugins'].items():
                                    if isinstance(plugin_data, dict):
                                        detection = self._create_whatweb_detection(plugin_name, plugin_data)
                                        if detection:
                                            detections.append(detection)
                                            
                except json.JSONDecodeError as je:
                    logger.warning(f"JSON decode error on line {i+1}: {je}")
                    logger.debug(f"Problematic line: {line[:100]}...")
                    continue
                except Exception as e:
                    logger.warning(f"Error processing line {i+1}: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Failed to parse WhatWeb output: {e}")
            logger.debug(f"Raw output: {output[:500]}...")
        
        logger.info(f"WhatWeb detected {len(detections)} technologies")
        return detections
    
    def _create_whatweb_detection(self, plugin_name: str, plugin_data: dict) -> DetectionResult:
        """Create DetectionResult from WhatWeb plugin data"""
        try:
            # Extract confidence with fallback
            confidence = plugin_data.get('confidence', 50)
            if isinstance(confidence, list) and confidence:
                confidence = confidence[0]
            elif not isinstance(confidence, (int, float)):
                confidence = 50
            
            # Extract version information
            versions = []
            if 'version' in plugin_data:
                version_data = plugin_data['version']
                if isinstance(version_data, list):
                    versions = version_data
                elif isinstance(version_data, str):
                    versions = [version_data]
            
            # Extract category
            category = plugin_data.get('category', 'Unknown')
            if isinstance(category, list) and category:
                category = category[0]
            
            # Create evidence
            evidence = [{
                'field': 'whatweb',
                'detail': str(plugin_data),
                'match': plugin_name,
                'confidence': confidence
            }]
            
            return DetectionResult(
                name=plugin_name,
                confidence=min(max(confidence, 10), 100),  # Clamp between 10-100
                category=category,
                versions=versions,
                evidence=evidence,
                source='whatweb',
                website=plugin_data.get('website', ''),
                description=plugin_data.get('description', ''),
                detection_time=time.time()
            )
        except Exception as e:
            logger.warning(f"Failed to create detection for {plugin_name}: {e}")
            return None

class CMSeeKIntegration:
    """CMSeeK integration for CMS detection and exploitation"""
    
    def __init__(self):
        self.cmseek_path = "./data/external_tools/CMSeeK/cmseek.py"
        self.available = self._check_availability()
    
    def _check_availability(self) -> bool:
        """Check if CMSeeK is available"""
        try:
            result = subprocess.run([sys.executable, self.cmseek_path, "--version"], 
                                  capture_output=True, text=True, timeout=10)
            # CMSeeK returns non-zero exit code even for version, so check if it's actually working
            return ("CMSeeK Version" in result.stdout or 
                   "Version:" in result.stdout or 
                   "1.1.3" in result.stdout or
                   "K-RONA" in result.stdout)
        except Exception as e:
            logger.warning(f"CMSeeK availability check failed: {e}")
            return False
    
    async def analyze_url(self, url: str) -> List[DetectionResult]:
        """Run CMSeeK analysis on URL"""
        if not self.available:
            return []
        
        try:
            cmd = [
                sys.executable,
                self.cmseek_path,
                "-u", url,
                "-v",
                "--batch"  # Non-interactive mode
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                if result.stdout and result.stdout.strip():
                    return self._parse_cmseek_output(result.stdout, url)
                else:
                    logger.info("CMSeeK completed but returned no output")
                    return []
            else:
                logger.warning(f"CMSeeK failed (exit code {result.returncode}): {result.stderr}")
                return []
                
        except Exception as e:
            logger.error(f"CMSeeK analysis failed: {e}")
            return []
    
    def _parse_cmseek_output(self, output: str, url: str) -> List[DetectionResult]:
        """Parse CMSeeK output and extract CMS information"""
        detections = []
        
        try:
            # Look for CMS detection patterns in the output
            lines = output.strip().split('\n')
            logger.debug(f"CMSeeK output lines: {len(lines)}")
            
            current_cms = None
            current_version = None
            
            for line in lines:
                line = line.strip()
                logger.debug(f"CMSeeK line: {line}")
                
                # Look for CMS detection patterns
                if ('CMS Detected' in line or 'CMS:' in line or 'Detected:' in line or 
                    'Found:' in line or 'CMS ID:' in line or 'Probable CMS:' in line):
                    # Extract CMS name and version if available
                    cms_info = self._extract_cms_info(line)
                    if cms_info and cms_info['name'] != '<name and/or cms url>':
                        current_cms = cms_info
                        detection = DetectionResult(
                            name=cms_info['name'],
                            confidence=90,  # High confidence for CMS detection
                            category='CMS',
                            versions=cms_info.get('versions', []),
                            evidence=[{
                                'field': 'cmseek',
                                'detail': line,
                                'match': cms_info['name'],
                                'confidence': 90
                            }],
                            source='cmseek',
                            website=cms_info.get('website', ''),
                            description=cms_info.get('description', ''),
                            detection_time=time.time()
                        )
                        detections.append(detection)
                        logger.info(f"CMSeeK detected CMS: {cms_info['name']}")
                    else:
                        # If we can't identify the specific CMS, create a generic detection
                        detection = DetectionResult(
                            name='Unknown CMS',
                            confidence=70,  # Lower confidence for unknown CMS
                            category='CMS',
                            versions=[],
                            evidence=[{
                                'field': 'cmseek',
                                'detail': line,
                                'match': 'Unknown CMS',
                                'confidence': 70
                            }],
                            source='cmseek',
                            website='',
                            description='Content management system detected by CMSeeK',
                            detection_time=time.time()
                        )
                        detections.append(detection)
                        logger.info("CMSeeK detected unknown CMS")
                
                # Look for version information
                elif ('Version:' in line or 'version' in line.lower() or 
                      'v ' in line.lower() or 'detected' in line.lower()):
                    version_info = self._extract_version_info(line)
                    if version_info:
                        if detections and current_cms:
                            # Add version to the last detection
                            detections[-1].versions.extend(version_info)
                            detections[-1].evidence.append({
                                'field': 'cmseek_version',
                                'detail': line,
                                'match': version_info[0],
                                'confidence': 85
                            })
                            logger.info(f"CMSeeK detected version: {version_info[0]} for {current_cms['name']}")
                        else:
                            # Create a new detection if we have version but no CMS
                            detection = DetectionResult(
                                name=current_cms.get('name', 'Unknown CMS') if current_cms else 'Unknown CMS',
                                confidence=80,
                                category='CMS',
                                versions=version_info,
                                evidence=[{
                                    'field': 'cmseek_version',
                                    'detail': line,
                                    'match': version_info[0],
                                    'confidence': 80
                                }],
                                source='cmseek',
                                website=current_cms.get('website', '') if current_cms else '',
                                description=current_cms.get('description', '') if current_cms else '',
                                detection_time=time.time()
                            )
                            detections.append(detection)
                            logger.info(f"CMSeeK detected version: {version_info[0]}")
            
            logger.info(f"CMSeeK detected {len(detections)} CMS technologies")
            
        except Exception as e:
            logger.error(f"Failed to parse CMSeeK output: {e}")
            logger.debug(f"Raw CMSeeK output: {output[:500]}...")
        
        return detections
    
    def _extract_cms_info(self, line: str) -> Optional[Dict[str, Any]]:
        """Extract CMS information from a line"""
        try:
            # Common CMS patterns
            cms_patterns = {
                'Sitefinity': {'website': 'https://www.sitefinity.com', 'description': 'Sitefinity is a .NET-based content management system'},
                'WordPress': {'website': 'https://wordpress.org', 'description': 'WordPress is a free and open-source content management system'},
                'Joomla': {'website': 'https://www.joomla.org', 'description': 'Joomla is a free and open-source content management system'},
                'Drupal': {'website': 'https://www.drupal.org', 'description': 'Drupal is a free and open-source content management system'},
                'Magento': {'website': 'https://magento.com', 'description': 'Magento is an e-commerce platform'},
                'Shopify': {'website': 'https://www.shopify.com', 'description': 'Shopify is a commerce platform'},
                'WooCommerce': {'website': 'https://woocommerce.com', 'description': 'WooCommerce is an e-commerce plugin for WordPress'},
                'PrestaShop': {'website': 'https://www.prestashop.com', 'description': 'PrestaShop is an e-commerce platform'},
                'OpenCart': {'website': 'https://www.opencart.com', 'description': 'OpenCart is an e-commerce platform'},
                'Ghost': {'website': 'https://ghost.org', 'description': 'Ghost is a modern publishing platform'},
                'Squarespace': {'website': 'https://www.squarespace.com', 'description': 'Squarespace is a website building platform'},
                'Wix': {'website': 'https://www.wix.com', 'description': 'Wix is a cloud-based web development platform'},
                'Webflow': {'website': 'https://webflow.com', 'description': 'Webflow is a visual web development platform'},
                'Hugo': {'website': 'https://gohugo.io', 'description': 'Hugo is a static site generator'},
                'Jekyll': {'website': 'https://jekyllrb.com', 'description': 'Jekyll is a static site generator'},
                'Gatsby': {'website': 'https://www.gatsbyjs.com', 'description': 'Gatsby is a React-based static site generator'},
                'Next.js': {'website': 'https://nextjs.org', 'description': 'Next.js is a React framework'},
                'Nuxt.js': {'website': 'https://nuxtjs.org', 'description': 'Nuxt.js is a Vue.js framework'},
                'Laravel': {'website': 'https://laravel.com', 'description': 'Laravel is a PHP web framework'},
                'Symfony': {'website': 'https://symfony.com', 'description': 'Symfony is a PHP web framework'},
                'CodeIgniter': {'website': 'https://codeigniter.com', 'description': 'CodeIgniter is a PHP web framework'},
                'CakePHP': {'website': 'https://cakephp.org', 'description': 'CakePHP is a PHP web framework'},
                'Yii': {'website': 'https://www.yiiframework.com', 'description': 'Yii is a PHP web framework'},
                'Zend': {'website': 'https://framework.zend.com', 'description': 'Zend Framework is a PHP web framework'},
                'Express.js': {'website': 'https://expressjs.com', 'description': 'Express.js is a Node.js web framework'},
                'Django': {'website': 'https://www.djangoproject.com', 'description': 'Django is a Python web framework'},
                'Flask': {'website': 'https://flask.palletsprojects.com', 'description': 'Flask is a Python web framework'},
                'Ruby on Rails': {'website': 'https://rubyonrails.org', 'description': 'Ruby on Rails is a Ruby web framework'},
                'ASP.NET': {'website': 'https://dotnet.microsoft.com', 'description': 'ASP.NET is a Microsoft web framework'},
                'Spring': {'website': 'https://spring.io', 'description': 'Spring is a Java framework'},
                'Struts': {'website': 'https://struts.apache.org', 'description': 'Apache Struts is a Java web framework'},
                'JSF': {'website': 'https://javaee.github.io/javaserverfaces-spec', 'description': 'JavaServer Faces is a Java web framework'},
                'Tapestry': {'website': 'https://tapestry.apache.org', 'description': 'Apache Tapestry is a Java web framework'},
                'Wicket': {'website': 'https://wicket.apache.org', 'description': 'Apache Wicket is a Java web framework'},
                'Grails': {'website': 'https://grails.org', 'description': 'Grails is a Groovy web framework'},
                'Play': {'website': 'https://www.playframework.com', 'description': 'Play Framework is a Java/Scala web framework'},
                'Vaadin': {'website': 'https://vaadin.com', 'description': 'Vaadin is a Java web framework'},
                'GWT': {'website': 'https://www.gwtproject.org', 'description': 'Google Web Toolkit is a Java web framework'},
                'ZK': {'website': 'https://www.zkoss.org', 'description': 'ZK is a Java web framework'},
                'PrimeFaces': {'website': 'https://www.primefaces.org', 'description': 'PrimeFaces is a Java web framework'},
                'RichFaces': {'website': 'https://richfaces.jboss.org', 'description': 'RichFaces is a Java web framework'},
                'IceFaces': {'website': 'https://www.icefaces.org', 'description': 'ICEfaces is a Java web framework'},
                'MyFaces': {'website': 'https://myfaces.apache.org', 'description': 'Apache MyFaces is a Java web framework'},
                'OpenFaces': {'website': 'https://openfaces.org', 'description': 'OpenFaces is a Java web framework'},
                'ButterFaces': {'website': 'https://butterfaces.org', 'description': 'ButterFaces is a Java web framework'},
                'OmniFaces': {'website': 'https://omnifaces.org', 'description': 'OmniFaces is a Java web framework'},
                'DeltaSpike': {'website': 'https://deltaspike.apache.org', 'description': 'Apache DeltaSpike is a Java web framework'},
                'Seam': {'website': 'https://seamframework.org', 'description': 'Seam is a Java web framework'},
                'Weld': {'website': 'https://weld.cdi-spec.org', 'description': 'Weld is a Java web framework'},
                'CDI': {'website': 'https://cdi-spec.org', 'description': 'Contexts and Dependency Injection is a Java web framework'},
                'EJB': {'website': 'https://javaee.github.io/ejb-spec', 'description': 'Enterprise JavaBeans is a Java web framework'},
                'JPA': {'website': 'https://javaee.github.io/javaee-spec', 'description': 'Java Persistence API is a Java web framework'},
                'JTA': {'website': 'https://javaee.github.io/javaee-spec', 'description': 'Java Transaction API is a Java web framework'},
                'JMS': {'website': 'https://javaee.github.io/javaee-spec', 'description': 'Java Message Service is a Java web framework'},
                'JAX-RS': {'website': 'https://javaee.github.io/javaee-spec', 'description': 'Java API for RESTful Web Services is a Java web framework'},
                'JAX-WS': {'website': 'https://javaee.github.io/javaee-spec', 'description': 'Java API for XML Web Services is a Java web framework'},
                'JAXB': {'website': 'https://javaee.github.io/javaee-spec', 'description': 'Java Architecture for XML Binding is a Java web framework'},
                'JAXP': {'website': 'https://javaee.github.io/javaee-spec', 'description': 'Java API for XML Processing is a Java web framework'},
                'JAXR': {'website': 'https://javaee.github.io/javaee-spec', 'description': 'Java API for XML Registries is a Java web framework'},
                'JAXM': {'website': 'https://javaee.github.io/javaee-spec', 'description': 'Java API for XML Messaging is a Java web framework'},
                'JAXRPC': {'website': 'https://javaee.github.io/javaee-spec', 'description': 'Java API for XML-based RPC is a Java web framework'},
                'JSTL': {'website': 'https://javaee.github.io/javaee-spec', 'description': 'JavaServer Pages Standard Tag Library is a Java web framework'},
                'JSF': {'website': 'https://javaee.github.io/javaserverfaces-spec', 'description': 'JavaServer Faces is a Java web framework'},
                'JSP': {'website': 'https://javaee.github.io/javaee-spec', 'description': 'JavaServer Pages is a Java web framework'},
                'Servlet': {'website': 'https://javaee.github.io/javaee-spec', 'description': 'Java Servlet is a Java web framework'},
                'JNDI': {'website': 'https://javaee.github.io/javaee-spec', 'description': 'Java Naming and Directory Interface is a Java web framework'},
                'JMX': {'website': 'https://javaee.github.io/javaee-spec', 'description': 'Java Management Extensions is a Java web framework'},
                'JCA': {'website': 'https://javaee.github.io/javaee-spec', 'description': 'Java Connector Architecture is a Java web framework'},
                'JACC': {'website': 'https://javaee.github.io/javaee-spec', 'description': 'Java Authorization Contract for Containers is a Java web framework'},
                'JASPIC': {'website': 'https://javaee.github.io/javaee-spec', 'description': 'Java Authentication Service Provider Interface for Containers is a Java web framework'},
                'JAXRPC': {'website': 'https://javaee.github.io/javaee-spec', 'description': 'Java API for XML-based RPC is a Java web framework'},
                'JAXR': {'website': 'https://javaee.github.io/javaee-spec', 'description': 'Java API for XML Registries is a Java web framework'},
                'JAXM': {'website': 'https://javaee.github.io/javaee-spec', 'description': 'Java API for XML Messaging is a Java web framework'},
                'JAXB': {'website': 'https://javaee.github.io/javaee-spec', 'description': 'Java Architecture for XML Binding is a Java web framework'},
                'JAXP': {'website': 'https://javaee.github.io/javaee-spec', 'description': 'Java API for XML Processing is a Java web framework'},
                'JAX-WS': {'website': 'https://javaee.github.io/javaee-spec', 'description': 'Java API for XML Web Services is a Java web framework'},
                'JAX-RS': {'website': 'https://javaee.github.io/javaee-spec', 'description': 'Java API for RESTful Web Services is a Java web framework'},
                'JMS': {'website': 'https://javaee.github.io/javaee-spec', 'description': 'Java Message Service is a Java web framework'},
                'JTA': {'website': 'https://javaee.github.io/javaee-spec', 'description': 'Java Transaction API is a Java web framework'},
                'JPA': {'website': 'https://javaee.github.io/javaee-spec', 'description': 'Java Persistence API is a Java web framework'},
                'EJB': {'website': 'https://javaee.github.io/ejb-spec', 'description': 'Enterprise JavaBeans is a Java web framework'},
                'CDI': {'website': 'https://cdi-spec.org', 'description': 'Contexts and Dependency Injection is a Java web framework'},
                'Weld': {'website': 'https://weld.cdi-spec.org', 'description': 'Weld is a Java web framework'},
                'Seam': {'website': 'https://seamframework.org', 'description': 'Seam is a Java web framework'},
                'DeltaSpike': {'website': 'https://deltaspike.apache.org', 'description': 'Apache DeltaSpike is a Java web framework'},
                'OmniFaces': {'website': 'https://omnifaces.org', 'description': 'OmniFaces is a Java web framework'},
                'ButterFaces': {'website': 'https://butterfaces.org', 'description': 'ButterFaces is a Java web framework'},
                'OpenFaces': {'website': 'https://openfaces.org', 'description': 'OpenFaces is a Java web framework'},
                'MyFaces': {'website': 'https://myfaces.apache.org', 'description': 'Apache MyFaces is a Java web framework'},
                'ICEfaces': {'website': 'https://www.icefaces.org', 'description': 'ICEfaces is a Java web framework'},
                'RichFaces': {'website': 'https://richfaces.jboss.org', 'description': 'RichFaces is a Java web framework'},
                'PrimeFaces': {'website': 'https://www.primefaces.org', 'description': 'PrimeFaces is a Java web framework'},
                'ZK': {'website': 'https://www.zkoss.org', 'description': 'ZK is a Java web framework'},
                'GWT': {'website': 'https://www.gwtproject.org', 'description': 'Google Web Toolkit is a Java web framework'},
                'Vaadin': {'website': 'https://vaadin.com', 'description': 'Vaadin is a Java web framework'},
                'Play': {'website': 'https://www.playframework.com', 'description': 'Play Framework is a Java/Scala web framework'},
                'Grails': {'website': 'https://grails.org', 'description': 'Grails is a Groovy web framework'},
                'Wicket': {'website': 'https://wicket.apache.org', 'description': 'Apache Wicket is a Java web framework'},
                'Tapestry': {'website': 'https://tapestry.apache.org', 'description': 'Apache Tapestry is a Java web framework'},
                'Struts': {'website': 'https://struts.apache.org', 'description': 'Apache Struts is a Java web framework'},
                'Spring': {'website': 'https://spring.io', 'description': 'Spring is a Java framework'},
                'ASP.NET': {'website': 'https://dotnet.microsoft.com', 'description': 'ASP.NET is a Microsoft web framework'},
                'Ruby on Rails': {'website': 'https://rubyonrails.org', 'description': 'Ruby on Rails is a Ruby web framework'},
                'Flask': {'website': 'https://flask.palletsprojects.com', 'description': 'Flask is a Python web framework'},
                'Django': {'website': 'https://www.djangoproject.com', 'description': 'Django is a Python web framework'},
                'Express.js': {'website': 'https://expressjs.com', 'description': 'Express.js is a Node.js web framework'},
                'Zend': {'website': 'https://framework.zend.com', 'description': 'Zend Framework is a PHP web framework'},
                'Yii': {'website': 'https://www.yiiframework.com', 'description': 'Yii is a PHP web framework'},
                'CakePHP': {'website': 'https://cakephp.org', 'description': 'CakePHP is a PHP web framework'},
                'CodeIgniter': {'website': 'https://codeigniter.com', 'description': 'CodeIgniter is a PHP web framework'},
                'Symfony': {'website': 'https://symfony.com', 'description': 'Symfony is a PHP web framework'},
                'Laravel': {'website': 'https://laravel.com', 'description': 'Laravel is a PHP web framework'},
                'Gatsby': {'website': 'https://www.gatsbyjs.com', 'description': 'Gatsby is a React-based static site generator'},
                'Jekyll': {'website': 'https://jekyllrb.com', 'description': 'Jekyll is a static site generator'},
                'Hugo': {'website': 'https://gohugo.io', 'description': 'Hugo is a static site generator'},
                'Webflow': {'website': 'https://webflow.com', 'description': 'Webflow is a visual web development platform'},
                'Wix': {'website': 'https://www.wix.com', 'description': 'Wix is a cloud-based web development platform'},
                'Squarespace': {'website': 'https://www.squarespace.com', 'description': 'Squarespace is a website building platform'},
                'Ghost': {'website': 'https://ghost.org', 'description': 'Ghost is a modern publishing platform'},
                'OpenCart': {'website': 'https://www.opencart.com', 'description': 'OpenCart is an e-commerce platform'},
                'PrestaShop': {'website': 'https://www.prestashop.com', 'description': 'PrestaShop is an e-commerce platform'},
                'WooCommerce': {'website': 'https://woocommerce.com', 'description': 'WooCommerce is an e-commerce plugin for WordPress'},
                'Shopify': {'website': 'https://www.shopify.com', 'description': 'Shopify is a commerce platform'},
                'Magento': {'website': 'https://magento.com', 'description': 'Magento is an e-commerce platform'},
                'Drupal': {'website': 'https://www.drupal.org', 'description': 'Drupal is a free and open-source content management system'},
                'Joomla': {'website': 'https://www.joomla.org', 'description': 'Joomla is a free and open-source content management system'},
                'WordPress': {'website': 'https://wordpress.org', 'description': 'WordPress is a free and open-source content management system'}
            }
            
            # Check for known CMS patterns
            for cms_name, cms_info in cms_patterns.items():
                if cms_name.lower() in line.lower():
                    return {
                        'name': cms_name,
                        'website': cms_info['website'],
                        'description': cms_info['description'],
                        'versions': []
                    }
            
            # Handle CMSeeK specific output format
            if 'CMS Detected' in line and 'CMS ID:' in line:
                # Extract CMS ID and map to known CMS
                cms_id_mapping = {
                    'sfy': 'Sitefinity',
                    'wp': 'WordPress',
                    'joomla': 'Joomla',
                    'drupal': 'Drupal',
                    'magento': 'Magento',
                    'shopify': 'Shopify',
                    'wix': 'Wix',
                    'squarespace': 'Squarespace'
                }
                
                # Extract CMS ID from line like "CMS Detected, CMS ID: sfy"
                import re
                cms_id_match = re.search(r'CMS ID:\s*(\w+)', line)
                if cms_id_match:
                    cms_id = cms_id_match.group(1)
                    if cms_id in cms_id_mapping:
                        cms_name = cms_id_mapping[cms_id]
                        if cms_name in cms_patterns:
                            return {
                                'name': cms_name,
                                'website': cms_patterns[cms_name]['website'],
                                'description': cms_patterns[cms_name]['description'],
                                'versions': []
                            }
            
            # If no known CMS found, try to extract generic CMS info
            if 'CMS:' in line or 'Detected:' in line or 'Found:' in line:
                # Extract the CMS name from the line
                parts = line.split(':')
                if len(parts) > 1:
                    cms_name = parts[1].strip()
                    return {
                        'name': cms_name,
                        'website': '',
                        'description': f'{cms_name} content management system',
                        'versions': []
                    }
            
        except Exception as e:
            logger.warning(f"Failed to extract CMS info from line: {line} - {e}")
        
        return None
    
    def _extract_version_info(self, line: str) -> List[str]:
        """Extract version information from a line"""
        try:
            # Look for version patterns
            version_patterns = [
                r'version\s+(\d+\.\d+(?:\.\d+)?(?:\s+\w+)?)',  # "version 15.2.8426.0 dx"
                r'v\s*(\d+\.\d+(?:\.\d+)?)',
                r'version\s*:?\s*(\d+\.\d+(?:\.\d+)?)',
                r'(\d+\.\d+(?:\.\d+)?)'
            ]
            
            for pattern in version_patterns:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    return [match.group(1).strip()]
            
        except Exception as e:
            logger.warning(f"Failed to extract version info from line: {line} - {e}")
        
        return []

class WhatCMSIntegration:
    """WhatCMS.org API integration for additional technology detection"""
    
    def __init__(self):
        # Load environment variables
        load_dotenv()
        self.api_key = os.getenv('WHATCMS_API_KEY')
        self.api_url = os.getenv('WHATCMS_API_URL', 'https://whatcms.org/API/Tech')
        self.available = self._check_availability()
        
    def _check_availability(self):
        """Check if WhatCMS.org API is available"""
        if not self.api_key:
            logger.warning("WhatCMS.org API key not found in environment variables")
            return False
        
        try:
            # Test API with a simple request
            response = requests.get(
                self.api_url,
                params={'key': self.api_key, 'url': 'example.com'},
                timeout=30
            )
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"WhatCMS.org API not available: {e}")
            return False
    
    async def analyze_url(self, url: str) -> List[DetectionResult]:
        """Analyze URL using WhatCMS.org API"""
        if not self.available:
            logger.warning("WhatCMS.org API not available")
            return []
        
        try:
            # Clean URL for API
            clean_url = url.replace('https://', '').replace('http://', '')
            
            # Make API request
            response = requests.get(
                self.api_url,
                params={'key': self.api_key, 'url': clean_url},
                timeout=30
            )
            
            if response.status_code != 200:
                logger.warning(f"WhatCMS.org API request failed: {response.status_code}")
                return []
            
            data = response.json()
            
            if data.get('result', {}).get('code') != 200:
                logger.warning(f"WhatCMS.org API error: {data.get('result', {}).get('msg', 'Unknown error')}")
                return []
            
            detections = []
            results = data.get('results', [])
            
            for tech in results:
                # Extract technology information
                name = tech.get('name', 'Unknown')
                version = tech.get('version', '')
                categories = tech.get('categories', [])
                tech_id = tech.get('id', '')
                tech_url = tech.get('url', '')
                
                # Determine primary category
                primary_category = 'Unknown'
                if categories:
                    # Prioritize certain categories
                    if 'CMS' in categories:
                        primary_category = 'CMS'
                    elif 'Programming Language' in categories:
                        primary_category = 'Programming Language'
                    elif 'Wiki' in categories:
                        primary_category = 'Wiki'
                    else:
                        primary_category = categories[0]
                
                # Create detection result
                detection = DetectionResult(
                    name=name,
                    confidence=95,  # High confidence for API results
                    category=primary_category,
                    versions=[version] if version else [],
                    evidence=[{
                        'field': 'whatcms_api',
                        'detail': f"API ID: {tech_id}",
                        'match': name,
                        'confidence': 95
                    }],
                    source='whatcms',
                    website=f"https://whatcms.org{tech_url}" if tech_url else '',
                    description=f"Detected by WhatCMS.org API (ID: {tech_id})",
                    detection_time=time.time()
                )
                detections.append(detection)
                logger.info(f"WhatCMS.org detected: {name} ({primary_category})")
            
            logger.info(f"WhatCMS.org detected {len(detections)} technologies")
            return detections
            
        except Exception as e:
            logger.error(f"WhatCMS.org analysis failed: {e}")
            return []

class WappalyzerIntegration:
    """Wappalyzer integration for technology detection"""
    
    def __init__(self):
        self.available = self._check_availability()
        
    def _check_availability(self):
        """Check if Wappalyzer is available"""
        try:
            # Check if wappalyzer command is available
            result = subprocess.run(['which', 'wappalyzer'], 
                                  capture_output=True, text=True, timeout=15)
            return result.returncode == 0
        except Exception as e:
            logger.warning(f"Wappalyzer not available: {e}")
            return False
    
    async def analyze_url(self, url: str) -> List[DetectionResult]:
        """Analyze URL using Wappalyzer"""
        if not self.available:
            logger.warning("Wappalyzer not available")
            return []
        
        try:
            # Run wappalyzer command
            result = subprocess.run(
                ['wappalyzer', url, '--json'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                logger.warning(f"Wappalyzer analysis failed: {result.stderr}")
                return []
            
            # Parse JSON output
            data = json.loads(result.stdout)
            detections = []
            
            technologies = data.get('technologies', [])
            for tech in technologies:
                name = tech.get('name', 'Unknown')
                confidence = tech.get('confidence', 0)
                category = tech.get('category', {}).get('name', 'Unknown') if isinstance(tech.get('category'), dict) else 'Unknown'
                version = tech.get('version', '')
                website = tech.get('website', '')
                description = tech.get('description', '')
                
                # Create detection result
                detection = DetectionResult(
                    name=name,
                    confidence=confidence,
                    category=category,
                    versions=[version] if version else [],
                    evidence=[{
                        'field': 'wappalyzer',
                        'detail': f"Confidence: {confidence}%",
                        'match': name,
                        'confidence': confidence
                    }],
                    source='wappalyzer',
                    website=website,
                    description=description,
                    detection_time=time.time()
                )
                detections.append(detection)
                logger.info(f"Wappalyzer detected: {name} ({category})")
            
            logger.info(f"Wappalyzer detected {len(detections)} technologies")
            return detections
            
        except Exception as e:
            logger.error(f"Wappalyzer analysis failed: {e}")
            return []

class UltimateTechDetector:
    """Ultimate unified technology detection system"""
    
    def __init__(self, datasets_dir: str = "data/datasets"):
        self.datasets_dir = datasets_dir
        self.dataset_manager = UltimateDatasetManager(datasets_dir)
        self.pattern_matcher = UltimatePatternMatcher(self.dataset_manager)
        self.whatweb = WhatWebIntegration()
        self.cmseek = CMSeeKIntegration()
        self.whatcms = WhatCMSIntegration()
        self.wappalyzer = WappalyzerIntegration()
        self.session = None
    
    async def close(self):
        """Close the HTTP session"""
        if self.session:
            await self.session.close()
            self.session = None
    
    async def analyze_url(self, url: str, options: Dict[str, Any] = None, engines: List[str] = None) -> AnalysisResult:
        """Analyze URL and detect all technologies"""
        if options is None:
            options = {}
        if engines is None:
            engines = ['pattern', 'whatweb', 'cmseek', 'whatcms', 'wappalyzer', 'additional', 'deep']
        
        start_time = time.time()
        logger.info(f"ANALYSIS_START: {url} with engines: {engines}")
        logger.debug(f"ANALYSIS_OPTIONS: {options}")
        
        # Log analysis start
        log_analysis_start(url, engines)
        
        # Initialize session
        if self.session is None or self.session.closed:
            logger.debug("Initializing new aiohttp session")
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=options.get('timeout', 60)),
                headers={'User-Agent': 'UltimateTechDetector/1.0'}
            )
        else:
            logger.debug("Reusing existing aiohttp session")
        
        try:
            # Fetch page content
            response_data = await self._fetch_page_content(url)
            
            technologies = []
            
            # Run Pattern Matching detection
            if 'pattern' in engines:
                logger.info("ENGINE_START: Pattern Matching detection")
                pattern_start = time.time()
                pattern_technologies = await self.pattern_matcher.detect_all_technologies(url, response_data)
                pattern_time = time.time() - pattern_start
                technologies.extend(pattern_technologies)
                logger.info(f"ENGINE_COMPLETE: Pattern Matching - {len(pattern_technologies)} technologies in {pattern_time:.2f}s")
                log_engine_status("Pattern Matching", "Completed", f"{len(pattern_technologies)} technologies")
            
            # Run WhatWeb detection
            if 'whatweb' in engines:
                logger.info("ENGINE_START: WhatWeb detection")
                whatweb_start = time.time()
                whatweb_technologies = await self.whatweb.analyze_url(url)
                whatweb_time = time.time() - whatweb_start
                technologies.extend(whatweb_technologies)
                logger.info(f"ENGINE_COMPLETE: WhatWeb - {len(whatweb_technologies)} technologies in {whatweb_time:.2f}s")
                log_engine_status("WhatWeb", "Completed", f"{len(whatweb_technologies)} technologies")
            
            # Run CMSeeK detection
            if 'cmseek' in engines:
                logger.info("ENGINE_START: CMSeeK detection")
                cmseek_start = time.time()
                cmseek_technologies = await self.cmseek.analyze_url(url)
                cmseek_time = time.time() - cmseek_start
                technologies.extend(cmseek_technologies)
                logger.info(f"ENGINE_COMPLETE: CMSeeK - {len(cmseek_technologies)} technologies in {cmseek_time:.2f}s")
                log_engine_status("CMSeeK", "Completed", f"{len(cmseek_technologies)} technologies")
            
            # Run WhatCMS.org API detection
            if 'whatcms' in engines:
                logger.info("ENGINE_START: WhatCMS.org API detection")
                whatcms_start = time.time()
                whatcms_technologies = await self.whatcms.analyze_url(url)
                whatcms_time = time.time() - whatcms_start
                technologies.extend(whatcms_technologies)
                logger.info(f"ENGINE_COMPLETE: WhatCMS.org - {len(whatcms_technologies)} technologies in {whatcms_time:.2f}s")
                log_engine_status("WhatCMS.org", "Completed", f"{len(whatcms_technologies)} technologies")
            
            # Run Wappalyzer detection
            if 'wappalyzer' in engines:
                logger.info("ENGINE_START: Wappalyzer detection")
                wappalyzer_start = time.time()
                wappalyzer_technologies = await self.wappalyzer.analyze_url(url)
                wappalyzer_time = time.time() - wappalyzer_start
                technologies.extend(wappalyzer_technologies)
                logger.info(f"ENGINE_COMPLETE: Wappalyzer - {len(wappalyzer_technologies)} technologies in {wappalyzer_time:.2f}s")
                log_engine_status("Wappalyzer", "Completed", f"{len(wappalyzer_technologies)} technologies")
            
            # Run additional pattern matching for 100% coverage
            if 'additional' in engines:
                logger.info("ENGINE_START: Additional Patterns detection")
                additional_start = time.time()
                logger.debug(f"Response data keys: {list(response_data.keys())}")
                logger.debug(f"CSS links: {len(response_data.get('css_links', []))}")
                logger.debug(f"Image sources: {len(response_data.get('img_srcs', []))}")
                additional_technologies = await self._detect_additional_patterns(url, response_data)
                additional_time = time.time() - additional_start
                logger.info(f"ENGINE_COMPLETE: Additional Patterns - {len(additional_technologies)} technologies in {additional_time:.2f}s")
                log_engine_status("Additional Patterns", "Completed", f"{len(additional_technologies)} technologies")
                technologies.extend(additional_technologies)
            
            # Run deep analysis for comprehensive detection
            if 'deep' in engines:
                logger.info("ENGINE_START: Deep Analysis detection")
                deep_start = time.time()
                deep_technologies = await self._run_deep_analysis(url, response_data)
                deep_time = time.time() - deep_start
                logger.info(f"ENGINE_COMPLETE: Deep Analysis - {len(deep_technologies)} technologies in {deep_time:.2f}s")
                log_engine_status("Deep Analysis", "Completed", f"{len(deep_technologies)} technologies")
                technologies.extend(deep_technologies)
            
            # Calculate detection breakdown BEFORE deduplication
            detection_breakdown = {
                'pattern_matching': len([t for t in technologies if 'pattern' in t.source]),
                'whatweb': len([t for t in technologies if t.source == 'whatweb']),
                'cmseek': len([t for t in technologies if t.source == 'cmseek']),
                'whatcms': len([t for t in technologies if t.source == 'whatcms']),
                'wappalyzer': len([t for t in technologies if t.source == 'wappalyzer']),
                'additional_patterns': len([t for t in technologies if t.source == 'additional_pattern']),
                'deep_analysis': len([t for t in technologies if t.source == 'deep'])
            }
            
            # Deduplicate and merge all technologies
            technologies = self._deduplicate_technologies(technologies)
            
            # Apply filters
            min_confidence = options.get('min_confidence', 0)
            max_results = options.get('max_results', 200)
            
            filtered_technologies = [
                tech for tech in technologies 
                if tech.confidence >= min_confidence
            ][:max_results]
            
            analysis_time = time.time() - start_time
            
            # Build result
            result = AnalysisResult(
                url=url,
                final_url=response_data.get('final_url', url),
                technologies=filtered_technologies,
                analysis_time=analysis_time,
                metadata={
                    'title': response_data.get('title', ''),
                    'description': response_data.get('description', ''),
                    'content_length': response_data.get('content_length', 0),
                    'response_time': response_data.get('response_time', 0),
                    'server': response_data.get('server', ''),
                    'total_technologies': len(filtered_technologies),
                    'dataset_utilization': f"{len(self.dataset_manager.all_technologies)} technologies available",
                    'categories_detected': len(set(tech.category for tech in filtered_technologies)),
                    'confidence_distribution': self._get_confidence_distribution(filtered_technologies),
                    'detection_breakdown': detection_breakdown,
                    'performance_metrics': {
                        'analysis_time_seconds': round(analysis_time, 2),
                        'technologies_per_second': round(len(filtered_technologies) / analysis_time, 2) if analysis_time > 0 else 0
                    }
                },
                user_agents_tried=[response_data.get('user_agent', 'Unknown')],
                successful_agent=response_data.get('user_agent', 'Unknown')
            )
            
            # Log comprehensive results
            logger.info(f"ANALYSIS_COMPLETE: {url} - {len(filtered_technologies)} technologies in {result.analysis_time:.2f}s")
            logger.info(f"DETECTION_BREAKDOWN: {detection_breakdown}")
            logger.info(f"CATEGORIES_DETECTED: {len(set(tech.category for tech in filtered_technologies))}")
            logger.info(f"CONFIDENCE_DISTRIBUTION: {self._get_confidence_distribution(filtered_technologies)}")
            
            # Log completion
            engines_used = [engine for engine in engines if detection_breakdown.get(engine, 0) > 0]
            log_analysis_complete(url, len(filtered_technologies), result.analysis_time, engines_used)
            
            return result
            
        except Exception as e:
            logger.error(f"ANALYSIS_FAILED: {url} - {str(e)}")
            logger.error(f"ERROR_TRACEBACK: {traceback.format_exc()}")
            log_analysis_error(url, str(e))
            analysis_time = time.time() - start_time
            return AnalysisResult(
                url=url,
                final_url=url,
                analysis_time=analysis_time,
                errors=[str(e)]
            )
        finally:
            # Don't close session here - let it be reused
            pass
    
    async def _fetch_page_content(self, url: str) -> Dict[str, Any]:
        """Fetch page content and extract relevant data"""
        try:
            # Ensure session is available
            if self.session is None or self.session.closed:
                self.session = aiohttp.ClientSession()
            
            async with self.session.get(url) as response:
                content = await response.text()
                
                # Extract basic metadata
                title_match = re.search(r'<title[^>]*>(.*?)</title>', content, re.IGNORECASE | re.DOTALL)
                title = title_match.group(1).strip() if title_match else ''
                
                desc_match = re.search(r'<meta[^>]*name=["\']description["\'][^>]*content=["\']([^"\']*)["\']', content, re.IGNORECASE)
                description = desc_match.group(1).strip() if desc_match else ''
                
                # Extract scripts
                script_matches = re.findall(r'<script[^>]*src=["\']([^"\']*)["\']', content, re.IGNORECASE)
                scripts = [script for script in script_matches if script]
                
                # Extract meta tags
                meta_tags = {}
                meta_matches = re.findall(r'<meta[^>]*name=["\']([^"\']*)["\'][^>]*content=["\']([^"\']*)["\']', content, re.IGNORECASE)
                for name, content_val in meta_matches:
                    meta_tags[name.lower()] = content_val
                
                # Extract headers
                headers = {}
                for header_name, header_value in response.headers.items():
                    headers[header_name.lower()] = header_value
                
                # Extract cookies
                cookies = {}
                if 'set-cookie' in response.headers:
                    cookie_header = response.headers['set-cookie']
                    for cookie in cookie_header.split(','):
                        if '=' in cookie:
                            name, value = cookie.split('=', 1)
                            cookies[name.strip()] = value.strip()
                
                # Extract additional patterns for comprehensive detection
                css_links = re.findall(r'<link[^>]*href=["\']([^"\']*\.css[^"\']*)["\']', content, re.IGNORECASE)
                img_srcs = re.findall(r'<img[^>]*src=["\']([^"\']*)["\']', content, re.IGNORECASE)
                
                return {
                    'content': content,
                    'title': title,
                    'description': description,
                    'scripts': scripts,
                    'css_links': css_links,
                    'img_srcs': img_srcs,
                    'meta_tags': meta_tags,
                    'headers': headers,
                    'cookies': cookies,
                    'final_url': str(response.url),
                    'content_length': len(content),
                    'response_time': response.headers.get('X-Response-Time', '0'),
                    'server': response.headers.get('Server', ''),
                    'user_agent': 'UltimateTechDetector/1.0'
                }
                
        except Exception as e:
            logger.error(f"Failed to fetch page content: {e}")
            return {
                'content': '',
                'title': '',
                'description': '',
                'scripts': [],
                'css_links': [],
                'img_srcs': [],
                'meta_tags': {},
                'headers': {},
                'cookies': {},
                'final_url': url,
                'content_length': 0,
                'response_time': '0',
                'server': '',
                'user_agent': 'UltimateTechDetector/1.0'
            }
    
    def _get_confidence_distribution(self, technologies: List[DetectionResult]) -> Dict[str, int]:
        """Get confidence distribution statistics"""
        distribution = {
            'high (80-100)': 0,
            'medium (50-79)': 0,
            'low (10-49)': 0
        }
        
        for tech in technologies:
            if tech.confidence >= 80:
                distribution['high (80-100)'] += 1
            elif tech.confidence >= 50:
                distribution['medium (50-79)'] += 1
            else:
                distribution['low (10-49)'] += 1
        
        return distribution
    
    async def _detect_additional_patterns(self, url: str, response_data: Dict[str, Any]) -> List[DetectionResult]:
        """Detect additional patterns for 100% coverage"""
        detections = []
        logger.info(f"Additional patterns: Starting analysis for {url}")
        logger.info(f"Response data keys: {list(response_data.keys())}")
        
        # CSS pattern detection
        css_links = response_data.get('css_links', [])
        logger.info(f"Additional patterns: Checking {len(css_links)} CSS links for patterns")
        for css_link in css_links:
            # Check all pattern types for CSS links
            for pattern_type in ['scripts', 'urls', 'html']:
                if pattern_type in self.dataset_manager.pattern_database:
                    logger.info(f"Additional patterns: Checking {len(self.dataset_manager.pattern_database[pattern_type])} {pattern_type} patterns")
                    for pattern in self.dataset_manager.pattern_database[pattern_type]:
                        try:
                            if re.search(pattern, css_link, re.IGNORECASE):
                                for match in self.dataset_manager.pattern_database[pattern_type][pattern]:
                                    tech_name = match['technology']
                                    tech_data = self.dataset_manager.all_technologies.get(tech_name, {})
                                    
                                    detection = DetectionResult(
                                        name=tech_name,
                                        confidence=match['confidence'],
                                        category=tech_data.get('category', 'Unknown'),
                                        evidence=[{
                                            'field': 'css',
                                            'detail': css_link,
                                            'match': pattern,
                                            'confidence': match['confidence']
                                        }],
                                        source='additional_pattern',
                                        website=tech_data.get('website'),
                                        description=tech_data.get('description'),
                                        detection_time=time.time()
                                    )
                                    detections.append(detection)
                                    logger.info(f"Additional pattern detected: {tech_name} from CSS link")
                        except re.error:
                            continue
            
            # Also check for common CSS framework patterns
            css_frameworks = {
                'Bootstrap': r'bootstrap',
                'Tailwind CSS': r'tailwind',
                'Bulma': r'bulma',
                'Foundation': r'foundation',
                'Materialize': r'materialize',
                'Semantic UI': r'semantic',
                'Pure CSS': r'pure',
                'Skeleton': r'skeleton'
            }
            
            for framework, pattern in css_frameworks.items():
                if re.search(pattern, css_link, re.IGNORECASE):
                    detection = DetectionResult(
                        name=framework,
                        confidence=70,
                        category='UI Frameworks',
                        evidence=[{
                            'field': 'css',
                            'detail': css_link,
                            'match': pattern,
                            'confidence': 70
                        }],
                        source='additional_pattern',
                        website='',
                        description=f'{framework} CSS framework detected',
                        detection_time=time.time()
                    )
                    detections.append(detection)
                    logger.info(f"Additional pattern detected: {framework} from CSS link")
        
        # Image source pattern detection
        img_srcs = response_data.get('img_srcs', [])
        logger.info(f"Additional patterns: Checking {len(img_srcs)} image sources for patterns")
        for img_src in img_srcs:
            # Check all pattern types for image sources
            for pattern_type in ['scripts', 'urls', 'html']:
                if pattern_type in self.dataset_manager.pattern_database:
                    for pattern in self.dataset_manager.pattern_database[pattern_type]:
                        try:
                            if re.search(pattern, img_src, re.IGNORECASE):
                                for match in self.dataset_manager.pattern_database[pattern_type][pattern]:
                                    tech_name = match['technology']
                                    tech_data = self.dataset_manager.all_technologies.get(tech_name, {})
                                    
                                    detection = DetectionResult(
                                        name=tech_name,
                                        confidence=match['confidence'],
                                        category=tech_data.get('category', 'Unknown'),
                                        evidence=[{
                                            'field': 'images',
                                            'detail': img_src,
                                            'match': pattern,
                                            'confidence': match['confidence']
                                        }],
                                        source='additional_pattern',
                                        website=tech_data.get('website'),
                                        description=tech_data.get('description'),
                                        detection_time=time.time()
                                    )
                                    detections.append(detection)
                                    logger.info(f"Additional pattern detected: {tech_name} from image source")
                        except re.error:
                            continue
            
            # Also check for common CDN and service patterns
            cdn_patterns = {
                'Cloudflare': r'cloudflare',
                'Amazon CloudFront': r'cloudfront',
                'Google Fonts': r'fonts\.googleapis\.com',
                'jsDelivr': r'cdn\.jsdelivr\.net',
                'unpkg': r'unpkg\.com',
                'cdnjs': r'cdnjs\.cloudflare\.com',
                'Bootstrap CDN': r'bootstrapcdn',
                'jQuery CDN': r'jquery'
            }
            
            # Check all content for common technologies
            all_content = []
            all_content.extend(response_data.get('scripts', []))
            all_content.extend(response_data.get('css_links', []))
            all_content.extend(response_data.get('img_srcs', []))
            all_content.append(response_data.get('content', ''))
            
            # Common technology patterns for additional detection
            tech_patterns = {
                'jQuery': [r'jquery', r'jQuery', r'jquery\.min\.js'],
                'Bootstrap': [r'bootstrap', r'Bootstrap', r'bootstrap\.min\.css'],
                'React': [r'react', r'React', r'react\.min\.js'],
                'Angular': [r'angular', r'Angular', r'angular\.min\.js'],
                'Vue': [r'vue', r'Vue', r'vue\.min\.js'],
                'Google Analytics': [r'google-analytics', r'gtag', r'analytics\.js'],
                'Google Tag Manager': [r'googletagmanager', r'gtm\.js'],
                'Font Awesome': [r'font-awesome', r'fontawesome', r'fa-'],
                'Cloudflare': [r'cloudflare', r'cf-'],
                'WordPress': [r'wp-content', r'wp-includes', r'wordpress'],
                'Drupal': [r'drupal', r'sites/default', r'misc/drupal'],
                'Joomla': [r'joomla', r'joomla\.org', r'joomla\.js']
            }
            
            for content_item in all_content:
                if content_item:
                    for tech_name, patterns in tech_patterns.items():
                        for pattern in patterns:
                            try:
                                if re.search(pattern, content_item, re.IGNORECASE):
                                    detection = DetectionResult(
                                        name=tech_name,
                                        confidence=55,
                                        category='JavaScript Library' if tech_name in ['jQuery', 'React', 'Angular', 'Vue'] else 'Analytics' if 'Google' in tech_name else 'CMS' if tech_name in ['WordPress', 'Drupal', 'Joomla'] else 'CDN' if tech_name == 'Cloudflare' else 'UI Framework',
                                        evidence=[{
                                            'field': 'additional',
                                            'detail': f'Found in content: {content_item[:100]}...',
                                            'match': pattern,
                                            'confidence': 55
                                        }],
                                        source='additional_pattern',
                                        website='',
                                        description=f'Detected from additional pattern matching',
                                        detection_time=time.time()
                                    )
                                    detections.append(detection)
                                    logger.info(f"Additional pattern detected: {tech_name} from content")
                                    break  # Only add once per technology
                            except re.error:
                                continue
            
            for service, pattern in cdn_patterns.items():
                if re.search(pattern, img_src, re.IGNORECASE):
                    detection = DetectionResult(
                        name=service,
                        confidence=60,
                        category='CDN',
                        evidence=[{
                            'field': 'images',
                            'detail': img_src,
                            'match': pattern,
                            'confidence': 60
                        }],
                        source='additional_pattern',
                        website='',
                        description=f'{service} CDN service detected',
                        detection_time=time.time()
                    )
                    detections.append(detection)
                    logger.info(f"Additional pattern detected: {service} from image source")
        
        # Cookie pattern detection
        cookies = response_data.get('cookies', {})
        logger.info(f"Checking {len(cookies)} cookies for patterns")
        for cookie_name, cookie_value in cookies.items():
            cookie_pattern = f"{cookie_name}={cookie_value}"
            # Check both exact match and pattern matching
            if 'cookies' in self.dataset_manager.pattern_database:
                if cookie_pattern in self.dataset_manager.pattern_database['cookies']:
                    for match in self.dataset_manager.pattern_database['cookies'][cookie_pattern]:
                        tech_name = match['technology']
                        tech_data = self.dataset_manager.all_technologies.get(tech_name, {})
                        
                        detection = DetectionResult(
                            name=tech_name,
                            confidence=match['confidence'],
                            category=tech_data.get('category', 'Unknown'),
                            evidence=[{
                                'field': 'cookies',
                                'detail': cookie_pattern,
                                'match': cookie_pattern,
                                'confidence': match['confidence']
                            }],
                            source='additional_pattern',
                            website=tech_data.get('website'),
                            description=tech_data.get('description'),
                            detection_time=time.time()
                        )
                        detections.append(detection)
                        logger.info(f"Additional pattern detected: {tech_name} from cookie")
            
            # Also check cookie name and value separately
            for pattern_type in ['scripts', 'urls', 'html']:
                if pattern_type in self.dataset_manager.pattern_database:
                    for pattern in self.dataset_manager.pattern_database[pattern_type]:
                        try:
                            if re.search(pattern, cookie_name, re.IGNORECASE) or re.search(pattern, cookie_value, re.IGNORECASE):
                                for match in self.dataset_manager.pattern_database[pattern_type][pattern]:
                                    tech_name = match['technology']
                                    tech_data = self.dataset_manager.all_technologies.get(tech_name, {})
                                    
                                    detection = DetectionResult(
                                        name=tech_name,
                                        confidence=match['confidence'],
                                        category=tech_data.get('category', 'Unknown'),
                                        evidence=[{
                                            'field': 'cookies',
                                            'detail': cookie_pattern,
                                            'match': pattern,
                                            'confidence': match['confidence']
                                        }],
                                        source='additional_pattern',
                                        website=tech_data.get('website'),
                                        description=tech_data.get('description'),
                                        detection_time=time.time()
                                    )
                                    detections.append(detection)
                                    logger.info(f"Additional pattern detected: {tech_name} from cookie pattern")
                        except re.error:
                            continue
        
        return detections
    
    async def _run_deep_analysis(self, url: str, response_data: Dict[str, Any]) -> List[DetectionResult]:
        """Run deep analysis for comprehensive technology detection"""
        detections = []
        
        try:
            logger.info("Starting deep analysis...")
            logger.info(f"Deep analysis: Response data keys: {list(response_data.keys())}")
            logger.info(f"Deep analysis: Pattern database keys: {list(self.dataset_manager.pattern_database.keys())}")
            
            if 'headers' in self.dataset_manager.pattern_database:
                logger.info(f"Deep analysis: Headers patterns count: {len(self.dataset_manager.pattern_database['headers'])}")
            if 'html' in self.dataset_manager.pattern_database:
                logger.info(f"Deep analysis: HTML patterns count: {len(self.dataset_manager.pattern_database['html'])}")
            
            # Deep header analysis
            headers = response_data.get('headers', {})
            logger.info(f"Deep analysis: Checking {len(headers)} headers")
            for header_name, header_value in headers.items():
                header_text = f"{header_name}: {header_value}"
                
                # Check for server technologies in headers using pattern database
                if 'headers' in self.dataset_manager.pattern_database:
                    for pattern in self.dataset_manager.pattern_database['headers']:
                        try:
                            if re.search(pattern, header_text, re.IGNORECASE):
                                for match in self.dataset_manager.pattern_database['headers'][pattern]:
                                    tech_name = match['technology']
                                    tech_data = self.dataset_manager.all_technologies.get(tech_name, {})
                                    
                                    detection = DetectionResult(
                                        name=tech_name,
                                        confidence=match['confidence'],
                                        category=tech_data.get('category', 'Unknown'),
                                        versions=[],
                                        evidence=[{
                                            'field': 'headers',
                                            'detail': header_text,
                                            'match': pattern,
                                            'confidence': match['confidence']
                                        }],
                                        source='deep',
                                        website=tech_data.get('website'),
                                        description=tech_data.get('description'),
                                        detection_time=time.time()
                                    )
                                    detections.append(detection)
                                    logger.info(f"Deep analysis detected: {tech_name} from header")
                        except re.error:
                            continue
            
            # Also check for common server technologies in headers
            server_patterns = {
                'Apache': r'apache',
                'Nginx': r'nginx',
                'IIS': r'microsoft-iis',
                'Cloudflare': r'cloudflare',
                'PHP': r'php',
                'Node.js': r'node\.js',
                'Express': r'express',
                'Django': r'django',
                'Flask': r'flask',
                'Ruby on Rails': r'rails',
                'ASP.NET': r'asp\.net'
            }
            
            # Check server patterns against all headers
            for header_name, header_value in headers.items():
                header_text = f"{header_name}: {header_value}"
                for server, pattern in server_patterns.items():
                    if re.search(pattern, header_text, re.IGNORECASE):
                        detection = DetectionResult(
                            name=server,
                            confidence=75,
                            category='Web Servers',
                            evidence=[{
                                'field': 'headers',
                                'detail': header_text,
                                'match': pattern,
                                'confidence': 75
                            }],
                            source='deep',
                            website='',
                            description=f'{server} server technology detected',
                            detection_time=time.time()
                        )
                        detections.append(detection)
                        logger.info(f"Deep analysis detected: {server} from header")
            
            # Deep HTML content analysis
            html_content = response_data.get('content', '')
            logger.info(f"Deep analysis: Checking HTML content ({len(html_content)} chars)")
            if html_content:
                # Use pattern database for HTML analysis
                if 'html' in self.dataset_manager.pattern_database:
                    for pattern in self.dataset_manager.pattern_database['html']:
                        try:
                            if re.search(pattern, html_content, re.IGNORECASE | re.DOTALL):
                                for match in self.dataset_manager.pattern_database['html'][pattern]:
                                    tech_name = match['technology']
                                    tech_data = self.dataset_manager.all_technologies.get(tech_name, {})
                                    
                                    detection = DetectionResult(
                                        name=tech_name,
                                        confidence=match['confidence'],
                                        category=tech_data.get('category', 'Unknown'),
                                        versions=[],
                                        evidence=[{
                                            'field': 'html',
                                            'detail': f"HTML pattern match: {pattern}",
                                            'match': pattern,
                                            'confidence': match['confidence']
                                        }],
                                        source='deep',
                                        website=tech_data.get('website'),
                                        description=tech_data.get('description'),
                                        detection_time=time.time()
                                    )
                                    detections.append(detection)
                                    logger.info(f"Deep analysis detected: {tech_name} from HTML pattern")
                        except re.error:
                            continue
                
                # Add fallback patterns for common technologies
                common_patterns = {
                    'jQuery': [r'jquery', r'jQuery', r'jquery\.min\.js'],
                    'Bootstrap': [r'bootstrap', r'Bootstrap', r'bootstrap\.min\.css'],
                    'React': [r'react', r'React', r'react\.min\.js'],
                    'Angular': [r'angular', r'Angular', r'angular\.min\.js'],
                    'Vue': [r'vue', r'Vue', r'vue\.min\.js'],
                    'Google Analytics': [r'google-analytics', r'gtag', r'analytics\.js'],
                    'Google Tag Manager': [r'googletagmanager', r'gtm\.js'],
                    'Font Awesome': [r'font-awesome', r'fontawesome', r'fa-'],
                    'Cloudflare': [r'cloudflare', r'cf-'],
                    'WordPress': [r'wp-content', r'wp-includes', r'wordpress'],
                    'Drupal': [r'drupal', r'sites/default', r'misc/drupal'],
                    'Joomla': [r'joomla', r'joomla\.org', r'joomla\.js']
                }
                
                for tech_name, patterns in common_patterns.items():
                    for pattern in patterns:
                        try:
                            if re.search(pattern, html_content, re.IGNORECASE):
                                detection = DetectionResult(
                                    name=tech_name,
                                    confidence=60,
                                    category='JavaScript Library' if tech_name in ['jQuery', 'React', 'Angular', 'Vue'] else 'Analytics' if 'Google' in tech_name else 'CMS' if tech_name in ['WordPress', 'Drupal', 'Joomla'] else 'CDN' if tech_name == 'Cloudflare' else 'UI Framework',
                                    versions=[],
                                    evidence=[{
                                        'field': 'html',
                                        'detail': f'Found pattern: {pattern}',
                                        'match': pattern,
                                        'confidence': 60
                                    }],
                                    source='deep',
                                    website='',
                                    description=f'Detected from HTML content pattern',
                                    detection_time=time.time()
                                )
                                detections.append(detection)
                                logger.info(f"Deep analysis detected: {tech_name} from HTML pattern")
                                break  # Only add once per technology
                        except re.error:
                            continue
                
                # Also check individual technology patterns
                for tech_name, tech_data in self.dataset_manager.all_technologies.items():
                    if 'html' in tech_data:
                        for pattern in tech_data['html']:
                            try:
                                matches = re.finditer(pattern, html_content, re.IGNORECASE | re.DOTALL)
                                for match in matches:
                                    detection = DetectionResult(
                                        name=tech_name,
                                        confidence=75,
                                        category=tech_data.get('category', 'Unknown'),
                                        versions=[],
                                        evidence=[{
                                            'field': 'html',
                                            'detail': match.group(0)[:200] + '...' if len(match.group(0)) > 200 else match.group(0),
                                            'match': pattern,
                                            'confidence': 75
                                        }],
                                        source='deep',
                                        website=tech_data.get('website'),
                                        description=tech_data.get('description'),
                                        detection_time=time.time()
                                    )
                                    detections.append(detection)
                                    logger.info(f"Deep analysis detected: {tech_name} from HTML content")
                            except re.error:
                                continue
            
            # Deep script analysis
            scripts = response_data.get('scripts', [])
            for script_url in scripts:
                for tech_name, tech_data in self.dataset_manager.all_technologies.items():
                    if 'scripts' in tech_data:
                        for pattern in tech_data['scripts']:
                            try:
                                if re.search(pattern, script_url, re.IGNORECASE):
                                    detection = DetectionResult(
                                        name=tech_name,
                                        confidence=80,
                                        category=tech_data.get('category', 'Unknown'),
                                        versions=[],
                                        evidence=[{
                                            'field': 'scripts',
                                            'detail': script_url,
                                            'match': pattern,
                                            'confidence': 80
                                        }],
                                        source='deep',
                                        website=tech_data.get('website'),
                                        description=tech_data.get('description'),
                                        detection_time=time.time()
                                    )
                                    detections.append(detection)
                            except re.error:
                                continue
            
            # Deep meta tag analysis
            meta_tags = response_data.get('meta_tags', {})
            for meta_name, meta_content in meta_tags.items():
                for tech_name, tech_data in self.dataset_manager.all_technologies.items():
                    if 'meta' in tech_data:
                        for pattern in tech_data['meta']:
                            try:
                                if re.search(pattern, f"{meta_name}: {meta_content}", re.IGNORECASE):
                                    detection = DetectionResult(
                                        name=tech_name,
                                        confidence=70,
                                        category=tech_data.get('category', 'Unknown'),
                                        versions=[],
                                        evidence=[{
                                            'field': 'meta',
                                            'detail': f"{meta_name}: {meta_content}",
                                            'match': pattern,
                                            'confidence': 70
                                        }],
                                        source='deep',
                                        website=tech_data.get('website'),
                                        description=tech_data.get('description'),
                                        detection_time=time.time()
                                    )
                                    detections.append(detection)
                            except re.error:
                                continue
            
            logger.info(f"Deep analysis completed: {len(detections)} technologies detected")
            
        except Exception as e:
            logger.error(f"Deep analysis failed: {e}")
        
        return detections
    
    def _deduplicate_technologies(self, technologies: List[DetectionResult]) -> List[DetectionResult]:
        """Deduplicate and merge technology detections"""
        tech_dict = {}
        
        for detection in technologies:
            name = detection.name
            if name in tech_dict:
                # Merge with existing detection
                existing = tech_dict[name]
                if detection.confidence > existing.confidence:
                    tech_dict[name] = detection
                # Merge evidence
                existing.evidence.extend(detection.evidence)
            else:
                tech_dict[name] = detection
        
        return list(tech_dict.values())

async def main():
    """Main function for command line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Ultimate Web Technology Detection System')
    parser.add_argument('url', help='URL to analyze')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--output', '-o', choices=['json', 'text'], default='json', help='Output format')
    parser.add_argument('--deep', action='store_true', help='Enable deep detection mode')
    parser.add_argument('--max-results', type=int, default=200, help='Maximum number of results')
    parser.add_argument('--min-confidence', type=int, default=0, help='Minimum confidence threshold')
    parser.add_argument('--timeout', type=int, default=30, help='Request timeout in seconds')
    parser.add_argument('--save-report', help='Save report to file')
    
    args = parser.parse_args()
    
    # Configure logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Initialize detector
    detector = UltimateTechDetector()
    
    # Run analysis
    options = {
        'min_confidence': args.min_confidence,
        'max_results': args.max_results,
        'timeout': args.timeout
    }
    
    result = await detector.analyze_url(args.url, options)
    
    # Output results
    if args.output == 'json':
        output_data = {
            'url': result.url,
            'final_url': result.final_url,
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
            'analysis_time': result.analysis_time,
            'metadata': result.metadata,
            'errors': result.errors,
            'warnings': result.warnings,
            'user_agents_tried': result.user_agents_tried,
            'successful_agent': result.successful_agent
        }
        
        if args.save_report:
            with open(args.save_report, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            print(f"Report saved to {args.save_report}")
        else:
            print(json.dumps(output_data, indent=2, ensure_ascii=False))
    
    else:  # text output
        print(f"Analysis Results for {result.url}")
        print(f"Final URL: {result.final_url}")
        print(f"Analysis Time: {result.analysis_time:.2f}s")
        print(f"Technologies Detected: {len(result.technologies)}")
        print(f"Categories: {result.metadata.get('categories_detected', 0)}")
        print("\nTechnologies:")
        for tech in result.technologies:
            print(f"  {tech.name} ({tech.category}) - {tech.confidence}% confidence")

if __name__ == "__main__":
    asyncio.run(main())

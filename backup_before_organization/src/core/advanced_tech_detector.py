#!/usr/bin/env python3
"""
Advanced Web Technology Detection System
========================================

A comprehensive, enterprise-grade web technology detection system that combines
multiple detection engines and datasets for maximum accuracy and coverage.

Features:
- Multi-engine detection (Dataset + WhatWeb + Wappalyzer)
- Advanced pattern matching with confidence scoring
- Parallel processing for performance
- Comprehensive error handling and logging
- Multiple output formats (JSON, XML, CSV, HTML)
- Caching and optimization
- Real-time analysis and batch processing
"""

import argparse
import asyncio
import json
import logging
import re
import sys
import time
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union
from urllib.parse import urljoin, urlparse
import csv
from io import StringIO

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from bs4 import BeautifulSoup
import dns.resolver

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('tech_detector.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Constants
DEFAULT_UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
DEFAULT_TIMEOUT = 30
MAX_WORKERS = 10
CACHE_TTL = 3600  # 1 hour

@dataclass
class DetectionResult:
    """Represents a technology detection result"""
    name: str
    confidence: int
    category: str
    versions: List[str] = field(default_factory=list)
    evidence: List[Dict[str, Any]] = field(default_factory=list)
    source: str = "dataset"
    website: Optional[str] = None
    description: Optional[str] = None
    saas: Optional[bool] = None
    oss: Optional[bool] = None

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

class PatternCompiler:
    """Advanced pattern compilation with caching and optimization"""
    
    def __init__(self):
        self._cache = {}
        self._confidence_re = re.compile(r";\s*confidence:(\d+)\s*$", re.I)
        self._version_re = re.compile(r";\s*version:\\(\d+)\s*$", re.I)
    
    def compile_pattern(self, pattern: str) -> Dict[str, Any]:
        """Compile a pattern with confidence and version extraction"""
        if pattern in self._cache:
            return self._cache[pattern]
        
        raw_pattern = pattern
        confidence = 50
        version_group = None
        
        # Extract version group
        version_match = self._version_re.search(pattern)
        if version_match:
            try:
                version_group = int(version_match.group(1))
            except ValueError:
                version_group = None
            pattern = pattern[:version_match.start()]
        
        # Extract confidence
        conf_match = self._confidence_re.search(pattern)
        if conf_match:
            confidence = int(conf_match.group(1))
            pattern = pattern[:conf_match.start()]
        
        # Compile regex
        try:
            regex = re.compile(pattern, re.I | re.S)
        except re.error:
            regex = re.compile(re.escape(pattern), re.I | re.S)
        
        result = {
            'pattern': raw_pattern,
            'regex': regex,
            'confidence': confidence,
            'version_group': version_group
        }
        
        self._cache[pattern] = result
        return result

class DatasetManager:
    """Manages multiple technology datasets with intelligent merging"""
    
    def __init__(self, datasets_dir: str = "json_datasets"):
        self.datasets_dir = Path(datasets_dir)
        self.datasets = {}
        self.categories = {}
        self.technologies = {}
        self._load_datasets()
    
    def _load_datasets(self):
        """Load all available datasets"""
        dataset_files = {
            'web_tech': 'web_tech_dataset.json',
            'wappalyzer': 'wappalyzer_technologies_clean.json',
            'technology_lookup': 'technology_lookup_merged.json'
        }
        
        for name, filename in dataset_files.items():
            filepath = self.datasets_dir / filename
            if filepath.exists():
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    self.datasets[name] = data
                    logger.info(f"Loaded {name} dataset: {len(data.get('technologies', {}))} technologies")
                except Exception as e:
                    logger.error(f"Failed to load {name} dataset: {e}")
        
        self._merge_datasets()
    
    def _merge_datasets(self):
        """Intelligently merge all datasets"""
        all_technologies = {}
        all_categories = {}
        
        # Merge categories
        for dataset_name, dataset in self.datasets.items():
            if 'categories' in dataset:
                for cat_id, cat_name in dataset['categories'].items():
                    if cat_id not in all_categories:
                        all_categories[cat_id] = cat_name
        
        # Merge technologies with conflict resolution
        for dataset_name, dataset in self.datasets.items():
            if 'technologies' in dataset:
                for tech_name, tech_data in dataset['technologies'].items():
                    if tech_name in all_technologies:
                        # Merge with priority: web_tech > wappalyzer > technology_lookup
                        priority = {'web_tech': 3, 'wappalyzer': 2, 'technology_lookup': 1}
                        if priority.get(dataset_name, 0) > priority.get(all_technologies[tech_name].get('_source', ''), 0):
                            tech_data['_source'] = dataset_name
                            all_technologies[tech_name] = tech_data
                    else:
                        tech_data['_source'] = dataset_name
                        all_technologies[tech_name] = tech_data
        
        self.technologies = all_technologies
        self.categories = all_categories
        logger.info(f"Merged {len(all_technologies)} technologies from {len(self.datasets)} datasets")
    
    def get_technology(self, name: str) -> Optional[Dict[str, Any]]:
        """Get technology data by name"""
        return self.technologies.get(name)
    
    def get_category_name(self, cat_id: Union[str, int]) -> str:
        """Get category name by ID"""
        return self.categories.get(str(cat_id), str(cat_id))
    
    def search_technologies(self, query: str, limit: int = 50) -> List[str]:
        """Search technologies by name or description"""
        query_lower = query.lower()
        results = []
        
        for name, data in self.technologies.items():
            if (query_lower in name.lower() or 
                query_lower in data.get('description', '').lower()):
                results.append(name)
                if len(results) >= limit:
                    break
        
        return results

class AdvancedTechDetector:
    """Main technology detection engine with advanced features"""
    
    def __init__(self, datasets_dir: str = "json_datasets"):
        self.dataset_manager = DatasetManager(datasets_dir)
        self.pattern_compiler = PatternCompiler()
        self.session = self._create_session()
        self.cache = {}
        
    def _create_session(self) -> requests.Session:
        """Create optimized HTTP session with retry strategy"""
        session = requests.Session()
        
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session
    
    async def analyze_url(self, url: str, options: Dict[str, Any] = None) -> AnalysisResult:
        """Analyze a URL for technologies"""
        options = options or {}
        start_time = time.time()
        
        try:
            # Normalize URL
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            logger.info(f"Analyzing URL: {url}")
            
            # Fetch page data
            page_data = await self._fetch_page_data(url, options)
            if not page_data:
                return AnalysisResult(url=url, final_url=url, errors=["Failed to fetch page"])
            
            # Detect technologies
            technologies = await self._detect_technologies(page_data, options)
            
            # Apply post-processing
            technologies = self._post_process_results(technologies, options)
            
            analysis_time = time.time() - start_time
            
            return AnalysisResult(
                url=url,
                final_url=page_data.get('final_url', url),
                technologies=technologies,
                analysis_time=analysis_time,
                metadata=page_data.get('metadata', {}),
                errors=page_data.get('errors', []),
                warnings=page_data.get('warnings', [])
            )
            
        except Exception as e:
            logger.error(f"Error analyzing {url}: {e}")
            return AnalysisResult(
                url=url,
                final_url=url,
                errors=[f"Analysis failed: {str(e)}"]
            )
    
    async def _fetch_page_data(self, url: str, options: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Fetch and parse page data"""
        try:
            headers = {
                'User-Agent': options.get('user_agent', DEFAULT_UA),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
            
            timeout = options.get('timeout', DEFAULT_TIMEOUT)
            response = self.session.get(
                url, 
                headers=headers, 
                timeout=timeout,
                allow_redirects=True
            )
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract data
            scripts = [script.get('src') for script in soup.find_all('script', src=True)]
            scripts = [urljoin(url, script) for script in scripts if script]
            
            # Extract meta tags
            meta_tags = {}
            for meta in soup.find_all('meta'):
                name = meta.get('name') or meta.get('property')
                content = meta.get('content')
                if name and content:
                    meta_tags[name] = content
            
            return {
                'url': url,
                'final_url': response.url,
                'html': response.text,
                'headers': dict(response.headers),
                'cookies': {c.name: c.value for c in response.cookies},
                'scripts': scripts,
                'meta_tags': meta_tags,
                'soup': soup,
                'status_code': response.status_code,
                'metadata': {
                    'title': soup.title.string.strip() if soup.title and soup.title.string else '',
                    'content_length': len(response.text),
                    'response_time': response.elapsed.total_seconds()
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to fetch {url}: {e}")
            return None
    
    async def _detect_technologies(self, page_data: Dict[str, Any], options: Dict[str, Any]) -> List[DetectionResult]:
        """Detect technologies using all available methods"""
        technologies = []
        
        # Use thread pool for parallel processing
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = []
            
            # Dataset-based detection
            if options.get('use_dataset', True):
                futures.append(executor.submit(
                    self._detect_from_dataset, page_data, options
                ))
            
            # WhatWeb detection
            if options.get('use_whatweb', False):
                futures.append(executor.submit(
                    self._detect_with_whatweb, page_data, options
                ))
            
            # Wappalyzer detection
            if options.get('use_wappalyzer', False):
                futures.append(executor.submit(
                    self._detect_with_wappalyzer, page_data, options
                ))
            
            # Collect results
            for future in as_completed(futures):
                try:
                    result = future.result()
                    if result:
                        technologies.extend(result)
                except Exception as e:
                    logger.error(f"Detection method failed: {e}")
        
        return technologies
    
    def _detect_from_dataset(self, page_data: Dict[str, Any], options: Dict[str, Any]) -> List[DetectionResult]:
        """Detect technologies using the merged dataset"""
        results = []
        
        for tech_name, tech_data in self.dataset_manager.technologies.items():
            try:
                confidence = 0
                evidence = []
                versions = set()
                
                # Check headers
                if 'headers' in tech_data:
                    header_matches = self._check_headers(
                        tech_data['headers'], 
                        page_data['headers'], 
                        tech_name
                    )
                    confidence += header_matches['confidence']
                    evidence.extend(header_matches['evidence'])
                    versions.update(header_matches['versions'])
                
                # Check cookies
                if 'cookies' in tech_data:
                    cookie_matches = self._check_cookies(
                        tech_data['cookies'],
                        page_data['cookies'],
                        page_data['headers'].get('Set-Cookie', ''),
                        tech_name
                    )
                    confidence += cookie_matches['confidence']
                    evidence.extend(cookie_matches['evidence'])
                    versions.update(cookie_matches['versions'])
                
                # Check scripts
                if 'scripts' in tech_data:
                    script_matches = self._check_scripts(
                        tech_data['scripts'],
                        page_data['scripts'],
                        tech_name
                    )
                    confidence += script_matches['confidence']
                    evidence.extend(script_matches['evidence'])
                    versions.update(script_matches['versions'])
                
                # Check HTML
                if 'html' in tech_data:
                    html_matches = self._check_html(
                        tech_data['html'],
                        page_data['html'],
                        tech_name
                    )
                    confidence += html_matches['confidence']
                    evidence.extend(html_matches['evidence'])
                    versions.update(html_matches['versions'])
                
                # Check URL
                if 'url' in tech_data:
                    url_matches = self._check_url(
                        tech_data['url'],
                        page_data['final_url'],
                        tech_name
                    )
                    confidence += url_matches['confidence']
                    evidence.extend(url_matches['evidence'])
                    versions.update(url_matches['versions'])
                
                # Check meta tags
                if 'meta' in tech_data:
                    meta_matches = self._check_meta(
                        tech_data['meta'],
                        page_data['meta_tags'],
                        tech_name
                    )
                    confidence += meta_matches['confidence']
                    evidence.extend(meta_matches['evidence'])
                    versions.update(meta_matches['versions'])
                
                # Only include if confidence is above threshold
                if confidence >= options.get('min_confidence', 10):
                    category_ids = tech_data.get('cats', [])
                    category_names = [
                        self.dataset_manager.get_category_name(cat_id) 
                        for cat_id in category_ids
                    ]
                    
                    results.append(DetectionResult(
                        name=tech_name,
                        confidence=min(confidence, 100),
                        category=category_names[0] if category_names else 'Unknown',
                        versions=list(versions),
                        evidence=evidence,
                        source=tech_data.get('_source', 'dataset'),
                        website=tech_data.get('website'),
                        description=tech_data.get('description'),
                        saas=tech_data.get('saas'),
                        oss=tech_data.get('oss')
                    ))
                    
            except Exception as e:
                logger.debug(f"Error checking {tech_name}: {e}")
                continue
        
        return results
    
    def _check_headers(self, patterns: Dict[str, str], headers: Dict[str, str], tech_name: str) -> Dict[str, Any]:
        """Check header patterns"""
        confidence = 0
        evidence = []
        versions = set()
        
        for header_pattern, value_pattern in patterns.items():
            compiled_header = self.pattern_compiler.compile_pattern(header_pattern)
            compiled_value = self.pattern_compiler.compile_pattern(value_pattern)
            
            for header_name, header_value in headers.items():
                if compiled_header['regex'].search(header_name):
                    match = compiled_value['regex'].search(header_value)
                    if match:
                        conf = compiled_value['confidence']
                        confidence += conf
                        
                        version = None
                        if compiled_value['version_group'] and compiled_value['version_group'] <= len(match.groups()):
                            version = match.group(compiled_value['version_group'])
                            if version:
                                versions.add(version)
                        
                        evidence.append({
                            'field': 'headers',
                            'detail': f"{header_name}: {header_value[:100]}",
                            'match': match.group(0)[:100],
                            'confidence': conf,
                            'version': version
                        })
        
        return {'confidence': confidence, 'evidence': evidence, 'versions': versions}
    
    def _check_cookies(self, patterns: Dict[str, str], cookies: Dict[str, str], set_cookie_header: str, tech_name: str) -> Dict[str, Any]:
        """Check cookie patterns"""
        confidence = 0
        evidence = []
        versions = set()
        
        # Merge cookies from response and Set-Cookie header
        all_cookies = dict(cookies)
        if set_cookie_header:
            for cookie_str in set_cookie_header.split(','):
                parts = cookie_str.strip().split(';')[0].split('=', 1)
                if len(parts) == 2:
                    all_cookies[parts[0].strip()] = parts[1].strip()
        
        for cookie_pattern, value_pattern in patterns.items():
            compiled_cookie = self.pattern_compiler.compile_pattern(cookie_pattern)
            compiled_value = self.pattern_compiler.compile_pattern(value_pattern)
            
            for cookie_name, cookie_value in all_cookies.items():
                if compiled_cookie['regex'].search(cookie_name):
                    match = compiled_value['regex'].search(cookie_value)
                    if match:
                        conf = compiled_value['confidence']
                        confidence += conf
                        
                        version = None
                        if compiled_value['version_group'] and compiled_value['version_group'] <= len(match.groups()):
                            version = match.group(compiled_value['version_group'])
                            if version:
                                versions.add(version)
                        
                        evidence.append({
                            'field': 'cookies',
                            'detail': f"{cookie_name}: {cookie_value[:100]}",
                            'match': match.group(0)[:100],
                            'confidence': conf,
                            'version': version
                        })
        
        return {'confidence': confidence, 'evidence': evidence, 'versions': versions}
    
    def _check_scripts(self, patterns: List[str], scripts: List[str], tech_name: str) -> Dict[str, Any]:
        """Check script patterns"""
        confidence = 0
        evidence = []
        versions = set()
        
        for pattern in patterns:
            compiled = self.pattern_compiler.compile_pattern(pattern)
            
            for script_url in scripts:
                match = compiled['regex'].search(script_url)
                if match:
                    conf = compiled['confidence']
                    confidence += conf
                    
                    version = None
                    if compiled['version_group'] and compiled['version_group'] <= len(match.groups()):
                        version = match.group(compiled['version_group'])
                        if version:
                            versions.add(version)
                    
                    evidence.append({
                        'field': 'scripts',
                        'detail': script_url[:100],
                        'match': match.group(0)[:100],
                        'confidence': conf,
                        'version': version
                    })
        
        return {'confidence': confidence, 'evidence': evidence, 'versions': versions}
    
    def _check_html(self, pattern: str, html: str, tech_name: str) -> Dict[str, Any]:
        """Check HTML patterns"""
        confidence = 0
        evidence = []
        versions = set()
        
        compiled = self.pattern_compiler.compile_pattern(pattern)
        match = compiled['regex'].search(html)
        
        if match:
            conf = compiled['confidence']
            confidence += conf
            
            version = None
            if compiled['version_group'] and compiled['version_group'] <= len(match.groups()):
                version = match.group(compiled['version_group'])
                if version:
                    versions.add(version)
            
            evidence.append({
                'field': 'html',
                'detail': 'HTML content',
                'match': match.group(0)[:200],
                'confidence': conf,
                'version': version
            })
        
        return {'confidence': confidence, 'evidence': evidence, 'versions': versions}
    
    def _check_url(self, pattern: str, url: str, tech_name: str) -> Dict[str, Any]:
        """Check URL patterns"""
        confidence = 0
        evidence = []
        versions = set()
        
        compiled = self.pattern_compiler.compile_pattern(pattern)
        match = compiled['regex'].search(url)
        
        if match:
            conf = compiled['confidence']
            confidence += conf
            
            version = None
            if compiled['version_group'] and compiled['version_group'] <= len(match.groups()):
                version = match.group(compiled['version_group'])
                if version:
                    versions.add(version)
            
            evidence.append({
                'field': 'url',
                'detail': url[:100],
                'match': match.group(0)[:100],
                'confidence': conf,
                'version': version
            })
        
        return {'confidence': confidence, 'evidence': evidence, 'versions': versions}
    
    def _check_meta(self, patterns: Dict[str, str], meta_tags: Dict[str, str], tech_name: str) -> Dict[str, Any]:
        """Check meta tag patterns"""
        confidence = 0
        evidence = []
        versions = set()
        
        for meta_name, meta_pattern in patterns.items():
            compiled = self.pattern_compiler.compile_pattern(meta_pattern)
            
            for tag_name, tag_value in meta_tags.items():
                if compiled['regex'].search(tag_name):
                    match = compiled['regex'].search(tag_value)
                    if match:
                        conf = compiled['confidence']
                        confidence += conf
                        
                        version = None
                        if compiled['version_group'] and compiled['version_group'] <= len(match.groups()):
                            version = match.group(compiled['version_group'])
                            if version:
                                versions.add(version)
                        
                        evidence.append({
                            'field': 'meta',
                            'detail': f"{tag_name}: {tag_value[:100]}",
                            'match': match.group(0)[:100],
                            'confidence': conf,
                            'version': version
                        })
        
        return {'confidence': confidence, 'evidence': evidence, 'versions': versions}
    
    def _detect_with_whatweb(self, page_data: Dict[str, Any], options: Dict[str, Any]) -> List[DetectionResult]:
        """Detect technologies using WhatWeb"""
        # Implementation for WhatWeb integration
        # This would call the WhatWeb binary and parse results
        return []
    
    def _detect_with_wappalyzer(self, page_data: Dict[str, Any], options: Dict[str, Any]) -> List[DetectionResult]:
        """Detect technologies using Wappalyzer"""
        # Implementation for Wappalyzer integration
        # This would use the python-Wappalyzer library
        return []
    
    def _post_process_results(self, technologies: List[DetectionResult], options: Dict[str, Any]) -> List[DetectionResult]:
        """Post-process detection results"""
        # Remove duplicates
        seen = set()
        unique_techs = []
        for tech in technologies:
            key = tech.name.lower()
            if key not in seen:
                seen.add(key)
                unique_techs.append(tech)
        
        # Sort by confidence
        unique_techs.sort(key=lambda x: x.confidence, reverse=True)
        
        # Apply confidence threshold
        min_confidence = options.get('min_confidence', 10)
        filtered_techs = [tech for tech in unique_techs if tech.confidence >= min_confidence]
        
        # Limit results
        max_results = options.get('max_results', 100)
        return filtered_techs[:max_results]

# Output formatters
class OutputFormatter:
    """Handles different output formats"""
    
    @staticmethod
    def to_json(result: AnalysisResult) -> str:
        """Convert result to JSON format"""
        return json.dumps(asdict(result), indent=2, ensure_ascii=False)
    
    @staticmethod
    def to_xml(result: AnalysisResult) -> str:
        """Convert result to XML format"""
        root = ET.Element("analysis")
        root.set("url", result.url)
        root.set("final_url", result.final_url)
        root.set("analysis_time", str(result.analysis_time))
        
        technologies = ET.SubElement(root, "technologies")
        for tech in result.technologies:
            tech_elem = ET.SubElement(technologies, "technology")
            tech_elem.set("name", tech.name)
            tech_elem.set("confidence", str(tech.confidence))
            tech_elem.set("category", tech.category)
            tech_elem.set("source", tech.source)
            
            if tech.versions:
                versions_elem = ET.SubElement(tech_elem, "versions")
                for version in tech.versions:
                    version_elem = ET.SubElement(versions_elem, "version")
                    version_elem.text = version
            
            if tech.evidence:
                evidence_elem = ET.SubElement(tech_elem, "evidence")
                for ev in tech.evidence:
                    ev_elem = ET.SubElement(evidence_elem, "item")
                    ev_elem.set("field", ev.get('field', ''))
                    ev_elem.set("confidence", str(ev.get('confidence', 0)))
                    ev_elem.text = ev.get('match', '')
        
        return ET.tostring(root, encoding='unicode')
    
    @staticmethod
    def to_csv(result: AnalysisResult) -> str:
        """Convert result to CSV format"""
        output = StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow(['Name', 'Confidence', 'Category', 'Versions', 'Source', 'Website', 'Description'])
        
        # Data
        for tech in result.technologies:
            writer.writerow([
                tech.name,
                tech.confidence,
                tech.category,
                '; '.join(tech.versions),
                tech.source,
                tech.website or '',
                tech.description or ''
            ])
        
        return output.getvalue()
    
    @staticmethod
    def to_html(result: AnalysisResult) -> str:
        """Convert result to HTML format"""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Technology Analysis - {result.url}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background: #f0f0f0; padding: 15px; border-radius: 5px; }}
                .tech {{ margin: 10px 0; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }}
                .confidence {{ background: #e8f5e8; padding: 5px; border-radius: 3px; }}
                .evidence {{ margin-top: 10px; font-size: 0.9em; color: #666; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Technology Analysis Report</h1>
                <p><strong>URL:</strong> {result.url}</p>
                <p><strong>Final URL:</strong> {result.final_url}</p>
                <p><strong>Analysis Time:</strong> {result.analysis_time:.2f}s</p>
                <p><strong>Technologies Found:</strong> {len(result.technologies)}</p>
            </div>
        """
        
        for tech in result.technologies:
            html += f"""
            <div class="tech">
                <h3>{tech.name}</h3>
                <div class="confidence">Confidence: {tech.confidence}% | Category: {tech.category} | Source: {tech.source}</div>
                {f'<p><strong>Versions:</strong> {", ".join(tech.versions)}</p>' if tech.versions else ''}
                {f'<p><strong>Website:</strong> <a href="{tech.website}" target="_blank">{tech.website}</a></p>' if tech.website else ''}
                {f'<p><strong>Description:</strong> {tech.description}</p>' if tech.description else ''}
                <div class="evidence">
                    <strong>Evidence:</strong>
                    <ul>
            """
            
            for ev in tech.evidence:
                html += f"<li>{ev.get('field', '')}: {ev.get('match', '')} (confidence: {ev.get('confidence', 0)})</li>"
            
            html += """
                    </ul>
                </div>
            </div>
            """
        
        html += """
        </body>
        </html>
        """
        
        return html

async def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Advanced Web Technology Detection System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s https://example.com
  %(prog)s https://example.com --output json --min-confidence 20
  %(prog)s https://example.com --use-whatweb --use-wappalyzer --output html
  %(prog)s --batch urls.txt --output csv --workers 5
        """
    )
    
    parser.add_argument('url', nargs='?', help='URL to analyze')
    parser.add_argument('--batch', help='File containing URLs to analyze (one per line)')
    parser.add_argument('--output', choices=['json', 'xml', 'csv', 'html'], default='json', help='Output format')
    parser.add_argument('--min-confidence', type=int, default=10, help='Minimum confidence threshold')
    parser.add_argument('--max-results', type=int, default=100, help='Maximum number of results')
    parser.add_argument('--timeout', type=int, default=30, help='Request timeout in seconds')
    parser.add_argument('--user-agent', default=DEFAULT_UA, help='User agent string')
    parser.add_argument('--use-dataset', action='store_true', default=True, help='Use dataset detection')
    parser.add_argument('--use-whatweb', action='store_true', help='Use WhatWeb detection')
    parser.add_argument('--use-wappalyzer', action='store_true', help='Use Wappalyzer detection')
    parser.add_argument('--workers', type=int, default=5, help='Number of parallel workers for batch processing')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    if not args.url and not args.batch:
        parser.error("Either URL or --batch file must be provided")
    
    detector = AdvancedTechDetector()
    
    options = {
        'min_confidence': args.min_confidence,
        'max_results': args.max_results,
        'timeout': args.timeout,
        'user_agent': args.user_agent,
        'use_dataset': args.use_dataset,
        'use_whatweb': args.use_whatweb,
        'use_wappalyzer': args.use_wappalyzer
    }
    
    if args.batch:
        # Batch processing
        with open(args.batch, 'r') as f:
            urls = [line.strip() for line in f if line.strip()]
        
        print(f"Processing {len(urls)} URLs...")
        
        with ThreadPoolExecutor(max_workers=args.workers) as executor:
            futures = {executor.submit(detector.analyze_url, url, options): url for url in urls}
            
            for future in as_completed(futures):
                url = futures[future]
                try:
                    result = future.result()
                    print(f"\n=== {url} ===")
                    print(OutputFormatter.to_json(result))
                except Exception as e:
                    print(f"Error processing {url}: {e}")
    else:
        # Single URL processing
        result = await detector.analyze_url(args.url, options)
        
        if args.output == 'json':
            print(OutputFormatter.to_json(result))
        elif args.output == 'xml':
            print(OutputFormatter.to_xml(result))
        elif args.output == 'csv':
            print(OutputFormatter.to_csv(result))
        elif args.output == 'html':
            print(OutputFormatter.to_html(result))

if __name__ == "__main__":
    asyncio.run(main())

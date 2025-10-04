#!/usr/bin/env python3
"""
Enhanced Web Technology Detector
================================

Advanced technology detection with multiple user agents, robust error handling,
and comprehensive dataset utilization.
"""

import asyncio
import json
import logging
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union
from urllib.parse import urljoin, urlparse

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from bs4 import BeautifulSoup
import dns.resolver

from ..utils.user_agents import UserAgentManager
from .enhanced_dataset_manager import EnhancedDatasetManager

logger = logging.getLogger(__name__)

@dataclass
class DetectionResult:
    """Enhanced detection result with metadata"""
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
    user_agent_used: Optional[str] = None
    detection_time: float = 0.0

@dataclass
class AnalysisResult:
    """Enhanced analysis result"""
    url: str
    final_url: str
    technologies: List[DetectionResult] = field(default_factory=list)
    analysis_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    user_agents_tried: List[str] = field(default_factory=list)
    successful_agent: Optional[str] = None

class PatternCompiler:
    """Enhanced pattern compiler with caching and optimization"""
    
    def __init__(self):
        self._cache = {}
        self._confidence_re = re.compile(r";\s*confidence:(\d+)\s*$", re.I)
        self._version_re = re.compile(r";\s*version:\\(\d+)\s*$", re.I)
    
    def compile_pattern(self, pattern: str) -> Dict[str, Any]:
        """Compile pattern with confidence and version extraction"""
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

class EnhancedTechDetector:
    """Enhanced technology detector with multiple user agents and robust error handling"""
    
    def __init__(self, datasets_dir: str = "json_datasets"):
        self.dataset_manager = EnhancedDatasetManager(datasets_dir)
        self.pattern_compiler = PatternCompiler()
        self.user_agent_manager = UserAgentManager()
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
        """Analyze URL with multiple user agents and robust error handling"""
        options = options or {}
        start_time = time.time()
        
        logger.info(f"Starting enhanced analysis of {url}")
        
        # Try multiple user agents
        user_agents = self._get_user_agents_for_analysis(options)
        page_data = None
        successful_agent = None
        
        for i, user_agent in enumerate(user_agents):
            try:
                logger.debug(f"Trying user agent {i+1}/{len(user_agents)}: {user_agent[:50]}...")
                page_data = await self._fetch_page_data(url, user_agent, options)
                if page_data:
                    successful_agent = user_agent
                    logger.info(f"Successfully fetched page with user agent: {user_agent[:50]}...")
                    break
            except Exception as e:
                logger.debug(f"User agent {i+1} failed: {e}")
                continue
        
        if not page_data:
            return AnalysisResult(
                url=url,
                final_url=url,
                errors=["Failed to fetch page with any user agent"],
                user_agents_tried=user_agents
            )
        
        # Detect technologies
        technologies = await self._detect_technologies(page_data, options, successful_agent)
        
        # Post-process results
        technologies = self._post_process_results(technologies, options)
        
        analysis_time = time.time() - start_time
        
        return AnalysisResult(
            url=url,
            final_url=page_data.get('final_url', url),
            technologies=technologies,
            analysis_time=analysis_time,
            metadata=page_data.get('metadata', {}),
            errors=page_data.get('errors', []),
            warnings=page_data.get('warnings', []),
            user_agents_tried=user_agents,
            successful_agent=successful_agent
        )
    
    def _get_user_agents_for_analysis(self, options: Dict[str, Any]) -> List[str]:
        """Get user agents for analysis based on options"""
        if 'user_agent' in options:
            return [options['user_agent']]
        
        # Get user agents based on preferences
        preferred_browser = options.get('preferred_browser', 'chrome')
        preferred_os = options.get('preferred_os', 'windows')
        
        if preferred_browser == 'random':
            return self.user_agent_manager.get_agents_for_retry(3)
        elif preferred_browser in ['chrome', 'firefox', 'safari', 'edge']:
            agent = self.user_agent_manager.get_agent_by_browser(preferred_browser)
            if agent:
                return [agent] + self.user_agent_manager.get_agents_for_retry(2)
        
        if preferred_os in ['windows', 'macos', 'linux']:
            agent = self.user_agent_manager.get_agent_by_os(preferred_os)
            if agent:
                return [agent] + self.user_agent_manager.get_agents_for_retry(2)
        
        # Default: try multiple agents
        return self.user_agent_manager.get_agents_for_retry(3)
    
    async def _fetch_page_data(self, url: str, user_agent: str, options: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Fetch page data with specific user agent"""
        try:
            headers = {
                'User-Agent': user_agent,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
            
            # Add custom headers
            if 'headers' in options:
                headers.update(options['headers'])
            
            timeout = options.get('timeout', 30)
            follow_redirects = options.get('follow_redirects', True)
            
            response = self.session.get(
                url, 
                headers=headers, 
                timeout=timeout,
                allow_redirects=follow_redirects
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
            
            # Extract additional metadata
            title = soup.title.string.strip() if soup.title and soup.title.string else ""
            description = ""
            keywords = ""
            
            desc_meta = soup.find('meta', attrs={'name': 'description'})
            if desc_meta:
                description = desc_meta.get('content', '')
            
            keywords_meta = soup.find('meta', attrs={'name': 'keywords'})
            if keywords_meta:
                keywords = keywords_meta.get('content', '')
            
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
                'user_agent': user_agent,
                'metadata': {
                    'title': title,
                    'description': description,
                    'keywords': keywords,
                    'content_length': len(response.text),
                    'response_time': response.elapsed.total_seconds(),
                    'server': response.headers.get('Server', ''),
                    'x_powered_by': response.headers.get('X-Powered-By', ''),
                    'content_type': response.headers.get('Content-Type', '')
                }
            }
            
        except Exception as e:
            logger.debug(f"Failed to fetch {url} with user agent {user_agent[:50]}...: {e}")
            return None
    
    async def _detect_technologies(self, page_data: Dict[str, Any], options: Dict[str, Any], user_agent: str) -> List[DetectionResult]:
        """Detect technologies using enhanced dataset"""
        technologies = []
        
        # Use thread pool for parallel processing
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = []
            
            # Process technologies in batches
            tech_batch_size = 100
            tech_items = list(self.dataset_manager.merged_technologies.items())
            
            for i in range(0, len(tech_items), tech_batch_size):
                batch = tech_items[i:i + tech_batch_size]
                future = executor.submit(
                    self._process_technology_batch, 
                    batch, 
                    page_data, 
                    options, 
                    user_agent
                )
                futures.append(future)
            
            # Collect results
            for future in as_completed(futures):
                try:
                    batch_results = future.result()
                    technologies.extend(batch_results)
                except Exception as e:
                    logger.error(f"Technology batch processing failed: {e}")
        
        return technologies
    
    def _process_technology_batch(self, tech_batch: List[Tuple[str, Dict[str, Any]]], 
                                 page_data: Dict[str, Any], options: Dict[str, Any], 
                                 user_agent: str) -> List[DetectionResult]:
        """Process a batch of technologies"""
        results = []
        
        for tech_name, tech_data in tech_batch:
            try:
                detection_result = self._detect_single_technology(
                    tech_name, tech_data, page_data, options, user_agent
                )
                if detection_result:
                    results.append(detection_result)
            except Exception as e:
                logger.debug(f"Error processing {tech_name}: {e}")
                continue
        
        return results
    
    def _detect_single_technology(self, tech_name: str, tech_data: Dict[str, Any], 
                                 page_data: Dict[str, Any], options: Dict[str, Any], 
                                 user_agent: str) -> Optional[DetectionResult]:
        """Detect a single technology"""
        start_time = time.time()
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
        
        # Only return if confidence is above threshold
        min_confidence = options.get('min_confidence', 10)
        if confidence >= min_confidence:
            category_ids = tech_data.get('cats', [])
            category_names = [
                self.dataset_manager.get_category_name(cat_id) 
                for cat_id in category_ids
            ]
            
            detection_time = time.time() - start_time
            
            return DetectionResult(
                name=tech_name,
                confidence=min(confidence, 100),
                category=category_names[0] if category_names else 'Unknown',
                versions=list(versions),
                evidence=evidence,
                source=tech_data.get('_source', 'dataset'),
                website=tech_data.get('website'),
                description=tech_data.get('description'),
                saas=tech_data.get('saas'),
                oss=tech_data.get('oss'),
                user_agent_used=user_agent,
                detection_time=detection_time
            )
        
        return None
    
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

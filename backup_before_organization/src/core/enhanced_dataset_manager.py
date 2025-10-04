#!/usr/bin/env python3
"""
Enhanced Dataset Manager

Comprehensive dataset management that utilizes all available JSON files
with intelligent merging, conflict resolution, and optimization.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union
from collections import defaultdict
import hashlib

logger = logging.getLogger(__name__)

class EnhancedDatasetManager:
    """Enhanced dataset manager with comprehensive JSON file utilization"""
    
    def __init__(self, datasets_dir: str = "json_datasets"):
        self.datasets_dir = Path(datasets_dir)
        self.datasets = {}
        self.categories = {}
        self.technologies = {}
        self.individual_files = {}
        self.merged_technologies = {}
        self.conflict_resolution = {}
        self._load_all_datasets()
    
    def _load_all_datasets(self):
        """Load all available JSON datasets"""
        logger.info("Loading all available datasets...")
        
        # Main datasets
        main_datasets = {
            'web_tech': 'web_tech_dataset.json',
            'wappalyzer_clean': 'wappalyzer_technologies_clean.json',
            'technology_lookup': 'technology_lookup_merged.json'
        }
        
        # Load main datasets
        for name, filename in main_datasets.items():
            filepath = self.datasets_dir / filename
            if filepath.exists():
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    self.datasets[name] = data
                    logger.info(f"Loaded {name} dataset: {len(data.get('technologies', {}))} technologies")
                except Exception as e:
                    logger.error(f"Failed to load {name} dataset: {e}")
        
        # Load individual Wappalyzer files
        wappalyzer_dir = self.datasets_dir / "wappalyzer_technologies"
        if wappalyzer_dir.exists():
            self._load_individual_wappalyzer_files(wappalyzer_dir)
        
        # Load report files for additional data
        self._load_report_files()
        
        # Load organized datasets
        self._load_organized_datasets()
        
        # Merge all datasets
        self._merge_all_datasets()
        
        logger.info(f"Total technologies loaded: {len(self.merged_technologies)}")
    
    def _load_individual_wappalyzer_files(self, wappalyzer_dir: Path):
        """Load individual Wappalyzer JSON files"""
        logger.info("Loading individual Wappalyzer files...")
        
        for json_file in wappalyzer_dir.glob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                if isinstance(data, dict) and 'technologies' in data:
                    self.individual_files[json_file.stem] = data
                    logger.debug(f"Loaded {json_file.name}: {len(data['technologies'])} technologies")
                elif isinstance(data, dict):
                    # Direct technology dictionary
                    self.individual_files[json_file.stem] = {'technologies': data}
                    logger.debug(f"Loaded {json_file.name}: {len(data)} technologies")
                    
            except Exception as e:
                logger.error(f"Failed to load {json_file.name}: {e}")
    
    def _load_organized_datasets(self):
        """Load organized datasets for maximum coverage"""
        organized_dir = self.datasets_dir / "organized"
        if not organized_dir.exists():
            logger.info("No organized datasets found, skipping...")
            return
        
        logger.info("Loading organized datasets...")
        
        # Load comprehensive dataset
        comprehensive_file = organized_dir / "comprehensive_technologies.json"
        if comprehensive_file.exists():
            try:
                with open(comprehensive_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                if 'technologies' in data:
                    self.datasets['organized_comprehensive'] = data['technologies']
                    logger.info(f"Loaded organized comprehensive dataset: {len(data['technologies'])} technologies")
                
                if 'categories' in data:
                    self.categories.update(data['categories'])
                    logger.info(f"Loaded {len(data['categories'])} categories from organized dataset")
                    
            except Exception as e:
                logger.error(f"Failed to load organized comprehensive dataset: {e}")
        
        # Load optimized Wappalyzer format
        wappalyzer_optimized_file = organized_dir / "wappalyzer_optimized.json"
        if wappalyzer_optimized_file.exists():
            try:
                with open(wappalyzer_optimized_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                if 'technologies' in data:
                    self.datasets['organized_wappalyzer'] = data['technologies']
                    logger.info(f"Loaded organized Wappalyzer dataset: {len(data['technologies'])} technologies")
                    
            except Exception as e:
                logger.error(f"Failed to load organized Wappalyzer dataset: {e}")
        
        # Load category-specific datasets
        for category_file in organized_dir.glob("category_*.json"):
            try:
                with open(category_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                category_name = category_file.stem.replace('category_', '')
                self.datasets[f'organized_category_{category_name}'] = data
                logger.info(f"Loaded organized category {category_name}: {len(data)} technologies")
                
            except Exception as e:
                logger.error(f"Failed to load organized category {category_file.name}: {e}")
    
    def _load_report_files(self):
        """Load report files for additional technology data"""
        report_files = [
            'merged_report.json',
            'report.json',
            'whatweb_merged_report.json'
        ]
        
        for filename in report_files:
            filepath = self.datasets_dir / filename
            if filepath.exists():
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    # Extract technologies from reports
                    if 'technologies_detected' in data:
                        self._extract_technologies_from_report(data, filename)
                        
                except Exception as e:
                    logger.debug(f"Could not load report {filename}: {e}")
    
    def _extract_technologies_from_report(self, report_data: Dict[str, Any], source: str):
        """Extract technologies from report data"""
        technologies = report_data.get('technologies_detected', [])
        
        for tech in technologies:
            if isinstance(tech, dict) and 'name' in tech:
                tech_name = tech['name']
                if tech_name not in self.individual_files:
                    self.individual_files[tech_name] = {'technologies': {}}
                
                # Convert report format to dataset format
                tech_data = {
                    'name': tech_name,
                    'confidence': tech.get('confidence', 50),
                    'category': tech.get('category', 'Unknown'),
                    'source': source,
                    'evidence': tech.get('evidence', [])
                }
                
                if tech_name not in self.individual_files[tech_name]['technologies']:
                    self.individual_files[tech_name]['technologies'][tech_name] = tech_data
    
    def _merge_all_datasets(self):
        """Intelligently merge all datasets with conflict resolution"""
        logger.info("Merging all datasets...")
        
        # Priority order: web_tech > wappalyzer_clean > individual_files > technology_lookup
        priority_order = [
            'web_tech',
            'wappalyzer_clean', 
            'technology_lookup'
        ]
        
        # Add individual files to priority
        for filename in sorted(self.individual_files.keys()):
            if filename not in priority_order:
                priority_order.append(filename)
        
        # Merge categories first
        self._merge_categories()
        
        # Merge technologies with conflict resolution
        all_technologies = {}
        conflict_log = []
        
        for source in priority_order:
            if source in self.datasets:
                dataset = self.datasets[source]
            elif source in self.individual_files:
                dataset = self.individual_files[source]
            else:
                continue
            
            if 'technologies' not in dataset:
                continue
                
            for tech_name, tech_data in dataset['technologies'].items():
                if tech_name in all_technologies:
                    # Conflict resolution
                    existing = all_technologies[tech_name]
                    resolved = self._resolve_technology_conflict(existing, tech_data, source)
                    all_technologies[tech_name] = resolved
                    conflict_log.append({
                        'technology': tech_name,
                        'existing_source': existing.get('_source', 'unknown'),
                        'new_source': source,
                        'resolution': 'merged'
                    })
                else:
                    # Add new technology
                    if isinstance(tech_data, dict):
                        tech_data['_source'] = source
                        all_technologies[tech_name] = tech_data
                    else:
                        # Handle case where tech_data is not a dict
                        all_technologies[tech_name] = {
                            'name': tech_name,
                            'description': str(tech_data),
                            '_source': source
                        }
        
        self.merged_technologies = all_technologies
        self.conflict_resolution = conflict_log
        
        logger.info(f"Merged {len(all_technologies)} technologies from {len(priority_order)} sources")
        logger.info(f"Resolved {len(conflict_log)} conflicts")
    
    def _merge_categories(self):
        """Merge categories from all datasets"""
        all_categories = {}
        
        # Merge from main datasets
        for dataset in self.datasets.values():
            if 'categories' in dataset:
                for cat_id, cat_name in dataset['categories'].items():
                    if cat_id not in all_categories:
                        all_categories[cat_id] = cat_name
        
        # Merge from individual files
        for file_data in self.individual_files.values():
            if 'categories' in file_data:
                for cat_id, cat_name in file_data['categories'].items():
                    if cat_id not in all_categories:
                        all_categories[cat_id] = cat_name
        
        self.categories = all_categories
        logger.info(f"Merged {len(all_categories)} categories")
    
    def _resolve_technology_conflict(self, existing: Dict[str, Any], new: Dict[str, Any], new_source: str) -> Dict[str, Any]:
        """Resolve conflicts between technologies from different sources"""
        resolved = existing.copy()
        
        # Ensure both are dictionaries
        if not isinstance(existing, dict):
            existing = {'name': str(existing), 'description': str(existing)}
        if not isinstance(new, dict):
            new = {'name': str(new), 'description': str(new)}
        
        # Merge patterns and evidence
        for key in ['headers', 'cookies', 'scripts', 'html', 'url', 'meta', 'dns']:
            if key in new and key in existing:
                # Merge patterns, preferring more specific ones
                existing_patterns = existing[key] if isinstance(existing[key], dict) else {}
                new_patterns = new[key] if isinstance(new[key], dict) else {}
                resolved[key] = {**existing_patterns, **new_patterns}
            elif key in new:
                resolved[key] = new[key]
        
        # Merge categories
        if 'cats' in new and 'cats' in existing:
            existing_cats = set(existing['cats']) if isinstance(existing['cats'], list) else {existing['cats']}
            new_cats = set(new['cats']) if isinstance(new['cats'], list) else {new['cats']}
            resolved['cats'] = list(existing_cats.union(new_cats))
        elif 'cats' in new:
            resolved['cats'] = new['cats']
        
        # Merge versions
        if 'versions' in new and 'versions' in existing:
            existing_versions = set(existing['versions']) if isinstance(existing['versions'], list) else {existing['versions']}
            new_versions = set(new['versions']) if isinstance(new['versions'], list) else {new['versions']}
            resolved['versions'] = list(existing_versions.union(new_versions))
        elif 'versions' in new:
            resolved['versions'] = new['versions']
        
        # Update metadata
        if '_sources' not in resolved:
            resolved['_sources'] = [existing.get('_source', 'unknown')]
        if isinstance(resolved['_sources'], list):
            resolved['_sources'].append(new_source)
        else:
            resolved['_sources'] = [resolved['_sources'], new_source]
        resolved['_last_updated'] = new_source
        
        # Prefer more detailed descriptions
        if 'description' in new and (not existing.get('description') or len(new['description']) > len(existing.get('description', ''))):
            resolved['description'] = new['description']
        
        # Prefer more recent website info
        if 'website' in new:
            resolved['website'] = new['website']
        
        return resolved
    
    def get_technology(self, name: str) -> Optional[Dict[str, Any]]:
        """Get technology data by name"""
        return self.merged_technologies.get(name)
    
    def get_category_name(self, cat_id: Union[str, int]) -> str:
        """Get category name by ID"""
        return self.categories.get(str(cat_id), str(cat_id))
    
    def search_technologies(self, query: str, limit: int = 50) -> List[str]:
        """Search technologies by name or description"""
        query_lower = query.lower()
        results = []
        
        for name, data in self.merged_technologies.items():
            if len(results) >= limit:
                break
                
            if (query_lower in name.lower() or 
                query_lower in data.get('description', '').lower()):
                results.append(name)
        
        return results
    
    def get_technologies_by_category(self, category: str) -> List[str]:
        """Get technologies by category"""
        results = []
        category_lower = category.lower()
        
        for name, data in self.merged_technologies.items():
            cats = data.get('cats', [])
            if isinstance(cats, list):
                cat_names = [self.get_category_name(cat_id) for cat_id in cats]
                if any(cat_lower in category_lower for cat_lower in [cat.lower() for cat in cat_names]):
                    results.append(name)
            elif isinstance(cats, str) and category_lower in cats.lower():
                results.append(name)
        
        return results
    
    def get_technologies_by_source(self, source: str) -> List[str]:
        """Get technologies by source"""
        results = []
        
        for name, data in self.merged_technologies.items():
            sources = data.get('_sources', [data.get('_source', 'unknown')])
            if source in sources:
                results.append(name)
        
        return results
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get dataset statistics"""
        stats = {
            'total_technologies': len(self.merged_technologies),
            'total_categories': len(self.categories),
            'sources': {},
            'categories': {},
            'conflicts_resolved': len(self.conflict_resolution)
        }
        
        # Count by source
        for tech_name, tech_data in self.merged_technologies.items():
            sources = tech_data.get('_sources', [tech_data.get('_source', 'unknown')])
            for source in sources:
                stats['sources'][source] = stats['sources'].get(source, 0) + 1
        
        # Count by category
        for tech_name, tech_data in self.merged_technologies.items():
            cats = tech_data.get('cats', [])
            if isinstance(cats, list):
                for cat_id in cats:
                    cat_name = self.get_category_name(cat_id)
                    stats['categories'][cat_name] = stats['categories'].get(cat_name, 0) + 1
            elif isinstance(cats, str):
                cat_name = self.get_category_name(cats)
                stats['categories'][cat_name] = stats['categories'].get(cat_name, 0) + 1
        
        return stats
    
    def export_merged_dataset(self, output_path: str):
        """Export merged dataset to file"""
        merged_data = {
            'categories': self.categories,
            'technologies': self.merged_technologies,
            'metadata': {
                'total_technologies': len(self.merged_technologies),
                'total_categories': len(self.categories),
                'sources': list(set().union(*[tech.get('_sources', [tech.get('_source', 'unknown')]) 
                                            for tech in self.merged_technologies.values()])),
                'conflicts_resolved': len(self.conflict_resolution),
                'generated_at': str(Path().cwd())
            }
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(merged_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Exported merged dataset to {output_path}")
    
    def get_technology_fingerprint(self, tech_name: str) -> Optional[str]:
        """Get unique fingerprint for a technology"""
        tech_data = self.get_technology(tech_name)
        if not tech_data:
            return None
        
        # Create fingerprint from key patterns
        fingerprint_data = {
            'headers': tech_data.get('headers', {}),
            'cookies': tech_data.get('cookies', {}),
            'scripts': tech_data.get('scripts', []),
            'html': tech_data.get('html', ''),
            'url': tech_data.get('url', '')
        }
        
        fingerprint_str = json.dumps(fingerprint_data, sort_keys=True)
        return hashlib.md5(fingerprint_str.encode()).hexdigest()
    
    def find_similar_technologies(self, tech_name: str, threshold: float = 0.8) -> List[Tuple[str, float]]:
        """Find similar technologies based on patterns"""
        target_tech = self.get_technology(tech_name)
        if not target_tech:
            return []
        
        target_fingerprint = self.get_technology_fingerprint(tech_name)
        if not target_fingerprint:
            return []
        
        similar = []
        
        for name, data in self.merged_technologies.items():
            if name == tech_name:
                continue
                
            fingerprint = self.get_technology_fingerprint(name)
            if not fingerprint:
                continue
            
            # Simple similarity based on fingerprint
            similarity = self._calculate_similarity(target_fingerprint, fingerprint)
            if similarity >= threshold:
                similar.append((name, similarity))
        
        return sorted(similar, key=lambda x: x[1], reverse=True)
    
    def _calculate_similarity(self, fp1: str, fp2: str) -> float:
        """Calculate similarity between two fingerprints"""
        if len(fp1) != len(fp2):
            return 0.0
        
        matches = sum(1 for a, b in zip(fp1, fp2) if a == b)
        return matches / len(fp1)

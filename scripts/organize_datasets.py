#!/usr/bin/env python3
"""
Comprehensive Dataset Organization and Optimization Script
Sorts, converts, and aligns all technology datasets for maximum coverage
"""

import json
import os
import re
from pathlib import Path
from typing import Dict, List, Any, Set, Tuple
from collections import defaultdict, Counter
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DatasetOrganizer:
    """Comprehensive dataset organization and optimization"""
    
    def __init__(self, datasets_dir: str = "json_datasets"):
        self.datasets_dir = Path(datasets_dir)
        self.output_dir = self.datasets_dir / "organized"
        self.output_dir.mkdir(exist_ok=True)
        
        # Technology categories mapping
        self.category_mapping = {
            1: 'CMS',
            2: 'Web Frameworks',
            3: 'E-commerce',
            4: 'Analytics',
            5: 'Advertising',
            6: 'Web Servers',
            7: 'Programming Languages',
            8: 'Operating Systems',
            9: 'CDN',
            10: 'Security',
            11: 'JavaScript Libraries',
            12: 'Blogs',
            13: 'Forums',
            14: 'Message Boards',
            15: 'Miscellaneous',
            16: 'Issue Trackers',
            17: 'Video Players',
            18: 'Widgets',
            19: 'Rich Text Editors',
            20: 'Webmail',
            21: 'Web Servers',
            22: 'Web Frameworks',
            23: 'Web Servers',
            24: 'Web Servers',
            25: 'Web Servers',
            26: 'Web Servers',
            27: 'Web Servers',
            28: 'Web Servers',
            29: 'Web Servers',
            30: 'Web Servers',
            31: 'Database',
            32: 'DevOps/CI',
            33: 'Search',
            34: 'UI Frameworks',
            35: 'Hosting/PAAS',
            36: 'Cookie compliance',
            37: 'JavaScript frameworks',
            38: 'Miscellaneous',
            39: 'CDN',
            40: 'Cookie compliance'
        }
        
        # Pattern field mappings
        self.pattern_fields = {
            'headers': 'header_patterns',
            'cookies': 'cookie_patterns', 
            'html': 'html_patterns',
            'scripts': 'script_patterns',
            'url': 'url_patterns',
            'meta': 'meta_patterns',
            'css': 'css_patterns',
            'text': 'text_patterns',
            'scriptSrc': 'script_src_patterns'
        }
    
    def load_all_datasets(self) -> Dict[str, Any]:
        """Load all available datasets"""
        datasets = {}
        
        # Load main datasets
        main_files = [
            'web_tech_dataset.json',
            'wappalyzer_technologies_clean.json',
            'technology_lookup_merged.json'
        ]
        
        for filename in main_files:
            file_path = self.datasets_dir / filename
            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        datasets[filename] = json.load(f)
                    logger.info(f"Loaded {filename}: {len(datasets[filename])} items")
                except Exception as e:
                    logger.error(f"Failed to load {filename}: {e}")
        
        # Load individual Wappalyzer files
        wappalyzer_dir = self.datasets_dir / 'wappalyzer'
        if wappalyzer_dir.exists():
            wappalyzer_data = {}
            for file_path in wappalyzer_dir.glob('*.json'):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        wappalyzer_data.update(data)
                except Exception as e:
                    logger.error(f"Failed to load {file_path.name}: {e}")
            
            if wappalyzer_data:
                datasets['wappalyzer_individual'] = wappalyzer_data
                logger.info(f"Loaded individual Wappalyzer files: {len(wappalyzer_data)} technologies")
        
        return datasets
    
    def normalize_technology_data(self, tech_name: str, tech_data: Dict[str, Any], source: str) -> Dict[str, Any]:
        """Normalize technology data to standard format"""
        normalized = {
            'name': tech_name,
            'source': source,
            'confidence': 0,
            'category': 'Unknown',
            'description': '',
            'website': '',
            'patterns': {},
            'versions': [],
            'evidence': [],
            'metadata': {}
        }
        
        # Extract basic info
        if 'description' in tech_data:
            normalized['description'] = str(tech_data['description'])
        
        if 'website' in tech_data:
            normalized['website'] = str(tech_data['website'])
        
        # Extract categories
        if 'cats' in tech_data:
            categories = tech_data['cats']
            if isinstance(categories, list):
                category_names = [self.category_mapping.get(cat, f'Category {cat}') for cat in categories]
                normalized['category'] = category_names[0] if category_names else 'Unknown'
                normalized['metadata']['all_categories'] = category_names
            else:
                normalized['category'] = self.category_mapping.get(categories, f'Category {categories}')
        
        # Extract patterns
        pattern_fields = ['headers', 'cookies', 'html', 'scripts', 'url', 'meta', 'css', 'text', 'scriptSrc']
        for field in pattern_fields:
            if field in tech_data:
                patterns = tech_data[field]
                if isinstance(patterns, list):
                    normalized['patterns'][field] = patterns
                elif isinstance(patterns, dict):
                    # Convert dict patterns to list
                    pattern_list = []
                    for key, value in patterns.items():
                        if isinstance(value, str):
                            pattern_list.append(f"{key}: {value}")
                        else:
                            pattern_list.append(f"{key}: {str(value)}")
                    normalized['patterns'][field] = pattern_list
                else:
                    normalized['patterns'][field] = [str(patterns)]
        
        # Extract versions
        if 'version' in tech_data:
            version = tech_data['version']
            if isinstance(version, list):
                normalized['versions'] = [str(v) for v in version]
            else:
                normalized['versions'] = [str(version)]
        
        # Calculate confidence based on evidence
        confidence = 50  # Base confidence
        if normalized['patterns']:
            confidence += 20
        if normalized['versions']:
            confidence += 15
        if normalized['description']:
            confidence += 10
        if normalized['website']:
            confidence += 5
        
        normalized['confidence'] = min(confidence, 100)
        
        return normalized
    
    def merge_technologies(self, datasets: Dict[str, Any]) -> Dict[str, Any]:
        """Merge all technologies with conflict resolution"""
        merged_technologies = {}
        source_counts = defaultdict(int)
        
        # Process each dataset
        for dataset_name, dataset_data in datasets.items():
            if dataset_name == 'web_tech_dataset.json':
                # Handle web_tech_dataset structure
                if 'technologies' in dataset_data:
                    tech_data = dataset_data['technologies']
                else:
                    tech_data = dataset_data
                
                for tech_name, tech_info in tech_data.items():
                    if isinstance(tech_info, dict):
                        normalized = self.normalize_technology_data(tech_name, tech_info, 'web_tech')
                        merged_technologies[tech_name] = normalized
                        source_counts['web_tech'] += 1
            
            elif 'wappalyzer' in dataset_name:
                for tech_name, tech_info in dataset_data.items():
                    if isinstance(tech_info, dict):
                        normalized = self.normalize_technology_data(tech_name, tech_info, 'wappalyzer')
                        
                        # Merge with existing if present
                        if tech_name in merged_technologies:
                            merged_technologies[tech_name] = self.resolve_conflict(
                                merged_technologies[tech_name], normalized
                            )
                        else:
                            merged_technologies[tech_name] = normalized
                        source_counts['wappalyzer'] += 1
            
            elif dataset_name == 'technology_lookup_merged.json':
                for tech_name, tech_info in dataset_data.items():
                    if isinstance(tech_info, dict):
                        normalized = self.normalize_technology_data(tech_name, tech_info, 'technology_lookup')
                        
                        # Merge with existing if present
                        if tech_name in merged_technologies:
                            merged_technologies[tech_name] = self.resolve_conflict(
                                merged_technologies[tech_name], normalized
                            )
                        else:
                            merged_technologies[tech_name] = normalized
                        source_counts['technology_lookup'] += 1
        
        logger.info(f"Merged technologies from sources: {dict(source_counts)}")
        return merged_technologies
    
    def resolve_conflict(self, existing: Dict[str, Any], new: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve conflicts between technology entries"""
        # Prefer higher confidence
        if new['confidence'] > existing['confidence']:
            existing, new = new, existing
        
        # Merge patterns
        for field, patterns in new['patterns'].items():
            if field in existing['patterns']:
                existing['patterns'][field].extend(patterns)
                existing['patterns'][field] = list(set(existing['patterns'][field]))  # Remove duplicates
            else:
                existing['patterns'][field] = patterns
        
        # Merge versions
        existing['versions'].extend(new['versions'])
        existing['versions'] = list(set(existing['versions']))  # Remove duplicates
        
        # Update metadata
        if 'sources' not in existing['metadata']:
            existing['metadata']['sources'] = [existing['source']]
        existing['metadata']['sources'].append(new['source'])
        existing['metadata']['sources'] = list(set(existing['metadata']['sources']))
        
        return existing
    
    def sort_technologies(self, technologies: Dict[str, Any]) -> Dict[str, Any]:
        """Sort technologies by category and confidence"""
        # Group by category
        by_category = defaultdict(list)
        for tech_name, tech_data in technologies.items():
            category = tech_data['category']
            by_category[category].append((tech_name, tech_data))
        
        # Sort within each category by confidence (descending)
        sorted_technologies = {}
        for category, tech_list in by_category.items():
            tech_list.sort(key=lambda x: x[1]['confidence'], reverse=True)
            for tech_name, tech_data in tech_list:
                sorted_technologies[tech_name] = tech_data
        
        return sorted_technologies
    
    def generate_statistics(self, technologies: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive statistics"""
        stats = {
            'total_technologies': len(technologies),
            'by_category': Counter(),
            'by_source': Counter(),
            'by_confidence': Counter(),
            'pattern_coverage': Counter(),
            'version_coverage': Counter()
        }
        
        for tech_name, tech_data in technologies.items():
            # Category stats
            stats['by_category'][tech_data['category']] += 1
            
            # Source stats
            if 'sources' in tech_data['metadata']:
                for source in tech_data['metadata']['sources']:
                    stats['by_source'][source] += 1
            else:
                stats['by_source'][tech_data['source']] += 1
            
            # Confidence stats
            confidence_range = (tech_data['confidence'] // 20) * 20
            stats['by_confidence'][f"{confidence_range}-{confidence_range+19}"] += 1
            
            # Pattern coverage
            pattern_count = len(tech_data['patterns'])
            stats['pattern_coverage'][f"{pattern_count} patterns"] += 1
            
            # Version coverage
            if tech_data['versions']:
                stats['version_coverage']['has_versions'] += 1
            else:
                stats['version_coverage']['no_versions'] += 1
        
        return stats
    
    def save_organized_datasets(self, technologies: Dict[str, Any], stats: Dict[str, Any]):
        """Save organized datasets in multiple formats"""
        
        # Save main organized dataset
        organized_data = {
            'meta': {
                'name': 'Comprehensive Technology Detection Dataset',
                'version': '2.0',
                'generated_at': str(Path().cwd()),
                'total_technologies': len(technologies),
                'statistics': stats
            },
            'categories': self.category_mapping,
            'technologies': technologies
        }
        
        with open(self.output_dir / 'comprehensive_technologies.json', 'w', encoding='utf-8') as f:
            json.dump(organized_data, f, indent=2, ensure_ascii=False)
        
        # Save by category
        by_category = defaultdict(dict)
        for tech_name, tech_data in technologies.items():
            category = tech_data['category']
            by_category[category][tech_name] = tech_data
        
        for category, techs in by_category.items():
            safe_category = re.sub(r'[^\w\-_]', '_', category)
            with open(self.output_dir / f'category_{safe_category}.json', 'w', encoding='utf-8') as f:
                json.dump(techs, f, indent=2, ensure_ascii=False)
        
        # Save statistics
        with open(self.output_dir / 'statistics.json', 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)
        
        # Save optimized Wappalyzer format
        wappalyzer_format = {
            'categories': self.category_mapping,
            'technologies': {}
        }
        
        for tech_name, tech_data in technologies.items():
            wappalyzer_tech = {
                'cats': [k for k, v in self.category_mapping.items() if v == tech_data['category']],
                'description': tech_data['description'],
                'website': tech_data['website']
            }
            
            # Convert patterns to Wappalyzer format
            for field, patterns in tech_data['patterns'].items():
                if patterns:
                    wappalyzer_tech[field] = patterns[0] if len(patterns) == 1 else patterns
            
            wappalyzer_format['technologies'][tech_name] = wappalyzer_tech
        
        with open(self.output_dir / 'wappalyzer_optimized.json', 'w', encoding='utf-8') as f:
            json.dump(wappalyzer_format, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved organized datasets to {self.output_dir}")
    
    def run_organization(self):
        """Run complete dataset organization"""
        logger.info("Starting comprehensive dataset organization...")
        
        # Load all datasets
        datasets = self.load_all_datasets()
        logger.info(f"Loaded {len(datasets)} datasets")
        
        # Merge technologies
        merged_technologies = self.merge_technologies(datasets)
        logger.info(f"Merged {len(merged_technologies)} technologies")
        
        # Sort technologies
        sorted_technologies = self.sort_technologies(merged_technologies)
        logger.info("Sorted technologies by category and confidence")
        
        # Generate statistics
        stats = self.generate_statistics(sorted_technologies)
        logger.info("Generated comprehensive statistics")
        
        # Save organized datasets
        self.save_organized_datasets(sorted_technologies, stats)
        
        # Print summary
        print("\n" + "="*60)
        print(" DATASET ORGANIZATION COMPLETE")
        print("="*60)
        print(f"Total Technologies: {stats['total_technologies']}")
        print(f"Categories: {len(stats['by_category'])}")
        print(f"Sources: {len(stats['by_source'])}")
        print("\nTop Categories:")
        for category, count in stats['by_category'].most_common(10):
            print(f"  {category}: {count}")
        print("\nSource Distribution:")
        for source, count in stats['by_source'].most_common():
            print(f"  {source}: {count}")
        print(f"\nOrganized datasets saved to: {self.output_dir}")
        print("="*60)

if __name__ == "__main__":
    organizer = DatasetOrganizer()
    organizer.run_organization()

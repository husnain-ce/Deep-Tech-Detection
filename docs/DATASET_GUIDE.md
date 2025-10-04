# Dataset Guide

## Overview

The Tech Detection System uses multiple organized datasets for comprehensive technology detection:

- **Core Dataset**: 241 custom technologies
- **Wappalyzer Dataset**: 3,774 technologies from Wappalyzer
- **Technology Lookup**: 1,530 technologies from Technology Lookup
- **Organized Datasets**: 3,954 merged and optimized technologies

## Dataset Structure

### Comprehensive Technologies

Location: `data/datasets/organized/comprehensive_technologies.json`

```json
{
  "meta": {
    "name": "Comprehensive Technology Detection Dataset",
    "version": "2.0",
    "total_technologies": 3954
  },
  "categories": {
    "1": "CMS",
    "2": "Web Frameworks",
    ...
  },
  "technologies": {
    "Technology Name": {
      "name": "Technology Name",
      "source": "wappalyzer",
      "confidence": 80,
      "category": "Web Frameworks",
      "description": "Technology description",
      "website": "https://example.com",
      "patterns": {
        "headers": ["X-Powered-By: Technology"],
        "scripts": ["technology.js"],
        "html": ["<div class="technology""]
      },
      "versions": ["1.0", "2.0"],
      "evidence": [...],
      "metadata": {...}
    }
  }
}
```

### Category-Specific Datasets

Location: `data/datasets/organized/category_*.json`

Each category has its own optimized dataset file for faster loading.

## Adding Custom Technologies

1. Add to appropriate dataset file
2. Run organization script: `python scripts/organize_datasets.py`
3. Restart detection system

## Dataset Statistics

View current statistics: `data/datasets/organized/statistics.json`

- Total technologies by category
- Source distribution
- Pattern coverage
- Version coverage

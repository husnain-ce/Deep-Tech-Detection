# JSON Datasets

This folder contains all the JSON technology detection datasets used by the Web Technology Detection System.

## Dataset Files

### Core Technology Datasets

#### `web_tech_dataset.json` (2,480+ technologies)
- **Source**: Original Tech Detection dataset
- **Description**: Comprehensive dataset covering front-end, back-end, CMS, headless CMS, hosting/CDN, analytics, e-commerce, payments, security, CI/CD, A/B testing, and more
- **Categories**: 30+ technology categories
- **Features**: Evidence-based detection with confidence scoring, version extraction, and relationship rules (implies/requires/excludes)

#### `wappalyzer_technologies_clean.json` (3,774 technologies)
- **Source**: Wappalyzer repository (tomnomnom/wappalyzer)
- **Description**: Clean merged dataset from all Wappalyzer technology JSON files (a.json through z.json)
- **Categories**: 102 different technology categories
- **Features**: Comprehensive detection patterns including headers, cookies, scripts, HTML, and DNS patterns

#### `technology_lookup_merged.json` (1,530 technologies)
- **Source**: Technology Lookup Web Application repository (sahilrahmann/Technology-Lookup-Web-Application)
- **Description**: Merged dataset from both JSON and CSV sources
- **Features**: Additional technology signatures and detection patterns

### Individual Wappalyzer Files
The `wappalyzer/` subfolder contains individual JSON files:
- `_.json` through `z.json` (27 files total)
- Each file contains 12-441 technologies
- These are the source files that were merged into `wappalyzer_technologies_clean.json`

### Report Files
The `individual_reports/` subfolder contains sample detection reports:
- `merged_report.json` - Sample detection report showing merged results from multiple engines
- `report.json` - Sample detection report from the core dataset
- `whatweb_merged_report.json` - Sample WhatWeb detection report

## Total Technology Coverage

- **Original Dataset**: 2,480+ technologies
- **Wappalyzer Dataset**: 3,774 technologies
- **Technology Lookup Dataset**: 1,530 technologies
- **Total Unique Technologies**: 7,000+ technologies

## Usage

### Basic Detection (Dataset Only)
```bash
python main.py https://example.com --dataset json_datasets/web_tech_dataset.json --json
```

### Full Multi-Engine Analysis
```bash
python main.py https://example.com \
  --dataset json_datasets/web_tech_dataset.json \
  --whatweb --whatweb-path ./WhatWeb/whatweb --whatweb-aggr 3 \
  --wappalyzer --wappalyzer-update \
  --json > json_datasets/individual_reports/detection_report.json
```

### Using Wappalyzer Dataset
```bash
python main.py https://example.com --dataset json_datasets/wappalyzer_technologies_clean.json --json
```

### Using Technology Lookup Dataset
```bash
python main.py https://example.com --dataset json_datasets/technology_lookup_merged.json --json
```

## Dataset Structure

Each technology entry typically contains:
- **Detection Patterns**: Headers, cookies, scripts, HTML patterns, DNS records
- **Categories**: Technology classification
- **Descriptions**: Detailed technology information
- **Confidence Scoring**: Detection confidence levels
- **Version Extraction**: Version detection patterns
- **Relationships**: Implies/requires/excludes rules
- **Metadata**: Icons, websites, pricing information

## Detection Capabilities

The combined datasets enable detection of:
- **Web Frameworks**: React, Vue.js, Angular, Django, Laravel, etc.
- **CMS Platforms**: WordPress, Drupal, Joomla, Ghost, etc.
- **E-commerce**: Shopify, WooCommerce, Magento, PrestaShop, etc.
- **Analytics**: Google Analytics, Adobe Analytics, Mixpanel, etc.
- **CDNs**: Cloudflare, AWS CloudFront, MaxCDN, etc.
- **Security**: WAFs, SSL certificates, security headers
- **Hosting**: Apache, Nginx, IIS, various hosting providers
- **And much more...**

## Updates

To update the datasets:
1. Re-run the cloning scripts to get latest versions
2. Update the merged files accordingly
3. Test with sample websites to ensure accuracy

## Notes

- All datasets are in JSON format for easy parsing and integration
- Detection patterns use regex for flexible matching
- Confidence scores help prioritize detection results
- Evidence arrays provide transparency in detection reasoning
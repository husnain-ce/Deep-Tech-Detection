# Advanced Web Technology Detection System

##  Overview

The Advanced Web Technology Detection System is an enterprise-grade solution that combines multiple detection engines and datasets to provide comprehensive web technology identification. It's designed for maximum accuracy, performance, and scalability.

## 🏗️ Architecture

### Core Components

1. **AdvancedTechDetector** - Main detection engine with pattern matching
2. **DatasetManager** - Intelligent dataset management and merging
3. **WhatWebIntegration** - WhatWeb binary integration
4. **WappalyzerIntegration** - Wappalyzer library integration
5. **OutputFormatter** - Multiple output format support

### Detection Engines

- **Dataset Engine**: Custom pattern matching with 7,000+ technologies
- **WhatWeb Engine**: Ruby-based detection with 1,800+ plugins
- **Wappalyzer Engine**: JavaScript-based detection with version extraction

## 📦 Installation

### Quick Install

```bash
# Clone the repository
git clone <repository-url>
cd Tech-Detection

# Run the advanced installer
python install_advanced.py

# Or install manually
pip install -r requirements_advanced.txt
```

### Manual Installation

```bash
# Install Python dependencies
pip install requests beautifulsoup4 dnspython python-Wappalyzer

# Install WhatWeb (Linux/macOS)
sudo apt-get install whatweb  # Ubuntu/Debian
brew install whatweb          # macOS

# Create directories
mkdir -p json_datasets integrations logs cache reports
```

##  Usage

### Basic Usage

```bash
# Single URL analysis
python webtech_matcher_advanced.py https://example.com

# With all engines
python webtech_matcher_advanced.py https://example.com --use-whatweb --use-wappalyzer

# High confidence analysis
python webtech_matcher_advanced.py https://example.com --min-confidence 50 --max-results 20
```

### Advanced Usage

```bash
# Batch processing
python webtech_matcher_advanced.py --batch urls.txt --workers 10 --output csv

# Custom output formats
python webtech_matcher_advanced.py https://example.com --output html --save-report report.html

# Debug mode
python webtech_matcher_advanced.py https://example.com --debug --dump --verbose

# Custom WhatWeb settings
python webtech_matcher_advanced.py https://example.com --use-whatweb --whatweb-aggression 4
```

### Python API Usage

```python
import asyncio
from webtech_matcher_advanced import WebTechMatcherAdvanced

async def analyze_website():
    matcher = WebTechMatcherAdvanced()
    
    # Single URL
    result = await matcher.analyze_url("https://example.com", {
        'use_whatweb': True,
        'use_wappalyzer': True,
        'min_confidence': 20
    })
    
    print(f"Detected {len(result.technologies)} technologies")
    for tech in result.technologies:
        print(f"- {tech.name} ({tech.confidence}%)")

# Run the analysis
asyncio.run(analyze_website())
```

##  Configuration

### Configuration File (config.json)

```json
{
  "datasets": {
    "directory": "json_datasets",
    "web_tech_dataset": "web_tech_dataset.json",
    "wappalyzer_dataset": "wappalyzer_technologies_clean.json"
  },
  "engines": {
    "whatweb": {
      "enabled": true,
      "path": "whatweb",
      "timeout": 30,
      "aggression": 3
    },
    "wappalyzer": {
      "enabled": true,
      "update_on_init": false
    }
  },
  "performance": {
    "max_workers": 5,
    "cache_enabled": true,
    "cache_ttl": 3600
  }
}
```

##  Output Formats

### JSON Output

```json
{
  "url": "https://example.com",
  "final_url": "https://example.com",
  "technologies": [
    {
      "name": "WordPress",
      "confidence": 85,
      "category": "CMS",
      "versions": ["5.8.1"],
      "evidence": [
        {
          "field": "html",
          "detail": "HTML content",
          "match": "wp-content/themes",
          "confidence": 40,
          "version": null
        }
      ],
      "source": "dataset",
      "website": "https://wordpress.org",
      "description": "WordPress is a content management system"
    }
  ],
  "analysis_time": 2.34,
  "metadata": {
    "summary": {
      "total_technologies": 15,
      "by_source": {
        "dataset": 10,
        "whatweb": 3,
        "wappalyzer": 2
      }
    }
  }
}
```

### HTML Output

Generates a comprehensive HTML report with:
- Technology details and confidence scores
- Evidence for each detection
- Category breakdown
- Visual confidence indicators

### CSV Output

```csv
Name,Confidence,Category,Versions,Source,Website,Description
WordPress,85,CMS,"5.8.1",dataset,https://wordpress.org,WordPress is a content management system
jQuery,70,JavaScript Libraries,"3.6.0",wappalyzer,https://jquery.com,jQuery is a JavaScript library
```

##  Performance Optimization

### Parallel Processing

```bash
# Use multiple workers for batch processing
python webtech_matcher_advanced.py --batch urls.txt --workers 20

# Adjust worker count based on system resources
python webtech_matcher_advanced.py --batch urls.txt --workers $(nproc)
```

### Caching

```bash
# Enable caching for repeated analysis
python webtech_matcher_advanced.py https://example.com --cache --cache-ttl 7200
```

### Memory Management

```python
# For large-scale analysis
options = {
    'max_results': 50,  # Limit results per URL
    'min_confidence': 30,  # Filter low-confidence results
    'use_dataset': True,   # Use only dataset (fastest)
    'use_whatweb': False,  # Disable slower engines
    'use_wappalyzer': False
}
```

##  Detection Capabilities

### Technology Categories

- **Web Frameworks**: React, Vue.js, Angular, Django, Laravel
- **CMS Platforms**: WordPress, Drupal, Joomla, Ghost
- **E-commerce**: Shopify, WooCommerce, Magento, PrestaShop
- **Analytics**: Google Analytics, Adobe Analytics, Mixpanel
- **CDNs**: Cloudflare, AWS CloudFront, MaxCDN
- **Security**: WAFs, SSL certificates, security headers
- **Hosting**: Apache, Nginx, IIS, various providers

### Detection Methods

1. **Header Analysis**: HTTP headers, cookies, meta tags
2. **Content Analysis**: HTML patterns, script sources
3. **URL Analysis**: Path patterns, query parameters
4. **DNS Analysis**: CNAME records, subdomain patterns
5. **JavaScript Analysis**: Library detection, framework signatures

##  Advanced Features

### Custom Pattern Development

```python
# Add custom technology patterns
custom_tech = {
    "name": "Custom Framework",
    "headers": {
        "X-Powered-By": "CustomFramework"
    },
    "html": "<!-- Custom Framework -->",
    "scripts": ["custom-framework\\.js"],
    "confidence": 80,
    "category": "Web Framework"
}
```

### Batch Processing with Progress

```python
import asyncio
from tqdm import tqdm

async def batch_analysis_with_progress(urls):
    matcher = WebTechMatcherAdvanced()
    results = []
    
    with tqdm(total=len(urls)) as pbar:
        for url in urls:
            result = await matcher.analyze_url(url)
            results.append(result)
            pbar.update(1)
    
    return results
```

### Integration with Other Tools

```python
# Integration with vulnerability scanners
def scan_with_tech_detection(url):
    # Detect technologies first
    matcher = WebTechMatcherAdvanced()
    result = await matcher.analyze_url(url)
    
    # Use detected technologies for targeted scanning
    for tech in result.technologies:
        if tech.name == "WordPress":
            # Run WordPress-specific scans
            run_wordpress_scan(url)
        elif tech.name == "Apache":
            # Run Apache-specific scans
            run_apache_scan(url)
```

##  Monitoring and Logging

### Log Configuration

```python
import logging

# Configure detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('tech_detection.log'),
        logging.StreamHandler()
    ]
)
```

### Performance Monitoring

```python
import time
import psutil

def monitor_performance():
    start_time = time.time()
    start_memory = psutil.Process().memory_info().rss
    
    # Run analysis
    result = await matcher.analyze_url(url)
    
    end_time = time.time()
    end_memory = psutil.Process().memory_info().rss
    
    print(f"Analysis time: {end_time - start_time:.2f}s")
    print(f"Memory used: {(end_memory - start_memory) / 1024 / 1024:.2f} MB")
```

##  Troubleshooting

### Common Issues

1. **WhatWeb not found**
   ```bash
   # Install WhatWeb
   sudo apt-get install whatweb
   # Or specify custom path
   python webtech_matcher_advanced.py --whatweb-path /usr/local/bin/whatweb
   ```

2. **Wappalyzer import error**
   ```bash
   # Install Wappalyzer
   pip install python-Wappalyzer
   ```

3. **Memory issues with large datasets**
   ```python
   # Reduce memory usage
   options = {
       'max_results': 20,
       'use_dataset': True,
       'use_whatweb': False,
       'use_wappalyzer': False
   }
   ```

### Debug Mode

```bash
# Enable debug mode for detailed output
python webtech_matcher_advanced.py https://example.com --debug --verbose --dump
```

##  API Reference

### WebTechMatcherAdvanced

```python
class WebTechMatcherAdvanced:
    def __init__(self, datasets_dir: str = "json_datasets")
    async def analyze_url(self, url: str, options: Dict[str, Any] = None) -> AnalysisResult
    async def analyze_batch(self, urls: List[str], options: Dict[str, Any] = None) -> List[AnalysisResult]
```

### AnalysisResult

```python
@dataclass
class AnalysisResult:
    url: str
    final_url: str
    technologies: List[DetectionResult]
    analysis_time: float
    metadata: Dict[str, Any]
    errors: List[str]
    warnings: List[str]
```

### DetectionResult

```python
@dataclass
class DetectionResult:
    name: str
    confidence: int
    category: str
    versions: List[str]
    evidence: List[Dict[str, Any]]
    source: str
    website: Optional[str]
    description: Optional[str]
```

##  Contributing

1. Fork the repository
2. Create a feature branch
3. Add your improvements
4. Add tests
5. Submit a pull request

##  License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- GitHub Issues: [Create an issue](https://github.com/your-repo/issues)
- Documentation: [Read the docs](https://your-docs-url.com)
- Community: [Join our Discord](https://discord.gg/your-server)

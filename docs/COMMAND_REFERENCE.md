# Command Reference - Advanced Web Technology Detection

## 🚀 Quick Start Commands

### Basic Detection
```bash
# Single URL analysis
python webtech_matcher_advanced.py https://example.com

# With all detection engines
python webtech_matcher_advanced.py https://example.com --use-whatweb --use-wappalyzer

# High confidence only
python webtech_matcher_advanced.py https://example.com --min-confidence 50
```

### Batch Processing
```bash
# Process multiple URLs
python webtech_matcher_advanced.py --batch urls.txt

# Parallel processing
python webtech_matcher_advanced.py --batch urls.txt --workers 10

# With custom delay
python webtech_matcher_advanced.py --batch urls.txt --delay 0.5
```

## 📊 Output Formats

### JSON Output
```bash
# Pretty JSON
python webtech_matcher_advanced.py https://example.com --output json --pretty

# Save to file
python webtech_matcher_advanced.py https://example.com --output json --save-report report.json
```

### HTML Report
```bash
# Generate HTML report
python webtech_matcher_advanced.py https://example.com --output html --save-report report.html
```

### CSV Export
```bash
# CSV format for spreadsheet analysis
python webtech_matcher_advanced.py https://example.com --output csv --save-report results.csv
```

### XML Output
```bash
# XML format
python webtech_matcher_advanced.py https://example.com --output xml
```

## 🔧 Detection Engine Options

### Dataset Engine (Default)
```bash
# Use only dataset (fastest)
python webtech_matcher_advanced.py https://example.com --use-dataset

# Disable dataset
python webtech_matcher_advanced.py https://example.com --no-dataset
```

### WhatWeb Integration
```bash
# Basic WhatWeb
python webtech_matcher_advanced.py https://example.com --use-whatweb

# Custom WhatWeb path
python webtech_matcher_advanced.py https://example.com --use-whatweb --whatweb-path /usr/local/bin/whatweb

# WhatWeb aggression level (0-4)
python webtech_matcher_advanced.py https://example.com --use-whatweb --whatweb-aggression 4
```

### Wappalyzer Integration
```bash
# Basic Wappalyzer
python webtech_matcher_advanced.py https://example.com --use-wappalyzer

# Update Wappalyzer data
python webtech_matcher_advanced.py https://example.com --use-wappalyzer --wappalyzer-update
```

## ⚙️ Analysis Options

### Confidence and Filtering
```bash
# Minimum confidence threshold
python webtech_matcher_advanced.py https://example.com --min-confidence 30

# Maximum number of results
python webtech_matcher_advanced.py https://example.com --max-results 50

# Combine filters
python webtech_matcher_advanced.py https://example.com --min-confidence 40 --max-results 25
```

### Request Options
```bash
# Custom timeout
python webtech_matcher_advanced.py https://example.com --timeout 60

# Custom user agent
python webtech_matcher_advanced.py https://example.com --user-agent "Custom Bot 1.0"

# Disable redirects
python webtech_matcher_advanced.py https://example.com --no-redirects
```

## 🐛 Debug and Verbose Options

### Debug Mode
```bash
# Full debug output
python webtech_matcher_advanced.py https://example.com --debug --verbose --dump

# Debug with custom log file
python webtech_matcher_advanced.py https://example.com --debug --log-file debug.log
```

### Verbose Output
```bash
# Verbose mode
python webtech_matcher_advanced.py https://example.com --verbose

# Very verbose
python webtech_matcher_advanced.py https://example.com --verbose --debug
```

## 🚀 Performance Optimization

### Parallel Processing
```bash
# High-performance batch processing
python webtech_matcher_advanced.py --batch urls.txt --workers 20

# Conservative batch processing
python webtech_matcher_advanced.py --batch urls.txt --workers 5 --delay 1.0
```

### Caching
```bash
# Enable caching
python webtech_matcher_advanced.py https://example.com --cache

# Custom cache TTL
python webtech_matcher_advanced.py https://example.com --cache --cache-ttl 7200
```

### Memory Optimization
```bash
# Limit results to reduce memory usage
python webtech_matcher_advanced.py https://example.com --max-results 20

# Use only dataset engine (lowest memory)
python webtech_matcher_advanced.py https://example.com --use-dataset --no-whatweb --no-wappalyzer
```

## 📁 File and Directory Options

### Custom Datasets
```bash
# Custom datasets directory
python webtech_matcher_advanced.py https://example.com --datasets-dir /path/to/datasets
```

### Batch Files
```bash
# Process URLs from file
python webtech_matcher_advanced.py --batch urls.txt

# Process with custom options
python webtech_matcher_advanced.py --batch urls.txt --output csv --workers 10
```

### Report Saving
```bash
# Save all formats
python webtech_matcher_advanced.py https://example.com --output json --save-report report.json
python webtech_matcher_advanced.py https://example.com --output html --save-report report.html
python webtech_matcher_advanced.py https://example.com --output csv --save-report report.csv
```

## 🔍 Advanced Analysis

### Technology-Specific Analysis
```bash
# Focus on specific categories
python webtech_matcher_advanced.py https://example.com --min-confidence 60 --max-results 10

# Analyze with specific engines
python webtech_matcher_advanced.py https://example.com --use-whatweb --whatweb-aggression 4
```

### Comparison Analysis
```bash
# Compare detection engines
python webtech_matcher_advanced.py https://example.com --use-dataset --use-whatweb --use-wappalyzer --output json --save-report comparison.json
```

### Large-Scale Analysis
```bash
# Process thousands of URLs
python webtech_matcher_advanced.py --batch large_urls.txt --workers 50 --delay 0.1 --output csv --save-report large_analysis.csv
```

## 🛠️ Maintenance Commands

### Update Datasets
```bash
# Update Wappalyzer data
python webtech_matcher_advanced.py https://example.com --use-wappalyzer --wappalyzer-update
```

### Test Installation
```bash
# Test all components
python install_advanced.py

# Test specific engine
python -c "from integrations.whatweb_integration import WhatWebIntegration; print('WhatWeb OK')"
python -c "from integrations.wappalyzer_integration import WappalyzerIntegration; print('Wappalyzer OK')"
```

### Clean Up
```bash
# Clear cache
rm -rf cache/*

# Clear logs
rm -f *.log

# Clear reports
rm -f reports/*
```

## 📊 Monitoring Commands

### Performance Monitoring
```bash
# Monitor with system resources
python webtech_matcher_advanced.py https://example.com --debug --verbose 2>&1 | tee analysis.log

# Batch monitoring
python webtech_matcher_advanced.py --batch urls.txt --workers 10 --verbose 2>&1 | tee batch_analysis.log
```

### Log Analysis
```bash
# View recent logs
tail -f webtech_matcher.log

# Search for errors
grep "ERROR" webtech_matcher.log

# Count detections
grep "technologies detected" webtech_matcher.log | wc -l
```

## 🔧 Troubleshooting Commands

### Check Dependencies
```bash
# Check Python packages
pip list | grep -E "(requests|beautifulsoup4|dnspython|Wappalyzer)"

# Check WhatWeb
whatweb --version

# Check system resources
free -h
df -h
```

### Test Individual Components
```bash
# Test dataset detection only
python webtech_matcher_advanced.py https://example.com --use-dataset --no-whatweb --no-wappalyzer

# Test WhatWeb only
python webtech_matcher_advanced.py https://example.com --no-dataset --use-whatweb --no-wappalyzer

# Test Wappalyzer only
python webtech_matcher_advanced.py https://example.com --no-dataset --no-whatweb --use-wappalyzer
```

### Debug Specific Issues
```bash
# Debug WhatWeb issues
python webtech_matcher_advanced.py https://example.com --use-whatweb --debug --verbose

# Debug Wappalyzer issues
python webtech_matcher_advanced.py https://example.com --use-wappalyzer --debug --verbose

# Debug memory issues
python webtech_matcher_advanced.py https://example.com --max-results 5 --debug --verbose
```

## 🎯 Use Case Examples

### Security Assessment
```bash
# Comprehensive security analysis
python webtech_matcher_advanced.py https://target.com --use-whatweb --use-wappalyzer --min-confidence 30 --output json --save-report security_analysis.json
```

### Technology Audit
```bash
# Technology audit for compliance
python webtech_matcher_advanced.py --batch company_urls.txt --output csv --save-report tech_audit.csv --workers 20
```

### Competitive Analysis
```bash
# Analyze competitor technologies
python webtech_matcher_advanced.py --batch competitors.txt --output html --save-report competitor_analysis.html --use-whatweb --use-wappalyzer
```

### Development Testing
```bash
# Test during development
python webtech_matcher_advanced.py http://localhost:3000 --debug --dump --output json
```

### Production Monitoring
```bash
# Monitor production sites
python webtech_matcher_advanced.py --batch production_urls.txt --output json --save-report production_monitor.json --workers 5 --delay 2.0
```

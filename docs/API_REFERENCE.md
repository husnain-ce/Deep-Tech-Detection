# API Reference

## Core Classes

### UltimateTechDetector

Main detection class that orchestrates all detection engines.

```python
from src.core.tech_detector import UltimateTechDetector

detector = UltimateTechDetector()
result = await detector.analyze_url("https://example.com")
```

### EnhancedDatasetManager

Manages all technology datasets with intelligent merging.

```python
from src.core.enhanced_dataset_manager import EnhancedDatasetManager

manager = EnhancedDatasetManager()
technologies = manager.get_technologies()
```

### DynamicWhatWebIntegration

WhatWeb integration with dynamic timeout based on site complexity.

```python
from src.integrations.dynamic_whatweb_integration import DynamicWhatWebIntegration

whatweb = DynamicWhatWebIntegration()
result, error = whatweb.analyze_url("https://example.com")
```

## Detection Results

### DetectionResult

Standard result object for all detected technologies.

```python
@dataclass
class DetectionResult:
    name: str
    confidence: int
    category: str
    versions: List[str]
    evidence: List[Dict[str, Any]]
    source: str
    website: Optional[str] = None
    description: Optional[str] = None
    saas: Optional[bool] = None
    oss: Optional[bool] = None
    user_agent_used: Optional[str] = None
    detection_time: float = 0.0
```

## Command Line Interface

```bash
python main.py <URL> [OPTIONS]

Options:
  --use-dataset              Use core dataset detection
  --use-whatweb              Use WhatWeb integration
  --use-wappalyzer           Use Wappalyzer integration
  --user-agents N            Number of user agents to try
  --preferred-browser TYPE   Preferred browser type
  --min-confidence N         Minimum confidence threshold
  --max-results N            Maximum results to return
  --timeout N                Request timeout in seconds
  --output FORMAT            Output format (default: json)
  --save-report FILE         Save JSON report to file
  --verbose                  Verbose output
  --debug                    Debug output

Output Formats:
  json (default)             Pretty-printed JSON with indentation
  csv                        Comma-separated values
  table                      Human-readable table
  text                       Plain text format
```

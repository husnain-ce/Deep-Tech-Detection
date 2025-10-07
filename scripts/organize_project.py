#!/usr/bin/env python3
"""
Comprehensive Project Organization Script
Organizes the entire Tech-Detection project for maximum maintainability and clarity
"""

import os
import shutil
import json
from pathlib import Path
from typing import Dict, List, Any
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ProjectOrganizer:
    """Comprehensive project organization and structure optimization"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).resolve()
        self.backup_dir = self.project_root / "backup_before_organization"
        
        # Define the new organized structure
        self.new_structure = {
            "src": {
                "core": [
                    "tech_detector.py",
                    "enhanced_tech_detector.py", 
                    "enhanced_dataset_manager.py",
                    "webtech_matcher_advanced.py"
                ],
                "integrations": [
                    "whatweb_integration.py",
                    "dynamic_whatweb_integration.py",
                    "wappalyzer_integration.py",
                    "__init__.py"
                ],
                "utils": [
                    "user_agents.py",
                    "__init__.py"
                ],
                "__init__.py": ""
            },
            "data": {
                "datasets": {
                    "raw": [
                        "web_tech_dataset.json",
                        "wappalyzer_technologies_clean.json",
                        "technology_lookup_merged.json"
                    ],
                    "individual": [
                        "wappalyzer"
                    ],
                    "organized": [
                        "comprehensive_technologies.json",
                        "wappalyzer_optimized.json",
                        "statistics.json",
                        "category_*.json"
                    ],
                    "reports": [
                        "individual_reports"
                    ]
                },
                "external_tools": [
                    "WhatWeb"
                ]
            },
            "scripts": [
                "organize_datasets.py",
                "organize_project.py",
                "setup.py",
                "install.py"
            ],
            "docs": [
                "README.md",
                "API_REFERENCE.md",
                "DATASET_GUIDE.md",
                "COMMAND_REFERENCE.md",
                "CHANGELOG.md"
            ],
            "config": [
                "config.json",
                "requirements.txt",
                "requirements_advanced.txt"
            ],
            "tests": [
                "test_core.py",
                "test_integrations.py",
                "test_datasets.py",
                "__init__.py"
            ],
            "examples": [
                "basic_usage.py",
                "advanced_usage.py",
                "custom_detection.py"
            ],
            "output": [
                "reports",
                "logs"
            ],
            "launchers": {
                "unix": [
                    "detect.sh",
                    "deep_detection.sh"
                ],
                "windows": [
                    "detect.bat",
                    "deep_detection.bat"
                ],
                "powershell": [
                    "detect.ps1",
                    "deep_detection.ps1"
                ]
            }
        }
    
    def create_backup(self):
        """Create backup of current project before reorganization"""
        logger.info("Creating backup of current project...")
        
        if self.backup_dir.exists():
            shutil.rmtree(self.backup_dir)
        
        # Copy important files to backup
        important_files = [
            "main.py",
            "src/",
            "json_datasets/",
            "scripts/",
            "requirements.txt",
            "README.md"
        ]
        
        self.backup_dir.mkdir(exist_ok=True)
        
        for item in important_files:
            src = self.project_root / item
            dst = self.backup_dir / item
            
            if src.exists():
                if src.is_dir():
                    shutil.copytree(src, dst)
                else:
                    shutil.copy2(src, dst)
        
        logger.info(f"Backup created at: {self.backup_dir}")
    
    def create_new_structure(self):
        """Create the new organized directory structure"""
        logger.info("Creating new organized directory structure...")
        
        def create_directories(structure: Dict, base_path: Path):
            for name, content in structure.items():
                if isinstance(content, dict):
                    # It's a directory
                    dir_path = base_path / name
                    dir_path.mkdir(exist_ok=True)
                    create_directories(content, dir_path)
                elif isinstance(content, list):
                    # It's a directory with files
                    dir_path = base_path / name
                    dir_path.mkdir(exist_ok=True)
                    for file_name in content:
                        if file_name.endswith("*"):
                            # Pattern files - create placeholder
                            continue
                        file_path = dir_path / file_name
                        if not file_path.exists():
                            file_path.touch()
                else:
                    # It's a file
                    file_path = base_path / name
                    if not file_path.exists():
                        file_path.touch()
        
        create_directories(self.new_structure, self.project_root)
        logger.info("New directory structure created")
    
    def move_files_to_new_structure(self):
        """Move existing files to the new organized structure"""
        logger.info("Moving files to new organized structure...")
        
        # Move source files
        src_moves = {
            "src/core/tech_detector.py": "src/core/tech_detector.py",
            "src/core/enhanced_tech_detector.py": "src/core/enhanced_tech_detector.py",
            "src/core/enhanced_dataset_manager.py": "src/core/enhanced_dataset_manager.py",
            "src/core/webtech_matcher_advanced.py": "src/core/webtech_matcher_advanced.py",
            "src/integrations/whatweb_integration.py": "src/integrations/whatweb_integration.py",
            "src/integrations/dynamic_whatweb_integration.py": "src/integrations/dynamic_whatweb_integration.py",
            "src/integrations/wappalyzer_integration.py": "src/integrations/wappalyzer_integration.py",
            "src/utils/user_agents.py": "src/utils/user_agents.py"
        }
        
        for src, dst in src_moves.items():
            src_path = self.project_root / src
            dst_path = self.project_root / dst
            
            if src_path.exists() and not dst_path.exists():
                dst_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(src_path), str(dst_path))
                logger.info(f"Moved {src} -> {dst}")
        
        # Move data files
        data_moves = {
            "json_datasets/web_tech_dataset.json": "data/datasets/raw/web_tech_dataset.json",
            "json_datasets/wappalyzer_technologies_clean.json": "data/datasets/raw/wappalyzer_technologies_clean.json",
            "json_datasets/technology_lookup_merged.json": "data/datasets/raw/technology_lookup_merged.json",
            "json_datasets/wappalyzer": "data/datasets/individual/wappalyzer",
            "json_datasets/organized": "data/datasets/organized",
            "json_datasets/individual_reports": "data/datasets/reports/individual_reports",
            "WhatWeb": "data/external_tools/WhatWeb"
        }
        
        for src, dst in data_moves.items():
            src_path = self.project_root / src
            dst_path = self.project_root / dst
            
            if src_path.exists():
                dst_path.parent.mkdir(parents=True, exist_ok=True)
                if src_path.is_dir():
                    if dst_path.exists():
                        if dst_path.is_file():
                            dst_path.unlink()
                        else:
                            shutil.rmtree(dst_path)
                    shutil.move(str(src_path), str(dst_path))
                else:
                    shutil.move(str(src_path), str(dst_path))
                logger.info(f"Moved {src} -> {dst}")
        
        # Move scripts
        script_moves = {
            "scripts/organize_datasets.py": "scripts/organize_datasets.py",
            "scripts/organize_project.py": "scripts/organize_project.py"
        }
        
        for src, dst in script_moves.items():
            src_path = self.project_root / src
            dst_path = self.project_root / dst
            
            if src_path.exists() and not dst_path.exists():
                shutil.move(str(src_path), str(dst_path))
                logger.info(f"Moved {src} -> {dst}")
        
        # Move configuration files
        config_moves = {
            "requirements.txt": "config/requirements.txt",
            "requirements_advanced.txt": "config/requirements_advanced.txt"
        }
        
        for src, dst in config_moves.items():
            src_path = self.project_root / src
            dst_path = self.project_root / dst
            
            if src_path.exists() and not dst_path.exists():
                shutil.move(str(src_path), str(dst_path))
                logger.info(f"Moved {src} -> {dst}")
    
    def create_launcher_scripts(self):
        """Create organized launcher scripts"""
        logger.info("Creating launcher scripts...")
        
        # Unix/macOS launcher
        unix_launcher = """#!/bin/bash
# Tech Detection System - Unix/macOS Launcher
# Comprehensive web technology detection with organized datasets

cd "$(dirname "$0")/.."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install requirements if needed
if [ ! -f "venv/.installed" ]; then
    echo "Installing requirements..."
    pip install -r config/requirements.txt
    touch venv/.installed
fi

# Run the detection system
python main.py "$@"
"""
        
        with open(self.project_root / "launchers" / "unix" / "detect.sh", "w") as f:
            f.write(unix_launcher)
        os.chmod(self.project_root / "launchers" / "unix" / "detect.sh", 0o755)
        
        # Windows launcher
        windows_launcher = """@echo off
REM Tech Detection System - Windows Launcher
REM Comprehensive web technology detection with organized datasets

cd /d "%~dp0\\.."

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\\Scripts\\activate.bat

REM Install requirements if needed
if not exist "venv\\.installed" (
    echo Installing requirements...
    pip install -r config\\requirements.txt
    echo. > venv\\.installed
)

REM Run the detection system
python main.py %*
"""
        
        with open(self.project_root / "launchers" / "windows" / "detect.bat", "w") as f:
            f.write(windows_launcher)
        
        # PowerShell launcher
        powershell_launcher = """# Tech Detection System - PowerShell Launcher
# Comprehensive web technology detection with organized datasets

Set-Location $PSScriptRoot\\..

# Check if virtual environment exists
if (-not (Test-Path "venv")) {
    Write-Host "Creating virtual environment..."
    python -m venv venv
}

# Activate virtual environment
& "venv\\Scripts\\Activate.ps1"

# Install requirements if needed
if (-not (Test-Path "venv\\.installed")) {
    Write-Host "Installing requirements..."
    pip install -r config\\requirements.txt
    New-Item -Path "venv\\.installed" -ItemType File
}

# Run the detection system
python main.py $args
"""
        
        with open(self.project_root / "launchers" / "powershell" / "detect.ps1", "w") as f:
            f.write(powershell_launcher)
        
        logger.info("Launcher scripts created")
    
    def create_documentation(self):
        """Create comprehensive documentation"""
        logger.info("Creating comprehensive documentation...")
        
        # Main README
        main_readme = """# Tech Detection System

A comprehensive web technology detection system that combines multiple detection engines and datasets for maximum accuracy and coverage.

## Features

- **3,954+ Technologies**: Comprehensive database of web technologies
- **117 Categories**: Organized technology classification
- **Multiple Detection Engines**: Core dataset, Wappalyzer, WhatWeb
- **Dynamic Timeout**: Adaptive timeout based on site complexity
- **Organized Datasets**: Properly structured and optimized data
- **Cross-Platform**: Works on Windows, macOS, and Linux

## Quick Start

### Using Launchers (Recommended)

**Unix/macOS:**
```bash
./launchers/unix/detect.sh https://example.com
```

**Windows:**
```cmd
launchers\\windows\\detect.bat https://example.com
```

**PowerShell:**
```powershell
.\\launchers\\powershell\\detect.ps1 https://example.com
```

### Manual Setup

1. **Install Dependencies:**
   ```bash
   pip install -r config/requirements.txt
   ```

2. **Run Detection:**
   ```bash
   python main.py https://example.com --use-dataset --use-whatweb --use-wappalyzer
   ```

## Project Structure

```
Tech-Detection/
├── src/                    # Source code
│   ├── core/              # Core detection engines
│   ├── integrations/      # External tool integrations
│   └── utils/             # Utility functions
├── data/                  # Data and datasets
│   ├── datasets/          # Technology datasets
│   └── external_tools/    # External tools (WhatWeb)
├── scripts/               # Organization and setup scripts
├── docs/                  # Documentation
├── config/                # Configuration files
├── tests/                 # Test files
├── examples/              # Usage examples
├── launchers/             # Platform-specific launchers
└── output/                # Generated reports and logs
```

## Advanced Usage

See `docs/` directory for detailed documentation:
- `API_REFERENCE.md` - Complete API documentation
- `DATASET_GUIDE.md` - Dataset structure and usage
- `COMMAND_REFERENCE.md` - All command-line options

## License

MIT License - see LICENSE file for details.
"""
        
        with open(self.project_root / "README.md", "w") as f:
            f.write(main_readme)
        
        # API Reference
        api_reference = """# API Reference

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
  --output FORMAT            Output format (json, csv, table)
  --save-report FILE         Save report to file
  --verbose                  Verbose output
  --debug                    Debug output
```
"""
        
        with open(self.project_root / "docs" / "API_REFERENCE.md", "w") as f:
            f.write(api_reference)
        
        # Dataset Guide
        dataset_guide = """# Dataset Guide

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
        "html": ["<div class=\"technology\""]
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
"""
        
        with open(self.project_root / "docs" / "DATASET_GUIDE.md", "w") as f:
            f.write(dataset_guide)
        
        logger.info("Documentation created")
    
    def update_imports(self):
        """Update import statements to reflect new structure"""
        logger.info("Updating import statements...")
        
        # Update main.py
        main_py = self.project_root / "main.py"
        if main_py.exists():
            with open(main_py, "r") as f:
                content = f.read()
            
            # Update imports
            content = content.replace(
                "from src.core.tech_detector import main as tech_detector_main",
                "from src.core.tech_detector import main as tech_detector_main"
            )
            
            with open(main_py, "w") as f:
                f.write(content)
        
        # Update __init__.py files
        init_files = [
            "src/__init__.py",
            "src/core/__init__.py", 
            "src/integrations/__init__.py",
            "src/utils/__init__.py",
            "tests/__init__.py"
        ]
        
        for init_file in init_files:
            init_path = self.project_root / init_file
            if not init_path.exists():
                init_path.parent.mkdir(parents=True, exist_ok=True)
                init_path.touch()
        
        logger.info("Import statements updated")
    
    def create_examples(self):
        """Create usage examples"""
        logger.info("Creating usage examples...")
        
        # Basic usage example
        basic_example = """#!/usr/bin/env python3
\"\"\"
Basic Usage Example
Simple technology detection for a single URL
\"\"\"

import asyncio
from src.core.tech_detector import main as tech_detector_main

async def basic_detection():
    \"\"\"Basic technology detection example\"\"\"
    url = "https://example.com"
    
    # Run detection with basic options
    result = await tech_detector_main([
        url,
        "--use-dataset",
        "--use-whatweb", 
        "--use-wappalyzer",
        "--output", "json",
        "--verbose"
    ])
    
    print(f"Detected {len(result.technologies)} technologies")
    for tech in result.technologies:
        print(f"- {tech.name} ({tech.category}) - {tech.confidence}%")

if __name__ == "__main__":
    asyncio.run(basic_detection())
"""
        
        with open(self.project_root / "examples" / "basic_usage.py", "w") as f:
            f.write(basic_example)
        
        # Advanced usage example
        advanced_example = """#!/usr/bin/env python3
\"\"\"
Advanced Usage Example
Comprehensive technology detection with custom options
\"\"\"

import asyncio
from src.core.tech_detector import main as tech_detector_main

async def advanced_detection():
    \"\"\"Advanced technology detection example\"\"\"
    urls = [
        "https://github.com",
        "https://stackoverflow.com", 
        "https://example.com"
    ]
    
    for url in urls:
        print(f"\\nAnalyzing {url}...")
        
        # Run detection with advanced options
        result = await tech_detector_main([
            url,
            "--use-dataset",
            "--use-whatweb",
            "--use-wappalyzer", 
            "--user-agents", "5",
            "--preferred-browser", "chrome",
            "--min-confidence", "20",
            "--max-results", "100",
            "--timeout", "30",
            "--follow-redirects",
            "--output", "csv",
            "--save-report", f"report_{url.replace('https://', '').replace('/', '_')}.csv",
            "--verbose",
            "--whatweb-aggression", "1"
        ])
        
        print(f"Detected {len(result.technologies)} technologies")
        
        # Group by category
        by_category = {}
        for tech in result.technologies:
            category = tech.category
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(tech)
        
        for category, techs in by_category.items():
            print(f"  {category}: {len(techs)} technologies")

if __name__ == "__main__":
    asyncio.run(advanced_detection())
"""
        
        with open(self.project_root / "examples" / "advanced_usage.py", "w") as f:
            f.write(advanced_example)
        
        logger.info("Usage examples created")
    
    def cleanup_old_files(self):
        """Clean up old files and temporary directories"""
        logger.info("Cleaning up old files...")
        
        # Files to remove
        files_to_remove = [
            "webtech_matcher.py",
            "newtech.py", 
            "advanced_tech_detector.py",
            "enhanced_tech_detector.py",
            "user_agents.py",
            "enhanced_dataset_manager.py",
            "tech_detector.py",
            "setup_ultimate.py",
            "install_advanced.py",
            "requirements_advanced.txt",
            "ADVANCED_USAGE.md",
            "COMMAND_REFERENCE.md", 
            "ADVANCED_SYSTEM_SUMMARY.md",
            "ULTIMATE_SYSTEM_COMPLETE.md",
            "PROJECT_STRUCTURE.md",
            "PROJECT_ORGANIZED_SUMMARY.md",
            "PROJECT_CLEANED_SUMMARY.md",
            "DEEP_DETECTION_COMMANDS.md",
            "COMMANDS_FIXED_SUMMARY.md",
            "DOMAIN_TEST_RESULTS_SUMMARY.md",
            "BEST_DETECTION_COMMANDS.md",
            "COMMANDS_FIXED_SUMMARY.md"
        ]
        
        for file_name in files_to_remove:
            file_path = self.project_root / file_name
            if file_path.exists():
                file_path.unlink()
                logger.info(f"Removed {file_name}")
        
        # Remove old directories
        old_dirs = [
            "integrations",
            "core"
        ]
        
        for dir_name in old_dirs:
            dir_path = self.project_root / dir_name
            if dir_path.exists():
                shutil.rmtree(dir_path)
                logger.info(f"Removed directory {dir_name}")
        
        logger.info("Cleanup completed")
    
    def create_config_files(self):
        """Create configuration files"""
        logger.info("Creating configuration files...")
        
        # Main config
        config = {
            "version": "2.0",
            "datasets": {
                "path": "data/datasets",
                "organized_path": "data/datasets/organized",
                "comprehensive_file": "comprehensive_technologies.json"
            },
            "whatweb": {
                "path": "data/external_tools/WhatWeb/whatweb",
                "timeout": 30,
                "aggression": 1
            },
            "wappalyzer": {
                "use_bundled": True,
                "update_on_init": False
            },
            "detection": {
                "min_confidence": 20,
                "max_results": 100,
                "user_agents": 5,
                "timeout": 30
            },
            "output": {
                "default_format": "json",
                "save_reports": True,
                "reports_dir": "output/reports"
            }
        }
        
        with open(self.project_root / "config" / "config.json", "w") as f:
            json.dump(config, f, indent=2)
        
        logger.info("Configuration files created")
    
    def run_organization(self):
        """Run complete project organization"""
        logger.info("Starting comprehensive project organization...")
        
        try:
            # Create backup
            self.create_backup()
            
            # Create new structure
            self.create_new_structure()
            
            # Move files
            self.move_files_to_new_structure()
            
            # Create launcher scripts
            self.create_launcher_scripts()
            
            # Create documentation
            self.create_documentation()
            
            # Update imports
            self.update_imports()
            
            # Create examples
            self.create_examples()
            
            # Create config files
            self.create_config_files()
            
            # Cleanup old files
            self.cleanup_old_files()
            
            logger.info("Project organization completed successfully!")
            
            # Print summary
            print("\n" + "="*60)
            print("🎉 PROJECT ORGANIZATION COMPLETE!")
            print("="*60)
            print("📁 New Structure:")
            print("  src/                    # Source code")
            print("  data/                   # Datasets and external tools")
            print("  scripts/                # Organization scripts")
            print("  docs/                   # Documentation")
            print("  config/                 # Configuration files")
            print("  tests/                  # Test files")
            print("  examples/               # Usage examples")
            print("  launchers/              # Platform launchers")
            print("  output/                 # Generated reports")
            print("\n Quick Start:")
            print("  Unix/macOS: ./launchers/unix/detect.sh https://example.com")
            print("  Windows:    launchers\\windows\\detect.bat https://example.com")
            print("  PowerShell: .\\launchers\\powershell\\detect.ps1 https://example.com")
            print("\n Documentation: See docs/ directory")
            print("="*60)
            
        except Exception as e:
            logger.error(f"Organization failed: {e}")
            print(f"\n❌ Organization failed: {e}")
            print("💾 Backup available at: backup_before_organization/")
            raise

if __name__ == "__main__":
    organizer = ProjectOrganizer()
    organizer.run_organization()

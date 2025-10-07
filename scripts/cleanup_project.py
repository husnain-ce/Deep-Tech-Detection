#!/usr/bin/env python3
"""
Project Cleanup Script
Removes unnecessary files, temporary data, and optimizes project structure
"""

import os
import shutil
import glob
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ProjectCleanup:
    """Comprehensive project cleanup and optimization"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).resolve()
        self.cleaned_files = []
        self.cleaned_dirs = []
        
    def clean_python_cache(self):
        """Remove Python cache files and __pycache__ directories"""
        logger.info("Cleaning Python cache files...")
        
        # Remove __pycache__ directories
        for pycache_dir in self.project_root.rglob("__pycache__"):
            if pycache_dir.is_dir():
                shutil.rmtree(pycache_dir)
                self.cleaned_dirs.append(str(pycache_dir))
                logger.info(f"Removed {pycache_dir}")
        
        # Remove .pyc files
        for pyc_file in self.project_root.rglob("*.pyc"):
            if pyc_file.is_file():
                pyc_file.unlink()
                self.cleaned_files.append(str(pyc_file))
                logger.info(f"Removed {pyc_file}")
        
        logger.info(f"Cleaned {len(self.cleaned_files)} .pyc files and {len(self.cleaned_dirs)} __pycache__ directories")
    
    def clean_temporary_files(self):
        """Remove temporary and backup files"""
        logger.info("Cleaning temporary files...")
        
        # File patterns to remove
        temp_patterns = [
            "*.tmp",
            "*.temp", 
            "*.bak",
            "*.backup",
            "*.old",
            "*.orig",
            "*.rej",
            "*.swp",
            "*.swo",
            "*~",
            ".DS_Store",
            "Thumbs.db"
        ]
        
        for pattern in temp_patterns:
            for file_path in self.project_root.rglob(pattern):
                if file_path.is_file():
                    file_path.unlink()
                    self.cleaned_files.append(str(file_path))
                    logger.info(f"Removed {file_path}")
    
    def clean_old_reports(self):
        """Clean up old CSV report files"""
        logger.info("Cleaning old report files...")
        
        # Keep only the most recent reports, remove old ones
        csv_files = list(self.project_root.glob("*.csv"))
        
        # Group by base name (without timestamp)
        report_groups = {}
        for csv_file in csv_files:
            # Extract base name (remove timestamp pattern)
            base_name = csv_file.stem
            # Remove timestamp pattern like _20251002_050641
            import re
            base_name = re.sub(r'_\d{8}_\d{6}$', '', base_name)
            
            if base_name not in report_groups:
                report_groups[base_name] = []
            report_groups[base_name].append(csv_file)
        
        # Keep only the most recent file from each group
        for base_name, files in report_groups.items():
            if len(files) > 1:
                # Sort by modification time, keep the newest
                files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
                for old_file in files[1:]:  # Remove all but the newest
                    old_file.unlink()
                    self.cleaned_files.append(str(old_file))
                    logger.info(f"Removed old report: {old_file}")
    
    def clean_log_files(self):
        """Clean up log files"""
        logger.info("Cleaning log files...")
        
        # Remove log files (keep recent ones)
        log_files = list(self.project_root.glob("*.log"))
        
        if len(log_files) > 1:
            # Sort by modification time, keep the newest
            log_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            for old_log in log_files[1:]:  # Remove all but the newest
                old_log.unlink()
                self.cleaned_files.append(str(old_log))
                logger.info(f"Removed old log: {old_log}")
    
    def clean_duplicate_datasets(self):
        """Remove duplicate and temporary dataset files"""
        logger.info("Cleaning duplicate dataset files...")
        
        # Files to remove (duplicates and temporary files)
        files_to_remove = [
            "json_datasets/wappalyzer_technologies_formatted.json",
            "json_datasets/wappalyzer_technologies_fixed.json", 
            "json_datasets/wappalyzer_technologies_fully_fixed.json",
            "json_datasets/individual_reports/whatweb_merged_report.json"
        ]
        
        for file_path in files_to_remove:
            full_path = self.project_root / file_path
            if full_path.exists():
                full_path.unlink()
                self.cleaned_files.append(str(full_path))
                logger.info(f"Removed duplicate dataset: {file_path}")
    
    def clean_empty_directories(self):
        """Remove empty directories"""
        logger.info("Cleaning empty directories...")
        
        # Find empty directories (excluding important ones)
        important_dirs = {
            "src", "data", "scripts", "docs", "config", "tests", 
            "examples", "launchers", "output", "venv", ".git"
        }
        
        for root, dirs, files in os.walk(self.project_root, topdown=False):
            for dir_name in dirs:
                dir_path = Path(root) / dir_name
                # Skip important directories
                if any(important in str(dir_path) for important in important_dirs):
                    continue
                
                try:
                    # Check if directory is empty
                    if not any(dir_path.iterdir()):
                        dir_path.rmdir()
                        self.cleaned_dirs.append(str(dir_path))
                        logger.info(f"Removed empty directory: {dir_path}")
                except OSError:
                    pass  # Directory not empty or permission error
    
    def clean_output_directory(self):
        """Clean up output directory but keep structure"""
        logger.info("Cleaning output directory...")
        
        output_dir = self.project_root / "output"
        if output_dir.exists():
            # Remove all files but keep directory structure
            for item in output_dir.rglob("*"):
                if item.is_file():
                    item.unlink()
                    self.cleaned_files.append(str(item))
                    logger.info(f"Removed output file: {item}")
                elif item.is_dir() and item != output_dir:
                    # Remove empty subdirectories
                    try:
                        if not any(item.iterdir()):
                            item.rmdir()
                            self.cleaned_dirs.append(str(item))
                            logger.info(f"Removed empty output directory: {item}")
                    except OSError:
                        pass
    
    def optimize_gitignore(self):
        """Update .gitignore to prevent future clutter"""
        logger.info("Optimizing .gitignore...")
        
        gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed
.pytest_cache/

# Virtual Environment
venv/
env/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Project specific
*.log
*.csv
*.tmp
*.bak
*.backup
output/reports/*.csv
output/logs/*.log

# Keep important files
!output/
!output/reports/
!output/logs/
!*.md
!requirements.txt
!config.json
"""
        
        gitignore_path = self.project_root / ".gitignore"
        with open(gitignore_path, "w") as f:
            f.write(gitignore_content)
        
        logger.info("Updated .gitignore")
    
    def create_cleanup_summary(self):
        """Create a summary of cleanup actions"""
        logger.info("Creating cleanup summary...")
        
        summary = f"""# Project Cleanup Summary

## Files Cleaned: {len(self.cleaned_files)}
## Directories Cleaned: {len(self.cleaned_dirs)}

## Cleaned Files:
"""
        
        for file_path in self.cleaned_files:
            summary += f"- {file_path}\n"
        
        summary += f"\n## Cleaned Directories:\n"
        
        for dir_path in self.cleaned_dirs:
            summary += f"- {dir_path}\n"
        
        summary += f"""
## Cleanup Actions Performed:
1.  Removed Python cache files (__pycache__, *.pyc)
2.  Cleaned temporary files (*.tmp, *.bak, etc.)
3.  Removed old CSV report files (kept most recent)
4.  Cleaned log files (kept most recent)
5.  Removed duplicate dataset files
6.  Removed empty directories
7.  Cleaned output directory
8.  Updated .gitignore

## Project Status: CLEAN AND OPTIMIZED
"""
        
        with open(self.project_root / "CLEANUP_SUMMARY.md", "w") as f:
            f.write(summary)
        
        logger.info("Cleanup summary created: CLEANUP_SUMMARY.md")
    
    def run_cleanup(self):
        """Run complete project cleanup"""
        logger.info("Starting comprehensive project cleanup...")
        
        try:
            # Clean Python cache
            self.clean_python_cache()
            
            # Clean temporary files
            self.clean_temporary_files()
            
            # Clean old reports
            self.clean_old_reports()
            
            # Clean log files
            self.clean_log_files()
            
            # Clean duplicate datasets
            self.clean_duplicate_datasets()
            
            # Clean empty directories
            self.clean_empty_directories()
            
            # Clean output directory
            self.clean_output_directory()
            
            # Optimize gitignore
            self.optimize_gitignore()
            
            # Create cleanup summary
            self.create_cleanup_summary()
            
            logger.info("Project cleanup completed successfully!")
            
            # Print summary
            print("\n" + "="*60)
            print("🧹 PROJECT CLEANUP COMPLETE!")
            print("="*60)
            print(f"Files Cleaned: {len(self.cleaned_files)}")
            print(f"Directories Cleaned: {len(self.cleaned_dirs)}")
            print("\n Cleanup Actions:")
            print("  - Removed Python cache files")
            print("  - Cleaned temporary files")
            print("  - Removed old CSV reports")
            print("  - Cleaned log files")
            print("  - Removed duplicate datasets")
            print("  - Removed empty directories")
            print("  - Cleaned output directory")
            print("  - Updated .gitignore")
            print("\n📁 Project Status: CLEAN AND OPTIMIZED")
            print("="*60)
            
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
            print(f"\n❌ Cleanup failed: {e}")
            raise

if __name__ == "__main__":
    cleaner = ProjectCleanup()
    cleaner.run_cleanup()

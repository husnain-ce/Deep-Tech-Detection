#!/usr/bin/env python3
"""
Project Cleanup Script
Removes unnecessary files and organizes the project structure
"""

import os
import shutil
import sys

def cleanup_project():
    """Clean up the project by removing unnecessary files"""
    
    print("🧹 Starting project cleanup...")
    
    # Files and directories to remove
    files_to_remove = [
        # Old core modules (replaced by ultimate_tech_detector.py)
        "src/core/advanced_tech_detector.py",
        "src/core/deep_dataset_manager.py", 
        "src/core/deep_pattern_matcher.py",
        "src/core/deep_tech_detector.py",
        "src/core/enhanced_dataset_manager.py",
        "src/core/enhanced_tech_detector.py",
        "src/core/tech_detector.py",
        "src/core/webtech_matcher_advanced.py",
        
        # Old scripts (functionality moved to main files)
        "scripts/advanced_deduplication.py",
        "scripts/compare_deduplication.py",
        "scripts/comprehensive_domain_analysis.py",
        "scripts/comprehensive_tech_analysis.py",
        "scripts/deep_detection_test.py",
        "scripts/enhanced_tech_detection.py",
        "scripts/merge_reports.py",
        "scripts/ultimate_deep_analysis.py",
        
        # Old main files
        "main.py",
        
        # Note: Preserving output data - only removing empty directories
        # "output/reports/",  # Commented out to preserve data
        # "output/deep/",     # Commented out to preserve data
        
        # Log files
        "tech_detector.log",
        
        # Cache directories
        "src/core/__pycache__/",
        "scripts/__pycache__/",
        "__pycache__/",
    ]
    
    # Directories to clean (remove contents but keep directory)
    dirs_to_clean = [
        "output/",
    ]
    
    removed_count = 0
    
    # Remove files
    for file_path in files_to_remove:
        if os.path.exists(file_path):
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    print(f"  ❌ Removed file: {file_path}")
                    removed_count += 1
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
                    print(f"  ❌ Removed directory: {file_path}")
                    removed_count += 1
            except Exception as e:
                print(f"  ⚠️  Could not remove {file_path}: {e}")
    
    # Clean directories (remove contents but keep directory)
    for dir_path in dirs_to_clean:
        if os.path.exists(dir_path):
            try:
                for item in os.listdir(dir_path):
                    item_path = os.path.join(dir_path, item)
                    if os.path.isfile(item_path):
                        os.remove(item_path)
                        print(f"  ❌ Removed file: {item_path}")
                        removed_count += 1
                    elif os.path.isdir(item_path):
                        shutil.rmtree(item_path)
                        print(f"  ❌ Removed directory: {item_path}")
                        removed_count += 1
            except Exception as e:
                print(f"  ⚠️  Could not clean {dir_path}: {e}")
    
    # Create new output directory
    os.makedirs("output", exist_ok=True)
    print(f"  ✅ Created clean output directory")
    
    print(f"\n🎉 Cleanup complete! Removed {removed_count} items")
    print("\n📁 New project structure:")
    print("  ultimate_tech_detector.py  - Main detection system")
    print("  detect.py                  - Simple launcher")
    print("  data/datasets/             - Technology datasets")
    print("  output/                    - Clean output directory")
    print("  README.md                  - Documentation")

if __name__ == "__main__":
    cleanup_project()

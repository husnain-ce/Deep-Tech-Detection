#!/usr/bin/env python3
"""
Log Rotation and Cleanup Script for Tech Detection System
"""

import os
import time
import gzip
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from logging_config import TechDetectionLogger

class LogRotator:
    """Handles log rotation and cleanup for the Tech Detection system"""
    
    def __init__(self, log_dir="logs", max_file_size=10*1024*1024, backup_count=5, days_to_keep=7):
        """
        Initialize log rotator
        
        Args:
            log_dir (str): Directory containing log files
            max_file_size (int): Maximum size of log file before rotation (bytes)
            backup_count (int): Number of backup files to keep
            days_to_keep (int): Number of days to keep old logs
        """
        self.log_dir = Path(log_dir)
        self.max_file_size = max_file_size
        self.backup_count = backup_count
        self.days_to_keep = days_to_keep
        
    def rotate_logs(self):
        """Rotate log files that exceed the maximum size"""
        print(f"Starting log rotation in {self.log_dir}")
        
        for log_file in self.log_dir.glob("*.log"):
            if log_file.stat().st_size > self.max_file_size:
                print(f"Rotating large log file: {log_file}")
                self._rotate_single_log(log_file)
    
    def _rotate_single_log(self, log_file):
        """Rotate a single log file"""
        try:
            # Create backup files
            for i in range(self.backup_count - 1, 0, -1):
                old_backup = log_file.with_suffix(f".log.{i}")
                new_backup = log_file.with_suffix(f".log.{i + 1}")
                
                if old_backup.exists():
                    if i == self.backup_count - 1:
                        # Remove the oldest backup
                        old_backup.unlink()
                    else:
                        # Move backup to next number
                        shutil.move(str(old_backup), str(new_backup))
            
            # Move current log to backup.1
            backup_file = log_file.with_suffix(".log.1")
            shutil.move(str(log_file), str(backup_file))
            
            # Compress the backup file
            self._compress_log(backup_file)
            
            print(f"Rotated {log_file} -> {backup_file}.gz")
            
        except Exception as e:
            print(f"Error rotating {log_file}: {e}")
    
    def _compress_log(self, log_file):
        """Compress a log file using gzip"""
        try:
            with open(log_file, 'rb') as f_in:
                with gzip.open(f"{log_file}.gz", 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            # Remove original file after compression
            log_file.unlink()
            print(f"Compressed {log_file} -> {log_file}.gz")
            
        except Exception as e:
            print(f"Error compressing {log_file}: {e}")
    
    def cleanup_old_logs(self):
        """Remove log files older than the specified number of days"""
        print(f"Cleaning up logs older than {self.days_to_keep} days")
        
        cutoff_time = time.time() - (self.days_to_keep * 24 * 60 * 60)
        removed_count = 0
        
        for log_file in self.log_dir.glob("*.log*"):
            if log_file.stat().st_mtime < cutoff_time:
                try:
                    log_file.unlink()
                    removed_count += 1
                    print(f"Removed old log: {log_file}")
                except Exception as e:
                    print(f"Error removing {log_file}: {e}")
        
        print(f"Removed {removed_count} old log files")
    
    def get_log_stats(self):
        """Get statistics about log files"""
        stats = {
            'total_files': 0,
            'total_size': 0,
            'files_by_type': {},
            'oldest_file': None,
            'newest_file': None
        }
        
        for log_file in self.log_dir.glob("*.log*"):
            stats['total_files'] += 1
            stats['total_size'] += log_file.stat().st_size
            
            # Categorize by file type
            if log_file.suffix == '.log':
                file_type = 'current'
            elif log_file.suffix == '.gz':
                file_type = 'compressed'
            else:
                file_type = 'backup'
            
            stats['files_by_type'][file_type] = stats['files_by_type'].get(file_type, 0) + 1
            
            # Track oldest and newest files
            file_time = log_file.stat().st_mtime
            if stats['oldest_file'] is None or file_time < stats['oldest_file'][1]:
                stats['oldest_file'] = (log_file, file_time)
            if stats['newest_file'] is None or file_time > stats['newest_file'][1]:
                stats['newest_file'] = (log_file, file_time)
        
        return stats
    
    def print_log_stats(self):
        """Print log file statistics"""
        stats = self.get_log_stats()
        
        print("\n=== Log File Statistics ===")
        print(f"Total files: {stats['total_files']}")
        print(f"Total size: {self._format_size(stats['total_size'])}")
        print(f"Files by type: {stats['files_by_type']}")
        
        if stats['oldest_file']:
            oldest_name, oldest_time = stats['oldest_file']
            print(f"Oldest file: {oldest_name} ({datetime.fromtimestamp(oldest_time)})")
        
        if stats['newest_file']:
            newest_name, newest_time = stats['newest_file']
            print(f"Newest file: {newest_name} ({datetime.fromtimestamp(newest_time)})")
        
        print("=" * 30)
    
    def _format_size(self, size_bytes):
        """Format file size in human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
    
    def run_maintenance(self):
        """Run complete log maintenance"""
        print(f"Starting log maintenance at {datetime.now()}")
        
        # Print current stats
        self.print_log_stats()
        
        # Rotate large files
        self.rotate_logs()
        
        # Clean up old files
        self.cleanup_old_logs()
        
        # Print final stats
        print("\nAfter maintenance:")
        self.print_log_stats()
        
        print(f"Log maintenance completed at {datetime.now()}")

def main():
    """Main function for log rotation"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Log rotation and cleanup for Tech Detection system')
    parser.add_argument('--log-dir', default='logs', help='Log directory path')
    parser.add_argument('--max-size', type=int, default=10*1024*1024, help='Maximum log file size in bytes')
    parser.add_argument('--backup-count', type=int, default=5, help='Number of backup files to keep')
    parser.add_argument('--days-to-keep', type=int, default=7, help='Days to keep old logs')
    parser.add_argument('--stats-only', action='store_true', help='Only show statistics, no rotation')
    parser.add_argument('--cleanup-only', action='store_true', help='Only cleanup old logs')
    
    args = parser.parse_args()
    
    rotator = LogRotator(
        log_dir=args.log_dir,
        max_file_size=args.max_size,
        backup_count=args.backup_count,
        days_to_keep=args.days_to_keep
    )
    
    if args.stats_only:
        rotator.print_log_stats()
    elif args.cleanup_only:
        rotator.cleanup_old_logs()
    else:
        rotator.run_maintenance()

if __name__ == "__main__":
    main()

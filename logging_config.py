#!/usr/bin/env python3
"""
Comprehensive Logging Configuration for Tech Detection System
"""

import logging
import logging.handlers
import os
import sys
from datetime import datetime
from pathlib import Path

class TechDetectionLogger:
    """Centralized logging configuration for the Tech Detection system"""
    
    def __init__(self, log_dir="logs", max_file_size=10*1024*1024, backup_count=5):
        """
        Initialize logging configuration
        
        Args:
            log_dir (str): Directory to store log files
            max_file_size (int): Maximum size of log file before rotation (bytes)
            backup_count (int): Number of backup files to keep
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Create log file with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = self.log_dir / f"tech_detection_{timestamp}.log"
        
        # Configure root logger
        self.setup_root_logger()
        
        # Configure specific loggers
        self.setup_api_logger()
        self.setup_detector_logger()
        self.setup_whatweb_logger()
        self.setup_cmseek_logger()
        self.setup_whatcms_logger()
        self.setup_wappalyzer_logger()
        
        # Create summary log
        self.setup_summary_logger()
        
    def setup_root_logger(self):
        """Setup root logger with file and console handlers"""
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)
        
        # Clear existing handlers
        root_logger.handlers.clear()
        
        # File handler with rotation
        file_handler = logging.handlers.RotatingFileHandler(
            self.log_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        
        # Formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        console_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        
        file_handler.setFormatter(detailed_formatter)
        console_handler.setFormatter(console_formatter)
        
        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)
        
    def setup_api_logger(self):
        """Setup API server specific logger"""
        api_logger = logging.getLogger('api_server')
        api_logger.setLevel(logging.DEBUG)
        
        # API specific log file
        api_file_handler = logging.handlers.RotatingFileHandler(
            self.log_dir / "api_server.log",
            maxBytes=5*1024*1024,  # 5MB
            backupCount=3,
            encoding='utf-8'
        )
        api_file_handler.setLevel(logging.DEBUG)
        
        api_formatter = logging.Formatter(
            '%(asctime)s - API - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        api_file_handler.setFormatter(api_formatter)
        api_logger.addHandler(api_file_handler)
        
    def setup_detector_logger(self):
        """Setup detector specific logger"""
        detector_logger = logging.getLogger('ultimate_tech_detector')
        detector_logger.setLevel(logging.DEBUG)
        
        # Detector specific log file
        detector_file_handler = logging.handlers.RotatingFileHandler(
            self.log_dir / "detector.log",
            maxBytes=10*1024*1024,  # 10MB
            backupCount=3,
            encoding='utf-8'
        )
        detector_file_handler.setLevel(logging.DEBUG)
        
        detector_formatter = logging.Formatter(
            '%(asctime)s - DETECTOR - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        detector_file_handler.setFormatter(detector_formatter)
        detector_logger.addHandler(detector_file_handler)
        
    def setup_whatweb_logger(self):
        """Setup WhatWeb specific logger"""
        whatweb_logger = logging.getLogger('whatweb')
        whatweb_logger.setLevel(logging.DEBUG)
        
        whatweb_file_handler = logging.handlers.RotatingFileHandler(
            self.log_dir / "whatweb.log",
            maxBytes=5*1024*1024,  # 5MB
            backupCount=2,
            encoding='utf-8'
        )
        whatweb_file_handler.setLevel(logging.DEBUG)
        
        whatweb_formatter = logging.Formatter(
            '%(asctime)s - WHATWEB - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        whatweb_file_handler.setFormatter(whatweb_formatter)
        whatweb_logger.addHandler(whatweb_file_handler)
        
    def setup_cmseek_logger(self):
        """Setup CMSeeK specific logger"""
        cmseek_logger = logging.getLogger('cmseek')
        cmseek_logger.setLevel(logging.DEBUG)
        
        cmseek_file_handler = logging.handlers.RotatingFileHandler(
            self.log_dir / "cmseek.log",
            maxBytes=5*1024*1024,  # 5MB
            backupCount=2,
            encoding='utf-8'
        )
        cmseek_file_handler.setLevel(logging.DEBUG)
        
        cmseek_formatter = logging.Formatter(
            '%(asctime)s - CMSEEK - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        cmseek_file_handler.setFormatter(cmseek_formatter)
        cmseek_logger.addHandler(cmseek_file_handler)
        
    def setup_whatcms_logger(self):
        """Setup WhatCMS specific logger"""
        whatcms_logger = logging.getLogger('whatcms')
        whatcms_logger.setLevel(logging.DEBUG)
        
        whatcms_file_handler = logging.handlers.RotatingFileHandler(
            self.log_dir / "whatcms.log",
            maxBytes=5*1024*1024,  # 5MB
            backupCount=2,
            encoding='utf-8'
        )
        whatcms_file_handler.setLevel(logging.DEBUG)
        
        whatcms_formatter = logging.Formatter(
            '%(asctime)s - WHATCMS - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        whatcms_file_handler.setFormatter(whatcms_formatter)
        whatcms_logger.addHandler(whatcms_file_handler)
        
    def setup_wappalyzer_logger(self):
        """Setup Wappalyzer specific logger"""
        wappalyzer_logger = logging.getLogger('wappalyzer')
        wappalyzer_logger.setLevel(logging.DEBUG)
        
        wappalyzer_file_handler = logging.handlers.RotatingFileHandler(
            self.log_dir / "wappalyzer.log",
            maxBytes=5*1024*1024,  # 5MB
            backupCount=2,
            encoding='utf-8'
        )
        wappalyzer_file_handler.setLevel(logging.DEBUG)
        
        wappalyzer_formatter = logging.Formatter(
            '%(asctime)s - WAPPALYZER - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        wappalyzer_file_handler.setFormatter(wappalyzer_formatter)
        wappalyzer_logger.addHandler(wappalyzer_file_handler)
        
    def setup_summary_logger(self):
        """Setup summary logger for high-level events"""
        summary_logger = logging.getLogger('summary')
        summary_logger.setLevel(logging.INFO)
        
        summary_file_handler = logging.handlers.RotatingFileHandler(
            self.log_dir / "summary.log",
            maxBytes=2*1024*1024,  # 2MB
            backupCount=10,
            encoding='utf-8'
        )
        summary_file_handler.setLevel(logging.INFO)
        
        summary_formatter = logging.Formatter(
            '%(asctime)s - SUMMARY - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        summary_file_handler.setFormatter(summary_formatter)
        summary_logger.addHandler(summary_file_handler)
        
    def get_logger(self, name):
        """Get a logger instance"""
        return logging.getLogger(name)
        
    def log_analysis_start(self, url, engines):
        """Log the start of an analysis"""
        summary_logger = self.get_logger('summary')
        summary_logger.info(f"ANALYSIS_START: {url} with engines: {engines}")
        
    def log_analysis_complete(self, url, technologies_count, analysis_time, engines_used):
        """Log the completion of an analysis"""
        summary_logger = self.get_logger('summary')
        summary_logger.info(f"ANALYSIS_COMPLETE: {url} - {technologies_count} technologies in {analysis_time:.2f}s using {engines_used}")
        
    def log_analysis_error(self, url, error_message):
        """Log an analysis error"""
        summary_logger = self.get_logger('summary')
        summary_logger.error(f"ANALYSIS_ERROR: {url} - {error_message}")
        
    def log_engine_status(self, engine_name, status, details=""):
        """Log engine status"""
        summary_logger = self.get_logger('summary')
        summary_logger.info(f"ENGINE_STATUS: {engine_name} - {status} {details}")
        
    def cleanup_old_logs(self, days_to_keep=7):
        """Clean up old log files"""
        import time
        current_time = time.time()
        cutoff_time = current_time - (days_to_keep * 24 * 60 * 60)
        
        for log_file in self.log_dir.glob("*.log*"):
            if log_file.stat().st_mtime < cutoff_time:
                try:
                    log_file.unlink()
                    print(f"Cleaned up old log file: {log_file}")
                except Exception as e:
                    print(f"Failed to clean up {log_file}: {e}")

# Global logger instance
logger_config = TechDetectionLogger()

def get_logger(name):
    """Get a logger instance"""
    return logger_config.get_logger(name)

def log_analysis_start(url, engines):
    """Log the start of an analysis"""
    logger_config.log_analysis_start(url, engines)

def log_analysis_complete(url, technologies_count, analysis_time, engines_used):
    """Log the completion of an analysis"""
    logger_config.log_analysis_complete(url, technologies_count, analysis_time, engines_used)

def log_analysis_error(url, error_message):
    """Log an analysis error"""
    logger_config.log_analysis_error(url, error_message)

def log_engine_status(engine_name, status, details=""):
    """Log engine status"""
    logger_config.log_engine_status(engine_name, status, details)

if __name__ == "__main__":
    # Test the logging configuration
    logger = get_logger('test')
    logger.info("Logging configuration test successful")
    logger.debug("Debug message test")
    logger.warning("Warning message test")
    logger.error("Error message test")
    
    # Test summary logging
    log_analysis_start("test.com", ["pattern", "whatweb"])
    log_analysis_complete("test.com", 5, 2.5, ["pattern", "whatweb"])
    log_engine_status("WhatWeb", "Available", "Version 0.5.5")

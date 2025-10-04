#!/usr/bin/env python3
"""
Flask API Server for Tech Detection Dashboard
Serves the frontend and provides API endpoints for technology detection
"""

import asyncio
import json
import logging
import os
import sys
from pathlib import Path
from typing import Dict, Any, List

from flask import Flask, request, jsonify, send_from_directory, render_template_string
from flask_cors import CORS
import aiohttp

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from ultimate_tech_detector import UltimateTechDetector

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Global detector instance
detector = None

def initialize_detector():
    """Initialize the UltimateTechDetector"""
    global detector
    try:
        detector = UltimateTechDetector()
        logger.info("UltimateTechDetector initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize UltimateTechDetector: {e}")
        return False

@app.route('/')
def index():
    """Serve the main dashboard"""
    frontend_path = Path(__file__).parent / 'frontend'
    return send_from_directory(frontend_path, 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    """Serve static files from frontend directory"""
    frontend_path = Path(__file__).parent / 'frontend'
    return send_from_directory(frontend_path, filename)

@app.route('/api/analyze', methods=['POST'])
def analyze_domain():
    """Analyze a domain for technologies"""
    try:
        data = request.get_json()
        domain = data.get('domain', '').strip()
        
        if not domain:
            return jsonify({'error': 'Domain is required'}), 400
        
        if not detector:
            return jsonify({'error': 'Detector not initialized'}), 500
        
        # Clean domain input
        if not domain.startswith(('http://', 'https://')):
            domain = f'https://{domain}'
        
        logger.info(f"Analyzing domain: {domain}")
        
        # Run analysis using asyncio
        try:
            # Use the existing event loop or create a new one
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            result = loop.run_until_complete(detector.analyze_url(domain))
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            return jsonify({'error': f'Analysis failed: {str(e)}'}), 500
        
        # Convert result to JSON-serializable format
        analysis_data = {
            'url': result.url,
            'final_url': result.final_url,
            'analysis_time': result.analysis_time,
            'technologies': [tech.to_dict() for tech in result.technologies],
            'metadata': result.metadata,
            'errors': result.errors
        }
        
        logger.info(f"Analysis completed: {len(result.technologies)} technologies detected")
        
        return jsonify(analysis_data)
        
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get system status"""
    try:
        if not detector:
            return jsonify({
                'status': 'error',
                'message': 'Detector not initialized',
                'engines': {
                    'pattern_matching': False,
                    'whatweb': False,
                    'cmseek': False
                }
            }), 500
        
        return jsonify({
            'status': 'ok',
            'engines': {
                'pattern_matching': True,
                'whatweb': detector.whatweb.available,
                'cmseek': detector.cmseek.available
            },
            'technologies_count': len(detector.dataset_manager.all_technologies),
            'patterns_count': sum(len(patterns) for patterns in detector.dataset_manager.pattern_database.values())
        })
        
    except Exception as e:
        logger.error(f"Status check failed: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/domains', methods=['GET'])
def get_available_domains():
    """Get list of previously analyzed domains"""
    try:
        output_dir = Path(__file__).parent / 'output' / 'enhanced_cms_detection'
        domains = []
        
        if output_dir.exists():
            for domain_dir in output_dir.iterdir():
                if domain_dir.is_dir():
                    json_file = domain_dir / f"{domain_dir.name}_enhanced_analysis.json"
                    if json_file.exists():
                        try:
                            with open(json_file, 'r') as f:
                                data = json.load(f)
                                domains.append({
                                    'domain': domain_dir.name.replace('_', '.'),
                                    'technologies_count': len(data.get('technologies', [])),
                                    'analysis_time': data.get('analysis_time', 0),
                                    'last_analyzed': json_file.stat().st_mtime
                                })
                        except Exception as e:
                            logger.warning(f"Failed to load domain data for {domain_dir.name}: {e}")
        
        # Sort by last analyzed time
        domains.sort(key=lambda x: x['last_analyzed'], reverse=True)
        
        return jsonify({'domains': domains})
        
    except Exception as e:
        logger.error(f"Failed to get domains: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/domain/<domain>', methods=['GET'])
def get_domain_analysis(domain):
    """Get analysis results for a specific domain"""
    try:
        domain_clean = domain.replace('.', '_')
        json_file = Path(__file__).parent / 'output' / 'enhanced_cms_detection' / domain_clean / f"{domain_clean}_enhanced_analysis.json"
        
        if not json_file.exists():
            return jsonify({'error': 'Domain analysis not found'}), 404
        
        with open(json_file, 'r') as f:
            data = json.load(f)
        
        return jsonify(data)
        
    except Exception as e:
        logger.error(f"Failed to get domain analysis: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/categories', methods=['GET'])
def get_categories():
    """Get all available technology categories"""
    try:
        if not detector:
            return jsonify({'error': 'Detector not initialized'}), 500
        
        categories = set()
        for tech in detector.dataset_manager.all_technologies.values():
            category = tech.get('category', 'Unknown')
            categories.add(category)
        
        return jsonify({'categories': sorted(list(categories))})
        
    except Exception as e:
        logger.error(f"Failed to get categories: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'detector_initialized': detector is not None,
        'timestamp': asyncio.get_event_loop().time()
    })

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500


def main():
    """Main function to run the server"""
    print("🚀 Starting Tech Detection API Server...")
    
    # Initialize detector
    if not initialize_detector():
        print("❌ Failed to initialize detector. Exiting.")
        sys.exit(1)
    
    print("✅ Detector initialized successfully")
    print("📊 System Statistics:")
    print(f"   - Technologies: {len(detector.dataset_manager.all_technologies)}")
    print(f"   - Patterns: {sum(len(patterns) for patterns in detector.dataset_manager.pattern_database.values())}")
    print(f"   - WhatWeb: {'✅ Available' if detector.whatweb.available else '❌ Not Available'}")
    print(f"   - CMSeeK: {'✅ Available' if detector.cmseek.available else '❌ Not Available'}")
    
    # Run Flask app
    print("\n🌐 Starting web server...")
    print("📱 Dashboard available at: http://localhost:9000")
    print("🔧 API endpoints available at: http://localhost:9000/api/")
    print("🌐 External access: http://159.65.65.140:9000")
    
    app.run(host='0.0.0.0', port=9000, debug=True)

if __name__ == '__main__':
    main()

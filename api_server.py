#!/usr/bin/env python3
"""
Flask API Server for Tech Detection Dashboard
"""

import asyncio
import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Dict, Any, List

from flask import Flask, request, jsonify, send_from_directory, render_template_string
from flask_cors import CORS
import aiohttp
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, str(Path(__file__).parent))

from ultimate_tech_detector import UltimateTechDetector
from logging_config import get_logger, log_analysis_start, log_analysis_complete, log_analysis_error, log_engine_status

logger = get_logger('api_server')
app = Flask(__name__)
CORS(app)
detector = None

class GroqAIIntegration:
    """Integration with Groq AI for technology summarization"""
    
    def __init__(self):
        self.api_key = os.getenv('GROK_API_KEY')
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"
        self.model = "llama-3.3-70b-versatile"
        
    async def summarize_technology(self, tech_data: Dict[str, Any]) -> str:
        """Generate a summary of technology data using Groq AI"""
        if not self.api_key:
            return self._generate_fallback_summary(tech_data)
            
        try:
            # Prepare the prompt for Groq AI
            prompt = f"""
            Please provide a comprehensive security-focused analysis of this technology detection data:
            
            Technology: {tech_data.get('name', 'Unknown')}
            Category: {tech_data.get('category', 'Unknown')}
            Confidence: {tech_data.get('confidence', 0)}%
            Source: {tech_data.get('source', 'Unknown')}
            Website: {tech_data.get('website', 'N/A')}
            Versions: {', '.join(tech_data.get('versions', [])) if tech_data.get('versions') else 'N/A'}
            
            Evidence:
            {self._format_evidence(tech_data.get('evidence', []))}
            
            Please provide a detailed analysis including:
            
            **1. Technology Overview:**
            - Brief description of what this technology is
            - Primary purpose and functionality
            - Common deployment scenarios
            
            **2. Security Analysis:**
            - OWASP Top 10 vulnerabilities that may apply
            - Known security weaknesses and attack vectors
            - Security best practices for this technology
            - Common misconfigurations that lead to vulnerabilities
            
            **3. Threat Assessment:**
            - Potential attack scenarios
            - Impact of security breaches
            - Risk level assessment (High/Medium/Low)
            - Recommended security controls
            
            **4. Technical Details:**
            - Key characteristics based on evidence
            - Version-specific security considerations
            - Configuration recommendations
            
            **5. Compliance & Standards:**
            - Relevant security standards (ISO 27001, NIST, etc.)
            - Compliance requirements
            - Security frameworks that apply
            
            **6. Recommended Actions:**
            - Immediate security steps
            - Long-term security improvements
            - Monitoring and detection recommendations
            
            **7. Font Awesome Icon:**
            - Recommended icon class for this technology
            
            Format the response with clear sections and bullet points for easy reading.
            Focus on actionable security insights and OWASP guidance.
            """
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": 500,
                "temperature": 0.7
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(self.base_url, headers=headers, json=payload, timeout=30) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result['choices'][0]['message']['content']
                    else:
                        error_text = await response.text()
                        logger.error(f"Groq AI API error: {response.status} - {error_text}")
                        # Use fallback when API fails
                        return self._generate_fallback_summary(tech_data)
                        
        except Exception as e:
            logger.error(f"Groq AI integration error: {e}")
            # Use fallback when there's an error
            return self._generate_fallback_summary(tech_data)
    
    def _format_evidence(self, evidence: List[Dict]) -> str:
        """Format evidence data for the prompt"""
        if not evidence:
            return "No evidence available"
        
        formatted = []
        for item in evidence:
            formatted.append(f"- {item.get('field', 'Unknown')}: {item.get('detail', 'N/A')}")
        
        return '\n'.join(formatted)
    
    def _generate_fallback_summary(self, tech_data: Dict[str, Any]) -> str:
        """Generate a fallback summary when Grok AI is not available"""
        name = tech_data.get('name', 'Unknown')
        category = tech_data.get('category', 'Unknown')
        confidence = tech_data.get('confidence', 0)
        source = tech_data.get('source', 'Unknown')
        
        summary = f"""
**Technology Analysis: {name}**

**Overview:**
{name} is a {category.lower()} technology detected with {confidence}% confidence.

**Detection Details:**
- **Category:** {category}
- **Confidence:** {confidence}%
- **Source:** {source}
- **Detection Method:** {source}

**Technical Information:**
"""
        
        if tech_data.get('website'):
            summary += f"- **Official Website:** {tech_data['website']}\n"
        
        if tech_data.get('versions'):
            versions = ', '.join(tech_data['versions'])
            summary += f"- **Detected Versions:** {versions}\n"
        
        if tech_data.get('evidence'):
            summary += f"- **Evidence Found:** {len(tech_data['evidence'])} detection points\n"
        
        # Add category-specific security information
        if category.lower() in ['cms', 'content management system']:
            summary += "\n**CMS Security Analysis:**\n"
            summary += "• **OWASP Top 10 Risks:** A01-Broken Access Control, A03-Injection, A05-Security Misconfiguration\n"
            summary += "• **Common Vulnerabilities:** SQL injection, XSS, CSRF, file upload vulnerabilities\n"
            summary += "• **Security Controls:** Regular updates, strong authentication, input validation\n"
            summary += "• **Risk Level:** Medium-High (depends on configuration and updates)\n"
        elif category.lower() in ['web framework', 'framework']:
            summary += "\n**Framework Security Analysis:**\n"
            summary += "• **OWASP Top 10 Risks:** A01-Broken Access Control, A03-Injection, A07-Identification Failures\n"
            summary += "• **Common Vulnerabilities:** Dependency vulnerabilities, configuration issues\n"
            summary += "• **Security Controls:** Secure coding practices, dependency management, regular updates\n"
            summary += "• **Risk Level:** Medium (depends on implementation and maintenance)\n"
        elif category.lower() in ['web server', 'server']:
            summary += "\n**Server Security Analysis:**\n"
            summary += "• **OWASP Top 10 Risks:** A05-Security Misconfiguration, A09-Security Logging Failures\n"
            summary += "• **Common Vulnerabilities:** Default configurations, unpatched vulnerabilities\n"
            summary += "• **Security Controls:** Hardening, regular updates, monitoring, access controls\n"
            summary += "• **Risk Level:** High (critical infrastructure component)\n"
        elif category.lower() in ['analytics', 'tracking']:
            summary += "\n**Analytics Security Analysis:**\n"
            summary += "• **OWASP Top 10 Risks:** A01-Broken Access Control, A03-Injection, A04-Insecure Design\n"
            summary += "• **Common Vulnerabilities:** Data exposure, privacy violations, XSS\n"
            summary += "• **Security Controls:** Data encryption, access controls, privacy compliance\n"
            summary += "• **Risk Level:** Medium (privacy and data protection concerns)\n"
        elif category.lower() in ['security']:
            summary += "\n**Security Technology Analysis:**\n"
            summary += "• **OWASP Top 10 Risks:** A05-Security Misconfiguration, A09-Security Logging Failures\n"
            summary += "• **Common Vulnerabilities:** Implementation flaws, configuration errors\n"
            summary += "• **Security Controls:** Proper implementation, regular testing, monitoring\n"
            summary += "• **Risk Level:** Low-Medium (security-enhancing technology)\n"
        
        summary += f"\n**Security Recommendations:**\n"
        summary += f"• **Immediate Actions:** Review configuration, check for updates, assess current security posture\n"
        summary += f"• **Long-term:** Implement security monitoring, regular security assessments, incident response planning\n"
        summary += f"• **Compliance:** Ensure adherence to relevant security standards (ISO 27001, NIST, OWASP)\n"
        summary += f"• **Monitoring:** Set up security alerts, log analysis, vulnerability scanning\n"
        
        return summary.strip()

# Initialize Groq AI integration
groq_ai = GroqAIIntegration()

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

@app.route('/static/<path:filename>')
def static_files(filename):
    """Serve static files"""
    return send_from_directory('static', filename)

@app.route('/<path:filename>')
def serve_static(filename):
    """Serve static files from frontend directory"""
    frontend_path = Path(__file__).parent / 'frontend'
    return send_from_directory(frontend_path, filename)

@app.route('/api/analyze', methods=['POST'])
def analyze_domain():
    """Analyze a domain for technologies"""
    start_time = time.time()
    client_ip = request.remote_addr
    user_agent = request.headers.get('User-Agent', 'Unknown')
    
    try:
        data = request.get_json()
        domain = data.get('domain', '').strip()
        engines = data.get('engines', ['pattern', 'whatweb', 'cmseek', 'whatcms', 'wappalyzer', 'additional', 'deep'])
        
        logger.info(f"API_REQUEST: {client_ip} - Analyzing domain: {domain} with engines: {engines}")
        logger.debug(f"REQUEST_DETAILS: User-Agent: {user_agent}, Request data: {data}")
        
        if not domain:
            logger.warning(f"API_ERROR: {client_ip} - No domain provided")
            return jsonify({'error': 'Domain is required'}), 400
        
        if not detector:
            logger.error(f"API_ERROR: {client_ip} - Detector not initialized")
            return jsonify({'error': 'Detector not initialized'}), 500
        
        # Clean domain input
        original_domain = domain
        if not domain.startswith(('http://', 'https://')):
            domain = f'https://{domain}'
        
        logger.info(f"DOMAIN_CLEANED: {original_domain} -> {domain}")
        
        # Log analysis start
        log_analysis_start(domain, engines)
        
        # Run analysis using asyncio
        try:
            # Use the existing event loop or create a new one
            try:
                loop = asyncio.get_event_loop()
                logger.debug("Using existing event loop")
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                logger.debug("Created new event loop")
            
            logger.info(f"STARTING_ANALYSIS: {domain} with {len(engines)} engines")
            result = loop.run_until_complete(detector.analyze_url(domain, engines=engines))
            logger.info(f"ANALYSIS_COMPLETED: {domain} - {len(result.technologies)} technologies detected in {result.analysis_time:.2f}s")
            
        except Exception as e:
            logger.error(f"ANALYSIS_FAILED: {domain} - {str(e)}")
            log_analysis_error(domain, str(e))
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
        
        # Log detailed results
        logger.info(f"ANALYSIS_RESULTS: {domain} - {len(result.technologies)} technologies, {result.analysis_time:.2f}s")
        if result.metadata and 'detection_breakdown' in result.metadata:
            breakdown = result.metadata['detection_breakdown']
            logger.info(f"DETECTION_BREAKDOWN: {domain} - {breakdown}")
        
        # Log completion
        engines_used = [engine for engine in engines if result.metadata.get('detection_breakdown', {}).get(engine, 0) > 0]
        log_analysis_complete(domain, len(result.technologies), result.analysis_time, engines_used)
        
        # Log response time
        response_time = time.time() - start_time
        logger.info(f"API_RESPONSE_TIME: {domain} - {response_time:.2f}s total (analysis: {result.analysis_time:.2f}s)")
        
        return jsonify(analysis_data)
        
    except Exception as e:
        logger.error(f"API_ERROR: {client_ip} - {str(e)}")
        log_analysis_error(domain if 'domain' in locals() else 'unknown', str(e))
        return jsonify({'error': str(e)}), 500

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get system status"""
    client_ip = request.remote_addr
    logger.info(f"STATUS_REQUEST: {client_ip} - Checking system status")
    
    try:
        if not detector:
            logger.warning(f"STATUS_ERROR: {client_ip} - Detector not initialized")
            return jsonify({
                'status': 'error',
                'message': 'Detector not initialized',
                'engines': {
                    'pattern_matching': False,
                    'whatweb': False,
                    'cmseek': False,
                    'whatcms': False,
                    'wappalyzer': False
                }
            }), 500
        
        # Check engine availability
        engine_status = {
            'pattern_matching': True,
            'whatweb': detector.whatweb.available,
            'cmseek': detector.cmseek.available,
            'whatcms': detector.whatcms.available,
            'wappalyzer': detector.wappalyzer.available
        }
        
        # Log engine status
        for engine, available in engine_status.items():
            log_engine_status(engine, "Available" if available else "Unavailable")
        
        technologies_count = len(detector.dataset_manager.all_technologies)
        patterns_count = sum(len(patterns) for patterns in detector.dataset_manager.pattern_database.values())
        
        logger.info(f"STATUS_SUCCESS: {client_ip} - {technologies_count} technologies, {patterns_count} patterns")
        
        return jsonify({
            'status': 'ok',
            'engines': engine_status,
            'technologies_count': technologies_count,
            'patterns_count': patterns_count
        })
        
    except Exception as e:
        logger.error(f"STATUS_ERROR: {client_ip} - {str(e)}")
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

@app.route('/api/logs', methods=['POST'])
def receive_client_logs():
    """Receive client-side logs"""
    try:
        data = request.get_json()
        client_ip = request.remote_addr
        
        logger.info(f"CLIENT_LOG: {client_ip} - {data.get('level', 'unknown').upper()}: {data.get('message', '')}")
        
        if data.get('data'):
            logger.debug(f"CLIENT_LOG_DATA: {data.get('data')}")
        
        return jsonify({'status': 'received'})
        
    except Exception as e:
        logger.error(f"Failed to process client log: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/summarize', methods=['POST'])
def summarize_technology():
    """Generate AI summary for a technology using Grok AI"""
    try:
        data = request.get_json()
        tech_data = data.get('technology')
        
        if not tech_data:
            return jsonify({'error': 'No technology data provided'}), 400
        
        logger.info(f"GROQ_REQUEST: Summarizing technology: {tech_data.get('name', 'Unknown')}")
        
        # Run the async function
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        summary = loop.run_until_complete(groq_ai.summarize_technology(tech_data))
        loop.close()
        
        logger.info(f"GROQ_RESPONSE: Summary generated for {tech_data.get('name', 'Unknown')}")
        
        return jsonify({
            'summary': summary,
            'technology': tech_data.get('name', 'Unknown')
        })
        
    except Exception as e:
        logger.error(f"GROQ_ERROR: Failed to generate summary: {e}")
        return jsonify({'error': str(e)}), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500


def main():
    """Main function to run the server"""
    print(" Starting Tech Detection API Server...")
    
    # Initialize detector
    if not initialize_detector():
        print("❌ Failed to initialize detector. Exiting.")
        sys.exit(1)
    
    print(" Detector initialized successfully")
    print(" System Statistics:")
    print(f"   - Technologies: {len(detector.dataset_manager.all_technologies)}")
    print(f"   - Patterns: {sum(len(patterns) for patterns in detector.dataset_manager.pattern_database.values())}")
    print(f"   - WhatWeb: {' Available' if detector.whatweb.available else '❌ Not Available'}")
    print(f"   - CMSeeK: {' Available' if detector.cmseek.available else '❌ Not Available'}")
    
    # Run Flask app
    print("\n🌐 Starting web server...")
    print("📱 Dashboard available at: http://localhost:9000")
    print(" API endpoints available at: http://localhost:9000/api/")
    print("🌐 External access: http://159.65.65.140:9000")
    
    app.run(host='0.0.0.0', port=9000, debug=True)

if __name__ == '__main__':
    main()

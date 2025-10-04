"""
Integration Modules
==================

Integration modules for external detection engines.
"""

from .whatweb_integration import WhatWebIntegration
from .wappalyzer_integration import WappalyzerIntegration

__all__ = [
    'WhatWebIntegration',
    'WappalyzerIntegration'
]

"""
User Agent Management

Comprehensive user agent collection for robust web technology detection.
"""

import random
from typing import List, Dict, Optional

class UserAgentManager:
    """Manages multiple user agents for robust detection"""
    
    def __init__(self):
        self.user_agents = self._load_user_agents()
        self.current_index = 0
    
    def _load_user_agents(self) -> List[Dict[str, str]]:
        """Load comprehensive user agent collection"""
        return [
            {
                "name": "Chrome Windows",
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "browser": "Chrome",
                "os": "Windows",
                "version": "120.0.0.0"
            },
            {
                "name": "Chrome Windows",
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
                "browser": "Chrome",
                "os": "Windows",
                "version": "119.0.0.0"
            },
            {
                "name": "Chrome Windows",
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
                "browser": "Chrome",
                "os": "Windows",
                "version": "118.0.0.0"
            },
            {
                "name": "Chrome macOS",
                "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "browser": "Chrome",
                "os": "macOS",
                "version": "120.0.0.0"
            },
            {
                "name": "Chrome macOS",
                "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
                "browser": "Chrome",
                "os": "macOS",
                "version": "119.0.0.0"
            },
            
            {
                "name": "Chrome Linux",
                "user_agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "browser": "Chrome",
                "os": "Linux",
                "version": "120.0.0.0"
            },
            {
                "name": "Chrome Linux",
                "user_agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
                "browser": "Chrome",
                "os": "Linux",
                "version": "119.0.0.0"
            },
            
            {
                "name": "Firefox Windows",
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
                "browser": "Firefox",
                "os": "Windows",
                "version": "121.0"
            },
            {
                "name": "Firefox Windows",
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
                "browser": "Firefox",
                "os": "Windows",
                "version": "120.0"
            },
            
            {
                "name": "Firefox macOS",
                "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0",
                "browser": "Firefox",
                "os": "macOS",
                "version": "121.0"
            },
            {
                "name": "Firefox macOS",
                "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:120.0) Gecko/20100101 Firefox/120.0",
                "browser": "Firefox",
                "os": "macOS",
                "version": "120.0"
            },
            
            {
                "name": "Firefox Linux",
                "user_agent": "Mozilla/5.0 (X11; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0",
                "browser": "Firefox",
                "os": "Linux",
                "version": "121.0"
            },
            {
                "name": "Firefox Linux",
                "user_agent": "Mozilla/5.0 (X11; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0",
                "browser": "Firefox",
                "os": "Linux",
                "version": "120.0"
            },
            
            {
                "name": "Safari macOS",
                "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
                "browser": "Safari",
                "os": "macOS",
                "version": "17.1"
            },
            {
                "name": "Safari macOS",
                "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Safari/605.1.15",
                "browser": "Safari",
                "os": "macOS",
                "version": "16.6"
            },
            
            {
                "name": "Edge Windows",
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
                "browser": "Edge",
                "os": "Windows",
                "version": "120.0.0.0"
            },
            {
                "name": "Edge Windows",
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0",
                "browser": "Edge",
                "os": "Windows",
                "version": "119.0.0.0"
            },
            
            {
                "name": "Safari iOS",
                "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1",
                "browser": "Safari",
                "os": "iOS",
                "version": "17.1"
            },
            {
                "name": "Safari iOS",
                "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1",
                "browser": "Safari",
                "os": "iOS",
                "version": "16.6"
            },
            
            {
                "name": "Chrome Android",
                "user_agent": "Mozilla/5.0 (Linux; Android 14; SM-G998B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
                "browser": "Chrome",
                "os": "Android",
                "version": "120.0.0.0"
            },
            {
                "name": "Chrome Android",
                "user_agent": "Mozilla/5.0 (Linux; Android 13; SM-G998B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Mobile Safari/537.36",
                "browser": "Chrome",
                "os": "Android",
                "version": "119.0.0.0"
            },
            
            {
                "name": "Google Bot",
                "user_agent": "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
                "browser": "Googlebot",
                "os": "Unknown",
                "version": "2.1"
            },
            {
                "name": "Bing Bot",
                "user_agent": "Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)",
                "browser": "Bingbot",
                "os": "Unknown",
                "version": "2.0"
            },
            {
                "name": "Facebook Bot",
                "user_agent": "facebookexternalhit/1.1 (+http://www.facebook.com/externalhit_uatext.php)",
                "browser": "FacebookBot",
                "os": "Unknown",
                "version": "1.1"
            },
            
            {
                "name": "IE 11",
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko",
                "browser": "Internet Explorer",
                "os": "Windows",
                "version": "11.0"
            },
            {
                "name": "Opera",
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 OPR/106.0.0.0",
                "browser": "Opera",
                "os": "Windows",
                "version": "106.0.0.0"
            }
        ]
    
    def get_random_agent(self) -> str:
        """Get a random user agent"""
        agent = random.choice(self.user_agents)
        return agent["user_agent"]
    
    def get_agent_by_browser(self, browser: str) -> Optional[str]:
        """Get user agent by browser name"""
        for agent in self.user_agents:
            if agent["browser"].lower() == browser.lower():
                return agent["user_agent"]
        return None
    
    def get_agent_by_os(self, os_name: str) -> Optional[str]:
        """Get user agent by OS name"""
        for agent in self.user_agents:
            if agent["os"].lower() == os_name.lower():
                return agent["user_agent"]
        return None
    
    def get_next_agent(self) -> str:
        """Get next user agent in sequence"""
        agent = self.user_agents[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.user_agents)
        return agent["user_agent"]
    
    def get_agents_for_retry(self, max_retries: int = 3) -> List[str]:
        """Get multiple user agents for retry scenarios"""
        agents = []
        for i in range(max_retries):
            agents.append(self.get_next_agent())
        return agents
    
    def get_mobile_agents(self) -> List[str]:
        """Get mobile user agents"""
        return [agent["user_agent"] for agent in self.user_agents 
                if agent["os"] in ["iOS", "Android"]]
    
    def get_desktop_agents(self) -> List[str]:
        """Get desktop user agents"""
        return [agent["user_agent"] for agent in self.user_agents 
                if agent["os"] in ["Windows", "macOS", "Linux"]]
    
    def get_bot_agents(self) -> List[str]:
        """Get bot/crawler user agents"""
        return [agent["user_agent"] for agent in self.user_agents 
                if "bot" in agent["browser"].lower() or "crawler" in agent["browser"].lower()]
    
    def get_all_agents(self) -> List[Dict[str, str]]:
        """Get all user agents with metadata"""
        return self.user_agents.copy()
    
    def get_agent_info(self, user_agent: str) -> Optional[Dict[str, str]]:
        """Get metadata for a specific user agent"""
        for agent in self.user_agents:
            if agent["user_agent"] == user_agent:
                return agent
        return None

user_agent_manager = UserAgentManager()

def get_random_user_agent() -> str:
    """Get a random user agent (convenience function)"""
    return user_agent_manager.get_random_agent()

def get_user_agents_for_retry(max_retries: int = 3) -> List[str]:
    """Get user agents for retry scenarios (convenience function)"""
    return user_agent_manager.get_agents_for_retry(max_retries)

def get_mobile_user_agents() -> List[str]:
    """Get mobile user agents (convenience function)"""
    return user_agent_manager.get_mobile_agents()

def get_desktop_user_agents() -> List[str]:
    """Get desktop user agents (convenience function)"""
    return user_agent_manager.get_desktop_agents()

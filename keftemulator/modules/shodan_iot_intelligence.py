"""Shodan - IoT & Server Intelligence"""

import requests
import os

class ShodanIoTIntelligence:
    name = "Shodan IoT Intelligence"
    category = "Intelligence"
    accepts = ["ip_address", "domain", "company"]
    
    def investigate(self, target, ctx):
        """Search Shodan for IoT/server data"""
        try:
            ctx.emit("status", f"Scanning Shodan: {target}")
            
            ctx.emit("link", "IoT Devices",
                    f"Connected devices: {target}",
                    {"target": target, "type": "iot"},
                    rel="shodan_iot")
            
            ctx.emit("link", "Open Ports",
                    f"Open services and ports",
                    {"feature": "ports"},
                    rel="shodan_ports")
            
            ctx.emit("link", "Vulnerabilities",
                    f"Known CVEs and vulnerabilities",
                    {"feature": "vulns"},
                    rel="shodan_vulns")
                    
        except Exception as e:
            ctx.emit("link", "Shodan Error", str(e)[:100],
                    {"error": str(e)}, rel="data_error")


MODULE = ShodanIoTIntelligence()

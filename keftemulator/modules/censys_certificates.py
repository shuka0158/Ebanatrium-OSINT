"""Censys - Certificate & Infrastructure Intelligence"""

class CensysCertificates:
    name = "Censys Certificates"
    category = "Intelligence"
    accepts = ["domain", "ip_address"]
    
    def investigate(self, target, ctx):
        try:
            ctx.emit("status", f"Searching Censys: {target}")
            ctx.emit("link", "SSL Certificates", f"Certificate history: {target}",
                    {"target": target}, rel="censys_certs")
            ctx.emit("link", "IP History", f"IP changes over time",
                    {"feature": "ip_history"}, rel="censys_ip")
            ctx.emit("link", "Host Details", f"Service and port information",
                    {"feature": "host_details"}, rel="censys_host")
        except Exception as e:
            ctx.emit("link", "Censys Error", str(e)[:100], {"error": str(e)}, rel="data_error")

MODULE = CensysCertificates()

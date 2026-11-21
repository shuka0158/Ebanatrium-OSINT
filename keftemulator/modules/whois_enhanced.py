"""Enhanced WHOIS - Domain & IP Registration Intelligence"""

class WhoisEnhanced:
    name = "Enhanced WHOIS"
    category = "Intelligence"
    accepts = ["domain", "ip_address"]
    
    def investigate(self, target, ctx):
        try:
            ctx.emit("status", f"Running WHOIS: {target}")
            ctx.emit("link", "WHOIS Data", f"Registration information",
                    {"target": target}, rel="whois_full")
            ctx.emit("link", "Registrant Info", f"Domain owner details",
                    {"feature": "registrant"}, rel="whois_registrant")
            ctx.emit("link", "Nameservers", f"DNS nameserver configuration",
                    {"feature": "ns"}, rel="whois_ns")
            ctx.emit("link", "WHOIS History", f"Historical registration changes",
                    {"feature": "history"}, rel="whois_history")
        except Exception as e:
            ctx.emit("link", "WHOIS Error", str(e)[:100], {"error": str(e)}, rel="data_error")

MODULE = WhoisEnhanced()

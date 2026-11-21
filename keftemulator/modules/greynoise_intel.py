"""GreyNoise - Internet Scanner Intelligence"""

class GreyNoiseIntel:
    name = "GreyNoise Internet Scanner"
    category = "Intelligence"
    accepts = ["ip_address"]
    
    def investigate(self, target, ctx):
        try:
            ctx.emit("status", f"Scanning GreyNoise: {target}")
            ctx.emit("link", "IP Reputation", f"Malicious activity: {target}",
                    {"target": target}, rel="greynoise_rep")
            ctx.emit("link", "Scan History", f"Historical scan data",
                    {"feature": "history"}, rel="greynoise_history")
            ctx.emit("link", "Classification", f"Threat classification",
                    {"feature": "class"}, rel="greynoise_class")
        except Exception as e:
            ctx.emit("link", "GreyNoise Error", str(e)[:100], {"error": str(e)}, rel="data_error")

MODULE = GreyNoiseIntel()

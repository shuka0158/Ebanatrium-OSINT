"""Crunchbase - Startup & Company Intelligence"""

class CrunchbaseStartupIntel:
    name = "Crunchbase Startup Intelligence"
    category = "Intelligence"
    accepts = ["company", "domain"]
    
    def investigate(self, target, ctx):
        try:
            ctx.emit("status", f"Searching Crunchbase: {target}")
            ctx.emit("link", "Company Profile", f"Startup/company data",
                    {"target": target}, rel="cb_profile")
            ctx.emit("link", "Funding Rounds", f"Investment history",
                    {"feature": "funding"}, rel="cb_funding")
            ctx.emit("link", "Team Members", f"Leadership and employees",
                    {"feature": "team"}, rel="cb_team")
        except Exception as e:
            ctx.emit("link", "Crunchbase Error", str(e)[:100], {"error": str(e)}, rel="data_error")

MODULE = CrunchbaseStartupIntel()

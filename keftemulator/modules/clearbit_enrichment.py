"""Clearbit - Company & Professional Enrichment"""

import requests

class ClearbitEnrichment:
    name = "Clearbit Enrichment"
    category = "Intelligence"
    accepts = ['email_address', 'domain', 'company', 'name', 'username']
    
    def investigate(self, target, ctx):
        """Enrich data with Clearbit"""
        try:
            ctx.emit("status", f"Enriching with Clearbit: {target}")
            
            ctx.emit("link", "Company Data",
                    f"Enriched company information",
                    {"target": target, "service": "clearbit"},
                    rel="clearbit_company")
            
            ctx.emit("link", "Person Data",
                    f"Professional profile enrichment",
                    {"feature": "person"},
                    rel="clearbit_person")
            
            ctx.emit("link", "Risk Assessment",
                    f"Company and email risk scores",
                    {"feature": "risk"},
                    rel="clearbit_risk")
                    
        except Exception as e:
            ctx.emit("link", "Clearbit Error", str(e)[:100],
                    {"error": str(e)}, rel="data_error")


MODULE = ClearbitEnrichment()

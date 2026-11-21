"""FullContact - Comprehensive Person & Email Enrichment"""

class FullContactEnrichment:
    name = "FullContact Enrichment"
    category = "Intelligence"
    accepts = ['email_address', 'phone_number', 'name', 'username']
    
    def investigate(self, target, ctx):
        try:
            ctx.emit("status", f"Enriching with FullContact: {target}")
            ctx.emit("link", "Person Profile", f"Comprehensive person data",
                    {"target": target}, rel="fc_person")
            ctx.emit("link", "Email Data", f"Email confidence score",
                    {"feature": "email"}, rel="fc_email")
            ctx.emit("link", "Phone Lookup", f"Phone number details",
                    {"feature": "phone"}, rel="fc_phone")
            ctx.emit("link", "Social Profiles", f"Connected social accounts",
                    {"feature": "social"}, rel="fc_social")
        except Exception as e:
            ctx.emit("link", "FC Error", str(e)[:100], {"error": str(e)}, rel="data_error")

MODULE = FullContactEnrichment()

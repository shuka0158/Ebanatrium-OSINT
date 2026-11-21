"""ZoomInfo - Business & Professional Intelligence"""

class ZoomInfoIntelligence:
    name = "ZoomInfo Intelligence"
    category = "Intelligence"
    accepts = ["company", "email_address", "phone_number"]
    
    def investigate(self, target, ctx):
        try:
            ctx.emit("status", f"Searching ZoomInfo: {target}")
            ctx.emit("link", "Company Profile", f"Detailed company data",
                    {"target": target}, rel="zi_company")
            ctx.emit("link", "Executive Directory", f"Company leadership",
                    {"feature": "execs"}, rel="zi_execs")
            ctx.emit("link", "Employee Directory", f"Company employees",
                    {"feature": "employees"}, rel="zi_employees")
            ctx.emit("link", "Company Tech Stack", f"Technologies used",
                    {"feature": "tech"}, rel="zi_tech")
        except Exception as e:
            ctx.emit("link", "ZoomInfo Error", str(e)[:100], {"error": str(e)}, rel="data_error")

MODULE = ZoomInfoIntelligence()

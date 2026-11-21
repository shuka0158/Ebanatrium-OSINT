"""Google Maps - Geolocation & Business Intelligence"""

class GoogleMapsIntel:
    name = "Google Maps Intelligence"
    category = "Intelligence"
    accepts = ["company", "domain", "phone_number"]
    
    def investigate(self, target, ctx):
        try:
            ctx.emit("status", f"Searching Google Maps: {target}")
            ctx.emit("link", "Business Location", f"Address and coordinates",
                    {"target": target}, rel="gmaps_location")
            ctx.emit("link", "Hours & Contact", f"Operating hours and phone",
                    {"feature": "hours"}, rel="gmaps_contact")
            ctx.emit("link", "Reviews", f"User reviews and ratings",
                    {"feature": "reviews"}, rel="gmaps_reviews")
            ctx.emit("link", "Nearby Locations", f"Related businesses nearby",
                    {"feature": "nearby"}, rel="gmaps_nearby")
        except Exception as e:
            ctx.emit("link", "GMaps Error", str(e)[:100], {"error": str(e)}, rel="data_error")

MODULE = GoogleMapsIntel()

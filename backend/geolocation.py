import requests

def get_location_from_ip(ip: str):
    try:
        # Skip for localhost
        if ip in ["127.0.0.1", "localhost", "::1"]:
            return {
                "country": "Sri Lanka",
                "city": "Colombo",
                "region": "Western"
            }
        
        # Use free IP geolocation API
        response = requests.get(f"http://ip-api.com/json/{ip}", timeout=5)
        data = response.json()
        
        if data["status"] == "success":
            return {
                "country": data.get("country", "Unknown"),
                "city": data.get("city", "Unknown"),
                "region": data.get("regionName", "Unknown")
            }
        else:
            return {
                "country": "Unknown",
                "city": "Unknown", 
                "region": "Unknown"
            }
    except:
        return {
            "country": "Unknown",
            "city": "Unknown",
            "region": "Unknown"
        }
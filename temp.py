import requests

# Beispielkoordinaten: Neustadt an der Weinstraße
lat = 48.7758
lon = 9.1829

url = (
    f"https://api.open-meteo.com/v1/forecast?"
    f"latitude={lat}&longitude={lon}&hourly=precipitation"
    f"&forecast_days=1&timezone=Europe/Berlin"
)

response = requests.get(url)
data = response.json()

times = data.get("hourly", {}).get("time", [])
print(f"📅 Anzahl stündlicher Zeitpunkte: {len(times)}")

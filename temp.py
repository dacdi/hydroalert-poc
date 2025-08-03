#!/usr/bin/env python3
"""
export_streets_kml.py

Ein einfaches Skript, das eine Liste von Straßen in Neustadt geokodiert und als KML-Datei exportiert.
Benötigte Bibliotheken:
  pip install geopy simplekml
"""
import sys
from geopy.geocoders import Nominatim
from simplekml import Kml

# Liste der Straßen mit optionaler Zusatzinformation (z. B. Breite)
streets = [
    ("Weinstraße", "50–100 cm"),
    ("An der Eselshaut", "50–100 cm"),
    ("Breitenweg", "50–100 cm"),
    ("Thüringer Straße", "50–100 cm"),
    ("Hermann-Löns-Straße", "50–100 cm"),
    ("Zum Ordenswald", "50–100 cm"),
    ("Am Dreschplatz", "30–50 cm"),
]

# Initialisiere Geocoder und KML-Objekt
geolocator = Nominatim(user_agent="street_kml_exporter")
kml = Kml()

# Durchlaufe jede Straße, geokodiere und füge einen Punkt ein
for name, detail in streets:
    try:
        query = f"{name}, Neustadt, Deutschland"
        location = geolocator.geocode(query)
        if not location:
            print(f"WARNung: Keine Koordinaten für '{name}' gefunden (Suchanfrage: {query})", file=sys.stderr)
            continue
        # Erstelle einen neuen Punkt in der KML
        p = kml.newpoint(name=name, coords=[(location.longitude, location.latitude)])
        p.description = f"Info: {detail}"
    except Exception as e:
        print(f"Fehler bei Geokodierung von '{name}': {e}", file=sys.stderr)

# Speichere die KML-Datei
output_file = "streets_neustadt.kml"
kml.save(output_file)
print(f"KML-Datei '{output_file}' erfolgreich erstellt.")

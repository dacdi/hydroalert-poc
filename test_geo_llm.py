# temp/test_geo_llm_geocode.py
import os, json, re, time, random, sys
import httpx
from dotenv import load_dotenv

# .env laden (braucht OPENAI_API_KEY; optional LLM_MODEL / LLM_BASE_URL)
load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")
MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")
BASE_URL = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1")

# ---------- 1) Koordinaten-Heuristik (billig & schnell) ----------
_LATLON = re.compile(r'(?P<lat>[+-]?\d{1,2}\.\d+)[,\s;]+(?P<lon>[+-]?\d{1,3}\.\d+)')

def extract_latlon(text: str):
    m = _LATLON.search(text)
    if m:
        return float(m.group("lat")), float(m.group("lon"))
    return None

# ---------- 2) LLM: nur ein sauberes place_label erzeugen ----------
def call_llm_for_place_label(user_text: str) -> str | None:
    """
    Fragt das LLM nur nach einem normalisierten Ortslabel, KEIN Radius.
    Antwort ist strikt ein JSON-Objekt: {"place_label": string|null}
    """
    if not API_KEY:
        raise RuntimeError("OPENAI_API_KEY fehlt (.env)")

    prompt = (
        "Extrahiere aus der Eingabe ein präzises, geocoder-taugliches Ortslabel.\n"
        "Antworte NUR als kompaktes JSON-Objekt mit exakt einem Feld:\n"
        '{"place_label": string|null}\n'
        "- Liefere einen eindeutigen, normalen Ortsnamen, z. B. \"München Hauptbahnhof\" oder \"Frankfurt am Main Flughafen\".\n"
        "- Wenn kein sinnvoller Ort erkennbar ist, setze place_label auf null.\n"
        f"Eingabe: {user_text}"
    )

    body = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.0,
        "response_format": {"type": "json_object"},
        "max_tokens": 60,
    }
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

    max_retries, backoff = 4, 1.0
    for attempt in range(max_retries):
        with httpx.Client(timeout=20) as client:
            r = client.post(f"{BASE_URL}/chat/completions", headers=headers, json=body)
        # Rate-Limit → kurzer Backoff
        if r.status_code == 429 and attempt < max_retries - 1:
            retry_after = r.headers.get("retry-after")
            wait = float(retry_after) if retry_after else backoff + random.uniform(0, 0.5)
            print(f"[429] LLM Rate-Limit – warte {wait:.1f}s")
            time.sleep(wait); backoff = min(backoff * 2, 16); continue
        r.raise_for_status()
        data = json.loads(r.json()["choices"][0]["message"]["content"])
        label = data.get("place_label")
        return label if (isinstance(label, str) and label.strip()) else None
    return None

# ---------- 3) Geocoder (Nominatim / OpenStreetMap) ----------
def geocode_place(label: str) -> tuple[float, float] | None:
    """
    Löst ein Ortslabel in Koordinaten auf. Nutzt OSM Nominatim (öffentliche Demo – bitte sparsam testen).
    Für Produktion: eigener Nominatim-Server oder anderer Geocoder + Rate Limits & Caching.
    """
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": label, "format": "jsonv2", "limit": 1}
    headers = {"User-Agent": "HydroAlert-Test/0.1 (mailto:example@example.com)"}

    max_retries, backoff = 3, 1.0
    for attempt in range(max_retries):
        with httpx.Client(timeout=12, headers=headers) as client:
            r = client.get(url, params=params)
        if r.status_code in (429, 503) and attempt < max_retries - 1:
            wait = backoff + random.uniform(0, 0.5)
            print(f"[{r.status_code}] Geocoder Rate-Limit – warte {wait:.1f}s")
            time.sleep(wait); backoff = min(backoff * 2, 8); continue
        r.raise_for_status()
        data = r.json()
        if not data:
            return None
        try:
            return float(data[0]["lat"]), float(data[0]["lon"])
        except Exception:
            return None
    return None

# ---------- 4) Orchestrierung ----------
def parse_text(text: str) -> dict:
    """
    Ziel: beliebiger User-Text → {lat, lon, place_label, source_text}
    - Falls direkte Dezimalgrad-Koordinaten erkannt: nutze die (kein Geocoder nötig).
    - Sonst: LLM erzeugt place_label → Geocoder liefert lat/lon.
    - KEIN Radius in diesem Skript (Default wird später im System vergeben).
    """
    # A) Direkte Koordinaten?
    latlon = extract_latlon(text)
    if latlon:
        lat, lon = latlon
        return {
            "lat": lat, "lon": lon,
            "place_label": None,
            "source_text": text
        }

    # B) LLM → place_label
    label = call_llm_for_place_label(text)
    lat, lon = (None, None)
    if label:
        geo = geocode_place(label)
        if geo:
            lat, lon = geo

    return {
        "lat": lat, "lon": lon,
        "place_label": label,
        "source_text": text
    }

# ---------- 5) CLI ----------
if __name__ == "__main__":
    user_text = " ".join(sys.argv[1:]) or "Bahnhof München"
    result = parse_text(user_text)
    print(json.dumps(result, ensure_ascii=False, indent=2))

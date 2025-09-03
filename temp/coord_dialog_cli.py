# temp/coord_dialog_cli.py
import os
import re
import json
import sys
import httpx
from dotenv import load_dotenv

"""
Einfacher CLI-Dialog:
- Ziel: Gültige Koordinaten im Format "lat, lon" (Dezimalgrad) einsammeln
- LLM wird NUR genutzt, um bei Fehlern kurze Hilfetexte + Beispiel zu geben
- Bestätigung: Nutzer antwortet 'ja' oder gibt neue Koordinaten ein
"""

# ---------- Setup ----------
load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")
MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")
BASE_URL = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1")

# ---------- Parser/Validator ----------
_RE = re.compile(r'^\s*([+-]?\d{1,2}\.\d+)\s*[,; ]\s*([+-]?\d{1,3}\.\d+)\s*$')

def parse_latlon(text: str):
    m = _RE.match(text)
    if not m:
        return None
    lat, lon = float(m.group(1)), float(m.group(2))
    if not (-90.0 <= lat <= 90.0 and -180.0 <= lon <= 180.0):
        return None
    return round(lat, 5), round(lon, 5)

# ---------- LLM-Hilfe bei Fehlern ----------
def llm_hint_for(user_text: str) -> str:
    """
    Fragt das LLM nach EINEM kurzen Hilfesatz + EINEM Beispiel.
    Wenn kein API-Key gesetzt ist oder ein Fehler passiert, liefert eine lokale Standardhilfe.
    """
    fallback = (
        "Bitte Koordinaten im Format 'lat, lon' mit DezimalPUNKT senden. "
        "Beispiel: 48.1351, 11.5820"
    )
    if not API_KEY:
        return fallback

    prompt = (
        "Du hilfst einem Nutzer, Koordinaten im Dezimalgrad-Format korrekt einzugeben.\n"
        "Regeln:\n"
        "- Nur ZWEI Zahlen: erst lat (−90..90), dann lon (−180..180)\n"
        "- DezimalPUNKT (.), kein Dezimalkomma\n"
        "- Trennung mit Komma oder Leerzeichen\n"
        "Gib eine sehr kurze, freundliche Hilfenachricht auf Deutsch und genau EIN gültiges Beispiel.\n"
        "Antworte NUR als JSON-Objekt mit Feldern:\n"
        '{"hint": string, "example": string}\n'
        f"Fehlerhafte Eingabe war: {user_text}"
    )

    body = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.0,
        "response_format": {"type": "json_object"},
        "max_tokens": 80,
    }
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

    try:
        with httpx.Client(timeout=20) as client:
            r = client.post(f"{BASE_URL}/chat/completions", headers=headers, json=body)
        if r.status_code == 429:
            # Soft-Fallback statt Retries, weil das hier nur ein Test-CLI ist
            return fallback
        r.raise_for_status()
        data = json.loads(r.json()["choices"][0]["message"]["content"])
        hint = data.get("hint")
        example = data.get("example")
        if isinstance(hint, str) and isinstance(example, str) and hint.strip() and example.strip():
            return f"{hint.strip()} Beispiel: {example.strip()}"
        return fallback
    except Exception:
        return fallback

# ---------- Dialog-Loop ----------
def main():
    print("Sende bitte Koordinaten im Format 'lat, lon' (Dezimalgrad).")
    print("Regeln: DezimalPUNKT (.), erst lat, dann lon. Beispiel: 48.1351, 11.5820")
    lat = lon = None
    while True:
        try:
            user = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nAbgebrochen.")
            sys.exit(0)

        if user.lower() in {"abbrechen", "cancel", "quit", "exit"}:
            print("Okay, beendet.")
            sys.exit(0)

        parsed = parse_latlon(user)
        if not parsed:
            # Ungültig → LLM um kurzen Tipp bitten
            print(llm_hint_for(user))
            continue

        lat, lon = parsed
        print(f"Habe: {lat:.5f}, {lon:.5f}. Richtig? Antworte 'ja' oder sende neue Werte.")
        # Bestätigungsschleife
        while True:
            try:
                confirm = input(">> ").strip().lower()
            except (EOFError, KeyboardInterrupt):
                print("\nAbgebrochen.")
                sys.exit(0)
            if confirm == "ja":
                print("Top! Starte Analyse … (hier würdest du HydroAlert aufrufen)")
                # Hier könntest du die Werte weiterreichen:
                # run_hydroalert(lat, lon)
                print(json.dumps({"lat": lat, "lon": lon}, ensure_ascii=False, indent=2))
                return
            else:
                # Nutzer will korrigieren → zurück zur Eingabe
                print("Alles klar. Bitte Koordinaten erneut im Format 'lat, lon' senden.")
                break

if __name__ == "__main__":
    main()

from src.services.telegram_bot_service import handle_message_logic

# Nachricht simulieren – später ersetzen wir das mit echten Koordinaten
user_input = "49.35, 8.10"

antwort_text, kml_path = handle_message_logic(user_input)

print("Antwort:", antwort_text)
print("KML-Pfad:", kml_path)

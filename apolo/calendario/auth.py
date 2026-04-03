import os
from pathlib import Path
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/calendar"]

_APOLO_DIR = Path.home() / "AppData" / "Roaming" / "apolo"
TOKEN_PATH = _APOLO_DIR / "token.json"


def get_calendar_service():
    """
    Retorna un servicio autenticado de Google Calendar API.
    Lee GOOGLE_CLIENT_ID y GOOGLE_CLIENT_SECRET desde .env.
    Primera vez: abre el navegador para OAuth2 y guarda token.json.
    Siguientes veces: reutiliza token.json y lo refresca si expiró.
    """
    client_id = os.getenv("GOOGLE_CLIENT_ID")
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET")

    if not client_id or not client_secret:
        raise ValueError(
            "Faltan GOOGLE_CLIENT_ID o GOOGLE_CLIENT_SECRET en el archivo .env."
        )

    _APOLO_DIR.mkdir(parents=True, exist_ok=True)

    creds = None
    if TOKEN_PATH.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            client_config = {
                "installed": {
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": ["http://localhost"],
                }
            }
            flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
            creds = flow.run_local_server(port=0)
        TOKEN_PATH.write_text(creds.to_json(), encoding="utf-8")

    return build("calendar", "v3", credentials=creds)

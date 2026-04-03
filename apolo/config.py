import os
import json
from pathlib import Path
from zoneinfo import ZoneInfo
import anthropic
from dotenv import load_dotenv
from tavily import TavilyClient

load_dotenv()

# Audio
IDIOMA          = "es-ES"
SAMPLE_RATE     = 16000
BLOCK_SIZE      = int(SAMPLE_RATE * 0.1)
VOZ_THRESHOLD   = 0.02
SILENCIO_LIMITE = 8
MAX_BLOQUES     = 60

# Conversación
TIMEOUT_CONV = 60  # segundos sin hablar antes de salir del modo conversación

# Aplicaciones
DOTA2_STEAM = "steam://rungameid/570"

# Zona horaria — leída de config_usuario.json
_config_path = Path(__file__).parent.parent / "config_usuario.json"
_config_usuario = json.loads(_config_path.read_text(encoding="utf-8")) if _config_path.exists() else {}
ZONA_USUARIO = ZoneInfo(_config_usuario.get("zona_horaria", "America/Bogota"))

# Localización
DIAS_ES = {
    "Monday": "lunes", "Tuesday": "martes", "Wednesday": "miércoles",
    "Thursday": "jueves", "Friday": "viernes", "Saturday": "sábado", "Sunday": "domingo"
}
MESES_ES = {
    1: "enero", 2: "febrero", 3: "marzo", 4: "abril", 5: "mayo", 6: "junio",
    7: "julio", 8: "agosto", 9: "septiembre", 10: "octubre", 11: "noviembre", 12: "diciembre"
}

# Palabras clave
WAKE_WORD       = "apolo"
COMANDO_DOTA    = ["dota"]
COMANDO_HORA    = ["hora", "tiempo", "fecha", "día"]
COMANDO_MUSICA  = ["pon ", "reproduce ", "busca ", "ponme ", "toca "]
COMANDO_ABRIR   = ["abre ", "abrir ", "lanza ", "lanzar ", "inicia ", "iniciar ", "ejecuta ", "ejecutar "]
COMANDO_PARAR   = ["para", "adiós", "adios", "detente", "stop"]
COMANDO_OLVIDAR = ["olvida todo", "borra el historial", "limpia el historial", "nueva conversación"]
COMANDO_CLIMA   = ["clima", "tiempo en", "temperatura", "lluvia", "pronóstico"]

# Clientes API
claude_client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

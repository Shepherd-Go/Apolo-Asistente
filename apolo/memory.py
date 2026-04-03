import json
import re
from pathlib import Path
from apolo.config import claude_client

MEMORIA_PATH = Path("memoria_usuario.json")


def cargar_memoria() -> dict:
    if MEMORIA_PATH.exists():
        with open(MEMORIA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"preferencias": []}


def guardar_memoria(memoria: dict):
    with open(MEMORIA_PATH, "w", encoding="utf-8") as f:
        json.dump(memoria, f, ensure_ascii=False, indent=2)


def memoria_como_texto() -> str:
    prefs = cargar_memoria().get("preferencias", [])
    if not prefs:
        return ""
    return "Lo que sabes del usuario: " + "; ".join(prefs) + "."


def extraer_y_guardar(historial: list):
    if not historial:
        return

    try:
        respuesta = claude_client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=200,
            system=(
                "Eres un extractor de preferencias. Analiza la conversación y extrae datos "
                "personales relevantes del usuario: gustos, ciudad, nombre, hobbies, etc. "
                "Responde SOLO con JSON válido con la clave 'nuevas' que contiene una lista de strings. "
                "Si no hay nada relevante, responde {\"nuevas\": []}."
            ),
            messages=historial + [{
                "role": "user",
                "content": "¿Qué preferencias o datos del usuario puedes extraer de esta conversación?",
            }],
        )
        texto = respuesta.content[0].text
        print(f"  🧠  Respuesta extractor: {texto}")
        match = re.search(r'\{.*\}', texto, re.DOTALL)
        if not match:
            print("  ⚠️  No se encontró JSON en la respuesta del extractor.")
            return
        datos = json.loads(match.group())
        nuevas = datos.get("nuevas", [])
    except Exception as e:
        print(f"  ⚠️  Error extrayendo preferencias: {e}")
        return

    if not nuevas:
        return

    memoria = cargar_memoria()
    existentes = set(memoria["preferencias"])
    agregadas = [p for p in nuevas if p not in existentes]
    memoria["preferencias"].extend(agregadas)
    guardar_memoria(memoria)
    print(f"  🧠  Aprendí {len(agregadas)} preferencia(s) nueva(s): {agregadas}")

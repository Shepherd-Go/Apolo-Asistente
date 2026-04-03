import json
import re
from datetime import datetime
from apolo.config import claude_client, ZONA_USUARIO
from apolo.calendario.auth import get_calendar_service

_SYSTEM_PARSER = """\
Eres un extractor de datos para eventos de calendario. \
El usuario habla en español colombiano informal (puede decir \
"mañana", "pasado mañana", "el viernes", "en dos horas", \
"a las 3 de la tarde", "a las 11 de la mañana", etc.).

Hoy es {hoy_iso} ({dia_semana}), zona horaria {zona}.

Extrae los datos del evento y responde ÚNICAMENTE con JSON válido, \
sin explicaciones, sin markdown, solo el objeto JSON:
{{"titulo": "string con título breve del evento", "fecha_iso": "YYYY-MM-DD", \
"hora_inicio": "HH:MM", "hora_fin": "HH:MM", "descripcion": "string o cadena vacía"}}

Reglas:
- Si el usuario no dice hora de fin, agrégale 1 hora a la hora de inicio.
- Si el usuario dice "mañana" calcula la fecha correcta desde hoy.
- Si el usuario dice "el viernes" elige el próximo viernes futuro.
- "de la tarde" significa hora en rango 12-19; "de la mañana" rango 6-11; "de la noche" rango 20-23.
- "a las 3 de la tarde" es "15:00"; "a las 11 de la mañana" es "11:00".
- El título debe ser conciso: "Eco médico con esposa", "Reunión", etc.
- Nunca incluyas texto fuera del JSON.\
"""

_DIAS_ES = {
    "Monday": "lunes",
    "Tuesday": "martes",
    "Wednesday": "miércoles",
    "Thursday": "jueves",
    "Friday": "viernes",
    "Saturday": "sábado",
    "Sunday": "domingo",
}


def parsear_evento_con_claude(texto_usuario: str) -> dict | None:
    ahora = datetime.now(ZONA_USUARIO)
    system = _SYSTEM_PARSER.format(
        hoy_iso=ahora.strftime("%Y-%m-%d"),
        dia_semana=_DIAS_ES[ahora.strftime("%A")],
        zona=str(ZONA_USUARIO),
    )

    try:
        respuesta = claude_client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=200,
            system=system,
            messages=[{"role": "user", "content": texto_usuario}],
        )
        texto = respuesta.content[0].text.strip()
        print(f"  📅  Parser calendario: {texto}")
        match = re.search(r"\{.*\}", texto, re.DOTALL)
        if not match:
            return None
        datos = json.loads(match.group())
        for campo in ("titulo", "fecha_iso", "hora_inicio", "hora_fin"):
            if campo not in datos:
                return None
        return datos
    except Exception as e:
        print(f"  ❌  Error parseando evento: {e}")
        return None


def _offset_zona(zona) -> str:
    ahora = datetime.now(zona)
    offset = ahora.utcoffset()
    total_min = int(offset.total_seconds() // 60)
    signo = "+" if total_min >= 0 else "-"
    horas, mins = divmod(abs(total_min), 60)
    return f"{signo}{horas:02d}:{mins:02d}"


def crear_evento_calendar(datos: dict) -> dict:
    zona_str = str(ZONA_USUARIO)
    evento = {
        "summary": datos["titulo"],
        "description": datos.get("descripcion", ""),
        "start": {
            "dateTime": f"{datos['fecha_iso']}T{datos['hora_inicio']}:00",
            "timeZone": zona_str,
        },
        "end": {
            "dateTime": f"{datos['fecha_iso']}T{datos['hora_fin']}:00",
            "timeZone": zona_str,
        },
    }
    service = get_calendar_service()
    return service.events().insert(calendarId="primary", body=evento).execute()


def consultar_eventos_por_rango(fecha_inicio: str, fecha_fin: str) -> list[dict]:
    offset = _offset_zona(ZONA_USUARIO)
    service = get_calendar_service()
    resultado = (
        service.events()
        .list(
            calendarId="primary",
            timeMin=f"{fecha_inicio}T00:00:00{offset}",
            timeMax=f"{fecha_fin}T23:59:59{offset}",
            singleEvents=True,
            orderBy="startTime",
            maxResults=20,
        )
        .execute()
    )
    return resultado.get("items", [])


def buscar_eventos_calendar(query: str, dias: int = 365) -> list[dict]:
    ahora = datetime.now(ZONA_USUARIO)
    offset = _offset_zona(ZONA_USUARIO)
    fin = ahora.replace(year=ahora.year + 1)
    service = get_calendar_service()
    resultado = (
        service.events()
        .list(
            calendarId="primary",
            q=query,
            timeMin=f"{ahora.strftime('%Y-%m-%d')}T00:00:00{offset}",
            timeMax=f"{fin.strftime('%Y-%m-%d')}T23:59:59{offset}",
            singleEvents=True,
            orderBy="startTime",
            maxResults=5,
        )
        .execute()
    )
    return resultado.get("items", [])


def consultar_eventos_calendar(fecha_iso: str) -> list[dict]:
    offset = _offset_zona(ZONA_USUARIO)
    service = get_calendar_service()
    resultado = (
        service.events()
        .list(
            calendarId="primary",
            timeMin=f"{fecha_iso}T00:00:00{offset}",
            timeMax=f"{fecha_iso}T23:59:59{offset}",
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )
    return resultado.get("items", [])

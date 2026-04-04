import calendar
from datetime import datetime, timedelta
from apolo.config import ZONA_USUARIO, DIAS_ES, MESES_ES
from apolo.tts import hablar
from apolo.calendario.ops import (
    parsear_evento_con_claude,
    crear_evento_calendar,
    consultar_eventos_calendar,
    buscar_eventos_calendar,
    consultar_eventos_por_rango,
)

_MESES_NUMERO = {
    "enero": 1,
    "febrero": 2,
    "marzo": 3,
    "abril": 4,
    "mayo": 5,
    "junio": 6,
    "julio": 7,
    "agosto": 8,
    "septiembre": 9,
    "octubre": 10,
    "noviembre": 11,
    "diciembre": 12,
}

_KW_LIMPIAR = [
    "cuándo es",
    "cuando es",
    "revisa el calendario",
    "revisen el calendario",
    "en mi calendario",
    "busca en mi calendario",
    "mi agenda",
    "mis eventos",
    "qué tengo",
    "que tengo",
    "qué hay",
    "que hay",
    "tengo algo",
    "tengo para",
    "para",
    "apolo",
]


def _hablar_evento(ev: dict):
    titulo = ev.get("summary", "Evento sin título")
    inicio = ev.get("start", {}).get("dateTime", "")
    if inicio:
        hora_dt = datetime.fromisoformat(inicio)
        hora_int = hora_dt.hour
        hora_m_str = hora_dt.strftime("%M")
        ampm = (
            "de la mañana"
            if hora_int < 12
            else "del mediodía"
            if hora_int == 12
            else "de la tarde"
            if hora_int < 20
            else "de la noche"
        )
        hora_voz = str(hora_int if hora_int <= 12 else hora_int - 12)
        fecha_dt = hora_dt
        dia_nombre = DIAS_ES[fecha_dt.strftime("%A")]
        mes_nombre = MESES_ES[fecha_dt.month]
        hablar(
            f"{titulo}, el {dia_nombre} {fecha_dt.day} de {mes_nombre} a las {hora_voz} y {hora_m_str} {ampm}."
        )
    else:
        fecha_str = ev.get("start", {}).get("date", "")
        if fecha_str:
            fecha_dt = datetime.strptime(fecha_str, "%Y-%m-%d")
            dia_nombre = DIAS_ES[fecha_dt.strftime("%A")]
            mes_nombre = MESES_ES[fecha_dt.month]
            hablar(f"{titulo}, el {dia_nombre} {fecha_dt.day} de {mes_nombre}.")
        else:
            hablar(titulo)


def agendar_evento(texto: str):
    hablar("Un momento, anoto eso.")
    print(f"  📅  Agendando: {texto}")

    datos = parsear_evento_con_claude(texto)
    if not datos:
        hablar("No pude entender los detalles. ¿Puedes repetirlo con fecha y hora?")
        return

    try:
        crear_evento_calendar(datos)
    except FileNotFoundError:
        hablar("No tengo acceso a Google Calendar. Falta el archivo de credenciales.")
        return
    except Exception as e:
        print(f"  ❌  Error creando evento: {e}")
        hablar("Hubo un problema al guardar el evento en Google Calendar.")
        return

    fecha = datetime.strptime(datos["fecha_iso"], "%Y-%m-%d")
    dia_nombre = DIAS_ES[fecha.strftime("%A")]
    mes_nombre = MESES_ES[fecha.month]
    hora_h, _ = datos["hora_inicio"].split(":")
    hora_int = int(hora_h)
    ampm = (
        "de la mañana"
        if hora_int < 12
        else "del mediodía"
        if hora_int == 12
        else "de la tarde"
        if hora_int < 20
        else "de la noche"
    )
    hora_voz = str(hora_int if hora_int <= 12 else hora_int - 12)
    hablar(
        f"Listo, agendé {datos['titulo']} el {dia_nombre} {fecha.day} de {mes_nombre} "
        f"a las {hora_voz} {ampm}."
    )


def ver_agenda(texto_lower: str):
    try:
        ahora = datetime.now(ZONA_USUARIO)

        # ── Hoy / mañana ────────────────────────────────────────────────────
        if "mañana" in texto_lower:
            fecha = ahora + timedelta(days=1)
            eventos = consultar_eventos_calendar(fecha.strftime("%Y-%m-%d"))
            cuando = "mañana"
            if not eventos:
                hablar(f"No tienes eventos para {cuando}.")
                return
            hablar(
                f"Tienes {len(eventos)} evento{'s' if len(eventos) > 1 else ''} para {cuando}."
            )
            for ev in eventos:
                _hablar_evento(ev)
            return

        if "hoy" in texto_lower:
            eventos = consultar_eventos_calendar(ahora.strftime("%Y-%m-%d"))
            cuando = "hoy"
            if not eventos:
                hablar(f"No tienes eventos para {cuando}.")
                return
            hablar(
                f"Tienes {len(eventos)} evento{'s' if len(eventos) > 1 else ''} para {cuando}."
            )
            for ev in eventos:
                _hablar_evento(ev)
            return

        # ── Mes específico ───────────────────────────────────────────────────
        mes_detectado = next((m for m in _MESES_NUMERO if m in texto_lower), None)
        if mes_detectado:
            num_mes = _MESES_NUMERO[mes_detectado]
            anio = ahora.year if num_mes >= ahora.month else ahora.year + 1
            ultimo_dia = calendar.monthrange(anio, num_mes)[1]
            inicio = f"{anio}-{num_mes:02d}-01"
            fin = f"{anio}-{num_mes:02d}-{ultimo_dia:02d}"
            print(f"  📅  Consultando {mes_detectado} {anio}: {inicio} → {fin}")
            eventos = consultar_eventos_por_rango(inicio, fin)
            if not eventos:
                hablar(f"No tienes eventos en {mes_detectado}.")
                return
            hablar(
                f"Tienes {len(eventos)} evento{'s' if len(eventos) > 1 else ''} en {mes_detectado}."
            )
            for ev in eventos:
                _hablar_evento(ev)
            return

        # ── Búsqueda por palabra clave ────────────────────────────────────────
        for kw in _KW_LIMPIAR:
            texto_lower = texto_lower.replace(kw, "")
        query = texto_lower.strip()
        if not query:
            hablar("¿Qué evento quieres buscar en el calendario?")
            return
        print(f"  📅  Buscando en calendario: «{query}»")
        eventos = buscar_eventos_calendar(query)
        if not eventos:
            hablar(f"No encontré eventos relacionados con {query}.")
            return
        hablar(f"Encontré {len(eventos)} resultado{'s' if len(eventos) > 1 else ''}.")
        for ev in eventos:
            _hablar_evento(ev)

    except FileNotFoundError:
        hablar("No tengo acceso a Google Calendar. Falta el archivo de credenciales.")
    except Exception as e:
        print(f"  ❌  Error consultando agenda: {e}")
        hablar("No pude consultar tu agenda en este momento.")

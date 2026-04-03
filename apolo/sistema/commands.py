from datetime import datetime
from apolo.config import ZONA_USUARIO, DIAS_ES, MESES_ES
from apolo.tts import hablar


def decir_hora():
    ahora = datetime.now(ZONA_USUARIO)
    dia = DIAS_ES[ahora.strftime("%A")]
    mes = MESES_ES[ahora.month]
    hora = ahora.strftime("%I").lstrip("0")
    minuto = ahora.strftime("%M")
    ampm = (
        "de la mañana"
        if ahora.hour < 12
        else "del mediodía"
        if ahora.hour == 12
        else "de la tarde"
        if ahora.hour < 20
        else "de la noche"
    )
    hablar(
        f"Hoy es {dia} {ahora.day} de {mes} de {ahora.year}. Son las {hora} y {minuto} {ampm}."
    )

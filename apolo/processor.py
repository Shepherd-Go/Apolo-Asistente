import time
from apolo.config import (
    WAKE_WORD,
    COMANDO_DOTA, COMANDO_HORA, COMANDO_MUSICA,
    COMANDO_PARAR, COMANDO_OLVIDAR, COMANDO_CLIMA, COMANDO_ABRIR,
)
from apolo.commands import buscar_musica, abrir_dota, decir_hora, buscar_y_abrir_app
from apolo.conversation import (
    activar_modo_conv, desactivar_modo_conv,
    limpiar_historial, preguntar_claude,
)
import apolo.conversation as conv


def procesar_comando(texto: str):
    texto_lower = texto.lower()
    print(f"  🗣️  Escuché: «{texto_lower}»")

    tiene_wake = WAKE_WORD in texto_lower

    if tiene_wake and any(p in texto_lower for p in COMANDO_DOTA):
        abrir_dota()
        return

    if (tiene_wake or conv.modo_conv) and any(p in texto_lower for p in COMANDO_ABRIR):
        trigger = next(p for p in COMANDO_ABRIR if p in texto_lower)
        nombre_app = texto_lower.replace(WAKE_WORD, "").replace(trigger, "").strip()
        buscar_y_abrir_app(nombre_app)
        return

    if tiene_wake and any(p in texto_lower for p in COMANDO_HORA):
        decir_hora()
        return

    if (tiene_wake or conv.modo_conv) and any(p in texto_lower for p in COMANDO_MUSICA):
        query = texto_lower.replace(WAKE_WORD, "").strip()
        buscar_musica(query)
        return

    if (tiene_wake or conv.modo_conv) and any(p in texto_lower for p in COMANDO_CLIMA):
        ciudad = (
            texto_lower
            .replace(WAKE_WORD, "")
            .replace("clima", "")
            .replace("tiempo en", "")
            .replace("temperatura", "")
            .replace("pronóstico", "")
            .strip()
        )
        consulta = f"¿Cómo está el clima ahora en {ciudad if ciudad else 'Colombia'}?"
        preguntar_claude(consulta)
        return

    if conv.modo_conv and any(p in texto_lower for p in COMANDO_PARAR):
        desactivar_modo_conv()
        return

    if (tiene_wake or conv.modo_conv) and any(p in texto_lower for p in COMANDO_OLVIDAR):
        limpiar_historial()
        return

    if tiene_wake and not conv.modo_conv:
        pregunta = texto_lower.replace(WAKE_WORD, "").strip()
        activar_modo_conv()
        if pregunta:
            preguntar_claude(pregunta)
        return

    if conv.modo_conv:
        conv.ultimo_habla = time.time()
        preguntar_claude(texto)
        return

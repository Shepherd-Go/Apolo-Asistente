#!/usr/bin/env python3
"""
Apolo - Asistente de voz con escucha continua y memoria de conversación.

- Di "Apolo" para activar el modo conversación.
- Luego habla sin repetir "Apolo".
- Di "para" o "adiós" para salir del modo conversación.
- Di "olvida todo" para limpiar el historial.

Dependencias:
    pip install SpeechRecognition sounddevice numpy anthropic tavily-python python-dotenv

Uso:
    python bienvenido_apolo.py
"""

import os
import sys
import queue
import time
import threading
import subprocess
import webbrowser
from urllib.parse import quote
from youtubesearchpython import VideosSearch
from datetime import datetime
from zoneinfo import ZoneInfo
import numpy as np
import sounddevice as sd
import speech_recognition as sr
import pyttsx3
import anthropic
from dotenv import load_dotenv
from tavily import TavilyClient

load_dotenv()

# ──────────────────────────────────────────────────────────────────────────────
#  Configuración
# ──────────────────────────────────────────────────────────────────────────────
IDIOMA          = "es-ES"
DOTA2_STEAM     = "steam://rungameid/570"

SAMPLE_RATE     = 16000
BLOCK_SIZE      = int(SAMPLE_RATE * 0.1)
VOZ_THRESHOLD   = 0.02
SILENCIO_LIMITE = 8
MAX_BLOQUES     = 60

TIMEOUT_CONV    = 60   # segundos sin hablar antes de salir del modo conversación

ZONA_COLOMBIA   = ZoneInfo("America/Bogota")
claude_client   = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
tavily_client   = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

DIAS_ES = {
    "Monday": "lunes", "Tuesday": "martes", "Wednesday": "miércoles",
    "Thursday": "jueves", "Friday": "viernes", "Saturday": "sábado", "Sunday": "domingo"
}
MESES_ES = {
    1: "enero", 2: "febrero", 3: "marzo", 4: "abril", 5: "mayo", 6: "junio",
    7: "julio", 8: "agosto", 9: "septiembre", 10: "octubre", 11: "noviembre", 12: "diciembre"
}

# Palabras clave
WAKE_WORD        = "apolo"
COMANDO_DOTA     = ["dota"]
COMANDO_HORA     = ["hora", "tiempo", "fecha", "día"]
COMANDO_MUSICA   = ["pon ", "reproduce ", "busca ", "ponme ", "toca "]
COMANDO_PARAR    = ["para", "adiós", "adios", "detente", "stop"]
COMANDO_OLVIDAR  = ["olvida todo", "borra el historial", "limpia el historial", "nueva conversación"]

# ──────────────────────────────────────────────────────────────────────────────
#  Estado global
# ──────────────────────────────────────────────────────────────────────────────
audio_queue: queue.Queue = queue.Queue()
grabando        = False
silencio_cnt    = 0
voz_buffer      = []

modo_conv       = False          # True = modo conversación activo
ultimo_habla    = 0.0            # timestamp del último comando
historial: list = []             # mensajes para Claude


# ──────────────────────────────────────────────────────────────────────────────
#  Callback de audio
# ──────────────────────────────────────────────────────────────────────────────
def audio_callback(indata, frames, time_info, status):
    global grabando, silencio_cnt, voz_buffer

    rms = float(np.sqrt(np.mean(indata.astype(np.float32) ** 2))) / 32768

    if rms > VOZ_THRESHOLD:
        grabando = True
        silencio_cnt = 0
        voz_buffer.append(indata.copy())
    elif grabando:
        voz_buffer.append(indata.copy())
        silencio_cnt += 1
        if silencio_cnt >= SILENCIO_LIMITE or len(voz_buffer) >= MAX_BLOQUES:
            audio_queue.put(np.concatenate(voz_buffer, axis=0))
            voz_buffer = []
            grabando = False
            silencio_cnt = 0


# ──────────────────────────────────────────────────────────────────────────────
#  Utilidades
# ──────────────────────────────────────────────────────────────────────────────
def hablar(texto: str):
    print(f"  🔊  {texto}")
    engine = pyttsx3.init()
    voces = engine.getProperty("voices")
    esp = [v for v in voces if "es" in v.id.lower() or "spanish" in v.name.lower()]
    if esp:
        engine.setProperty("voice", esp[0].id)
    engine.setProperty("rate", 148)
    engine.say(texto)
    engine.runAndWait()


def limpiar_historial():
    global historial
    historial = []
    print("  🗑️  Historial borrado.")
    hablar("Historial borrado. Empezamos de cero.")


def activar_modo_conv():
    global modo_conv, ultimo_habla
    modo_conv = True
    ultimo_habla = time.time()
    print("  💬  Modo conversación activado.")
    hablar("Dime.")


def desactivar_modo_conv():
    global modo_conv
    modo_conv = False
    print("  💤  Modo conversación desactivado.")
    hablar("Hasta luego.")


# ──────────────────────────────────────────────────────────────────────────────
#  Comandos
# ──────────────────────────────────────────────────────────────────────────────
def buscar_musica(texto: str):
    cancion = texto
    for cmd in COMANDO_MUSICA:
        cancion = cancion.replace(cmd, "")
    cancion = cancion.strip()

    if not cancion:
        hablar("¿Qué canción quieres escuchar?")
        return

    print(f"  🎵  Buscando: {cancion}")
    try:
        resultados = VideosSearch(cancion, limit=1).result()
        video_id = resultados["result"][0]["id"]
        url = f"https://www.youtube.com/watch?v={video_id}"
    except Exception:
        url = f"https://www.youtube.com/results?search_query={quote(cancion)}"

    opera = r"C:\Users\ACER\AppData\Local\Programs\Opera\opera.exe"
    subprocess.Popen([
        opera,
        "--new-window",
        "--autoplay-policy=no-user-gesture-required",
        "--disable-features=PreloadMediaEngagementData,MediaEngagementBypassAutoplayPolicies",
        url
    ])

    hablar(f"Poniendo {cancion}.")


def abrir_dota():
    print("  🎮  Abriendo Dota 2…")
    os.startfile(DOTA2_STEAM)


def decir_hora():
    ahora  = datetime.now(ZONA_COLOMBIA)
    dia    = DIAS_ES[ahora.strftime("%A")]
    mes    = MESES_ES[ahora.month]
    hora   = ahora.strftime("%I").lstrip("0")
    minuto = ahora.strftime("%M")
    ampm   = ("de la mañana" if ahora.hour < 12
              else "del mediodía" if ahora.hour == 12
              else "de la tarde" if ahora.hour < 20
              else "de la noche")
    hablar(f"Hoy es {dia} {ahora.day} de {mes} de {ahora.year}. Son las {hora} y {minuto} {ampm}.")


def preguntar_claude(pregunta: str):
    global historial, ultimo_habla

    print("  🔎  Buscando información actualizada…")
    try:
        resultado = tavily_client.search(query=pregunta, max_results=3)
        contexto = "\n".join(r["content"] for r in resultado.get("results", []))
    except Exception:
        contexto = ""

    contenido = f"Pregunta: {pregunta}\n\nInformación reciente de internet:\n{contexto}" if contexto else pregunta

    historial.append({"role": "user", "content": contenido})

    print("  🤖  Consultando a Claude…")
    mensaje = claude_client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=300,
        system=(
            "Eres Apolo, un asistente de voz. "
            "Responde siempre en español, de forma breve y directa (máximo 3 oraciones). "
            "Sin markdown, sin listas, solo texto plano para ser leído en voz alta."
        ),
        messages=historial,
    )
    respuesta = mensaje.content[0].text
    historial.append({"role": "assistant", "content": respuesta})
    ultimo_habla = time.time()
    hablar(respuesta)


# ──────────────────────────────────────────────────────────────────────────────
#  Procesador de comandos
# ──────────────────────────────────────────────────────────────────────────────
def procesar_comando(texto: str):
    global modo_conv, ultimo_habla

    texto_lower = texto.lower()
    print(f"  🗣️  Escuché: «{texto_lower}»")

    tiene_wake = WAKE_WORD in texto_lower

    # ── Comandos que siempre requieren "apolo" ───────────────────────────────
    if tiene_wake and any(p in texto_lower for p in COMANDO_DOTA):
        abrir_dota()
        return

    if tiene_wake and any(p in texto_lower for p in COMANDO_HORA):
        decir_hora()
        return

    if (tiene_wake or modo_conv) and any(p in texto_lower for p in COMANDO_MUSICA):
        query = texto_lower.replace(WAKE_WORD, "").strip()
        buscar_musica(query)
        return

    # ── Salir del modo conversación ───────────────────────────────────────────
    if modo_conv and any(p in texto_lower for p in COMANDO_PARAR):
        desactivar_modo_conv()
        return

    # ── Borrar historial ──────────────────────────────────────────────────────
    if (tiene_wake or modo_conv) and any(p in texto_lower for p in COMANDO_OLVIDAR):
        limpiar_historial()
        return

    # ── Activar modo conversación ─────────────────────────────────────────────
    if tiene_wake and not modo_conv:
        pregunta = texto_lower.replace(WAKE_WORD, "").strip()
        activar_modo_conv()
        if pregunta:
            preguntar_claude(pregunta)
        return

    # ── En modo conversación: responde sin necesitar "apolo" ─────────────────
    if modo_conv:
        ultimo_habla = time.time()
        preguntar_claude(texto)
        return


# ──────────────────────────────────────────────────────────────────────────────
#  Main
# ──────────────────────────────────────────────────────────────────────────────
def main():
    global modo_conv

    print("=" * 50)
    print("  🎤  Apolo escuchando… (Ctrl+C para salir)")
    print("  Di \"Apolo\" para activar el modo conversación.")
    print("=" * 50 + "\n")

    with sd.InputStream(
        samplerate=SAMPLE_RATE,
        blocksize=BLOCK_SIZE,
        channels=1,
        dtype="int16",
        callback=audio_callback,
    ):
        print("  👂  Listo.\n")
        while True:
            try:
                # Timeout automático del modo conversación
                if modo_conv and (time.time() - ultimo_habla) > TIMEOUT_CONV:
                    print("  ⏱️  Timeout de conversación.")
                    desactivar_modo_conv()

                audio_np = audio_queue.get(timeout=0.5)

                print("  ⏳  Procesando…")
                audio = sr.AudioData(audio_np.tobytes(), SAMPLE_RATE, 2)
                texto = recognizer.recognize_google(audio, language=IDIOMA)
                procesar_comando(texto)

            except queue.Empty:
                pass
            except sr.UnknownValueError:
                print("  🔇  No entendí, repite.")
            except sr.RequestError as e:
                print(f"  ⚠️  Error Google Speech: {e}")
            except KeyboardInterrupt:
                print("\n\nHasta luego! 👋")
                sys.exit(0)


if __name__ == "__main__":
    recognizer = sr.Recognizer()
    main()

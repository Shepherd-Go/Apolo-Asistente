#!/usr/bin/env python3
"""
Apolo - Asistente de voz con escucha continua y memoria de conversación.

- Di "Apolo" para activar el modo conversación.
- Luego habla sin repetir "Apolo".
- Di "para" o "adiós" para salir del modo conversación.
- Di "olvida todo" para limpiar el historial.
"""

import sys
import queue
import time
import speech_recognition as sr
import sounddevice as sd

from apolo.config import SAMPLE_RATE, BLOCK_SIZE, TIMEOUT_CONV
from apolo.audio import audio_queue, audio_callback
from apolo.conversation import modo_conv, desactivar_modo_conv
from apolo.processor import procesar_comando
import apolo.conversation as conv


def main():
    recognizer = sr.Recognizer()

    print("=" * 50)
    print("  🎤  Apolo escuchando… (Ctrl+C para salir)")
    print('  Di "Apolo" para activar el modo conversación.')
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
                if conv.modo_conv and (time.time() - conv.ultimo_habla) > TIMEOUT_CONV:
                    print("  ⏱️  Timeout de conversación.")
                    desactivar_modo_conv()

                audio_np = audio_queue.get(timeout=0.5)

                print("  ⏳  Procesando…")
                audio = sr.AudioData(audio_np.tobytes(), SAMPLE_RATE, 2)
                texto = recognizer.recognize_google(audio, language="es-ES")
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
    main()

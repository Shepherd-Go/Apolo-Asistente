# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Ejecutar el proyecto

```bash
python main.py
```

Para inicio automático en Windows: copiar `iniciar_apolo.bat` a la carpeta de inicio (`shell:startup`).

## Dependencias

```bash
pip install -r requirements.txt
```

El proyecto no tiene test suite ni linter configurado.

## Variables de entorno

Archivo `.env` requerido en la raíz:
```
ANTHROPIC_API_KEY=...
TAVILY_API_KEY=...
GOOGLE_CLIENT_ID=...       # solo si se usa Google Calendar
GOOGLE_CLIENT_SECRET=...   # solo si se usa Google Calendar
```

Zona horaria configurable en `config_usuario.json` (raíz del proyecto). Memoria persistente del usuario en `memoria_usuario.json`.

## Arquitectura

Apolo es un asistente de voz con escucha continua. El flujo principal es:

```
main.py → audio_callback (micrófono) → cola de audio → Google Speech-to-Text → processor.py → feature/commands.py
```

**`main.py`** — bucle principal: captura audio con `sounddevice`, transcribe con `SpeechRecognition` (Google), llama a `procesar_comando`.

**`apolo/config.py`** — fuente única de constantes: palabras clave de activación, comandos por feature, clientes de API (Anthropic, Tavily), zona horaria, parámetros de audio.

**`apolo/processor.py`** — router de comandos: recibe el texto transcrito, lo compara contra las listas de keywords de `config.py` y delega al módulo de feature correspondiente.

**`apolo/audio.py`** — callback de `sounddevice`: detecta voz por RMS, acumula bloques y empuja el audio a `audio_queue` cuando hay silencio.

**`apolo/tts.py`** — síntesis de voz con `pyttsx3`. Función única `hablar(texto)`.

### Paquetes de features

Cada feature es un subpaquete con `commands.py` como punto de entrada:

| Paquete | Responsabilidad |
|---|---|
| `apolo/conversacion/` | `chat.py`: historial, modo conversación, llamadas a Claude + Tavily. `memoria.py`: extrae y persiste preferencias del usuario al final de cada conversación. |
| `apolo/calendario/` | `auth.py`: OAuth2 con Google Calendar. `ops.py`: operaciones CRUD sobre la API. `commands.py`: lógica de voz para agendar y consultar eventos. |
| `apolo/musica/` | Búsqueda en YouTube con `yt-dlp` y reproducción en VLC. Mantiene referencia al proceso VLC activo para reemplazar canciones sin abrir instancias múltiples. |
| `apolo/apps/` | Apertura dinámica de aplicaciones buscando en el Menú Inicio y PATH. |
| `apolo/sistema/` | Comandos del sistema operativo (hora, fecha). |

### Modo conversación

`conv.modo_conv` (bool global en `apolo/conversacion/chat.py`) controla si Apolo responde sin necesitar la wake word "Apolo". Se activa al decir "Apolo" y se desactiva por timeout (`TIMEOUT_CONV` segundos de silencio) o al decir "para"/"adiós". Al desactivarse, `extraer_y_guardar()` analiza el historial con Claude y persiste preferencias nuevas.

## Flujo de ramas

```
feat/* → dev → main
```

- PRs de features siempre apuntan a `dev`, nunca a `main`.
- El CI (`enforce-branching.yml`) cierra automáticamente PRs que violen esta regla.
- Releases se generan desde `main` con `.github/scripts/generar_release.py`.

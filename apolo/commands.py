import os
import shutil
import subprocess
from pathlib import Path
from urllib.parse import quote
from datetime import datetime
from youtubesearchpython import VideosSearch

from apolo.config import DOTA2_STEAM, ZONA_USUARIO, DIAS_ES, MESES_ES, COMANDO_MUSICA, COMANDO_ABRIR
from apolo.tts import hablar


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
        url,
    ])

    hablar(f"Poniendo {cancion}.")


def buscar_y_abrir_app(nombre: str):
    nombre_lower = nombre.lower().strip()
    if not nombre_lower:
        hablar("¿Qué aplicación quieres abrir?")
        return

    start_menu_dirs = [
        Path(os.environ.get("ProgramData", r"C:\ProgramData")) / "Microsoft/Windows/Start Menu/Programs",
        Path(os.environ.get("APPDATA", "")) / "Microsoft/Windows/Start Menu/Programs",
    ]

    for start_dir in start_menu_dirs:
        if not start_dir.exists():
            continue
        for lnk in start_dir.rglob("*.lnk"):
            if nombre_lower in lnk.stem.lower():
                print(f"  🖥️  Abriendo {lnk.stem}.")
                subprocess.Popen(
                    ["cmd", "/c", "start", "", str(lnk)],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    stdin=subprocess.DEVNULL,
                )
                hablar(f"Abriendo {lnk.stem}.")
                return

    exe = shutil.which(nombre_lower) or shutil.which(nombre_lower + ".exe")
    if exe:
        print(f"  🖥️  Abriendo desde PATH: {exe}")
        subprocess.Popen([exe], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        hablar(f"Abriendo {nombre}.")
        return

    hablar(f"No encontré {nombre} en tu ordenador.")


def abrir_dota():
    print("  🎮  Abriendo Dota 2…")
    os.startfile(DOTA2_STEAM)


def decir_hora():
    ahora  = datetime.now(ZONA_USUARIO)
    dia    = DIAS_ES[ahora.strftime("%A")]
    mes    = MESES_ES[ahora.month]
    hora   = ahora.strftime("%I").lstrip("0")
    minuto = ahora.strftime("%M")
    ampm   = (
        "de la mañana" if ahora.hour < 12
        else "del mediodía" if ahora.hour == 12
        else "de la tarde" if ahora.hour < 20
        else "de la noche"
    )
    hablar(f"Hoy es {dia} {ahora.day} de {mes} de {ahora.year}. Son las {hora} y {minuto} {ampm}.")

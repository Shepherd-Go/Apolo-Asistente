import os
import shutil
import subprocess
from pathlib import Path
from apolo.config import DOTA2_STEAM
from apolo.tts import hablar


def buscar_y_abrir_app(nombre: str):
    nombre_lower = nombre.lower().strip()
    if not nombre_lower:
        hablar("¿Qué aplicación quieres abrir?")
        return

    start_menu_dirs = [
        Path(os.environ.get("ProgramData", r"C:\ProgramData"))
        / "Microsoft/Windows/Start Menu/Programs",
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

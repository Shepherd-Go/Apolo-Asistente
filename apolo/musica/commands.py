import subprocess
import yt_dlp
from apolo.config import COMANDO_MUSICA
from apolo.tts import hablar

_vlc_proceso = None


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
        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "format": "bestaudio/best",
            "noplaylist": True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch1:{cancion}", download=False)
            entry = info["entries"][0]
            url = entry["url"]
    except Exception as e:
        print(f"  ❌  yt-dlp falló: {e}")
        hablar(f"No encontré {cancion} en YouTube.")
        return

    global _vlc_proceso
    if _vlc_proceso is not None and _vlc_proceso.poll() is None:
        _vlc_proceso.terminate()
        _vlc_proceso = None

    print(f"  🎵  Reproduciendo en VLC: {url[:80]}...")
    vlc = r"C:\Program Files\VideoLAN\VLC\vlc.exe"
    _vlc_proceso = subprocess.Popen(
        [vlc, url],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        stdin=subprocess.DEVNULL,
    )

    hablar(f"Poniendo {cancion}.")

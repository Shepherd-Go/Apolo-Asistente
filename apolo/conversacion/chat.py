import time
from apolo.config import claude_client, tavily_client
from apolo.tts import hablar
from apolo.conversacion.memoria import memoria_como_texto, extraer_y_guardar

historial: list = []
modo_conv: bool = False
ultimo_habla: float = 0.0


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
    global modo_conv, historial
    extraer_y_guardar(historial)
    modo_conv = False
    print("  💤  Modo conversación desactivado.")
    hablar("Hasta luego.")


def preguntar_claude(pregunta: str):
    global historial, ultimo_habla

    print("  🔎  Consultando Tavily…")
    try:
        resultado = tavily_client.search(query=pregunta, max_results=3)
        resultados = resultado.get("results", [])
        contexto = "\n".join(r["content"] for r in resultados)
        if resultados:
            print(f"  ✅  Tavily: {len(resultados)} resultado(s) encontrado(s).")
        else:
            print("  ⚠️  Tavily: sin resultados.")
    except Exception as e:
        print(f"  ❌  Tavily falló: {e}")
        contexto = ""

    contenido = (
        f"Pregunta: {pregunta}\n\nInformación reciente de internet:\n{contexto}"
        if contexto
        else pregunta
    )

    historial.append({"role": "user", "content": contenido})

    print("  🤖  Consultando a Claude…")
    mensaje = claude_client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=300,
        system=(
            "Eres Apolo, un asistente de voz. "
            "Responde siempre en español, de forma breve y directa (máximo 3 oraciones). "
            "Sin markdown, sin listas, solo texto plano para ser leído en voz alta. "
            + memoria_como_texto()
        ),
        messages=historial,
    )
    respuesta = mensaje.content[0].text
    historial.append({"role": "assistant", "content": respuesta})
    hablar(respuesta)
    ultimo_habla = time.time()

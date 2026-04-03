import pyttsx3


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

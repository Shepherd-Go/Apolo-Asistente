#!/usr/bin/env python3
"""
Calcula la siguiente versión semántica y genera release notes en español
usando Claude a partir de los commits desde el último tag.
"""

import os
import subprocess
import anthropic

# ── Obtener último tag ────────────────────────────────────────────────────────
def ultimo_tag():
    result = subprocess.run(
        ["git", "tag", "--sort=-version:refname"],
        capture_output=True, text=True
    )
    tags = result.stdout.strip().splitlines()
    return tags[0] if tags else None


def commits_desde(tag: str | None) -> list[str]:
    rango = f"{tag}..HEAD" if tag else "HEAD"
    result = subprocess.run(
        ["git", "log", rango, "--pretty=format:%s"],
        capture_output=True, text=True
    )
    return [c.strip() for c in result.stdout.strip().splitlines() if c.strip()]


# ── Calcular bump de versión ──────────────────────────────────────────────────
def calcular_version(tag_actual: str | None, commits: list[str]) -> str:
    if not tag_actual:
        return "v1.0.0"

    version = tag_actual.lstrip("v")
    partes = version.split(".")
    major, minor, patch = int(partes[0]), int(partes[1]), int(partes[2])

    mensajes = " ".join(commits).lower()

    if "breaking change" in mensajes:
        return f"v{major + 1}.0.0"
    elif any(c.startswith("feat") for c in commits):
        return f"v{major}.{minor + 1}.0"
    else:
        return f"v{major}.{minor}.{patch + 1}"


# ── Generar notas con Claude ──────────────────────────────────────────────────
def generar_notas(version: str, commits: list[str]) -> str:
    if not commits:
        return "Mejoras y correcciones internas."

    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    commits_texto = "\n".join(f"- {c}" for c in commits)

    mensaje = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=500,
        system=(
            "Eres un asistente que genera release notes para GitHub en español. "
            "Dado un listado de commits, genera notas de release claras y organizadas. "
            "Agrupa los cambios en secciones: '### Nuevas funciones', '### Correcciones', "
            "'### Mejoras'. Usa viñetas con '-'. Solo incluye secciones que tengan contenido. "
            "Sin introducciones ni conclusiones, solo las secciones."
        ),
        messages=[{
            "role": "user",
            "content": f"Versión: {version}\n\nCommits:\n{commits_texto}"
        }]
    )

    return mensaje.content[0].text.strip()


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    tag_actual = ultimo_tag()
    commits    = commits_desde(tag_actual)
    nueva_ver  = calcular_version(tag_actual, commits)
    notas      = generar_notas(nueva_ver, commits)
    nombre     = f"Apolo {nueva_ver}"

    # Escapar saltos de línea para GitHub Actions output
    notas_escaped = notas.replace("\n", "\\n").replace("\r", "")

    output_file = os.environ.get("GITHUB_OUTPUT", "")
    if output_file:
        with open(output_file, "a") as f:
            f.write(f"tag={nueva_ver}\n")
            f.write(f"nombre={nombre}\n")
            f.write(f"notas={notas_escaped}\n")
    else:
        print(f"tag={nueva_ver}")
        print(f"nombre={nombre}")
        print(f"notas={notas}")


if __name__ == "__main__":
    main()

# Apolo - Asistente de voz

Asistente de voz en español con IA. Di "Apolo" y hazle cualquier pregunta.

## Requisitos

- Windows 10/11
- Python 3.9+
- Micrófono
- Cuenta en [Anthropic](https://console.anthropic.com) (Claude API)
- Cuenta en [Tavily](https://tavily.com) (búsquedas en internet)

## Instalación

**1. Clona el repositorio**
```bash
git clone <url-del-repo>
cd jarvis
```

**2. Instala las dependencias**
```bash
pip install -r requirements.txt
```

**3. Crea el archivo `.env`** con tus API keys
```
ANTHROPIC_API_KEY=sk-ant-tu-key-aquí
TAVILY_API_KEY=tvly-tu-key-aquí
```

**4. Corre Apolo**
```bash
python apolo-asistente.py
```

## Comandos de voz

| Di esto | Resultado |
|---|---|
| "Apolo" | Activa el modo conversación |
| "Apolo abre el Dota" | Abre Dota 2 via Steam |
| "Apolo qué hora es" | Dice el día, fecha y hora (Colombia) |
| "Apolo pon X canción" | Busca y abre la canción en YouTube |
| Cualquier pregunta | Busca en internet y responde con IA |
| "para" / "adiós" | Sale del modo conversación |
| "olvida todo" | Borra el historial de la conversación |

## Configuración de zona horaria

Edita `config_usuario.json` en la raíz del proyecto:

```json
{
  "zona_horaria": "America/Bogota"
}
```

### Zonas horarias de Latinoamérica

| País | Zona horaria |
|---|---|
| Argentina | `America/Argentina/Buenos_Aires` |
| Bolivia | `America/La_Paz` |
| Brasil (Brasilia) | `America/Sao_Paulo` |
| Brasil (Manaos) | `America/Manaus` |
| Chile | `America/Santiago` |
| Colombia | `America/Bogota` |
| Costa Rica | `America/Costa_Rica` |
| Cuba | `America/Havana` |
| Ecuador | `America/Guayaquil` |
| El Salvador | `America/El_Salvador` |
| Guatemala | `America/Guatemala` |
| Honduras | `America/Tegucigalpa` |
| México (Ciudad de México) | `America/Mexico_City` |
| México (Cancún) | `America/Cancun` |
| México (Tijuana) | `America/Tijuana` |
| Nicaragua | `America/Managua` |
| Panamá | `America/Panama` |
| Paraguay | `America/Asuncion` |
| Perú | `America/Lima` |
| Puerto Rico | `America/Puerto_Rico` |
| República Dominicana | `America/Santo_Domingo` |
| Uruguay | `America/Montevideo` |
| Venezuela | `America/Caracas` |

## Flujo de contribución

```
feat/mi-rama  →  dev  →  main
```

1. Crea tu rama desde `dev`: `git checkout -b feat/mi-feature`
2. Haz tus cambios y push
3. Abre un PR apuntando a `dev`
4. El dueño del repo aprueba y mergea
5. Cuando `dev` esté listo, se abre un PR de `dev` → `main`

> ⚠️ No se aceptan PRs de ramas feature directamente a `main`.

## Inicio automático con Windows

1. Presiona **Win + R** → escribe `shell:startup` → Enter
2. Copia `iniciar_jarvis.bat` a esa carpeta

## Ajuste del micrófono

Si Apolo no te escucha:
- Ve a **Panel de control → Sonido → Grabación → Micrófono → Propiedades → Mejoras**
- Marca **"Deshabilitar todos los efectos de sonido"**
- Ajusta `VOZ_THRESHOLD` en el script si sigue fallando (bajar = más sensible)

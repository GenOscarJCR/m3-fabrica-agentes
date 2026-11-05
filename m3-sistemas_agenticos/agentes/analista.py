"""Sesión 1 · Agente 1, analista: historia de usuario -> criterios de aceptación en Gherkin.

Uso:  python -m agentes.analista historias/HU-01-registrar-empleado.md
"""
import re
import sys
from pathlib import Path

from agentes.base import RAIZ, SALIDA, ejecutar_agente, herramientas_archivos, hu_de, rel

SISTEMA = """Eres analista de producto en un equipo de software. Conviertes historias de usuario
en criterios de aceptación escritos en Gherkin, en español.

Cómo trabajas:
1. Lee la historia, contexto/reglas_negocio.md, contexto/convenciones_app.md y todo archivo de
   contexto/ que la historia cite.
2. Escribe {destino}. La primera línea es `# language: es` y usas las palabras clave
   Característica, Escenario, Dado, Cuando, Entonces, Y.
3. Incluye el camino feliz y un escenario de error por cada regla de negocio que aplique a ESTA historia.
4. Si el contexto define una tabla de errores, escribe un escenario por cada fila, con el código HTTP y el
   mensaje copiados LETRA POR LETRA (acentos y puntuación incluidos). Donde el mensaje tenga una N, pon el número concreto.
5. Para cada regla con un límite, incluye un escenario justo en el límite (se acepta) y otro que lo
   rebase por uno (se rechaza).
6. Cubre cada endpoint de la API que definan esos archivos, incluidas las consultas y no solo las altas.
   En el «Cuando» escribe el método y la ruta concreta, por ejemplo `GET /api/empleados/7/vacaciones?anio=2026`.
7. Cada escenario se puede verificar desde la pantalla o la API: datos concretos, nada de «funciona bien».
8. No inventes reglas. Si falta información, agrégala al final como comentarios bajo `# Preguntas abiertas`.
9. Responde al final con una sola línea: cuántos escenarios escribiste."""


def escenarios(gherkin: str) -> list[str]:
    return re.findall(r"^\s*Escenario:\s*(.+?)\s*$", gherkin, flags=re.MULTILINE)


def preguntas_abiertas(gherkin: str) -> list[str]:
    if "# Preguntas abiertas" not in gherkin:
        return []
    bloque = gherkin.split("# Preguntas abiertas", 1)[1]
    return [l.lstrip("# -").strip() for l in bloque.splitlines() if l.strip().lstrip("#").strip()]

def mensajes_requeridos(historia_texto: str) -> list[str]:
    """Mensajes exactos que exige la historia: las filas 4xx de las tablas de errores
    de los archivos de contexto que la historia cita."""
    mensajes = []
    for ruta in sorted(set(re.findall(r"contexto/[\w\-]+\.md", historia_texto))):
        archivo = RAIZ / ruta
        if archivo.exists():
            for fila in archivo.read_text(encoding="utf-8").splitlines():
                m = re.match(r"^\|.*\|\s*4\d\d\s*\|\s*`([^`]+)`\s*\|\s*$", fila)
                if m:
                    mensajes.append(m.group(1))
    return mensajes

def rutas_requeridas(historia_texto: str) -> list[str]:
    """Endpoints que exige la historia: los `MÉTODO /api/...` de los archivos de contexto que cita."""
    rutas = []
    for ruta in sorted(set(re.findall(r"contexto/[\w\-]+\.md", historia_texto))):
        archivo = RAIZ / ruta
        if archivo.exists():
            rutas += re.findall(r"`((?:GET|POST|PUT|PATCH|DELETE) /api/[^`?\s]+)",
                                archivo.read_text(encoding="utf-8"))
    return sorted(set(rutas))

def validar_gherkin(texto: str, mensajes: list[str] = (), rutas: list[str] = ()) -> list[str]:
    """Evaluador determinista: devuelve los problemas encontrados; vacío = válido."""
    problemas = []
    if not texto.lstrip().startswith("# language: es"):
        problemas.append("La primera línea debe ser '# language: es'.")
    if "Característica:" not in texto:
        problemas.append("Falta 'Característica:'.")
    bloques = re.split(r"^\s*Escenario:", texto, flags=re.MULTILINE)[1:]
    if len(bloques) < 2:
        problemas.append("Se esperan al menos 2 escenarios (camino feliz y un error).")
    for i, bloque in enumerate(bloques, 1):
        for clave in ("Dado", "Cuando", "Entonces"):
            if not re.search(rf"^\s*{clave}\b", bloque, flags=re.MULTILINE):
                problemas.append(f"El escenario {i} no tiene '{clave}'.")
    for m in mensajes:   # la N del mensaje acepta cualquier número
        if not re.search(re.sub(r"\bN\b", r"\\d+", re.escape(m)), texto):
            problemas.append(f"Falta un escenario con el mensaje exacto: «{m}».")
    for r in rutas:   # {empleado_id} acepta un id concreto
        patron = re.sub(r"\\\{[^}]*\\\}", lambda _: r"[^/\s?]+", re.escape(r))
        if not re.search(patron, texto):
            problemas.append(f"Falta un escenario que use la ruta {r} con un id concreto.")
    return problemas


def generar_criterios(historia: Path, max_intentos: int = 2) -> Path:
    carpeta = SALIDA / hu_de(historia)
    destino = carpeta / "criterios.feature"
    herramientas = herramientas_archivos(lectura=[RAIZ / "historias", RAIZ / "contexto"], escritura=carpeta)
    tarea = f"Historia de usuario: {rel(historia)}"
    mensajes = mensajes_requeridos(historia.read_text(encoding="utf-8"))
    rutas = rutas_requeridas(historia.read_text(encoding="utf-8"))
    for intento in range(1, max_intentos + 1):
        print(f"Analista · intento {intento}")
        ejecutar_agente(SISTEMA.format(destino=rel(destino)), herramientas, tarea, nombre="analista")
        problemas = validar_gherkin(destino.read_text(encoding="utf-8"), mensajes, rutas) if destino.exists() \
            else [f"No se escribió {rel(destino)}."]
        if not problemas:
            return destino
        # Reflexión guiada por un evaluador determinista: el agente recibe los problemas y corrige
        tarea += "\n\nTu versión anterior tiene estos problemas; corrígelos:\n- " + "\n- ".join(problemas)
    raise ValueError("Criterios inválidos tras varios intentos:\n- " + "\n- ".join(problemas))


if __name__ == "__main__":
    ruta = generar_criterios(Path(sys.argv[1]).resolve())
    texto = ruta.read_text(encoding="utf-8")
    print(f"\nListo: {rel(ruta)} · {len(escenarios(texto))} escenarios")
    for p in preguntas_abiertas(texto):
        print("  Pregunta abierta:", p)

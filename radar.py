"""
Radar de ayudas I+D+i y digitalización para pymes.

Punto de entrada principal. Desde aquí el usuario:
  1) Define o selecciona el perfil de su empresa (modo interactivo o por JSON).
  2) Lanza la búsqueda de convocatorias en CDTI, Horizonte Europa, ENISA, etc.
  3) Busca noticias de digitalización.
  4) Guarda un CSV con los resultados.
  5) Genera un HTML visual en docs/index.html (listo para GitHub Pages).

Uso:
    python radar.py                 # modo interactivo (cuestionario)
    python radar.py --perfil demo   # usa un perfil de demostración
    python radar.py --perfil ruta/miempresa.json
"""

from __future__ import annotations

import argparse
import csv
import json
from dataclasses import asdict
from pathlib import Path
from typing import List

from config import (
    PerfilEmpresa,
    OPCIONES_SECTOR,
    OPCIONES_TAMANO,
    OPCIONES_AMBITO,
    OPCIONES_INTERESES,
)
from fuentes import (
    Resultado,
    buscar_convocatorias,
    buscar_noticias_digitalizacion,
    resultado_a_dict,
)
from html_render import generar_html


# ---------------------------------------------------------------------------
# Rutas
# ---------------------------------------------------------------------------
RAIZ = Path(__file__).parent
RUTA_CSV = RAIZ / "datos" / "resultados.csv"
RUTA_HTML = RAIZ / "docs" / "index.html"
RUTA_PERFIL = RAIZ / "datos" / "perfil_empresa.json"


# ---------------------------------------------------------------------------
# Perfil de la empresa
# ---------------------------------------------------------------------------

def _preguntar_opcion(titulo: str, opciones: List[str], por_defecto: str) -> str:
    """Pregunta al usuario una opción de una lista numerada."""
    print(f"\n{titulo}")
    for i, opc in enumerate(opciones, 1):
        print(f"  {i}. {opc}")
    seleccion = input(f"Elige número (Enter = {por_defecto}): ").strip()
    if not seleccion:
        return por_defecto
    try:
        return opciones[int(seleccion) - 1]
    except (ValueError, IndexError):
        print(f"  (valor no válido, uso {por_defecto})")
        return por_defecto


def _preguntar_multi(titulo: str, opciones: List[str]) -> List[str]:
    """Permite elegir varias opciones separadas por coma."""
    print(f"\n{titulo}")
    for i, opc in enumerate(opciones, 1):
        print(f"  {i}. {opc}")
    seleccion = input("Elige varios números separados por coma (Enter = ninguno): ").strip()
    if not seleccion:
        return []
    elegidos: List[str] = []
    for parte in seleccion.split(","):
        try:
            elegidos.append(opciones[int(parte.strip()) - 1])
        except (ValueError, IndexError):
            continue
    return elegidos


def cuestionario_empresa() -> PerfilEmpresa:
    """Lanza el cuestionario interactivo y devuelve el perfil."""
    print("=" * 60)
    print("  Definamos el perfil de tu empresa")
    print("=" * 60)
    nombre = input("Nombre de la empresa (Enter = Mi Empresa): ").strip() or "Mi Empresa"
    sector = _preguntar_opcion("Sector principal:", OPCIONES_SECTOR, "general")
    tamano = _preguntar_opcion("Tamaño:", OPCIONES_TAMANO, "pyme")
    ambito = _preguntar_opcion("Ámbito de actuación:", OPCIONES_AMBITO, "nacional")
    intereses = _preguntar_multi("Intereses / líneas de I+D:", OPCIONES_INTERESES)

    perfil = PerfilEmpresa(
        nombre=nombre, sector=sector, tamano=tamano,
        ambito=ambito, intereses=intereses,
    )

    # Guardamos para que la próxima vez se pueda reutilizar.
    RUTA_PERFIL.parent.mkdir(parents=True, exist_ok=True)
    RUTA_PERFIL.write_text(
        json.dumps(asdict(perfil), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"\n✅ Perfil guardado en {RUTA_PERFIL}")
    return perfil


def cargar_perfil(origen: str) -> PerfilEmpresa:
    """Carga un perfil desde un archivo JSON o usa uno de demo."""
    if origen == "demo":
        return PerfilEmpresa(
            nombre="Pyme Demo SL",
            sector="software",
            tamano="pyme",
            ambito="nacional",
            intereses=["digitalización", "inteligencia artificial", "ciberseguridad"],
        )
    ruta = Path(origen)
    if not ruta.exists():
        raise FileNotFoundError(f"No existe el perfil: {ruta}")
    datos = json.loads(ruta.read_text(encoding="utf-8"))
    return PerfilEmpresa(**datos)


# ---------------------------------------------------------------------------
# Persistencia: CSV
# ---------------------------------------------------------------------------

def guardar_csv(resultados: List[Resultado], ruta: Path) -> Path:
    """Escribe un CSV con las columnas pedidas: título, fuente, fecha, URL, resumen.
    Incluye también categoría y puntuación para análisis posterior."""
    ruta.parent.mkdir(parents=True, exist_ok=True)
    campos = ["titulo", "fuente", "fecha", "url", "resumen", "categoria", "centro_id", "puntuacion"]
    with ruta.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=campos)
        writer.writeheader()
        for r in resultados:
            writer.writerow(resultado_a_dict(r))
    return ruta


# ---------------------------------------------------------------------------
# Orquestador
# ---------------------------------------------------------------------------

def ejecutar_flujo_completo(perfil: PerfilEmpresa | None = None) -> dict:
    """Flujo completo: buscar → guardar CSV → generar HTML.

    Devuelve un dict con rutas generadas, útil para scripts externos
    (p. ej. el email scheduler)."""
    # Si no se pasa perfil, intentamos cargar el guardado o usamos demo.
    if perfil is None:
        if RUTA_PERFIL.exists():
            perfil = cargar_perfil(str(RUTA_PERFIL))
            print(f"📂 Perfil cargado: {perfil.nombre}")
        else:
            perfil = cargar_perfil("demo")
            print("⚠️  Sin perfil configurado, uso el perfil DEMO.")

    print("\n🔎 Buscando convocatorias...")
    convocatorias = buscar_convocatorias(perfil)
    print(f"   → {len(convocatorias)} resultados")

    print("\n🗞️  Buscando noticias...")
    noticias = buscar_noticias_digitalizacion(perfil)
    print(f"   → {len(noticias)} resultados")

    todos = convocatorias + noticias

    print(f"\n💾 Guardando CSV en {RUTA_CSV}")
    guardar_csv(todos, RUTA_CSV)

    print(f"🎨 Generando HTML en {RUTA_HTML}")
    generar_html(perfil, todos, RUTA_HTML)

    print("\n✨ Listo. Abre docs/index.html en tu navegador o publícalo en GitHub Pages.")
    return {"csv": RUTA_CSV, "html": RUTA_HTML, "total": len(todos)}


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Radar de ayudas I+D+i para pymes.")
    parser.add_argument(
        "--perfil",
        help="Ruta a un JSON de perfil o 'demo'. Si se omite, se lanza el cuestionario.",
    )
    args = parser.parse_args()

    if args.perfil:
        perfil = cargar_perfil(args.perfil)
    else:
        # Si ya hay perfil guardado, pregunta si reutilizarlo.
        if RUTA_PERFIL.exists():
            reutilizar = input(
                f"Se encontró un perfil previo en {RUTA_PERFIL.name}. ¿Reutilizarlo? [S/n]: "
            ).strip().lower()
            if reutilizar in ("", "s", "si", "sí", "y", "yes"):
                perfil = cargar_perfil(str(RUTA_PERFIL))
            else:
                perfil = cuestionario_empresa()
        else:
            perfil = cuestionario_empresa()

    ejecutar_flujo_completo(perfil)


if __name__ == "__main__":
    main()

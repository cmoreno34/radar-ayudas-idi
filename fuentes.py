"""
Módulo de obtención de convocatorias y noticias.

Usamos Google News RSS como agregador universal: es público, estable y
permite filtrar por consulta y por sitio. Esto evita tener que mantener
un scraper a medida para cada organismo (muchos cambian de HTML con
frecuencia) y hace que el sistema funcione sin API keys.

Para cada consulta obtenemos un feed RSS → lo parseamos con feedparser →
extraemos título, enlace, fecha y resumen. BeautifulSoup se usa para
limpiar el HTML del resumen.
"""

from __future__ import annotations

import time
import urllib.parse
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import List

import feedparser
import requests
from bs4 import BeautifulSoup

from config import (
    CENTROS,
    CONSULTAS_NOTICIAS_DIGITALIZACION,
    PerfilEmpresa,
)


# URL base del RSS de Google News. hl=es y gl=ES fuerzan resultados en español.
GOOGLE_NEWS_RSS = (
    "https://news.google.com/rss/search?q={query}&hl=es&gl=ES&ceid=ES:es"
)

# Cabecera "de navegador" para evitar bloqueos básicos.
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"
)


@dataclass
class Resultado:
    """Estructura homogénea para cualquier convocatoria o noticia."""
    titulo: str
    fuente: str            # nombre del centro o "Noticias digitalización"
    fecha: str             # ISO-8601 (YYYY-MM-DD) o cadena vacía
    url: str
    resumen: str
    categoria: str         # "convocatoria" | "noticia"
    centro_id: str = ""    # id del centro (si aplica)
    puntuacion: float = 0.0  # relevancia según perfil de empresa


# ---------------------------------------------------------------------------
# Funciones auxiliares
# ---------------------------------------------------------------------------

def _limpiar_html(texto: str) -> str:
    """Quita etiquetas HTML del resumen que a veces devuelve Google News."""
    if not texto:
        return ""
    sopa = BeautifulSoup(texto, "lxml")
    return sopa.get_text(separator=" ", strip=True)


def _descargar_feed(url: str, timeout: int = 15) -> feedparser.FeedParserDict:
    """Descarga un feed RSS usando requests (para respetar el User-Agent)
    y lo pasa a feedparser. Si falla, devuelve un feed vacío."""
    try:
        r = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=timeout)
        r.raise_for_status()
        return feedparser.parse(r.content)
    except Exception as exc:  # noqa: BLE001  (queremos capturar cualquier fallo)
        print(f"  [aviso] fallo al descargar {url}: {exc}")
        return feedparser.parse(b"")


def _fecha_iso(entry) -> str:
    """Convierte la fecha publicada de feedparser a ISO YYYY-MM-DD."""
    try:
        t = entry.get("published_parsed") or entry.get("updated_parsed")
        if t:
            return datetime(*t[:6]).strftime("%Y-%m-%d")
    except Exception:  # noqa: BLE001
        pass
    return ""


def _puntuar(texto: str, palabras_clave: List[str]) -> float:
    """Puntuación simple por coincidencia de palabras clave del perfil."""
    if not palabras_clave:
        return 0.0
    texto_l = texto.lower()
    puntos = 0.0
    for kw in palabras_clave:
        if kw and kw.lower() in texto_l:
            puntos += 1.0
    # Bonus por menciones múltiples: normalizamos para no saturar.
    return round(puntos, 2)


# ---------------------------------------------------------------------------
# Funciones públicas
# ---------------------------------------------------------------------------

def buscar_convocatorias(perfil: PerfilEmpresa, max_por_consulta: int = 8) -> List[Resultado]:
    """Recorre todos los CENTROS configurados y devuelve convocatorias.

    Para cada centro se lanzan sus "consultas" al RSS de Google News y se
    acumulan los resultados únicos (deduplicados por URL)."""
    vistos: set[str] = set()
    resultados: List[Resultado] = []
    palabras = perfil.palabras_clave()

    for centro in CENTROS:
        print(f"[CONVOCATORIAS] {centro['nombre']}")
        for consulta in centro["consultas"]:
            url = GOOGLE_NEWS_RSS.format(query=urllib.parse.quote(consulta))
            feed = _descargar_feed(url)
            for entry in feed.entries[:max_por_consulta]:
                link = entry.get("link", "")
                if not link or link in vistos:
                    continue
                vistos.add(link)
                titulo = entry.get("title", "").strip()
                resumen = _limpiar_html(entry.get("summary", ""))
                texto_completo = f"{titulo} {resumen}"
                resultados.append(
                    Resultado(
                        titulo=titulo,
                        fuente=centro["nombre"],
                        fecha=_fecha_iso(entry),
                        url=link,
                        resumen=resumen[:400],
                        categoria="convocatoria",
                        centro_id=centro["id"],
                        puntuacion=_puntuar(texto_completo, palabras),
                    )
                )
            # Pequeña pausa para ser amables con el servicio.
            time.sleep(0.4)
    return resultados


def buscar_noticias_digitalizacion(perfil: PerfilEmpresa, max_por_consulta: int = 6) -> List[Resultado]:
    """Busca noticias generales sobre digitalización de pymes en España."""
    vistos: set[str] = set()
    resultados: List[Resultado] = []
    palabras = perfil.palabras_clave()

    for consulta in CONSULTAS_NOTICIAS_DIGITALIZACION:
        print(f"[NOTICIAS] {consulta}")
        url = GOOGLE_NEWS_RSS.format(query=urllib.parse.quote(consulta))
        feed = _descargar_feed(url)
        for entry in feed.entries[:max_por_consulta]:
            link = entry.get("link", "")
            if not link or link in vistos:
                continue
            vistos.add(link)
            titulo = entry.get("title", "").strip()
            resumen = _limpiar_html(entry.get("summary", ""))
            texto_completo = f"{titulo} {resumen}"
            resultados.append(
                Resultado(
                    titulo=titulo,
                    fuente="Noticias digitalización",
                    fecha=_fecha_iso(entry),
                    url=link,
                    resumen=resumen[:400],
                    categoria="noticia",
                    puntuacion=_puntuar(texto_completo, palabras),
                )
            )
        time.sleep(0.4)
    return resultados


def resultado_a_dict(r: Resultado) -> dict:
    """Helper para volcar a CSV/JSON."""
    return asdict(r)

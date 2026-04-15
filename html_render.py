"""
Genera un resumen HTML visual y bonito con los mejores resultados.

Usa Jinja2 + una plantilla embebida para producir un único archivo HTML
auto-contenido (CSS inline). El archivo se puede:
  - abrir localmente en el navegador
  - adjuntar/incrustar en un email
  - publicar en GitHub Pages (docs/index.html)
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import List

from jinja2 import Template

from fuentes import Resultado
from config import PerfilEmpresa


# Plantilla HTML con diseño moderno en un único archivo.
_PLANTILLA = Template(r"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<title>Radar I+D+i — {{ perfil.nombre }}</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
  :root{
    --azul:#0b3d91; --azul2:#1e6ed9; --gris:#f4f6fb;
    --oscuro:#111827; --borde:#e5e7eb; --acento:#f59e0b;
  }
  *{box-sizing:border-box}
  body{margin:0;font-family:-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;
       color:var(--oscuro);background:var(--gris);line-height:1.5}
  header{background:linear-gradient(135deg,var(--azul),var(--azul2));color:#fff;
         padding:32px 24px;box-shadow:0 2px 8px rgba(0,0,0,.1)}
  header h1{margin:0;font-size:28px}
  header p{margin:6px 0 0;opacity:.9}
  main{max-width:1100px;margin:24px auto;padding:0 16px}
  .perfil{background:#fff;border:1px solid var(--borde);border-radius:12px;
          padding:16px 20px;margin-bottom:24px;display:flex;flex-wrap:wrap;gap:12px}
  .chip{display:inline-block;background:var(--gris);border:1px solid var(--borde);
        border-radius:999px;padding:4px 12px;font-size:13px}
  h2{border-left:4px solid var(--azul2);padding-left:10px;margin-top:32px}
  .tarjeta{background:#fff;border:1px solid var(--borde);border-radius:12px;
           padding:16px 20px;margin-bottom:14px;transition:box-shadow .15s}
  .tarjeta:hover{box-shadow:0 4px 12px rgba(0,0,0,.08)}
  .tarjeta h3{margin:0 0 6px;font-size:17px}
  .tarjeta h3 a{color:var(--azul);text-decoration:none}
  .tarjeta h3 a:hover{text-decoration:underline}
  .meta{font-size:13px;color:#555;margin-bottom:8px}
  .meta .fuente{font-weight:600;color:var(--azul2)}
  .meta .score{background:var(--acento);color:#fff;padding:1px 8px;border-radius:999px;
               font-size:12px;margin-left:8px}
  .resumen{font-size:14px;color:#374151}
  footer{text-align:center;color:#6b7280;font-size:12px;padding:24px}
  .vacio{background:#fff;border:1px dashed var(--borde);border-radius:12px;
         padding:24px;text-align:center;color:#6b7280}
</style>
</head>
<body>
<header>
  <h1>Radar de Ayudas I+D+i</h1>
  <p>Resumen generado para <strong>{{ perfil.nombre }}</strong> — {{ fecha }}</p>
</header>
<main>
  <section class="perfil">
    <span class="chip">🏢 {{ perfil.sector }}</span>
    <span class="chip">👥 {{ perfil.tamano }}</span>
    <span class="chip">🌍 {{ perfil.ambito }}</span>
    {% for i in perfil.intereses %}<span class="chip">✨ {{ i }}</span>{% endfor %}
  </section>

  <h2>🎯 Convocatorias abiertas ({{ convocatorias|length }})</h2>
  {% if convocatorias %}
    {% for r in convocatorias %}
    <article class="tarjeta">
      <h3><a href="{{ r.url }}" target="_blank" rel="noopener">{{ r.titulo }}</a></h3>
      <div class="meta">
        <span class="fuente">{{ r.fuente }}</span>
        {% if r.fecha %} · 📅 {{ r.fecha }}{% endif %}
        {% if r.puntuacion > 0 %}<span class="score">★ {{ r.puntuacion }}</span>{% endif %}
      </div>
      <div class="resumen">{{ r.resumen }}</div>
    </article>
    {% endfor %}
  {% else %}
    <div class="vacio">No se han encontrado convocatorias nuevas en esta ejecución.</div>
  {% endif %}

  <h2>📰 Noticias de digitalización para pymes ({{ noticias|length }})</h2>
  {% if noticias %}
    {% for r in noticias %}
    <article class="tarjeta">
      <h3><a href="{{ r.url }}" target="_blank" rel="noopener">{{ r.titulo }}</a></h3>
      <div class="meta">
        <span class="fuente">{{ r.fuente }}</span>
        {% if r.fecha %} · 📅 {{ r.fecha }}{% endif %}
        {% if r.puntuacion > 0 %}<span class="score">★ {{ r.puntuacion }}</span>{% endif %}
      </div>
      <div class="resumen">{{ r.resumen }}</div>
    </article>
    {% endfor %}
  {% else %}
    <div class="vacio">Sin noticias destacadas esta semana.</div>
  {% endif %}

  <footer>
    Generado automáticamente por <strong>Radar Ayudas I+D+i</strong>
    · Fuentes: Google News RSS + organismos oficiales citados.
  </footer>
</main>
</body>
</html>
""")


def generar_html(
    perfil: PerfilEmpresa,
    resultados: List[Resultado],
    ruta_salida: Path,
    top_n: int = 20,
) -> Path:
    """Genera el informe HTML y lo escribe en `ruta_salida`.

    - Ordena por puntuación descendente (relevancia según perfil).
    - Separa en dos secciones: convocatorias y noticias.
    - Limita a `top_n` por sección para no saturar el correo.
    """
    ordenados = sorted(resultados, key=lambda r: (r.puntuacion, r.fecha), reverse=True)
    convocatorias = [r for r in ordenados if r.categoria == "convocatoria"][:top_n]
    noticias = [r for r in ordenados if r.categoria == "noticia"][:top_n]

    html = _PLANTILLA.render(
        perfil=perfil,
        convocatorias=convocatorias,
        noticias=noticias,
        fecha=datetime.now().strftime("%d/%m/%Y %H:%M"),
    )

    ruta_salida.parent.mkdir(parents=True, exist_ok=True)
    ruta_salida.write_text(html, encoding="utf-8")
    return ruta_salida

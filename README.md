# Radar de Ayudas I+D+i y Digitalización para Pymes

Aplicación en Python que:

1. Busca **convocatorias I+D abiertas** en los principales centros: CDTI, Horizonte Europa, EIC, ENISA, Red.es (Kit Digital), ICEX, Ministerio de Industria, AEI, Eureka/Eurostars y BEI/EIF.
2. Busca **noticias sobre digitalización para pymes en España**.
3. Guarda todo en un **CSV** (`datos/resultados.csv`) con columnas: título, fuente, fecha, URL, resumen.
4. Genera un **HTML visual y bonito** (`docs/index.html`) listo para abrir en navegador o publicar en **GitHub Pages**.
5. Incluye un **scheduler** que envía el resumen por email cada **lunes a las 08:00**.

La aplicación **pregunta características de tu empresa** (sector, tamaño, ámbito, intereses) y las usa para **puntuar la relevancia** de cada resultado.

## Instalación

```bash
cd radar_ayudas_idi
python -m venv venv
# Windows
venv\Scripts\activate
# Linux / macOS
source venv/bin/activate

pip install -r requirements.txt
```

## Uso básico

### Ejecución interactiva (pregunta el perfil)

```bash
python radar.py
```

Te pedirá: nombre, sector, tamaño, ámbito e intereses. El perfil se guarda en `datos/perfil_empresa.json` para reutilizarlo la próxima vez.

### Ejecución con perfil de demostración

```bash
python radar.py --perfil demo
```

### Ejecución con un perfil guardado

```bash
python radar.py --perfil datos/perfil_empresa.json
```

## Salida

Tras ejecutarse:

- `datos/resultados.csv` — todos los resultados en CSV.
- `docs/index.html` — informe visual listo para publicar.

Abre `docs/index.html` en tu navegador para ver el resumen con tarjetas, chips de perfil y puntuación de relevancia.

## Envío por email los lunes a las 08:00

1. Copia `.env.example` a `.env` y rellena las credenciales SMTP:

   ```bash
   cp .env.example .env
   ```

   Para Gmail, usa una **contraseña de aplicación** (https://myaccount.google.com/apppasswords).

2. Prueba un envío inmediato:

   ```bash
   python email_scheduler.py --ahora
   ```

3. Deja corriendo el scheduler (se queda escuchando):

   ```bash
   python email_scheduler.py
   ```

   Enviará el correo cada lunes a las 08:00 hora local.

Para que funcione de forma persistente, ejecútalo con:

- **Windows**: Programador de tareas → acción → `python C:\...\email_scheduler.py`
- **Linux/macOS**: `cron` o `systemd` con `python email_scheduler.py`

## Publicar en GitHub Pages

El HTML se genera en `docs/index.html`, que es la ruta por defecto de GitHub Pages.

```bash
cd radar_ayudas_idi
git init
git add .
git commit -m "Radar de ayudas I+D+i"
git branch -M main
git remote add origin https://github.com/<tu-usuario>/<tu-repo>.git
git push -u origin main
```

Luego en GitHub: **Settings → Pages → Source: Deploy from a branch → Branch: `main` / `/docs`** → Save.

Tu informe quedará disponible en `https://<tu-usuario>.github.io/<tu-repo>/`.

Para republicar tras cada ejecución:

```bash
python radar.py
git add docs/index.html datos/resultados.csv
git commit -m "Actualización radar $(date +%F)"
git push
```

## Estructura del proyecto

```
radar_ayudas_idi/
├── radar.py              # Punto de entrada principal
├── config.py             # Catálogo de centros y cuestionario
├── fuentes.py            # Búsqueda en Google News RSS
├── html_render.py        # Generación del HTML visual
├── email_scheduler.py    # Envío programado por email
├── requirements.txt
├── .env.example
├── datos/                # CSV y perfil guardado
└── docs/                 # HTML publicable en GitHub Pages
```

## Centros incluidos

| Centro | Ámbito |
|---|---|
| CDTI — Centro para el Desarrollo Tecnológico e Innovación | España |
| Horizonte Europa (Horizon Europe) | Unión Europea |
| EIC — European Innovation Council | Unión Europea |
| ENISA — Empresa Nacional de Innovación | España |
| Red.es / Acelera Pyme (Kit Digital) | España |
| ICEX España Exportación e Inversiones | España |
| Ministerio de Industria, Comercio y Turismo | España |
| Agencia Estatal de Investigación (AEI) | España |
| Eureka / Eurostars | Internacional |
| BEI / Fondo Europeo de Inversiones | Unión Europea |

Para añadir más centros, edita la lista `CENTROS` en `config.py`.

## Notas técnicas

- Usamos **Google News RSS** como agregador universal: no requiere API key, es estable y filtra por idioma y país (`hl=es`, `gl=ES`).
- Cada resultado se puntúa según coincidencias con las palabras clave de tu perfil.
- Los resultados se deduplican por URL.
- BeautifulSoup limpia el HTML de los resúmenes.

## Licencia

MIT.

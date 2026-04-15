"""
Script para enviar el resumen por email cada LUNES a las 08:00.

Usa SMTP estándar (Gmail, Outlook, cualquier servidor). Las credenciales
se leen de un archivo `.env` para no dejar contraseñas en el código.

Ejecución:
    python email_scheduler.py          # queda escuchando y envía los lunes
    python email_scheduler.py --ahora  # envío inmediato de prueba
"""

from __future__ import annotations

import argparse
import os
import smtplib
import ssl
import time
from email.message import EmailMessage
from pathlib import Path

import schedule
from dotenv import load_dotenv

from radar import ejecutar_flujo_completo  # función orquestadora definida en radar.py


# Carga las variables de entorno desde `.env` si existe.
load_dotenv()

# Rutas por defecto (relativas a este archivo).
RAIZ = Path(__file__).parent
RUTA_HTML = RAIZ / "docs" / "index.html"
RUTA_CSV = RAIZ / "datos" / "resultados.csv"


def _leer_credenciales() -> dict:
    """Lee las credenciales SMTP del entorno. Lanza error claro si faltan."""
    cred = {
        "host": os.getenv("SMTP_HOST", "smtp.gmail.com"),
        "port": int(os.getenv("SMTP_PORT", "465")),
        "user": os.getenv("SMTP_USER", ""),
        "password": os.getenv("SMTP_PASSWORD", ""),
        "destinatario": os.getenv("EMAIL_DESTINO", ""),
        "remitente": os.getenv("EMAIL_REMITENTE", ""),
    }
    faltan = [k for k in ("user", "password", "destinatario") if not cred[k]]
    if faltan:
        raise RuntimeError(
            "Faltan variables en .env: " + ", ".join(faltan) +
            ". Copia .env.example → .env y rellénalo."
        )
    if not cred["remitente"]:
        cred["remitente"] = cred["user"]
    return cred


def enviar_email() -> None:
    """Regenera el radar y envía el HTML por correo.

    1) Llama a `ejecutar_flujo_completo` para refrescar CSV y HTML.
    2) Lee el HTML recién generado.
    3) Lo manda como cuerpo HTML y también como adjunto por si acaso.
    """
    print("⏰ Ejecutando radar antes de enviar el email...")
    ejecutar_flujo_completo()  # actualiza CSV y HTML

    cred = _leer_credenciales()

    if not RUTA_HTML.exists():
        raise RuntimeError(f"No se encuentra el HTML en {RUTA_HTML}")
    cuerpo_html = RUTA_HTML.read_text(encoding="utf-8")

    msg = EmailMessage()
    msg["Subject"] = "📡 Radar semanal de ayudas I+D+i y digitalización"
    msg["From"] = cred["remitente"]
    msg["To"] = cred["destinatario"]
    msg.set_content(
        "Tu cliente de correo no muestra HTML. Abre el archivo adjunto para ver el resumen."
    )
    msg.add_alternative(cuerpo_html, subtype="html")

    # Adjuntamos también el CSV si existe, para archivarlo fácilmente.
    if RUTA_CSV.exists():
        msg.add_attachment(
            RUTA_CSV.read_bytes(),
            maintype="text",
            subtype="csv",
            filename=RUTA_CSV.name,
        )

    contexto = ssl.create_default_context()
    print(f"📧 Conectando a {cred['host']}:{cred['port']}...")
    with smtplib.SMTP_SSL(cred["host"], cred["port"], context=contexto) as smtp:
        smtp.login(cred["user"], cred["password"])
        smtp.send_message(msg)
    print(f"✅ Email enviado a {cred['destinatario']}")


def _bucle_programado() -> None:
    """Programa la tarea todos los lunes a las 08:00 y deja el proceso vivo."""
    schedule.every().monday.at("08:00").do(enviar_email)
    print("🗓️  Programado: lunes 08:00. Ctrl+C para salir.")
    while True:
        schedule.run_pending()
        time.sleep(30)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Enviador semanal del radar.")
    parser.add_argument("--ahora", action="store_true", help="Enviar un email de prueba ahora.")
    args = parser.parse_args()

    if args.ahora:
        enviar_email()
    else:
        _bucle_programado()

"""
Configuración central del Radar de Ayudas I+D+i.

Este módulo define:
  1) El catálogo de CENTROS/ORGANISMOS sobre los que se buscan convocatorias.
  2) Las fuentes (URLs o RSS de Google News) asociadas a cada centro.
  3) El cuestionario para definir el PERFIL DE LA EMPRESA del usuario.
  4) El sistema de palabras clave para puntuar la relevancia de cada resultado.

Todo está en español y no requiere API keys: usamos feeds RSS públicos
(Google News) y, cuando es posible, el RSS/HTML de cada organismo.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict


# ---------------------------------------------------------------------------
# 1) CATÁLOGO DE CENTROS / ORGANISMOS DE FINANCIACIÓN I+D+i
# ---------------------------------------------------------------------------
# Cada centro tiene:
#   - nombre legible
#   - web oficial (para citar en el HTML)
#   - lista de consultas que se lanzan a Google News RSS (cubren tanto la
#     web oficial vía "site:" como noticias generales sobre ese organismo).
#
# Si quieres añadir más centros, solo agrega una entrada a esta lista.
# ---------------------------------------------------------------------------

CENTROS: List[Dict] = [
    {
        "id": "cdti",
        "nombre": "CDTI — Centro para el Desarrollo Tecnológico e Innovación",
        "web": "https://www.cdti.es",
        "ambito": "España",
        "consultas": [
            "site:cdti.es convocatoria",
            "CDTI ayudas convocatoria abierta",
            "CDTI Neotec",
            "CDTI Misiones",
        ],
    },
    {
        "id": "horizonte_europa",
        "nombre": "Horizonte Europa (Horizon Europe)",
        "web": "https://ec.europa.eu/info/funding-tenders/opportunities/portal/screen/home",
        "ambito": "Unión Europea",
        "consultas": [
            "Horizonte Europa convocatoria abierta pymes",
            "Horizon Europe call open SMEs",
            "EIC Accelerator convocatoria",
            "Cluster 4 digital Horizon Europe",
        ],
    },
    {
        "id": "eic",
        "nombre": "EIC — European Innovation Council",
        "web": "https://eic.ec.europa.eu",
        "ambito": "Unión Europea",
        "consultas": [
            "EIC Pathfinder call",
            "EIC Accelerator open call",
            "European Innovation Council convocatoria",
        ],
    },
    {
        "id": "enisa",
        "nombre": "ENISA — Empresa Nacional de Innovación",
        "web": "https://www.enisa.es",
        "ambito": "España",
        "consultas": [
            "site:enisa.es línea",
            "ENISA préstamo participativo pymes",
            "ENISA emprendedores",
        ],
    },
    {
        "id": "red_es",
        "nombre": "Red.es / Acelera Pyme (Kit Digital)",
        "web": "https://www.acelerapyme.gob.es",
        "ambito": "España",
        "consultas": [
            "Kit Digital convocatoria pymes",
            "Red.es convocatoria ayudas digitalización",
            "Acelera Pyme ayudas",
        ],
    },
    {
        "id": "icex",
        "nombre": "ICEX España Exportación e Inversiones",
        "web": "https://www.icex.es",
        "ambito": "España",
        "consultas": [
            "ICEX Next pymes internacionalización",
            "ICEX convocatoria ayudas",
        ],
    },
    {
        "id": "mincotur",
        "nombre": "Ministerio de Industria, Comercio y Turismo",
        "web": "https://www.mincotur.gob.es",
        "ambito": "España",
        "consultas": [
            "Ministerio Industria ayudas I+D pymes convocatoria",
            "PERTE ayudas convocatoria",
        ],
    },
    {
        "id": "aei",
        "nombre": "Agencia Estatal de Investigación (AEI)",
        "web": "https://www.aei.gob.es",
        "ambito": "España",
        "consultas": [
            "Agencia Estatal Investigación convocatoria",
            "AEI ayudas I+D",
        ],
    },
    {
        "id": "eureka",
        "nombre": "Eureka / Eurostars",
        "web": "https://www.eurekanetwork.org",
        "ambito": "Internacional",
        "consultas": [
            "Eurostars convocatoria pymes I+D",
            "Eureka cluster call",
        ],
    },
    {
        "id": "bei_eif",
        "nombre": "BEI / Fondo Europeo de Inversiones",
        "web": "https://www.eib.org",
        "ambito": "Unión Europea",
        "consultas": [
            "BEI financiación pymes innovación",
            "European Investment Fund SME",
        ],
    },
]


# ---------------------------------------------------------------------------
# 2) CONSULTAS GENÉRICAS DE NOTICIAS SOBRE DIGITALIZACIÓN DE PYMES
# ---------------------------------------------------------------------------
# Búsquedas adicionales que NO cuelgan de un centro concreto, para cubrir
# el apartado de "noticias sobre digitalización para pymes en España".
# ---------------------------------------------------------------------------

CONSULTAS_NOTICIAS_DIGITALIZACION: List[str] = [
    "digitalización pymes España",
    "transformación digital pequeña empresa",
    "ayudas digitalización pymes 2026",
    "inteligencia artificial pymes España",
    "ciberseguridad pymes",
]


# ---------------------------------------------------------------------------
# 3) PERFIL DE LA EMPRESA — CUESTIONARIO INTERACTIVO
# ---------------------------------------------------------------------------

@dataclass
class PerfilEmpresa:
    """Representa las características de la empresa del usuario."""
    nombre: str = "Mi Empresa"
    sector: str = "general"          # p.ej. agroalimentario, industrial, salud, software, comercio
    tamano: str = "pyme"             # micro, pyme, mediana, grande
    ambito: str = "nacional"          # local, nacional, europeo, internacional
    intereses: List[str] = field(default_factory=list)  # p.ej. ["digitalización", "IA", "sostenibilidad"]

    def palabras_clave(self) -> List[str]:
        """Genera palabras clave para puntuar la relevancia de cada resultado."""
        base = [self.sector, self.tamano, self.ambito]
        return [p.lower() for p in base + self.intereses if p]


# Opciones que se muestran al usuario durante el cuestionario.
OPCIONES_SECTOR = [
    "agroalimentario", "industrial", "salud", "software", "comercio",
    "turismo", "energía", "construcción", "educación", "logística", "otro",
]
OPCIONES_TAMANO = ["micro", "pyme", "mediana", "grande"]
OPCIONES_AMBITO = ["local", "nacional", "europeo", "internacional"]
OPCIONES_INTERESES = [
    "digitalización", "inteligencia artificial", "ciberseguridad",
    "sostenibilidad", "economía circular", "biotecnología",
    "industria 4.0", "internacionalización", "formación", "I+D básica",
]

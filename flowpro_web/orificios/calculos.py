"""
calculos.py — Orificios
=======================
Descarga por un orificio circular o cuadrado.

    Q = C · A · √(2·g·H)

con C = coeficiente de descarga (corrige contracción del chorro y pérdidas),
A = área del orificio y H = carga medida desde la superficie libre al eje del
orificio. Válido con el orificio sumergido aguas arriba y descarga libre aguas
abajo (régimen permanente).

Reimplementación limpia de la herramienta *Orifices* de Flow Pro 2.1.

Sistemas de unidades
--------------------
    SI      : m, m², m³/s    →  g = 9.806 m/s²
    English : ft, ft², ft³/s →  g = 32.174 ft/s²
"""
from __future__ import annotations

import math
from dataclasses import dataclass

# ─────────────────────────────────────────────────────────────────────────────
#  CONSTANTES Y CATÁLOGOS
# ─────────────────────────────────────────────────────────────────────────────

G = {"SI": 9.806, "English": 32.174}
SISTEMAS = ["SI", "English"]

UNIDAD = {
    "SI":      {"L": "m", "A": "m²", "Q": "m³/s", "V": "m/s"},
    "English": {"L": "ft", "A": "ft²", "Q": "ft³/s", "V": "ft/s"},
}

CIRCULAR = "Circular"
CUADRADO = "Square"
FORMAS = [CIRCULAR, CUADRADO]

# Coeficientes típicos de descarga (guía para el usuario)
COEF_TIPICOS = [
    ("Borde agudo", 0.61),
    ("Entrada redondeada", 0.70),
    ("Bocina (bell-mouth)", 0.80),
    ("Tobera", 0.95),
]


# ─────────────────────────────────────────────────────────────────────────────
#  CÁLCULO
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class Resultado:
    sistema: str
    forma: str
    tamano: float
    C: float
    H: float
    A: float
    Q: float
    V: float          # velocidad media en el orificio = Q/A
    V_ideal: float    # velocidad ideal = √(2gH)


def area_orificio(forma: str, tamano: float) -> float:
    """Área del orificio. tamano = diámetro (circular) o lado (cuadrado)."""
    if forma == CIRCULAR:
        return math.pi * tamano * tamano / 4.0
    if forma == CUADRADO:
        return tamano * tamano
    raise ValueError(f"Forma de orificio desconocida: {forma}")


def resolver(sistema: str, forma: str, tamano: float, C: float, H: float) -> Resultado:
    """Resuelve el caudal por el orificio."""
    if sistema not in SISTEMAS:
        raise ValueError(f"Sistema de unidades desconocido: {sistema}")
    if forma not in FORMAS:
        raise ValueError(f"Forma de orificio desconocida: {forma}")
    if tamano is None or tamano <= 0:
        raise ValueError("El diámetro o lado del orificio debe ser > 0.")
    if C is None or C <= 0:
        raise ValueError("El coeficiente de descarga debe ser > 0.")
    if H is None or H <= 0:
        raise ValueError("La carga sobre el orificio debe ser > 0.")

    g = G[sistema]
    A = area_orificio(forma, tamano)
    V_ideal = math.sqrt(2.0 * g * H)
    Q = C * A * V_ideal
    V = Q / A if A > 0 else 0.0

    return Resultado(sistema=sistema, forma=forma, tamano=tamano, C=C, H=H,
                     A=A, Q=Q, V=V, V_ideal=V_ideal)

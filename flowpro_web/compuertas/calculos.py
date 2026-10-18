"""
calculos.py — Compuertas de fondo (Underflow Gates)
===================================================
Descarga libre bajo una compuerta en un canal rectangular:

    Q = C_d · b · a · √(2·g·y₁)          V = Q / (b·a)

con ``b`` = ancho de la compuerta, ``a`` = apertura, ``y₁`` = tirante aguas arriba y
``C_d`` = coeficiente de contracción/descarga (default 0.61). El mismo coeficiente
sirve para compuertas vertical, radial (tainter) o tambor, usando el valor que
corresponda a cada tipo (bordes redondeados ⇒ ``C_d`` algo mayor).

Reimplementación limpia de la herramienta *Underflow Gates* de Flow Pro 2.1.

Sistemas de unidades
--------------------
    SI      : m, m³/s    →  g = 9.806 m/s²
    English : ft, ft³/s  →  g = 32.174 ft/s²
"""
from __future__ import annotations

import math
from dataclasses import dataclass

G = {"SI": 9.806, "English": 32.174}
SISTEMAS = ["SI", "English"]
UNIDAD = {
    "SI":      {"L": "m", "A": "m²", "Q": "m³/s", "V": "m/s"},
    "English": {"L": "ft", "A": "ft²", "Q": "ft³/s", "V": "ft/s"},
}

# Coeficientes de descarga típicos (descarga libre)
CD_VERTICAL = 0.61    # compuerta plana/deslizante (rango 0.55–0.61)
CD_RADIAL = 0.65      # radial/tainter (borde redondeado)
CD_TAMBOR = 0.65      # tambor (borde redondeado)


@dataclass
class Resultado:
    sistema: str
    y1: float          # tirante aguas arriba
    b: float           # ancho de la compuerta
    a: float           # apertura
    C: float           # coeficiente de descarga
    A: float           # área de la abertura = b·a
    Q: float           # caudal
    V: float           # velocidad en la abertura = Q/A


def resolver(*, sistema: str = "SI", y1: float = None, b: float = None,
             a: float = None, C: float = None) -> Resultado:
    if sistema not in SISTEMAS:
        raise ValueError(f"Sistema de unidades desconocido: {sistema}")
    if y1 is None or y1 <= 0:
        raise ValueError("El tirante aguas arriba y₁ debe ser > 0.")
    if b is None or b <= 0:
        raise ValueError("El ancho de la compuerta b debe ser > 0.")
    if a is None or a <= 0:
        raise ValueError("La apertura a debe ser > 0.")
    if a >= y1:
        raise ValueError("La apertura a debe ser menor que el tirante aguas arriba y₁.")
    if C is None or C <= 0:
        raise ValueError("El coeficiente de descarga debe ser > 0.")

    g = G[sistema]
    A = b * a
    Q = C * b * a * math.sqrt(2.0 * g * y1)
    V = Q / A if A > 0 else 0.0

    return Resultado(sistema=sistema, y1=y1, b=b, a=a, C=C, A=A, Q=Q, V=V)

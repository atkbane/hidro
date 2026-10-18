"""
calculos.py — Vertederos
========================
Descarga por un vertedero de pared delgada (y de cresta ancha), libre o sumergido.

Forma unificada de la pared delgada (``C_d`` adimensional):

    Rectangular / Cipolletti :  Q = C_d · (2/3)·√(2g) · L · H^(3/2)
    Triangular (V)           :  Q = C_d · (8/15)·√(2g) · tan(θ/2) · H^(5/2)

Cresta ancha (teórico, flujo crítico): misma forma con ``C_d ≈ 0.577``.

Sumergido (Villemonte):

    Q_s / Q_f = [ 1 − (H₂/H₁)^n ]^0.385      n = 3/2 (rect./Cipolletti), 5/2 (triang.)

El coeficiente ``C_d`` por defecto es 0.61 (valor clásico de pared delgada), igual
que en el programa original. Reimplementación limpia de la herramienta *Weirs* de
Flow Pro 2.1.

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
    "SI":      {"L": "m", "Q": "m³/s"},
    "English": {"L": "ft", "Q": "ft³/s"},
}

RECTANGULAR = "Rectangular"
TRIANGULAR = "Triangular"
CIPOLETTI = "Cipolletti"
TIPOS = [RECTANGULAR, TRIANGULAR, CIPOLETTI]

# Coeficiente de descarga por defecto
CD_PARED_DELGADA = 0.61     # valor clásico (0.61–0.63)
CD_CRESTA_ANCHA = 0.577     # teórico en la forma (2/3)√(2g)  (⇒ 1.705·L·H^1.5 en SI)
EXPONENTE_VILLEMONTE = 0.385


def coef_defecto(tipo: str, broad_crested: bool) -> float:
    """Coeficiente de descarga sugerido según el tipo de vertedero."""
    if broad_crested and tipo != TRIANGULAR:
        return CD_CRESTA_ANCHA
    return CD_PARED_DELGADA


@dataclass
class Resultado:
    sistema: str
    tipo: str
    sumergido: bool
    broad_crested: bool
    C: float
    L: float          # longitud de cresta (rect/cipolletti); 0 en triangular
    H: float          # carga aguas arriba
    H2: float         # carga aguas abajo (sumergido); 0 si libre
    angulo: float     # ángulo del V (grados); 0 si no aplica
    Qf: float         # caudal si fuese libre
    Q: float          # caudal (corregido si sumergido)
    n: float          # exponente de H en la ecuación libre


def _factor(tipo: str, sistema: str) -> float:
    """Constante geométrico-gravitatoria (sin C_d) que multiplica a H^n."""
    g = G[sistema]
    if tipo == TRIANGULAR:
        return (8.0 / 15.0) * math.sqrt(2.0 * g)
    return (2.0 / 3.0) * math.sqrt(2.0 * g)


def exponente(tipo: str) -> float:
    return 2.5 if tipo == TRIANGULAR else 1.5


def resolver(
    *, sistema: str = "SI", tipo: str = RECTANGULAR, sumergido: bool = False,
    broad_crested: bool = False, L: float = None, H: float = None,
    H2: float = None, angulo: float = None, C: float = None,
) -> Resultado:
    if sistema not in SISTEMAS:
        raise ValueError(f"Sistema de unidades desconocido: {sistema}")
    if tipo not in TIPOS:
        raise ValueError(f"Tipo de vertedero desconocido: {tipo}")
    if H is None or H <= 0:
        raise ValueError("La carga aguas arriba H debe ser > 0.")
    if C is None or C <= 0:
        raise ValueError("El coeficiente de descarga debe ser > 0.")

    n = exponente(tipo)

    if tipo == TRIANGULAR:
        if angulo is None or not (0 < angulo < 180):
            raise ValueError("El ángulo del vertedero en V debe estar entre 0° y 180°.")
        factor = _factor(tipo, sistema) * math.tan(math.radians(angulo) / 2.0)
        L_ef = 0.0
    else:
        if L is None or L <= 0:
            raise ValueError("La longitud de cresta L debe ser > 0.")
        factor = _factor(tipo, sistema)
        L_ef = L
        angulo = 0.0

    Qf = C * factor * (L_ef if tipo != TRIANGULAR else 1.0) * (H ** n)

    Q = Qf
    H2_ok = 0.0
    if sumergido:
        if H2 is None or H2 <= 0:
            raise ValueError("En régimen sumergido debe indicarse la carga aguas abajo H₂.")
        if H2 >= H:
            raise ValueError("La carga aguas abajo H₂ debe ser menor que H₁.")
        ratio = H2 / H
        Q = Qf * (1.0 - ratio ** n) ** EXPONENTE_VILLEMONTE
        H2_ok = H2

    return Resultado(
        sistema=sistema, tipo=tipo, sumergido=sumergido, broad_crested=broad_crested,
        C=C, L=L_ef, H=H, H2=H2_ok, angulo=(angulo or 0.0), Qf=Qf, Q=Q, n=n,
    )

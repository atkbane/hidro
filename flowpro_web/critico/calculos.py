"""
calculos.py — Tirante y pendiente crítica
=========================================
Régimen crítico en un canal abierto prismático.

En régimen crítico el número de Froude vale 1 (energía específica mínima):

    Q²·T / (g·A³) = 1        con A = A(y), T = T(y) en y = Yc

Resuelto por bisección. La pendiente crítica es la pendiente que, por Manning,
produce el tirante crítico:

    Sc = ( n·Q / (k · A_c · R_c^(2/3)) )²

Reimplementación limpia de la herramienta *Critical Depth and Slope* de Flow Pro 2.1.

Sistemas de unidades
--------------------
    SI      : m, m³/s    →  k = 1.000, g = 9.806 m/s²
    English : ft, ft³/s  →  k = 1.486, g = 32.174 ft/s²
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Optional

G = {"SI": 9.806, "English": 32.174}
K_MANNING = {"SI": 1.000, "English": 1.486}
SISTEMAS = ["SI", "English"]

UNIDAD = {
    "SI":      {"L": "m", "A": "m²", "Q": "m³/s", "V": "m/s"},
    "English": {"L": "ft", "A": "ft²", "Q": "ft³/s", "V": "ft/s"},
}

TRAPEZOIDAL = "Trapezoidal"
CIRCULAR = "Circular"
USHAPED = "Ushaped"
ELONGATED = "Elongated circular"
FORMAS = [TRAPEZOIDAL, CIRCULAR, USHAPED, ELONGATED]
FORMAS_IMPLEMENTADAS = [TRAPEZOIDAL, CIRCULAR]


# ─────────────────────────────────────────────────────────────────────────────
#  GEOMETRÍA
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class Props:
    y: float
    A: float   # área mojada
    P: float   # perímetro mojado
    T: float   # ancho superior
    R: float   # radio hidráulico


@dataclass
class Seccion:
    forma: str
    b: Optional[float] = None
    m: Optional[float] = None
    D: Optional[float] = None

    def props(self, y: float) -> Props:
        if y <= 0.0:
            return Props(0.0, 0.0, 0.0, 0.0, 0.0)
        if self.forma == TRAPEZOIDAL:
            b, m = self.b, self.m
            A = y * (b + m * y)
            P = b + 2.0 * y * math.sqrt(1.0 + m * m)
            T = b + 2.0 * m * y
        elif self.forma == CIRCULAR:
            D = self.D
            y = min(y, D)
            th = 2.0 * math.acos(max(-1.0, min(1.0, 1.0 - 2.0 * y / D)))
            A = D * D / 8.0 * (th - math.sin(th))
            P = D * th / 2.0
            T = D * math.sin(th / 2.0)
        else:
            raise NotImplementedError(f"Sección no implementada: {self.forma}")
        R = A / P if P > 0 else 0.0
        return Props(y, A, P, T, R)

    def y_max(self) -> Optional[float]:
        return self.D if self.forma == CIRCULAR else None

    def validar(self) -> None:
        if self.forma not in FORMAS_IMPLEMENTADAS:
            raise ValueError(f"Sección «{self.forma}» aún no implementada.")
        if self.forma == TRAPEZOIDAL:
            if self.b is None or self.b <= 0:
                raise ValueError("El ancho de solera debe ser > 0.")
            if self.m is None or self.m < 0:
                raise ValueError("El talud debe ser ≥ 0.")
        elif self.forma == CIRCULAR:
            if self.D is None or self.D <= 0:
                raise ValueError("El diámetro debe ser > 0.")


# ─────────────────────────────────────────────────────────────────────────────
#  CÁLCULO
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class Resultado:
    forma: str
    sistema: str
    Q: float
    n: float
    Yc: float
    Ac: float
    Tc: float
    Pc: float
    Rc: float
    Vc: float
    Sc: float


def _f_critico(sec: Seccion, y: float, Q: float, g: float) -> float:
    """f(y) = Q²·T/(g·A³) — vale 1 en el tirante crítico (decreciente en y)."""
    p = sec.props(y)
    if p.A <= 0:
        return float("inf")
    return Q * Q * p.T / (g * p.A ** 3)


def tirante_critico(sec: Seccion, Q: float, g: float) -> float:
    """Bisección de Q²T/(gA³) = 1."""
    ymax = sec.y_max()
    if ymax is not None:
        hi = ymax
        if _f_critico(sec, hi, Q, g) > 1.0:
            raise ValueError("No hay tirante crítico dentro de la sección.")
    else:
        hi = max(1.0, sec.b or 1.0)
        for _ in range(200):
            if _f_critico(sec, hi, Q, g) <= 1.0:
                break
            hi *= 2.0
        else:
            raise ValueError("No se pudo acotar el tirante crítico.")

    lo = 1e-12
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if _f_critico(sec, mid, Q, g) > 1.0:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def resolver(sec: Seccion, *, sistema: str = "SI", Q: float = None, n: float = None) -> Resultado:
    if sistema not in SISTEMAS:
        raise ValueError(f"Sistema de unidades desconocido: {sistema}")
    sec.validar()
    if Q is None or Q <= 0:
        raise ValueError("El caudal debe ser > 0.")
    if n is None or n <= 0:
        raise ValueError("La rugosidad n debe ser > 0.")

    g = G[sistema]
    k = K_MANNING[sistema]

    Yc = tirante_critico(sec, Q, g)
    pc = sec.props(Yc)
    Vc = Q / pc.A if pc.A > 0 else 0.0
    Sc = (n * Q / (k * pc.A * (pc.R ** (2.0 / 3.0)))) ** 2 if pc.R > 0 else 0.0

    return Resultado(forma=sec.forma, sistema=sistema, Q=Q, n=n,
                     Yc=Yc, Ac=pc.A, Tc=pc.T, Pc=pc.P, Rc=pc.R, Vc=Vc, Sc=Sc)

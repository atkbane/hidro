"""
calculos.py
===========
Núcleo hidráulico — «Tirante normal y Manning».

Reimplementación limpia (clean-room) de la herramienta *Depth, Flowrate, Slope,
and Roughness* de Flow Pro 2.1, a partir de la ecuación de Manning y de la
geometría estándar de las secciones. No contiene código del programa original.

    Q = (k/n) · A · R^(2/3) · S^(1/2)        con  R = A/P

Permite resolver cualquiera de las cuatro incógnitas —tirante y, caudal Q,
pendiente S o rugosidad n— dejando las otras tres como datos. Las salidas
adicionales (V, A, P, R) siguen la disposición de la herramienta original.

Sistemas de unidades
--------------------
    SI      : m, m³/s    →  k = 1.000   (g = 9.806 m/s²)
    English : ft, ft³/s  →  k = 1.486   (g = 32.174 ft/s²)

El factor K de Manning es adimensional en SI y vale 1.486 en unidades inglesas.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Optional

# ─────────────────────────────────────────────────────────────────────────────
#  CONSTANTES
# ─────────────────────────────────────────────────────────────────────────────

# Aceleración de la gravedad por sistema de unidades
G = {"SI": 9.806, "English": 32.174}

# Factor K de Manning: 1.000 en SI, 1.486 en unidades inglesas
K_MANNING = {"SI": 1.000, "English": 1.486}

SISTEMAS = ["SI", "English"]

# Símbolos de unidad por sistema
UNIDAD = {
    "SI":      {"L": "m", "A": "m²", "Q": "m³/s", "V": "m/s"},
    "English": {"L": "ft", "A": "ft²", "Q": "ft³/s", "V": "ft/s"},
}

# ─────────────────────────────────────────────────────────────────────────────
#  CATÁLOGOS
# ─────────────────────────────────────────────────────────────────────────────

# Formas de sección (nombres usados por Flow Pro 2.1)
TRAPEZOIDAL = "Trapezoidal"
CIRCULAR = "Circular"
USHAPED = "Ushaped"
ELONGATED = "Elongated circular"
FORMAS = [TRAPEZOIDAL, CIRCULAR, USHAPED, ELONGATED]

# Formas con geometría implementada (U-shaped y elongated circular pendientes)
FORMAS_IMPLEMENTADAS = [TRAPEZOIDAL, CIRCULAR]

# Incógnitas (equivalen a las cuatro pestañas del original)
PROFUNDIDAD = "profundidad"
CAUDAL = "caudal"
PENDIENTE = "pendiente"
RUGOSIDAD = "rugosidad"
INCOGNITAS = [PROFUNDIDAD, CAUDAL, PENDIENTE, RUGOSIDAD]

# ─────────────────────────────────────────────────────────────────────────────
#  GEOMETRÍA DE LA SECCIÓN
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class Props:
    """Propiedades hidráulicas de la sección para un tirante dado."""
    y: float   # tirante [L]
    A: float   # área mojada [L²]
    P: float   # perímetro mojado [L]
    T: float   # ancho superior [L]
    R: float   # radio hidráulico = A/P [L]


@dataclass
class Seccion:
    """Geometría de una sección transversal prismática.

    forma : una de FORMAS
    b     : ancho de solera [L]  (trapezoidal)
    m     : talud H:V, m=0 ⇒ rectangular [—]  (trapezoidal)
    D     : diámetro [L]  (circular)
    """
    forma: str
    b: Optional[float] = None
    m: Optional[float] = None
    D: Optional[float] = None

    def props(self, y: float) -> Props:
        """Área, perímetro, ancho superior y radio hidráulico en el tirante y."""
        if y <= 0.0:
            return Props(y=0.0, A=0.0, P=0.0, T=0.0, R=0.0)

        if self.forma == TRAPEZOIDAL:
            b, m = self.b, self.m
            A = y * (b + m * y)
            P = b + 2.0 * y * math.sqrt(1.0 + m * m)
            T = b + 2.0 * m * y

        elif self.forma == CIRCULAR:
            D = self.D
            y = min(y, D)
            # θ = 2·arccos(1 − 2y/D), el ángulo central del segmento mojado
            th = 2.0 * math.acos(max(-1.0, min(1.0, 1.0 - 2.0 * y / D)))
            A = D * D / 8.0 * (th - math.sin(th))
            P = D * th / 2.0
            T = D * math.sin(th / 2.0)

        else:
            raise NotImplementedError(f"Sección no implementada: {self.forma}")

        R = A / P if P > 0.0 else 0.0
        return Props(y=y, A=A, P=P, T=T, R=R)

    def y_max(self) -> Optional[float]:
        """Tirante máximo admisible (secciones cerradas) o None si no hay límite."""
        if self.forma == CIRCULAR:
            return self.D
        return None

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
#  MANNING
# ─────────────────────────────────────────────────────────────────────────────

def caudal_manning(sec: Seccion, y: float, n: float, S: float, k: float) -> float:
    """Caudal por Manning: Q = (k/n)·A·R^(2/3)·S^(1/2)."""
    if y <= 0.0 or n <= 0.0 or S <= 0.0:
        return 0.0
    p = sec.props(y)
    if p.A <= 0.0 or p.P <= 0.0:
        return 0.0
    return (k / n) * p.A * (p.R ** (2.0 / 3.0)) * math.sqrt(S)


def _tirante_normal(sec: Seccion, Q: float, n: float, S: float, k: float) -> float:
    """Resuelve el tirante normal por bisección.

    En sección circular el caudal crece con el tirante solo hasta y/D ≈ 0.938
    (máximo de Manning); por encima el flujo pasa a conducto lleno y el método
    deja de ser aplicable. Se busca la raíz en la rama monótona.
    """
    ymax = sec.y_max()

    # Límite superior del intervalo
    if ymax is not None:
        hi = 0.938 * ymax
        if caudal_manning(sec, hi, n, S, k) < Q:
            raise ValueError(
                "El caudal supera la capacidad de la sección y el flujo pasa a "
                "conducto lleno (a presión); fuera del alcance del canal abierto."
            )
    else:
        hi = max(1.0, sec.b or 1.0)
        for _ in range(200):
            if caudal_manning(sec, hi, n, S, k) >= Q:
                break
            hi *= 2.0
        else:
            raise ValueError("No se pudo acotar el tirante normal.")

    lo = 1e-9
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if caudal_manning(sec, mid, n, S, k) < Q:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


# ─────────────────────────────────────────────────────────────────────────────
#  RESULTADO Y ORQUESTADOR
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class Resultado:
    """Resultado completo del cálculo."""
    forma: str
    sistema: str
    incognita: str
    y: float
    Q: float
    S: float
    n: float
    V: float
    A: float
    P: float
    T: float
    R: float
    Fr: float
    regimen: str


def _req(valor: Optional[float], nombre: str) -> float:
    if valor is None:
        raise ValueError(f"Falta el dato: {nombre}.")
    return float(valor)


def resolver(
    sec: Seccion,
    incognita: str,
    *,
    sistema: str = "SI",
    y: Optional[float] = None,
    Q: Optional[float] = None,
    S: Optional[float] = None,
    n: Optional[float] = None,
) -> Resultado:
    """Resuelve Manning para la incógnita indicada.

    incognita : PROFUNDIDAD | CAUDAL | PENDIENTE | RUGOSIDAD
    Deben aportarse los tres datos restantes (y, Q, S, n).
    """
    if sistema not in SISTEMAS:
        raise ValueError(f"Sistema de unidades desconocido: {sistema}")
    sec.validar()
    k = K_MANNING[sistema]
    g = G[sistema]

    if incognita == PROFUNDIDAD:
        Q = _req(Q, "caudal")
        n = _req(n, "rugosidad n")
        S = _req(S, "pendiente de fondo")
        if Q <= 0:
            raise ValueError("El caudal debe ser > 0.")
        if n <= 0:
            raise ValueError("La rugosidad n debe ser > 0.")
        if S <= 0:
            raise ValueError("La pendiente debe ser > 0.")
        y = _tirante_normal(sec, Q, n, S, k)

    elif incognita == CAUDAL:
        y = _req(y, "tirante")
        n = _req(n, "rugosidad n")
        S = _req(S, "pendiente de fondo")
        if y <= 0:
            raise ValueError("El tirante debe ser > 0.")
        if n <= 0:
            raise ValueError("La rugosidad n debe ser > 0.")
        if S <= 0:
            raise ValueError("La pendiente debe ser > 0.")
        Q = caudal_manning(sec, y, n, S, k)

    elif incognita == PENDIENTE:
        Q = _req(Q, "caudal")
        y = _req(y, "tirante")
        n = _req(n, "rugosidad n")
        if Q <= 0:
            raise ValueError("El caudal debe ser > 0.")
        if y <= 0:
            raise ValueError("El tirante debe ser > 0.")
        if n <= 0:
            raise ValueError("La rugosidad n debe ser > 0.")
        p = sec.props(y)
        if p.A <= 0 or p.R <= 0:
            raise ValueError("Geometría no válida para ese tirante.")
        S = (Q * n / (k * p.A * (p.R ** (2.0 / 3.0)))) ** 2

    elif incognita == RUGOSIDAD:
        Q = _req(Q, "caudal")
        y = _req(y, "tirante")
        S = _req(S, "pendiente de fondo")
        if Q <= 0:
            raise ValueError("El caudal debe ser > 0.")
        if y <= 0:
            raise ValueError("El tirante debe ser > 0.")
        if S <= 0:
            raise ValueError("La pendiente debe ser > 0.")
        p = sec.props(y)
        if p.A <= 0 or p.R <= 0:
            raise ValueError("Geometría no válida para ese tirante.")
        n = k * p.A * (p.R ** (2.0 / 3.0)) * math.sqrt(S) / Q

    else:
        raise ValueError(f"Incógnita desconocida: {incognita}")

    # Validación del tirante frente al límite de la sección
    ymax = sec.y_max()
    aviso = None
    if ymax is not None and y > ymax:
        raise ValueError("El tirante no puede superar el diámetro de la sección.")

    # Propiedades y régimen en el tirante final
    p = sec.props(y)
    V = Q / p.A if p.A > 0 else 0.0
    Dh = p.A / p.T if p.T > 0 else 0.0     # profundidad hidráulica
    Fr = V / math.sqrt(g * Dh) if Dh > 0 else 0.0
    if abs(Fr - 1.0) < 1e-9:
        regimen = "crítico"
    elif Fr < 1.0:
        regimen = "subcrítico"
    else:
        regimen = "supercrítico"

    return Resultado(
        forma=sec.forma, sistema=sistema, incognita=incognita,
        y=y, Q=Q, S=S, n=n,
        V=V, A=p.A, P=p.P, T=p.T, R=p.R,
        Fr=Fr, regimen=regimen,
    )

"""
calculos.py — Perfil de superficie libre
========================================
Perfil de flujo gradualmente variado (GVF) en un canal abierto prismático, por
el método de paso directo (integración de dx/dy con la regla de Simpson 1/3).

    dx/dy = (1 − Fr²) / (S₀ − S_f)
    S_f   = (Q·n/k)² · P^(4/3) / A^(10/3)
    Fr²   = Q²·T / (g·A³)

Reimplementación limpia de la herramienta *Water Surface Profile* de Flow Pro 2.1.
Reproduce el algoritmo documentado por el programa: control en el extremo aguas
abajo para flujo subcrítico y aguas arriba para supercrítico; paso en tirante
Δy = (Y_destino − Y_control)·0.998/N, con N sub-pasos y una fila por cada dos
sub-pasos; parada al alcanzar el tirante de referencia o el extremo del canal.

Sistemas de unidades
--------------------
    SI      : m, m³/s    →  k = 1.000, g = 9.806 m/s²
    English : ft, ft³/s  →  k = 1.486, g = 32.174 ft/s²
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List, Optional

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

N_PASOS_DEF = 30          # sub-pasos por defecto (2 por fila)
FACTOR_PARADA = 0.998     # evita alcanzar exactamente el tirante de referencia


# ─────────────────────────────────────────────────────────────────────────────
#  GEOMETRÍA
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class Props:
    y: float
    A: float
    P: float
    T: float
    R: float


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

    def momento_area(self, y: float) -> float:
        """Primer momento de área respecto a la superficie libre: A·ȳ."""
        if y <= 0.0:
            return 0.0
        if self.forma == TRAPEZOIDAL:
            return self.b * y * y / 2.0 + self.m * y ** 3 / 3.0
        if self.forma == CIRCULAR:
            D = self.D
            y = min(y, D)
            R = D / 2.0
            al = math.acos(max(-1.0, min(1.0, 1.0 - 2.0 * y / D)))  # ∈ [0, π]
            return 2.0 * R ** 3 * (
                -al * math.cos(al) / 2.0
                + math.sin(al) * math.cos(al) ** 2 / 2.0
                + math.sin(al) ** 3 / 3.0
            )
        raise NotImplementedError(f"Sección no implementada: {self.forma}")

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
#  TIRANTES DE REFERENCIA
# ─────────────────────────────────────────────────────────────────────────────

def caudal_manning(sec: Seccion, y: float, n: float, S0: float, k: float) -> float:
    p = sec.props(y)
    if p.A <= 0 or p.P <= 0 or n <= 0 or S0 <= 0:
        return 0.0
    return (k / n) * p.A * (p.R ** (2.0 / 3.0)) * math.sqrt(S0)


def tirante_normal(sec: Seccion, Q: float, n: float, S0: float, k: float) -> float:
    """Tirante normal por bisección. Marca error si excede la capacidad."""
    ymax = sec.y_max()
    if ymax is not None:
        hi = 0.938 * ymax
        if caudal_manning(sec, hi, n, S0, k) < Q:
            raise ValueError("capacidad excedida")
    else:
        hi = max(1.0, sec.b or 1.0)
        for _ in range(200):
            if caudal_manning(sec, hi, n, S0, k) >= Q:
                break
            hi *= 2.0
        else:
            raise ValueError("No se pudo acotar el tirante normal.")
    lo = 1e-9
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if caudal_manning(sec, mid, n, S0, k) < Q:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def _f_critico(sec: Seccion, y: float, Q: float, g: float) -> float:
    p = sec.props(y)
    if p.A <= 0:
        return float("inf")
    return Q * Q * p.T / (g * p.A ** 3)


def tirante_critico(sec: Seccion, Q: float, g: float) -> float:
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


# ─────────────────────────────────────────────────────────────────────────────
#  PERFIL
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class Fila:
    estacion: float
    y: float
    E: float       # energía específica = y + V²/(2g)
    A: float
    V: float
    T: float
    M: float       # momentum total (fuerza específica) = A·ȳ + Q²/(gA)
    Fr: float
    Fr2: float
    hv: float      # carga de velocidad V²/(2g)
    R: float
    P: float


@dataclass
class Resultado:
    forma: str
    sistema: str
    Q: float
    n: float
    S0: float
    control: float
    est0: float
    est1: float
    Yn: Optional[float]
    An: Optional[float]
    Yc: float
    Ac: float
    perfil: str
    flujo: str
    filas: List[Fila]
    aviso: Optional[str] = None


def _fila(sec: Seccion, est: float, y: float, Q: float, g: float) -> Fila:
    p = sec.props(y)
    A = p.A
    V = Q / A if A > 0 else 0.0
    hv = V * V / (2.0 * g)
    E = y + hv
    M = sec.momento_area(y) + (Q * Q / (g * A) if A > 0 else 0.0)
    Dh = A / p.T if p.T > 0 else 0.0
    Fr = V / math.sqrt(g * Dh) if Dh > 0 else 0.0
    return Fila(estacion=est, y=y, E=E, A=A, V=V, T=p.T, M=M,
                Fr=Fr, Fr2=Fr * Fr, hv=hv, R=p.R, P=p.P)


def _dx_dy(sec: Seccion, y: float, Q: float, n: float, S0: float, k: float, g: float) -> float:
    p = sec.props(y)
    if p.A <= 0 or p.P <= 0 or p.T <= 0:
        return 0.0
    Sf = (Q * n / k) ** 2 * p.P ** (4.0 / 3.0) / p.A ** (10.0 / 3.0)
    Fr2 = Q * Q * p.T / (g * p.A ** 3)
    den = S0 - Sf
    if abs(den) < 1e-15:
        return 0.0
    return (1.0 - Fr2) / den


def _clasificar(sec: Seccion, Yn: Optional[float], Yc: float, y: float, S0: float) -> str:
    if S0 < 0:
        letra, nombre = "A", "adverse"
    elif S0 == 0:
        letra, nombre = "H", "horizontal"
    elif Yn is None:
        letra, nombre = "C", "critical"
    elif abs(Yn - Yc) <= 1e-6 * max(1.0, Yc):
        letra, nombre = "C", "critical"
    elif Yn > Yc:
        letra, nombre = "M", "mild"
    else:
        letra, nombre = "S", "steep"

    if Yn is not None and letra in ("M", "S", "C"):
        if y > Yn and y > Yc:
            dig = 1
        elif y < Yn and y < Yc:
            dig = 3
        else:
            dig = 2
    else:
        dig = 2 if y >= Yc else 3
    return f"{nombre}, {letra}-{dig}"


def resolver_perfil(
    sec: Seccion, *,
    sistema: str = "SI",
    Q: float,
    n: float,
    S0: float,
    control: Optional[float] = None,
    est0: float = 0.0,
    est1: float = 100.0,
    N: int = N_PASOS_DEF,
) -> Resultado:
    if sistema not in SISTEMAS:
        raise ValueError(f"Sistema de unidades desconocido: {sistema}")
    sec.validar()
    if Q is None or Q <= 0:
        raise ValueError("El caudal debe ser > 0.")
    if n is None or n <= 0:
        raise ValueError("La rugosidad n debe ser > 0.")
    if N is None or N < 4:
        raise ValueError("El número de sub-pasos N debe ser ≥ 4.")
    if est1 <= est0:
        raise ValueError("La estación final debe ser mayor que la inicial.")

    g = G[sistema]
    k = K_MANNING[sistema]
    aviso = None

    # 1) tirantes de referencia
    Yc = tirante_critico(sec, Q, g)
    Ac = sec.props(Yc).A
    Yn = An = None
    if S0 > 0:
        try:
            Yn = tirante_normal(sec, Q, n, S0, k)
            An = sec.props(Yn).A
        except ValueError:
            ymax = sec.y_max()
            if ymax is not None:
                Yn = ymax
                An = sec.props(Yn).A
                aviso = "capacidad excedida (flujo a conducto lleno)"

    # 2) control y tipo de flujo
    if control is not None and control > 0:
        y_ctl = control
        p_ctl = sec.props(y_ctl)
        Dh = p_ctl.A / p_ctl.T if p_ctl.T > 0 else 0.0
        Fr_ctl = (Q / p_ctl.A) / math.sqrt(g * Dh) if Dh > 0 and p_ctl.A > 0 else 0.0
        flujo = "supercritical" if Fr_ctl > 1.0 else "subcritical"
    else:
        y_ctl = Yc
        flujo = "supercritical" if (Yn is not None and Yn < Yc) else "subcritical"

    subcritico = (flujo == "subcritical")
    target = Yn if Yn is not None else Yc

    if abs(target - y_ctl) <= 1e-9:
        raise ValueError("El tirante de control coincide con el tirante de referencia; no hay perfil que calcular.")

    # 3) marcha: subcrítico desde aguas abajo hacia arriba; supercrítico al revés
    est_ini = est1 if subcritico else est0
    est_fin = est0 if subcritico else est1
    if (est_fin - est_ini) * (1 if subcritico else -1) > 0:
        pass  # coherencia de extremos

    dy0 = (target - y_ctl) * FACTOR_PARADA / N
    y = y_ctl
    est = est_ini
    filas: List[Fila] = [_fila(sec, est, y, Q, g)]

    for _ in range(200000):
        y2 = y + 2.0 * dy0
        if (dy0 > 0 and y2 >= target) or (dy0 < 0 and y2 <= target):
            break
        ym = 0.5 * (y + y2)
        dx = (_dx_dy(sec, y, Q, n, S0, k, g)
              + 4.0 * _dx_dy(sec, ym, Q, n, S0, k, g)
              + _dx_dy(sec, y2, Q, n, S0, k, g)) / 6.0 * (y2 - y)
        est_next = est + dx
        y = y2
        filas.append(_fila(sec, est_next, y, Q, g))
        est = est_next
        if subcritico and est <= est_fin:
            break
        if (not subcritico) and est >= est_fin:
            break

    # 4) interpolar la última fila al extremo del canal si se pasó
    ult = filas[-1]
    if (subcritico and ult.estacion < est_fin) or ((not subcritico) and ult.estacion > est_fin):
        prev = filas[-2]
        denom = (ult.estacion - prev.estacion)
        frac = (est_fin - prev.estacion) / denom if denom != 0 else 0.0
        y_int = prev.y + frac * (ult.y - prev.y)
        filas[-1] = _fila(sec, est_fin, y_int, Q, g)

    perfil = _clasificar(sec, Yn, Yc, y_ctl, S0)

    return Resultado(
        forma=sec.forma, sistema=sistema, Q=Q, n=n, S0=S0,
        control=y_ctl, est0=est0, est1=est1,
        Yn=Yn, An=An, Yc=Yc, Ac=Ac,
        perfil=perfil, flujo=flujo, filas=filas, aviso=aviso,
    )

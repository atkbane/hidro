"""
calculos.py
===========
Funciones hidráulicas y lógica de negocio para cálculo de pérdidas de carga.
Unidades del Sistema Internacional (SI).
"""
import math
from dataclasses import dataclass, field
from typing import List

# ─────────────────────────────────────────────────────────────────────────────
#  CONSTANTES FÍSICAS
# ─────────────────────────────────────────────────────────────────────────────

VISCO_20C = 1.004e-6   # m²/s — viscosidad cinemática agua 20 °C
GAMMA     = 9.81       # kN/m³ — peso específico del agua
G         = 9.81       # m/s²  — aceleración de la gravedad

_DW_K = 8.0 / (math.pi ** 2 * G)   # ≈ 0.08265  [s²/m]

# ─────────────────────────────────────────────────────────────────────────────
#  PROPIEDADES GEOMÉTRICAS / CINEMÁTICAS
# ─────────────────────────────────────────────────────────────────────────────

def area_ci(d: float) -> float:
    """Área de sección circular. d en metros."""
    return math.pi * d ** 2 / 4

def vel_media(Q: float, d: float) -> float:
    """Velocidad media en tubería circular. Q [m³/s], d [m]."""
    a = area_ci(d)
    return Q / a if a > 0 else 0.0

# ─────────────────────────────────────────────────────────────────────────────
#  FACTOR DE FRICCIÓN — SWAMEE-JAIN (explícita)
# ─────────────────────────────────────────────────────────────────────────────

def f_swamee_jain(Q: float, d: float, k_mm: float,
                  visco: float = VISCO_20C) -> float:
    """
    Factor de fricción de Darcy-Weisbach por la aproximación Swamee-Jain.

    Q     : caudal [m³/s]
    d     : diámetro interior [m]
    k_mm  : rugosidad absoluta [mm]  ← siempre en milímetros
    visco : viscosidad cinemática [m²/s], por defecto agua a 20 °C
    """
    if d <= 0 or visco <= 0:
        return 0.0
    v  = vel_media(Q, d)
    Re = v * d / visco
    if Re < 1:
        return 0.0
    k_m    = k_mm / 1000                    # mm → m
    p_elem = k_m / (3.7 * d)
    s_elem = 5.74 / Re ** 0.9
    base   = math.log(p_elem + s_elem) ** 2
    return 1.325 / base if base > 0 else 0.0

# ─────────────────────────────────────────────────────────────────────────────
#  PÉRDIDAS POR FRICCIÓN
# ─────────────────────────────────────────────────────────────────────────────

def perdida_dw(Q: float, d: float, L: float, k_mm: float) -> float:
    """Darcy-Weisbach: hf = f · (8/(π²·g)) · Q² · L / D⁵"""
    if d <= 0:
        return 0.0
    f = f_swamee_jain(Q, d, k_mm)
    return _DW_K * f * Q ** 2 * L / d ** 5

def perdida_hw(Q: float, d: float, L: float, C: float) -> float:
    """Hazen-Williams: hf = 10.67 · L · Q^1.852 / (C^1.852 · D^4.87)"""
    if d <= 0 or C <= 0:
        return 0.0
    return 10.67 * L * Q ** 1.852 / (C ** 1.852 * d ** 4.87)

def perdida_ma(Q: float, d: float, L: float, n: float) -> float:
    """Manning: hf = 10.29 · n² · L · Q² / D^5.333"""
    if d <= 0:
        return 0.0
    return 10.29 * n ** 2 * L * Q ** 2 / d ** 5.333

# ─────────────────────────────────────────────────────────────────────────────
#  MODELO DE DATOS
# ─────────────────────────────────────────────────────────────────────────────

METODOS = [
    "Darcy-Weisbach",
    "Hazen-Williams",
    "Manning",
]

LABEL_COEF = {
    "Darcy-Weisbach": "k (mm)",
    "Hazen-Williams": "C",
    "Manning":        "n",
}

@dataclass
class Segmento:
    """Datos de un tramo de tubería."""
    L: float       # longitud [m]
    D: float       # diámetro interior [m]
    coef: float    # coeficiente de fricción (k_mm / C / n)

@dataclass
class SegmentoInfo:
    """Información de un segmento para mostrar en resultados."""
    idx: int
    D: float
    L: float
    V: float
    hf: float

@dataclass
class Resultado:
    """Resultado del cálculo completo."""
    titulo: str
    metodo: str
    segmentos: List[SegmentoInfo]
    hf_total: float
    h_entrada: float
    h_salida: float
    h_total: float
    potencia_kw: float

# ─────────────────────────────────────────────────────────────────────────────
#  ORQUESTADOR DE CÁLCULO
# ─────────────────────────────────────────────────────────────────────────────

class CalculoModel:
    """Valida y ejecuta el cálculo completo."""

    @staticmethod
    def calcular(
        titulo: str, Q: float, metodo: str,
        segmentos: List[Segmento],
        k_entrada: float, k_salida: float,
    ) -> Resultado:
        if Q <= 0:
            raise ValueError("El caudal debe ser > 0.")
        if not segmentos:
            raise ValueError("Debe haber al menos un segmento.")
        for i, seg in enumerate(segmentos, 1):
            if seg.L <= 0:
                raise ValueError(f"Segmento {i}: la longitud debe ser > 0.")
            if seg.D <= 0:
                raise ValueError(f"Segmento {i}: el diámetro debe ser > 0.")
            if seg.coef <= 0:
                raise ValueError(f"Segmento {i}: el coeficiente debe ser > 0.")

        fn_fric = {
            "Darcy-Weisbach": perdida_dw,
            "Hazen-Williams": perdida_hw,
            "Manning":        perdida_ma,
        }[metodo]

        infos: List[SegmentoInfo] = []
        hf_total = 0.0
        for i, seg in enumerate(segmentos):
            V = vel_media(Q, seg.D)
            hf = fn_fric(Q, seg.D, seg.L, seg.coef)
            infos.append(SegmentoInfo(idx=i + 1, D=seg.D, L=seg.L, V=V, hf=hf))
            hf_total += hf

        V_primero = infos[0].V
        V_ultimo  = infos[-1].V
        h_entrada = k_entrada * V_primero ** 2 / (2 * G)
        h_salida  = k_salida * V_ultimo ** 2 / (2 * G)

        h_total = hf_total + h_entrada + h_salida
        potencia_kw = GAMMA * Q * h_total

        return Resultado(
            titulo=titulo, metodo=metodo, segmentos=infos,
            hf_total=hf_total, h_entrada=h_entrada, h_salida=h_salida,
            h_total=h_total, potencia_kw=potencia_kw,
        )
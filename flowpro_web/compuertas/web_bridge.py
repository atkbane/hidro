"""
web_bridge.py — Compuertas de fondo
===================================
Puente Python ⇄ JavaScript para Pyodide de la herramienta *Underflow Gates*.
"""
from __future__ import annotations

from typing import Any, Dict, Optional

from calculos import resolver, Resultado, UNIDAD


def _num(d: Dict[str, Any], clave: str) -> Optional[float]:
    v = d.get(clave)
    if v is None or v == "":
        return None
    return float(v)


def _formatear(res: Resultado, U: Dict[str, str]) -> str:
    L, A, Q, V = U["L"], U["A"], U["Q"], U["V"]
    sep = "\u2500" * 46
    return "\n".join([
        "MEMORIA DE CÁLCULO — Compuerta de fondo",
        sep,
        f"  Sistema de unidades       : {res.sistema} ({L}, {Q})",
        sep,
        f"  {'Tirante aguas arriba (y₁)':<26}: {res.y1:>12.4f} {L}",
        f"  {'Ancho de la compuerta (b)':<26}: {res.b:>12.4f} {L}",
        f"  {'Apertura (a)':<26}: {res.a:>12.4f} {L}",
        f"  {'Coeficiente de descarga C':<26}: {res.C:>12.4f} —",
        sep,
        "  Ecuación: Q = C·b·a·√(2g·y₁)   ·   V = Q/(b·a)",
        f"  {'Área de la abertura (A=b·a)':<26}: {res.A:>12.4f} {A}",
        f"  {'CAUDAL (Q)':<26}: {res.Q:>12.6f} {Q}",
        f"  {'VELOCIDAD (V)':<26}: {res.V:>12.4f} {V}",
    ]) + "\n"


def ejecutar_simulacion(parametros: Dict[str, Any]) -> Dict[str, Any]:
    """Punto de entrada desde JavaScript vía Pyodide.

    ``parametros``: sistema, y1, b, a, C
    """
    try:
        sistema = str(parametros.get("sistema", "SI"))
        res = resolver(
            sistema=sistema,
            y1=_num(parametros, "y1"), b=_num(parametros, "b"),
            a=_num(parametros, "a"), C=_num(parametros, "C"),
        )
        U = UNIDAD[sistema]
        return {
            "exito": True,
            "sistema": res.sistema,
            "y1": res.y1, "b": res.b, "a": res.a, "C": res.C,
            "A": res.A, "Q": res.Q, "V": res.V,
            "unidades": U,
            "resultado_texto": _formatear(res, U),
        }
    except (ValueError, KeyError, TypeError) as ex:
        return {"exito": False, "error": str(ex)}
    except Exception as ex:  # noqa: BLE001
        return {"exito": False, "error": f"Error inesperado: {ex}"}

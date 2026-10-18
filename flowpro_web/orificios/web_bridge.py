"""
web_bridge.py — Orificios
=========================
Puente Python ⇄ JavaScript para Pyodide.

Expone ``ejecutar_simulacion(parametros)``: recibe los datos del orificio,
llama a ``calculos.resolver`` y devuelve un dict JSON-serializable con el
caudal y una memoria de cálculo formateada.
"""
from __future__ import annotations

from typing import Any, Dict, Optional

from calculos import resolver, Resultado, UNIDAD, COEF_TIPICOS


def _num(d: Dict[str, Any], clave: str) -> Optional[float]:
    v = d.get(clave)
    if v is None or v == "":
        return None
    return float(v)


def _formatear(res: Resultado, U: Dict[str, str]) -> str:
    L, A, Q, V = U["L"], U["A"], U["Q"], U["V"]
    sep = "\u2500" * 46
    medida = "Diámetro" if res.forma == "Circular" else "Lado"
    return "\n".join([
        "MEMORIA DE CÁLCULO — Orificio",
        sep,
        f"  Forma                     : {res.forma}",
        f"  Sistema de unidades       : {res.sistema} ({L}, {Q})",
        sep,
        f"  {'Carga sobre el orificio (H)':<26}: {res.H:>12.4f} {L}",
        f"  {medida + ' del orificio':<26}: {res.tamano:>12.4f} {L}",
        f"  {'Coeficiente de descarga (C)':<26}: {res.C:>12.4f} —",
        sep,
        "Resultados:",
        f"  {'Área del orificio (A)':<26}: {res.A:>12.6f} {A}",
        f"  {'Velocidad ideal √(2gH)':<26}: {res.V_ideal:>12.4f} {V}",
        f"  {'Velocidad de descarga V':<26}: {res.V:>12.4f} {V}",
        f"  {'CAUDAL (Q = C·A·√(2gH))':<26}: {res.Q:>12.6f} {Q}",
    ]) + "\n"


def ejecutar_simulacion(parametros: Dict[str, Any]) -> Dict[str, Any]:
    """Punto de entrada desde JavaScript vía Pyodide.

    ``parametros``:
        - sistema: 'SI' | 'English'
        - forma:   'Circular' | 'Square'
        - tamano:  diámetro o lado (float)
        - C:       coeficiente de descarga
        - H:       carga sobre el orificio
    """
    try:
        sistema = str(parametros.get("sistema", "SI"))
        forma = str(parametros.get("forma", "Circular"))
        res = resolver(
            sistema=sistema,
            forma=forma,
            tamano=_num(parametros, "tamano"),
            C=_num(parametros, "C"),
            H=_num(parametros, "H"),
        )
        U = UNIDAD[sistema]
        return {
            "exito": True,
            "sistema": res.sistema,
            "forma": res.forma,
            "tamano": res.tamano,
            "C": res.C,
            "H": res.H,
            "A": res.A,
            "Q": res.Q,
            "V": res.V,
            "V_ideal": res.V_ideal,
            "unidades": U,
            "resultado_texto": _formatear(res, U),
        }
    except (ValueError, KeyError, TypeError) as ex:
        return {"exito": False, "error": str(ex)}
    except Exception as ex:  # noqa: BLE001
        return {"exito": False, "error": f"Error inesperado: {ex}"}

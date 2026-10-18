"""
web_bridge.py
=============
Puente Python ⇄ JavaScript para Pyodide.

Expone ``ejecutar_simulacion(parametros)``: recibe un diccionario con los datos
del cálculo, llama a ``calculos.resolver`` y devuelve un diccionario
JSON-serializable con los resultados y una memoria de cálculo formateada.

Equivale a la herramienta *Depth, Flowrate, Slope, and Roughness* de Flow Pro 2.1.
"""
from __future__ import annotations

from typing import Any, Dict, Optional

from calculos import (
    Seccion, resolver, Resultado, UNIDAD,
    TRAPEZOIDAL, CIRCULAR, PROFUNDIDAD, CAUDAL, PENDIENTE, RUGOSIDAD,
)

_INCOGNITA_TXT = {
    PROFUNDIDAD: "Tirante normal (y)",
    CAUDAL:      "Caudal (Q)",
    PENDIENTE:   "Pendiente de fondo (S)",
    RUGOSIDAD:   "Rugosidad de Manning (n)",
}


def _num(d: Dict[str, Any], clave: str) -> Optional[float]:
    v = d.get(clave)
    if v is None or v == "":
        return None
    return float(v)


def _formatear(
    res: Resultado, sec: Seccion, unidades: Dict[str, str],
) -> str:
    """Memoria de cálculo en texto monoespaciado."""
    L, A, Q, V = unidades["L"], unidades["A"], unidades["Q"], unidades["V"]
    sep = "\u2500" * 46

    def fila(etq: str, val: float, u: str, nd: int = 4) -> str:
        return f"  {etq:<26}: {val:>12.{nd}f} {u}"

    geom = []
    if sec.forma == TRAPEZOIDAL:
        geom.append(f"  {'Ancho de solera (b)':<26}: {sec.b:>12.4f} {L}")
        geom.append(f"  {'Talud H:V (m)':<26}: {sec.m:>12.4f} —")
    elif sec.forma == CIRCULAR:
        geom.append(f"  {'Diámetro (D)':<26}: {sec.D:>12.4f} {L}")

    lineas = [
        "MEMORIA DE CÁLCULO — Manning (canal abierto)",
        sep,
        f"  Sección                   : {res.forma}",
        f"  Sistema de unidades       : {res.sistema} ({L}, {Q})",
        f"  Incógnita                 : {_INCOGNITA_TXT[res.incognita]}",
        sep,
        "Datos:",
        *geom,
        f"  Caudal (Q)                : {res.Q:>12.4f} {Q}",
        f"  Tirante (y)               : {res.y:>12.4f} {L}",
        f"  Pendiente de fondo (S)    : {res.S:>12.6f} m/m",
        f"  Rugosidad de Manning (n)  : {res.n:>12.4f} —",
        sep,
        "Resultados hidráulicos:",
        fila("Área mojada (A)", res.A, A),
        fila("Perímetro mojado (P)", res.P, L),
        fila("Radio hidráulico (R=A/P)", res.R, L),
        fila("Ancho superior (T)", res.T, L),
        fila("Velocidad media (V=Q/A)", res.V, V),
        f"  {'Número de Froude (Fr)':<26}: {res.Fr:>12.4f} —  ({res.regimen})",
    ]
    return "\n".join(lineas) + "\n"


def ejecutar_simulacion(parametros: Dict[str, Any]) -> Dict[str, Any]:
    """Punto de entrada desde JavaScript vía Pyodide.

    ``parametros`` debe contener:
        - sistema:   'SI' | 'English'
        - forma:     'Trapezoidal' | 'Circular'
        - incognita: 'profundidad' | 'caudal' | 'pendiente' | 'rugosidad'
        - y, Q, S, n, b, m, D  (float; solo los que apliquen)

    Devuelve un dict serializable con ``exito`` y, o bien ``error``, o bien los
    resultados + ``resultado_texto``.
    """
    try:
        sistema = str(parametros.get("sistema", "SI"))
        forma = str(parametros.get("forma", TRAPEZOIDAL))
        incognita = str(parametros.get("incognita", PROFUNDIDAD))

        sec = Seccion(
            forma=forma,
            b=_num(parametros, "b"),
            m=_num(parametros, "m"),
            D=_num(parametros, "D"),
        )

        res = resolver(
            sec, incognita, sistema=sistema,
            y=_num(parametros, "y"),
            Q=_num(parametros, "Q"),
            S=_num(parametros, "S"),
            n=_num(parametros, "n"),
        )

        unidades = UNIDAD[sistema]

        return {
            "exito": True,
            "forma": res.forma,
            "sistema": res.sistema,
            "incognita": res.incognita,
            "y": res.y,
            "Q": res.Q,
            "S": res.S,
            "n": res.n,
            "V": res.V,
            "A": res.A,
            "P": res.P,
            "T": res.T,
            "R": res.R,
            "Fr": res.Fr,
            "regimen": res.regimen,
            "unidades": unidades,
            "resultado_texto": _formatear(res, sec, unidades),
        }

    except (ValueError, KeyError, TypeError) as ex:
        return {"exito": False, "error": str(ex)}
    except Exception as ex:  # noqa: BLE001
        return {"exito": False, "error": f"Error inesperado: {ex}"}

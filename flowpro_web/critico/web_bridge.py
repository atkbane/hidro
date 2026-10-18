"""
web_bridge.py — Tirante y pendiente crítica
===========================================
Puente Python ⇄ JavaScript para Pyodide de la herramienta
*Critical Depth and Slope*.
"""
from __future__ import annotations

from typing import Any, Dict, Optional

from calculos import Seccion, resolver, Resultado, UNIDAD, TRAPEZOIDAL


def _num(d: Dict[str, Any], clave: str) -> Optional[float]:
    v = d.get(clave)
    if v is None or v == "":
        return None
    return float(v)


def _formatear(res: Resultado, sec: Seccion, U: Dict[str, str]) -> str:
    L, A, Q, V = U["L"], U["A"], U["Q"], U["V"]
    sep = "\u2500" * 46
    geom = []
    if sec.forma == TRAPEZOIDAL:
        geom.append(f"  {'Ancho de solera (b)':<26}: {sec.b:>12.4f} {L}")
        geom.append(f"  {'Talud H:V (m)':<26}: {sec.m:>12.4f} —")
    else:
        geom.append(f"  {'Diámetro (D)':<26}: {sec.D:>12.4f} {L}")
    return "\n".join([
        "MEMORIA DE CÁLCULO — Régimen crítico",
        sep,
        f"  Sección                   : {res.forma}",
        f"  Sistema de unidades       : {res.sistema} ({L}, {Q})",
        sep,
        "Datos:",
        *geom,
        f"  {'Caudal (Q)':<26}: {res.Q:>12.4f} {Q}",
        f"  {'Rugosidad de Manning (n)':<26}: {res.n:>12.4f} —",
        sep,
        "Resultados:",
        f"  {'TIRANTE CRÍTICO (Yc)':<26}: {res.Yc:>12.4f} {L}",
        f"  {'Área crítica (Ac)':<26}: {res.Ac:>12.4f} {A}",
        f"  {'Ancho superior crítico (Tc)':<26}: {res.Tc:>12.4f} {L}",
        f"  {'Perímetro mojado crítico (Pc)':<26}: {res.Pc:>12.4f} {L}",
        f"  {'Radio hidráulico crítico (Rc)':<26}: {res.Rc:>12.4f} {L}",
        f"  {'Velocidad crítica (Vc)':<26}: {res.Vc:>12.4f} {V}",
        f"  {'PENDIENTE CRÍTICA (Sc)':<26}: {res.Sc:>12.6f} m/m",
        f"  {'Número de Froude':<26}: {1.0:>12.4f} —  (crítico)",
    ]) + "\n"


def ejecutar_simulacion(parametros: Dict[str, Any]) -> Dict[str, Any]:
    """Punto de entrada desde JavaScript vía Pyodide.

    ``parametros``:
        - sistema: 'SI' | 'English'
        - forma:   'Trapezoidal' | 'Circular'
        - Q, n, y geometría (b, m / D)
    """
    try:
        sistema = str(parametros.get("sistema", "SI"))
        forma = str(parametros.get("forma", TRAPEZOIDAL))
        sec = Seccion(forma=forma, b=_num(parametros, "b"),
                      m=_num(parametros, "m"), D=_num(parametros, "D"))
        res = resolver(sec, sistema=sistema,
                       Q=_num(parametros, "Q"), n=_num(parametros, "n"))
        U = UNIDAD[sistema]
        return {
            "exito": True,
            "forma": res.forma, "sistema": res.sistema,
            "Q": res.Q, "n": res.n,
            "Yc": res.Yc, "Ac": res.Ac, "Tc": res.Tc, "Pc": res.Pc,
            "Rc": res.Rc, "Vc": res.Vc, "Sc": res.Sc,
            "unidades": U,
            "resultado_texto": _formatear(res, sec, U),
        }
    except (ValueError, KeyError, TypeError) as ex:
        return {"exito": False, "error": str(ex)}
    except Exception as ex:  # noqa: BLE001
        return {"exito": False, "error": f"Error inesperado: {ex}"}

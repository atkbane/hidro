"""
web_bridge.py — Vertederos
==========================
Puente Python ⇄ JavaScript para Pyodide de la herramienta *Weirs*.
"""
from __future__ import annotations

from typing import Any, Dict, Optional

from calculos import resolver, Resultado, UNIDAD, TRIANGULAR


def _num(d: Dict[str, Any], clave: str) -> Optional[float]:
    v = d.get(clave)
    if v is None or v == "":
        return None
    return float(v)


def _formatear(res: Resultado, U: Dict[str, str]) -> str:
    L, Q = U["L"], U["Q"]
    sep = "\u2500" * 46
    if res.tipo == TRIANGULAR:
        ecu = f"  Q = C·(8/15)·√(2g)·tan(θ/2)·H^{res.n:g}"
        geom = f"  {'Ángulo del V (θ)':<26}: {res.angulo:>12.4f} °"
    else:
        ecu = f"  Q = C·(2/3)·√(2g)·L·H^{res.n:g}"
        geom = f"  {'Longitud de cresta (L)':<26}: {res.L:>12.4f} {L}"
    extra = " (cresta ancha)" if res.broad_crested else ""
    lines = [
        f"MEMORIA DE CÁLCULO — Vertedero{extra}",
        sep,
        f"  Tipo                      : {res.tipo}",
        f"  Régimen                   : {'sumergido' if res.sumergido else 'libre'}",
        f"  Sistema de unidades       : {res.sistema} ({L}, {Q})",
        sep,
        f"  {geom.strip()}",
        f"  {'Carga aguas arriba (H₁)':<26}: {res.H:>12.4f} {L}",
    ]
    if res.sumergido:
        lines.append(f"  {'Carga aguas abajo (H₂)':<26}: {res.H2:>12.4f} {L}")
    lines += [
        f"  {'Coeficiente de descarga C':<26}: {res.C:>12.4f} —",
        sep,
        f"  {'Ecuación':<26}: {ecu.strip()}",
    ]
    if res.sumergido:
        lines.append(f"  {'Q libre (H₁)':<26}: {res.Qf:>12.6f} {Q}")
        lines.append(f"  {'Corrección Villemonte (n)':<26}: {res.n:>12.2f} —")
    lines.append(f"  {'CAUDAL (Q)':<26}: {res.Q:>12.6f} {Q}")
    return "\n".join(lines) + "\n"


def ejecutar_simulacion(parametros: Dict[str, Any]) -> Dict[str, Any]:
    """Punto de entrada desde JavaScript vía Pyodide.

    ``parametros``:
        - sistema: 'SI' | 'English'
        - tipo: 'Rectangular' | 'Triangular' | 'Cipolletti'
        - sumergido, broad_crested: bool
        - L, H, H2, angulo, C
    """
    try:
        sistema = str(parametros.get("sistema", "SI"))
        tipo = str(parametros.get("tipo", "Rectangular"))
        res = resolver(
            sistema=sistema, tipo=tipo,
            sumergido=bool(parametros.get("sumergido", False)),
            broad_crested=bool(parametros.get("broad_crested", False)),
            L=_num(parametros, "L"), H=_num(parametros, "H"),
            H2=_num(parametros, "H2"), angulo=_num(parametros, "angulo"),
            C=_num(parametros, "C"),
        )
        U = UNIDAD[sistema]
        return {
            "exito": True,
            "sistema": res.sistema, "tipo": res.tipo,
            "sumergido": res.sumergido, "broad_crested": res.broad_crested,
            "C": res.C, "L": res.L, "H": res.H, "H2": res.H2, "angulo": res.angulo,
            "Qf": res.Qf, "Q": res.Q, "n": res.n,
            "unidades": U,
            "resultado_texto": _formatear(res, U),
        }
    except (ValueError, KeyError, TypeError) as ex:
        return {"exito": False, "error": str(ex)}
    except Exception as ex:  # noqa: BLE001
        return {"exito": False, "error": f"Error inesperado: {ex}"}

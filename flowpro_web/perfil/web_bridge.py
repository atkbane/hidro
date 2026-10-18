"""
web_bridge.py — Perfil de superficie libre
==========================================
Puente Python ⇄ JavaScript para Pyodide de la herramienta *Water Surface Profile*.
"""
from __future__ import annotations

from typing import Any, Dict, Optional

from calculos import (
    Seccion, resolver_perfil, Resultado, UNIDAD, N_PASOS_DEF, TRAPEZOIDAL,
)


def _num(d: Dict[str, Any], clave: str) -> Optional[float]:
    v = d.get(clave)
    if v is None or v == "":
        return None
    return float(v)


def _formatear(res: Resultado, sec: Seccion, U: Dict[str, str], froude_modo: str) -> str:
    L, A, Q, V = U["L"], U["A"], U["Q"], U["V"]
    sep = "\u2500" * 78
    linea = "\u2500" * 46

    geom = []
    if sec.forma == TRAPEZOIDAL:
        geom.append(f"  {'Ancho de solera (b)':<26}: {sec.b:>12.4f} {L}")
        geom.append(f"  {'Talud H:V (m)':<26}: {sec.m:>12.4f} —")
    else:
        geom.append(f"  {'Diámetro (D)':<26}: {sec.D:>12.4f} {L}")

    cab = [
        "PERFIL DE SUPERFICIE LIBRE — flujo gradualmente variado",
        sep,
        f"  Sección                   : {res.forma}",
        f"  Sistema de unidades       : {res.sistema} ({L}, {Q})",
        sep,
        "Datos:",
        *geom,
        f"  {'Caudal (Q)':<26}: {res.Q:>12.4f} {Q}",
        f"  {'Rugosidad de Manning (n)':<26}: {res.n:>12.5f} —",
        f"  {'Pendiente de fondo (S0)':<26}: {res.S0:>12.6f} m/m",
        f"  {'Tirante de control':<26}: {res.control:>12.4f} {L}",
        f"  {'Estación inicial':<26}: {res.est0:>12.3f} {L}",
        f"  {'Estación final':<26}: {res.est1:>12.3f} {L}",
        sep,
        "Resultados:",
        f"  {'Tirante normal (Yn)':<26}: {(res.Yn if res.Yn is not None else float('nan')):>12.4f} {L}",
        f"  {'Área normal (An)':<26}: {(res.An if res.An is not None else float('nan')):>12.4f} {A}",
        f"  {'Tirante crítico (Yc)':<26}: {res.Yc:>12.4f} {L}",
        f"  {'Área crítica (Ac)':<26}: {res.Ac:>12.4f} {A}",
        f"  {'Tipo de perfil':<26}: {res.perfil:>12}",
        f"  {'Tipo de flujo':<26}: {res.flujo:>12}",
    ]
    if res.aviso:
        cab.append(f"  AVISO: {res.aviso}")
    cab.append(linea)

    col_fr = "Fr²" if froude_modo == "Fr2" else "Fr"
    enc = (f"{'Estación':>10} {'Tirante':>9} {'Energía':>9} {'Área':>9} "
           f"{'Veloc.':>9} {'Ancho sup':>10} {'Momentum':>10} {col_fr:>8} "
           f"{'c.vel':>8} {'Radio':>8} {'Perí.':>8}")
    filas_txt = []
    for f in res.filas:
        frv = f.Fr2 if froude_modo == "Fr2" else f.Fr
        filas_txt.append(
            f"{f.estacion:>10.3f} {f.y:>9.4f} {f.E:>9.4f} {f.A:>9.4f} "
            f"{f.V:>9.4f} {f.T:>10.4f} {f.M:>10.4f} {frv:>8.4f} "
            f"{f.hv:>8.4f} {f.R:>8.4f} {f.P:>8.4f}"
        )
    enc2 = (f"{'[' + L + ']':>10} {'[' + L + ']':>9} {'[' + L + ']':>9} {'[' + A + ']':>9} "
            f"{'[' + V + ']':>9} {'[' + L + ']':>10} {'[m³]':>10} {'[-]':>8} "
            f"{'[' + L + ']':>8} {'[' + L + ']':>8} {'[' + L + ']':>8}")

    return "\n".join(cab + [enc, enc2, *filas_txt]) + "\n"


def ejecutar_simulacion(parametros: Dict[str, Any]) -> Dict[str, Any]:
    """Punto de entrada desde JavaScript vía Pyodide.

    ``parametros``:
        - sistema: 'SI' | 'English'
        - forma:   'Trapezoidal' | 'Circular'
        - Q, n, S0, control (opcional), est0, est1, N
        - b, m / D
        - froude_modo: 'Fr' | 'Fr2'   (columna a exponer)
    """
    try:
        sistema = str(parametros.get("sistema", "SI"))
        forma = str(parametros.get("forma", TRAPEZOIDAL))
        froude_modo = str(parametros.get("froude_modo", "Fr"))
        control = _num(parametros, "control")
        N = parametros.get("N")
        N = int(N) if N not in (None, "") else N_PASOS_DEF

        sec = Seccion(forma=forma, b=_num(parametros, "b"),
                      m=_num(parametros, "m"), D=_num(parametros, "D"))

        res = resolver_perfil(
            sec, sistema=sistema,
            Q=_num(parametros, "Q"), n=_num(parametros, "n"), S0=_num(parametros, "S0"),
            control=(control if (control is not None and control > 0) else None),
            est0=_num(parametros, "est0") if _num(parametros, "est0") is not None else 0.0,
            est1=_num(parametros, "est1") if _num(parametros, "est1") is not None else 100.0,
            N=N,
        )
        U = UNIDAD[sistema]

        filas = [
            {"estacion": f.estacion, "y": f.y, "E": f.E, "A": f.A, "V": f.V,
             "T": f.T, "M": f.M, "Fr": f.Fr, "Fr2": f.Fr2, "hv": f.hv, "R": f.R, "P": f.P}
            for f in res.filas
        ]

        return {
            "exito": True,
            "forma": res.forma, "sistema": res.sistema,
            "Q": res.Q, "n": res.n, "S0": res.S0, "control": res.control,
            "est0": res.est0, "est1": res.est1,
            "Yn": res.Yn, "An": res.An, "Yc": res.Yc, "Ac": res.Ac,
            "perfil": res.perfil, "flujo": res.flujo, "aviso": res.aviso,
            "filas": filas, "unidades": U,
            "resultado_texto": _formatear(res, sec, U, froude_modo),
        }
    except (ValueError, KeyError, TypeError) as ex:
        return {"exito": False, "error": str(ex)}
    except Exception as ex:  # noqa: BLE001
        return {"exito": False, "error": f"Error inesperado: {ex}"}

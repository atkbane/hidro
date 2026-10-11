"""
web_main.py
===========
Función ejecutar_simulacion para usar desde Pyodide en el navegador.
Recibe un dict con parámetros, llama a CalculoModel.calcular() y
devuelve un dict JSON-serializable con los resultados.
"""
import json
import sys
from typing import Any, Dict, List

# El módulo calculos.py debe estar en el sistema de archivos virtual de Pyodide
from calculos import (
    METODOS, LABEL_COEF, Segmento, SegmentoInfo, Resultado, CalculoModel,
)


def _formatear_resultado_texto(res: Resultado) -> str:
    """Mismo formateo que la versión PySide."""
    sep = "\u2500" * 44

    cab = f"{'#':>3}  {'L (m)':>7}  {'D (m)':>7}  {'V (m/s)':>8}  {'hf (m)':>8}"
    lin = "\u2500" * 40
    filas = "\n".join(
        f"{s.idx:>3}  {s.L:>7.2f}  {s.D:>7.3f}  {s.V:>8.2f}  {s.hf:>8.4f}"
        for s in res.segmentos
    )

    pot = res.potencia_kw
    pot_str = f"{pot/1000:.2f} MW" if pot >= 1000 else f"{pot:.2f} kW"

    return (
        f"Proyecto : {res.titulo}\n"
        f"Método   : {res.metodo}\n"
        f"{sep}\n"
        f"Segmentación:\n"
        f"{cab}\n"
        f"{lin}\n"
        f"{filas}\n"
        f"{sep}\n"
        f"Perd. fricción       : {res.hf_total:>8.2f} m\n"
        f"Perd. entrada        : {res.h_entrada:>8.2f} m\n"
        f"Perd. salida         : {res.h_salida:>8.2f} m\n"
        f"{sep}\n"
        f"TOTAL PÉRDIDAS       : {res.h_total:>8.2f} m\n"
        f"Potencia perdida     : {pot_str:>8}\n"
    )


def ejecutar_simulacion(parametros: Dict[str, Any]) -> Dict[str, Any]:
    """
    Punto de entrada desde JavaScript vía Pyodide.

    ``parametros`` debe contener:
        - titulo: str
        - Q: float
        - metodo: str (debe coincidir con METODOS)
        - segmentos: list[dict]  cada dict con keys 'L', 'D', 'coef'
        - k_entrada: float
        - k_salida: float

    Retorna un dict serializable con:
        exito: bool
        y en caso de éxito:
            titulo, metodo, segmentos (lista con idx, D, L, V, hf),
            hf_total, h_entrada, h_salida, h_total, potencia_kw,
            resultado_texto (str formateado)
        en caso de error:
            exito: False, error: str
    """
    try:
        titulo = parametros.get("titulo", "").strip() or "—"
        Q = float(parametros["Q"])
        metodo = str(parametros["metodo"])
        k_entrada = float(parametros.get("k_entrada", 0.5))
        k_salida = float(parametros.get("k_salida", 1.0))

        segs_data = parametros.get("segmentos", [])
        if not segs_data:
            return {"exito": False, "error": "No hay segmentos definidos."}

        segmentos: List[Segmento] = []
        for i, sd in enumerate(segs_data, 1):
            L = float(sd["L"])
            D = float(sd["D"])
            coef = float(sd["coef"])
            segmentos.append(Segmento(L=L, D=D, coef=coef))

        res: Resultado = CalculoModel.calcular(
            titulo=titulo, Q=Q, metodo=metodo,
            segmentos=segmentos,
            k_entrada=k_entrada, k_salida=k_salida,
        )

        segmentos_out: List[Dict[str, Any]] = [
            {
                "idx": s.idx,
                "D": s.D,
                "L": s.L,
                "V": s.V,
                "hf": s.hf,
            }
            for s in res.segmentos
        ]

        return {
            "exito": True,
            "titulo": res.titulo,
            "metodo": res.metodo,
            "segmentos": segmentos_out,
            "hf_total": res.hf_total,
            "h_entrada": res.h_entrada,
            "h_salida": res.h_salida,
            "h_total": res.h_total,
            "potencia_kw": res.potencia_kw,
            "resultado_texto": _formatear_resultado_texto(res),
        }

    except (ValueError, KeyError, TypeError) as ex:
        return {"exito": False, "error": str(ex)}
    except Exception as ex:
        return {"exito": False, "error": f"Error inesperado: {ex}"}
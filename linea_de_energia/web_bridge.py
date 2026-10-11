"""
Puente Pyodide para bernoulli — versión web.

Expone una función única ejecutar_cadena() que recibe la definición
de una cadena de nodos y retorna los resultados de cada paso.
"""

from core import (
    nodo_crear_seccion, nodo_transicion, nodo_tranquilizadores,
    nodo_rejillas_serie, nodo_perdida,
)


def _formatear_seccion(d):
    regimen = d.get("regimen", "")
    color = {
        "Subcrítico": "#2563eb",
        "Supercrítico": "#dc2626",
        "Crítico": "#d97706",
    }.get(regimen, "#334155")

    lineas = [
        f"── {d['nombre']} ──",
        f"  Q: {d['Q']:.2f} m³/s | b: {d['b']:.2f} m | y: {d['y']:.2f} m | z: {d['z']:.2f} m",
        f"  Fr: {d['Fr']:.2f} ({regimen}) | v: {d['vel']:.2f} m/s | hv: {d['hv']:.2f} m",
        f"  N.Agua: {d['n_agua']:.2f} m | N.Energía: {d['n_energia']:.2f} m",
    ]
    if d.get("hl", 0) > 0:
        lineas.append(f"  hL tramo: {d['hl']:.2f} m")
    return "\n".join(lineas), color


def ejecutar_cadena(nodos):
    """
    Procesa una cadena de nodos secuencialmente.

    Parameters
    ----------
    nodos : list[dict]
        Cada dict tiene 'tipo' y los parámetros específicos del tipo.

    Returns
    -------
    dict
        { "ok": True, "resultados": [...], "texto": str }
        o
        { "ok": False, "error": str }
    """
    try:
        resultados = []
        secciones = []  # todas las secciones calculadas

        for i, nodo in enumerate(nodos):
            tipo = nodo["tipo"]
            nombre = nodo.get("nombre", f"Seccion {i + 1}")

            if tipo == "Sección Inicial":
                sec = nodo_crear_seccion(
                    Q=nodo["Q"], b=nodo["b"], y=nodo["y"], z=nodo["z"],
                    nombre=nombre,
                )

            elif tipo == "Transición":
                prev = secciones[-1]
                Q_opt = nodo.get("Q_opt")
                if Q_opt is not None:
                    Q_opt = float(Q_opt)
                sec = nodo_transicion(
                    prev, nodo["b_nuevo"], nodo["z_nuevo"],
                    nodo["tipo_trans"], Q=Q_opt, nombre=nombre,
                )

            elif tipo == "Tranquilizadores":
                if len(secciones) < 2:
                    return {"ok": False, "error": f"Paso {i + 1}: se requieren al menos 2 nodos previos para Tranquilizadores."}
                sec_abajo = secciones[-1]
                sec_arriba = secciones[-2]
                sec = nodo_tranquilizadores(
                    sec_abajo, sec_arriba,
                    longitud=nodo["longitud"],
                    c=nodo["c"], e=nodo["e"], s=nodo["s"],
                    ang=nodo["ang"], nombre=nombre,
                )

            elif tipo == "Rejillas Serie":
                prev = secciones[-1]
                rejillas = nodo.get("rejillas", [])
                sec = nodo_rejillas_serie(prev, rejillas, nombre=nombre)

            elif tipo == "Pérdida Directa":
                prev = secciones[-1]
                sec = nodo_perdida(prev, nodo["delta_y"], nombre=nombre)

            else:
                return {"ok": False, "error": f"Paso {i + 1}: tipo '{tipo}' no reconocido."}

            secciones.append(sec)
            d = sec.to_dict()
            texto, color = _formatear_seccion(d)
            resultados.append({
                "paso": i + 1,
                "tipo": tipo,
                "nombre": nombre,
                "datos": d,
                "texto": texto,
                "color": color,
            })

        # Bloque de texto completo
        bloques = []
        for r in resultados:
            bloques.append(r["texto"])
        texto_completo = "\n\n".join(bloques)

        return {
            "ok": True,
            "resultados": resultados,
            "texto": texto_completo,
        }

    except ValueError as ex:
        return {"ok": False, "error": str(ex)}
    except Exception as ex:
        return {"ok": False, "error": f"Error inesperado: {ex}"}

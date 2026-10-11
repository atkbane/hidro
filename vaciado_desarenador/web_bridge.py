"""
Módulo para ejecutar la simulación de vaciado de desarenador desde Pyodide.
Convierte los resultados de numpy a listas nativas para JSON.
"""
import calculos
import numpy as np


def ejecutar_simulacion(parametros):
    """
    Ejecuta la simulación con los parámetros dados (dict) y devuelve
    un dict con todos los resultados serializables a JSON.
    """
    try:
        # Extraer parámetros con validación
        L = float(parametros['L'])
        W = float(parametros['W'])
        B = float(parametros['B'])
        d = float(parametros['d'])
        t_open = float(parametros['t_open'])
        h0 = float(parametros['h0'])
        h_parada = float(parametros['h_parada'])
        Cd_orif = float(parametros['Cd_orif'])
        Cd_weir = float(parametros['Cd_weir'])
        g = float(parametros.get('g', 9.81))
        t_max = float(parametros.get('t_max', 3600))
        n_puntos = int(parametros.get('n_puntos', 2000))
        max_step = float(parametros.get('max_step', 5.0))

        # Validar valores positivos
        for nombre, val in [
            ('L', L), ('W', W), ('B', B), ('d', d),
            ('t_open', t_open), ('h0', h0), ('Cd_orif', Cd_orif),
            ('Cd_weir', Cd_weir), ('g', g), ('t_max', t_max),
            ('n_puntos', n_puntos), ('max_step', max_step)
        ]:
            if val <= 0:
                raise ValueError(f"El parámetro {nombre} debe ser positivo.")

        if h_parada < 0:
            raise ValueError("h_parada debe ser >= 0.")

        # Validar restricciones físicas/geométricas
        if B > W:
            raise ValueError(
                f"Ancho de compuerta B={B} m excede el ancho del desarenador W={W} m."
            )
        if h_parada >= h0:
            raise ValueError(
                f"Nivel de parada h_parada={h_parada} m debe ser menor que el nivel inicial h0={h0} m."
            )

        # Ejecutar simulación
        resultado = calculos.simular_vaciado(
            L, W, B, d, t_open, h0, h_parada,
            Cd_orif, Cd_weir, g, t_max, n_puntos, max_step
        )

        # Convertir arrays numpy a listas
        t_res = resultado['t_res'].tolist()
        h_res = resultado['h_res'].tolist()
        q_res = resultado['q_res'].tolist()

        # Calcular caudal máximo
        Q_max = float(max(q_res))

        # Convertir índices de transición a lista nativa
        indices_transicion = [int(i) for i in resultado['indices_transicion']]

        return {
            'exito': True,
            't_res': t_res,
            'h_res': h_res,
            'q_res': q_res,
            't_parada': float(resultado['t_parada']),
            't_apertura_total': float(resultado['t_apertura_total']),
            'indices_transicion': indices_transicion,
            'Q_max': Q_max,
            'parametros': resultado['parametros']
        }

    except Exception as e:
        return {
            'exito': False,
            'error': str(e)
        }
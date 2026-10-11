"""
Módulo de cálculos para la simulación de vaciado de desarenador.
Contiene las funciones de caudal y el solver.
"""
import numpy as np
from scipy.integrate import solve_ivp


def calcular_caudal(t, h, B, d, t_open, tasa_apertura, Cd_orif, Cd_weir, g, k_transicion=20.0):
    """
    Calcula el caudal de salida según el régimen de flujo,
    con transición suave entre orificio y vertedero (sigmoide).

    Parameters
    ----------
    t : float
        Tiempo desde el inicio de la apertura [s].
    h : float
        Tirante de agua sobre el fondo del desarenador [m].
    B : float
        Ancho de la compuerta [m].
    d : float
        Apertura máxima de la compuerta [m].
    t_open : float
        Tiempo de apertura total de la compuerta [s].
    tasa_apertura : float
        Velocidad lineal de apertura de la compuerta [m/s] = d / t_open.
    Cd_orif : float
        Coeficiente de descarga en régimen de orificio.
    Cd_weir : float
        Coeficiente de descarga en régimen de vertedero.
    g : float
        Aceleración de gravedad [m/s²].
    k_transicion : float, default 20.0
        Factor de pendiente de la sigmoide. k=20 produce una transición
        en ~15% de la apertura. Hardcodeado por diseño (no es parámetro
        de proyecto). Ver marco_teorico.md §3.3.
    """
    a_t = tasa_apertura * t if t < t_open else d

    if h <= 0 or a_t <= 0:
        return 0.0

    h_efectiva = h - (a_t / 2)
    if h_efectiva < 0:
        h_efectiva = 0.0
    Q_orificio = Cd_orif * (B * a_t) * np.sqrt(2 * g * h_efectiva)

    Q_vertedero = (2 / 3) * Cd_weir * B * np.sqrt(2 * g) * (h ** 1.5)

    x = (h - a_t) / a_t if a_t > 0 else 0
    w = 1.0 / (1.0 + np.exp(-k_transicion * x))

    Q = w * Q_orificio + (1.0 - w) * Q_vertedero

    return Q


def simular_vaciado(L, W, B, d, t_open, h0, h_parada, Cd_orif, Cd_weir,
                     g=9.81, t_max=3600, n_puntos=2000, max_step=5.0):
    """
    Ejecuta la simulación completa de vaciado del desarenador.

    El modelo asume área superficial constante A = L·W (paredes verticales).
    Desarenadores con bisel inferior requieren A = A(h) y otra formulación.
    Ver marco_teorico.md §2.
    """
    if B > W:
        raise ValueError(
            f"Ancho de compuerta B={B} m excede el ancho del desarenador W={W} m."
        )
    if h_parada >= h0:
        raise ValueError(
            f"Nivel de parada h_parada={h_parada} m debe ser menor que el nivel inicial h0={h0} m."
        )

    A_res = L * W
    tasa_apertura = d / t_open if t_open > 0 else 0

    def ecuacion_diferencial(t, h):
        Q_out = calcular_caudal(t, h[0], B, d, t_open, tasa_apertura,
                                Cd_orif, Cd_weir, g)
        dhdt = -Q_out / A_res
        return dhdt

    def vaciado_completo(t, h):
        return h[0] - h_parada

    vaciado_completo.terminal = True
    vaciado_completo.direction = -1

    t_span = (0, t_max)
    t_eval = np.linspace(0, t_max, n_puntos)

    sol = solve_ivp(
        ecuacion_diferencial,
        t_span,
        [h0],
        t_eval=t_eval,
        events=vaciado_completo,
        method='RK45',
        max_step=max_step
    )

    t_res = sol.t
    h_res = sol.y[0]
    q_res = np.array([calcular_caudal(t, h, B, d, t_open, tasa_apertura,
                                       Cd_orif, Cd_weir, g)
                      for t, h in zip(t_res, h_res)])

    t_parada = t_res[-1]

    aperturas = np.array([tasa_apertura * t if t < t_open else d for t in t_res])
    diff_transicion = h_res - aperturas

    indices_transicion = []
    for i in range(1, len(diff_transicion)):
        if diff_transicion[i - 1] * diff_transicion[i] < 0:
            indices_transicion.append(i)
        if t_res[i - 1] < t_open <= t_res[i]:
            if i not in indices_transicion:
                indices_transicion.append(i)

    return {
        't_res': t_res,
        'h_res': h_res,
        'q_res': q_res,
        't_parada': t_parada,
        't_apertura_total': t_open,
        'indices_transicion': indices_transicion,
        'parametros': {
            'L': L, 'W': W, 'B': B, 'd': d, 't_open': t_open,
            'h0': h0, 'h_parada': h_parada,
            'Cd_orif': Cd_orif, 'Cd_weir': Cd_weir
        }
    }
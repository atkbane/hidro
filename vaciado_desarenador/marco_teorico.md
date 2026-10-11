# Marco Teórico — Simulación de Vaciado de Desarenador

## 1. Definición y clasificación

El **vaciado de un desarenador** consiste en evacuar el volumen de agua almacenado a través de una compuerta de fondo (compuerta de lavado/purga). Es un problema de **flujo no permanente** donde:

- el nivel de agua $h(t)$ desciende con el tiempo,
- el caudal de salida $Q(t)$ depende del nivel y de la apertura instantánea de la compuerta $a(t)$,
- y la evolución es **acoplada**: $h$ baja porque sale caudal, y $Q$ baja porque baja $h$.

**Objetivo del programa:** estimar la evolución temporal $h(t)$ y $Q(t)$ desde el inicio de la apertura de compuerta hasta que el nivel alcanza el tirante de parada $h_{\text{parada}}$, entregando como resultado principal el **tiempo de vaciado** $t_{\text{parada}}$.

---

## 2. Geometría y datos de entrada

### 2.1 Desarenador

| Variable | Símbolo | Unidad | Función / uso |
|---|---|---|---|
| Largo | $L$ | m | Geometría del estanque |
| Ancho | $W$ | m | Geometría del estanque |
| Tirante inicial | $h_0$ | m | Condición inicial de la ODE |
| Tirante de parada | $h_{\text{parada}}$ | m | Evento terminal de la ODE |

**Restricciones geométricas** (validadas en `calculos.simular_vaciado`):
- $B \le W$ — la compuerta no puede ser más ancha que el desarenador.
- $h_{\text{parada}} < h_0$ — sin tramo útil la simulación no produce resultados.

### 2.2 Compuerta de fondo

| Variable | Símbolo | Unidad | Función / uso |
|---|---|---|---|
| Ancho de compuerta | $B$ | m | Área de descarga $A_o = B \cdot a(t)$ |
| Apertura máxima | $d$ | m | Valor final de $a(t)$ |
| Tiempo de apertura | $t_{\text{open}}$ | s | Duración de la maniobra de apertura |
| Tasa de apertura | $\dot{a} = d / t_{\text{open}}$ | m/s | Pendiente lineal de $a(t)$ |

### 2.3 Coeficientes y constantes físicas

| Variable | Símbolo | Default UI | Función / uso |
|---|---|---|---|
| Coef. orificio | $C_{d,\text{orif}}$ | 0.60 | Fórmula de orificio (§3.1) |
| Coef. vertedero | $C_{d,\text{weir}}$ | 0.40 | Fórmula de vertedero (§3.2) |
| Gravedad | $g$ | 9.81 m/s² | Carga de velocidad $\sqrt{2g}$ |

> **Nota sobre $C_{d,\text{weir}}$:** el default de la UI es **0.40** (conservador, para vertedero de pared gruesa / compuerta con flujo sumergido parcialmente). Para un vertedero rectangular tipo Francis estándar, el valor típico es $C_d \approx 0.62$ (equivalente a $C = 1.84$). El usuario debe ajustarlo según la geometría real. Ver §9.

---

## 3. Caudal de salida

La compuerta puede operar en dos regímenes según la relación entre el nivel $h$ y la apertura $a(t)$. El modelo implementa una transición suave entre ambos mediante una sigmoide (§5).

### 3.1 Régimen de orificio — `calcular_caudal`

Cuando el nivel cubre completamente la compuerta ($h > a$), la descarga sigue la ecuación de orificio de pared delgada:

$$
Q_{\text{orificio}} = C_{d,\text{orif}} \cdot A_o \cdot \sqrt{2 g \cdot h_{\text{ef}}}
$$

Donde:
- $A_o = B \cdot a(t)$ — área instantánea de la abertura [m²]
- $h_{\text{ef}} = h - a(t)/2$ — carga efectiva medida al **centroide** del orificio [m]
- $C_{d,\text{orif}}$ — coeficiente de descarga (default 0.60)

### 3.2 Régimen de vertedero — `calcular_caudal`

Cuando la compuerta está casi totalmente abierta o el nivel es bajo, el flujo se comporta como un vertedero rectangular sin contracciones laterales:

$$
Q_{\text{vertedero}} = \frac{2}{3} \cdot C_{d,\text{weir}} \cdot B \cdot \sqrt{2g} \cdot h^{3/2}
$$

Forma derivada de la ecuación de Francis $Q = C \cdot B \cdot h^{3/2}$, con la equivalencia $C = \tfrac{2}{3} \cdot C_d \cdot \sqrt{2g}$.

---

## 4. Apertura de la compuerta

Implementada en `calcular_caudal`. La compuerta se abre linealmente desde $t=0$ hasta $t = t_{\text{open}}$:

$$
a(t) = \begin{cases}
\dfrac{d}{t_{\text{open}}} \cdot t, & t < t_{\text{open}} \\[4pt]
d, & t \ge t_{\text{open}}
\end{cases}
$$

El modelo **no incluye** la inercia hidráulica del flujo (golpe de ariete) ni efectos transitorios de cierre súbito.

---

## 5. Transición orificio–vertedero — sigmoide

Implementada en `calcular_caudal`. La transición entre los dos regímenes se interpola con una **función logística** sobre la variable adimensional $x = (h - a)/a$:

$$
w = \frac{1}{1 + e^{-k \cdot x}}, \quad x = \frac{h - a(t)}{a(t)}
$$

$$
Q = w \cdot Q_{\text{orificio}} + (1 - w) \cdot Q_{\text{vertedero}}
$$

**Comportamiento:**
- $h \gg a$ → $x \gg 0$ → $w \to 1$ → domina orificio
- $h = a$ → $x = 0$ → $w = 0.5$ → ambos contribuyen igual
- $h \ll a$ → $x \ll 0$ → $w \to 0$ → domina vertedero

> **Parámetro $k = 20$:** hardcodeado en la firma de `calcular_caudal`. Produce una zona de transición de $\pm 15\%$ de la apertura. **No es un parámetro de proyecto**: la elección $k=20$ refleja un compromiso entre suavidad numérica y fidelidad al modelo físico. Valores más altos (≥50) acercan la transición a un switch discreto; valores más bajos (≤5) mezclan ambos regímenes en un rango demasiado amplio. Ver GUIA_REVISION.md §6.

---

## 6. Solución numérica — `simular_vaciado`

### 6.1 Planteamiento

La conservación de masa en el desarenador da:

$$
A \cdot \frac{dh}{dt} = -Q(t, h)
\qquad\Longrightarrow\qquad
\frac{dh}{dt} = -\frac{Q(t, h)}{L \cdot W}, \quad h(0) = h_0
$$

con $A = L \cdot W$ constante (asunción de paredes verticales — ver §9).

### 6.2 Integración con RK45

Se usa `scipy.integrate.solve_ivp` con el método **RK45** (Runge–Kutta–Fehlberg de orden 5(4) con paso adaptativo):

| Parámetro | Default | Notas |
|---|---|---|
| `t_max` | 3600 s | Tiempo máximo de simulación (configurable) |
| `n_puntos` | 2000 | Puntos uniformes de evaluación para el gráfico |
| `max_step` | 5.0 s | Evita saltos abruptos durante la apertura de compuerta |

### 6.3 Evento terminal

La integración se detiene cuando $h \le h_{\text{parada}}$ mediante el evento:

$$
h(t) \le h_{\text{parada}} \implies \text{fin de simulación}
$$

`h_parada` típicamente = 0.10 m (nivel residual que la compuerta no termina de vaciar).

---

## 7. Resultados entregados

Devueltos por `simular_vaciado` y serializados por `web_bridge.ejecutar_simulacion`:

| Resultado | Símbolo | Cálculo |
|---|---|---|
| Tiempo de vaciado | $t_{\text{parada}}$ | Último instante de la solución de la ODE |
| Caudal máximo | $Q_{\max}$ | `max(q_res)` sobre toda la trayectoria |
| Tiempo de apertura total | $t_{\text{open}}$ | Parámetro de entrada |
| Nivel inicial | $h_0$ | Parámetro de entrada |
| Índices de transición | — | Instantes donde $h = a(t)$ o $t = t_{\text{open}}$ (cambio de régimen) |

---

## 8. Analogía con vaciado por vertedero (Rocha)

Rocha (§9.9) resuelve analíticamente el vaciado de un estanque por un vertedero rectangular solo:

$$
t = \frac{2A}{C \cdot L} \left( \frac{1}{\sqrt{H_2}} - \frac{1}{\sqrt{H_1}} \right)
$$

Este programa **generaliza** esa solución para:

1. incluir ambos mecanismos de descarga (orificio **y** vertedero),
2. incluir apertura progresiva de compuerta $a(t)$,
3. resolver numéricamente — sin solución analítica cerrada en el caso general.

---

## 9. Supuestos y constantes

| Supuesto / constante | Valor / forma | Justificación |
|---|---|---|
| $C_{d,\text{orif}}$ default | 0.60 | Orificio de pared delgada, compuerta deslizante |
| $C_{d,\text{weir}}$ default | 0.40 | Conservador (Francis ≈ 0.62; pared gruesa sumergida ≈ 0.40). Ajustar según geometría |
| $g$ | 9.81 m/s² | Gravedad estándar |
| $k$ sigmoide | 20.0 | Transición en ~15% de la apertura. Hardcodeado (no es parámetro de proyecto) |
| $A = L \cdot W$ | constante | **Paredes verticales, sin bisel.** Desarenadores con bisel inferior requieren $A = A(h)$ y otra formulación de la ODE — **fuera del alcance de este programa** |
| $a(t)$ | lineal | Apertura a velocidad constante, sin golpes |
| $t_{\max}$ | 3600 s | Tiempo máximo de simulación (configurable desde la UI) |
| $h_{\text{parada}}$ | 0.10 m | Nivel residual típico |
| Fricción en el canal | nula | Solo se consideran pérdidas por contracción en la compuerta |
| Efectos 3D | nulos | Modelo 1D promediado en sección |
| Golpe de ariete | nulo | Sin inercia hidráulica del flujo |

**Validez del modelo:** anteproyectos y estudios preliminares. Para diseño definitivo, calibrar $C_d$ con datos del prototipo y verificar con un modelo numérico 2D/3D.

---

## 10. Referencias

1. ANA. *Criterios de Diseño de Obras Hidráulicas* §2.11.4 — ecuación de orificio de pared delgada, $C_d = 0.60$.
2. Villón, M. *Diseño de Estructuras Hidráulicas* cap. 7 — compuertas y descarga por orificio.
3. Rocha, A. *Hidráulica de Tuberías y Canales* §9.3, §9.9 — vertedero rectangular y vaciado analítico de estanque.
4. Cengel, Y. *Mecánica de Fluidos* §13.5 — descarga sobre vertedero rectangular, $Q = C_{wd} \cdot \tfrac{2}{3} \cdot b \cdot \sqrt{2g} \cdot H^{3/2}$.
5. Mansen, A. *Diseño de Bocatomas* §compuertas — $C_d$ para compuerta radial (0.72) vs deslizante (0.60).
6. Khatsuria, R.M. *Hydraulics of Spillways and Energy Dissipators* Eq. 7-11 — descarga sobre vertedero.

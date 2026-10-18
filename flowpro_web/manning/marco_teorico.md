# Marco Teórico — Tirante normal y Manning

Herramienta «Tirante normal y Manning»: réplica web (clean-room) de la herramienta
*Depth, Flowrate, Slope, and Roughness* de **Flow Pro 2.1**. Resuelve la ecuación de
Manning en canales abiertos prismáticos y permite despejar cualquiera de sus cuatro
variables —tirante, caudal, pendiente o rugosidad— dejando las otras tres como datos.

Todo el cálculo corre en el navegador (Pyodide). No se usa código del programa original;
las ecuaciones son las de la hidráulica de canales estándar.

## 1. Definición y clasificación

Flujo **permanente**, **uniforme** (tirante normal) en un canal **prismático**, de
superficie libre, con **flujo 1-D** y distribución de presión **hidrostática**. El tirante
normal es el tirante de flujo uniforme: aquel en que la pendiente de fricción iguala la
pendiente del fondo.

La herramienta calcula una incógnita por vez:

| Incógnita (`incognita`) | Datos requeridos |
|---|---|
| `profundidad` — tirante `y` | `Q`, `n`, `S` (+ geometría) |
| `caudal` — `Q` | `y`, `n`, `S` (+ geometría) |
| `pendiente` — `S` | `Q`, `y`, `n` (+ geometría) |
| `rugosidad` — `n` | `Q`, `y`, `S` (+ geometría) |

En todos los casos se reportan además `V`, `A`, `P` y `R` (velocidad, área, perímetro
mojado y radio hidráulico), tal como en el programa original.

> Las comparaciones con la herramienta original están verificadas en §7.

## 2. Sistemas de unidades y constantes

| | SI | Inglés |
|---|---|---|
| Longitud | m | ft |
| Caudal | m³/s | ft³/s |
| Factor de Manning `k` | **1.000** | **1.486** |
| Gravedad `g` | 9.806 m/s² | 32.174 ft/s² |

La ecuación de Manning se escribe de forma unificada con el factor `k`:

```
Q = (k/n) · A · R^(2/3) · S^(1/2)
```

Al cambiar de sistema, la herramienta **no convierte los números**: reinterpreta los
valores en las nuevas unidades y cambia `k` (mismo comportamiento de «unidades automáticas»
del original). Constantes en `calculos.py`: `G`, `K_MANNING`, `UNIDAD`.

## 3. Geometría de la sección — `Seccion.props`

`y` = tirante desde el fondo (invert); `A` = área mojada; `P` = perímetro mojado;
`T` = ancho superior; `R = A/P` = radio hidráulico.

### 3.1 Trapezoidal — `Seccion.props` (rama `TRAPEZOIDAL`)

Con `b` = ancho de solera y `m` = talud H:V (`m = 0` ⇒ rectangular; `b = 0` con `m > 0` ⇒
triangular):

```
A = y · (b + m·y)
P = b + 2·y·√(1 + m²)
T = b + 2·m·y
```

### 3.2 Circular — `Seccion.props` (rama `CIRCULAR`)

Con diámetro `D` y `θ = 2·arccos(1 − 2y/D)` (ángulo central del segmento mojado, rad):

```
A = D²/8 · (θ − sen θ)
P = D·θ/2
T = D·sen(θ/2)   (= 2·√(y·(D−y)))
```

### 3.3 Secciones pendientes

`Ushaped` y `Elongated circular` figuran en la interfaz pero **deshabilitadas**: su
geometría no está publicada por el programa original y se fijará contra un caso de prueba
antes de habilitarlas (ver §8).

## 4. Manning — `caudal_manning`

```
Q = (k/n) · A · R^(2/3) · S^(1/2)
```

Válida para `y > 0`, `n > 0`, `S > 0`; devuelve `0` fuera de ese dominio. Se evalúa con las
propiedades de §3 en el tirante dado.

## 5. Resolución de la incógnita — `resolver`

- **`caudal`**: directamente `Q = caudal_manning(...)`.
- **`pendiente`**: se despeja de Manning → `S = (Q·n / (k·A·R^(2/3)))²`.
- **`rugosidad`**: `n = k·A·R^(2/3)·√S / Q`.
- **`profundidad`** (`profundidad`): se resuelve por **bisección** la raíz de
  `f(y) = Q − caudal_manning(y) = 0`, función monótona creciente en `y` mientras el canal no
  se llena (§5.1). Tolerancia de máquina (200 iteraciones).

### 5.1 Techo del intervalo en sección circular

En una sección circular, el caudal de Manning crece con el tirante solo hasta
`y/D ≈ 0.938`; por encima, al acercarse a conducto lleno, el caudal **disminuye** y el
método pierde sentido. La búsqueda se restringe a la rama monótona `(0, 0.938·D]`. Si el
caudal pedido supera la capacidad de esa rama, se avisa que el flujo pasa a **conducto
lleno (a presión)**, fuera del alcance del canal abierto —coherente con la advertencia del
original («accurate as long as the flow does not become compressed»).

## 6. Salidas derivadas — `resolver`

- **Velocidad**: `V = Q/A` (continuidad).
- **Profundidad hidráulica**: `Dh = A/T`.
- **Número de Froude**: `Fr = V / √(g·Dh)`.
- **Régimen**: `subcrítico` (`Fr < 1`), `crítico` (`Fr = 1`), `supercrítico` (`Fr > 1`).

El original no muestra `Fr` en esta herramienta; aquí se añade como información de régimen
(el ingeniero interpreta), sin alterar las cinco salidas del programa.

## 7. Verificaciones

Caso de referencia (trapezoidal rectangular, SI): `B = 5 m`, `Q = 15 m³/s`, `n = 0.05`,
`S₀ = 0.02` (idéntico al reporte de Flow Pro 2.1 documentado).

| Variable | Original | Este núcleo |
|---|---|---|
| Tirante normal `Yₙ` | 1.214 m | **1.2136** m |
| Área normal `Aₙ` | 6.068 m² | **6.068** m² |

Se verificó además la **inversión**: partiendo de `y = 1.2136` se recuperan `Q = 15.00`,
`S = 0.0200` y `n = 0.0500`. En circular, ida y vuelta de `Q ↔ y` cierra con error < 1×10⁻⁴.

## 8. Condiciones especiales y limitaciones

- **Conducto lleno**: no aplicable (canal abierto). En circular, aviso si `Q` excede la
  capacidad de la rama monótona (§5.1).
- **Tirante > diámetro**: se rechaza en secciones cerradas.
- **`S ≤ 0` o `n ≤ 0`**: no aplicables a Manning; se avisa.
- **U-shaped / circular alargada**: pendientes de verificación (§3.3).
- Es una herramienta de cálculo, no un sistema experto: el ingeniero interpreta los
  resultados.

## 9. Supuestos y constantes

- Flujo permanente y uniforme; canal prismático; `g` según §2.
- Rugosidad `n` de Manning en su forma adimensional; `k` según el sistema de unidades.
- El programa original imprime el encabezado *Depth, Flowrate, Slope, and Roughness*; aquí
  se conservan las mismas salidas y la disposición de campos.

## 10. Referencias

1. Chow, V. T. *Open-Channel Hydraulics*. McGraw-Hill, Nueva York, 1959.
2. Jeppson, R. W. *Open Channel Flow Utilizing Computers*. 1994 (base teórica citada por Flow Pro).
3. ProSoft Apps. *Flow Pro 2.1 — Depth, Flowrate, Slope, and Roughness* (nota de ayuda del programa).

> Inventario de cálculos del programa original: `flowpro2-fuente/flowpro-2.1-calculos.md` (raíz del monorepo).

# Marco Teórico — Perfil de superficie libre

Réplica web (clean-room) de la herramienta *Water Surface Profile* de **Flow Pro 2.1**.
Calcula el perfil de flujo gradualmente variado (GVF) en un canal abierto prismático por el
**método de paso directo**, con integración de Simpson 1/3.

## 1. Definición

Flujo **gradualmente variado**: permanente, 1-D, en canal prismático, con presión
hidrostática y aproximación de pendiente pequeña. La ecuación diferencial del perfil es:

```
dx/dy = (1 − Fr²) / (S₀ − S_f)
```

con

```
S_f = (Q·n/k)² · P^(4/3) / A^(10/3)      (pendiente de fricción, Manning)
Fr² = Q²·T / (g·A³)                       (número de Froude al cuadrado)
```

Integrar `dx/dy` entre tirantes da la longitud. El método **directo** integra en `y` (no en
`x`), por lo que afina el paso donde `dx/dy` crece —más preciso que el *standard step* de paso
fijo, sobre todo cerca de la profundidad crítica.

## 2. Geometría y primer momento — `Seccion.props`, `Seccion.momento_area`

`A`, `P`, `T`, `R = A/P` como en las otras herramientas. Además, para el **momentum** se
requiere el primer momento de área respecto a la superficie libre, `A·ȳ`:

- **Trapezoidal**: `A·ȳ = b·y²/2 + m·y³/3`.
- **Circular** (`α = arccos(1 − 2y/D)`, `R = D/2`):

```
A·ȳ = 2·R³ · [ −α·cos α/2 + sen α·cos²α/2 + sen³α/3 ]
```

Comprobación: para medio llenado (`α = π/2`) resulta `2R³/3`, y para sección llena
(`α = π`) `πR³`, ambos correctos.

## 3. Tirantes de referencia — `tirante_normal`, `tirante_critico`

Se calculan por bisección (Manning para `Yn`; `Q²T/(gA³) = 1` para `Yc`), igual que en las
herramientas de Manning y de régimen crítico. Si el caudal excede la capacidad de la sección
(en circular), se usa `Yn = D` y se emite el aviso **«capacidad excedida»**.

## 4. Clasificación del perfil — `_clasificar`

Letra por pendiente y subíndice por la posición del tirante respecto de `Yn` y `Yc`
(1 = sobre ambos, 2 = entre ambos, 3 = bajo ambos):

- `M` mild (`Yn > Yc`) · `S` steep (`Yn < Yc`) · `C` critical (`Yn = Yc`) ·
  `H` horizontal (`S₀ = 0`) · `A` adverse (`S₀ < 0`).

El **tipo de flujo** es *subcrítico* si `Fr < 1` en el control, *supercrítico* si `Fr > 1`.
El original usa *subcritical* / *supercritical*.

## 5. Algoritmo de integración — `resolver_perfil`

1. Calcular `Yc` y (si `S₀ > 0`) `Yn`.
2. Tirante de control: el dato del usuario; si viene vacío/0 se usa `Yc`.
3. Dirección de marcha: **subcrítico** desde aguas abajo hacia arriba (control en el extremo
   final); **supercrítico** desde aguas arriba hacia abajo (control en el extremo inicial).
4. Paso en tirante `Δy = (Y_destino − Y_control)·0.998/N`, con `N = 30` sub-pasos por defecto
   y **una fila por cada dos sub-pasos**. El factor 0.998 evita el punto donde `dx/dy → ∞`.
5. Integrar con **Simpson 1/3** cada par de sub-pasos y acumular la estación.
6. Parar al alcanzar el tirante de referencia o el extremo del canal (interpolando la última
   fila si se sobrepasa).

`Y_destino` es `Yn` si existe, o `Yc` en pendientes horizontal/adversa.

## 6. Columnas de salida

| Columna | Fórmula |
|---|---|
| Tirante | `y` |
| Energía específica | `E = y + V²/(2g)` |
| Área | `A(y)` |
| Velocidad | `V = Q/A` |
| Ancho superior | `T(y)` |
| Momentum (fuerza específica) | `M = A·ȳ + Q²/(gA)` |
| Froude | `Fr` (real) — o `Fr²` como el original |
| Carga de velocidad | `V²/(2g)` |
| Radio hidráulico | `R = A/P` |
| Perímetro mojado | `P(y)` |

> **Nota sobre la columna «Froude Number»**: el programa original imprime en realidad `Fr²`
> (el cuadrado del número de Froude). Esta web permite elegir entre `Fr` real y `Fr²` por
> compatibilidad con los reportes del original.

## 7. Verificación

Caso del reporte de Flow Pro 2.1 (SI, rectangular `B = 5 m`, `Q = 15 m³/s`, `n = 0.05`,
`S₀ = 0.02`, control `1.200 m`, estaciones 0 a 100, `N = 30`):

| Resultado | Original | Este núcleo |
|---|---|---|
| Tirante normal `Yn` | 1.214 m | **1.2136** m |
| Área normal `An` | 6.068 m² | **6.0682** m² |
| Tirante crítico `Yc` | 0.972 m | **0.9718** m |
| Área crítica `Ac` | 4.859 m² | **4.8591** m² |
| Tipo de perfil | mild, M-2 | **mild, M-2** |
| Tipo de flujo | subcritical | **subcritical** |
| Filas | 16 | **16** |

Las estaciones coinciden con el reporte (p. ej. 0+99.338 / 0+98.624 / 0+97.850 / … / 0+73.225)
y la primera fila reproduce `E = 1.519`, `A = 6.000`, `V = 2.500`, `M = 7.424`, `R = 0.811`.
La última fila depende del criterio de parada (ahí `dx/dy → ∞`), como en el original.

## 8. Limitaciones

- Flujo permanente; canal prismático; una fase; sin resaltos ni estructuras dentro del perfil.
- Superficie libre (si hay «capacidad excedida», el cálculo es referencial).
- Secciones **U** y **circular alargada** pendientes de verificación.

## 9. Supuestos y constantes

`k = 1.000` (SI) / `1.486` (inglés); `g = 9.806` / `32.174`; `N = 30`; factor de parada `0.998`.

## 10. Referencias

1. Chow, V. T. *Open-Channel Hydraulics*. McGraw-Hill, 1959.
2. Jeppson, R. W. *Open Channel Flow Utilizing Computers*. 1994.
3. ProSoft Apps. *Flow Pro 2.1 — Water Surface Profile* (nota de ayuda del programa).

> Inventario de cálculos del programa original: `flowpro2-fuente/flowpro-2.1-calculos.md` (raíz del monorepo).

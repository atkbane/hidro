# Marco Teórico — Tirante y pendiente crítica

Réplica web (clean-room) de la herramienta *Critical Depth and Slope* de **Flow Pro 2.1**.
Calcula el tirante crítico y la pendiente crítica de un canal abierto prismático.

## 1. Definición

Régimen crítico: estado de energía específica mínima para un caudal dado, que ocurre cuando
el número de Froude vale 1. Es la frontera entre flujo subcrítico (`Fr < 1`) y supercrítico
(`Fr > 1`).

## 2. Geometría de la sección — `Seccion.props`

Idéntica a la de la herramienta de Manning:

- **Trapezoidal** (`b` solera, `m` talud, `m = 0` ⇒ rectangular):
  `A = y·(b + m·y)`, `P = b + 2y√(1 + m²)`, `T = b + 2m·y`.
- **Circular** (`D` diámetro, `θ = 2·arccos(1 − 2y/D)`):
  `A = D²/8·(θ − sen θ)`, `P = D·θ/2`, `T = D·sen(θ/2)`.

## 3. Tirante crítico — `tirante_critico`

Condición de energía específica mínima:

```
Q²·T / (g·A³) = 1        con A = A(y), T = T(y) en y = Yc
```

`f(y) = Q²·T/(g·A³)` es **decreciente** en `y`, por lo que se resuelve por **bisección**:
en trapezoidal con cota superior expandida; en circular dentro de `(0, D]`.

## 4. Pendiente crítica — `resolver`

Es la pendiente que, por Manning, haría fluir el canal con el tirante crítico:

```
Sc = ( n·Q / (k · A_c · R_c^(2/3)) )²
```

con `A_c`, `R_c` evaluados en `y = Yc`. La rugosidad `n` se pide como dato (no influye en
`Yc`, solo en `Sc`).

## 5. Salidas

`Yc`, `Ac`, `Vc`, `Tc`, `Pc`, `Rc` y `Sc`. El número de Froude en el tirante crítico es 1
por definición.

## 6. Verificación

Caso de referencia (SI, trapezoidal rectangular, `B = 5 m`, `Q = 15 m³/s`, `n = 0.05`):

| Variable | Documento de referencia | Este núcleo |
|---|---|---|
| Tirante crítico `Yc` | 0.972 m | **0.9718** m |
| Área crítica `Ac` | 4.859 m² | **4.8591** m² |

## 7. Limitaciones

- Secciones **U** y **circular alargada** pendientes (geometría sin verificar).
- Conducto lleno: en circular, error si no existe tirante crítico dentro de la sección.

## 8. Supuestos y constantes

Flujo permanente, canal prismático, flujo 1-D, presión hidrostática, pendiente pequeña.
`k = 1.000` (SI) / `1.486` (inglés); `g = 9.806` / `32.174`.

## 9. Referencias

1. Chow, V. T. *Open-Channel Hydraulics*. McGraw-Hill, 1959.
2. Jeppson, R. W. *Open Channel Flow Utilizing Computers*. 1994.
3. ProSoft Apps. *Flow Pro 2.1 — Critical Depth and Slope* (nota de ayuda del programa).

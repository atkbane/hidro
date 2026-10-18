# Marco Teórico — Vertederos

Réplica web (clean-room) de la herramienta *Weirs* de **Flow Pro 2.1**.
Calcula el caudal sobre un vertedero de pared delgada (rectangular, triangular o
Cipolletti) y de cresta ancha, en régimen libre o sumergido.

## 1. Definición

Un vertedero es un obstáculo sobre el que escurre el agua. La descarga depende de la carga
`H` sobre la cresta. En pared delgada, el `C_d` es **adimensional**; en las formas con
coeficiente dimensional (1.84 SI / 3.33 ft) ese factor ya incluye la geometría.

## 2. Forma unificada — `resolver`

Todas las formas de pared delgada se deducen de la integral de orificio sobre una franja:

```
Rectangular / Cipolletti :  Q = C_d · (2/3)·√(2g) · L · H^(3/2)
Triangular (V)           :  Q = C_d · (8/15)·√(2g) · tan(θ/2) · H^(5/2)
```

Constantes:

| Factor | SI | Inglés |
|---|---|---|
| `(2/3)√(2g)` | 2.9527 | 5.350 |
| `(8/15)√(2g)` | 2.362 | 4.280 |

`θ` = **ángulo total** del vertedero en V (campo de entrada; Flow Pro lo pide).

## 3. Coeficiente de descarga `C_d`

- **Pared delgada (rect./triangular)**: `C_d = 0.61` (rango 0.58–0.63), valor clásico.
  El documento de la biblioteca confirma que el **0.61 por defecto del programa es `C_d`
  adimensional** en la forma teórica — no el coeficiente dimensional 1.84/3.33.
- **Cipolletti**: la literatura da `c ≈ 0.63` (⇒ 1.86·L·H^1.5 en SI). Se deja editable.
- **Cresta ancha**: valor **teórico** `C_d ≈ 0.577` en la forma `(2/3)√(2g)`
  (equivale a 1.705·L·H^1.5 en SI; o 0.385 en la forma `√(2g)·L·H^1.5`).
  Ver la nota de la §7.

## 4. Contracción lateral (vertedero contraído)

La fórmula de Francis reduce la longitud efectiva en `0.1·H` por cada contracción:

```
Q = C_d·(2/3)√(2g) · (L − 0.1·n·H) · H^(3/2)        n = 0, 1, 2
```

La UI de Flow Pro **no** tiene campo de contracciones (solo «Weir length»), por lo que esta
implementación usa la longitud efectiva `L_ef = L` (vertedero suprimido). Si se requiere un
vertedero contraído, el usuario puede introducir directamente la longitud efectiva.

## 5. Vertedero sumergido — Villemonte — `resolver` (sumergido)

```
Q_s / Q_f = [ 1 − (H₂/H₁)^n ]^0.385
```

- `Q_f` = caudal que tendría el vertedero **libre** con la carga `H₁`.
- `n` = exponente de la ecuación libre: **3/2** rectangular/Cipolletti, **5/2** triangular.
- Exponente `0.385`, adimensional, igual para todas las formas.
- Requiere `H₂ < H₁`. Aplica a las tres formas cambiando solo `n`.

## 6. Salidas

`Q` (caudal). En régimen sumergido se informa además el `Q_f` libre equivalente.

## 7. Verificación

Predicciones con las fórmulas anteriores (SI, `C_d = 0.61` salvo indicación):

| Caso | Entradas | Resultado |
|---|---|---|
| Rectangular libre | `L=1`, `H=0.5` | **0.6367** m³/s |
| Triangular libre (90°) | `H=0.15` | **0.01256** m³/s |
| Cipolletti libre | `L=1`, `H=0.3`, `C=0.63` | **0.3056** m³/s |
| Cresta ancha | `L=1`, `H=0.2`, `C=0.577` | **0.1524** m³/s |
| Rectangular sumergido | `L=1`, `H₁=0.3`, `H₂=0.1` | **0.2725** m³/s |
| Triangular sumergido (90°) | `H₁=0.3`, `H₂=0.1` | **0.0692** m³/s |

## 8. Limitaciones

- La **convención exacta de coeficientes** de Flow Pro no está publicada; esta implementación
  adopta la forma teórica con `C_d` adimensional (hipótesis más coherente). Pendiente de
  contrastar con un caso real (batería de pruebas del documento de la biblioteca).
- El comportamiento de la **cresta ancha** (forma `√(2g)` con `C≈0.385` vs `(2/3)√(2g)` con
  `C≈0.577`, y el rango de validez `H/L`) queda por confirmar.
- Cresta ancha sumergida: Villemonte **no** es estricto (HEC-RAS usa otra curva); se aplica
  como aproximación.

## 9. Supuestos y constantes

Flujo permanente, aproximación de pared delgada, `g = 9.806` (SI) / `32.174` (inglés).
`C_d = 0.61` (pared delgada), `0.577` (cresta ancha), exponente de Villemonte `0.385`.

## 10. Referencias

1. Rocha Felices, A. *Hidráulica de Tuberías y Canales*. Cap. IX (vertederos; ecs. 9-3 a 9-42).
2. Brater, E. F.; King, H. W.; Lindell, J. E.; Wei, C. Y. *Handbook of Hydraulics*. Sec. 5.
3. USBR. *Design of Small Canal Structures*. §5-3 (weir equations).
4. Linsley, R. K. *Ingeniería de los Recursos Hidráulicos*. Cap. 10.
5. HEC-RAS. *Hydraulic Reference Manual* v6.6 — «Submerged Weir Flow» (Villemonte).
6. ProSoft Apps. *Flow Pro 2.1 — Weirs* (nota de ayuda del programa).

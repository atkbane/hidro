# Marco Teórico — Compuertas de fondo

Réplica web (clean-room) de la herramienta *Underflow Gates* de **Flow Pro 2.1**.
Calcula el caudal y la velocidad bajo una compuerta (vertical, radial/tainter o tambor)
en un canal rectangular, en descarga libre.

## 1. Definición

La compuerta de fondo controla el paso del agua por debajo de ella. El flujo se comporta
como un orificio de altura igual a la apertura `a`, con la carga tomada sobre el centro de
la abertura. `C_d` es un **coeficiente de descarga/contracción** que corrige la vena
contracta; su valor depende del tipo de compuerta y de la relación `y₁/a`.

## 2. Ecuación — `resolver`

```
Q = C_d · b · a · √(2·g·y₁)          V = Q / (b·a)
```

- `Q` = caudal · `b` = ancho de la compuerta · `a` = apertura.
- `y₁` = tirante aguas arriba.
- `C_d` = coeficiente de descarga (default **0.61**).

La biblioteca confirma esta forma como *la ecuación convencional de compuerta deslizante*
(Swamee-Chahar §3.3.1) y como orificio con carga sobre el centro (Brater §4). Las variantes
con `(y₁ − y₂)` corresponden al caso **sumergido**, y con `(y₁ − C_c·a)` a la vena contracta
explícita; con solo `y₁` como dato y dos salidas (Q, V), Flow Pro corresponde a la forma libre.

## 3. Coeficiente de descarga `C_d`

| Tipo de compuerta | `C_d` típico | Comentario |
|---|---|---|
| Vertical / deslizante | 0.55–0.61 | default del programa: **0.61** |
| Radial (tainter) | ~0.65 | borde redondeado ⇒ algo mayor |
| Tambor | ~0.65 | borde redondeado |

Correlación de Henry (1950), para descarga libre:

```
C_d = 0.611 · [ (y₁ − a) / (y₁ + 15·a) ]^0.072
```

`C_d → 0.611` cuando `y₁ ≫ a` (coincide con el default). En esta herramienta `C_d` es dato
editable, por lo que el usuario puede introducir el valor de Henry o el de su tipo de compuerta.

## 4. Velocidad

`V = Q/(b·a)`, velocidad media en la abertura. (Si el programa reportara la velocidad en la
vena contracta, sería `Q/(C_c·b·a)`; el texto de Flow Pro —«velocity under a gate»— sugiere
la velocidad en la abertura.)

## 5. Verificación

`b = 1.0 m`, `a = 0.20 m`, `y₁ = 1.0 m`, `C_d = 0.61` (SI):

```
Q = 0.61 · 1.0 · 0.20 · √(2·9.806·1.0) = 0.540 m³/s
V = 0.540 / 0.20 = 2.70 m/s
```

## 6. Limitaciones

- **Descarga libre** únicamente (la UI solo pide `y₁`, `b`, `a`, `C`).
- No modela el resalto sumergido ni la energía específica/momentum del chorro.
- La convención exacta de `C_d` de Flow Pro queda por contrastar con un caso real.

## 7. Supuestos y constantes

Flujo permanente, canal rectangular, `g = 9.806` (SI) / `32.174` (inglés);
`C_d` por defecto `0.61`.

## 8. Referencias

1. Swamee, P. K.; Chahar, B. R. *Design of Canals*. §3.3.1 (sluice gate; Henry 1950).
2. Brater, E. F.; King, H. W.; Lindell, J. E.; Wei, C. Y. *Handbook of Hydraulics*. Sec. 4.
3. USBR. *Design of Small Canal Structures*. Fig. 4-10 (orificio compuerta).
4. Rocha Felices, A. *Hidráulica de Tuberías y Canales*. §7.14 (compuerta de fondo).
5. ProSoft Apps. *Flow Pro 2.1 — Underflow Gates* (nota de ayuda del programa).

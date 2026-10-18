# Marco Teórico — Orificios

Réplica web (clean-room) de la herramienta *Orifices* de **Flow Pro 2.1**.
Calcula el caudal que descarga un orificio circular o cuadrado bajo una carga `H`.

## 1. Definición

Un orificio es una abertura, en pared o fondo, por la que descarga un depósito o conducto.
La carga `H` se mide desde la superficie libre hasta el **eje** del orificio y se supone
constante (régimen permanente). Válido con el orificio sumergido aguas arriba y descarga
libre aguas abajo.

## 2. Ecuación de descarga — `resolver`

```
Q = C · A · √(2·g·H)
```

- `C` = coeficiente de descarga (corrige contracción del chorro y pérdidas).
- `A` = área del orificio.
- `H` = carga sobre el orificio.

### 2.1 Área — `area_orificio`

```
Circular :  A = π·D²/4        (D = diámetro)
Cuadrado :  A = s²            (s = lado)
```

## 3. Coeficientes típicos — `COEF_TIPICOS`

| Configuración | `C` |
|---|---|
| Borde agudo | 0.61 |
| Entrada redondeada | 0.70 |
| Bocina (bell-mouth) | 0.80 |
| Tobera | 0.95 |

El programa original usa **0.61** por defecto. Los coeficientes para orificios circulares de
borde agudo fueron tabulados por Medaugh y Johnson (*Civil Engineering*, julio 1940, p. 424).

## 4. Salidas

`Q` (caudal), `A` (área), `V = Q/A` (velocidad media de descarga) y `V_ideal = √(2gH)`.

## 5. Limitaciones

- Solo régimen permanente y carga constante.
- No modela el orificio como abertura sumergida aguas abajo (ahogado) con carga diferencial.

## 6. Supuestos y constantes

`g = 9.806 m/s²` (SI) / `32.174 ft/s²` (inglés). El coeficiente `C` es dato del usuario.

## 7. Referencias

1. Medaugh, F. W.; Johnson, G. D. *Civil Engineering*, julio 1940, p. 424.
2. ProSoft Apps. *Flow Pro 2.1 — Orifices* (nota de ayuda del programa).

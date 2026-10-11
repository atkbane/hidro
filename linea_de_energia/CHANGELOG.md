# CHANGELOG — bernoulli

## Refinamiento visual + unidades (Jul 2026)

### interfaz_A.py — UI desktop

- **Dark theme para controles nativos**: ComboBox, QDoubleSpinBox, QLineEdit
  y QScrollArea ahora tienen estilos explícitos (`background: #1e293b`,
  `border: 1px solid #334155`) para consistencia con el dark theme en todos
  los SO.
- **Botones uniformizados**: border-radius 3px, padding 4px 12px, font-size
  9pt en todos los botones de acción (Calcular, + Agregar Nodo, + Rejilla, ×).
- **Hover en todos los botones**: incluido el botón × de rejillas que no lo
  tenía.
- **Separador QFrame**: cambiado de `color` a `background: #334155;
  max-height: 1px` para mayor compatibilidad entre SO.
- **Labels de resultado sin HTML redundante**: eliminado `<span>` wrapper
  que repetía el color del stylesheet.

### Unidades y decimales

- **e y s en milímetros**: campos de espesor y separación ahora se muestran
  en mm (sufijo "mm", 1 decimal) en Tranquilizadores y Rejillas. La fórmula
  de Kirschmer usa e/s como relación adimensional, por lo que no se necesita
  conversión.
- **Headers de rejillas**: actualizados a `e (mm), s (mm)`.
- **Decimales reducidos en coef de rejillas**: de 3 a 2 decimales.
- **Ángulo en Tranquilizadores**: 0 decimales (ya estaba correcto en
  rejillas).
- **specialValueText("0")**: todos los spinboxes muestran "0" cuando el
  valor es 0, evitando visualmente "0.000" o "0.001".

### Labels arriba del campo

- **`_add_dspin`, `_add_combo_g`, `_add_lineedit_g`**: cambiados de
  `QHBoxLayout` a `QVBoxLayout`. La descripción del campo ahora aparece
  arriba del input, con la unidad entre paréntesis (ej: "Q (m³/s)"). Se
  eliminó el suffix de los spinboxes para mayor legibilidad.

### Valores por defecto

- **Tranquilizadores**: e=0, s=0, ang=0 (antes e=70mm, s=150mm, ang=90°).
- **Rejillas**: e=0, s=0, ang=0, coef=2.42 (antes e=70mm, s=150mm,
  ang=90°).
- **Coef c**: mantiene 2.42 como valor por defecto.

### Validación en core.py

- **`calc_tranq`**: valida que `coef > 0`, `espesor > 0` y `separacion > 0`
  antes de calcular. Mensajes de error claros en español.
- **`nodo_rejillas_serie`**: valida por rejilla que `e > 0`, `s > 0` y
  `coef > 0`. Error indica número de rejilla (ej: "Rejilla 2: el espesor
  (e) debe ser mayor que 0 mm.").

### Layout y espaciado

- **Ventana**: `resize(520, 700)` → `resize(780, 700)`.
- **Flecha entre nodos**: reducida de `font-size: 14pt` a `10pt`,
  `setFixedHeight(14)`, texto "↓" sin espacios extra.
- **Resultados**: texto continuo sin `<br>` (word wrap natural según ancho
  de ventana). Label con `setMinimumHeight(36)`.
- **Scroll layout spacing**: de 4 a 2.
- **Backup**: `interfaz_A.py.bak` creado antes de los cambios.

## Refactor solvers + precisión numérica + UI responsiva (Jul 2026)

### core.py — motor de cálculo

- **`G` → `GRAVEDAD`**: renombrado para cumplir PEP8 (constantes en mayúsculas).
- **`COEFS_TRANSICION`**: coeficientes de contracción/expansión movidos a
  constante global (antes se recreaba el dict en cada llamada a `calcular_hl`).
- **Eliminado `nodo_mostrar`**: código muerto (solo hacía `print`).
- **`calc_tranq`**: parámetros renombrados para mayor claridad:
  `l_trans`→`longitud`, `sec_ini`→`sec_abajo`, `sec_fin`→`sec_arriba`,
  `c`→`coef`, `e`→`espesor`, `s`→`separacion`, `ang`→`angulo`.
- **Estrategia de convergencia de solvers** (`nodo_transicion`,
  `nodo_rejillas_serie`):
  - **Navegación**: usa precisión float completa (bisección suave).
  - **Convergencia**: verifica con los valores redondeados que publicará
    `SeccionHidraulica` (y, hv, hl a 0.01 m).
  - **Fallback**: si ningún tirante discretizado a 0.01 m satisface la
    tolerancia, retorna el mejor candidato (menor |dif|).
- **FIXME documentado**: el `+8` en `calc_tranq` queda como ajuste temporal
  pendiente de discusión.

### interfaz_A.py — UI desktop

- **FlowLayout**: implementado layout responsivo (basado en el ejemplo oficial
  de Qt). Los widgets fluyen en fila y bajan de línea cuando se angosta la
  ventana.
- **Todos los form builders** convertidos a FlowLayout (`_build_initial`,
  `_build_transicion`, `_build_tranquilizadores`, `_build_perdida`).
- **Spinboxes más angostos**: ancho reducido (60-70px según el campo).
- **Decimales por campo**: Q, b, y, z, longitud → 2 decimales; coeficientes
  de Kirschmer → 3 decimales.
- **Valores por defecto en 0.0**: los campos parten de 0 con
  `specialValueText("0")` para que se vean vacíos visualmente.
- **Ángulo de rejillas**: ahora se conserva como float (antes se truncaba a
  `int`).
- **Rangos de rejillas**: b_spin y z_spin corregidos para que `auto`
  funcione realmente (rango mínimo 0.0).

### bernoulli_03_mar.py — notebook de pruebas

- Mismos cambios que core.py (G→GRAVEDAD, COEFS_TRANSICION, parámetros de
  calc_tranq, eliminado nodo_mostrar).

## Rejillas en serie — balance de energía + Kirschmer v  (Jul 2026)

### Migración de `nodo_rejillas_serie` (core + GUI)

- **`nodo_rejillas_serie` en `core.py`**: reemplazada por la lógica corregida
  (antes en `nodo_rejillas_serie_prueba` en `bernoulli_03_mar.py`):
  - Cada rejilla acepta `z` y `b` propios (fallback al valor anterior).
  - Calcula `hl` de cada rejilla usando `NA_inicial` sin recalcular entre
    pasos.
  - **Balance de energía por bisección**: `E_target = E_inicial + hl_total`,
    encuentra el tirante `y` que satisface `z + y + hv(y) = E_target`.
  - `z` y `b` de la sección resultante = los de la última rejilla.

- **`interfaz_A.py`**: agregado campo `z (m)` por rejilla (valor "auto"
  hereda de la rejilla/sección anterior). Header actualizado a:
  `e, s, b, z, ang, coef`.

### Kirschmer: parámetro `hv` → `v`

- **`kirschmer`**: ahora recibe `v` (velocidad, m/s) en lugar de `hv` (carga
  de velocidad). Calcula `hv = v²/(2g)` internamente.
- Actualizados todos los llamadores en `core.py` (`calc_tranq`,
  `nodo_rejillas_serie`) y `bernoulli_03_mar.py` (mismas funciones + celda
  de prueba).
- Corrección en celda de prueba de marimo: `.94` (sin(70°) precalculado)
  → `70` (ángulo en grados, ahora se calcula `sin()` internamente).

## Refactor layout (Jul 2026)

- **`_inputs_grid` compartido → `_inputs_lav` contenedor**: cada builder
  (`_build_initial`, `_build_transicion`, etc.) crea su propio `QGridLayout`
  interno y lo añade a `_inputs_lav`. No más colisiones entre nodos.

- **Helpers con parámetro `grid`**: `_add_dspin`, `_add_combo_g`,
  `_add_lineedit_g` reciben el grid local. Cada builder controla su layout
  sin afectar a otros.

- **Selector de tipo movido al botón "Agregar Nodo"**: se eliminó el
  `QComboBox` de tipo dentro de cada nodo. El tipo se elige desde un combo
  en el header antes de agregar. Una vez agregado, el tipo es fijo.

- **Ventana**: `resize(950, 700)` → `resize(520, 700)` → `resize(780, 700)`.

- **Columnas del grid**: `setColumnStretch(0,0)` y `(1,0)` para que no se
  expandan. Celdas alineadas a `AlignLeft`.

## Tranquilizadores (auto-detección)

- Eliminado combo "Sección ref:" y métodos `set_ref_steps`,
  `get_selected_ref_name`, `_update_ref_combos`.
- Auto-detecta: `idx-1` = sección aguas abajo, `idx-2` = aguas arriba.
- Llamada a `nodo_tranquilizadores`: `(sec_arriba, sec_abajo, ...)` para
  coincidir con el orden del notebook marimo (upstream, downstream).
- Guard al agregar: muestra `QMessageBox.warning` si <2 nodos previos.
- Guard al eliminar: marca con `set_error` si un Tranquilizadores existente
  se queda con `index < 2`.

## Archivos limpiados

- Eliminados: `core_01.py`, `interfaz.py`, `interfaz_01.py`,
  `interfaz_02.py`, `run_desktop.py`, `run_desktop_01.py`,
  `run_desktop_02.py`, `DISENO_VERSION_A.md`, `__pycache__/`,
  `__marimo__/`.
- Quedan: `core.py`, `interfaz_A.py`, `run_desktop_A.py`,
  `bernoulli_03_mar.py`.

# Marco Teórico — Pérdida de Carga en Tuberías a Presión

## 1. Ecuación de Darcy-Weisbach (1845)

### 1.1 Fórmula general

La ecuación fundamental para pérdidas por fricción en tuberías a presión:

$$
h_f = f \cdot \frac{L}{D} \cdot \frac{v^2}{2g}
$$

Donde:
- $h_f$ = pérdida de carga por fricción [m]
- $f$ = factor de fricción de Darcy-Weisbach (adimensional)
- $L$ = longitud del tramo [m]
- $D$ = diámetro interior [m]
- $v$ = velocidad media del flujo [m/s]
- $g = 9.81$ m/s²

### 1.2 Forma en función del caudal

Sustituyendo $v = \frac{Q}{A} = \frac{4Q}{\pi D^2}$:

$$
h_f = f \cdot \frac{8}{\pi^2 g} \cdot \frac{Q^2 \cdot L}{D^5}
$$

El programa usa el factor precalculado $\frac{8}{\pi^2 g} \approx 0.08265$ s²/m, implementado en `calculos.py:_DW_K`.

> **Fuentes:** Brater §6.4, Cengel §8.5, Mendez §2.4, ESHA §2.1. Aplicación en memorias: CARHUAC, SANTARI, ZANA.

---

## 2. Factor de fricción — Swamee-Jain (1976)

### 2.1 Ecuación explícita

$$
f = \frac{0.25}{\left[ \log_{10} \left( \frac{k/D}{3.7} + \frac{5.74}{Re^{0.9}} \right) \right]^2}
$$

Forma equivalente (base $e$):

$$
f = \frac{1.325}{\left[ \ln \left( \frac{k/D}{3.7} + \frac{5.74}{Re^{0.9}} \right) \right]^2}
$$

El programa implementa la segunda forma (con $\ln$) en `calculos.py:f_swamee_jain`.

### 2.2 Rangos de validez

| Condición | Rango |
|-----------|-------|
| Rugosidad relativa | $10^{-6} \leq k/D \leq 10^{-2}$ |
| Número de Reynolds | $5000 \leq Re \leq 10^8$ |
| Precisión | ±1-2% respecto a Colebrook |

> **Advertencia:** No es válida para régimen laminar ($Re < 2300$) ni transicional ($2300 < Re < 4000$). En laminar, usar $f = 64/Re$ (Poiseuille). El programa no verifica este rango en tiempo de ejecución; retorna `0.0` para $Re < 1$ pero no advierte para $Re < 5000$.

### 2.3 Comparación con Colebrook-White

La ecuación implícita de Colebrook (1939) que Swamee-Jain aproxima:

$$
\frac{1}{\sqrt{f}} = -2.0 \cdot \log_{10} \left( \frac{k/D}{3.7} + \frac{2.51}{Re \cdot \sqrt{f}} \right)
$$

> **Fuentes:** Cengel §8.8 (Swamee-Jain), Mendez §2.5, Silowash §11.3. Colebrook: Cengel §8.8, Rocha cap. 5.

---

## 3. Número de Reynolds

### 3.1 Definición

$$
Re = \frac{v \cdot D}{\nu} = \frac{\rho \cdot v \cdot D}{\mu}
$$

Donde:
- $v$ = velocidad media [m/s]
- $D$ = diámetro de la tubería [m]
- $\nu$ = viscosidad cinemática [m²/s]
- $\nu_{\text{agua, 20°C}} = 1.004 \times 10^{-6}$ m²/s

### 3.2 Regímenes de flujo en tubería circular

| $Re$ | Régimen | Factor de fricción |
|------|---------|-------------------|
| $Re < 2300$ | Laminar | $f = 64/Re$ (Poiseuille) |
| $2300 < Re < 4000$ | Transición | Indeterminado (evitar diseño en este rango) |
| $Re > 4000$ | Turbulento | Colebrook / Swamee-Jain |

### 3.3 Significado físico

$$
Re = \frac{\text{Fuerzas de inercia}}{\text{Fuerzas viscosas}}
$$

> **Fuentes:** Cengel §8.2, Rocha §3.3, Brater §6.2, ESHA §2.2.

---

## 4. Hazen-Williams (1905)

### 4.1 Fórmula en unidades SI

$$
h_f = 10.67 \cdot L \cdot \frac{Q^{1.852}}{C^{1.852} \cdot D^{4.87}}
$$

Donde:
- $h_f$ = pérdida de carga [m]
- $L$ = longitud [m]
- $Q$ = caudal [m³/s]
- $C$ = coeficiente de Hazen-Williams (adimensional)
- $D$ = diámetro interior [m]

### 4.2 Valores típicos de $C$

| Material | $C$ |
|----------|-----|
| Plástico (PVC, HDPE) | 140 - 150 |
| Fibra de vidrio (nuevo) | 150 - 165 |
| Acero revestido | 130 - 140 |
| Concreto centrifugado | 130 - 140 |
| Hierro fundido nuevo | 130 |
| Acero nuevo sin revestir | 120 - 130 |
| Hierro fundido viejo | 100 |
| Tubería deteriorada | 60 - 80 |
| Uralita (asbesto-cemento) | 140 |

### 4.3 Limitaciones

- Válida solo para agua a temperaturas normales
- No considera viscosidad ni temperatura (a diferencia de Darcy-Weisbach)
- Tiende a sobrestimar pérdidas para $C < 100$ en régimen rugoso
- Empírica — usar con reserva fuera del rango calibrado

### 4.4 Relación con $f$ de Darcy-Weisbach

$$
f = \frac{13.637 \cdot g}{C^{1.852} \cdot Re^{0.148} \cdot v^{0.148} \cdot D^{0.018}}
$$

> **Fuentes:** Mendez §2.6, Brater §6.5, ESHA §2.3 + Tabla 2.3, AWWA M45 §2.3, Karassik *Pump Handbook*.

---

## 5. Manning para tuberías a presión

### 5.1 Derivación

Partiendo de la fórmula de Manning para canales abiertos:

$$
v = \frac{1}{n} \cdot R^{2/3} \cdot S^{1/2}
$$

Para tubería circular llena:
- $A = \pi D^2 / 4$
- $R = D / 4$
- $S = h_f / L$
- $v = Q / A$

Sustituyendo y despejando:

$$
h_f = 10.29 \cdot n^2 \cdot L \cdot \frac{Q^2}{D^{16/3}}
$$

El programa implementa `d ** 5.333` en `calculos.py:perdida_ma`. La forma algebraicamente exacta es $D^{16/3} \approx D^{5.3333}$, pero la diferencia es despreciable (error relativo $< 0.025\%$) y se mantiene la forma decimal por legibilidad.

### 5.2 Valores típicos de $n$

| Material | $n$ |
|----------|-----|
| Concreto pulido | 0.012 - 0.014 |
| Tubería de concreto | 0.013 - 0.015 |
| Acero soldado liso | 0.011 - 0.013 |
| Acero corrugado | 0.024 - 0.030 |
| PVC / HDPE | 0.009 - 0.011 |

### 5.3 Limitaciones

> **Importante:** La ecuación de Manning fue desarrollada para canales abiertos. Para tuberías a presión deben preferirse Darcy-Weisbach o Hazen-Williams. Manning en tuberías es una extensión práctica pero no teóricamente rigurosa.

> **Fuentes:** Brater §6.5, Cengel §8.10, Síntesis *Manning*, Liria §3.2.

---

## 6. Pérdidas localizadas (minor losses)

### 6.1 Fórmula general

$$
h_L = K \cdot \frac{v^2}{2g}
$$

Donde $K$ es el coeficiente de pérdida localizada.

### 6.2 Coeficientes de entrada y salida

| Accesorio | $K$ |
|-----------|-----|
| Entrada a ras de pared (bordes vivos) | 0.50 |
| Entrada redondeada | 0.04 - 0.20 |
| Entrada saliente (bordes vivos) | 0.80 - 0.90 |
| Salida a depósito (ensanchamiento brusco) | 1.00 |
| Contracción brusca | $0.5 \cdot (1 - A_2/A_1)$ |
| Expansión brusca (Borda) | $(1 - A_1/A_2)^2$ |

### 6.3 Programa: solo entrada y salida

El programa aplica pérdidas localizadas únicamente en:
- **Entrada:** $h_{\text{entrada}} = K_{\text{entrada}} \cdot v_1^2/(2g)$, usando la velocidad del primer segmento
- **Salida:** $h_{\text{salida}} = K_{\text{salida}} \cdot v_n^2/(2g)$, usando la velocidad del último segmento

Valores por defecto: $K_{\text{entrada}} = 0.50$, $K_{\text{salida}} = 1.0$ (estándar para entrada de bordes vivos y salida a depósito).

### 6.4 Aclaración sobre el término "minor losses"

El término "pérdidas menores" es apropiado para tuberías largas. En tuberías cortas, las pérdidas localizadas pueden superar a las pérdidas por fricción.

> **Fuentes:** Brater §6.7, Cengel §8.9, Mendez §2.7.

---

## 7. Potencia perdida

### 7.1 Ecuación

$$
P = \gamma \cdot Q \cdot h_{\text{total}} \quad [\text{kW}]
$$

Donde:
- $\gamma = 9.81$ kN/m³ (peso específico del agua)
- $Q$ = caudal [m³/s]
- $h_{\text{total}} = h_f + h_{\text{entrada}} + h_{\text{salida}}$ = pérdida total [m]

### 7.2 Conversión

- $P \geq 1000$ kW → se muestra en MW ($P / 1000$)

> **Significado:** Energía hidráulica disipada por fricción que no se convierte en energía útil. En centrales hidroeléctricas representa potencia que deja de generarse.

---

## 8. Rugosidad absoluta de materiales ($k$)

Para Darcy-Weisbach con Swamee-Jain:

| Material | $k$ [mm] |
|----------|----------|
| Vidrio, plástico liso | 0 (teórico: 0.0015) |
| Acero comercial nuevo | 0.045 - 0.05 |
| Hierro galvanizado | 0.15 |
| Hierro fundido nuevo | 0.26 |
| Hierro fundido viejo (oxidado) | 1.0 - 1.5 |
| Concreto liso | 0.3 - 0.6 |
| Concreto rugoso | 1.0 - 3.0 |
| Acero remachado | 0.9 - 9.0 |

> **Fuentes:** Cengel Tabla 8-1, Mendez Tabla 2.2, Brater Tablas de rugosidad.

---

## 9. Tabla comparativa de métodos

| Método | Base | Precisión | Aplica para | Limitación |
|--------|------|-----------|-------------|------------|
| **Darcy-Weisbach + Swamee-Jain** | Teórica + empírica | ±2% de Colebrook | Cualquier fluido, $Re > 5000$ | Requiere $k$ y $\nu$ |
| **Hazen-Williams** | Empírica | Variable según material | Agua, $D > 50$ mm | No considera $T$ ni $\nu$ |
| **Manning** | Empírica (canales) | Baja en tuberías | Extensión práctica | No rigurosa para presión |

---

## 10. Supuestos y constantes

| Parámetro | Valor | Justificación |
|-----------|-------|---------------|
| Gravedad $g$ | 9.81 m/s² | Valor estándar a nivel del mar |
| Peso específico $\gamma$ | 9.81 kN/m³ | Agua a condiciones normales |
| Viscosidad cinemática $\nu$ | $1.004 \times 10^{-6}$ m²/s | Agua a 20 °C — hardcodeada en `calculos.py:VISCO_20C` |
| $K_{\text{entrada}}$ por defecto | 0.50 | Entrada de bordes vivos |
| $K_{\text{salida}}$ por defecto | 1.00 | Salida a depósito |
| Factor Darcy-Weisbach $8/(\pi^2 g)$ | $\approx 0.08265$ s²/m | Precalculado en `calculos.py:_DW_K` |
| Mínimo $Re$ para Swamee-Jain | 5000 | Límite inferior de validez de la aproximación |

> **Nota:** El programa no incluye validaciones en tiempo de ejecución para $Re$, $T$ o naturaleza del fluido. Ver sección *Limitaciones* del `README.md`.

---

## 11. Referencias

1. Brater, E.F. et al. *Handbook of Hydraulics*.
2. Cengel, Y.A. & Cimbala, J.M. *Mecánica de Fluidos* (2ª Ed.).
3. Rocha, A. *Hidráulica de Tuberías y Canales*.
4. Mendez, M.V. *Tuberías a Presión*.
5. ESHA. *Guía para el Desarrollo de una Pequeña Central Hidroeléctrica*.
6. Silowash, B. *Piping Systems Manual*.
7. AWWA. *Fiberglass Pipe Design (M45, 3rd Ed.)*.
8. Karassik, I.J. *Pump Handbook* (4th Ed.).
9. Leishear, R.A. *Fluid Mechanics, Water Hammer, Dynamic Stresses...*.
10. Liria, J. *Canales Hidráulicos* (cap. 3, fórmulas de Manning en tuberías).
11. Síntesis *Manning* (notas de taller).

**Memorias de cálculo consultadas:** CARHUAC, SANTARI, ZANA (aplicación de Darcy-Weisbach en túneles y tuberías de presión de centrales hidroeléctricas peruanas).

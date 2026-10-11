# Marco Teórico — Línea de Energía Desarenador → Bocatoma

## 1. Ecuación de Bernoulli / Balance de energía

La ecuación fundamental que gobierna el programa es el teorema de Bernoulli para fluido real (con pérdidas):

$$
\frac{v_1^2}{2g} + \frac{p_1}{\gamma} + z_1 = \frac{v_2^2}{2g} + \frac{p_2}{\gamma} + z_2 + h_f
$$

En canales abiertos, la presión en la superficie libre es atmosférica ($p = 0$):

$$
z_1 + y_1 + \frac{v_1^2}{2g} = z_2 + y_2 + \frac{v_2^2}{2g} + h_f
$$

**Niveles hidráulicos:**
- **Nivel de agua (NA):** $NA = z + y$
- **Nivel de energía (NE):** $NE = z + y + v^2/(2g)$
- **Energía específica:** $E = y + v^2/(2g)$ (referida al fondo)
- **Carga de velocidad:** $h_v = v^2/(2g)$

> **Fuentes:** Rocha §3.2, Warnick §3.2, ESHA §2.2.1

**Aplicación en memorias de cálculo:** Las 18 memorias usan "aplicación reiterada del teorema de Bernoulli" para calcular niveles entre secciones del desarenador a la bocatoma.

---

## 2. Pérdidas por transición (contracción / expansión)

### 2.1 Fórmula general

$$
h_L = k \cdot \left| \frac{v_1^2}{2g} - \frac{v_2^2}{2g} \right| = k \cdot |h_{v1} - h_{v2}|
$$

### 2.2 Coeficientes de pérdida

| Tipo | $k$ | Fuente |
|------|-----|--------|
| **Contracción** | 0.30 | Memorias de cálculo, ANA, Mery |
| **Expansión** | 0.50 | Memorias de cálculo, ANA, Mery |

**Valores según tipo de transición (Mery, Tabla 2.16):**

| Geometría | Entrada ($k_s$) | Salida ($k_e$) |
|-----------|-----------------|-----------------|
| Línea recta (broken-back) | 0.30 | 0.50 |
| Reglada (warped) | 0.20 | 0.30 |
| Ext. cuadrados | 0.30 | 0.75 |
| En curva | 0.10 | — |

El programa usa los valores estándar de memorias de cálculo peruanas: $k_s = 0.30$ (contracción), $k_e = 0.50$ (expansión).

> **Fuentes:** Mery §2.16; ANA cap. transiciones; Villón Tabla 1.1

---

## 3. Pérdidas en rejillas — Fórmula de Kirschmer

### 3.1 Ecuación de Kirschmer

$$
h_r = \beta \cdot \left( \frac{e}{s} \right)^{4/3} \cdot \frac{v^2}{2g} \cdot \sin\alpha
$$

Donde:
- $\beta$ = coeficiente de forma de la barra (adimensional)
- $e$ = espesor de la barra [mm]
- $s$ = separación libre entre barras [mm]
- $v$ = velocidad de aproximación [m/s]
- $\alpha$ = ángulo de inclinación de la rejilla respecto a la horizontal [°]

### 3.2 Coeficiente de forma ($\beta$) según perfil de barra

| Perfil | $\beta$ |
|--------|---------|
| Nariz y cola cuadradas, $L/s = 5$ | **2.42** |
| Nariz cuadrada, cola semicircular | 1.83 |
| Nariz y cola semicirculares | 1.67 |
| Nariz y cola redondeadas | 1.79 |
| Perfil aerodinámico (airfoil) | 0.76 |

El programa usa $\beta = 2.42$ (barras rectangulares, caso más común y conservador).

> **Fuentes:** Novak Tabla 9.2 (fórmula original de Kirschmer), Krochin §10.2, Chow §7.12

### 3.3 Velocidad de aproximación

Valores recomendados por Krochin (citando a Sokolov):
- Obras grandes: hasta 2.5 m/s
- Obras pequeñas/medianas: 0.5 a 1.2 m/s
- Para turbinas: 0.6 m/s

> **Fuentes:** Krochin §10.2

---

## 4. Tranquilizadores (baffles / flow straighteners)

### 4.1 Función

Los tranquilizadores son rejas dispuestas transversalmente en una transición para:
1. Uniformizar la distribución de velocidades
2. Disipar energía cinética excedente
3. Evitar la formación de vórtices y zonas muertas

### 4.2 Cálculo de pérdidas

No existe una fórmula específica para tranquilizadores. **Las memorias de cálculo peruanas aplican la fórmula de Kirschmer** a cada barra del tranquilizador:

$$
h_T = \beta \cdot \left( \frac{e}{s} \right)^{4/3} \cdot \frac{v_0^2}{2g} \cdot \sin\alpha
$$

Con $\beta = 2.42$, $\alpha = 90°$ (barras verticales).

**Disposición típica:**
- 2 a 3 tranquilizadores espaciados a lo largo de la transición (~cada 3 m)
- Área creciente hacia aguas abajo → velocidad decreciente
- Pérdida total = suma de pérdidas individuales
- Pérdida típica: ~0.02-0.03 m (despreciable frente a otras pérdidas)

> **Fuentes:** Memorias CARHUAC l.206-253 ("se evalúa tomando como guía la fórmula de Kirschmer, ya que no existe una fórmula específica para este caso"), SANTARI l.143-184, Mery §2.130 (cita a Bouvard)

### 4.3 Nota sobre el algoritmo (`calc_tranq`)

El programa distribuye $n = \max(2, \text{round}(L/3))$ tranquilizadores uniformemente a lo largo de la transición. Para cada posición $x$:
1. Interpola linealmente $y(x)$ y $b(x)$ entre secciones de aguas abajo y aguas arriba
2. Calcula área local y velocidad
3. Aplica Kirschmer y acumula

> **Advertencia:** El código contiene un ajuste temporal `area_local = b_local * y_local + 8`. Este término está marcado como FIXME y debe resolverse antes de usar resultados en producción. Ver `observaciones.md` #1.

---

## 5. Número de Froude y régimen de flujo

### 5.1 Definición

$$
Fr = \frac{v}{\sqrt{g \cdot y}}
$$

Para sección rectangular (ancho $b$, tirante $y$):

$$
Fr = \frac{Q}{b \cdot y \cdot \sqrt{g \cdot y}}
$$

### 5.2 Interpretación física

$$
Fr = \sqrt{\frac{\text{Fuerzas de inercia}}{\text{Fuerzas gravitacionales}}}
$$

### 5.3 Clasificación de régimen

| $Fr$ | Régimen | Comportamiento |
|------|---------|----------------|
| $Fr < 0.99$ | **Subcrítico** (río) | Control desde aguas abajo, $v < v_c$ |
| $0.99 \leq Fr \leq 1.01$ | **Crítico** | $v = v_c$, energía específica mínima |
| $Fr > 1.01$ | **Supercrítico** (torrente) | Control desde aguas arriba, $v > v_c$ |

### 5.4 Criterio de diseño en CH peruanas

Las memorias de cálculo limitan el número de Froude a **$Fr \leq 0.70$** en canales de conducción. Este criterio asegura:
- Margen de seguridad ante obstrucciones
- Flujo estable sin ondas cruzadas
- Transiciones graduales sin resalto

> **Fuentes:** Rocha §4.2, Krochin §7.5, ESHA §5.2.2, Chow §2.3

---

## 6. Tirante crítico (referencia para bisección)

El tirante crítico $y_c$ para sección rectangular es el límite inferior del rango de búsqueda en los solvers iterativos:

$$
y_c = \left( \frac{Q^2}{b^2 \cdot g} \right)^{1/3}
$$

En régimen subcrítico (el caso normal en desarenadores), $y > y_c$.

---

## 7. Solución numérica — Bisección

### 7.1 Algoritmo general

Para encontrar el tirante $y$ que satisface el balance de energía:

$$
E_{\text{target}} = z + y + \frac{Q^2}{2g \cdot b^2 \cdot y^2}
$$

1. Definir rango: $y_{\text{min}} = y_c + 0.001$, $y_{\text{max}} = y_{\text{min}} + 5.0$
2. Bisección: evaluar signo de $E_{\text{target}} - (z + y + h_v)$
3. Convergencia: $|\text{diferencia}| < 0.01$ m (precisión de cm)

### 7.2 Estrategia de redondeo

El programa publica resultados redondeados a 0.01 m (cm), consistente con la precisión de diseño en obra civil. Los solvers usan precisión float completa para navegar, pero verifican convergencia con los valores redondeados que verá el usuario.

### 7.3 Fallback

Si ningún tirante discretizado a 0.01 m converge en 100 iteraciones, se retorna el mejor candidato (menor $|\text{dif}|$). El error está siempre dentro de la precisión de diseño.

---

## 8. Sección rectangular — Propiedades hidráulicas

Para sección rectangular de ancho $b$ y tirante $y$:

| Propiedad | Expresión |
|-----------|-----------|
| Área | $A = b \cdot y$ |
| Velocidad media | $v = Q / A$ |
| Carga de velocidad | $h_v = v^2 / (2g)$ |
| Energía específica | $E = y + h_v$ |
| Tirante crítico | $y_c = (Q^2 / (b^2 \cdot g))^{1/3}$ |
| Froude | $Fr = v / \sqrt{g \cdot y}$ |

---

## 9. Tipos de nodo en el programa

| Nodo | Entrada | Salida | Algoritmo |
|------|---------|--------|-----------|
| **Sección inicial** | $Q, b, y, z$ | `SeccionHidraulica` | Directo |
| **Transición** | Sección anterior, $b_{\text{nuevo}}, z_{\text{nuevo}}$, tipo | Nueva sección con $y$ resuelto | Bisección con $h_L = k \cdot \|h_{v0} - h_{v1}\|$ |
| **Tranquilizadores** | Secciones aguas abajo y arriba, $L, \beta, e, s, \alpha$ | Nueva sección con $y + h_L$ | Kirschmer distribuido |
| **Rejillas en serie** | Sección anterior, lista de rejillas (cada una con $e, s, b, z, \alpha, \beta$) | Nueva sección con $y$ resuelto | Kirschmer acumulado + bisección |
| **Pérdida directa** | Sección anterior, $\Delta y$ | Nueva sección con $y + \Delta y$ | Directo (no itera) |

---

## 10. Referencias

- Rocha, A. *Hidráulica de Tuberías y Canales*
- Krochin, S. *Diseño Hidráulico*
- Chow, V.T. *Hidráulica de Canales Abiertos*
- Chanson, H. *Hydraulics of Open Channel Flow*
- Novak, P. et al. *Hydraulic Structures*
- Mery, H. *Hidráulica Aplicada al Diseño de Obras*
- Villón, M. *Diseño de Estructuras Hidráulicas*
- ANA. *Criterios de Diseño de Obras Hidráulicas*
- Warnick, C.C. *Hydropower Engineering*
- ESHA. *Guía para el Desarrollo de una Pequeña Central Hidroeléctrica*
- ASME. *The Guide to Hydropower Mechanical Design*

**Memorias de cálculo consultadas:** CARHUAC, SANTARI, CHANCAY II, MARAÑÓN, ZANA, BAÑOS V, CAPILLUCAS (aplicación directa del método de Bernoulli entre secciones).

---

*Ver también:* `observaciones.md` (hallazgos de revisión 2026-07-12), `CHANGELOG.md` (historial de cambios del programa)

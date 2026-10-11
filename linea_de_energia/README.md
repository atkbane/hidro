# Línea de Energía — Desarenador → Bocatoma

Calcula la línea de energía entre un desarenador y una bocatoma aplicando el teorema de Bernoulli con pérdidas por transición (contracción/expansión), rejillas (Kirschmer) y tranquilizadores.  
Pensado para ingenieros civiles que necesitan verificar niveles hidráulicos en cadenas de nodos secuenciales para centrales hidroeléctricas.

---

## 🌐 Acceso web

Abre la aplicación directamente desde el navegador, sin instalación:  
👉 [https://hidro.rfntc.com/linea_de_energia/](https://hidro.rfntc.com/linea_de_energia/)

> Funciona completamente en el navegador. No envía datos a ningún servidor.

---

## 📐 Base teórica

### Ecuación de Bernoulli para canales abiertos

$$
z_1 + y_1 + \frac{v_1^2}{2g} = z_2 + y_2 + \frac{v_2^2}{2g} + h_f
$$

### Tipos de nodo y pérdidas

| Nodo | Pérdida | Algoritmo |
|------|---------|-----------|
| **Sección inicial** | — | Directo |
| **Transición** (contracción/expansión) | $h_L = k \cdot \|h_{v0} - h_{v1}\|$, $k_s = 0.30$, $k_e = 0.50$ | Bisección |
| **Tranquilizadores** | $h_T = \beta \cdot (e/s)^{4/3} \cdot v^2/(2g) \cdot \sin\alpha$, $\beta = 2.42$ | Kirschmer distribuido |
| **Rejillas en serie** | Kirschmer por rejilla, balance de energía acumulado | Kirschmer + bisección |
| **Pérdida directa** | $\Delta y$ fijo | Directo |

### Fórmulas principales

| Concepto | Expresión | Parámetros |
|----------|-----------|------------|
| Kirschmer | $h_r = \beta \cdot (e/s)^{4/3} \cdot v^2/(2g) \cdot \sin\alpha$ | $\beta$: coef. forma, $e$: espesor [mm], $s$: separación [mm], $\alpha$: inclinación [°] |
| Pérdida por transición | $h_L = k \cdot \|v_1^2/(2g) - v_2^2/(2g)\|$ | $k = 0.30$ (contracción), $k = 0.50$ (expansión) |
| Tirante crítico | $y_c = (Q^2 / (b^2 \cdot g))^{1/3}$ | Límite inferior de bisección |
| Número de Froude | $Fr = v / \sqrt{g \cdot y}$ | Clasifica régimen subcrítico/crítico/supercrítico |

### Supuestos del modelo

- Sección rectangular en todos los nodos ($A = b \cdot y$).
- Flujo en régimen subcrítico ($Fr < 0.99$).
- Coeficiente de forma de barras $\beta = 2.42$ (rectangular, caso conservador).
- Tranquilizadores calculados con la fórmula de Kirschmer ($\alpha = 90°$).
- Los niveles se publican redondeados a 0.01 m (precisión de cm en obra civil).
- Resultados de bisección convergen con tolerancia de 0.01 m.

---

## ✨ Características

- **Cadena secuencial de nodos** — encadena secciones iniciales, transiciones, tranquilizadores, rejillas y pérdidas directas.
- **Rejillas en serie** — cada rejilla con su propia cota $z$, ancho $b$, espesor $e$, separación $s$ y ángulo $\alpha$.
- **Balance de energía por bisección** — resuelve el tirante que satisface $E_{\text{target}} = z + y + v^2/(2g)$.
- **Tranquilizadores con Kirschmer** — distribuidos automáticamente a lo largo de la transición ($\sim$cada 3 m).
- **Número de Froude** — clasifica el régimen de cada sección (subcrítico/crítico/supercrítico).
- **Interfaz web sin instalación** — Pyodide ejecuta Python en el navegador.

---

## 🧪 Cómo usar

1. **Crea una sección inicial** — ingresa caudal $Q$, ancho $b$, tirante $y$ y cota $z$.
2. **Agrega nodos secuencialmente** — selecciona el tipo (Transición, Tranquilizadores, Rejillas, Pérdida directa).
3. **Configura cada nodo** — ancho, cota, tipo de transición, parámetros de rejillas, etc.
4. **Presiona "Calcular"** — los resultados de cada sección aparecen encadenados, mostrando $y$, $v$, $h_v$, $Fr$, $NA$, $NE$ y $h_L$.

Para reiniciar, presiona **"Limpiar"**.

---

## 🛠️ Tecnologías

- [Python](https://python.org) — Lógica de cálculo hidráulico (solo `math`, sin numpy).
- [Pyodide](https://pyodide.org) — Python en el navegador vía WebAssembly.

---

## 📁 Estructura del proyecto

```
linea_de_energia/
├── core.py              # Motor de cálculo (SeccionHidraulica, bisección, Kirschmer)
├── web_bridge.py         # Puente Python/Pyodide para la versión web
├── index.html            # Interfaz web
├── marco_teorico.md      # Documentación teórica completa
└── README.md
```

---

## 📄 Licencia

Este proyecto se distribuye bajo la licencia **MIT**. Consulta el archivo [LICENSE](../LICENSE) para más detalles.

## 👨‍💻 Autor

Creado por Rufino Tapia – ingeniero civil hidráulico.

# Simulador de Vaciado de Desarenador

Simulador web del vaciado de un desarenador rectangular de fondo horizontal.  
Pensado para ingenieros civiles, estudiantes o profesionales que necesiten estimar el tiempo de vaciado y la evolución del caudal de salida.

---

## 🌐 Acceso web

Abre la aplicación directamente desde el navegador, sin instalación:  
👉 [https://hidro.rfntc.com/vaciado_desarenador/](https://hidro.rfntc.com/vaciado_desarenador/)

> Funciona completamente en el navegador. No envía datos a ningún servidor.

---

## 📐 Base teórica

### Fórmulas principales

| Concepto          | Expresión                                              | Parámetros clave          |
|-------------------|--------------------------------------------------------|---------------------------|
| Caudal (orificio) | `Q = Cd_orif · (B·a(t)) · √(2g·h_ef)`                 | `a(t)` = apertura en t    |
| Caudal (vertedero)| `Q = (2/3) · Cd_weir · B · √(2g) · h^1.5`             | —                         |
| Combinación       | `Q = w · Q_orif + (1−w) · Q_weir`                     | `w` = función sigmoide    |
| Continuidad       | `dh/dt = −Q(t) / (L·W)`                               | Integrada con RK45        |
| Apertura lineal   | `a(t) = (d/t_open) · t`  para `t < t_open`            | Luego `a(t) = d`          |

La transición entre régimen de orificio y vertedero se hace de forma continua mediante una **función sigmoide**, evitando discontinuidades en el caudal.

### Supuestos del modelo

- Geometría rectangular constante (largo `L`, ancho `W`). Fondo horizontal, sin pendiente.
- Compuerta rectangular (ancho `B`, altura `d`) con apertura lineal en el tiempo `t_open`.
- Las únicas pérdidas consideradas son por contracción en la salida (`Cd_orif`, `Cd_weir`).
- No se incluye fricción en el canal ni efectos tridimensionales.
- Modelo válido para anteproyectos y estudios preliminares.

---

## ✨ Características

- **Modelo combinado orificio‑vertedero** – transición suave entre regímenes mediante sigmoide.
- **Apertura progresiva de compuerta** – simulación realista de la maniobra de vaciado.
- **Gráfico interactivo** – nivel h (m) y caudal Q (m³/s) vs. tiempo en doble eje Y.
- **Panel de resumen** – tiempo de vaciado, caudal máximo, tiempo de apertura y nivel inicial.
- **Marcadores de eventos** – fin de apertura (línea verde) y vaciado completo (línea roja).
- **Responsive** – funciona en móviles y escritorio.

---

## 🧪 Cómo usar

1. Ingresa los parámetros geométricos del desarenador (L, W) y de la compuerta (B, d, t_open).
2. Define el nivel inicial `h0`, el nivel de parada `h_parada` y los coeficientes Cd.
3. Presiona **Calcular**.
4. El gráfico y el panel de resumen se actualizan automáticamente.

---

## 🛠️ Tecnologías

- [Pyodide v0.26.4](https://pyodide.org/) — Python en el navegador vía WebAssembly
- [Plotly.js v2.35.2](https://plotly.com/javascript/) — gráficos interactivos
- HTML5, CSS3, JavaScript vanilla
- Python 3.12 con NumPy y SciPy

---

## 📁 Estructura del proyecto

```
vaciado_desarenador/
├── calculos.py        # Lógica hidráulica (caudal, solver ODE)
├── web_bridge.py      # Puente Python/Pyodide para la web
├── index.html         # Interfaz web (Pyodide + Plotly)
├── marco_teorico.md   # Base teórica con mapeo a funciones
└── README.md
```

---

## 📄 Licencia

Este proyecto se distribuye bajo la licencia **MIT**. Consulta el archivo [LICENSE](../LICENSE) para más detalles.

## 👨‍💻 Autor

Creado por Rufino Tapia – ingeniero civil hidráulico.

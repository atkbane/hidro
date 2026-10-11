# Pérdida de Carga en Tuberías

Calculadora web de pérdidas de carga en tuberías circulares a presión.  
Pensada para ingenieros civiles, estudiantes o profesionales que necesiten estimar fricciones y pérdidas localizadas en sistemas de tuberías a presión.

---

## 🌐 Acceso web

Abre la aplicación directamente desde el navegador, sin instalación:  
👉 [https://hidro.rfntc.com/perdida_de_carga_tuberias/](https://hidro.rfntc.com/perdida_de_carga_tuberias/)

> Funciona completamente en el navegador. No envía datos a ningún servidor.

---

## 📐 Base teórica

### Fórmulas principales

| Método           | Expresión                                           | Coeficiente        |
|------------------|-----------------------------------------------------|--------------------|
| Darcy‑Weisbach   | `hf = f · (8/(π²·g)) · Q² · L / D⁵`                | Rugosidad `k` (mm) |
| Hazen‑Williams   | `hf = 10.67 · L · Q^1.852 / (C^1.852 · D^4.87)`    | Coeficiente `C`    |
| Manning          | `hf = 10.29 · n² · L · Q² / D^5.333`               | Rugosidad `n`      |
| Pérd. localizada | `h_local = K · V²/(2g)`                             | Coef. `K` (entrada/salida) |
| Potencia perdida | `P = γ · Q · h_total`  (γ = 9.81 kN/m³)            | Resultado en kW o MW |

El factor de fricción `f` de Darcy‑Weisbach se calcula con la aproximación explícita de **Swamee‑Jain**, asumiendo agua a 20 °C (ν = 1.004×10⁻⁶ m²/s).

---

## ✨ Características

- **Tres métodos de cálculo** – selecciona el más adecuado según el material y fluido.
- **Segmentación dinámica** – añade o elimina tramos de tubería sin límite práctico.
- **Pérdidas localizadas** – coeficiente K de entrada (primer segmento) y de salida (último segmento).
- **Resultados por tramo** – velocidad media, pérdida por fricción, pérdida total y potencia perdida.
- **Validación de entrada** – resalta campos inválidos con mensajes descriptivos.
- **Responsive** – funciona en móviles y escritorio.

---

## 🧪 Cómo usar

1. Ingresa el título del proyecto y el caudal Q (m³/s).
2. Selecciona el método de cálculo.
3. Ajusta los coeficientes K de entrada y salida.
4. Añade los segmentos de tubería: longitud L (m), diámetro D (m) y coeficiente según el método.
5. Presiona **Calcular**.
6. Los resultados aparecen en el panel derecho sin recargar la página.

---

## ⚠️ Limitaciones

- **Swamee-Jain (Darcy-Weisbach) es válida solo para régimen turbulento** ($Re > 5000$). Para régimen laminar ($Re < 2300$) o transicional ($2300 < Re < 4000$) los resultados del factor de fricción no son confiables. Ver marco teórico §2.2 y §3.2.
- **Viscosidad del agua fijada a 20 °C** ($\nu = 1{,}004 \times 10^{-6}$ m²/s). Para temperaturas distintas el número de Reynolds y por tanto el factor `f` se desvían. La constante está documentada en `calculos.py:15` y justificada en marco teórico §3.1.
- **Manning en tuberías a presión** es una extensión empírica. Darcy-Weisbach o Hazen-Williams son preferibles cuando se dispone de los datos de rugosidad o coeficiente del material.

El programa es una herramienta de cálculo, no un sistema experto. El ingeniero interpreta los resultados.

---

## 🛠️ Tecnologías

- [Pyodide v0.26.4](https://pyodide.org/) — Python en el navegador vía WebAssembly
- HTML5, CSS3, JavaScript vanilla
- Python 3.12 (biblioteca estándar: `math`, `dataclasses`, `typing`)

---

## 📁 Estructura del proyecto

```
perdida_de_carga_tuberias/
├── calculos.py       # Lógica hidráulica (fricción, pérdidas, modelos)
├── web_bridge.py     # Puente Python/Pyodide para la versión web
├── index.html        # Interfaz web
└── README.md
```

---

## 📄 Licencia

Este proyecto se distribuye bajo la licencia **MIT**. Consulta el archivo [LICENSE](../LICENSE) para más detalles.

## 👨‍💻 Autor

Creado por Rufino Tapia – ingeniero civil hidráulico.

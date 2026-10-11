# 🧰 Hidro — Herramientas de Cálculo

Calculadoras de ingeniería hidráulica que ejecutan **Python en el navegador** (vía [Pyodide](https://pyodide.org)) — sin instalación, sin servidor. Todo el cálculo corre en el dispositivo del visitante.

🌐 **En línea:** <https://hidro.rfntc.com/>

---

## Herramientas

| Herramienta | Descripción | Enlace |
|-------------|-------------|--------|
| **Vaciado de Desarenador** | Simulación del vaciado de un desarenador rectangular. Transición orificio→vertedero con sigmoide, integración ODE. | [Abrir](https://hidro.rfntc.com/vaciado_desarenador/) |
| **Pérdida de Carga en Tuberías** | Fricción y pérdidas localizadas en tuberías a presión. Darcy‑Weisbach, Hazen‑Williams, Manning. | [Abrir](https://hidro.rfntc.com/perdida_de_carga_tuberias/) |
| **Diseño de Desarenador** | Dimensionamiento de naves de sedimentación. Camp, Shields, Zanke. Bisel dinámico. | [Abrir](https://hidro.rfntc.com/diseno_desarenador/) |
| **Línea de Energía** | Bernoulli encadenado: desarenador → bocatoma. Transiciones, rejillas (Kirschmer), tranquilizadores. | [Abrir](https://hidro.rfntc.com/linea_de_energia/) |

---

## Estructura del repositorio

```
hidro/
├── index.html                    # Landing con enlaces a las 4 herramientas
├── diseno_desarenador/           # Cálculo + UI (Pyodide)
├── vaciado_desarenador/          # Cálculo + UI (Pyodide + Plotly)
├── perdida_de_carga_tuberias/    # Cálculo + UI (Pyodide)
└── linea_de_energia/             # Cálculo + UI (Pyodide)
```

Cada herramienta es **autocontenida**: su `index.html`, su módulo de cálculo (`.py`), su puente `web_bridge.py` y su `marco_teorico.md`. No hay código compartido entre herramientas — cada una conserva sus propias constantes y fórmulas.

---

## Tecnologías

- [Pyodide v0.26.4](https://pyodide.org/) — Python en el navegador vía WebAssembly
- [Plotly.js](https://plotly.com/javascript/) — gráficos interactivos (solo *Vaciado de Desarenador*)
- HTML5, CSS3, JavaScript vanilla
- Python 3.12 — NumPy y SciPy (solo *Vaciado de Desarenador*)

---

## Fuente de verdad

Este repositorio es el **espejo de publicación** de las herramientas. La fuente de verdad (notas de cálculo, pruebas y experimentos en marimo/Jupyter) vive en el monorepo de autoría. Los cambios se desarrollan y verifican allí y se exportan aquí.

---

## 📄 Licencia

**MIT** — consulta el archivo [LICENSE](LICENSE).

## 👨‍💻 Autor

Creado por Rufino Tapia — ingeniero civil hidráulico.

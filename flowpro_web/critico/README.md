# Tirante y pendiente crítica

Calculadora web del **régimen crítico** de un canal abierto prismático: tirante crítico
(`Fr = 1`) y pendiente crítica.

Reimplementación limpia de la herramienta *Critical Depth and Slope* de **Flow Pro 2.1**.

---

## 🌐 Acceso web

👉 [https://hidro.rfntc.com/flowpro_web/critico/](https://hidro.rfntc.com/flowpro_web/critico/)

> Funciona completamente en el navegador. No envía datos a ningún servidor.

---

## 📐 Base teórica

Energía específica mínima (número de Froude = 1):

```
Q²·T / (g·A³) = 1
```

Pendiente crítica (Manning evaluado en el tirante crítico):

```
Sc = ( n·Q / (k · A_c · R_c^(2/3)) )²
```

Interpretación: `S₀ > Sc` ⇒ pendiente fuerte (supercrítico); `S₀ < Sc` ⇒ pendiente suave
(subcrítico). Detalle en [`marco_teorico.md`](marco_teorico.md).

---

## 📁 Estructura

```
critico/
├── calculos.py       # Geometría, tirante crítico (bisección) y pendiente crítica
├── web_bridge.py     # Puente Python/Pyodide
├── index.html        # Interfaz web
├── marco_teorico.md  # Base teórica
└── README.md
```

---

## ⚠️ Limitaciones

- Secciones **U** y **circular alargada** pendientes de verificación.
- Solo canal abierto (no conducto a presión).

---

## 📄 Licencia

MIT — consulta [LICENSE](../../LICENSE).

## 👨‍💻 Autor

Creado por Rufino Tapia – ingeniero civil hidráulico.

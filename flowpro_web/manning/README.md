# Tirante normal y Manning

Calculadora web de **canal abierto** por la ecuación de Manning. Resuelve el tirante
normal, el caudal, la pendiente o la rugosidad de un canal prismático y reporta velocidad,
área, perímetro mojado y radio hidráulico.

Es una **reimplementación limpia** de la herramienta *Depth, Flowrate, Slope, and
Roughness* de **Flow Pro 2.1** (ProSoft Apps), construida solo a partir de la ecuación de
Manning y la geometría estándar de las secciones. No contiene código del programa original.

---

## 🌐 Acceso web

Abre la aplicación directamente desde el navegador, sin instalación:
👉 [https://hidro.rfntc.com/flowpro_web/manning/](https://hidro.rfntc.com/flowpro_web/manning/)

> Funciona completamente en el navegador. No envía datos a ningún servidor.

---

## 📐 Base teórica

Ecuación de Manning:

```
Q = (k/n) · A · R^(2/3) · S^(1/2)          R = A/P
```

con `k = 1.000` en SI y `k = 1.486` en unidades inglesas.

| Incógnita | Datos requeridos |
|---|---|
| Tirante `y` | `Q`, `n`, `S` |
| Caudal `Q` | `y`, `n`, `S` |
| Pendiente `S` | `Q`, `y`, `n` |
| Rugosidad `n` | `Q`, `y`, `S` |

Geometría soportada: **trapezoidal** (rectangular `m = 0`, triangular `b = 0`) y **circular**.
El detalle completo está en [`marco_teorico.md`](marco_teorico.md).

---

## ✨ Características

- **Cuatro incógnitas** — pestañas Tirante / Caudal / Pendiente / Rugosidad, como el original.
- **Dos sistemas de unidades** — SI (m, m³/s) e inglés (ft, ft³/s); cambia la etiqueta y el factor `k`.
- **Salidas completas** — tirante, velocidad, área, perímetro mojado y radio hidráulico.
- **Régimen de flujo** — número de Froude y clasificación (sub/super/crítico).
- **Recálculo en vivo** — el resultado se actualiza al escribir, sin botón "Calcular".
- **Memoria de cálculo** — reporte en texto copiable al final.

---

## 🧪 Cómo usar

1. Elige el sistema de unidades.
2. Elige la incógnita a despejar (pestaña) y el tipo de sección.
3. Completa los datos restantes; el resultado aparece en vivo a la derecha.
4. Despliega **Memoria de cálculo** para copiar el reporte.

---

## ⚠️ Limitaciones

- **Canal abierto** únicamente: no modela conducto lleno a presión. En circular, si el caudal
  excede la capacidad de la sección llena, se avisa.
- **Secciones U y circular alargada** aún no implementadas (geometría pendiente de verificar).
- Sesión de alcance: reproduce la herramienta de **Manning**. Las demás herramientas de
  Flow Pro (tirante crítico, perfil de superficie, orificios, compuertas, vertederos) se
  añadirán por separado.

El programa es una herramienta de cálculo, no un sistema experto. El ingeniero interpreta
los resultados.

---

## 🛠️ Tecnologías

- [Pyodide v0.26.4](https://pyodide.org/) — Python en el navegador vía WebAssembly
- HTML5, CSS3, JavaScript vanilla
- Python 3.12 (biblioteca estándar: `math`, `dataclasses`, `typing`)

---

## 📁 Estructura del proyecto

```
flowpro_web/
├── calculos.py       # Núcleo hidráulico (geometría, Manning, resolución)
├── web_bridge.py     # Puente Python/Pyodide para la versión web
├── index.html        # Interfaz web
├── marco_teorico.md  # Base teórica y verificación
└── README.md
```

---

## 📄 Licencia

Este proyecto se distribuye bajo la licencia **MIT**. Consulta el archivo [LICENSE](../../LICENSE) para más detalles.

## 👨‍💻 Autor

Creado por Rufino Tapia – ingeniero civil hidráulico.

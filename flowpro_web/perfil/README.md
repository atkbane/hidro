# Perfil de superficie libre

Calculadora web del **perfil de flujo gradualmente variado** (GVF) en un canal abierto
prismático, por el método de paso directo con integración de Simpson 1/3.

Reimplementación limpia de la herramienta *Water Surface Profile* de **Flow Pro 2.1**.

---

## 🌐 Acceso web

👉 [https://hidro.rfntc.com/flowpro_web/perfil/](https://hidro.rfntc.com/flowpro_web/perfil/)

> Funciona completamente en el navegador. No envía datos a ningún servidor.

---

## 📐 Base teórica

```
dx/dy = (1 − Fr²) / (S₀ − S_f)          S_f = (Q·n/k)²·P^(4/3)/A^(10/3)
```

Salidas: tirante normal y crítico (con sus áreas), tipo de perfil (`mild, M-2`, `steep, S-2`…),
tipo de flujo (sub/supercrítico) y la tabla del perfil por estaciones (tirante, energía, área,
velocidad, ancho superior, momentum, Froude, carga de velocidad, radio y perímetro).

Detalle en [`marco_teorico.md`](marco_teorico.md).

---

## ✨ Características

- **Paso directo + Simpson 1/3** — como el original, más preciso que el *standard step* de paso fijo.
- **Clasificación automática** del perfil (M/S/C/H/A · 1/2/3) y del tipo de flujo.
- **Columna Froude configurable** — `Fr` real o `Fr²` como el original.
- **Estaciones en cadena** (`1+00.000`) y tabla desplazable.
- **Recálculo en vivo** y memoria de cálculo copiable.

---

## ⚠️ Limitaciones

- Secciones **U** y **circular alargada** pendientes de verificación.
- Régimen permanente, canal prismático, sin estructuras dentro del perfil.
- Si el caudal excede la capacidad de la sección, se avisa (resultado referencial).

---

## 📁 Estructura

```
perfil/
├── calculos.py       # Geometría, tirantes de referencia, integración del perfil
├── web_bridge.py     # Puente Python/Pyodide
├── index.html        # Interfaz web + tabla
├── marco_teorico.md  # Base teórica y verificación
└── README.md
```

---

## 📄 Licencia

MIT — consulta [LICENSE](../../LICENSE).

## 👨‍💻 Autor

Creado por Rufino Tapia – ingeniero civil hidráulico.

# Compuertas de fondo

Calculadora web del **caudal y la velocidad** bajo una compuerta en un canal rectangular
(vertical, radial/tainter o tambor), en descarga libre.

Reimplementación limpia de la herramienta *Underflow Gates* de **Flow Pro 2.1**.

---

## 🌐 Acceso web

👉 [https://hidro.rfntc.com/flowpro_web/compuertas/](https://hidro.rfntc.com/flowpro_web/compuertas/)

> Funciona completamente en el navegador. No envía datos a ningún servidor.

---

## 📐 Base teórica

```
Q = C_d · b · a · √(2·g·y₁)          V = Q / (b·a)
```

`C_d` por defecto **0.61** (vertical). Para radial/tambor, ≈0.65. Detalle en
[`marco_teorico.md`](marco_teorico.md).

---

## ⚠️ Limitaciones

- **Descarga libre** únicamente (no modela sumergido ni resalto).
- La convención exacta de `C_d` de Flow Pro queda por contrastar con un caso real.

---

## 📁 Estructura

```
compuertas/
├── calculos.py       # Descarga libre bajo compuerta
├── web_bridge.py     # Puente Python/Pyodide
├── index.html        # Interfaz web
├── marco_teorico.md  # Base teórica
└── README.md
```

---

## 📄 Licencia

MIT — consulta [LICENSE](../../LICENSE).

## 👨‍💻 Autor

Creado por Rufino Tapia – ingeniero civil hidráulico.

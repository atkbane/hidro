# Vertederos

Calculadora web del **caudal sobre un vertedero**: rectangular, triangular (V) o Cipolletti,
en pared delgada o cresta ancha, **libre** o **sumergido**.

Reimplementación limpia de la herramienta *Weirs* de **Flow Pro 2.1**.

---

## 🌐 Acceso web

👉 [https://hidro.rfntc.com/flowpro_web/vertederos/](https://hidro.rfntc.com/flowpro_web/vertederos/)

> Funciona completamente en el navegador. No envía datos a ningún servidor.

---

## 📐 Base teórica

```
Rectangular / Cipolletti :  Q = C_d·(2/3)·√(2g)·L·H^(3/2)
Triangular (V)           :  Q = C_d·(8/15)·√(2g)·tan(θ/2)·H^(5/2)
Sumergido (Villemonte)   :  Q_s/Q_f = [1 − (H₂/H₁)^n]^0.385
```

`C_d` por defecto **0.61** (pared delgada) · **0.577** (cresta ancha) · `n = 3/2` (rect./Cipolletti),
`n = 5/2` (triangular). Detalle en [`marco_teorico.md`](marco_teorico.md).

---

## ⚠️ Limitaciones

- La **convención exacta de coeficientes** de Flow Pro 2.1 no está publicada; se adopta la forma
  teórica con `C_d` adimensional. Coeficientes editables para calibrar.
- Cresta ancha sumergida: Villemonte es una aproximación.

---

## 📁 Estructura

```
vertederos/
├── calculos.py       # Formas de pared delgada/cresta ancha + Villemonte
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

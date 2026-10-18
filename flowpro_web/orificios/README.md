# Orificios

Calculadora web del **caudal por un orificio** circular o cuadrado, a partir de su carga.

Reimplementación limpia de la herramienta *Orifices* de **Flow Pro 2.1**.

---

## 🌐 Acceso web

👉 [https://hidro.rfntc.com/flowpro_web/orificios/](https://hidro.rfntc.com/flowpro_web/orificios/)

> Funciona completamente en el navegador. No envía datos a ningún servidor.

---

## 📐 Base teórica

```
Q = C · A · √(2·g·H)
```

`C` = coeficiente de descarga · `A` = área del orificio · `H` = carga sobre el eje.

Coeficientes típicos: **0.61** borde agudo · **0.70** entrada redondeada · **0.80** bocina ·
**0.95** tobera. Detalle en [`marco_teorico.md`](marco_teorico.md).

---

## 📁 Estructura

```
orificios/
├── calculos.py       # Ecuación de descarga y área del orificio
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

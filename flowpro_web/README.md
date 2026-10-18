# Flow Pro — canal abierto (réplica web)

Suite de calculadoras de **canal abierto** que reimplementa, en la web y desde cero
(*clean-room*), las herramientas de **Flow Pro 2.1** (ProSoft Apps). Todo el cálculo corre en
el navegador vía [Pyodide](https://pyodide.org); no contiene código del programa original.

---

## 🌐 Acceso web

👉 [https://hidro.rfntc.com/flowpro_web/](https://hidro.rfntc.com/flowpro_web/)

---

## Herramientas

| Herramienta | Qué calcula | Estado |
|---|---|---|
| [Tirante normal y Manning](manning/) | tirante normal, caudal, pendiente o rugosidad | ✅ |
| [Tirante y pendiente crítica](critico/) | régimen crítico (`Fr = 1`) y pendiente crítica | ✅ |
| [Perfil de superficie libre](perfil/) | flujo gradualmente variado (paso directo + Simpson) | ✅ |
| [Orificios](orificios/) | descarga por orificio circular o cuadrado | ✅ |
| [Vertederos](vertederos/) | rectangular, triangular, Cipolletti · libre y sumergido | ✅ |
| [Compuertas de fondo](compuertas/) | caudal y velocidad bajo compuerta | ✅ |

**Pendiente:** secciones **U** y **circular alargada** (geometría no publicada por el original).

---

## Estructura

```
flowpro_web/
├── index.html        # menú de la suite
├── manning/          # Tirante normal y Manning
├── critico/          # Tirante y pendiente crítica
├── perfil/           # Perfil de superficie libre
├── orificios/        # Orificios
├── vertederos/       # Vertederos
└── compuertas/       # Compuertas de fondo
```

Cada herramienta es **autocontenida**: su `index.html`, su `calculos.py`, su `web_bridge.py`,
su `marco_teorico.md` y su `README.md`. La única pieza común es `../theme.css`.

---

## Base teórica y trazabilidad

Cada herramienta documenta sus fórmulas en su `marco_teorico.md`. El inventario del programa
original y la bibliografía utilizada están en el monorepo de autoría
(`flowpro2-fuente/flowpro-2.1-calculos.md` y `flowpro2-fuente/RESPUESTAS_flowpro_biblioteca.md`).

---

## 📄 Licencia

MIT — consulta [LICENSE](../LICENSE).

## 👨‍💻 Autor

Creado por Rufino Tapia – ingeniero civil hidráulico.

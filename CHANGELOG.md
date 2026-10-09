# Cambios

## 0.3
- WEBFISHING actualiza también `bait_unlocked`: una cantidad positiva desbloquea el cebo y puede corregir cebos editados anteriormente.
- WEBFISHING aplica los cambios al save slot activo, con respaldo y reemplazo atómico; ya no genera un archivo `.edited.sav`.
- Nombre UniversalSaveEditor en ventana, navegación, guía y ejecutable.
- Seis portadas originales con fuentes registradas.
- WEBFISHING: progreso, mejoras, inventario existente y diario.
- KH Final Mix: 154 objetos con nombre y VT/PM actuales.
- Decimales con conservación del tipo binario, verificación y respaldo.
- Distribución portátil de Windows con PyInstaller.
- 16 pruebas automatizadas. Validación dentro de los juegos pendiente.

# Cambios

## 0.2 — Interfaz PySide6

- Sustituye la interfaz Tkinter por una aplicación Qt Widgets.
- Biblioteca de seis juegos con disponibilidad explícita; dos editores implementados.
- Ilustraciones vectoriales originales para las tarjetas, sin descargas ni recursos de juegos.
- Búsqueda, filtros y navegación por colecciones.
- Editor con categorías, resumen en vivo, campos modificados y errores visibles.
- Conservación de ajustes al cambiar de pestaña, registro o sección.
- Revisión de cambios, exportación con respaldo y detección de cambios externos del original.
- Guía integrada, arrastrar y soltar y atajos de teclado.
- 13 pruebas automatizadas. Falta validar las copias dentro de los juegos.

## 0.1 — Base funcional

- Lectura de WEBFISHING y KH Final Mix de Steam.
- Edición puntual de campos, respaldo y validación de integridad.

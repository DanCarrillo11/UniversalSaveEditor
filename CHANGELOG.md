# Cambios

## 0.5
- Gestor de 454 desbloqueables de Risk of Rain 2 extraídos del catálogo instalado: personajes, habilidades, skins y recolores, artefactos, objetos, registros y altares de Newt.
- Checkboxes, búsqueda y acciones para desbloquear o restaurar categorías completas.
- Los desbloqueos se agregan o eliminan sin reserializar el resto del perfil XML.
- 22 pruebas automatizadas, incluida la edición masiva de desbloqueos sobre una copia de un perfil real.

## 0.4
- Compatibilidad inicial con perfiles XML de Risk of Rain 2: monedas lunares y estadísticas de progreso, combate y economía, con detección, respaldo y reemplazo seguro.
- Nuevo icono de memory card con fondo transparente para la aplicación y el ejecutable de Windows.
- WEBFISHING actualiza automáticamente `bait_unlocked`: cualquier cebo con cantidad positiva queda comprado y desbloqueado sin mostrar otro control.
- WEBFISHING aplica los cambios al save slot activo, con respaldo y reemplazo atómico; ya no genera un archivo `.edited.sav`.
- Nombre UniversalSaveEditor en ventana, navegación, guía y ejecutable.
- Siete portadas originales con fuentes registradas.
- WEBFISHING: progreso, mejoras, inventario existente y diario.
- KH Final Mix: 154 objetos con nombre y VT/PM actuales.
- Decimales con conservación del tipo binario, verificación y respaldo.
- Distribución portátil de Windows con PyInstaller.
- 20 pruebas automatizadas. Validación dentro de los juegos pendiente.

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

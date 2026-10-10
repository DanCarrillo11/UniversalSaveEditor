# UniversalSaveEditor

Editor local de partidas para Windows, en español, con una interfaz inspirada en los menús de la época de PS2. Versión 0.5: Python + PySide6 (Qt Widgets), con biblioteca visual y portadas originales de cada juego. Funciona sin conexión con el ejecutable portátil, sin cuentas y sin subir las partidas a un servidor.

## Abrir como usuario

En GitHub, pulsa **Code → Download ZIP**, extrae la carpeta descargada y abre **UniversalSaveEditor.exe** con doble clic. Es portátil: no necesita instalar Python ni ejecutar comandos. No requiere conexión para editar partidas. El primer inicio puede tardar unos segundos mientras se extraen sus componentes temporales.

El ejecutable está incluido en la raíz del repositorio junto al código fuente. No hay archivos `.cmd` que debas ejecutar. Las versiones anteriores también están disponibles en **Releases → Assets**.

### Ejecutar el código fuente (desarrollo)

Solo para desarrollar: con Python de 64 bits, crea un entorno `.venv`, instala `requirements.txt` y ejecuta `app.py`.

### Crear el ejecutable

En Windows, instala `requirements-build.txt` en el entorno de desarrollo y ejecuta `python -m PyInstaller --clean --noconfirm UniversalSaveEditor.spec`. El resultado es `dist/UniversalSaveEditor.exe`.

## Interfaz

- Biblioteca con portadas originales sin recortar, búsqueda y filtros por disponibilidad.
- Colecciones para WEBFISHING, Risk of Rain, Kingdom Hearts y Max Payne.
- Arrastra una partida sobre la ventana o usa **Abrir partida**.
- Categorías de edición según el juego: economía, progreso, combate, cebos, personajes e inventario.
- Resumen de cambios en vivo, marcado de campos modificados y validación antes de exportar.
- La navegación entre biblioteca, pestañas y registros conserva los cambios; abrir otro archivo pide resolver los cambios sin exportar.
- Guía integrada. Atajos: **Ctrl+O** abrir, **Ctrl+F** buscar, **Ctrl+Enter** revisar y exportar.

Esta entrega añade el editor inicial de Risk of Rain 2. Tres juegos tienen edición disponible y los otros cuatro siguen pendientes.

## Compatibilidad actual

| Juego | Disponible |
|---|---|
| WEBFISHING | Dinero, deuda, dinero acumulado, nivel, XP, capturas, cantidades y desbloqueo de cebos, capacidad, seis mejoras, tamaño y calidad de objetos existentes, capturas y récords del diario. |
| Risk of Rain 2, Steam | 454 desbloqueables del catálogo instalado: personajes, habilidades, skins y recolores, artefactos, objetos, registros y altares de Newt. También permite editar monedas lunares, progreso, combate y economía. |
| Kingdom Hearts Final Mix, HD 1.5 + 2.5 ReMIX, Steam | Selección de partida, platines, VT/PM actuales y base, PH, fuerza y defensa de Sora, Donald y Goofy; cantidades de 154 objetos, materiales, armas y accesorios identificados. |
| Re:Chain of Memories, Steam | Detección del archivo; edición pendiente. |
| KH II Final Mix y Birth by Sleep, Steam | Edición pendiente. No se afirma compatibilidad con toda la colección. |
| Max Payne 1 | Edición pendiente de investigar y validar su formato con partidas de ejemplo. |

Los límites del editor son límites conservadores de entrada, no garantías de equilibrio o de aceptación de cualquier combinación por el juego. En KH los atributos base pueden diferir de los valores efectivos por el equipo. En KH no se editan nivel, experiencia, historia ni habilidades. En WEBFISHING no se añaden ni eliminan objetos, no se desbloquean cosméticos y no se modifican misiones; nivel y XP se modifican como valores independientes y no conceden automáticamente recompensas. Los límites de mejoras son conservadores. Las armas de KH se añaden al inventario: no se equipan automáticamente. Los objetos de historia y los identificadores desconocidos no se exponen. Risk of Rain 2 puede registrar los desbloqueos en el perfil, pero el juego todavía puede exigir que tengas instalado o comprado el DLC correspondiente.

## Uso

1. Elige **Abrir editor** en la tarjeta del juego, o usa **Abrir partida**.
2. Selecciona el registro de KH que quieres editar. En Risk of Rain 2, usa los checkboxes o **Desbloquear categoría** y busca por personaje o identificador.
3. En WEBFISHING o Risk of Rain 2, pulsa **Revisar y aplicar**. El programa crea una copia `.bak` exacta y reemplaza de forma segura el archivo actual, conservando su nombre original.
4. En Kingdom Hearts, pulsa **Revisar y exportar** y elige otro archivo. Su instalación directa seguirá desactivada hasta validar las copias dentro del juego.
5. Cierra el juego antes de aplicar cambios. Steam Cloud puede sustituir una partida local si conserva otra versión.
6. Carga la partida dentro del juego y verifica los cambios. Si no funciona, restaura el archivo `.bak` generado por el editor.

Si el bloque `sqEX` de KH tiene un CRC que no coincide, la aplicación permite inspeccionarlo y explica el problema. Para exportarlo, debes marcar **Reparar la comprobación de integridad al exportar la copia**. Reparar ese CRC no corrige otros posibles daños internos.

## Verificación realizada

- 22 pruebas automatizadas con partidas sintéticas: límites, XML inválido, desbloqueos individuales y masivos, conservación de datos ajenos a la edición, desbloqueo automático de cebos, reemplazo atómico con respaldo, varios registros de KH, CRC y rechazo de sobrescrituras; búsqueda, filtros, navegación con cambios, cancelación y aplicación a través del diálogo de Qt.
- Revisión visual de biblioteca y editor mediante capturas renderizadas por Qt.
- Lectura y edición en memoria verificadas con archivos locales reales de WEBFISHING, Risk of Rain 2 y KH Final Mix de Steam. Ninguno se incluye en el proyecto.
- En Risk of Rain 2 se aplicaron los 454 identificadores sobre una copia real, que volvió a analizarse correctamente con respaldo exacto. Los originales no se modificaron. **La carga de las copias dentro de los juegos todavía no se ha probado.**

Ejecutar pruebas: `.venv\Scripts\python -m unittest discover -s tests -v`.

## Desarrollo

`core.py` separa formatos y escritura de la interfaz `app.py`. Los lectores producen registros y campos con posiciones, tipo y límites. `catalog.py` mantiene los metadatos y la disponibilidad de los juegos; `artwork.py` presenta las portadas completas y `theme.qss` define el estilo. Las modificaciones cambian exclusivamente los campos elegidos y el CRC del contenedor cuando corresponde; no se serializa toda la partida desde cero.

Siguientes pasos: validar la carga dentro de los juegos; añadir nombres públicos y descripciones para más identificadores internos de Risk of Rain 2; extraer los lectores a módulos independientes; añadir Re:CoM con su checksum interno; incorporar KH II y BBS con fixtures específicos; investigar Max Payne a partir de dos partidas que difieran en un dato conocido. La distribución portátil ya cuenta con una configuración reproducible de PyInstaller.

Preparado para guardar en un repositorio. No publiques partidas personales: pueden contener identificadores, nombres y datos de otros jugadores. `.gitignore` excluye las extensiones de guardados habituales.

## Licencia

GPL-3.0-or-later. Consulta [SOURCES.md](SOURCES.md) para las referencias y atribuciones de los formatos.

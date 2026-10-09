# SaveRoom

Editor local de partidas para Windows, en español, con una interfaz inspirada en los menús de la época de PS2. Versión 0.2: Python + PySide6 (Qt Widgets), con biblioteca visual e ilustraciones vectoriales originales. Funciona sin conexión después de instalar las dependencias, sin cuentas y sin subir las partidas a un servidor.

## Ejecutar

Necesitas Python 3.10 o posterior, de 64 bits. En Windows:

1. Ejecuta **Instalar.cmd** una vez. Prepara un entorno `.venv` local e instala PySide6; necesita internet.
2. Abre **Iniciar.cmd** para usar la aplicación.

En la copia de trabajo de esta conversación ya está instalado el entorno. El ZIP contiene código fuente; no incluye Python, `.venv` ni un ejecutable autónomo.

Alternativa desde una terminal: `python -m venv .venv`, después `.venv\Scripts\python -m pip install -r requirements.txt` y `.venv\Scripts\python app.py`.

## Interfaz

- Biblioteca con tarjetas ilustradas, búsqueda y filtros por disponibilidad.
- Colecciones para WEBFISHING, Kingdom Hearts y Max Payne.
- Arrastra una partida sobre la ventana o usa **Abrir partida**.
- Categorías de edición: economía y cebos, o economía y personajes.
- Resumen de cambios en vivo, marcado de campos modificados y validación antes de exportar.
- La navegación entre biblioteca, pestañas y registros conserva los cambios; abrir otro archivo pide resolver los cambios sin exportar.
- Guía integrada. Atajos: **Ctrl+O** abrir, **Ctrl+F** buscar, **Ctrl+Enter** revisar y exportar.

Esta entrega mejora la interfaz; no amplía el soporte de juegos respecto de la versión 0.1.

## Compatibilidad actual

| Juego | Disponible |
|---|---|
| WEBFISHING | Dinero, deuda pendiente y cantidades de los cebos existentes. |
| Kingdom Hearts Final Mix, HD 1.5 + 2.5 ReMIX, Steam | Selección de partida, platines y VT/PM/PH base, fuerza y defensa de Sora, Donald y Goofy. |
| Re:Chain of Memories, Steam | Detección del archivo; edición pendiente. |
| KH II Final Mix y Birth by Sleep, Steam | Edición pendiente. No se afirma compatibilidad con toda la colección. |
| Max Payne 1 | Edición pendiente de investigar y validar su formato con partidas de ejemplo. |

Los límites del editor son límites conservadores de entrada, no garantías de equilibrio o de aceptación de cualquier combinación por el juego. En KH los atributos base pueden diferir de los valores efectivos por el equipo. Nivel, experiencia, historia y habilidades no se editan en esta versión.

## Uso

1. Elige **Abrir editor** en la tarjeta del juego, o usa **Abrir partida**.
2. Selecciona el registro de KH que quieres editar. Cambia los valores deseados.
3. Pulsa **Revisar y exportar**. Revisa la lista de modificaciones y elige un nombre nuevo.
4. Obtendrás el archivo editado y una copia `.bak` exacta del original en la misma carpeta. El programa nunca sobrescribe el archivo que abriste ni un destino existente.
5. Para probar la copia, cierra el juego, conserva un respaldo independiente de la carpeta de partidas y sustituye manualmente el archivo correspondiente con la copia, usando el nombre original. En Steam, comprueba que la sincronización no sustituya tu copia por otra versión. El editor no instala archivos ni cambia Steam Cloud.
6. Carga la partida dentro del juego y verifica los cambios. Si no funciona, vuelve a colocar el original con su nombre original.

Si el bloque `sqEX` de KH tiene un CRC que no coincide, la aplicación permite inspeccionarlo y explica el problema. Para exportarlo, debes marcar **Reparar la comprobación de integridad al exportar la copia**. Reparar ese CRC no corrige otros posibles daños internos.

## Verificación realizada

- 13 pruebas automatizadas con partidas sintéticas: límites, archivos truncados, conservación de bytes ajenos a la edición, varios registros de KH, CRC, respaldo y rechazo de sobrescrituras; búsqueda, filtros, navegación con cambios, cancelación y exportación a través del diálogo de Qt.
- Revisión visual de biblioteca y editor mediante capturas renderizadas por Qt.
- Lectura y edición en memoria verificadas con un archivo local real de WEBFISHING y uno de KH Final Mix de Steam. Ninguno se incluye en el proyecto.
- Los originales no se modificaron. **La carga de las copias dentro de los juegos todavía no se ha probado.**

Ejecutar pruebas: `.venv\Scripts\python -m unittest discover -s tests -v`.

## Desarrollo

`core.py` separa formatos y escritura de la interfaz `app.py`. Los lectores producen registros y campos con posiciones, tipo y límites. `catalog.py` mantiene los metadatos y la disponibilidad de los juegos; `artwork.py` dibuja las ilustraciones y `theme.qss` define el estilo. Las modificaciones cambian exclusivamente los campos elegidos y el CRC del contenedor cuando corresponde; no se serializa toda la partida desde cero.

Siguientes pasos: validar la carga dentro de los juegos; extraer los lectores a módulos independientes; añadir Re:CoM con su checksum interno; incorporar KH II y BBS con fixtures específicos; investigar Max Payne a partir de dos partidas que difieran en un dato conocido; preparar una distribución `.exe`.

Preparado para guardar en un repositorio. No publiques partidas personales: pueden contener identificadores, nombres y datos de otros jugadores. `.gitignore` excluye las extensiones de guardados habituales.

## Licencia

GPL-3.0-or-later. Consulta [SOURCES.md](SOURCES.md) para las referencias y atribuciones de los formatos.

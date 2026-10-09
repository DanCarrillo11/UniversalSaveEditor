# Referencias y atribuciones

El proyecto se distribuye bajo GPL-3.0-or-later. La implementación es Python y utiliza la biblioteca estándar. No incluye imágenes ni archivos de los juegos.

- [Godot 3.5 binary serialization API](https://docs.godotengine.org/en/3.5/tutorials/io/binary_serialization_api.html): tipos, tamaños y flags de Variant.
- [NotNite/webfishing-save-editor](https://github.com/NotNite/webfishing-save-editor): referencia para el envoltorio del archivo y nombres de campos WEBFISHING (`src/game/types.ts`, `src/App.svelte`). No se incluyen sus recursos visuales ni su interfaz.
- [Xeeynamo/KingdomSaveEditor](https://github.com/Xeeynamo/KingdomSaveEditor), GPL-3.0: formato de archivo PC y posiciones de campos de KH Final Mix; archivos `KHSave.Archives/PcSaveArchive.cs`, `KHSave.Archives/Factories/PcKh1Factory.cs`, `KHSave.Lib1/SaveKh1.FinalMix.cs`, `KHSave.Lib1/Models/Character.cs`. Copyright de los autores originales conservado. SaveRoom adapta el conocimiento de esas estructuras a un editor que preserva los bytes originales.
- [KatRewrites/kh1-save-editor](https://github.com/KatRewrites/kh1-save-editor), GPL-3.0: referencia consultada sobre los contenedores PNG/sqEX y la necesidad de conservar registros relacionados. No se incorporan sus tablas ni su interfaz.

Los nombres de juegos pertenecen a sus respectivos titulares. SaveRoom es un proyecto independiente.

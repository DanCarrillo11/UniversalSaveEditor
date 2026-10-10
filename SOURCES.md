# Referencias y atribuciones

El proyecto se distribuye bajo GPL-3.0-or-later. La implementación es Python y utiliza la biblioteca estándar. No incluye partidas personales. Las portadas se incluyen como recursos visuales de identificación; sus derechos pertenecen a los titulares respectivos y no están cubiertos por la licencia GPL del código.

- [Godot 3.5 binary serialization API](https://docs.godotengine.org/en/3.5/tutorials/io/binary_serialization_api.html): tipos, tamaños y flags de Variant.
- [NotNite/webfishing-save-editor](https://github.com/NotNite/webfishing-save-editor): referencia para el envoltorio del archivo y nombres de campos WEBFISHING (`src/game/types.ts`, `src/App.svelte`). No se incluyen sus recursos visuales ni su interfaz.
- [Xeeynamo/KingdomSaveEditor](https://github.com/Xeeynamo/KingdomSaveEditor), GPL-3.0: formato de archivo PC y posiciones de campos de KH Final Mix; archivos `KHSave.Archives/PcSaveArchive.cs`, `KHSave.Archives/Factories/PcKh1Factory.cs`, `KHSave.Lib1/SaveKh1.FinalMix.cs`, `KHSave.Lib1/Models/Character.cs`. Copyright de los autores originales conservado. UniversalSaveEditor adapta el conocimiento de esas estructuras a un editor que preserva los bytes originales.
- [KatRewrites/kh1-save-editor](https://github.com/KatRewrites/kh1-save-editor), GPL-3.0: referencia consultada sobre los contenedores PNG/sqEX y la necesidad de conservar registros relacionados. No se incorporan sus tablas ni su interfaz.

Los nombres de juegos pertenecen a sus respectivos titulares. UniversalSaveEditor es un proyecto independiente.

El icono de memory card se obtuvo de la imagen aportada por el autor del repositorio y se preparó como recorte PNG transparente. Las marcas y logotipos visibles pertenecen a sus titulares respectivos y no están cubiertos por la licencia GPL del código.

## Portadas

- [kh1](https://www.khwiki.com/File:Kingdom_Hearts_Final_Mix_Boxart_JP.png): archivo original, URL de imagen y procedencia en `assets/covers/sources.json`.
- [recom](https://www.khwiki.com/File:Kingdom_Hearts_ReChain_of_Memories_Boxart_NA.png): archivo original, URL de imagen y procedencia en `assets/covers/sources.json`.
- [kh2](https://www.khwiki.com/File:Kingdom_Hearts_II_Final_Mix%2B_Boxart_JP.png): archivo original, URL de imagen y procedencia en `assets/covers/sources.json`.
- [bbs](https://www.khwiki.com/File:Kingdom_Hearts_Birth_by_Sleep_Final_Mix_Boxart_JP.png): archivo original, URL de imagen y procedencia en `assets/covers/sources.json`.
- [webfishing](https://store.steampowered.com/app/3146520/): archivo original, URL de imagen y procedencia en `assets/covers/sources.json`.
- [maxpayne](https://store.steampowered.com/app/12140/): archivo original, URL de imagen y procedencia en `assets/covers/sources.json`.
- [ror2](https://store.steampowered.com/app/632360/): arte oficial de biblioteca de Steam; URL y tamaño registrados en `assets/covers/sources.json`.

Las ediciones Final Mix usan las portadas japonesas de sus lanzamientos originales (KH II Final Mix+ incluye Re:CoM); no se presentan como cajas de una edición individual de Steam. WEBFISHING, Risk of Rain 2 y Max Payne usan el arte de biblioteca de Steam.

La compatibilidad con Risk of Rain 2 se validó contra la estructura de un perfil local de Steam aportado por el autor. El perfil contiene datos personales y no se incluye en el repositorio.

La tabla `kh_items.py` adapta `KHSave.Lib1/Types/EquipmentType.cs` de Xeeynamo/KingdomSaveEditor (GPL-3.0); conserva su atribución y excluye objetos de historia y entradas sin uso.

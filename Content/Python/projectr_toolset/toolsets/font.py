import unreal

import toolset_registry
from editor_toolset.toolsets.asset import import_asset


@unreal.uclass()
class FontTools(unreal.ToolsetDefinition):
    """Imports font files (TTF/OTF) as FontFace assets that UMG and Slate text can use."""

    @toolset_registry.tool_call
    @staticmethod
    def import_font_face(folder_path: str, asset_name: str, source_file: str) -> unreal.FontFace:
        """Imports a TrueType or OpenType font file as a FontFace asset.
        The font data is stored inside the asset (inline loading), so it ships with packaged builds.

        Args:
            folder_path: The content-browser folder to create the asset in.
            asset_name: The name of the new FontFace asset.
            source_file: The absolute path to the .ttf or .otf file on disk.

        Returns:
            The imported FontFace.
        """
        assets = import_asset(folder_path, asset_name, source_file, factory=unreal.FontFileImportFactory())
        face = next((a for a in assets if isinstance(a, unreal.FontFace)), None)
        if face is None:
            raise RuntimeError(f'Import of "{source_file}" produced no FontFace.')
        face.set_editor_property('loading_policy', unreal.FontLoadingPolicy.INLINE)
        return face

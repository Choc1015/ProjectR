import unreal

import toolset_registry
from toolset_registry.helpers import create_asset
from editor_toolset.toolsets.asset import import_asset


@unreal.uclass()
class AnimationAssetTools(unreal.ToolsetDefinition):
    """Creates animation assets for skeletal characters: imports animation clips from FBX onto an
    existing skeleton, and builds Anim Montages and Animation Blueprints from them."""

    @toolset_registry.tool_call
    @staticmethod
    def import_animation(
            folder_path: str, asset_name: str, source_file: str,
            skeleton: unreal.Skeleton) -> unreal.AnimSequence:
        """Imports the animation in an FBX file as an AnimSequence on an existing skeleton.
        Any mesh in the file is ignored.

        Args:
            folder_path: The content-browser folder to create the asset in.
            asset_name: The name of the new asset.
            source_file: The absolute path to the FBX file on disk.
            skeleton: The skeleton the animation's bones are mapped onto.

        Returns:
            The imported AnimSequence.
        """
        if skeleton is None:
            raise ValueError('skeleton must not be None.')
        options = unreal.FbxImportUI()
        options.automated_import_should_detect_type = False
        options.import_mesh = False
        options.import_as_skeletal = True
        options.import_animations = True
        options.import_materials = False
        options.import_textures = False
        options.mesh_type_to_import = unreal.FBXImportType.FBXIT_ANIMATION
        options.original_import_type = unreal.FBXImportType.FBXIT_ANIMATION
        options.skeleton = skeleton
        assets = import_asset(
            folder_path, asset_name, source_file,
            options=options, factory=unreal.FbxFactory())
        for asset in assets:
            if isinstance(asset, unreal.AnimSequence):
                return asset
        raise RuntimeError(f'"{source_file}" contains no animation for skeleton {skeleton.get_name()}.')

    @toolset_registry.tool_call
    @staticmethod
    def create_montage(
            folder_path: str, asset_name: str, animation: unreal.AnimSequence) -> unreal.AnimMontage:
        """Creates an Anim Montage that plays the given animation in the 'DefaultSlot' slot.

        Args:
            folder_path: The content-browser folder to create the asset in.
            asset_name: The name of the new asset.
            animation: The animation the montage plays.

        Returns:
            The created montage.
        """
        if animation is None:
            raise ValueError('animation must not be None.')
        factory = unreal.AnimMontageFactory()
        factory.set_editor_property('source_animation', animation)
        factory.set_editor_property('target_skeleton', animation.get_editor_property('skeleton'))
        return create_asset(folder_path, asset_name, unreal.AnimMontage.static_class(), factory)

    @toolset_registry.tool_call
    @staticmethod
    def get_montage_animations(montage: unreal.AnimMontage) -> list[unreal.AnimSequenceBase]:
        """Returns the animations a montage plays, in timeline order across all slot tracks.

        Args:
            montage: The montage to read.

        Returns:
            The animations, or an empty list if the montage has none.
        """
        if montage is None:
            raise ValueError('montage must not be None.')
        animations = []
        for slot in montage.get_editor_property('slot_anim_tracks'):
            track = slot.get_editor_property('anim_track')
            for segment in track.get_editor_property('anim_segments'):
                animations.append(segment.get_editor_property('anim_reference'))
        return animations

    @toolset_registry.tool_call
    @staticmethod
    def create_anim_blueprint(
            folder_path: str, asset_name: str, skeleton: unreal.Skeleton,
            parent_class: unreal.Class) -> unreal.AnimBlueprint:
        """Creates an Animation Blueprint for a skeleton. Its AnimGraph starts empty.

        Args:
            folder_path: The content-browser folder to create the asset in.
            asset_name: The name of the new asset.
            skeleton: The skeleton the Animation Blueprint animates.
            parent_class: AnimInstance or a subclass of it, such as a C++ AnimInstance.

        Returns:
            The created Animation Blueprint.
        """
        if skeleton is None:
            raise ValueError('skeleton must not be None.')
        if parent_class is None or not unreal.MathLibrary.class_is_child_of(
                parent_class, unreal.AnimInstance.static_class()):
            raise ValueError(f'{parent_class} is not an AnimInstance class.')
        factory = unreal.AnimBlueprintFactory()
        factory.set_editor_property('target_skeleton', skeleton)
        factory.set_editor_property('parent_class', parent_class)
        return create_asset(folder_path, asset_name, unreal.AnimBlueprint.static_class(), factory)

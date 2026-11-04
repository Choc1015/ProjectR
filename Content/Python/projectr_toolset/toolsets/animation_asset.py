import os

import unreal

import toolset_registry
from toolset_registry.helpers import create_asset
from editor_toolset.toolsets.asset import import_asset


@unreal.uclass()
class AnimationAssetTools(unreal.ToolsetDefinition):
    """Creates animation assets for skeletal characters: imports skinned meshes and animation clips
    from FBX with a unit scale, and builds Anim Montages and Animation Blueprints from them."""

    @toolset_registry.tool_call
    @staticmethod
    def import_skeletal_mesh(
            folder_path: str, asset_name: str, source_file: str,
            skeleton: unreal.Skeleton | None = None, uniform_scale: float = 1.0,
            import_materials: bool = False, replace_existing: bool = False,
            update_reference_pose: bool = False) -> unreal.SkeletalMesh:
        """Imports the skinned mesh in an FBX file as a SkeletalMesh. Animations in the file are ignored.

        Args:
            folder_path: The content-browser folder to create the asset in.
            asset_name: The name of the new asset.
            source_file: The absolute path to the FBX file on disk.
            skeleton: An existing skeleton to bind to. When None, a new Skeleton asset is created.
            uniform_scale: Multiplier applied to the file's geometry, e.g. 100 for a file whose
                meters were read as centimeters.
            import_materials: When True, create Material assets for the file's materials.
            replace_existing: When True, overwrite an existing asset at the same path in place,
                keeping references to it. When False, raises if the asset exists.
            update_reference_pose: When True, the given skeleton's reference pose is replaced by
                the imported mesh's bind pose. This affects every mesh using the skeleton.

        Returns:
            The imported SkeletalMesh.
        """
        options = AnimationAssetTools._fbx_options(unreal.FBXImportType.FBXIT_SKELETAL_MESH, skeleton)
        options.import_mesh = True
        options.import_animations = False
        options.import_materials = import_materials
        settings = {'import_uniform_scale': uniform_scale, 'update_skeleton_reference_pose': update_reference_pose}
        for key, value in settings.items():
            options.skeletal_mesh_import_data.set_editor_property(key, value)
        assets = AnimationAssetTools._import(
            folder_path, asset_name, source_file, options, replace_existing, settings)
        return AnimationAssetTools._first_of(assets, unreal.SkeletalMesh, source_file)

    @toolset_registry.tool_call
    @staticmethod
    def import_animation(
            folder_path: str, asset_name: str, source_file: str,
            skeleton: unreal.Skeleton, uniform_scale: float = 1.0,
            replace_existing: bool = False) -> unreal.AnimSequence:
        """Imports the animation in an FBX file as an AnimSequence on an existing skeleton.
        Any mesh in the file is ignored.

        Args:
            folder_path: The content-browser folder to create the asset in.
            asset_name: The name of the new asset.
            source_file: The absolute path to the FBX file on disk.
            skeleton: The skeleton the animation's bones are mapped onto.
            uniform_scale: Multiplier applied to bone translations. Use the same value the
                skeleton's mesh was imported with.
            replace_existing: When True, overwrite an existing asset at the same path in place,
                keeping references to it. When False, raises if the asset exists.

        Returns:
            The imported AnimSequence.
        """
        if skeleton is None:
            raise ValueError('skeleton must not be None.')
        options = AnimationAssetTools._fbx_options(unreal.FBXImportType.FBXIT_ANIMATION, skeleton)
        options.import_mesh = False
        options.import_animations = True
        options.import_materials = False
        settings = {'import_uniform_scale': uniform_scale}
        options.anim_sequence_import_data.set_editor_property('import_uniform_scale', uniform_scale)
        assets = AnimationAssetTools._import(
            folder_path, asset_name, source_file, options, replace_existing, settings)
        return AnimationAssetTools._first_of(assets, unreal.AnimSequence, source_file)

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

    @staticmethod
    def _fbx_options(import_type: unreal.FBXImportType, skeleton: unreal.Skeleton | None) -> unreal.FbxImportUI:
        options = unreal.FbxImportUI()
        options.automated_import_should_detect_type = False
        options.import_as_skeletal = True
        options.import_textures = False
        options.mesh_type_to_import = import_type
        options.original_import_type = import_type
        if skeleton is not None:
            options.skeleton = skeleton
        return options

    @staticmethod
    def _import(
            folder_path: str, asset_name: str, source_file: str,
            options: unreal.FbxImportUI, replace_existing: bool,
            settings: dict[str, object]) -> list[unreal.Object]:
        if not replace_existing:
            return import_asset(folder_path, asset_name, source_file, options=options, factory=unreal.FbxFactory())
        if not os.path.isfile(source_file):
            raise FileNotFoundError(f'Source file not found: {source_file}')
        # Replacing reuses the import settings stored on the existing asset, so update those too.
        existing = unreal.load_asset(f'{folder_path}/{asset_name}')
        if existing is not None:
            import_data = existing.get_editor_property('asset_import_data')
            for key, value in settings.items():
                import_data.set_editor_property(key, value)
        task = unreal.AssetImportTask()
        task.filename = source_file
        task.destination_path = folder_path
        task.destination_name = asset_name
        task.replace_existing = True
        task.automated = True
        task.save = False
        task.factory = unreal.FbxFactory()
        task.options = options
        unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
        return [unreal.load_asset(p) for p in task.get_editor_property('imported_object_paths')]

    @staticmethod
    def _first_of(assets: list[unreal.Object], asset_class: type, source_file: str) -> unreal.Object:
        for asset in assets:
            if isinstance(asset, asset_class):
                return asset
        raise RuntimeError(f'Importing "{source_file}" produced no {asset_class.__name__}.')

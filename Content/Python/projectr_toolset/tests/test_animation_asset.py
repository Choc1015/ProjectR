import os
from contextlib import ExitStack

import unreal

from toolset_registry.tests.toolset_testcase import ToolCallTestCase
from toolset_registry.tests.automation import create_temp_folder
from editor_toolset.toolsets.skeletal_mesh import SkeletalMeshTools
from projectr_toolset.toolsets.animation_asset import AnimationAssetTools

# Mixamo exports in the project: skinned mesh + one animation each.
_MIXAMO_DIR = os.path.join(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir()),
                           'SourceArt', 'Mixamo')
_IDLE_FBX = os.path.join(_MIXAMO_DIR, 'Anim_Idle.fbx')
_WALK_FBX = os.path.join(_MIXAMO_DIR, 'Anim_Walk.fbx')


class AnimationAssetToolsTestCase(ToolCallTestCase):
    """Test AnimationAssetTools against a skeleton imported from the project's Mixamo files."""

    def setUp(self):
        super().setUp()
        self._stack = ExitStack()
        # tearDown is skipped when setUp fails, so register cleanup before anything can raise.
        self.addCleanup(self._release)
        self.folder = self._stack.enter_context(create_temp_folder()).rstrip('/')
        mesh = SkeletalMeshTools.import_file(self.folder, 'SK_Test', _IDLE_FBX)[0]
        self.skeleton = mesh.get_editor_property('skeleton')

    def _release(self):
        self.skeleton = None
        self._stack.close()

    def _import_walk(self) -> unreal.AnimSequence:
        return AnimationAssetTools.import_animation(self.folder, 'A_Walk', _WALK_FBX, self.skeleton)

    def test_import_animation_creates_sequence_on_skeleton(self):
        """Imports an AnimSequence bound to the given skeleton."""
        anim = self._import_walk()
        self.assertIsInstance(anim, unreal.AnimSequence)
        self.assertEqual(anim.get_editor_property('skeleton'), self.skeleton)
        self.assertGreater(anim.get_play_length(), 0.0)

    def test_import_animation_raises_on_missing_file(self):
        """Raises when the source file does not exist."""
        with self.assertToolRaisesRuntimeError():
            AnimationAssetTools.import_animation(
                self.folder, 'A_Missing', os.path.join(_MIXAMO_DIR, 'missing.fbx'), self.skeleton)

    def test_import_animation_raises_on_null_skeleton(self):
        """Raises when no skeleton is given."""
        with self.assertToolRaisesRuntimeError():
            AnimationAssetTools.import_animation(self.folder, 'A_NoSkeleton', _WALK_FBX, None)

    def test_create_montage_plays_animation(self):
        """Creates a montage whose only animation is the source animation."""
        anim = self._import_walk()
        montage = AnimationAssetTools.create_montage(self.folder, 'AM_Walk', anim)
        self.assertIsInstance(montage, unreal.AnimMontage)
        self.assertEqual(AnimationAssetTools.get_montage_animations(montage), [anim])

    def test_create_montage_raises_on_null_animation(self):
        """Raises when no animation is given."""
        with self.assertToolRaisesRuntimeError():
            AnimationAssetTools.create_montage(self.folder, 'AM_None', None)

    def test_create_montage_raises_when_asset_exists(self):
        """Raises when an asset with the same name already exists."""
        anim = self._import_walk()
        AnimationAssetTools.create_montage(self.folder, 'AM_Dup', anim)
        with self.assertToolRaisesRuntimeError():
            AnimationAssetTools.create_montage(self.folder, 'AM_Dup', anim)

    def test_get_montage_animations_raises_on_null_montage(self):
        """Raises when no montage is given."""
        with self.assertToolRaisesRuntimeError():
            AnimationAssetTools.get_montage_animations(None)

    def test_create_anim_blueprint_targets_skeleton(self):
        """Creates an Animation Blueprint for the skeleton with the given parent class."""
        abp = AnimationAssetTools.create_anim_blueprint(
            self.folder, 'ABP_Test', self.skeleton, unreal.AnimInstance.static_class())
        self.assertIsInstance(abp, unreal.AnimBlueprint)
        self.assertEqual(abp.get_editor_property('target_skeleton'), self.skeleton)

    def test_create_anim_blueprint_raises_on_non_anim_instance_parent(self):
        """Raises when the parent class is not an AnimInstance."""
        with self.assertToolRaisesRuntimeError():
            AnimationAssetTools.create_anim_blueprint(
                self.folder, 'ABP_Bad', self.skeleton, unreal.Actor.static_class())

    def test_create_anim_blueprint_raises_on_null_skeleton(self):
        """Raises when no skeleton is given."""
        with self.assertToolRaisesRuntimeError():
            AnimationAssetTools.create_anim_blueprint(
                self.folder, 'ABP_NoSkeleton', None, unreal.AnimInstance.static_class())

import os
from contextlib import ExitStack

import unreal

from toolset_registry.tests.toolset_testcase import ToolCallTestCase
from toolset_registry.tests.automation import create_temp_folder
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
        self.mesh = AnimationAssetTools.import_skeletal_mesh(self.folder, 'SK_Test', _IDLE_FBX)
        self.skeleton = self.mesh.get_editor_property('skeleton')

    def _release(self):
        self.mesh = None
        self.skeleton = None
        self._stack.close()

    def _import_walk(self) -> unreal.AnimSequence:
        return AnimationAssetTools.import_animation(self.folder, 'A_Walk', _WALK_FBX, self.skeleton)

    @staticmethod
    def _height(mesh: unreal.SkeletalMesh) -> float:
        return mesh.get_bounds().box_extent.z * 2.0

    def test_import_skeletal_mesh_creates_mesh_and_skeleton(self):
        """Imports a SkeletalMesh with a new Skeleton when none is given."""
        self.assertIsInstance(self.mesh, unreal.SkeletalMesh)
        self.assertIsInstance(self.skeleton, unreal.Skeleton)

    def test_import_skeletal_mesh_applies_uniform_scale(self):
        """Scales the imported geometry by uniform_scale."""
        scaled = AnimationAssetTools.import_skeletal_mesh(
            self.folder, 'SK_Scaled', _IDLE_FBX, uniform_scale=100.0)
        self.assertAlmostEqual(self._height(scaled), self._height(self.mesh) * 100.0, delta=self._height(self.mesh))

    def test_import_skeletal_mesh_replaces_existing_in_place(self):
        """Overwrites the existing asset at the same path when replace_existing is True."""
        replaced = AnimationAssetTools.import_skeletal_mesh(
            self.folder, 'SK_Test', _IDLE_FBX, skeleton=self.skeleton,
            uniform_scale=100.0, replace_existing=True, update_reference_pose=True)
        self.assertEqual(replaced.get_path_name(), self.mesh.get_path_name())
        self.assertEqual(replaced.get_editor_property('skeleton'), self.skeleton)
        self.assertGreater(self._height(replaced), 10.0)

    def test_import_skeletal_mesh_raises_when_asset_exists(self):
        """Raises when the asset exists and replace_existing is False."""
        with self.assertToolRaisesRuntimeError():
            AnimationAssetTools.import_skeletal_mesh(self.folder, 'SK_Test', _IDLE_FBX)

    def test_import_skeletal_mesh_raises_on_missing_file(self):
        """Raises when the source file does not exist, including when replacing."""
        with self.assertToolRaisesRuntimeError():
            AnimationAssetTools.import_skeletal_mesh(
                self.folder, 'SK_Test', os.path.join(_MIXAMO_DIR, 'missing.fbx'), replace_existing=True)

    def test_import_animation_replaces_existing_in_place(self):
        """Overwrites the existing animation at the same path when replace_existing is True."""
        anim = self._import_walk()
        replaced = AnimationAssetTools.import_animation(
            self.folder, 'A_Walk', _WALK_FBX, self.skeleton, uniform_scale=100.0, replace_existing=True)
        self.assertEqual(replaced.get_path_name(), anim.get_path_name())

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

    def _walk_montage(self) -> unreal.AnimMontage:
        return AnimationAssetTools.create_montage(self.folder, 'AM_Walk', self._import_walk())

    def test_set_montage_notify_places_notify_at_time(self):
        """Places a Montage Notify on its own track at the given time."""
        montage = self._walk_montage()
        AnimationAssetTools.set_montage_notify(montage, 'Hit', 0.3)
        self.assertAlmostEqual(AnimationAssetTools.get_montage_notify_time(montage, 'Hit'), 0.3, places=3)
        events = unreal.AnimationLibrary.get_animation_notify_events_for_track(montage, 'Hit')
        self.assertEqual(len(events), 1)
        notify = events[0].get_editor_property('notify')
        self.assertIsInstance(notify, unreal.AnimNotify_PlayMontageNotify)
        self.assertEqual(str(notify.get_editor_property('notify_name')), 'Hit')

    def test_set_montage_notify_moves_existing_notify(self):
        """Setting the same notify again moves it instead of adding a second one."""
        montage = self._walk_montage()
        AnimationAssetTools.set_montage_notify(montage, 'Hit', 0.3)
        AnimationAssetTools.set_montage_notify(montage, 'Hit', 0.5)
        self.assertAlmostEqual(AnimationAssetTools.get_montage_notify_time(montage, 'Hit'), 0.5, places=3)
        self.assertEqual(len(unreal.AnimationLibrary.get_animation_notify_events_for_track(montage, 'Hit')), 1)

    def test_set_montage_notify_raises_on_time_outside_montage(self):
        """Raises when the time is past the montage end."""
        montage = self._walk_montage()
        with self.assertToolRaisesRuntimeError():
            AnimationAssetTools.set_montage_notify(montage, 'Hit', montage.get_play_length() + 1.0)

    def test_set_montage_notify_raises_on_empty_name(self):
        """Raises when the notify name is empty."""
        montage = self._walk_montage()
        with self.assertToolRaisesRuntimeError():
            AnimationAssetTools.set_montage_notify(montage, '', 0.1)

    def test_get_montage_notify_time_raises_when_missing(self):
        """Raises when the montage has no notify with that name."""
        montage = self._walk_montage()
        with self.assertToolRaisesRuntimeError():
            AnimationAssetTools.get_montage_notify_time(montage, 'Hit')

    def test_remove_montage_notify_removes_it(self):
        """Removes the notify so it can no longer be read."""
        montage = self._walk_montage()
        AnimationAssetTools.set_montage_notify(montage, 'Hit', 0.3)
        AnimationAssetTools.remove_montage_notify(montage, 'Hit')
        with self.assertToolRaisesRuntimeError():
            AnimationAssetTools.get_montage_notify_time(montage, 'Hit')

    def test_remove_montage_notify_raises_when_missing(self):
        """Raises when there is nothing to remove."""
        montage = self._walk_montage()
        with self.assertToolRaisesRuntimeError():
            AnimationAssetTools.remove_montage_notify(montage, 'Hit')

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

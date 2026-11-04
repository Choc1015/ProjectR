import os

import unreal

from toolset_registry.tests.toolset_testcase import ToolCallTestCase
from toolset_registry.tests.automation import create_temp_folder
from projectr_toolset.toolsets.font import FontTools

_FONT = os.path.join(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir()),
                     'SourceArt', 'Fonts', 'NanumPenScript-Regular.ttf')


class FontToolsTestCase(ToolCallTestCase):
    """Test FontTools with the project's Nanum Pen Script font."""

    def test_import_font_face_is_inline(self):
        with create_temp_folder() as folder:
            face = FontTools.import_font_face(folder.rstrip('/'), 'FF_Test', _FONT)
            self.assertIsInstance(face, unreal.FontFace)
            self.assertEqual(face.get_editor_property('loading_policy'), unreal.FontLoadingPolicy.INLINE)

    def test_import_missing_file_raises(self):
        with create_temp_folder() as folder:
            with self.assertRaises(FileNotFoundError):
                FontTools.import_font_face(folder.rstrip('/'), 'FF_Missing', _FONT + '.nope')

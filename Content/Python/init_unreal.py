import unreal

from projectr_toolset import toolsets
from projectr_toolset import tests

toolsets._registration.register()

tests._test_runner = unreal.PythonTestRunner.create(
    'AI.Toolsets.ProjectR',
    unreal.PythonTestRunnerSearchOptions(root_module=tests.__name__))

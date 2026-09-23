"""Regression checks for source selection and CMake target discovery."""

import importlib.util
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("run_file", ROOT / "tools/run_file.py")
runner = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(runner)


class RunFileTests(unittest.TestCase):
    def setUp(self):
        (ROOT / "workspace").mkdir(exist_ok=True)
        self.directory = tempfile.TemporaryDirectory(dir=ROOT / "workspace")
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)

    def source(self, relative, contents="int main() { return 0; }\n"):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(contents)
        return path

    def test_duplicate_basenames_require_path_and_ignore_build_outputs(self):
        expected = self.source("first/example.cpp")
        self.source("workspace/copy/example.cpp")
        self.assertEqual(runner.resolve_source(self.root, "example.cpp"), expected)
        self.source("second/example.cpp")
        with self.assertRaisesRegex(ValueError, "first/example.cpp.*"):
            runner.resolve_source(self.root, "example.cpp")
        self.assertEqual(runner.resolve_source(self.root, "first/example.cpp"), expected)

    def test_cmake_artifact_name_comes_from_target(self):
        source = self.source("example.cpp")
        self.source("CMakeLists.txt", """cmake_minimum_required(VERSION 3.22)
project(validation LANGUAGES CXX)
add_executable(different_target example.cpp)
set_target_properties(different_target PROPERTIES OUTPUT_NAME actual_binary)
""")
        artifact = runner.executable_for_source(self.root, source)
        self.assertEqual(artifact.name, "actual_binary")
        self.assertTrue(artifact.is_file())

    def test_ambiguous_executables_and_library_source_are_not_guessed(self):
        source = self.source("example.cpp")
        project = self.source("CMakeLists.txt", """cmake_minimum_required(VERSION 3.22)
project(validation LANGUAGES CXX)
add_executable(first example.cpp)
add_executable(second example.cpp)
""")
        with self.assertRaisesRegex(ValueError, "found 2: first, second"):
            runner.executable_for_source(self.root, source)
        project.write_text("""cmake_minimum_required(VERSION 3.22)
project(validation LANGUAGES CXX)
add_library(only_library STATIC example.cpp)
""")
        with self.assertRaisesRegex(ValueError, "Library-only sources"):
            runner.executable_for_source(self.root, source)


if __name__ == "__main__":
    unittest.main()

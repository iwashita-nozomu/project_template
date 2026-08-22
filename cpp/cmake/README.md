<!--
@dependency-start
contract design
responsibility Documents the parent-local CMake helper boundary.
upstream design ../../documents/design/cpp-build-layout.md C++ helper ownership
downstream implementation ../CMakeLists.txt single C++ project entrypoint
@dependency-end
-->

# CMake Helpers

このディレクトリは `cpp/CMakeLists.txt` が利用する project-local CMake helper
と package configuration の置き場所です。C++ project の正本は親 repository の
root ではなく `cpp/CMakeLists.txt` です。

- `cpp/include/`: public header
- `cpp/src/`: production translation unit
- `cpp/tests/`: CTest consumer
- `cpp/experiments/`: native experiment consumer
- `build/cpp/<profile>/`: out-of-source configure/build tree
- `.state/cpp-install/<profile>/`: reusable install tree

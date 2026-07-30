<!--
@dependency-start
contract test
responsibility Documents the parent-local CTest consumer boundary.
upstream design ../../vendor/agent-canon/documents/design/cpp-build-layout.md CTest graph and aggregate contract
downstream implementation ../CMakeLists.txt test manifest
@dependency-end
-->

# C++ Tests

このディレクトリの各 C++ source は `cpp-test-<name>` executable として
`cpp-core` を consume し、CTest に登録されます。`cpp-tests` は全 individual
および CTest consumer の build aggregate です。

```bash
cmake --build build/cpp/dev --target cpp-tests --parallel
ctest --test-dir build/cpp/dev --output-on-failure
```

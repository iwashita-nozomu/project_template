# C++ validation projects

Each case under `test/cpp/<case>/` owns its executable and `CMakeLists.txt`.
The root library build uses this directory's `CMakeLists.txt` to aggregate cases.

The [version case](version/CMakeLists.txt) is also a standalone project. It
adds the root library with `add_subdirectory()` only if `project::core` is not
already available, then links that target. From the repository root:

```bash
cmake -S test/cpp/version -B workspace/build/version
cmake --build workspace/build/version --parallel
ctest --test-dir workspace/build/version --output-on-failure
```

Add a case's own dependencies in its local CMake project. Library dependencies
remain declared by the root library and arrive through the consumed target.
A consumer may also obtain the library with `FetchContent_MakeAvailable()`;
use a full commit SHA when fetching from Git. Do not `include()` the root
`CMakeLists.txt`. See the [C++ build layout](../../documents/design/cpp-build-layout.md).

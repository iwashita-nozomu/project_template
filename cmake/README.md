# CMake Layout

この template で C++ を使うときの CMake 正本は root の `CMakeLists.txt` です。

- root `CMakeLists.txt`
  - repo 全体の canonical entrypoint
- `cmake/`
  - `find_package` 補助、toolchain helper、JAX / OpenXLA 連携 helper
- `src/`
  - 実装本体
- `include/`
  - public header
- `lib/`
  - checked-in third-party source や手動 vendor する補助 library
- `tests/cpp/`
  - C++ test と smoke source

build は必ず out-of-source で行います。
既定の build tree は `build/cpp/<profile>/`、再利用する local install tree は `.state/cpp-install/<profile>/`、`jax.export` artifact cache は `.state/jax-export/<profile>/` です。

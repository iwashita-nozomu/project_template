<!--
@dependency-start
contract design
responsibility Documents the parent-local C++ project layout.
upstream design ../documents/design/cpp-build-layout.md C++ project boundary and migration map
downstream implementation CMakeLists.txt single C++ project entrypoint
@dependency-end
-->

# C++ Project Layout

このディレクトリが template の唯一の CMake project root です。親 repository
の root は language-neutral な入口として保ち、C++ の source、test、native
experiment target はここから同じ configure graph に取り込みます。

- `CMakeLists.txt`: project identity、`cpp-core`、output/install/result contract
- `include/`: public header
- `src/`: production implementation
- `tests/`: CTest consumer と `cpp-tests` aggregate
- `experiments/`: native experiment consumer と `cpp-experiments` aggregate
- `cmake/`: project-local CMake helper/configuration

```bash
ROOT=/workspace/project_template
PROFILE=dev
cmake -S "$ROOT/cpp" -B "$ROOT/build/cpp/$PROFILE" \
  -DCMAKE_INSTALL_PREFIX="$ROOT/.state/cpp-install/$PROFILE"
cmake --build "$ROOT/build/cpp/$PROFILE" --parallel
ctest --test-dir "$ROOT/build/cpp/$PROFILE" --output-on-failure
cmake --install "$ROOT/build/cpp/$PROFILE"
```

native experiment の source は `cpp/experiments/`、実行結果は既存の lifecycle
契約に従う `experiments/<topic>/result/<run_name>/` が所有します。

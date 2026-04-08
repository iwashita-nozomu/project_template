# C++ Build Layout

この template で C++ を使うときは、build layout を次で固定します。

## Source Of Truth

- root `CMakeLists.txt`
  - repo 全体の canonical CMake entrypoint
- `cmake/`
  - CMake helper module
- `src/`
  - C++ / CUDA 実装
- `include/`
  - public header
- `lib/`
  - checked-in third-party source や補助 library
- `tests/cpp/`
  - smoke / test source

`CMakeLists.txt` を `src/` や `cpp/` の下へ分散させることを禁止します。entrypoint は root に 1 つだけ置きます。

## Default Build Directories

- `build/cpp/<profile>/`
  - out-of-source build tree
- `.state/cpp-install/<profile>/`
  - local install tree
- `.state/jax-export/<profile>/`
  - reusable local `jax.export` artifact

`build/` と `.state/` の内容は commit しません。人手で編集することも禁止します。

## jax.export Flow

JAX 側は Python で `jax.export` artifact を生成し、C++ 側は同じ workspace の `src/` / `include/` と root `CMakeLists.txt` から consumer を build します。

最低限の smoke として、template 既定では次を通します。

```bash
python3 scripts/ci/check_jax_export_stack.py
cmake -S . -B build/cpp/dev -DPROJECT_TEMPLATE_ENABLE_CPP_SMOKE=ON
cmake --build build/cpp/dev --target project_template_cpp_smoke
```

## Reuse Policy

`build/cpp/<profile>/`、`.state/cpp-install/<profile>/`、`.state/jax-export/<profile>/` は再利用してよいですが、次のどれかが変わったら rebuild します。

- `docker/Dockerfile`
- `docker/requirements.txt`
- root `CMakeLists.txt`
- `cmake/` 配下
- `src/`, `include/`, `lib/`, `tests/cpp/`
- `jax` / `jaxlib` version
- `JAX_EXPORT_CALLING_CONVENTION_VERSION`
- export する関数の signature、shape、dtype、platform

再利用は「同じ toolchain / 同じ ABI / 同じ export contract の範囲」に限定します。怪しい場合は cache を消して rebuild します。

## Recommended Profiles

- `build/cpp/dev`
  - 日常開発
- `build/cpp/docker-smoke`
  - Docker smoke
- `.state/cpp-install/dev`
  - local reusable install
- `.state/jax-export/dev`
  - local reusable export artifact

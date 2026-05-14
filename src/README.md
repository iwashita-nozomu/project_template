# src

<!--
@dependency-start
responsibility Documents the optional C++ source directory policy.
upstream design ../vendor/agent-canon/documents/cpp-build-layout.md defines C++ source layout.
upstream implementation ../CMakeLists.txt defines the canonical C++ entrypoint.
downstream implementation ../include contains the default header-only implementation surface.
@dependency-end
-->

template 既定の C++ 実装は header-only です。
通常は `include/project_template/*.hpp` に実装し、`src/` は使いません。

`src/` を使うのは次のような特例だけです。

- header-only だと compile time や ODR の負担が大きすぎる
- 外部 library の binary link が必要
- 明示的な translation unit 分離が必要

`src/` に実装を置く場合は、なぜ header-only では駄目かを change note か設計文書に残します。

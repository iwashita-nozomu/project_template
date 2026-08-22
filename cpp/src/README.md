<!--
@dependency-start
contract design
responsibility Documents the parent-local C++ source boundary.
upstream design ../../documents/design/cpp-build-layout.md native source ownership
downstream implementation ../CMakeLists.txt cpp-core source inventory
@dependency-end
-->

# C++ Source

template 既定では production translation unit を持ちません。派生 repository
で C++ 実装を追加する場合は、public header を `cpp/include/`、private または
分離が必要な translation unit を `cpp/src/` に置き、`cpp-core` の source
inventory によって同じ CMake project graph に接続します。

header-only の実装は `cpp/include/` に置き、binary artifact が必要な場合だけ
`cpp/src/` に source を追加します。旧 root `src/` は C++ source owner では
ありません。

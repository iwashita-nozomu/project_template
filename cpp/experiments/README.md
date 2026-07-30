<!--
@dependency-start
contract experiment
responsibility Documents the parent-local native experiment target boundary.
upstream design ../../vendor/agent-canon/documents/design/cpp-build-layout.md experiment graph and result contract
downstream implementation ../CMakeLists.txt experiment manifest
@dependency-end
-->

# Native Experiments

native experiment source はこのディレクトリに置き、各 source は
`cpp-experiment-<name>` executable として `cpp-core` を consume します。
`cpp-experiments` は build aggregate です。build と run は分離し、run name、
config、result root、保存と report は親 `experiments/` の lifecycle owner が
管理します。

```bash
cmake --build build/cpp/dev --target cpp-experiments --parallel
```

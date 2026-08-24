<!--
@dependency-start
contract policy
responsibility Documents the parent project's remote execution contract.
upstream design ../design/docker-zero-build-environment.md project container boundary
@dependency-end
-->

# Remote Execution Repo Contract

この文書は、server や orchestration layer から SSH 経由で parent repo を実行するための
最小契約です。外部のsource、tool runtime、eval archiveは別repositoryの責務です。

## 必須

- `docker/Dockerfile`
- repo root から動く project-owned 実行入口
- `commit SHA` 固定実行で壊れないこと
- log / artifact の出力先が決まっていること

## 推奨

- CPU 前提の default runtime pack を 1 つ持つ
- GPU を要する場合だけ追加 pack と明示的な Docker run option を持つ
- `README.md` か `docker/README.md` に runtime の役割を書く

## branch と commit の扱い

- 実行依頼では branch を受けてもよい
- orchestration 側で branch を `commit SHA` に解決し、その SHA を execution record に残す
- target 側では branch 名ではなく resolved commit を checkout する

## Docker 契約

- remote execution は repo 定義の Dockerfile と test runner を使う
- server 固有の ad-hoc command 断片に依存しない
- 必要な env や mount は project pack か repo 内 script に寄せる
- project pack は外部のmanaged devcontainerやtool runtimeを呼ばない
- nested Codex の state と credentials は明示的に分離する

## artifact 契約

- 実行結果の log と artifact の置き場を決める
- repo 内に残すものと orchestration 側で集約するものを分ける
- partial run を正式結果として扱うかどうかを repo 文書で明示する

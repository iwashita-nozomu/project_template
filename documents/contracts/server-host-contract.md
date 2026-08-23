<!--
@dependency-start
contract policy
responsibility Documents the parent project's server host contract.
upstream design ../design/docker-zero-build-environment.md project container boundary
@dependency-end
-->

# Server Host Contract

この文書は、server または SSH orchestration からこの parent repo を実行する host の
最小契約を定めます。AgentCanon の source、runtime、eval archive は別 repository の
責務であり、parent server host に常駐させません。

## 必須

- `git`、`python3`、`codex`、`docker` または `podman` が利用できること
- bare repo root と project workspace root が決まっていること
- local Linux filesystem に build/cache/artifact root があること
- `origin` push、artifact root、log retention の責務分担が文書化されていること
- remote execution が実行する commit SHA を記録すること

## Storage

bare repo root と workspace root は分けます。Docker state、build cache、runtime artifact
は local Linux filesystem に置き、CIFS、9p、network share を正本にしません。
project checkout の `workspace/agent-canondevelop/` は AgentCanon 編集時だけ使う ignored
作業領域で、task 終了時に exact task directory を削除します。

## Container

remote execution は project が定義する `docker/Dockerfile` と test runner を使います。
server 固有の ad-hoc command、parent test directory の AgentCanon runtime mount、
AgentCanon managed devcontainer は使いません。GPU は project command の明示的な run
option でのみ渡します。daemon が rootful/rootless かを契約条件にしません。

## Git and artifacts

- execution は branch を commit SHA に解決して記録します
- log と artifact の出力先を execution record に残します
- partial run を正式結果として扱うかを project contract で明示します
- host credentials は project container に自動 forward しません

## Validation

```bash
bash test/testrunner.sh
bash docker/run-tests.sh --tag project-template:server-check
```

## Related

- [Linux / WSL host requirements](linux-wsl-host-requirements.md)
- [Remote execution repo contract](remote-execution-repo-contract.md)
- [Docker environment boundary](../design/docker-zero-build-environment.md)

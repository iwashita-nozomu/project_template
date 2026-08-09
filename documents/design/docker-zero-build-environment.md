<!--
@dependency-start
contract design
responsibility Defines the parent Docker zero-build runtime, identity, CPU default, and explicit GPU profile contract.
upstream design ../../vendor/agent-canon/CONTAINER_OPERATIONS.md AgentCanon/product image ownership boundary
upstream design ../../vendor/agent-canon/documents/design/devcontainer/parent-devcontainer-policy.md parent devcontainer mount and lifecycle contract
upstream design ../../vendor/agent-canon/documents/design/devcontainer/parent-devcontainer-policy.md default and GPU-admission profile boundary
downstream implementation ../../docker/Dockerfile product image and runtime capability owner
downstream implementation ../../docker/requirements.txt parent Python lock manifest
downstream implementation ../../docker/install_python_dependencies.sh installs the parent Python lock
downstream implementation ../../docker/cold-build-smoke.sh single cold build/smoke evidence executor
downstream implementation ../../docker/check_zero_build_contract.sh static zero-build contract checker
@dependency-end
-->

# Docker zero-build environment design

## Requirement trace

この設計は、Docker layer/cache、host の preinstall、既存 container state、host
`~/.codex` が無い fresh checkout でも、同じ runtime/tool surface を作成できる
Docker/devcontainer 契約を定義する。CI は通常の local cache を禁止せず、`--pull --no-cache` の cold build と smoke を再現性の acceptance path にする。

実装時点の一次資料は次の URL で固定する。Ubuntu image digest と NVIDIA package
metadata は GPU target を更新するときだけ再取得し、変更があれば実装を停止して
この設計と選定値を更新する。

- Ubuntu Official Image metadata: <https://hub.docker.com/_/ubuntu>
- NVIDIA CUDA Installation Guide for Linux, Ubuntu network repository:
  <https://docs.nvidia.com/cuda/cuda-installation-guide-linux/#ubuntu>
- NVIDIA Ubuntu 22.04 x86_64 repository metadata:
  <https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/>

選定した実装値は `linux/amd64` 用の次の digest と package version である。

- base: `ubuntu:22.04@sha256:0d779ea97881505f5ef0039336ee85edba27519bdba968c284c86ee066a973c8`
- CUDA keyring: `cuda-keyring_1.1-1_all.deb`
- CUDA keyring SHA256:
  `d93190d50b98ad4699ff40f4f7af50f16a76dac3bb8da1eaaf366d47898ff8df`
- CUDA toolkit: `cuda-toolkit-12-8=12.8.2-1`

既存の `nvidia/cuda:12.8.2-devel-ubuntu22.04` は base として採用しない。CUDA
toolkit は明示的な `gpu-runtime` Docker target だけで Ubuntu 22.04 に NVIDIA の
公式 keyring/repository を追加して導入する。CPU default target は CUDA/cuDNN/NCCL
を含まず、driver と host 認証情報は image に入れない。

## Runtime order and owners

| 順序 | surface                                                                                                  | owner                                                                               | completion evidence                                                                  |
| ---- | -------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------ |
| 1    | Ubuntu 22.04 base と target platform                                                                     | `docker/Dockerfile` と `docker/packs/*.toml`                                        | pinned `FROM --platform=linux/amd64` の static readback                              |
| 2    | OS fundamentals（git、build-essential、cmake、Python 3.11、zsh、Docker CLI、`ca-certificates`、sudo 等） | `docker/Dockerfile`                                                                 | package/executable smoke と Dockerfile contract check                                |
| 3    | CPU default target と explicit GPU target                                                                | `docker/Dockerfile` の `cpu-runtime`/`gpu-runtime` stages と `docker/packs/*.toml`  | default の CUDA/cuDNN/NCCL 不在 smoke、GPU target の keyring SHA と `nvcc --version` |
| 4    | language/build capability（Python、Node/npm、Ninja）                                                     | Python/Ninja は `docker/Dockerfile`、Node/npm は exact devcontainer Feature          | image smoke と Feature digest/options readback                                       |
| 5    | mounted developer/agent tools                                                                            | `vendor/agent-canon/.devcontainer/dependencies.toml`                                 | typed manifest validation、record verification                                       |
| 6    | parent workspace Python dependencies                                                                     | `docker/requirements.txt` と `docker/install_python_dependencies.sh`                | CPU lock の `--require-hashes` install、GPU profile の追加 lock、`pip check`         |
| 7    | parent-specific final hook                                                                               | `.devcontainer/post-create-parent.sh`                                               | shared post-create 成功後の final hook receipt                                       |

同じ package を Dockerfile、Feature、vendor TOML、parent TOML の複数箇所で宣言しない。
Python/Ninja は parent image、Node/npm は exact Feature、`tree` 等の mounted tool は
manifest の一つの installer だけが導入する。host PATH、host `~/.codex`、前回の receipt
を成功条件にしない。AgentCanon parent-first manifest merge 契約は保持し、親固有 record
が無い場合は空 manifest や sentinel を作らず、不在を parent overlay なしとして表す。

runtime identity は root を許可しない。Dockerfile は `PROJECT_USER`、
`PROJECT_UID`、`PROJECT_GID` を ARG として受け取り、非ゼロ UID/GID の canonical
`project` group/user を作成または互換 identity を安全に rename する。既存の
canonical name と異なる collision は unrecoverable として停止し、非 1000 ID を
受け入れる。devcontainer generator は host process の `id -u`/`id -g` だけを
build args と runtime `user` に同じ値で渡し、workspace-owner 推測や
`updateRemoteUserUID` を使わない。image construction と package install だけを root
で実行し、各 target の最後を専用 user の `USER project` にする。専用 user の home、
primary group、sudoers は同じ identity に揃え、`/etc/sudoers.d/project` を
`0440`・`NOPASSWD` にして `visudo -cf` と `sudo -n true` で確認する。

`devcontainer.json` の `containerUser`、`remoteUser`、生成 Compose の `user`、
workspace bind ownership、shared/parent post-create の実行 identity は同じ専用
user に揃える。root の `~/.codex` は mount せず、host `~/.zshrc` が regular file
として存在する場合だけ専用 user の home 配下へ read-only projection する。host
`~/.zshrc` が無い場合はその mount を生成せず、image-owned zsh startup のみで cold
CI を成立させる。pack smoke は `id -u != 0`、`sudo -n true`、`HOME` の専用 user
所有、workspace writable/readable ownership、zsh、Python、CPU JAX、`npm`、`ninja`、
`tree` と declared AgentCanon tools を確認する。GPU pack は明示 profile と host
driver が選択されたときだけ GPU JAX/CUDA libraries を確認する。

### Rootless and user-namespace limitation

Docker rootless mode または user-namespace remapping では、bind mount の数値 UID/GID
が container 内の `project` identity と一致しても host filesystem の owner readback が
異なる場合がある。これは mapping の capability limitation であり、default runtime
を root に昇格したり、host 側で `chmod`/`chown` を fallback として実行して解消しない。
必要な writable bind が成立しない場合は、同じ host process UID/GID で再作成できる
rootful/userns 設定へ戻すか、明示的な runtime blocker として停止する。GPU-admission
profile もこの制約を共有し、host group や `/var/lib` の privileged mutation を
default path に移さない。

## AgentCanon and parent PR boundary

AgentCanon source PR は AgentCanon clone の `.devcontainer/` と、その owner contract
だけを変更する。shared script の parent copy、親 Dockerfile の CUDA package、親
Python lock、parent CI は変更しない。

Parent PR は `docker/`、`.devcontainer` の regular parent overlay、pack、Docker
workflow、親 runbook と submodule pin を変更する。`vendor/agent-canon/.devcontainer`
の source は編集せず、AgentCanon PR が main に統合された commit の pin を一度だけ
更新する。

## Runtime boundary and rollback packet

この Docker change は AgentCanon audit canon とは別責務である。次の invariant を
Docker design/PR body と static/smoke evidence に投影する。

- `ubuntu22.04-direct-base`: digest と `linux/amd64` platform を固定し、CUDA は
  explicit `gpu-runtime` target の NVIDIA 公式 keyring/repository から導入する。
- `cold-build-reproducibility`: `--pull --no-cache`、host preinstall、previous
  container state、host `~/.codex` が不要で、cold build/smoke 一回が runtime evidence
  になる。
- `non-root-default`: default runtime UID は非ゼロで、専用 user/group・workspace
  ownership・post-create identity を一致させる。
- `sudo-nopasswd`: `/etc/sudoers.d/<user>` は `0440`、`NOPASSWD`、`visudo` と
  `sudo -n true` の readback を持つ。
- `dependency-owner-split`: OS/base、optional CUDA/toolchain、CPU/GPU Python lock、
  AgentCanon TOML、parent final hook の owner と順序が一意で、duplicate install/
  fallback がない。
- `driver-host-ownership`: NVIDIA driver/kernel module は host 責務で、image は
  toolkit/runtime と Compose の optional passthrough wiring だけを持つ。

The Docker-specific invariants are checked by `docker/check_zero_build_contract.sh`,
the CPU cold smoke, and the explicit GPU pack. The cold runtime witness is the existing
stdout JSON receipt retained in the CI log; no named artifact file is required.

親 `.devcontainer/devcontainer.json` と `.devcontainer/gpu-admission/devcontainer.json`
は regular Template-owned selectors とし、source-root resolver 経由で AgentCanon の
generator/shared post-create を呼ぶ。legacy symlink は作らない。host zshrc は read-only
optional mount とし、無い fresh CI では mount を省略して image-owned zsh startup で
create を成立させる。

## Validation and rollback

実装後の必要十分な検証は、Dockerfile/pack/manifest/devcontainer の static contract
readback、依存 installer の static/readback、`docker build --pull --no-cache` と一回の
CPU default pack smoke、devcontainer post-create の順序確認である。host GPU が無い
実行は CPU path を使い、GPU smoke は明示 profile と host driver が見える環境でのみ
optional passthrough として扱う。CUDA package や source pin が一次資料と一致しない
場合は、その変更を rollback し、設計の選定値を先に更新する。

## Design review resolution

最初の nested detailed-design review は implementation-ready `blocked` を返した。
以下の decisions で blocker を閉じてから実装する。

1. **stage terminology and order**: image build は Python 3.11/Ninja、Feature は Node/npm、
   mounted lifecycle は AgentCanon vendor manifest、選択された parent Python extras、
   AgentCanon cache/projection、parent final hook の順である。parent product image の
   cold smoke は parent lock installer と final hook だけを実行し、Feature/manifest を
   devcontainer acceptance と重複実行しない。source contract、
   post-create readback、focused order test はこの stage 名を明記する。
1. **base/Feature ownership**: 親 Dockerfile は `ca-certificates`、`curl`、`xz-utils`、
   Python 3.11、Ninja、build/runtime OS packages、sudo、zsh、CPU runtime を所有する。
   Node/npm は exact digest/options の official devcontainer Feature が所有する。
   ad hoc bootstrap や implicit fallback は持たず、parent Dockerfile、Feature、
   AgentCanon manifest は同じ package を宣言しない。
1. **Python source**: Ubuntu 22.04 Jammy に `python3.11` の公式 apt package が
   無いため、parent Dockerfile は Python.org の `Python-3.11.15.tar.xz` を SHA256
   `272179ddd9a2e41a0fc8e42e33dfbdca0b3711aa5abf372d3f2d51543d09b625` で検証して
   `/usr/local` に build する。PPA、moving installer、host Python は使用しない。
1. **PyYAML provider**: AgentCanon vendor record と parent lock は同一の exact
   PyYAML provider versionを参照し、manifest validation は version mismatch を fail
   させる。vendor install 後の parent lock install は既存 exact distribution を再利用
   し、別 version の reinstall を行わない。対応する source/test/ownership checker は
   provider mismatch を検出する。
1. **Jammy derived apt records**: AgentCanon source PR は全 `apt-package` record の
   `source` と version を Ubuntu 22.04/Jammy metadata に再選定する。Ubuntu 24.04
   literal は parent 22.04 image に残さない。
1. **zshrc**: AgentCanon generator は host `${HOME}/.zshrc` が regular file の場合だけ
   non-root home 配下へ read-only bind を生成し、欠落時は volume を省略する。validator
   と focused tests は present/absent の両分岐を確認し、image-owned zsh startup は両方で
   有効にする。
1. **non-root identity**: AgentCanon generator は build args `PROJECT_USER`、
   `PROJECT_UID`、`PROJECT_GID` と Compose runtime `user` を同じ host identity から
   materialize する。Dockerfile は dedicated user/group、`sudoers.d` `0440`、
   `visudo` readback、末尾 `USER` を持つ。pack smoke と devcontainer config check は
   root runtime、root home/config mount、ownership drift を fail させる。
1. **CPU/GPU boundary**: `docker/requirements.txt` と `pyproject.toml` の通常依存は
   CPU JAX とし、CUDA plugin/PJRT は `docker/requirements-gpu.txt` と `gpu` extra
   に分離する。CPU `Dockerfile` target と default pack は CUDA/cuDNN/NCCL packageを
   installせず、cold smoke は CPU backend と absent package を確認する。NVIDIA 公式
   Ubuntu 22.04 repo の CUDA toolkit 12.8.2、cuDNN 9.8、NCCL 2.25 は explicit
   `gpu-runtime` target と `docker/packs/gpu-admission.toml` が exact installし、
   GPU profile の installerだけが追加 lock と `jax[cuda12-local]` extra を導入する。
   host driver と `gpus: all` passthrough は host/runtime owner で、GPU が無い cold CI
   は CPU evidence のみを実行する。

### Immutable source evidence ledger

実装時点の readback は 2026-08-03 JST に取得した。Ubuntu official image の selected
amd64 manifest は `ubuntu:22.04@sha256:0d779ea97881505f5ef0039336ee85edba27519bdba968c284c86ee066a973c8`
で、pack platform は `linux/amd64`。NVIDIA `InRelease` は 2026-07-31 03:02:57 UTC、
repo signing key は short id `3BF863CC`、full fingerprint
`EB693B3035CD5710E231E123A4B469963BF863CC`。公式 `Packages.gz` record は
`cuda-toolkit-12-8=12.8.2-1`、amd64 package SHA256
`2e4e7b3dbb13136b76a89629872ce5dfa3102fe386a82d6745ee59d30c216549`、cuDNN runtime
SHA256 `e2339c5f18f2636cf302efa564a7d0916c6aff21e74739905b17252ae483fd90`、cuDNN dev
SHA256 `08cff04c68bc86ad9f312ac913c1eabda6fac8277c968b87317b440a599870aa`、NCCL runtime
SHA256 `ec5b980aefa6d4413841b873960f6855123dfe55d2db27c079a1c2c5f822c762`、NCCL dev
SHA256 `4c660de25e9a4cab3348ecae6b666cf7a240a8f11862c36a7343fd41ef9b3fd3`。keyring package
は `cuda-keyring_1.1-1_all.deb`、SHA256
`d93190d50b98ad4699ff40f4f7af50f16a76dac3bb8da1eaaf366d47898ff8df`。実装 static checker
はこれらの URL/version/hash と driver-package exclusion を read back する。

Python source evidence は Python.org の Python 3.11.15 release page と official XZ
tarball URL に固定し、上記 SHA256 を Dockerfile static contract と build step で確認する。
JAX source evidence は <https://docs.jax.dev/en/latest/installation.html> の
`cuda12-local` route と compatibility tableを参照する。JAX/PJRT/pluginのlock
生成元は parentが選択したJAX release metadataとこの公式compatibility tableに限定し、
resolved hashesは `docker/requirements.txt` に集約する。

### Cold acceptance owner

`docker/cold-build-smoke.sh` が parent PR の唯一の cold acceptance executor である。
この script は host UID/GID を `PROJECT_UID/PROJECT_GID` build args と runtime
identity に一度だけ materialize し、`docker build --platform linux/amd64 --pull --no-cache` を一度、同じ image の non-root smoke を一度実行する。smoke は
`id -u`、`sudo -n true`、home/workspace ownership、zsh、Python 3.11、CPU JAX import、
CUDA/cuDNN/NCCL absent、Ninja、Git/CMake/SSH/Docker/Graphviz を確認する。Node/npm と
mounted AgentCanon tools は Feature/manifest を実行する fresh-clone devcontainer acceptance
が所有し、product image smoke の追加要件にしない。CPU target で CUDA/cuDNN/NCCL が
不在であることを確認し、最後に status、uid、gid、home、workspace を含む JSON pass receipt を stdout へ
一度だけ出力する。CI log がこの stdout receipt を保持し、named file や artifact upload は
要求しない。
host-docker pack はこの acceptance path から外し、local Make target は通常 cache を
許可する。`docker/check_zero_build_contract.sh` は script/workflow/pack/source evidence
の static owner であり、cold image の差分 build は行わない。

design packet には dependency header、current source path、owner、implementation
mechanism、validation witness、rollback route を持つ evidence ledger を追加し、
`check_design_doc_claims.py` が graph snapshot 不在のために成功を偽装しないよう、
stdout/readback route を implementation packet に記録する。

<!--
@dependency-start
contract design
responsibility Defines the parent Docker zero-build runtime, identity, CUDA/JAX, and audit synchronization contract.
upstream design ../../vendor/agent-canon/CONTAINER_OPERATIONS.md AgentCanon/product image ownership boundary
upstream design ../../vendor/agent-canon/documents/design/devcontainer/parent-devcontainer-policy.md parent devcontainer mount and lifecycle contract
upstream implementation ../../docker/Dockerfile product image and runtime capability owner
upstream implementation ../../docker/requirements.txt parent Python lock manifest
upstream implementation ../../docker/install_python_dependencies.sh installs the parent Python lock
downstream implementation ../../docker/cold-build-smoke.sh single cold build/smoke evidence executor
downstream implementation ../../docker/check_zero_build_contract.sh static zero-build contract checker
@dependency-end
-->

# Docker zero-build environment design

## Requirement trace

この設計は、Docker layer/cache、host の preinstall、既存 container state、host
`~/.codex` が無い fresh checkout でも、同じ runtime/tool surface を作成できる
Docker/devcontainer 契約を定義する。CI は通常の local cache を禁止せず、`--pull
--no-cache` の cold build と smoke を再現性の acceptance path にする。

実装時点の一次資料は次の URL で固定する。Ubuntu image digest と NVIDIA package
metadata は実装時に再取得して、変更があれば実装を停止してこの設計と選定値を更新
する。

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
toolkit は Ubuntu 22.04 に NVIDIA の公式 keyring/repository を明示的に追加して
導入する。`cuda-drivers`、NVIDIA kernel driver、host 認証情報は image に入れず、
driver は host と container runtime の passthrough 契約に属する。

## Runtime order and owners

| 順序 | surface | owner | completion evidence |
| --- | --- | --- | --- |
| 1 | Ubuntu 22.04 base と target platform | `docker/Dockerfile` と `docker/packs/*.toml` | pinned `FROM --platform=linux/amd64` の static readback |
| 2 | OS fundamentals（git、build-essential、cmake、Python 3.11、zsh、Docker CLI、`ca-certificates`、sudo 等） | `docker/Dockerfile` | package/executable smoke と Dockerfile contract check |
| 3 | NVIDIA keyring、Ubuntu 22.04 repository、CUDA 12.8 toolkit | `docker/Dockerfile` の一つの CUDA block | keyring SHA、`nvcc --version`、driver package 不在、host passthrough docs |
| 4 | language runtime capability（Python、Node/npm、Ninja） | `docker/Dockerfile` または AgentCanon fixed bootstrap の一意な owner | version/executable static readback と smoke |
| 5 | AgentCanon fixed bootstrap と derived developer/agent tools | `vendor/agent-canon/.devcontainer/bootstrap-dependencies.sh` と `dependencies.toml` | bootstrap check、typed manifest validation、record verification |
| 6 | parent workspace Python dependencies | `docker/requirements.txt` と `docker/install_python_dependencies.sh` | `--require-hashes` install、`pip check`、Python import smoke |
| 7 | parent-specific final hook | `.devcontainer/post-create-parent.sh` | shared post-create 成功後の final hook receipt |

同じ package を Dockerfile、fixed bootstrap、vendor TOML、parent TOML の複数箇所
で宣言しない。親 Dockerfile が image 基礎能力を提供する場合、AgentCanon fixed
bootstrap はそれを `--check` で検証し、同じ package を再 install しない。standalone
bootstrap 用の install route が必要なら、その mode は明示 flag として扱い、parent
image route の暗黙 fallback にしない。`tree` 等の派生 tool は manifest の一つの
installer だけが導入し、host PATH、host `~/.codex`、前回の receipt を成功条件に
しない。既存の AgentCanon parent-first manifest merge 契約は保持し、parent manifest
が空の場合も明示的な `records = []` を保持する。

runtime identity は root を許可しない。Dockerfile は `PROJECT_USER`、
`PROJECT_UID`、`PROJECT_GID` を ARG として受け取り、非ゼロ UID/GID の専用 group/user
を作成する。default は UID/GID `1000` とし、devcontainer generator は host の
workspace UID/GID を build args と runtime `user` に同じ値で渡す。image construction
と package install だけを root で実行し、Dockerfile の最後を専用 user の `USER`
にする。専用 user の home は `${HOME}` として使い、`/etc/sudoers.d/<user>` を
`0440`・`NOPASSWD` にして `visudo -cf` と `sudo -n true` で確認する。

`devcontainer.json` の `containerUser`、`remoteUser`、生成 Compose の `user`、
workspace bind ownership、shared/parent post-create の実行 identity は同じ専用
user に揃える。root の `~/.codex` は mount せず、host `~/.zshrc` が regular file
として存在する場合だけ専用 user の home 配下へ read-only projection する。host
`~/.zshrc` が無い場合はその mount を生成せず、image-owned zsh startup のみで cold
CI を成立させる。pack smoke は `id -u != 0`、`sudo -n true`、`HOME` の専用 user
所有、workspace writable/readable ownership、zsh、Python、CUDA、`npm`、`ninja`、
`tree` と declared AgentCanon tools を確認する。

## AgentCanon and parent PR boundary

AgentCanon source PR は AgentCanon clone の `.devcontainer/` と、その owner contract
だけを変更する。shared script の parent copy、親 Dockerfile の CUDA package、親
Python lock、parent CI は変更しない。

Parent PR は `docker/`、`.devcontainer` の regular parent overlay、pack、Docker
workflow、親 runbook と submodule pin を変更する。`vendor/agent-canon/.devcontainer`
の source は編集せず、AgentCanon PR が main に統合された commit の pin を一度だけ
更新する。

## Audit synchronization packet

別 worker が設計する AgentCanon parent-repository audit canon/public skill と、この
Docker change は別責務である。ただし次の同一 invariant を audit item と Docker
design/PR body の両方へ投影する。

- `ubuntu22.04-direct-base`: digest と `linux/amd64` platform を固定し、CUDA は
  NVIDIA 公式 keyring/repository から導入する。
- `cold-build-reproducibility`: `--pull --no-cache`、host preinstall、previous
  container state、host `~/.codex` が不要で、cold build/smoke 一回が runtime evidence
  になる。
- `non-root-default`: default runtime UID は非ゼロで、専用 user/group・workspace
  ownership・post-create identity を一致させる。
- `sudo-nopasswd`: `/etc/sudoers.d/<user>` は `0440`、`NOPASSWD`、`visudo` と
  `sudo -n true` の readback を持つ。
- `dependency-owner-split`: OS/base、CUDA/toolchain、Python parent lock、AgentCanon
  TOML、parent final hook の owner と順序が一意で、duplicate install/fallback がない。
- `driver-host-ownership`: NVIDIA driver/kernel module は host 責務で、image は
  toolkit/runtime と Compose の optional passthrough wiring だけを持つ。

Audit PR が先に main へ統合された場合は、この PR の design/PR body が audit item
identifier と clause/ref を取り込み、同じ cold evidence receipt を参照する。Docker PR
が先に進む場合は、次の exact update packet を返して audit PR の後続変更へ渡す。

```text
audit_item_update=required
audit_item_ids=ubuntu22.04-direct-base,cold-build-reproducibility,non-root-default,sudo-nopasswd,dependency-owner-split,driver-host-ownership
source_design=documents/design/docker-zero-build-environment.md#Runtime-order-and-owners
runtime_evidence=docker/cold-build-smoke.sh:one-cold-build-one-smoke
required_clause_refs=FROM-platform-digest;CUDA-keyring-toolkit;USER-nonzero;sudoers-0440-NOPASSWD-visudo;owner-order-no-duplicate;driver-host-passthrough
audit_followup=apply-the-six-invariants-and-reuse-the-cold-runtime-receipt
```

親 `.devcontainer/devcontainer.json` は AgentCanon file への symlink、host zshrc は
read-only optional mount とする。host `~/.zshrc` が無い fresh CI では mount を省略し、
image-owned zsh startup と parent environment があれば create を成功させる。

## Validation and rollback

実装後の必要十分な検証は、Dockerfile/pack/manifest/devcontainer の static contract
readback、依存 installer の static/readback、`docker build --pull --no-cache` と一回の
default pack smoke、devcontainer post-create の順序確認である。host GPU が無い実行は
CPU path を使い、GPU smoke は host driver が見える環境でのみ optional passthrough と
して扱う。CUDA package や source pin が一次資料と一致しない場合は、その変更を
 rollback し、設計の選定値を先に更新する。

## Design review resolution

最初の nested detailed-design review は implementation-ready `blocked` を返した。
以下の decisions で blocker を閉じてから実装する。

1. **stage terminology and order**: `language runtime capability` は Python 3.11、
   Node/npm、Ninja の供給であり、`parent workspace Python dependencies` は最後の
   parent dependency stage である。したがって実行順は fixed bootstrap による
   language runtime capability → AgentCanon vendor manifest → parent workspace
   Python lock → AgentCanon cache/projection → parent final hook とする。source contract、
   post-create readback、focused order test はこの stage 名を明記する。
2. **base/bootstrap ownership**: 親 Dockerfile は `ca-certificates`、`curl`、
   `xz-utils`、Python 3.11、build/runtime OS packages、sudo、zsh、CUDA を所有する。
   AgentCanon fixed bootstrap は Node/npm と Ninja を所有し、parent image route では
   明示的な `--install-language-runtime` を使う。`--check` は install をせず、
   standalone の `--install` 以外に implicit fallback を持たない。parent Dockerfile と
   AgentCanon manifest は同じ package を宣言しない。
3. **Python source**: Ubuntu 22.04 Jammy に `python3.11` の公式 apt package が
   無いため、parent Dockerfile は Python.org の `Python-3.11.15.tar.xz` を SHA256
   `272179ddd9a2e41a0fc8e42e33dfbdca0b3711aa5abf372d3f2d51543d09b625` で検証して
   `/usr/local` に build する。PPA、moving installer、host Python は使用しない。
4. **PyYAML provider**: AgentCanon vendor record と parent lock は同一の exact
   PyYAML provider versionを参照し、manifest validation は version mismatch を fail
   させる。vendor install 後の parent lock install は既存 exact distribution を再利用
   し、別 version の reinstall を行わない。対応する source/test/ownership checker は
   provider mismatch を検出する。
5. **Jammy derived apt records**: AgentCanon source PR は全 `apt-package` record の
   `source` と version を Ubuntu 22.04/Jammy metadata に再選定する。Ubuntu 24.04
   literal は parent 22.04 image に残さない。
6. **zshrc**: AgentCanon generator は host `${HOME}/.zshrc` が regular file の場合だけ
   non-root home 配下へ read-only bind を生成し、欠落時は volume を省略する。validator
   と focused tests は present/absent の両分岐を確認し、image-owned zsh startup は両方で
   有効にする。
7. **non-root identity**: AgentCanon generator は build args `PROJECT_USER`、
   `PROJECT_UID`、`PROJECT_GID` と Compose runtime `user` を同じ host identity から
   materialize する。Dockerfile は dedicated user/group、`sudoers.d` `0440`、
   `visudo` readback、末尾 `USER` を持つ。pack smoke と devcontainer config check は
   root runtime、root home/config mount、ownership drift を fail させる。
8. **CUDA/JAX boundary**: NVIDIA 公式 Ubuntu 22.04 repo の CUDA toolkit 12.8.2、
   `libcudnn9-cuda-12=9.8.0.87-1`、`libcudnn9-dev-cuda-12=9.8.0.87-1`、
   `libnccl2=2.25.1-1+cuda12.8`、`libnccl-dev=2.25.1-1+cuda12.8` を image owner
   が exact install する。`docker/requirements.txt` が `jax[cuda12-local]`、その
   CUDA plugin/PJRT distribution、及び parent Python dependencyの唯一の resolved
   lock ownerであり、各distributionのversion/hashを保持する。`pyproject.toml` は
   project dependency intentのみを宣言し、lockでもinstall sourceでもなく、static
   contractはそのintentが requirements lock によって充足されることと、別のJAX/
   plugin/PJRT versionを宣言しないことを確認する。parent installerはこのrequirements
   lockだけを `--require-hashes` でinstallし、pyprojectから再解決しない。JAX 公式の
   CUDA 12 compatibility（CUDA >=12.1、cuDNN >=9.8,<10、NCCL >=2.18）を contract
   evidence にする。host driver（Linux CUDA 12 driver >=525）と `gpus: all`
   passthrough は host/runtime owner とし、GPU が無い cold CI は CPU JAX import +
   toolkit/library static smoke を行い、GPU execution は optional host evidence に
   分離する。

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
identity に一度だけ materialize し、`docker build --platform linux/amd64 --pull
--no-cache` を一度、同じ image の non-root smoke を一度実行する。smoke は
`id -u`、`sudo -n true`、home/workspace ownership、zsh、Python 3.11、JAX import、
`nvcc`、CUDA library versions、Node/npm、Ninja、tree、required AgentCanon tools を
確認し、`docker-cold-build-smoke.json` を stdout と CI artifact に一度だけ出力する。
host-docker pack はこの acceptance path から外し、local Make target は通常 cache を
許可する。`docker/check_zero_build_contract.sh` は script/workflow/pack/source evidence
の static owner であり、cold image の差分 build は行わない。

design packet には dependency header、current source path、owner、implementation
mechanism、validation witness、rollback route を持つ evidence ledger を追加し、
`check_design_doc_claims.py` が graph snapshot 不在のために成功を偽装しないよう、
artifact/readback route を implementation packet に記録する。

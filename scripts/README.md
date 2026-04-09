# scripts

`scripts/` は repo-local bootstrap の置き場です。
shared automation は `tools/` を使います。

## ここに置くもの

- clone 直後の初期化
- project slug や display name の置換
- bare remote 名の初期化

## 置かないもの

- agent helper
- CI / review / validation
- Docker / container runner
- experiment helper
- Markdown 整備

それらは `tools/` に置きます。

## 現在の入口

- [init_from_template.sh](/mnt/l/workspace/project_template/scripts/init_from_template.sh)
  - clone 直後に project slug、display name、bare remote 名などを初期化します。

## 参照先

- [tools/README.md](/mnt/l/workspace/project_template/tools/README.md)
- [documents/tools/README.md](/mnt/l/workspace/project_template/documents/tools/README.md)
- [documents/SHARED_RUNTIME_SURFACES.md](/mnt/l/workspace/project_template/documents/SHARED_RUNTIME_SURFACES.md)

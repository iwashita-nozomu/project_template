# References

<!--
@dependency-start
responsibility Documents repository-local reference material placement.
upstream design ../vendor/agent-canon/agents/workflows/research-workflow.md defines research workflow policy.
upstream design ../vendor/agent-canon/agents/workflows/README.md indexes workflow references.
downstream implementation workflow stores workflow literature notes.
@dependency-end
-->

このディレクトリは、実装、実験、workflow 設計で参照した一次資料や索引を置く場所です。
topic ごとの論文束や reference note をまとめる場合は、ここを入口にします。

## 置くもの

- topic ごとの reference index
- 論文、標準、仕様書、手順書の整理メモ
- repo-wide workflow や review policy の外部根拠に紐づく補助資料

## 置かないもの

- 日付付きの作業ログ
- run ごとの一次結果
- repo-wide の恒久ルールそのもの

これらは次へ分けます。

- 作業ログや補助メモ
  - `notes/`
- run ごとの結果や report
  - `experiments/` または `reports/agents/`
- 恒久ルール
  - `documents/` と `agents/`

## 推奨構成

    references/
    ├── README.md
    ├── workflow/
    │   └── README.md
    └── <topic>/
        ├── README.md
        └── *.pdf

## 関連入口

- [workflow-references.md](../vendor/agent-canon/documents/workflow-references.md)
  - workflow と review policy の外部根拠索引です。
- [research-workflow.md](../vendor/agent-canon/documents/research-workflow.md)
  - 研究・実験改造の正本です。
- [notes/README.md](../notes/README.md)
  - cross-run の知見整理はこちらです。

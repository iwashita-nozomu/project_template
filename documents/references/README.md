# References

<!--
@dependency-start
contract design
responsibility Documents external source records for this repository.
upstream design ../../AGENTS.md reference sweep requirement
upstream design ../README.md repository-owned document index and responsibility boundary
downstream design ../notes/README.md durable cross-run note owner
@dependency-end
-->

`documents/references/` は、実装、実験、workflow設計で参照した一次資料や索引を置く場所です。
topicごとの論文束やreference noteをまとめる場合は、ここを入口にします。

## 置くもの

- topicごとのreference index
- 論文、標準、仕様書、手順書の整理メモ
- repo-wideの設計や運用を補足する外部根拠

## 置かないもの

- 日付付きの作業ログ
- runごとの一次結果
- repo-wideの恒久ルールそのもの

これらは次へ分けます。

- 作業ログや補助メモ
  - `documents/notes/`
- runごとの結果やreport
  - `experiments/`または`reports/agents/`
- 恒久ルール
  - Template固有のcontractは`documents/contracts/`
  - Template固有のdesignは`documents/design/`

## Source Record Policy

新しいsource noteを追加する前に、`documents/references/`、`documents/notes/`、
`documents/contracts/`、`documents/design/`、task reportから同じtitle、DOI、URL、claimを検索します。
既存noteがsourceを扱っている場合は、重複を作らず、そのnoteを更新または参照します。

外部sourceを回答、設計、workflow、実験、reviewで利用した場合は、durable source recordを残します。
最低限、URLまたはDOI、access date、利用したclaim、既知の制約、採用・除外判断、download artifactを
tracked treeへ保持したか意図的に除外したかを記録します。

## 推奨構成

```text
documents/references/
├── README.md
├── workflow/
│   └── README.md
└── <topic>/
    ├── README.md
    └── *.pdf
```

## 関連入口

- [Repository documents](../README.md)
  - Template固有文書の正本入口です。
- [Notes](../notes/README.md)
  - cross-runの知見整理はこちらです。

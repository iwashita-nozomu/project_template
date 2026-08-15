# Notes Hub
<!--
@dependency-start
contract design
responsibility Documents Notes Hub for this repository.
upstream design ../README.md repository entrypoint and operating context
upstream design ../documents/README.md repository-owned document index and contract ownership
@dependency-end
-->

`notes/` は、この template で作業をまたいで残す知見、比較、補助メモの置き場です。
規約や設計の一次情報は `documents/` に残し、ここではそれに昇格させる前の知見や、
複数の run にまたがって参照する判断を扱います。

## 使い方

- 規約や設計として確定した内容は、所有する文書を `documents/` に追加または更新します。
- 作業メモは、対象の責務が分かる名前を付け、不要になったものを残しません。
- 実験結果や report は、対応する `experiments/` または `reports/` の所有面に置きます。
- 外部資料の出典記録は `references/` に置き、URL、参照日、利用した主張、制約を記録します。

## 配置

このディレクトリは通常の追跡対象ファイルだけで構成します。生成物、メモリ、symlink、
親 checkout への参照は配置しません。

## 関連入口

- [Repository entrypoint](../README.md)
- [Repository documents](../documents/README.md)
- [References](../references/README.md)

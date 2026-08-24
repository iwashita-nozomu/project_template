# Notes Hub

<!--
@dependency-start
contract design
responsibility Documents durable cross-run notes for this repository.
upstream design ../README.md repository-owned document index and responsibility boundary
upstream design ../../README.md repository entrypoint and operating context
downstream design ../references/README.md external source record owner
@dependency-end
-->

`documents/notes/` は、この template で作業をまたいで残す知見、比較、補助メモの置き場です。
規約や設計の一次情報は `documents/contracts/` と `documents/design/` に置き、ここでは
それらに昇格させる前の知見や、複数のrunにまたがって参照する判断を扱います。

## 使い方

- 規約や設計として確定した内容は、所有するcontractまたはdesign文書へ反映します。
- 作業メモは、対象の責務が分かる名前を付け、不要になったものを残しません。
- 実験結果やreportは、対応する`experiments/`または`reports/`の所有面に置きます。
- 外部資料の出典記録は`documents/references/`に置き、URL、参照日、利用した主張、制約を記録します。

## 配置

このディレクトリは通常の追跡対象fileだけで構成します。生成物、runtime memory、symlink、
親checkoutへの参照は配置しません。

## 関連入口

- [Repository entrypoint](../../README.md)
- [Repository documents](../README.md)
- [References](../references/README.md)

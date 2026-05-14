<!--
@dependency-start
responsibility Documents the tracked canonical catalogs used by normalized data assets.
upstream implementation basename_catalog.json defines normalized data basename identifiers
downstream implementation ../normalized/apparent_power_demand consumes catalog identifiers for normalized demand data
@dependency-end
-->

# Data Catalogs

この directory には、整理済みデータが参照する canonical catalog を置きます。
source workbook や旧 notebook の出力をそのまま置く場所ではありません。

予定する正本は次です。

- `site_catalog.json`
  - 拠点 ID、代表名、表示名、alias、source 側 ID の対応。
- `site_name_dictionary.json`
  - 拠点名の表記ゆれを canonical site key に寄せる辞書。
  - key は日本語の代表名 `<ID>_<拠点名>` とし、値に表記ゆれ list を置く。
  - 構造は `documents/rootdata-normalization-plan.md` を正本にし、実ファイルは後続の生成 code で作る。
- `dataset_catalog.json`
  - dataset domain、source artifact、normalized output、再生成 command の対応。
- `item_catalog.json`
  - 項目 ID、表示名、単位、値型、欠損値、source column の対応。

catalog を更新する場合は、対応する transform script と QC summary も同じ変更で確認します。

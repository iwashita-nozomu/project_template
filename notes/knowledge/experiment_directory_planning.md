# Experiment Directory Planning

実験コードの配置は、再現に必要な入口を 1 か所で辿れるかを基準に決めます。

## 先に結論

- reusable runtime は共通実装側に置く
- topic 固有コードは `experiments/<topic>/` に置く
- run ごとの report は `experiments/report/` に置く
- 長期に残す知見は `notes/` に置く

## 標準配置

- `experiments/<topic>/README.md`
- `experiments/<topic>/cases.*`
- `experiments/<topic>/experiment.*`
- `experiments/<topic>/result/<run_name>/`
- `experiments/report/<run_name>.md`

## Surviving Lessons

- experiment 実装は topic の近くに置いたほうが保守しやすいです。
- reusable process lifecycle は共通 runtime モジュールへ寄せるべきです。
- directory 構造は、topic ごとの入口、条件定義、実装本体、結果、report をまとめて辿れる形にするべきです。

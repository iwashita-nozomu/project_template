# Experiment Operations

## 保存

- 長時間 run は逐次保存を前提にします。
- final summary だけに頼りません。
- timeout、signal 終了、completion 欠落も診断できる形にします。

## ケース順

- case ordering は実験設計の一部です。
- 途中停止しても何が読めるかを先に考えます。

## `main` に残すもの

- 再集計や比較に必要な summary
- 実験の要約 note
- 再利用できる runtime や共通コード

## 監視

- 実行中プロセス
- メモリや GPU の使用量
- 中間生成物の増え方
- failure kind の分布

## よくある失敗

- partial run を正式結果として扱う
- summary を残さずに run を閉じる
- 実験コード側で env と process lifecycle を抱え込みすぎる

## 関連

- [Benchmark vs Experiment](/mnt/l/workspace/project_template/notes/knowledge/benchmark_vs_experiment.md)
- [documents/coding-conventions-experiments.md](/mnt/l/workspace/project_template/documents/coding-conventions-experiments.md)

# Imported Battery LP Model Analysis

## Scope

- Reuse surface:
  `python/docomo_bt_management/model/battery_lp_builder.py`,
  `python/docomo_bt_management/model/LPproblem.py`,
  `python/docomo_bt_management/model/lp_protocol.py`
- Applies when:
  過去プロジェクトから持ち込まれた蓄電池 LP モデルの役割、変数、制約、定式の妥当性を短時間で把握したいとき。
- Does not apply when:
  実装の import 修正、solver 実装の性能比較、KDE 学習器の内部詳細を詰めたいとき。

## Known

- この 3 ファイルは「学校の PV と Load の不確実性下で、蓄電池運用によるピークカットを扱う」コード群として読める。
- `battery_lp_builder.py` は蓄電池運用の block-structured LP を疎行列で構成する層で、等式制約と不等式制約を別 block で持つ。
- もともとの imported snapshot には `schoolmodel.py` があり、学校データから PV/Load 分布を作って LP パラメータへ写像する層を担っていた。
- 現在の refactor 後は `LPproblem.py` が、builder の block 行列と外生 PV/Load ベクトルから solver 向け LP を組み立てる層である。
- 下位 LP の主目的変数は `L0` で、これは各時刻残需要 `Lt` の上界として使われる。`min L0` により「最大残需要の最小化」、つまりピークカットを表現している。

## File Roles

### `battery_lp_builder.py`

- `BatteryLPBuilder.assemble()` が蓄電池運用問題の制約行列を構築する。
- 変数ブロックは以下のように読める。
  - `L0`: 一日のピーク需要
  - `Lt_t`: 各時刻の残需要
  - `x_t^+, x_t^-`: PCS/DC 側の正負分解
  - `y_t^+, y_t^-`: 効率反映後の AC 側正負分解
  - `b_t^+, b_t^-`: 電池の放電と充電
  - `B_t`: SOC
  - `hatb_t^+, hatb_t^-`: 上位側から固定または設計したい電池操作量
  - `z`: Big-M 線形化に使うモード選択変数
  - `p_t`: PV
  - `C_t`: Load
- `convert_to_Ineq()` は等式制約を `Ax <= b`, `-Ax <= -b` に展開して不等式系へ統一する。

### historical `schoolmodel.py`

- imported snapshot では `SchoolModel` が PV/Load CSV を読み込み、PCA と KDE を使って確率モデルを作っていた。
- `JointDistribution` は PV と Load の対数密度を足していたので、両者を独立近似していた。
- refactor 後の現 repo にはこの file は残しておらず、distribution-specific な層は LP builder / LP assembly の外へ分離された扱いである。

### `LPproblem.py`

- 現在の refactor 後は `optimal_control_lp()` が、builder の block 行列を solver 向けの LP operator に組み立てる。
- imported snapshot では距離関数ベースの境界最適化コードが含まれていたが、現 repo では LP assembly に責務を絞っている。

## Reconstructed Formulation

`battery_lp_builder.py` から読める代表的な制約は次の通り。

### Residual Load Definition

\[
L_t + y_t^+ - y_t^- = C_t
\]

- `Lt definition` block がこれを作っている。
- 需要から蓄電池・PCS 経由の有効出力を差し引いた残需要 `L_t` を定義している。

### Efficiency Coupling

\[
y_t^+ - y_t^- = \eta x_t^+ - \frac{1}{\eta} x_t^-
\]

- `Efficiency` block がこれを作っている。
- DC 側電力 `x` と AC 側有効電力 `y` の間にラウンドトリップ効率を入れている。

### Power Flow Balance

\[
x_t^+ - x_t^- - b_t^+ + b_t^- = p_t
\]

- `Flow` block がこれを作っている。
- PV 入力 `p_t` を PCS 出力と電池充放電で収支させている。

### SOC Dynamics

\[
B_{t+1} = B_t - b_t^+ + b_t^- - loss
\]

- `State` block がこれを作っている。
- `loss` は名前は rate だが、式上は時刻ごとの定数減衰として入っている。

### Peak Minimization

\[
L_0 \ge L_t,\quad \min L_0
\]

- `Peak via L` block がこれを作っている。
- これにより日内最大残需要を最小化するピークカット問題になる。

### Bound And Logic Constraints

- `B_lower <= B_t <= B_upper`
- `x`, `y`, `b`, `L0`, `Lt` の非負制約
- `x^+ + x^- <= pcs`, `y^+ + y^- <= pcs`
- `b^+ + b^- <= charge`
- Big-M による `min` 線形化とモード切替補助制約

## Interpretation Of The Two-Level Structure

- historical `schoolmodel.py` の `x_hat` は、`hatb` 系の電池操作スケジュールを上位側で固定または設計する用途に見える。
- 下位 LP は、その `x_hat` と PV/Load シナリオが与えられたときに可行か、ピーク `L0` がいくつになるかを計算する。
- imported snapshot の `LPproblem.py` はさらにこの下位問題の境界近傍を滑らかに扱って、外側の設計最適化へ接続しようとしていた。

## Validity Assessment

### Reasonable Parts

- `L0 >= Lt` と `min L0` の組は、ピークカットの定式として自然である。
- SOC 状態方程式、SOC 上下限制約、PCS 容量制約を分けて持っている点は物理モデルとして理解しやすい。
- `b^+ + b^- <= charge` を追加して同時充放電の緩みを抑えようとしている点は、LP 緩和を使う場合の安全策として筋が良い。

### Weak Or Questionable Parts

- `z` は 0/1 ではなく `0 <= z <= 1` の連続緩和でしかない。したがって、同時充放電禁止や `min` 線形化は厳密な物理ロジックではなく LP 緩和になっている。
- 初期 SOC `B_0` が固定されていない。最適化は都合のよい初期電池量を選べてしまうため、ピークカット能力を過大評価しうる。
- 終端 SOC 条件 `B_N = B_0` や `B_N >= target` がない。日末に電池を使い切る楽観的運用が許される。
- `self_discharge_rate` という名前に対して、式は割合減衰ではなく定数減衰である。パラメータ名と数式意味が一致していない。
- PV curtailment 変数が見当たらない。PV が需要や充電能力を上回る場合の余剰処理が曖昧で、状況によっては infeasible になりうる。
- `Lt >= 0` により逆潮流は基本的に許していない。これは仕様なら妥当だが、仕様明記が必要である。
- `JointDistribution` は PV と Load の独立近似で、相関や共通天候因子を捨てている。

### About historical `LPproblem.py`

- imported snapshot の `_DistanceFunction` が返す量は、polytope への厳密距離というより「LP 最適値と制約残差から作った滑らかな違反スコア」と解釈する方が正確である。
- `logsumexp` による soft max と勾配ノルム正規化は、外側最適化用の surrogate としては理解できるが、幾何学的距離そのものではない。

## Practical Reading Order

1. `battery_lp_builder.py` の `assemble()` で変数ブロックと制約 block を読む。
2. historical `schoolmodel.py` が残っている場合は、どの block が設計変数・補助変数・外生パラメータへ割り当てられているかを見る。
3. 現 repo では `LPproblem.py` の `optimal_control_lp()` で solver 向け LP がどう assembled されるかを見る。

## Open

- `hatb` が物理的に何を意味するかは、過去コードの solver 実装と元の C++ モデルを見ないと最終確定できない。
- `z` の 7 ブロックがそれぞれどの論理最小化を担当していたかは、元の `battery_lp_model.hpp` と対応を取るとより確実になる。
- imported snapshot 側の境界距離が何を最終目的にしていたかは、外側の training or design optimization コードがないと断定できない。

## Practical Commands Or Paths

- `python/docomo_bt_management/model/battery_lp_builder.py`
- `python/docomo_bt_management/model/LPproblem.py`
- `python/docomo_bt_management/model/lp_protocol.py`
- `notes/knowledge/imported_battery_lp_model_analysis.md`

## References

- `python/docomo_bt_management/model/battery_lp_builder.py`
- `python/docomo_bt_management/model/LPproblem.py`
- `python/docomo_bt_management/model/lp_protocol.py`
- `notes/README.md`

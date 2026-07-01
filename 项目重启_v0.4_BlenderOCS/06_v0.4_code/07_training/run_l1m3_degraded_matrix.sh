#!/usr/bin/env bash
# run_l1m3_degraded_matrix.sh —— R116 子任务 B 正式 degraded 小矩阵
# 预注册矩阵（不做开放超参搜索）：
#   protocol = P-INT, seed = 42, select = final+best（脚本内置双口径）
#   ocs_only : G1/G3/G5 × {degraded-mild, degraded-moderate}   (clean 引用 R115)
#   image_only: G1/G5 × {mild, moderate}
#   joint     : G1/G5 × {mild, moderate}
# clean 不重跑，degraded 汇总表标注 clean 来源为 R115（11_l1m2）。
set -u
PY="C:/Users/97466/.conda/envs/ocs_sim/python.exe"
cd "$(dirname "$0")/../.." || exit 1
SCRIPT="06_v0.4_code/07_training/train_l1m3_degraded.py"
LOG="v0.4_results/12_l1m3_degraded_mroll/degraded/_l1m3_degraded_matrix.log"
: > "$LOG"

run() {
  echo "=== $* ===" | tee -a "$LOG"
  "$PY" "$SCRIPT" --train --protocol P-INT --seed 42 --max-epochs 30 "$@" 2>&1 | tee -a "$LOG" | tail -3
}

for LVL in degraded-mild degraded-moderate; do
  # ocs_only 全 G
  for G in G1 G3 G5; do
    run --level "$LVL" --geom-group "$G" --mode ocs_only
  done
  # image_only / joint 仅 G1/G5
  for G in G1 G5; do
    run --level "$LVL" --geom-group "$G" --mode image_only
    run --level "$LVL" --geom-group "$G" --mode joint
  done
done
echo "[MATRIX DONE]" | tee -a "$LOG"

#!/usr/bin/env bash
# run_l1m2_matrix.sh —— 1C-L1M2 clean/P-INT 第一阶段正式矩阵
# 3 几何组(G1/G3/G5) × 3 通道(ocs_only/image_only/joint) = 9 runs
# image_only 在 G1/G3/G5 下输入相同(固定 phase63 图像)，但仍各跑一次以对齐同 split。
set -u
PY="C:/Users/97466/.conda/envs/ocs_sim/python.exe"
ROOT="d:/我的文件/研究生学术/光学项目/0506新/项目重启_v0.4_BlenderOCS"
cd "$ROOT" || exit 1
SCRIPT="06_v0.4_code/07_training/train_l1m2_multigeometry.py"
LOG="v0.4_results/11_l1m2_multigeometry_ocs/_l1m2_train_matrix.log"
EPOCHS="${1:-30}"
SEED="${2:-42}"

echo "==== L1M2 train matrix start $(date) epochs=$EPOCHS seed=$SEED ====" | tee -a "$LOG"
for G in G1 G3 G5; do
  for M in ocs_only image_only joint; do
    echo "---- $G / $M ----" | tee -a "$LOG"
    "$PY" "$SCRIPT" --train --geom-group "$G" --mode "$M" --protocol P-INT \
      --max-epochs "$EPOCHS" --seed "$SEED" >> "$LOG" 2>&1
    echo "   rc=$? $(date)" | tee -a "$LOG"
  done
done
echo "==== L1M2 train matrix DONE $(date) ====" | tee -a "$LOG"

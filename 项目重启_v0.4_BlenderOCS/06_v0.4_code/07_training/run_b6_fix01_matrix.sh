#!/usr/bin/env bash
# 1C-B6-FIX01 完整矩阵批处理：no-aug 5-fold×3通道（优先）+ standard 5-fold×2通道
set -u
cd "d:/我的文件/研究生学术/光学项目/0506新/项目重启_v0.4_BlenderOCS"
PYEXE="C:/Users/97466/.conda/envs/ocs_sim/python.exe"
SCRIPT="06_v0.4_code/07_training/train_b6_circular_regression.py"
LOG="v0.4_results/10_b6_circular_regression_fix01/_batch_fix01.log"
mkdir -p "v0.4_results/10_b6_circular_regression_fix01"
echo "=== B6-FIX01 batch start $(date) ===" > "$LOG"

run() {
  local mode="$1" fold="$2" aug="$3"
  echo "" >> "$LOG"
  echo ">>> RUN mode=$mode fold=$fold aug=$aug start=$(date +%H:%M:%S)" >> "$LOG"
  "$PYEXE" "$SCRIPT" --train --mode "$mode" --fold "$fold" --aug "$aug" --max-epochs 20 >> "$LOG" 2>&1
  local rc=$?
  echo "<<< rc=$rc mode=$mode fold=$fold aug=$aug end=$(date +%H:%M:%S)" >> "$LOG"
}

# 优先级1：no-aug 5-fold × 3 通道
for fold in 0 1 2 3 4; do
  for mode in image_only joint ocs_only; do
    run "$mode" "$fold" none
  done
done

# 优先级2：standard 5-fold × image_only/joint
for fold in 0 1 2 3 4; do
  for mode in image_only joint; do
    run "$mode" "$fold" standard
  done
done

echo "" >> "$LOG"
echo "=== B6-FIX01 batch done $(date) ===" >> "$LOG"

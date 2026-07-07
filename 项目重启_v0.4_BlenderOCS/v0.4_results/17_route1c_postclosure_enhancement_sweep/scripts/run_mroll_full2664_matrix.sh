#!/usr/bin/env bash
# run_mroll_full2664_matrix.sh —— R126 子任务 D：M-roll full-2664 渲染+后处理编排
#
# 把 R117 的 312 分层子集扩展到 full-2664 姿态。
#   - phase63 代表几何（图像通道 + G1 OCS）
#   - roll ∈ {+15,-15,+30,-30}，roll=0 复用 clean（不重渲）
#   - 复用 render_mroll_probe.py（其 generate_full_attitude_list 已覆写为全2664网格）
#     用 --start-index 0 --count 2664 + skip_existing 跳过已渲 312 子集
#   - 后处理复用 run_mroll_probe_postprocess.py，attitudes-file 用 full2664 列表
#
# 红线：不改旧脚本；roll=0 不重渲；不改 yaw/pitch 网格步长。
# 输出仍写入 12 号 mroll/ 渲染与后处理目录（与 312 子集同结构，full 覆盖），
# 汇总/评估/图表写入 17 号包。

set -u
BL="D:/Program Files/Blender Foundation/Blender 4.2/blender.exe"
PY="C:/Users/97466/.conda/envs/ocs_sim/python.exe"
cd "$(dirname "$0")/../.." || exit 1

FULL="v0.4_results/17_route1c_postclosure_enhancement_sweep/mroll_full2664/mroll_full2664_attitudes.json"
LOG="v0.4_results/17_route1c_postclosure_enhancement_sweep/logs/mroll_full2664_render.log"
: > "$LOG"

GEOM="phase63"
ROLLS=(15 -15 30 -30)

echo "[MROLL FULL2664 START] $(date)" | tee -a "$LOG"

for ROLL in "${ROLLS[@]}"; do
  ROLLTAG=$(printf "roll%+04d" "$ROLL")
  echo "=== RENDER $GEOM $ROLLTAG (full 2664, skip existing) ===" | tee -a "$LOG"
  "$BL" --background --python "06_v0.4_code/02_blender/render_mroll_probe.py" -- \
      --geom "$GEOM" --roll "$ROLL" --start-index 0 --count 2664 2>&1 \
      | grep -E "RENDERED:|SKIPPED_|FAILED:|SUCCESS|selected_count" | tee -a "$LOG"

  echo "=== POSTPROCESS $GEOM $ROLLTAG (full 2664) ===" | tee -a "$LOG"
  "$PY" "06_v0.4_code/05_postprocess/run_mroll_probe_postprocess.py" \
      --geom "$GEOM" --roll "$ROLL" --attitudes-file "$FULL" 2>&1 \
      | grep -E "COMPLETE|n_labels|本次待处理|完成|MROLL-POST" | tail -5 | tee -a "$LOG"
done

echo "[MROLL FULL2664 DONE] $(date)" | tee -a "$LOG"

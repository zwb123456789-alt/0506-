#!/usr/bin/env bash
# run_p3_all.sh —— R135 P3 local refinement 全量编排
# 9 个 roll 批次：roll=0 只渲 65 个半度点（整数点复用 fullrun），
# 8 个非零 roll 各渲 107 个 pose（整数42+半度65）。合计新渲染 921 单位。
# 每个 roll 一次 Blender 进程（渲染）+ 一次 ocs_sim python 后处理。
set -u

BLENDER="D:/Program Files/Blender Foundation/Blender 4.2/blender.exe"
PYEXE="C:/Users/97466/.conda/envs/ocs_sim/python.exe"
PKG="D:/我的文件/研究生学术/光学项目/0506新/项目重启_v0.4_BlenderOCS/v0.4_results/21_three_axis_p3_local_refinement"
RENDER_PY="$PKG/scripts/p3_render_local_refinement.py"
POST_PY="$PKG/scripts/p3_postprocess_local_refinement.py"
LOG="$PKG/logs/p3_render_postprocess.log"

# roll=0 先跑（只渲半度点），再跑 8 个非零 roll
ROLLS="0 -60 -45 -30 -15 15 30 45 60"

echo "==== R135 P3 local refinement 全量开始 $(date) ====" | tee "$LOG"
for r in $ROLLS; do
  echo "" | tee -a "$LOG"
  echo "######## ROLL $r : RENDER ########" | tee -a "$LOG"
  "$BLENDER" --background --python "$RENDER_PY" -- --roll "$r" >> "$LOG" 2>&1
  echo "render roll $r exit=$?" | tee -a "$LOG"

  echo "######## ROLL $r : POSTPROCESS ########" | tee -a "$LOG"
  "$PYEXE" "$POST_PY" --roll "$r" >> "$LOG" 2>&1
  echo "postprocess roll $r exit=$?" | tee -a "$LOG"
done
echo "" | tee -a "$LOG"
echo "==== R135 P3 全量结束 $(date) ====" | tee -a "$LOG"

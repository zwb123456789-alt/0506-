#!/usr/bin/env bash
# run_p1_all.sh —— R131 P1 seed-roll scan smoke 全量编排（96 渲染单位）
# 8 个非零 roll × 12 seed。roll=0 复用 01_fullrun，不重渲。
# 每个 roll 一次 Blender 进程（渲染 12 seed）+ 一次 ocs_sim python 后处理。
set -u

BLENDER="D:/Program Files/Blender Foundation/Blender 4.2/blender.exe"
PYEXE="C:/Users/97466/.conda/envs/ocs_sim/python.exe"
PKG="D:/我的文件/研究生学术/光学项目/0506新/项目重启_v0.4_BlenderOCS/v0.4_results/19_three_axis_p1_seed_roll_scan"
RENDER_PY="$PKG/scripts/p1_render_seed_roll.py"
POST_PY="$PKG/scripts/p1_postprocess_seed_roll.py"
LOG="$PKG/logs/p1_render_postprocess.log"

ROLLS="-60 -45 -30 -15 15 30 45 60"

echo "==== R131 P1 seed-roll scan smoke 全量开始 $(date) ====" | tee "$LOG"
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
echo "==== R131 P1 全量结束 $(date) ====" | tee -a "$LOG"

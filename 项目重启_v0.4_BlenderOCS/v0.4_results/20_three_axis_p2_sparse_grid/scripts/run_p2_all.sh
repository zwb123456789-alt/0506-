#!/usr/bin/env bash
# run_p2_all.sh —— R133 P2 sparse 3-axis grid 全量编排（1000 非零 roll 渲染单位）
# 8 个非零 roll × 125 唯一 pose。roll=0 复用 01_fullrun，不重渲。
# 每个 roll 一次 Blender 进程（渲染 125 pose）+ 一次 ocs_sim python 后处理。
set -u

BLENDER="D:/Program Files/Blender Foundation/Blender 4.2/blender.exe"
PYEXE="C:/Users/97466/.conda/envs/ocs_sim/python.exe"
PKG="D:/我的文件/研究生学术/光学项目/0506新/项目重启_v0.4_BlenderOCS/v0.4_results/20_three_axis_p2_sparse_grid"
RENDER_PY="$PKG/scripts/p2_render_sparse_grid.py"
POST_PY="$PKG/scripts/p2_postprocess_sparse_grid.py"
LOG="$PKG/logs/p2_render_postprocess.log"

ROLLS="-60 -45 -30 -15 15 30 45 60"

echo "==== R133 P2 sparse 3-axis grid 全量开始 $(date) ====" | tee "$LOG"
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
echo "==== R133 P2 全量结束 $(date) ====" | tee -a "$LOG"

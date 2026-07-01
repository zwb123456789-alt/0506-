#!/usr/bin/env bash
# run_l1m2_render_all.sh —— 1C-L1M2 全量渲染+后处理编排（后台长程执行）
# 逐几何串行：phase24 -> phase45 -> phase90 -> phase120
# 每几何：先渲染 2664 姿态（skip 已存在），再后处理生成 OCS。
# 断点续跑：渲染 skip_existing 默认开；后处理 resume 自身 summary。

set -u
BLENDER="D:/Program Files/Blender Foundation/Blender 4.2/blender.exe"
PY="C:/Users/97466/.conda/envs/ocs_sim/python.exe"
ROOT="d:/我的文件/研究生学术/光学项目/0506新/项目重启_v0.4_BlenderOCS"
cd "$ROOT" || exit 1

LOG="v0.4_results/11_l1m2_multigeometry_ocs/_l1m2_batch.log"
echo "==== L1M2 render+postprocess batch start: $(date) ====" | tee -a "$LOG"

for GEOM in phase24 phase45 phase90 phase120; do
  echo "" | tee -a "$LOG"
  echo "==== [$GEOM] RENDER start $(date) ====" | tee -a "$LOG"
  "$BLENDER" --background --python "06_v0.4_code/02_blender/render_l1m2_multigeometry.py" \
    -- --geom "$GEOM" >> "$LOG" 2>&1
  RC=$?
  NCAM=$(ls -1 "v0.4_results/11_l1m2_multigeometry_ocs/shadow_passes/$GEOM/"*_camera.exr 2>/dev/null | wc -l)
  echo "==== [$GEOM] RENDER done rc=$RC camera_exr=$NCAM/2664 $(date) ====" | tee -a "$LOG"

  echo "==== [$GEOM] POSTPROCESS start $(date) ====" | tee -a "$LOG"
  "$PY" "06_v0.4_code/05_postprocess/run_l1m2_multigeometry_postprocess.py" \
    --geom "$GEOM" --all >> "$LOG" 2>&1
  RC2=$?
  NOCS=$(ls -1 "v0.4_results/11_l1m2_multigeometry_ocs/postprocess/$GEOM/"*_ocs.json 2>/dev/null | wc -l)
  echo "==== [$GEOM] POSTPROCESS done rc=$RC2 ocs_json=$NOCS/2664 $(date) ====" | tee -a "$LOG"
done

echo "" | tee -a "$LOG"
echo "==== L1M2 batch ALL DONE: $(date) ====" | tee -a "$LOG"

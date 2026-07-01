#!/usr/bin/env bash
# run_mroll_probe_matrix.sh —— R116 子任务 C：M-roll 探针渲染+后处理编排
#
# M-roll 是 fixed-roll 边界探针（非三轴小项目）。策略：
#   - 分层子集 312 姿态（yaw step15 × pitch step15），覆盖 yaw/pitch 空间
#   - roll ∈ {+15,-15,+30,-30}（roll=0 复用现有 fixed-roll 数据）
#   - phase63 渲染+后处理（图像通道 + G1 OCS）；子集足够低成本
#   - full 2664 全量成本在报告中给出估算，不在本轮铺满
#
# 用法： bash run_mroll_probe_matrix.sh [phase63]   # 默认仅 phase63

set -u
BL="D:/Program Files/Blender Foundation/Blender 4.2/blender.exe"
PY="C:/Users/97466/.conda/envs/ocs_sim/python.exe"
cd "$(dirname "$0")/../.." || exit 1

SUBSET="v0.4_results/12_l1m3_degraded_mroll/mroll/mroll_subset_attitudes.json"
LOG="v0.4_results/12_l1m3_degraded_mroll/mroll/_mroll_probe.log"
: > "$LOG"

GEOM="${1:-phase63}"
ROLLS=(15 -15 30 -30)

# 构造子集 label（yaw/pitch，roll 后缀由脚本加）
SUBSET_LABELS=$("$PY" -c "import json;print(','.join(json.load(open(r'$SUBSET'))))")

for ROLL in "${ROLLS[@]}"; do
  ROLLTAG=$(printf "roll%+04d" "$ROLL")
  echo "=== RENDER $GEOM $ROLLTAG (312 subset) ===" | tee -a "$LOG"
  # 渲染：把子集 label 加 roll 后缀
  LABELS=$("$PY" -c "
import json
subset=json.load(open(r'$SUBSET'))
print(','.join('%s_%s'%(a,'$ROLLTAG') for a in subset))
")
  "$BL" --background --python "06_v0.4_code/02_blender/render_mroll_probe.py" -- \
      --geom "$GEOM" --roll "$ROLL" --labels "$LABELS" 2>&1 | grep -E "RENDERED:|SKIPPED_|FAILED:|SUCCESS" | tee -a "$LOG"

  echo "=== POSTPROCESS $GEOM $ROLLTAG ===" | tee -a "$LOG"
  "$PY" "06_v0.4_code/05_postprocess/run_mroll_probe_postprocess.py" \
      --geom "$GEOM" --roll "$ROLL" --attitudes-file "$SUBSET" 2>&1 | grep -E "COMPLETE|n_labels|本次待处理|完成" | tee -a "$LOG"
done
echo "[MROLL PROBE DONE]" | tee -a "$LOG"

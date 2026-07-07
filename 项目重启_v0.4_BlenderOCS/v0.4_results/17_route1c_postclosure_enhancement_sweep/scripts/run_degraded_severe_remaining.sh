#!/usr/bin/env bash
set -u
PY="C:/Users/97466/.conda/envs/ocs_sim/python.exe"
cd "$(dirname "$0")/../../.." || exit 1
LOG="v0.4_results/17_route1c_postclosure_enhancement_sweep/logs/degraded_severe_remaining.log"
: > "$LOG"
echo "[SEVERE REMAINING START] $(date)" | tee -a "$LOG"
for combo in "G1 joint" "G3 ocs_only" "G3 image_only" "G3 joint" "G5 ocs_only" "G5 image_only" "G5 joint"; do
  set -- $combo
  echo "--- $1 $2 $(date) ---" | tee -a "$LOG"
  "$PY" "06_v0.4_code/07_training/postclosure_degraded_severe_train.py" \
      --geom-group $1 --mode $2 --seed 42 --max-epochs 30 2>&1 \
      | grep -E "TEST (final|best )|DONE|Error|Traceback" | tee -a "$LOG"
done
echo "[SEVERE REMAINING DONE] $(date)" | tee -a "$LOG"

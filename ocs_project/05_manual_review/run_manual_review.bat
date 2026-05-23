@echo off
REM Manual Occlusion Review - Blender MVP launcher
REM Outputs under: 结果\人工遮挡抽查\run_YYYYMMDD_HHMMSS\

set BLENDER="D:\Program Files\Blender Foundation\Blender 5.0\blender.exe"
set SCRIPT="D:\我的文件\研究生学术\光学项目\0506新\ocs_project\05_manual_review\manual_review_blender.py"
set INPUT="D:\我的文件\研究生学术\光学项目\0506新\结果\遮挡验证\run_20260512_213850\manual_review_candidates.csv"
set MODEL_DIR="D:\我的文件\研究生学术\光学项目\0506新\建模\真实模型"
set OUTDIR="D:\我的文件\研究生学术\光学项目\0506新\结果\人工遮挡抽查"

REM Default params: MVP smoke test (3 cases, mhd=1.0, only rows with any occlusion)
set MAX_CASES=3
set MHD=1.0
set ONLY_OCC=1
set SELF_TOL=0.001
set MAX_RAY=10000

%BLENDER% --background --python %SCRIPT% -- ^
  --input %INPUT% ^
  --model_dir %MODEL_DIR% ^
  --outdir %OUTDIR% ^
  --max_cases %MAX_CASES% ^
  --mhd_filter %MHD% ^
  --only_occluded %ONLY_OCC% ^
  --self_hit_tol_mm %SELF_TOL% ^
  --max_ray_dist_mm %MAX_RAY% ^
  --save_blend 1 ^
  --render_png 1

echo.
echo [run_manual_review] done. Check: %OUTDIR%
pause

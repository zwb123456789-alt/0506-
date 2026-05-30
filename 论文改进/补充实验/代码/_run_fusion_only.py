"""Quick runner for fusion-only random split."""
import sys, os, json
_PROJECT_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(_PROJECT_ROOT, "ocs_project", "03_inversion"))
sys.path.insert(0, os.path.join(_PROJECT_ROOT, "ocs_project", "01_code"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from run_random_split import run_fusion_random, _find

manifest = _find(os.path.join(_PROJECT_ROOT, "结果", "模块A_重构",
    "multi_geom_ggx_yaw73_pitch37", "run_*", "multi_geom_manifest.json"))
image_dir = os.path.dirname(_find(os.path.join(_PROJECT_ROOT, "结果", "模块B_渲染",
    "run_*", "render_log.csv")))

print(f"Manifest: {manifest}")
print(f"Image: {image_dir}")

out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..",
    "结果", "random_split", "run_fusion_fix")
os.makedirs(out_dir, exist_ok=True)

s, _ = run_fusion_random(manifest, image_dir, "per_part", True, out_dir)
print(json.dumps(s, indent=2))
print("DONE")

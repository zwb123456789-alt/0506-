"""Step 11d runner: OCS+image joint with args wired in, log to file."""
import sys, os, signal

try:
    signal.signal(signal.SIGPIPE, signal.SIG_IGN)
except AttributeError:
    pass

log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_joint_11d_log.txt")
_real_stdout = sys.stdout
_real_stderr = sys.stderr
sys.stdout = open(log_path, "w", encoding="utf-8", buffering=1)
sys.stderr = sys.stdout

# Also close the original fds so pipe writes don't cause BrokenPipeError
try:
    _real_stdout.close()
    _real_stderr.close()
except Exception:
    pass

sys.argv = [
    "inv_joint.py",
    "--ocs-root", r"d:\我的文件\研究生学术\光学项目\0506新\结果\模块A_重构\multi_geom_ggx_yaw73_pitch37\run_20260520_162831",
    "--geom-set", "concat5",
    "--ocs-feat", "all",
    "--ocs-transform", "raw",
    "--image-dir", r"d:\我的文件\研究生学术\光学项目\0506新\结果\模块B_渲染\run_20260521_phase63_ggx",
    "--image-subdir", "brdf_images",
    "--out-root", r"d:\我的文件\研究生学术\光学项目\0506新\结果\模块C_反演\inv_joint",
]
print("=" * 60)
print("[11d] Starting run_joint_11d ...", flush=True)
import inv_joint
inv_joint.main()
print("[11d] DONE.", flush=True)
sys.stdout.close()

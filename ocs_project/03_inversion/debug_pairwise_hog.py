"""Step 11d debug：隔离 HOG 距离矩阵生成步骤，定位静默退出根因。

按 202605211536.md 诊断方案：
  A. 加载图像 + 提取 HOG
  B. 打印 shape / dtype / nbytes / finite
  C. 转 float32 + zscore_float32
  D. 调用 pairwise_euclidean_chunked（chunked GEMM）
  E. 打印 D_img 统计；不做 alpha sweep
"""
import os
import sys
import time
import signal

# 屏蔽 SIGPIPE（部分 Windows 下被外层管道关闭可能触发）
try:
    signal.signal(signal.SIGPIPE, signal.SIG_IGN)
except AttributeError:
    pass

# 自写日志，绕开 shell 管道
HERE = os.path.dirname(os.path.abspath(__file__))
LOG_PATH = os.path.join(HERE, "_debug_pairwise_hog_log.txt")
_real_stdout = sys.stdout
_real_stderr = sys.stderr
sys.stdout = open(LOG_PATH, "w", encoding="utf-8", buffering=1)
sys.stderr = sys.stdout
try:
    _real_stdout.close()
    _real_stderr.close()
except Exception:
    pass

print("=" * 70, flush=True)
print(f"[debug] log: {LOG_PATH}", flush=True)
print(f"[debug] argv: {sys.argv}", flush=True)
print("=" * 70, flush=True)

sys.path.insert(0, HERE)

import numpy as np
import inv_common as IC
import inv_joint as IJ


def fmt_mb(nbytes):
    return f"{nbytes / 1024 / 1024:.2f} MB"


def main():
    image_dir = r"d:\我的文件\研究生学术\光学项目\0506新\结果\模块B_渲染\run_20260521_phase63_ggx"
    image_subdir = "brdf_images"

    # ── A. 加载 HOG ──────────────────────────────────────────────
    print(f"[A] 加载图像目录: {image_dir}", flush=True)
    yaw, pitch, rows = IJ.load_image_data(image_dir, image_subdir)
    print(f"    yaw[N]={len(yaw)}  pitch[N]={len(pitch)}  rows={len(rows)}", flush=True)

    t0 = time.time()
    print("[A] 提取 HOG ...", flush=True)
    X = IJ.extract_hog_features(rows, verbose=True)
    print(f"    HOG 完成 in {time.time()-t0:.1f}s", flush=True)

    # ── B. 打印 shape / dtype / nbytes / finite ─────────────────
    print(f"[B] X.shape={X.shape}  dtype={X.dtype}  nbytes={fmt_mb(X.nbytes)}", flush=True)
    print(f"    finite_count = {int(np.isfinite(X).sum())} / {X.size}", flush=True)
    print(f"    min={float(np.nanmin(X)):.6f}  max={float(np.nanmax(X)):.6f}", flush=True)

    # ── C. 转 float32 + zscore ──────────────────────────────────
    print("[C] 转 float32 ...", flush=True)
    X32 = np.asarray(X, dtype=np.float32, order="C")
    print(f"    X32.shape={X32.shape}  dtype={X32.dtype}  nbytes={fmt_mb(X32.nbytes)}", flush=True)

    print("[C] zscore_float32 ...", flush=True)
    t0 = time.time()
    Xz = IC.zscore_float32(X32)
    print(f"    Xz.shape={Xz.shape}  dtype={Xz.dtype}  nbytes={fmt_mb(Xz.nbytes)}  "
          f"in {time.time()-t0:.2f}s", flush=True)
    print(f"    finite_count = {int(np.isfinite(Xz).sum())} / {Xz.size}", flush=True)
    print(f"    mean(col0)={float(Xz[:,0].mean()):.4e}  std(col0)={float(Xz[:,0].std()):.4f}", flush=True)

    # ── D. chunked pairwise euclidean ──────────────────────────
    print("[D] pairwise_euclidean_chunked ...", flush=True)
    t0 = time.time()
    D = IC.pairwise_euclidean_chunked(Xz, batch_size=128)
    print(f"    D.shape={D.shape}  dtype={D.dtype}  nbytes={fmt_mb(D.nbytes)}  "
          f"in {time.time()-t0:.2f}s", flush=True)

    # ── E. 距离矩阵健康检查 ────────────────────────────────────
    diag = np.diag(D)
    mask = ~np.eye(D.shape[0], dtype=bool)
    off = D[mask]
    print(f"[E] diag.min={float(diag.min())}  diag.max={float(diag.max())}", flush=True)
    print(f"    off.shape={off.shape}  finite={int(np.isfinite(off).sum())}/{off.size}", flush=True)
    print(f"    off.min={float(off.min()):.6f}  off.max={float(off.max()):.6f}  "
          f"off.mean={float(off.mean()):.6f}", flush=True)

    print("=" * 70, flush=True)
    print("[debug] D_img 生成成功 — pairwise 问题已隔离修复", flush=True)


if __name__ == "__main__":
    main()

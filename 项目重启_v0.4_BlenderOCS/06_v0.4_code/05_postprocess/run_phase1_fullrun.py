# -*- coding: utf-8 -*-
"""
run_phase1_fullrun.py —— Phase 1 全量后处理入口 wrapper
========================================================
R35 规划文件预期入口名为 run_phase1_fullrun.py，E17 实际交付为 run_full_postprocess.py。
本文件作为 R35 兼容 wrapper，将所有调用转发到 run_full_postprocess.py 的 main()。

使用方式同 run_full_postprocess.py：
    python run_phase1_fullrun.py --attitudes yaw010_pitch+000_roll+000,...
    python run_phase1_fullrun.py --all
    python run_phase1_fullrun.py --resume <summary.json>

命名统一说明（1C-E17-FIX01）：
    正式入口名 = run_full_postprocess.py（E17 实际交付，已通过 R36 smoke）
    兼容入口名 = run_phase1_fullrun.py（满足 R35 规划文件预期）
    两个入口等价，后续命令与文档统一使用 run_full_postprocess.py 或明确注明两者等价。
"""

import os
import sys
import importlib.util

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_FULL_POSTPROCESS = os.path.join(_THIS_DIR, "run_full_postprocess.py")

if not os.path.isfile(_FULL_POSTPROCESS):
    print(f"[FATAL] 主入口不存在: {_FULL_POSTPROCESS}")
    sys.exit(1)

# 加载 run_full_postprocess 模块并调用其 main()
spec = importlib.util.spec_from_file_location("run_full_postprocess", _FULL_POSTPROCESS)
module = importlib.util.module_from_spec(spec)
sys.modules["run_full_postprocess"] = module
spec.loader.exec_module(module)

if __name__ == "__main__":
    sys.exit(module.main())

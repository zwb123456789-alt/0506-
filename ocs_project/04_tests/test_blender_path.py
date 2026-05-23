# -*- coding: utf-8 -*-
"""
test_blender_path.py —— 验证 Blender 5.0 命令行可用
====================================================
仅做最小验证：调用 blender.exe --version 并打印输出。
通过条件：能看到 Blender 版本号。
"""

import os
import sys
import subprocess

# 让脚本可以在 04_tests/ 内独立运行，引用 01_code/config.py
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "01_code"))

from config import BLENDER_EXE


def main():
    print(f"[BLENDER_EXE] {BLENDER_EXE}")
    if not os.path.isfile(BLENDER_EXE):
        print("[FAIL] 路径不存在，请检查 config.py 中 BLENDER_EXE。")
        sys.exit(1)

    result = subprocess.run(
        [BLENDER_EXE, "--version"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="ignore",
    )
    print("---- STDOUT ----")
    print(result.stdout)
    print("---- STDERR ----")
    print(result.stderr)

    if result.returncode == 0 and "Blender" in (result.stdout or ""):
        print("\n[OK] Blender 可执行文件可用。")
    else:
        print(f"\n[FAIL] returncode={result.returncode}")
        sys.exit(1)


if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-
"""
generate_depth_epsilon_calibration_report.py
================================================================================
根据 shadow validation 结果生成 DEPTH_EPSILON_M_FINAL 校准报告
"""

import os
import sys
import json
import numpy as np
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = r"D:\我的文件\研究生学术\光学项目\0506新"
V04_PROJECT = os.path.join(PROJECT_ROOT, "项目重启_v0.4_BlenderOCS")
VALIDATION_DIR = os.path.join(V04_PROJECT, "v0.4_results", "00_validation", "shadow_validation")


def generate_markdown_report(summary_file, output_file):
    """生成 Markdown 格式的校准报告"""

    with open(summary_file, 'r', encoding='utf-8') as f:
        summary = json.load(f)

    n_validated = summary["attitudes_validated"]
    n_pass = summary["pass_count"]
    n_fail = summary["fail_count"]
    epsilon_initial = summary["depth_epsilon_initial"]
    epsilon_suggested = summary["depth_epsilon_suggested"]

    results = summary["results"]

    # 统计所有姿态的深度信息
    sun_depth_stats = []
    for r in results:
        if r["status"] == "PASS":
            sun_depth_stats.append({
                "label": r["label"],
                "mean": r["sun_depth_from_camera_position"]["mean"],
                "std": r["sun_depth_from_camera_position"]["std"],
                "range": r["sun_depth_from_camera_position"]["range"]
            })

    # 计算全局统计
    all_means = [s["mean"] for s in sun_depth_stats]
    all_stds = [s["std"] for s in sun_depth_stats]

    global_mean_of_means = np.mean(all_means) if all_means else 0.0
    global_std_of_stds = np.mean(all_stds) if all_stds else 0.0
    global_max_std = np.max(all_stds) if all_stds else 0.0

    # 生成报告内容
    report = f"""# DEPTH_EPSILON_M_FINAL 校准报告

最后更新：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
任务：Phase 0 Step 4 - 20 姿态 shadow validation

---

## 1. 执行摘要

**校准结果**：
- 初始阈值：{epsilon_initial:.4e} m
- **建议最终阈值**：**{epsilon_suggested:.4e} m**

**验证状态**：
- 总姿态数：{n_validated}
- 通过：{n_pass}
- 失败：{n_fail}

**校准方法**：
基于 20 个代表姿态的 sun depth 统计，采用 3-sigma 准则确定深度判定阈值。

---

## 2. 校准原理

**Shadow Validation 核心**：
对于可见且被照亮的表面点，camera-view 的 Position 和 sun-view 的 Depth 应满足几何一致性：

```
sun_depth = dot(position_camera, sun_direction_normalized)
```

**深度阈值用途**：
在 shadow rendering 中，判断一个点是否在阴影中：

```python
if abs(sun_depth_from_camera - sun_depth_actual) < DEPTH_EPSILON_M_FINAL:
    # 点在照亮区域
else:
    # 点在阴影中
```

**校准目标**：
找到一个合适的 `DEPTH_EPSILON_M_FINAL`，使得：
1. 不会因为数值误差将照亮区域误判为阴影
2. 不会因为阈值过大将阴影误判为照亮区域

---

## 3. 全局统计

基于 {len(sun_depth_stats)} 个通过验证的姿态：

| 统计量 | 值 (m) |
|--------|--------|
| Sun depth 均值的均值 | {global_mean_of_means:.4e} |
| Sun depth 标准差的均值 | {global_std_of_stds:.4e} |
| Sun depth 标准差的最大值 | {global_max_std:.4e} |

**3-sigma 准则**：
```
建议阈值 = max(初始阈值, 标准差均值 × 3)
         = max({epsilon_initial:.4e}, {global_std_of_stds:.4e} × 3)
         = {epsilon_suggested:.4e} m
```

---

## 4. 各姿态详细统计

| 姿态 | Sun Depth 均值 (m) | Sun Depth 标准差 (m) | Sun Depth 范围 (m) |
|------|-------------------|---------------------|-------------------|
"""

    for s in sun_depth_stats:
        report += f"| {s['label']} | {s['mean']:+.4f} | {s['std']:.4f} | [{s['range'][0]:+.4f}, {s['range'][1]:+.4f}] |\n"

    report += f"""
---

## 5. 校准结论

**推荐值**：`DEPTH_EPSILON_M_FINAL = {epsilon_suggested:.4e} m`

**应用位置**：
- 写入 manifest 字段规范（14 号冻结文件）
- 用于后续 shadow rendering 和 V_sun_macro 计算

**验证状态**：
{'[PASS] - 所有姿态通过验证' if n_fail == 0 else f'[PARTIAL] - {n_fail} 个姿态验证失败'}

---

## 6. 下一步

Phase 0 Step 4 完成后：
1. 更新 14 号文件中的 `depth_epsilon_m_final` 字段（需 Codex 批准）
2. 进入 Phase 0 Step 5：V_sun_macro reprojection（如果 Step 4 通过）
3. 继续完成 G0-G7 阶段门验证

---

**报告生成时间**：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

    # 写入报告
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"[SUCCESS] 校准报告已生成: {output_file}")


def main():
    print("=" * 80)
    print("生成 DEPTH_EPSILON_M_FINAL 校准报告")
    print("=" * 80)

    summary_file = os.path.join(VALIDATION_DIR, "shadow_validation_summary.json")

    if not os.path.isfile(summary_file):
        print(f"[ERROR] 找不到验证汇总文件: {summary_file}")
        print("请先运行 validate_shadow_consistency.py")
        return 1

    output_file = os.path.join(VALIDATION_DIR, "depth_epsilon_calibration_report.md")

    generate_markdown_report(summary_file, output_file)

    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""备份汇报所需的关键图表和数据文件"""
import os
import shutil
from pathlib import Path

ROOT = Path(r"d:\我的文件\研究生学术\光学项目\0506新")
REPORT_DIR = ROOT / "汇报0521_完整版"
FIG_DIR = REPORT_DIR / "figures"
DATA_DIR = REPORT_DIR / "data"

FIG_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)


def copy_if_exists(src, dst, desc=""):
    if src.exists():
        shutil.copy2(src, dst)
        print(f"[OK] {desc}")
        return True
    else:
        print(f"[SKIP] {desc}")
        return False


def copy_dir_if_exists(src_dir, dst_dir, desc="", pattern="*.png"):
    """复制目录中匹配模式的所有文件"""
    if not src_dir.exists():
        print(f"[SKIP] {desc}: 目录不存在")
        return 0
    dst_dir.mkdir(parents=True, exist_ok=True)
    count = 0
    for f in src_dir.glob(pattern):
        shutil.copy2(f, dst_dir / f.name)
        count += 1
    print(f"[OK] {desc}: {count} 个文件")
    return count


print("=" * 60)
print("开始备份汇报文件...")
print("=" * 60)

# ========== 1. BRDF 验证图表 ==========
print("\n[1/6] BRDF 验证图表")
brdf_base = ROOT / "结果/BRDF验证"

copy_if_exists(
    brdf_base / "plane_batch_20260519_204323/fig_plane_batch_compare.png",
    FIG_DIR / "fig_plane_batch_compare.png",
    "单平板三端闭合")

copy_if_exists(
    brdf_base / "plane_batch_20260519_204323/plane_batch_validation_report.md",
    DATA_DIR / "plane_batch_validation_report.md",
    "单平板验证报告")

copy_if_exists(
    brdf_base / "plane_batch_20260519_204323/plane_batch_validation.csv",
    DATA_DIR / "plane_batch_validation.csv",
    "单平板验证数据")

# L 型 - 检查有哪些文件
L_dir = brdf_base / "L_plate_20260520_103105"
if L_dir.exists():
    for f in sorted(L_dir.glob("*.png")):
        copy_if_exists(f, FIG_DIR / f"L_plate_{f.name}", f"L 型图表: {f.name}")
    for f in sorted(L_dir.glob("*.csv")):
        copy_if_exists(f, DATA_DIR / f"L_plate_{f.name}", f"L 型数据: {f.name}")

# 立方体 - 检查有哪些文件
cube_dir = brdf_base / "cube_20260520_103846"
if cube_dir.exists():
    for f in sorted(cube_dir.glob("*.png")):
        copy_if_exists(f, FIG_DIR / f"cube_{f.name}", f"立方体图表: {f.name}")
    for f in sorted(cube_dir.glob("*.csv")):
        copy_if_exists(f, DATA_DIR / f"cube_{f.name}", f"立方体数据: {f.name}")

# ========== 2. OCS 扫描结果图表 ==========
print("\n[2/6] OCS 扫描结果图表")
ocs_dir = ROOT / "结果/模块A_重构/2d_yaw73_pitch37/run_20260520_160847"

ocs_png_map = {
    "fig01_ocs_3d_surface.png": "GGX OCS 3D 曲面",
    "fig02_ocs_heatmap.png": "GGX OCS 热图 (yaw x pitch)",
    "fig03_parts_heatmap.png": "三部件 OCS 热图",
    "fig04_occlusion_ratio_heatmap.png": "遮挡率热图",
    "fig05_ocs_loss_heatmap.png": "遮挡损失热图",
    "fig06_satellite_model.png": "卫星模型可视化",
}

for fname, desc in ocs_png_map.items():
    copy_if_exists(ocs_dir / fname, FIG_DIR / fname, desc)

copy_if_exists(ocs_dir / "ocs_scan.csv", DATA_DIR / "ocs_scan_ggx_5deg.csv", "GGX 5度网格 OCS CSV")
copy_if_exists(ocs_dir / "ocs_scan.json", DATA_DIR / "ocs_scan_ggx_5deg.json", "GGX 5度网格 OCS JSON")
copy_if_exists(ocs_dir / "config_used.json", DATA_DIR / "config_ocs_ggx_5deg.json", "OCS 扫描配置")

# ========== 3. 多观测几何图表 ==========
print("\n[3/6] 多观测几何图表")
multi_dir = ROOT / "结果/模块A_重构/multi_geom_ggx_yaw73_pitch37/run_20260520_162831"

# 每个几何一个子目录
geom_dirs = [
    "phase24_near_backscatter",
    "phase45_overhead",
    "phase63_backscatter",
    "phase90_side",
    "phase120_forward_scatter",
]

for gdir in geom_dirs:
    gpath = multi_dir / gdir
    if gpath.exists():
        # 复制 fig02_ocs_heatmap.png（最有代表性的）
        for fname in ["fig02_ocs_heatmap.png", "fig04_occlusion_ratio_heatmap.png"]:
            copy_if_exists(gpath / fname, FIG_DIR / f"{gdir}_{fname}", f"多几何 {gdir} {fname}")
        # 复制 config
        copy_if_exists(gpath / "config_used.json", DATA_DIR / f"config_{gdir}.json", f"配置 {gdir}")

copy_if_exists(multi_dir / "multi_geom_manifest.json",
               DATA_DIR / "multi_geom_manifest.json", "多几何配置清单")

# ========== 4. MLP 反演数据 ==========
print("\n[4/6] MLP OCS 回归数据")
mlp_dir = ROOT / "结果/模块C_反演/mlp_ocs/run_20260521_084723"

# 训练曲线 CSV
for feat in ["all_raw", "all_log", "per_part_log", "total_log", "obs_total_log"]:
    for seed in range(5):
        copy_if_exists(
            mlp_dir / f"train_curve_{feat}_seed{seed}.csv",
            DATA_DIR / f"mlp_train_curve_{feat}_seed{seed}.csv",
            f"MLP {feat} seed{seed} 训练曲线")

# 预测结果
for pred_file in sorted(mlp_dir.glob("predictions_test_*.csv")):
    copy_if_exists(pred_file, DATA_DIR / f"mlp_{pred_file.name}", f"MLP 预测: {pred_file.name}")

# 指标汇总
copy_if_exists(mlp_dir / "metrics_by_seed.csv", DATA_DIR / "mlp_metrics_by_seed.csv", "MLP 各 seed 指标")
copy_if_exists(mlp_dir / "metrics_summary.json", DATA_DIR / "mlp_metrics_summary.json", "MLP 指标汇总 JSON")
copy_if_exists(mlp_dir / "config_used.json", DATA_DIR / "mlp_config_used.json", "MLP 训练配置")

# ========== 5. CNN 反演数据 ==========
print("\n[5/6] CNN 图像回归数据")
cnn_dir = ROOT / "结果/模块C_反演/cnn_image/run_20260521_164437_final_log1p"

for seed in range(5):
    copy_if_exists(cnn_dir / f"train_curve_seed{seed}.csv",
                   DATA_DIR / f"cnn_train_curve_seed{seed}.csv",
                   f"CNN seed{seed} 训练曲线")
    copy_if_exists(cnn_dir / f"metrics_seed{seed}.json",
                   DATA_DIR / f"cnn_metrics_seed{seed}.json",
                   f"CNN seed{seed} 指标")
    copy_if_exists(cnn_dir / f"predictions_seed{seed}.csv",
                   DATA_DIR / f"cnn_predictions_seed{seed}.csv",
                   f"CNN seed{seed} 预测")

copy_if_exists(cnn_dir / "summary.csv", DATA_DIR / "cnn_summary.csv", "CNN 汇总 CSV")
copy_if_exists(cnn_dir / "summary.json", DATA_DIR / "cnn_summary.json", "CNN 汇总 JSON")
copy_if_exists(cnn_dir / "config_used.json", DATA_DIR / "cnn_config_used.json", "CNN 训练配置")

# ========== 6. 联合反演数据 ==========
print("\n[6/6] 联合反演数据")
joint_dir = ROOT / "结果/模块C_反演/inv_joint/run_20260521_155144"

copy_if_exists(joint_dir / "alpha_sweep.csv", DATA_DIR / "joint_alpha_sweep.csv", "联合反演 alpha 扫描")
copy_if_exists(joint_dir / "ablation_table.md", DATA_DIR / "joint_ablation_table.md", "联合反演消融表")
copy_if_exists(joint_dir / "predictions_best.csv", DATA_DIR / "joint_predictions_best.csv", "联合反演最佳预测")
copy_if_exists(joint_dir / "summary.json", DATA_DIR / "joint_summary.json", "联合反演摘要")
copy_if_exists(joint_dir / "config_used.json", DATA_DIR / "joint_config_used.json", "联合反演配置")

# ========== 复制渲染图像示例 ==========
print("\n[bonus] 渲染图像示例")
brdf_img_dir = ROOT / "结果/模块B_渲染/run_20260521_phase63_ggx/brdf_images"
if brdf_img_dir.exists():
    example_poses = [
        "yaw000.00_pitch+00.00_brdf.png",
        "yaw045.00_pitch-45.00_brdf.png",
        "yaw090.00_pitch-40.00_brdf.png",
        "yaw150.00_pitch-80.00_brdf.png",
        "yaw180.00_pitch+00.00_brdf.png",
    ]
    for fname in example_poses:
        copy_if_exists(brdf_img_dir / fname, FIG_DIR / fname, f"渲染示例: {fname}")

# 复制渲染日志
copy_if_exists(ROOT / "结果/模块B_渲染/run_20260521_phase63_ggx/render_log.csv",
               DATA_DIR / "render_log_phase63.csv", "渲染日志")
copy_if_exists(ROOT / "结果/模块B_渲染/run_20260521_phase63_ggx/ocs_comparison.csv",
               DATA_DIR / "ocs_comparison_phase63.csv", "OCS A/B 对比")

print("\n" + "=" * 60)
print("备份完成！")
print(f"  图表目录: {FIG_DIR}")
print(f"  数据目录: {DATA_DIR}")
print(f"  汇报文档: {REPORT_DIR / '进度汇报_20260521.md'}")
print("=" * 60)

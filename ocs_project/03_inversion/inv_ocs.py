"""
模块 C · 反演脚本 1：纯 OCS 表 kNN 检索（Step 11b 升级版）
============================================================
支持：
  1. 单几何 kNN × 5（每个观测几何独立跑）
  2. 五几何拼接 kNN（特征横向拼接）
  3. LOO / 10°→5° coarse-to-fine / random split
  4. --log 选项（log10 变换检查镜面峰尺度影响）
  5. --feat 选项（total / per_part / all）
  6. --ablation 一键跑完紧凑消融矩阵

输出落 `结果/模块C_反演/inv_ocs/run_YYYYMMDD_HHMMSS/`。
"""

import argparse
import json
import os
from datetime import datetime

import numpy as np

import inv_common as ic

# 默认多几何 manifest
MANIFEST = os.path.normpath(os.path.join(
    os.path.dirname(__file__), "..", "..",
    "结果", "模块A_重构", "multi_geom_ggx_yaw73_pitch37",
    "run_20260520_162831", "multi_geom_manifest.json"
))
OUT_ROOT = os.path.normpath(os.path.join(
    os.path.dirname(__file__), "..", "..",
    "结果", "模块C_反演", "inv_ocs"
))


def parse_args():
    p = argparse.ArgumentParser(description="OCS-only kNN 姿态反演")
    p.add_argument("--manifest", default=MANIFEST, help="multi_geom_manifest.json 路径")
    p.add_argument("--out-root", default=OUT_ROOT, help="输出根目录")
    p.add_argument("--geoms", default="all", help="几何索引 'all' 或 '0,2,4'")
    p.add_argument("--feat", default="all", choices=["all", "total", "per_part"],
                   help="特征子集：all=全部9维, total=3维总OCS+遮挡率, per_part=6维分部件OCS")
    p.add_argument("--log", action="store_true", help="log10 变换特征")
    p.add_argument("--split", default="all", choices=["all", "loo", "c2f", "random"],
                   help="split 类型")
    p.add_argument("--ablation", action="store_true",
                   help="一键跑完紧凑消融矩阵 (2geom×2split×3feat×2transform=24)")
    return p.parse_args()


# ---- 特征选择与 log 列处理 ----


def get_log_skip_cols(feat_mode):
    """返回 log 变换时应跳过的列索引（遮挡率列）。"""
    if feat_mode in ("per_part", "obs_total"):
        return None  # 全是 OCS 特征，无遮挡率
    # all (9维) 和 total (3维) 模式下，遮挡率都在第 2 列
    return {2}


def get_dim_label(feat_mode, n_geoms):
    """返回特征维度标签。"""
    base = {"obs_total": 1, "total": 3, "per_part": 6, "all": 9}[feat_mode]
    return base * n_geoms


# ---- 单次实验运行 ----

def run_single_geom(label_order, feat_dict, yaw_dict, pitch_dict, args, feat_mode, use_log):
    """单几何 kNN × 5。"""
    all_metrics = []
    log_skip = get_log_skip_cols(feat_mode)
    for label in label_order:
        feats = ic.select_features(feat_dict[label], feat_mode)
        yaw = yaw_dict[label]
        pitch = pitch_dict[label]
        N = len(yaw)

        # LOO
        metrics, _, _, _ = ic.run_knn_experiment(
            feats, yaw, pitch, feats, yaw, pitch,
            query_self_indices=np.arange(N),
            label=f"single:{label}:LOO:{feat_mode}:{'log' if use_log else 'raw'}",
            log_transform_feats=use_log, log_skip_cols=log_skip)
        all_metrics.append(metrics)

        # 10° → 5° coarse-to-fine
        split = ic.split_coarse_to_fine(yaw, pitch, coarse_step=10.0)
        metrics_c2f, _, _, _ = ic.run_knn_experiment(
            feats[split["train_idx"]], yaw[split["train_idx"]], pitch[split["train_idx"]],
            feats[split["test_idx"]], yaw[split["test_idx"]], pitch[split["test_idx"]],
            label=f"single:{label}:10°→5°:{feat_mode}:{'log' if use_log else 'raw'}",
            log_transform_feats=use_log, log_skip_cols=log_skip)
        all_metrics.append(metrics_c2f)

    return all_metrics


def run_concat(label_order, feat_dict, yaw_dict, pitch_dict, feat_mode, use_log):
    """五几何拼接 kNN。"""
    feats_concat, yaw, pitch, _ = ic.build_concat_features_with_mode(
        feat_dict, yaw_dict, pitch_dict, label_order, feat_mode)
    log_skip = get_log_skip_cols(feat_mode)
    N = len(yaw)
    all_metrics = []

    # LOO
    metrics, _, _, _ = ic.run_knn_experiment(
        feats_concat, yaw, pitch, feats_concat, yaw, pitch,
        query_self_indices=np.arange(N),
        label=f"concat:5geom:LOO:{feat_mode}:{'log' if use_log else 'raw'}",
        log_transform_feats=use_log, log_skip_cols=log_skip)
    all_metrics.append(metrics)

    # 10° → 5° coarse-to-fine
    split = ic.split_coarse_to_fine(yaw, pitch, coarse_step=10.0)
    metrics_c2f, _, _, _ = ic.run_knn_experiment(
        feats_concat[split["train_idx"]], yaw[split["train_idx"]], pitch[split["train_idx"]],
        feats_concat[split["test_idx"]], yaw[split["test_idx"]], pitch[split["test_idx"]],
        label=f"concat:5geom:10°→5°:{feat_mode}:{'log' if use_log else 'raw'}",
        log_transform_feats=use_log, log_skip_cols=log_skip)
    all_metrics.append(metrics_c2f)

    return all_metrics, yaw, pitch


# ---- 消融矩阵 ----

ABLATION_GEOM_SETS = [
    ("phase63", [0]),       # 只用 phase63 单几何
    ("concat5", "all"),     # 五几何拼接
]

ABLATION_SPLITS = ["loo", "c2f"]

ABLATION_FEATS = ["total", "per_part", "all"]

ABLATION_TRANSFORMS = [
    ("raw", False, "raw"),
    ("log", True,  "log"),
]


def run_ablation(label_order, feat_dict, yaw_dict, pitch_dict):
    """运行紧凑消融矩阵：2 geom_set × 2 split × 3 feat × 2 transform = 24 实验。"""
    all_metrics = []

    for geom_name, geom_filter in ABLATION_GEOM_SETS:
        # 选择几何
        if geom_filter == "all":
            cur_labels = label_order[:]
        else:
            cur_labels = [label_order[i] for i in geom_filter if i < len(label_order)]

        for split_name in ABLATION_SPLITS:
            for feat_mode in ABLATION_FEATS:
                for xform_name, use_log, tag in ABLATION_TRANSFORMS:
                    log_skip = get_log_skip_cols(feat_mode)
                    n_geoms = len(cur_labels)
                    dim = get_dim_label(feat_mode, n_geoms)

                    print(f"\n  ▶ geom={geom_name} split={split_name} feat={feat_mode} "
                          f"xform={xform_name} dim={dim}")

                    if geom_filter == "all" or len(cur_labels) > 1:
                        # 多几何 concat — 每个几何先选特征再拼接
                        feats, yaw, pitch, _ = ic.build_concat_features_with_mode(
                            feat_dict, yaw_dict, pitch_dict, cur_labels, feat_mode)

                        if split_name == "loo":
                            metrics, _, _, _ = ic.run_knn_experiment(
                                feats, yaw, pitch, feats, yaw, pitch,
                                query_self_indices=np.arange(len(yaw)),
                                label=f"{geom_name}:LOO:{feat_mode}:{tag}",
                                log_transform_feats=use_log, log_skip_cols=log_skip)
                        else:
                            split = ic.split_coarse_to_fine(yaw, pitch, coarse_step=10.0)
                            metrics, _, _, _ = ic.run_knn_experiment(
                                feats[split["train_idx"]], yaw[split["train_idx"]],
                                pitch[split["train_idx"]],
                                feats[split["test_idx"]], yaw[split["test_idx"]],
                                pitch[split["test_idx"]],
                                label=f"{geom_name}:10°→5°:{feat_mode}:{tag}",
                                log_transform_feats=use_log, log_skip_cols=log_skip)
                    else:
                        # 单几何
                        label = cur_labels[0]
                        feats = ic.select_features(feat_dict[label], feat_mode)
                        yaw = yaw_dict[label]
                        pitch = pitch_dict[label]

                        if split_name == "loo":
                            metrics, _, _, _ = ic.run_knn_experiment(
                                feats, yaw, pitch, feats, yaw, pitch,
                                query_self_indices=np.arange(len(yaw)),
                                label=f"{geom_name}:LOO:{feat_mode}:{tag}",
                                log_transform_feats=use_log, log_skip_cols=log_skip)
                        else:
                            split = ic.split_coarse_to_fine(yaw, pitch, coarse_step=10.0)
                            metrics, _, _, _ = ic.run_knn_experiment(
                                feats[split["train_idx"]], yaw[split["train_idx"]],
                                pitch[split["train_idx"]],
                                feats[split["test_idx"]], yaw[split["test_idx"]],
                                pitch[split["test_idx"]],
                                label=f"{geom_name}:10°→5°:{feat_mode}:{tag}",
                                log_transform_feats=use_log, log_skip_cols=log_skip)

                    all_metrics.append(metrics)
                    # 打印单行结果
                    m = metrics
                    print(f"     mean={m['angular_err_mean']:.2f}° med={m['angular_err_median']:.2f}° "
                          f"p90={m['angular_err_p90']:.2f}° "
                          f"T1@5={m.get('top1_acc@5deg',0):.1%} "
                          f"T5@5={m.get('top5_acc@5deg',0):.1%} "
                          f"T1@10={m.get('top1_acc@10deg',0):.1%} "
                          f"T5@10={m.get('top5_acc@10deg',0):.1%}")

    return all_metrics


# ---- 主入口 ----

def main():
    args = parse_args()

    print("=" * 80)
    print("  模块 C · OCS-only kNN 姿态反演 (Step 11b)")
    print(f"  数据源: {args.manifest}")
    if args.ablation:
        print("  模式: 紧凑消融矩阵 (2geom×2split×3feat×2transform=24)")
    else:
        print(f"  特征模式: {args.feat}")
        print(f"  log10 变换: {args.log}")
    print("=" * 80)

    # 加载数据
    label_order, geoms, feat_dict, yaw_dict, pitch_dict = ic.load_multi_geom(args.manifest)
    if not label_order:
        print("[错误] 没有加载到任何几何数据")
        return

    print(f"\n  单几何样本数: {len(yaw_dict[label_order[0]])}")
    print(f"  几何数: {len(label_order)}")

    # ---- 实验 ----
    all_metrics = []

    if args.ablation:
        all_metrics = run_ablation(label_order, feat_dict, yaw_dict, pitch_dict)
        # 取最佳行的 yaw/pitch 用于保存（concat all feat raw LOO）
        feats_concat, yaw_concat, pitch_concat, _ = ic.build_concat_features(
            feat_dict, yaw_dict, pitch_dict, label_order)
    else:
        # 过滤几何
        cur_labels = label_order[:]
        if args.geoms != "all":
            keep_indices = [int(x.strip()) for x in args.geoms.split(",")]
            cur_labels = [cur_labels[i] for i in keep_indices if i < len(cur_labels)]
            print(f"  已过滤，仅使用几何: {cur_labels}")

        print(f"  特征维度: {feat_dict[cur_labels[0]].shape[1]} "
              f"(选择后: {ic.select_features(feat_dict[cur_labels[0]], args.feat).shape[1]})")

        # 单几何
        print("\n" + "-" * 60)
        print("【实验组 1】单几何 OCS kNN")
        print("-" * 60)
        all_metrics += run_single_geom(cur_labels, feat_dict, yaw_dict, pitch_dict,
                                       args, args.feat, args.log)

        # 五几何拼接
        print("\n" + "-" * 60)
        print("【实验组 2】五几何拼接 OCS kNN")
        print("-" * 60)
        concat_metrics, yaw_concat, pitch_concat = run_concat(
            cur_labels, feat_dict, yaw_dict, pitch_dict, args.feat, args.log)
        all_metrics += concat_metrics

    # ---- 输出 ----
    print("\n" + ic.format_metrics_table(all_metrics))

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    if args.ablation:
        feature_tag = "ablation"
    else:
        feature_tag = f"feat_{args.feat}" + ("_log" if args.log else "")
    out_dir = os.path.join(args.out_root, f"run_{stamp}_{feature_tag}")
    ic.save_metrics(out_dir, all_metrics,
                    extra_config={
                        "manifest": args.manifest,
                        "feature_mode": args.feat,
                        "log_transform": args.log,
                        "ablation": args.ablation,
                        "n_geometries": len(label_order),
                        "geom_labels": label_order,
                        "n_samples_per_geom": int(len(yaw_dict[label_order[0]])),
                    },
                    yaw=yaw_concat, pitch=pitch_concat,
                    details=None)
    print(f"\n  输出目录: {out_dir}")


if __name__ == "__main__":
    main()

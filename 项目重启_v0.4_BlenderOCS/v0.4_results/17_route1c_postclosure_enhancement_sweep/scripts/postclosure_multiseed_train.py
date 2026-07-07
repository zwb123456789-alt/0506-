#!/usr/bin/env python3
"""
postclosure_multiseed_train.py —— R126 子任务 B：multi-seed sanity（派生 wrapper）

红线：不改旧脚本、不改 split、不改姿态网格、不换 backbone。
复用 train_l1m2_multigeometry 的 model / loss / metrics / split / posterior-like，
唯一改动：把【split seed】与【模型初始化 seed】分离。

原始 train_l1m2_multigeometry.py 中 split_pint(table, seed=args.seed) 使 split 与
训练 seed 共用 --seed，不可分离。本 wrapper：
  - split 固定用 SPLIT_SEED=42（沿用 R115/R125 确定性 split）
  - 模型初始化/训练随机性用 --model-seed ∈ {7,123}
从而回答“主结论对训练随机种子是否敏感”，同时保持 split/test 集合不变。

预注册口径：P-INT clean, ocs_only, L1-G1/G3/G5, split_seed=42, model_seed∈{7,123}。
运行数：3 几何 × 2 新种子 = 6 个新 run。

用法：
  python postclosure_multiseed_train.py --geom-group G5 --model-seed 7 --max-epochs 30
"""

import argparse
import copy
import csv
import json
import sys
import time
from pathlib import Path

import numpy as np
import torch
import torch.optim as optim
from torch.utils.data import DataLoader

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "06_v0.4_code" / "07_training"))

from dataset_l1m2_multigeometry import (  # noqa: E402
    build_multigeometry_table, fit_flux_transform, L1M2Dataset,
)
from train_l1m2_multigeometry import (  # noqa: E402
    L1M2RegModel, compute_metrics, make_targets, reg_loss,
    collect_predictions, build_candidate_grid, posterior_like_scores,
    yaw_circ_err, split_pint, MAX_EPOCHS_HARD,
)

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

OUT = PROJECT_ROOT / "v0.4_results" / "17_route1c_postclosure_enhancement_sweep" / "multiseed"
SPLIT_SEED = 42   # 固定 split，沿用 R115/R125


def evaluate(model, loader, device):
    yp, pp, yt, pt, _ = collect_predictions(model, loader, device)
    return compute_metrics(yp, pp, yt, pt)


def train_one_epoch(model, loader, opt, device, nw):
    model.train(); tot, nb = 0.0, 0
    for b in loader:
        bd = {}
        if "ocs" in b and model.mode in ("ocs_only", "joint"):
            bd["ocs"] = b["ocs"].to(device)
        if "image" in b and model.mode in ("image_only", "joint"):
            bd["image"] = b["image"].to(device)
        target = make_targets(b["yaw_deg"], b["pitch_deg"], device)
        out = model(bd); loss = reg_loss(out, target, nw)
        opt.zero_grad(); loss.backward(); opt.step()
        tot += loss.item(); nb += 1
    return tot / nb


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--geom-group", choices=["G1", "G3", "G5"], required=True)
    ap.add_argument("--mode", choices=["ocs_only", "image_only", "joint"], default="ocs_only")
    ap.add_argument("--model-seed", type=int, required=True)
    ap.add_argument("--max-epochs", type=int, default=30)
    ap.add_argument("--lr", type=float, default=1e-3)
    ap.add_argument("--batch-size", type=int, default=64)
    ap.add_argument("--norm-weight", type=float, default=0.1)
    ap.add_argument("--device", default="auto")
    args = ap.parse_args()

    if args.max_epochs > MAX_EPOCHS_HARD:
        print(f"[BLOCKED] max-epochs>{MAX_EPOCHS_HARD}"); return 1

    device = torch.device("cuda" if (args.device == "auto" and torch.cuda.is_available())
                          else (args.device if args.device != "auto" else "cpu"))
    # 模型初始化/训练随机性用 model-seed；split 用固定 SPLIT_SEED
    torch.manual_seed(args.model_seed); np.random.seed(args.model_seed)
    if device.type == "cuda":
        torch.cuda.manual_seed(args.model_seed)

    table, geoms = build_multigeometry_table(args.geom_group)
    ocs_dim = len(geoms)
    # 关键：split 固定 seed=42（与 seed42 基线同一 train/val/test）
    tr, va, te = split_pint(table, seed=SPLIT_SEED)
    flux_tf = fit_flux_transform(tr) if args.mode in ("ocs_only", "joint") else None

    run_name = f"P-INT_{args.geom_group}_{args.mode}_splitseed{SPLIT_SEED}_modelseed{args.model_seed}"
    run_dir = OUT / "runs" / run_name
    run_dir.mkdir(parents=True, exist_ok=True)

    use_gpu = device.type == "cuda"
    mk = lambda recs, shuf: DataLoader(
        L1M2Dataset(recs, args.mode, flux_tf), batch_size=args.batch_size,
        shuffle=shuf, num_workers=0, pin_memory=use_gpu)
    train_loader, val_loader, test_loader = mk(tr, True), mk(va, False), mk(te, False)

    model = L1M2RegModel(args.mode, ocs_dim).to(device)
    n_params = sum(p.numel() for p in model.parameters())
    opt = optim.Adam(model.parameters(), lr=args.lr)

    print(f"{'='*64}\nMULTISEED | {run_name}")
    print(f"geoms={geoms} device={device} split_seed={SPLIT_SEED} model_seed={args.model_seed}")
    print(f"train/val/test={len(tr)}/{len(va)}/{len(te)}\n{'='*64}")

    run_config = {
        "task": "1C-postclosure_multiseed_sanity",
        "geom_group": args.geom_group, "geoms": geoms, "ocs_dim": ocs_dim,
        "mode": args.mode, "protocol": "P-INT",
        "split_seed": SPLIT_SEED, "model_seed": args.model_seed,
        "max_epochs": args.max_epochs, "lr": args.lr, "batch_size": args.batch_size,
        "norm_weight": args.norm_weight,
        "split": "P-INT(pitch-stratified random), split seed FIXED=42",
        "flux_transform": flux_tf, "n_train": len(tr), "n_val": len(va), "n_test": len(te),
        "n_params": n_params, "device": str(device),
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "note": "split 与 seed42 基线一致；仅模型初始化/训练随机性使用 model_seed，检验主结论稳健性。",
    }
    json.dump(run_config, open(run_dir / "run_config.json", "w", encoding="utf-8"),
              indent=2, ensure_ascii=False)

    log_rows = []
    best_cmae, best_epoch, best_state = float("inf"), -1, None
    t0 = time.time()
    for ep in range(1, args.max_epochs + 1):
        loss = train_one_epoch(model, train_loader, opt, device, args.norm_weight)
        vm = evaluate(model, val_loader, device)
        log_rows.append({"epoch": ep, "train_loss": loss,
                         "val_yaw_cmae_deg": vm["yaw_circular_mae_deg"],
                         "val_yaw_hit@10": vm["yaw_hit@10"]})
        if vm["yaw_circular_mae_deg"] < best_cmae:
            best_cmae = vm["yaw_circular_mae_deg"]; best_epoch = ep
            best_state = copy.deepcopy({k: v.detach().cpu().clone()
                                        for k, v in model.state_dict().items()})
    elapsed = time.time() - t0

    with open(run_dir / "train_log.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(log_rows[0].keys()))
        w.writeheader(); w.writerows(log_rows)

    grid = build_candidate_grid()

    def eval_dump(tag, ckpt):
        vmet = evaluate(model, val_loader, device)
        yp, pp, yt, pt, rids = collect_predictions(model, test_loader, device)
        tmet = compute_metrics(yp, pp, yt, pt)
        for m in (vmet, tmet):
            m["elapsed_s"] = elapsed; m["run"] = run_name; m["select"] = tag
            m["best_epoch"] = best_epoch; m["geom_group"] = args.geom_group
            m["mode"] = args.mode; m["protocol"] = "P-INT"
            m["split_seed"] = SPLIT_SEED; m["model_seed"] = args.model_seed
        json.dump(vmet, open(run_dir / f"metrics_val_{tag}.json", "w", encoding="utf-8"),
                  indent=2, ensure_ascii=False)
        json.dump(tmet, open(run_dir / f"metrics_test_{tag}.json", "w", encoding="utf-8"),
                  indent=2, ensure_ascii=False)
        scores, top5, ent, margin = posterior_like_scores(yp, pp, grid)
        yce = yaw_circ_err(yp, yt); pae = np.abs(pp - pt)
        np.savez(run_dir / f"samples_test_{tag}.npz",
                 record_id=np.array(rids), yaw_true_deg=yt, pitch_true_deg=pt,
                 yaw_pred_deg=yp, pitch_pred_deg=pp,
                 yaw_circular_error_deg=yce, pitch_abs_error_deg=pae,
                 geometry_group=np.array([args.geom_group] * len(rids)),
                 mode=np.array([args.mode] * len(rids)),
                 entropy=ent, margin=margin)
        torch.save({"model_state": model.state_dict(), "run_config": run_config,
                    "select": tag, "best_epoch": best_epoch}, run_dir / ckpt)
        return tmet

    tm_final = eval_dump("final", "checkpoint_final.pt")
    if best_state is not None:
        model.load_state_dict(best_state)
    tm_best = eval_dump("best", "checkpoint_best.pt")

    print(f"[TEST final] cmae={tm_final['yaw_circular_mae_deg']:.2f} hit@30={tm_final['yaw_hit@30']:.3f}")
    print(f"[TEST best ] (ep{best_epoch}) cmae={tm_best['yaw_circular_mae_deg']:.2f} hit@30={tm_best['yaw_hit@30']:.3f}")
    print(f"[DONE] {run_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

# 1C-E19 训练入口与数据切分准备 —— Claude 执行报告

最后更新：2026-06-24  
执行端：Claude  
依据审阅：`04_Codex审阅/R38_Codex_审阅_1C-E18全量通过成果归档但训练暂不放行.md` §6

---

## 0. 执行摘要

```text
1C-E19：训练入口与数据切分方案准备 —— PASS
- split manifest 已生成（train=2109, val=259, test=296）
- PyTorch Dataset + DataLoader 已实现并冒烟通过
- 训练入口骨架（CNN/MLP/joint）已实现并前向冒烟通过
- emoji/GBK 风险输出已清理
- 不训练、不写论文、不改冻结文件
```

---

## 1. 产物清单

### 1.1 新建文件

| 文件 | 说明 |
|---|---|
| `06_v0.4_code/07_training/__init__.py` | 模块初始化 |
| `06_v0.4_code/07_training/split_dataset.py` | 数据切分脚本（支持 random/yaw_block 两种方法） |
| `06_v0.4_code/07_training/dataset.py` | PyTorch `OCSImageDataset` + `make_dataloaders` |
| `06_v0.4_code/07_training/train_entry.py` | 训练入口骨架（CNN/MLP/joint 三模式，不执行训练） |
| `v0.4_results/01_fullrun/postprocess/split_manifest.json` | 切分产物（train/val/test split manifest） |

### 1.2 修改文件（emoji/GBK 清理）

| 文件 | 修改内容 |
|---|---|
| `06_v0.4_code/05_postprocess/run_full_postprocess.py` | `⚠` → `[WARN]`（2 处） |
| `06_v0.4_code/10_validation/generate_depth_epsilon_calibration_report.py` | `✅`→`[PASS]`, `⚠️`→`[PARTIAL]`（1 处） |
| `06_v0.4_code/10_validation/transform_position_to_world_space.py` | `✓`→`[OK]`, `✗`→`[FAIL]`（5 处） |

修改原则：仅替换可能导致 GBK 编码失败的 Unicode 符号为 ASCII 安全标识，不改变逻辑。

---

## 2. 数据切分方案

### 2.1 方法：随机分层切分（random stratified by pitch）

- **种子**：42（固定可复现）
- **切分比例**：train 80% / val 10% / test 10%（按每个 pitch 层内分配）
- **分层依据**：37 个 pitch bin（-90°..+90°, step 5°），每个 bin 内有 72 个 yaw，确保各切分的 pitch 分布一致

### 2.2 切分结果

| 切分 | 样本数 | 占比 | yaw 覆盖 | pitch 覆盖 | non-clean |
|---|---|---|---|---|---|
| train | 2109 | 79.2% | 0..355 (72/72) | -90..+90 (37/37) | 0 |
| val | 259 | 9.7% | 0..355 (70/72) | -90..+90 (37/37) | 0 |
| test | 296 | 11.1% | 0..355 (71/72) | -90..+90 (37/37) | 0 |
| **合计** | **2664** | **100%** | — | — | 0 |

### 2.3 备选方案

`split_dataset.py` 同时实现了 `--method yaw_block`：按 yaw 连续块切分，train 使用前 80% yaw 角度，val 中间 10%，test 末尾 10%。该方案测试对**未见几何方向**的泛化能力，但初轮训练推荐 random 分层方案以保证各切分的 yaw 覆盖。

### 2.4 split manifest 结构

每条记录包含：
```json
{
  "record_id": "phase63_yaw170_pitch+020",
  "yaw_deg": 170.0,
  "pitch_deg": 20.0,
  "yaw_idx": 34,
  "pitch_idx": 22,
  "ocs_total": 0.02136,
  "ocs_jinshuzhuti": 0.01992,
  "ocs_taiyangnengban": 0.00084,
  "ocs_yinshenban": 0.00059,
  "png_path": "v0.4_results/01_fullrun/postprocess/...",
  "exr_linear_path": "v0.4_results/01_fullrun/postprocess/..."
}
```

---

## 3. Dataset 与 DataLoader

### 3.1 `OCSImageDataset`（`dataset.py`）

- **输入模式**：`image_only` / `ocs_only` / `joint`
- **图像**：单通道 256×256 float32 tensor [0,1]，从 BRDF PNG 加载
- **OCS**：4 维向量 `[ocs_total, ocs_jinshuzhuti, ocs_taiyangnengban, ocs_yinshenban]`
- **标签**：`yaw_bin` (0..71, 72 类) + `pitch_bin` (0..36, 37 类)，对应 5° 步长网格
- **便捷函数**：`make_dataloaders()` 一键创建 train/val/test DataLoader

### 3.2 Loader Smoke 结果

```text
train: 2109 samples, 66 batches @ batch_size=32
  image:    [32, 1, 256, 256] float32
  ocs:      [32, 4] float32
  yaw_bin:  [32], range=[0, 71]
  pitch_bin:[32], range=[0, 36]
  NaN: False, Inf: False
  Path check (first 10): OK

val:   259 samples, 9 batches — OK
test:  296 samples, 10 batches — OK
```

---

## 4. 训练入口骨架

### 4.1 模型架构（`train_entry.py`）

| 模式 | 编码器 | 参数量 | 融合维度 |
|---|---|---|---|
| `image_only` | 6 层 CNN (32→64→128→256→256→256) + FC | 3,865,613 | 256 |
| `ocs_only` | 3 层 MLP (4→128→128→128) | 47,725 | 128 |
| `joint` | CNN + MLP concat → FC | 3,913,229 | 384 |

**预测头**：yaw (72 类) + pitch (37 类) 分类。

### 4.2 Forward Smoke 结果

```text
image_only:  yaw_acc=0.0000 (随机基线~0.014), pitch_acc=0.0000 (~0.027)
ocs_only:    yaw_acc=0.0000, pitch_acc=0.0312
joint:       yaw_acc=0.0000, pitch_acc=0.0312
```

随机权重下精度符合预期（接近 1/72 和 1/37 随机基线）。三个模式前向传播均无报错。

### 4.3 训练红线（已内置检查）

- `--epochs` 必须为 0，否则脚本拒绝执行并退出
- 不保存模型权重
- 不写入 `04_Codex审阅/`

---

## 5. 数据定义总结

### 5.1 三类输入绑定方式

| 输入类型 | 数据来源 | manifest 绑定字段 |
|---|---|---|
| **image** | BRDF PNG（log1p 预处理，256×256） | `png_path` → PIL → float32[0,1] |
| **OCS** | OCS JSON manifest（4 维向量） | `ocs_total` + 3 per-part 值 |
| **joint** | 上述两者 concat | 同 image + OCS |

### 5.2 标签定义

- **yaw_bin**：`int(round(yaw_deg / 5.0))`，范围 0..71，共 72 类
- **pitch_bin**：`int(round((pitch_deg + 90.0) / 5.0))`，范围 0..36，共 37 类
- **fixed-roll 条件**：所有样本 roll=0，姿态自由度固定为 yaw × pitch 二维网格

### 5.3 当前未实现（留待后续训练准备阶段）

1. 回归标签（直接预测 yaw/pitch 角度值而非分类）
2. 数据增强（旋转、翻转、噪声）
3. 不平衡采样 / 加权损失
4. EXR 线性光强通道读取（当前仅用 PNG）
5. 训练日志、checkpoint、TensorBoard 集成

---

## 6. 执行红线确认

```text
[OK] 不训练 — 所有脚本 --epochs=0 / smoke-only，无训练循环执行
[OK] 不改论文正文
[OK] 不改冻结文件 13/14/24/25
[OK] 不启动 B1/GGX/三轴/路线二/三/四
[OK] 不写入 04_Codex审阅/ — 本报告写入 02_Claude输出/
```

---

## 7. 下一步建议（供 Codex 审阅后决定）

1. 正式放行训练前需要完成的准备：
   - 确定 train/val/test split 方法（random vs yaw_block vs 两者对比）
   - 确定损失函数（CE 分类 vs smooth L1 回归 vs 联合损失）
   - 确定评估指标（top-1 acc, MAE deg, 混淆矩阵，per-pitch 细分）
   - 确定超参数搜索空间和 budget
2. `1C-E20`：训练最小 smoke（1-3 epoch，小 batch），验证 loss 能正常下降
3. `1C-E21`：受控完整训练 + 评估报告
4. 可考虑在 split manifest 中同时打包两种切分方法（random primary + yaw_block alternative）

---

## 附录 A. 文件路径索引

```text
新建代码：
  06_v0.4_code/07_training/__init__.py
  06_v0.4_code/07_training/split_dataset.py
  06_v0.4_code/07_training/dataset.py
  06_v0.4_code/07_training/train_entry.py

切分产物：
  v0.4_results/01_fullrun/postprocess/split_manifest.json

修改文件（emoji 清理）：
  06_v0.4_code/05_postprocess/run_full_postprocess.py
  06_v0.4_code/10_validation/generate_depth_epsilon_calibration_report.py
  06_v0.4_code/10_validation/transform_position_to_world_space.py

本报告：
  04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/40_1C-E19_训练入口与数据切分准备_Claude执行报告.md
```

## 附录 B. 命令行复现

```powershell
# 1. 生成 split manifest
"C:\Users\97466\.conda\envs\ocs_sim\python.exe" 06_v0.4_code/07_training/split_dataset.py --seed 42 --method random

# 2. Loader smoke
"C:\Users\97466\.conda\envs\ocs_sim\python.exe" 06_v0.4_code/07_training/train_entry.py --smoke-only --batch-size 32

# 3. Forward smoke
"C:\Users\97466\.conda\envs\ocs_sim\python.exe" 06_v0.4_code/07_training/train_entry.py --forward-smoke --batch-size 32
```

# 下一轮任务草案：P1 seed-roll scan（next_task_draft_P1_seed_roll_scan）

最后更新：2026-07-01
性质：给下一轮 Claude 的 P1 执行任务草案（**草案，需 Codex 另行放行后才执行**）。
矩阵：`tables/p1_seed_roll_pre_registered_matrix.csv`（96 渲染单位）。
预期输出：`tables/p1_expected_outputs.csv`。

## 1. P1 目标

围绕少量种子点扫描 roll，验证 fixed-roll 结论（最亮点、可分性）在 roll 方向是否迁移。
这是三轴小项目的第一个 smoke，**不是全量三轴，不训练 roll-aware 模型**。

## 2. 限定范围（预注册）

- 种子：从 66 seed 选 12 个类别代表（bright×2, high-info×2, roll-sensitive×2,
  low-info/ocs-hard/disagreement/image-hard/dark/robust-easy 各 1）。
- roll 网格：{-60,-45,-30,-15,0,15,30,45,60}，roll=0 复用 `01_fullrun`，仅 8 个非零 roll 需渲染。
- 几何：仅 phase63（L1-G1）做 smoke。
- 渲染单位：12 × 8 = 96；估计 ~2 min、~25 MB（见 resources 估计）。

## 3. 只计算这些量（不训练）

- OCS magnitude vs roll（每种子）。
- 图像渲染可用性（非空 / 未饱和 flag）。
- local contrast vs roll。
- roll sensitivity：最亮点 / 可分点是否随 roll 迁移。

## 4. 执行方式（复用现有可参数化脚本）

- 渲染：复用 `06_v0.4_code/02_blender/render_mroll_probe.py` 的 roll 注入机制
  （已证明可注入非零 roll 并生成 `roll{+NNN}` label），限定到 12 种子点、phase63。
- 后处理：复用现有 postprocess，产出 `*_ocs.json`。
- 输出目录：新建 `v0.4_results/19_three_axis_p1_seed_roll_scan/`（P1 专用，不写 18 号包）。

## 5. smoke 通过判据

- 96 个非零 roll 渲染完成，OCS/图像非空。
- 每种子 OCS(roll) 与 contrast(roll) 曲线可画。
- 能初步回答：最亮/可分点在 roll 下是否迁移。
- 若 smoke 通过 → 交 Codex 另行放行正式 P1 / P2。

## 6. 红线

- 不扩大到全量三轴或多几何（P2 及以后另行放行）。
- 不训练 roll-aware 模型（C 类变更，需完整阶段门）。
- roll=0 不重渲。
- 不改姿态网格步长、OBS_GEOMETRIES、split、backbone、超参。
- 不把 P1 结果写成最优反演姿态或真实反演系统。

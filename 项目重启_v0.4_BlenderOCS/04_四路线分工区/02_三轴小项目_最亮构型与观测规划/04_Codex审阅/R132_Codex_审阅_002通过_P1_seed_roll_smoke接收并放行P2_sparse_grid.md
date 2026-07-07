# R132 Codex 审阅：002 通过，P1 seed-roll smoke 接收并放行 P2 sparse grid

最后更新：2026-07-01  
审阅端：Codex  
审阅对象：

```text
02_Claude输出/002_P1_seed_roll_scan_smoke_Claude执行报告.md
v0.4_results/19_three_axis_p1_seed_roll_scan/
```

## 1. 审阅结论

002 执行报告与 19 号包通过。P1 seed-roll smoke 达到 R131 强接收标准：

```text
96/96 非零 roll 渲染单位完成。
96/96 后处理完成。
roll=0 baseline 12/12 复用 01_fullrun，未重渲。
roll 曲线、roll sensitivity、brightness rank shift、glint/saturation flag 完成。
一致性检查 11/11 PASS。
红线自检 12/12 PASS。
gate matrix 0 FAIL。
```

Codex 裁定：**19 号包接收为三轴小项目当前主用 P1 smoke 成果；P1 smoke 链路跑通；放行下一步 P2 sparse 3-axis grid。**

本次通过不等于三轴小项目完成，不放行 P3 local refinement，不放行 roll-aware 训练，不启动 R128 新路线二或路线二/三/四扩展。

## 2. 完成度核验

Codex 抽查结果：

```text
generated_files_manifest.csv：439/439 exists=True
numeric_path_consistency_check.csv：11/11 PASS
redline_self_check.csv：12/12 PASS
p1_smoke_gate_matrix.csv：0 FAIL
render manifest：96 行，camera/sun 全 True
postprocess manifest：96 行，status COMPLETE
EXR 实际数：192
linear.exr 实际数：96
```

002 报告写入三轴小项目 `02_Claude输出/`，19 号包写入 `v0.4_results/19_three_axis_p1_seed_roll_scan/`。未写成果区、未改 `CLAUDE.md`、未训练、未启动 P2/P3/P4/R128。

## 3. 接收证据

### 3.1 P1 smoke 链路跑通

R131 要求的 12 seed × 8 非零 roll 在 phase63 / L1-G1 下全部完成。派生 wrapper `p1_render_seed_roll.py` 与 `p1_postprocess_seed_roll.py` 合规：复用旧 driver 的场景和 OCS 逻辑，只把姿态子集与输出目录定向到 19 号包，未改旧脚本或旧结果链。

### 3.2 最亮构型与信息构型分离

接收 smoke 级观察：

```text
bright-seed / robust-easy：roll 下 OCS 变化约 5-7%，rank shift <= 1，最亮构型较稳健；
但这些 seed 的 local contrast 排名靠后，且有 glint/saturation 风险。
```

这支持三轴小项目核心边界：

```text
最亮构型 != 高信息构型。
```

### 3.3 高 |pitch| 暗构型 roll 敏感

接收 smoke 级观察：

```text
high-info yaw240 系：roll_sensitivity_score 约 3.2-3.6；
low-info / ocs-hard yaw065 系：约 1.5-1.6；
roll-sensitive / dark yaw285 系：约 0.77-1.07；
亮度排名漂移最大到 7。
```

这说明高 |pitch|、yaw~240/285/065 邻域值得进入 P2 sparse grid 或局部加密候选。

### 3.4 information proxy 边界

接收 `local_contrast` 作为 P1 smoke 代理指标，但不把它升格为正式信息量结论。正式阶段应补 P-DB / margin / entropy / top-k stability 等更接近路线一 C 置信一致性主线的指标。R132 不放行 roll-aware 训练；若 P2 后需要模型指标，必须另行阶段门。

## 4. 裁决问题回答

Q1 002 P1 smoke 是否通过：通过，进入当前主用成果摘要。  
Q2 是否放行 P1 正式扩展或 P2 sparse grid：放行 P2 sparse 3-axis grid；不再单独做 P1 正式扩展，P1 已足够证明链路跑通。  
Q3 是否修正 seed 类别或采样计划：不返工 seed；P2 应优先覆盖高 |pitch|、yaw~240/285/065 与 bright/robust 对照。  
Q4 是否认可早期证据：认可为 smoke 级证据，不能写成三轴最终结论。  
Q5 information proxy 是否升级：P2 仍可先用 OCS/contrast/rank/geometry utility；P-DB/margin/entropy 升级列为 P2 后或单独阶段门。  
Q6 R128 是否继续挂起：继续挂起到三轴小项目完成后再回看。

## 5. 成果区升级

同意新增当前主用成果摘要：

```text
01_成果区/00_当前主用成果/01_P1_seed_roll_smoke_R132通过.md
```

同意新增小项目阶段性技术路线框架：

```text
01_成果区/00_当前主用成果/02_三轴小项目后续技术路线执行框架_R132通过.md
```

19 号包本体仍保留在：

```text
v0.4_results/19_three_axis_p1_seed_roll_scan/
```

## 6. 下一步

下一步放行：

```text
P2 sparse 3-axis grid
```

建议输出目录：

```text
v0.4_results/20_three_axis_p2_sparse_grid/
```

边界：

```text
1. 只做受控 sparse grid，不做 P3 local refinement。
2. 不训练 roll-aware 模型。
3. 优先覆盖 high |pitch|、yaw~240/285/065、bright/robust 对照和少量中性区域。
4. 继续保留 brightness != information、model-known simulated、非真实未知目标反演系统等红线。
```


# 71_1C-E38_PathB论文结构与缺口清单_Claude执行报告

执行端：Claude | 任务编号：1C-E38 | 日期：2026-06-26

## 0. 裁决

```text
1C-E38：COMPLETED。范围：论文结构骨架 + 缺口清单，不含正式正文段落。
```

## 1. Results 骨架

### 3.1 C1: OCS Feature Extraction & Pre-Registration
| 有 | 缺 |
|---|---|
| Table 1 — 13 configs overview (dim, claim_class, feature_keys) | 14→13 筛选的 exclusion log |
| C1 pre-registration integrity (constant check passed) | |

### 3.2 C2: OCS-Only Baseline Screening
| 有 | 缺 |
|---|---|
| Table 2 — 13×5 folds, all yaw_acc = 0.00% | |
| Table 3 — 按 claim_class 分组的 C2 summary | |
| Figure 2 — circular yaw-block holdout (72/72 aggregate) | |
| S2 per-fold table (65 rows) | |
| Null result verdict + within-3 chance-level 9.72% | |

### 3.3 Diagnostic Observations
| 有 | 缺 |
|---|---|
| Figure 3 — yaw CMAE vs within-3 scatter | 为何 visibility control configs within-3 偏高（仅描述，不做 causal claim） |
| Figure 4 — pitch_acc bar chart | |
| within-3 range 2.75%-15.57%, coarse localization pattern | |

### 3.4 Observability Boundary
| 有 | 缺 |
|---|---|
| C2 = controlled null baseline for OCS-only low-dim features | Image-only baseline（需 C3） |
| | Joint result + 三通道对比 + 通道归因（需 C3） |

## 2. Methods 骨架

### 2.1 Simulation & Features (C1)
| 有 | 缺 |
|---|---|
| phase63 fixed-roll Blender render 描述 | 每个 config 的归因边界（sub-type a vs b） |
| OCS feature extraction pipeline (Figure 1) | |
| 13 configs + claim class 定义 | |

### 2.2 Training Protocol (C2)
| 有 | 缺 |
|---|---|
| Fixed MLP 3-layer, 5-fold yaw-block holdout | 不选更强架构的 formal justification（fixed-protocol 原则） |
| Fixed protocol, no hyperparameter search | |
| Metrics: yaw_acc, CMAE, within-3, pitch_acc | |

### 2.3 Model Architecture (B0 baseline)
| 有 | 缺 |
|---|---|
| B0 Lambert = smoke test / 兜底 baseline | B1 改进冯模型公式-材料对应（待作者确认） |
| | GGX 对照 rationale（待 B1 确认后展开） |

## 3. Discussion claim 边界

**可讨论**：
```text
- C2 = 固定协议下的受控 null result
- Low-dim OCS-only features 未在 cross-yaw holdout 下泛化
- within-3 局部聚集不代表 exact-bin accuracy
- 该 null result 对后续对照实验有方法学 baseline 价值
- phase63 data + 当前特征 + MLP 协议下的可观测性边界
```

**不可讨论（缺证据）**：
```text
- OCS vs image 比较/互补性/通道归因（缺 C3）
- 该 null 在更强架构下是否成立（未做架构搜索）
- 对真实 GEO 目标的推断（无姿态真值）
```

**需 C3 后才可讨论**：
```text
- Image-only 能否跨 yaw 泛化 → C3 image-only
- Joint 是否有增益 → C3 joint
- OCS 是否提供 image 之外的正交信息 → 三通道对比
- fixed-roll 几何约束是否主因 → 多几何扩展
```

## 4. 投稿前 gap list

### Must-have（缺则不可投）
| Gap | 依赖 |
|---|---|
| Image-only baseline | C3 image-only |
| Joint OCS+image result | C3 joint |
| 三通道对比表与归因分析 | C3 全部完成 |
| Methods 中 image encoder + fusion 描述 | C3 协议锁定后 |

### Nice-to-have（缺则 Discussion 注明 limitation）
| Gap | 依赖 |
|---|---|
| B1 模型确认 → 替换 B0 | 作者确认 + Blender 实现 |
| 多几何扩展（非 fixed-roll） | 新渲染 |
| GGX 对照 | B1 完成后 |
| 高维 OCS 特征 | 后验特征工程（另立 exploratory） |
| GEO 真实光度定性对比 | 路线二 GEO 初探 |

## 5. 当前阶段门

```text
C1/C2 / Results材料包 / 图表SI / 论文结构缺口清单：CLOSED
C3 / 正文段落 / 三轴小项目 / 路线二三四：NOT RELEASED
```

## 6. 红线

```text
未启动 C3/训练/改代码/写正文；未放行其他路线；未外推 C2。
```

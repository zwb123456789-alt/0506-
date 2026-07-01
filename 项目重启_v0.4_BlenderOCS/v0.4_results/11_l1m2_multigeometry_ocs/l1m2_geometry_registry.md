# L1(M2) 几何注册表

生成时间：2026-06-30T20:07:28  
来源：`config_v0_4.py :: OBS_GEOMETRIES`

## 编号冲突处理（R114 §3）

> 两套编号严格区分：'code_index'/'code_comment_id'(G0~G4) 来自 config 代码层；'L1-G1/L1-G3/L1-G5' 是实验组名(R114 §3)。二者不可混用。config 注释 G0~G4 ≠ 实验组 G1/G3/G5。

## 代码层几何（OBS_GEOMETRIES）

| code_index | 注释ID | label | geom_id | 相位角° | 已渲染 |
|---:|:--|:--|:--|---:|:--|
| 0 | G0 | phase63_backscatter | phase63 | 63.112 | ✅ |
| 1 | G1 | phase24_near_backscatter | phase24 | 23.603 | ❌缺口 |
| 2 | G2 | phase120_forward_scatter | phase120 | 120.001 | ❌缺口 |
| 3 | G3 | phase90_side | phase90 | 90.0 | ❌缺口 |
| 4 | G4 | phase45_overhead | phase45 | 45.0 | ❌缺口 |

## 实验组（嵌套 G1⊂G3⊂G5）

嵌套校验：✅ 通过

### L1-G1（1 几何）

- 特征向量布局：`['total_flux_phase63']`
- 按相位角排序：['phase63_backscatter']

### L1-G3（3 几何）

- 特征向量布局：`['total_flux_phase24', 'total_flux_phase63', 'total_flux_phase120']`
- 按相位角排序：['phase24_near_backscatter', 'phase63_backscatter', 'phase120_forward_scatter']

### L1-G5（5 几何）

- 特征向量布局：`['total_flux_phase24', 'total_flux_phase45', 'total_flux_phase63', 'total_flux_phase90', 'total_flux_phase120']`
- 按相位角排序：['phase24_near_backscatter', 'phase45_overhead', 'phase63_backscatter', 'phase90_side', 'phase120_forward_scatter']

## 冲突清单

无。代码几何与实验预注册一致。

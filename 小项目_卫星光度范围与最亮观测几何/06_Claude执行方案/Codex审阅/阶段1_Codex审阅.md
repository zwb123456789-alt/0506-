# 阶段1 Codex审阅：OCS定义与星等公式审计

审阅时间：2026-06-05

审阅对象：

```text
06_Claude执行方案/Claude输出/阶段1_OCS定义与星等公式审计.md
```

交叉核验文件：

```text
ocs_project/01_code/ocs_core.py
ocs_project/01_code/materials.py
ocs_project/01_code/config.py
ocs_project/07_brdf/brdf_models.py
结果/模块A_重构/multi_geom_ggx_yaw73_pitch37/run_20260527_195122/phase63_backscatter/config_used.json
```

## 总体结论

阶段1输出整体方向正确：识别了代码中的核心积分形式

```text
OCS = Σ A · f_r · cos_i · cos_r
```

并正确指出相对星等差

```text
Delta m = -2.5 log10(OCS_2 / OCS_1)
```

是当前最稳妥的口径。

但阶段1中有几处表述偏确定，需要压回“条件成立/代码定义下/待验证”：

1. GGX 能量守恒不能直接写成已完全确认；
2. `OCS/R^2` 的绝对星等公式可作为代码定义下的候选式，但不能过早作为最终物理公式；
3. `4π` 不适用的结论应限定在“本代码当前定义的 directional OCS”内，不能泛化到所有 OCS 文献定义；
4. 绝对星等量级示例建议移到附录或标成“非结论性 sanity check”；
5. `Delta m` 若跨 STK 时间序列比较，需要加入距离变化项。

## 主要问题

### 1. GGX “能量守恒”表述过强

Claude 原文写：

```text
GGX BRDF 满足能量守恒
```

交叉核验 `brdf_models.py` 后，当前 GGX 实现为：

```python
f_diffuse = (1.0 - metallic) * (base_color / PI)
f_specular = (D * G * F) / (4 * NoL * NoV)
f_r = f_diffuse + f_specular
```

问题：

- 对电介质，当前 diffuse 项没有乘 `(1 - F)` 或更严格的能量分配项；
- 对当前 `taiyangnengban base_color=0.15`、`yinshenban base_color=0.08` 这类低反射材料，超能量风险较低；
- 对 `jinshuzhuti metallic=1.0`，diffuse 为 0，金属项更合理；
- 但不能由此泛称“GGX实现已严格能量守恒”。

建议改为：

```text
当前 GGX 实现采用标准 Cook-Torrance 镜面项和 Lambert 漫反射项，具有明确物理量纲；
在当前 nominal 低反射非金属参数下可作为物理近似使用。
但其漫反射-镜面能量分配未做严格半球积分审计，因此不要写成已严格能量守恒。
```

### 2. OCS 的物理单位可作为代码定义下的 m^2，但仍需限定

Claude 对 `ocs_core.py` 的积分形式判断基本正确：

```python
areas * unit_scale^2 * brdf * cos_i * cos_r
```

在 BRDF 单位为 `sr^-1`、方向为远场单位向量、STL尺度正确时，该量可解释为 directional optical cross-section-like area。

但建议把结论从：

```text
OCS 输出具有 m²量纲的物理意义
```

改成：

```text
按本代码定义，OCS具有面积量纲，可作为方向性等效光学散射截面使用；
其绝对物理可信度仍依赖 STL比例尺、BRDF参数、mesh精度和遮挡语义。
```

原因：

- 当前 `config_used.json` 显示 `accuracy_level="fast"`，这通常意味着并非 full mesh 论文级精度；
- 绝对 OCS 对 mesh抽稀、面法向、遮挡射线语义敏感；
- 材料参数是 nominal，不是实测标定。

### 3. `4π` 不适用的结论应更谨慎

Claude 原文写：

```text
OCS / (4πR²) 不适用于本项目
```

这个方向基本可以接受，但建议增加限定：

```text
对于本代码中直接由 BRDF 面元积分得到的 directional OCS，不应再额外除以 4π；
但不同文献可能把 OCS/phase function/散射截面定义为总散射量或各向同性等效量，届时可能出现 4π 或相位函数归一化。因此后续和文献公式对接时必须核对定义。
```

这样既保住当前代码公式，也避免将本项目定义外推到所有光度学定义。

### 4. 绝对星等示例不宜放在主结论段

Claude 给出：

```text
phase63 最大 OCS=14.82, GEO R=3.6e7 m -> m≈8.1 mag
中位 OCS=0.00981 -> m≈16.1 mag
```

问题：

- 用户当前目标是规划与审计，不是给绝对星等结果；
- OCS绝对公式仍需阶段3/4确认波段、太阳星等、距离、STL尺度、材料参数；
- 这个数值容易被后续误复制成结果。

建议：

- 保留为“sanity check/量级演示”，但不要放入阶段1核心结论；
- 文件中应加粗标注“不得引用为结果”；
- 阶段6前不把 `8.1 mag`、`16.1 mag` 写入结论证据表。

### 5. `Delta m` 的适用条件需要补充距离项

Claude 写：

```text
Delta m 不依赖距离
```

这只在比较同一距离、同一波段、同一标定口径下的姿态或部件时成立。若后续 STK 给的是不同时间、不同距离，则观测星等差应为：

```text
Delta m_obs = -2.5 log10(OCS_2 / OCS_1) + 5 log10(R_2 / R_1)
```

建议阶段1补一句：

```text
当前 phase63 姿态扫描使用同一抽象观测距离，因此 Delta m 可只由 OCS 比值给出；若比较高轨时间序列，必须加入 range_km 的变化。
```

### 6. `m_sun=-26.74` 需要来源和波段锁定

Claude 写 V波段常用 `m_sun≈-26.74`。这个数值常见，但阶段1里应标成：

```text
[待阶段3/4引用确认]
```

原因：

- 不同波段太阳星等不同；
- 文献调研中的卫星光度可能是 V、R、clear、宽带或仪器星等；
- 绝对星等换算必须与调研口径一致。

## 可保留内容

- `ocs_core.py` 积分式识别正确；
- `UNIT_SCALE=1e-3` 和面积 `s²` 的分析合理；
- LegacyPhong 缺少归一化的提醒有价值；
- 相对星等差作为当前可靠口径的判断正确；
- 待确认项 C1-C5 基本完整；
- 阶段5建议“最亮姿态/部件贡献可直接使用 OCS排序和 Delta m”是对的。

## 建议给 Claude 的修改指令

请 Claude 对阶段1文档小修，不需要重写全文：

1. 将“GGX BRDF 满足能量守恒”改为“当前 GGX 实现具有物理形式，但严格能量守恒未做半球积分审计；当前 nominal 参数下可作为合理近似”。
2. 将“OCS 输出具有 m²量纲的物理意义”改为“按本代码定义具有面积量纲，可作为方向性 OCS-like 量；绝对可信度依赖 STL尺度、BRDF参数、mesh精度和遮挡语义”。
3. 将 `OCS/(4πR²)` “不适用”改为“对本代码 directional OCS 不应额外除以 4π；但与外部文献对接时需核查其 OCS/相位函数定义”。
4. 给 `Delta m` 增加距离变化说明：

```text
Delta m_obs = -2.5 log10(OCS_2/OCS_1) + 5 log10(R_2/R_1)
```

5. 将 `8.1 mag`、`16.1 mag` 示例移为“非结论性 sanity check”，并标注不得作为结果引用。
6. 将 `m_sun=-26.74` 标为 V波段候选值，待阶段3/4引用和波段锁定。

## 审阅结论

阶段1可以进入下一步，但建议先按上述六点小修。修完后，阶段2可以继续做 STK/高轨场景需求设计；阶段3调研时必须特别锁定波段和星等定义。

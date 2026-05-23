

可保存为：

```text
BRDF_bottleneck_and_AB_physics_summary.md
```

```md
# BRDF Step 5 瓶颈与模块 A/B 物理定位总结

> 本文总结当前 BRDF 精确化阶段的核心判断、A/B 模块物理可信度定位，以及下一步最小闭合诊断方案。

---

## 1. 当前总体判断

当前项目不是整体卡死，而是进入了一个非常具体的数值闭合瓶颈：

```text
模块 A：mesh face-level OCS 积分
vs
模块 B：image pixel-level BRDF 后处理积分
```

在真实复杂 STL 上尚未数值闭合。

目前最可疑的根因不是：

- OSL；
- Backfacing；
- 分辨率；
- Combined pass；
- 色彩管理；
- 法线坐标系。

而是：

```text
A 端 fast 简化网格 + 面元中心采样
vs
B 端完整 STL + 像素级采样
```

对于 Phong 指数 `n=80` 的窄镜面峰，法线差异 1°~2° 就可能造成数倍 BRDF 差异。

---

## 2. 当前最关键的问题

最坏姿态：

```text
yaw = 150°
pitch = -80°
```

当前观测到：

```text
B_image ≈ 0.171
A_no_occ ≈ 0.077
A_with_occ ≈ 0.016
```

并且在该姿态下，`jinshuzhuti` 金属主体贡献占主导，B 端出现明显镜面峰：

```text
f_r ≈ 0.575
NoH ≈ 0.998
```

这说明差异很可能不是遮挡导致的，而是：

```text
A 端没有采到或保留住完整 STL 上的高光法线分布。
```

---

## 3. 模块 A 和模块 B 谁更接近真实物理？

简短结论：

```text
当前 B_exact / B_full 方向更接近高保真物理；
当前 A_fast 不是物理真值。
```

但也要注意：

```text
B 端也不是现实世界真值。
```

---

## 4. 为什么 B 端更接近高保真物理？

### 4.1 几何精度更高

模块 B 当前使用完整 STL：

```text
约 150k faces
```

而模块 A 当前 fast 模式只保留约 20% 面元：

```text
约 30k faces
```

网格简化会改变局部法线分布。对于高光 BRDF：

```text
specular ∝ (NoH)^80
```

小角度法线误差会被指数项极大放大。

---

### 4.2 像素级采样更容易捕捉窄镜面峰

模块 A 当前做法：

```text
每个三角面一个 BRDF 值
```

模块 B 后处理做法：

```text
每个可见像素一个 BRDF 值
```

对于窄高光区域，B 端更容易在图像空间捕捉到峰值，而 A 端大面元中心采样可能漏掉峰值。

---

### 4.3 可见性与投影更接近真实相机成像

B 端通过 Blender 渲染得到：

- 可见像素；
- 世界法线；
- 深度；
- 材料 ID；
- 投影面积。

这更接近真实图像形成过程。

---

## 5. 但 B 端不能直接等于真实世界

B 端当前仍缺少：

1. 真实材料 BRDF 参数；
2. 传感器响应；
3. 曝光模型；
4. 噪声；
5. PSF；
6. 杂散光；
7. 大气影响；
8. 地球反照；
9. 真实太阳光谱与相机光谱响应；
10. 绝对辐射定标。

因此 B 端应被理解为：

```text
比 A_fast 更高保真的仿真器
```

而不是：

```text
真实世界完整复现器
```

---

## 6. 重要原则：不要让 B 去逼近 A_fast

如果为了数值一致性，强行让 B 去逼近当前 A_fast，那么最终确实可能离真实图像更远。

原因是：

```text
A_fast 可能低估了真实高光；
真实图像中可能存在强高光；
如果仿真模型中没有高光，姿态反演会把真实高光解释错。
```

因此不能把当前 A_fast 当作物理标准。

正确理解应该是：

```text
A_fast：快速预览 / 粗略扫描 / 工程加速
A_full：mesh-level 高精度 OCS 实现
B_exact：image-level 高精度图像实现
最终参考：A_full 与 B_exact 在同一显式模型下收敛后的结果
```

---

## 7. 当前真正目标

当前目标不是：

```text
让 B 逼近 A_fast
```

而是：

```text
先让 A/B 在同一个明确物理模型下闭合；
再把低精度的一端升级到高精度模型。
```

最终应该是：

```text
A_full / A_adaptive 去接近 B_exact / full 几何结果
```

而不是：

```text
B_exact 去降级匹配 A_fast。
```

---

## 8. 立即执行的最小诊断实验

下一步只做单姿态，不要全量重跑。

目标姿态：

```text
yaw = 150°
pitch = -80°
```

需要比较：

```text
A_fast_no_occ
A_full_no_occ
A_full_detector_only
A_full_with_occ
B_image
```

其中最重要的比较是：

```text
B_image vs A_full_detector_only
```

如果暂时没有 `detector_only`，至少先比较：

```text
B_image vs A_full_no_occ
```

注意：

```text
当前 B 后处理主要是相机可见像素 + BRDF + NoL；
它更接近 detector-visible 积分，
不能直接拿来和 A_with_occ 强行比较。
```

---

## 9. 分支判断

### 情况 A：A_full 接近 B

例如：

```text
A_fast_no_occ ≈ 0.077
A_full_no_occ / A_full_detector_only ≈ 0.15 ~ 0.18
B_image ≈ 0.171
```

则根因基本确认：

```text
A_fast 网格简化导致镜面峰丢失。
```

后续策略：

1. 论文定量验证不要用 fast；
2. A/B 使用同一精度网格；
3. 或者两端都用 full STL；
4. 或者 A 保存简化后 STL，B 也导入同一份简化 STL；
5. fast 仅作为预览模式，不作为物理真值。

---

### 情况 B：A_full 仍远低于 B

例如：

```text
A_full_no_occ ≈ 0.077
B_image ≈ 0.171
```

则说明问题不只是 fast 网格简化。

这时继续做两个诊断：

```text
diffuse-only 验证
NoH 分布验证
```

---

## 10. diffuse-only 验证

临时关闭镜面项：

```text
rho_s = 0
```

只保留：

```text
f_r = rho_d / pi
```

然后比较：

```text
A_full_detector_only_diffuse
vs
B_image_diffuse
```

---

### 10.1 如果 diffuse-only 都对不上

说明问题不在镜面 BRDF，而在基础几何/投影/单位/面积/可见性。

重点排查：

1. `pixel_area` 是否正确；
2. `ortho_scale` 是否正确；
3. mm → m 是否重复或遗漏；
4. IndexOB 材料 ID 是否错；
5. B 端法线是否确实是世界坐标；
6. 相机方向是否和 A 端探测器方向完全一致；
7. 是否只统计了前景像素；
8. A 端是否比较的是 detector-visible，而不是所有 NoV>0 面元。

---

### 10.2 如果 diffuse-only 能对上，但镜面对不上

说明根因大概率是：

```text
高光窄峰积分采样问题。
```

也就是：

```text
A 端 face-center 积分没有采到镜面峰；
B 端 pixel-level 积分采到了完整 STL 上的高光区域。
```

后续可选方案：

1. A 端用 full STL；
2. A 端对高光面元做 sub-face 采样；
3. A 端做自适应积分；
4. B 端临时改用 A 端同一份简化网格做闭合验证；
5. 或者直接以 B geometry pass + Python exact BRDF 作为统一前向模型。

---

## 11. NoH 分布诊断

对同一姿态：

```text
yaw = 150°
pitch = -80°
```

分别统计：

```text
fast mesh
full mesh
B image pixels
```

的：

```text
NoH = dot(N, H)
```

重点统计：

```text
NoH > 0.99
NoH > 0.995
NoH > 0.998
```

因为对于 `n=80`：

```text
NoH = 1.000 → spec = 1.000
NoH = 0.995 → 0.995^80 ≈ 0.67
NoH = 0.990 → 0.990^80 ≈ 0.45
NoH = 0.980 → 0.980^80 ≈ 0.20
NoH = 0.950 → 0.950^80 ≈ 0.017
```

如果观察到：

```text
full STL / B pixels 有大量 NoH≈0.998；
fast mesh 没有。
```

则可以确认：

```text
根因是几何精度/采样不足，而不是 BRDF 公式错误。
```

---

## 12. 推荐执行顺序

当前不要继续发散排查，严格按下面顺序：

```text
1. 单帧 yaw=150, pitch=-80，A 端切 full 精度跑一次
2. 输出 per-part 贡献，重点看 jinshuzhuti
3. 比较 B_image vs A_full_no_occ / A_full_detector_only
4. 做 diffuse-only 验证
5. 做 NoH 分布统计
6. 如果确认 fast 简化是根因，则统一两端 mesh
7. 再跑 9 帧小集合
8. 再跑 703 帧 LegacyPhong 验证
9. LegacyPhong 闭合后再进入 GGX
10. GGX 验证通过后再考虑 CNN / 联合反演 / 消融实验
```

---

## 13. 当前不要做的事情

暂时不要：

1. 不要继续查 Backfacing；
2. 不要再折腾 OSL；
3. 不要直接进入 GGX；
4. 不要上 CNN；
5. 不要重跑全量 703 帧；
6. 不要拿 B 当前结果直接和 A_with_occ 强行比较；
7. 不要把 Principled BSDF 当作定量模型；
8. 不要为了匹配 A_fast 而降低 B 端物理精度。

---

## 14. 最终论文期推荐定位

论文主实验应使用：

```text
完整或高精度 STL
+ 显式 BRDF
+ 统一材料参数
+ 统一太阳/相机方向
+ 统一遮挡语义
+ 充分采样积分
```

推荐角色划分：

| 模块 | 定位 |
|---|---|
| A_fast | 快速预览、粗筛、调试，不作为物理真值 |
| A_full | mesh-level 高精度 OCS 计算 |
| A_adaptive | 针对窄高光的自适应积分增强版本 |
| B_exact | image-level 高精度图像/OCS-like 积分 |
| Principled Preview | 可视化预览，不用于论文定量分析 |

最终验证目标：

```text
A_full / A_adaptive 与 B_exact 在同一显式 BRDF 下数值收敛。
```

---

## 15. 对真实图像姿态反演的影响

如果用当前 A_fast 作为训练或匹配真值，可能出现：

```text
真实图像有强高光；
A_fast 模型没有或低估高光；
反演算法把高光解释错；
姿态估计误差增大。
```

因此，为了未来真实图像反演，应该尽量保留高保真几何和高光，而不是让 B 去匹配低精度 A_fast。

但是，即使使用 B/full，也不等于已经解决 sim-to-real gap。

后续仍需：

1. 材料参数敏感性分析；
2. 多组 BRDF 参数扰动；
3. 传感器噪声建模；
4. 曝光和响应曲线建模；
5. 如有真实数据，则做材料/辐射反标定。

---

## 16. 一句话总结

当前不应该让 B 去逼近 A_fast。

正确路线是：

```text
用单姿态最小实验确认 A/B 差异来源；
如果 A_fast 错，就升级 A 到 full/adaptive；
最终让 A_full 与 B_exact 共同逼近同一个高保真显式物理模型。
```

更简短地说：

```text
A_fast 是工程近似，不是物理真值；
B_exact/full 更接近高保真仿真方向；
最终目标是 A_full 与 B_exact 收敛，而不是 B 降级匹配 A_fast。
```
```
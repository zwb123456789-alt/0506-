# Step 1 Claude 返修版复审记录

审阅日期：2026-06-01  
审阅对象：

```text
D:\我的文件\研究生学术\光学项目\0506新\论文改进\论文写作\Claude交互\claude writing\01_Step1_返修版_标题摘要贡献点.md
```

## 1. 复审结论

Claude Step 1 返修版通过，可以进入 Claude Step 2：Introduction 指导与初稿。

本次复审仅针对 Claude 这一边，不与 GPT 比较优劣。最终优劣判断保留到两边完整初稿完成后。

## 2. 返修点完成情况

| 返修要求 | 完成情况 | 说明 |
|---|---|---|
| 降调 “realistic degradation” | 已完成 | 改成 `controlled image degradation tests` 和 `simple image degradation tests motivated by realistic observation artifacts` |
| 摘要骨架去掉 `Hit@5 = 99.7%` | 已完成 | Sentence 4 保留 worst-case 9.9° -> 6.6°，更适合摘要骨架 |
| brightness ×0.5 = 3.45° 不作为主证据 | 已完成 | 移到 candidate secondary evidence |
| 明确 r=0.003 来源 | 已完成 | 标注为 TinyCNN + OCS MLP pair，不默认推广到 ResNet pair |
| OCS robustness 限定 simulation | 已完成 | 写明 OCS 不依赖 image inputs；真实 OCS 会受 calibration/sensor noise 影响 |
| 单几何/多几何 OCS 数值放到 Results/Ablation | 基本完成 | Claim map 中写了 detailed values for Results/Ablation, not Abstract |

## 3. 仍需注意的小问题

1. **“degraded observation conditions” 仍偶尔偏宽**  
   后续 Introduction 中应优先写 `controlled degradation tests` 或 `observation-quality variations`，不要写成完整 field degradation model。

2. **Recommended title 偏长**  
   主标题可用，但若投 Acta Astronautica / ASR，后续可考虑压缩：

   ```text
   BRDF-Driven OCS and Photometric Image Simulation for Space Object Attitude Inversion
   ```

3. **Contribution 1 的证据较多**  
   Introduction 中不要堆 `13,505 attitude-OCS pairs`、`2,701 images` 等所有数字；这些更适合 Methods/Results。

4. **Claim 2 出现 `single-geom: 21.68°`**  
   该值与早期总览中的 `single-geom mean=79°` 属不同设置/特征定义。后续 Results 写作必须明确实验设置，避免混用。

## 4. 是否进入 Claude Step 2

可以进入。

Claude Step 2 应重点要求：

- 写 Introduction，不写完整 Related Work。
- 使用漏斗结构。
- 输出保守审稿安全版和平衡投稿版两个版本。
- 引用用 `[CITATION: ...]` 占位，不发明文献。
- 不把 Results 数字堆太多。
- 不把 limitation 写得像自毁，只在末段边界控制。


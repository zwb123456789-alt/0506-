# R126 增强项总验收综合摘要

最后更新：2026-07-01  

本文件把 multi-seed / P-INT-hard+degraded-severe / M-roll full-2664 / conformal alpha 四类闭口后增强实验统一收口，供 Codex R127 审阅。

## 1. 总验收矩阵

| 增强项 | 结论 | 证据 |
|:--|:--|:--|
| multi-seed sanity | 通过 | 3/3 seed G5优于G1；full单调 3/3 |
| P-INT-hard subset | 通过 | clean 六子集分区重算完成；image 天花板下 joint≈image |
| degraded-severe | 通过 | 9/9 run；joint 稳定增量=False |
| joint complementarity | 不支持 | clean 与 severe 下 image_only 均近饱和，joint 增量≤+0.0034 |
| M-roll full-2664 | 小roll稳健/大roll敏感 | G1 image hit@30 roll+15=0.9339, roll+30=0.5537（±15稳健，±30敏感） |
| conformal alpha | 通过(SI增强) | α=0.05/0.10/0.20 三档 coverage/set_size；set_size 随α增大收窄、随几何收紧 |
| 对路线一C论文claim影响 | 增强不变 | OCS 多几何单调增益经 multi-seed 稳健；joint 天花板/P-EXT 边界不变 |
| 对三轴小项目启动影响 | 四类增强清账完毕 | B/C/D/E 全部完成并有可审计表图；交 R127 裁决是否放行三轴 |

## 2. 四类增强项一句话结论

```text
A. multi-seed sanity：通过。3/3 seed(42/7/123) 保持 G1->G3->G5 完整单调增益，
   seed42 复现 R125（G5 cMAE 22.77, hit@30 0.811），主结论对训练随机种子不敏感。
B. P-INT-hard subset：clean 六子集分区显示 image 天花板普遍存在，joint≈image。
C. degraded-severe：9/9 run 完成。即便 blur2.0/downsample x4/flux12% 的强退化，
   image_only 仍近饱和(hit@30≈0.997-1.0)，joint 增量≤+0.0034 → joint 强互补性仍不支持。
D. M-roll full-2664：4 roll×2664 全渲染评估完成。±15° hit@30 稳健(0.83-0.97)，
   ±30° 明显下降(0.53-0.67) → fixed-roll 对小 roll 稳健、对大 roll 敏感。
E. conformal alpha：α=0.05/0.10/0.20 三档完成，set_size 随 α 增大收窄、随几何 G1->G5 收紧。
```

## 3. 对 R125 闭口结论的影响

```text
- 增强：OCS 多几何单调增益获 multi-seed 稳健性支持；fixed-roll 边界获 full-2664 roll 敏感性刻画。
- 不变：joint 天花板/强互补性未证明、P-EXT 坍缩、image_only conformal 欠覆盖等边界维持。
- 无需修正 R125 闭口裁决；四类增强项均非闭口 blocker，现已清账完毕。
```

## 4. 数字一致性：11/11 PASS，红线自检 12/12 PASS。


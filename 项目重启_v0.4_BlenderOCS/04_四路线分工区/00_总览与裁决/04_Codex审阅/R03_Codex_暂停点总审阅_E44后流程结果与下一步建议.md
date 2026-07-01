# R03 Codex 暂停点总审阅：E44 后流程、现有结果与下一步建议

最后更新：2026-06-27  
审阅端：Codex  
性质：暂停点阶段性总审阅，不放行新训练、论文正文、三轴小项目、路线二/三/四扩展。

## 0. 总裁决

```text
当前流程总体健康，阶段门控制有效，结果虽然是负结果，但不是项目失败。
E44/R78 后，路线一 C 已形成一条可审计的受控负结果证据链：
C2 enhanced OCS-only、C3 image_only、C3 joint 在 phase63 fixed-roll + circular yaw-block + 固定协议下，
cross-yaw exact-bin yaw accuracy 均为 0.00%。
```

该结果可以支撑论文中的“当前固定特征/固定早期融合协议不能跨 yaw-block 泛化”与“cross-yaw 可观测性/泛化边界”叙事；不能支撑“OCS/图像物理上无姿态信息”“融合无价值”或“真实 GEO / 三轴 / 暗室也会失败”的外推。

## 1. 实际进度校准

`CLAUDE.md` 仍停留在 E41 后的下一步状态，但成果区与 Codex 审阅已推进到：

```text
R75：E41 通过并放行 E42
R76：E42 通过，C3 正式 5-fold 负结果稳定
R77：E43 通过，C2/C3 三通道负结果证据包进入成果区
R78：E44 通过，C2/C3 Results 非正文总材料包进入成果区
```

当前稳定成果区入口为：

```text
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/01_成果区/
  08_C1C2_OCS-only证据包与claim边界_R62通过.md
  09_C1C2_OCS-only_Results非正文材料包_E35_R65通过.md
  10_C1C2_OCS-only图表与SI资产_E36_R69通过.md
  11_C2C3三通道负结果证据包_E43_R77通过.md
  12_C2C3_Results非正文总材料包_E44_R78通过.md
```

建议后续先由作者确认后同步 `CLAUDE.md`，否则新对话会误以为下一步仍是 E41/E42，而不是 R78 后的作者决策点。

## 2. 现有结果质量判断

强项：

- 证据链可审计：C2 13 configs x 5 folds = 65 runs；C3 image_only/joint 各 5 folds；split strict overlap 成立。
- 负结果不是单点偶然：C2、C3 image、C3 joint 三类固定协议均返回 exact-bin yaw 0.00%。
- 结果边界收得比较干净：C2 enhanced OCS 与 C3 raw 4-dim OCS 已明确区分。
- 结果解释有空间：C3 random test yaw_acc 约 50-70%，说明模型不是完全学不会 yaw，而是在 cross-yaw holdout / 分布外泛化上失败。

弱项与风险：

- 当前证据更强地支持“固定协议泛化失败”，还不足以直接完成 24 号三问中的完整互补性与置信一致性主线。
- 图表资产仍不完整：Figure 1/3/4/5、S3/S4/S5 尚未全部生成或提取。
- Figure 5 全 0 yaw_acc 图信息量较低，若作为正文主图会显得单薄。
- `CLAUDE.md` 状态滞后，是流程风险。
- 如果此时启动后验架构/超参补救，容易把干净的预注册负结果污染成“追结果”。

## 3. 是否达到预期

若原预期是“joint 明显优于 image_only / OCS 帮助姿态反演”，则当前结果没有达到。

若按 24 号主线的更稳口径，即研究 model-known 条件下 OCS/image 的可观测性、互补性和置信边界，则当前结果是有价值的中期成果：它说明在当前 phase63 fixed-roll 数据、circular yaw-block split 和固定 C2/C3 协议下，简单低维 OCS、图像 CNN 与 early-fusion joint 都不能完成跨 yaw exact-bin 泛化。这个负结果能帮助论文诚实定位“哪里不可知、哪里不该信任”。

但它还不是完整闭环。现在缺的不是继续盲目训练，而是把失败模式转化成可解释证据：混淆结构、yaw_cmae/within-3 分布、训练/验证分离、random vs yaw-block 对照、以及和 C1/C2 observability 资产之间的关系。

## 4. 下一步建议

推荐顺序：

```text
Step A：作者先确认 R78 三项版式/资产决策。
Step B：同步 CLAUDE.md 到 E44/R78 后真实状态。
Step C：放行一个窄 E45，只做 S3/S4/S5 提取与图表资产补齐，不训练、不改代码。
Step D：再放行 Results prose 草稿，但只写 Results，不写 Abstract/Intro/Discussion。
Step E：写一份“负结果如何服务 24 号三问”的解释桥接文件，再决定是否进入三轴小项目。
```

R78 三项作者决策建议：

```text
1. Figure 5：降级为 supplementary 或紧凑嵌入，不作正文主图。
2. S3/S4：建议现在提取，避免写作阶段再补数据导致口径漂移。
3. 编号体系：建议先按 C2/C3 分组编号，正式投稿前再统一重排。
```

## 5. 暂不建议做的事

```text
暂不启动后验架构/超参/特征补救。
暂不运行 raw 4-dim OCS-only 或 --mode all。
暂不启动正式论文全文改写。
暂不启动三轴小项目、路线二、路线三或路线四。
暂不把 C2/C3 负结果扩展成对 OCS 物理价值的否定。
```

## 6. 给作者的判断

当前最重要的不是“赶紧补一个正结果”，而是先把这条负结果证据链包装成可信的科学发现：在严格跨 yaw-block 设定下，当前简单通道和早期融合并不可靠；这恰好支持 v0.4 从“姿态反演成功率论文”转向“可观测性、泛化边界与置信一致性论文”的必要性。

下一阶段应以“解释失败模式、补齐资产、稳定写作入口”为主，而不是立刻扩大战场。

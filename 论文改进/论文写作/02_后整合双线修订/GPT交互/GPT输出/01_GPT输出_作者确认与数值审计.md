# GPT 输出：作者确认与数值审计

> 日期：2026-06-01  
> 对象：最终整合版 v0.1  
> 输出性质：交给 Codex 审阅整合的审计清单；不直接修改主稿。  
> 主要依据：`最终整合版_v0.1_基于GPT吸收Claude.md`、`20260529_论文写作完整规划.md`、`论文项目总览 copy.md`、`20260529_补充实验进度.md`。

## 总体结论

v0.1 的主线边界总体稳健：clean rendered images 被定位为 upper-bound，`all_raw` 被定位为 semi-oracle，`r = 0.003` 被限定为 TinyCNN/OCS 诊断，未宣称真实望远镜验证或 fusion universal superiority。当前最大投稿风险不是叙事跑偏，而是未确认方法细节、表格占位、引用占位和补充实验数值是否进入正文的问题。

最优先处理项为：Euler/坐标约定、target encoding、angular error formula、0% OCS-noise 表格、Table 1 文献核验、主结果数值回查、材料参数来源、模型训练细节和哪些 sensitivity/ablation 数值可进入正文。

## A. 作者确认项总表

| ID | 位置 | 确认问题 | 为什么重要 | 风险等级 | 作者需要提供什么 | 建议处理 |
|---|---|---|---|---|---|---|
| A001 | Method 3.2 | Euler order / rotation matrix convention | 姿态定义是全文方法可复现核心；若写错会影响所有 yaw-pitch 结果解释 | High | 明确 yaw/pitch/roll 轴、内旋/外旋、矩阵顺序；项目总览出现 `R = Rz @ Ry @ Rx`、Z-Y-X 内旋，需作者最终确认 | 补证后写入 Method；未确认前保留占位 |
| A002 | Method 3.8 | exact target encoding | 影响模型输出、loss、周期角处理和复现实验 | High | 是否为 `[sin(yaw), cos(yaw), sin(pitch), cos(pitch)]`；是否所有 MLP/CNN/fusion 一致 | 补证；建议写入模型小节或补充材料 |
| A003 | Method 3.9 | angular error formula | 直接决定 mean error、Hit@5/Hit@10、P90、worst-case 的合法性 | High | 角误差公式、yaw 周期处理、pitch 是否直接欧氏角差或球面方向差 | 补证；投稿前必须固定 |
| A004 | Results Table 4 / 4.5 | 0% OCS-noise table values | 主稿已有占位；若不填表格不完整 | High | 0% OCS-only mean/std/Hit@5、fusion mean/std/Hit@5、seed 统计；补充实验进度给出 5.91±0.22 / 73.8% 与 3.93±0.46 / 86.3%，需确认是否采用 | 补证后填表；若不用则删除 0% 行或改为文字 |
| A005 | Results Table 4 | 10%/20% OCS-noise Hit@5 | 目前 mean 已有，Hit@5 仍占位 | Medium | 10% Hit@5：OCS 57.8%、fusion 74.9%；20% Hit@5：OCS 35.8%、fusion 59.6%，需确认是否采用 | 补证后填表 |
| A006 | Table 2 | Weighted kNN all_raw 的 Hit@10 | 表格中仍为 `[需要作者确认]`；低容量 baseline 不完整 | Medium | Weighted kNN all_raw 的 Hit@10 和对应实验日志路径 | 补证或删去该列/该行 |
| A007 | Method / Results | model architecture and training details | 审稿人会要求可复现性；v0.1 只给了粗略模型类型 | High | MLP 层数、ResNet 修改、fusion branch、epochs、batch size、learning rate、seeds、early stopping、hardware | 放 Method 精简版，完整表放 Supplementary |
| A008 | Method 3.4 | nominal material parameters source | 金属 `F0=0.91`、roughness 等若无来源会被质疑为任意设定 | High | 参数来源、是否来自文献/工程假设/调参；是否可公开材料表 | 保留但明确 nominal；补文献或移详细参数到 Supplementary |
| A009 | Results 4.6 | 哪些 ablation/sensitivity 数值可入正文 | 补充实验已完成，但主稿仍写“where finalized values are available” | High | Phase63、公平消融、random split、BRDF sensitivity、occlusion、roll sensitivity 是否全部为最终值 | Codex 决定正文/补充材料分配 |
| A010 | Method 3.3 / Results 4.6 | phase63 fairness and cross-phase values | 主图像分支仅 phase63；跨 phase 未测或未进入主线会被问 | Medium | phase63 fairness 数值是否采用；是否存在 cross-phase 小规模结果 | phase63 公平性可正文/补充；cross-phase 若无结果写 limitation/future work |
| A011 | Results 4.3 | target centroid cue `r = 0.66` 是否作为正文风险说明 | 质心线索可能被审稿人视为伪线索或数据偏差 | Medium | 数据集审计报告路径、centroid 计算方法、是否已做居中控制 | 保留为 limitation/diagnostic，不作为贡献 |
| A012 | Results / Discussion | ResNet-fusion image-degradation 是否存在 | 当前只有 ResNet image-only 图像退化；fusion 图像退化未作为结果 | Medium | 是否已补跑 ResNet+OCS 在 degraded images 下的结果 | 若无，明确 future work，避免暗示已验证 |
| A013 | Related Work / Table 1 | Dickinson 2025 PhD 是否保留 | 学位论文可用但期刊稿中可能不如期刊/会议文献稳 | Medium | 是否有更合适的 journal/conference image-based pose source | Codex 后续引用核验阶段决策替换或保留 |
| A014 | Front matter | target journal priority and title | 影响术语、结构、Data Availability/COI 格式 | Medium | 最终目标期刊与标题选择 | 作者确认后再做期刊风格压缩 |
| A015 | Data Availability | 数据/模型/代码是否可共享 | 多数期刊需明确数据可用性；也影响可复现性评价 | High | 是否共享 simulation data、STL-derived products、trained models、scripts；仓库或按需访问语句 | 投稿前必须定稿 |
| A016 | Author Contributions | author list and CRediT roles | 投稿材料硬要求 | Medium | 作者名单、顺序、贡献分工 | 投稿材料阶段补齐 |
| A017 | Conflict of Interest | final COI wording | 各期刊格式不同 | Low | 是否确无冲突；目标期刊模板 | 投稿材料阶段补齐 |
| A018 | Limitations | 是否保持 no real optical telescope validation 的独立段落 | 这是核心审稿防线，不能被压缩掉 | High | 作者是否接受作为显性 limitation | 保留；Codex 压缩语言时不得删除 |
| A019 | ISAR boundary | 是否明确 ISAR 不进入本文主线 | 项目有真实 ISAR 数据，若混入会导致模态错配 | Medium | 是否需要在 Future Work 明确 radar/ISAR boundary | 建议 Discussion/Future Work 简短说明 |
| A020 | Result tables | 是否统一旧 TinyCNN 数值 12.38±0.74 与补充实验同批 11.87±0.69 | 项目材料中存在旧/同批复测差异，主稿采用 12.38±0.74 | Medium | 最终采用哪组 TinyCNN 数值及来源日志 | 主结果表只保留一个版本；另一个作为历史复测不进正文 |

## B. 数值审计总表

| ID | 位置 | 数值 | 对应结论 | 证据状态 | 风险等级 | 建议处理 |
|---|---|---|---|---|---|---|
| N001 | Abstract / Results | ResNet clean `1.69 +/- 0.07 deg`, Hit@5 `97.6%`, Hit@10 `99.9%` | clean image upper-bound | 与补充实验 ResNet baseline / fusion 表一致 | High | 保留，但必须继续写 upper-bound not field performance |
| N002 | Abstract / Results | 1% Gaussian image noise `85.85 +/- 3.00 deg`, Hit@5 `2.2%` | clean ResNet 对图像噪声脆弱 | 与补充实验一致 | High | 保留；注明 controlled stress test |
| N003 | Abstract / Results | worst-case `9.9 deg -> 6.6 deg` | ResNet + per_part_log fusion 改善尾部 | 与 ResNet-fusion A1/A2 一致 | Medium | 保留；避免说 fusion always best |
| N004 | Method 3.2 | grid `5 deg`, yaw `73`, pitch `37`, total `2701` | 主 yaw-pitch 网格 | 项目总览一致 | High | 保留；需 Euler/坐标定义补证 |
| N005 | Method 3.2/3.9 | train `10 deg` -> test `5 deg` | 插值泛化 split | 项目总览一致；train 563/test 1998 见项目总览 | High | 保留；建议补 train/val/test 数量 |
| N006 | Method 3.3 | `5 x 2701 = 13,505` samples | OCS 五观测几何样本数 | 项目总览一致 | Medium | 保留 |
| N007 | Method 3.3 | phase-angle `24 deg to 120 deg` | 观测几何覆盖范围 | 补充实验/项目总览一致 | Medium | 保留；若表述“approximately”可接受 |
| N008 | Method 3.7 | image resolution `128 x 128`, phase63 | 主图像分支设置 | 补充实验路径一致 | High | 保留；明确 one phase condition |
| N009 | Method 3.4 | metal `metallic=1`, `roughness=0.20`, `F0=0.91` | nominal GGX material | 主稿有值，来源需作者/文献确认 | High | 保留为 nominal；补来源或补充材料 |
| N010 | Method 3.4 | solar panel `metallic=0`, `roughness=0.40`, `ior=1.5` | nominal GGX material | 主稿有值，来源需确认 | High | 保留为 nominal；补来源 |
| N011 | Method 3.4 | baffle `metallic=0`, `roughness=0.90`, `base_color=0.08` | nominal GGX material | 主稿有值，来源需确认 | High | 保留为 nominal；补来源 |
| N012 | Method 3.5 / 4.6 | `epsilon = 1.0 mm`, `min_hit_distance = 1.0 mm` | 遮挡射线过滤设置 | 项目总览给出敏感性依据 | Medium | 保留；可把详细扫描放 Supplementary |
| N013 | Results 4.1 | OCS/Image consistency `sub-percent agreement` | forward-model sanity check | 主稿只概述，需具体日志/图表支持 | Medium | 若无明确数值，改为“within sub-percent in selected checks”或补证 |
| N014 | Results 4.1/4.6 | occlusion rates `60% to 78.5%` | 自遮挡显著 | 补充实验一致；具体几何为 60.1/69.7/72.6/78.5 等 | Medium | 保留；正文可列范围，补充材料列全表 |
| N015 | Results 4.2 | OCS `per_part_log 30D`: `5.91 +/- 0.22 deg`, Hit@5 `73.8%`, Hit@10 `94.3%` | practical OCS-only | 与补充实验 OCS-noise 0% OCS 一致 | High | 保留为 practical OCS |
| N016 | Results 4.2 | OCS `total_log 15D`: `36.69 +/- 3.6 deg`, Hit@5 `9.7%`, Hit@10 `23.5%` | total OCS weak | 项目总览支持，需日志路径 | Medium | 保留；作为弱 baseline |
| N017 | Results 4.2 | OCS `all_raw 45D`: `3.98 +/- 0.60 deg`, Hit@5 `90.7%`, Hit@10 `97.1%` | semi-oracle upper bound | 项目总览/补充实验一致 | High | 保留但只作 diagnostic/semi-oracle |
| N018 | Results 4.3 | TinyCNN `12.38 +/- 0.74 deg`, Hit@5 `26.1%`, Hit@10 `55.8%` | lightweight image baseline | 项目总览旧值一致；补充实验另有同批 `11.87±0.69`, Hit@5 27.1%, Hit@10 58.2% | Medium | 作者确认采用哪组；避免混用 |
| N019 | Results 4.3 | centroid-yaw `r = 0.66`; mean intensity `r < 0.02` | 数据集审计，无显性泄漏但存在物理位置线索 | 补充实验一致 | Medium | 保留为审计说明；勿写成可迁移真实观测特征 |
| N020 | Results 4.4 | ResNet A1 P90 `3.31`, worst `9.9`, Hit@5 `97.6%`, Hit@10 `99.9%` | image-only clean upper bound | 补充实验一致 | Medium | 保留 |
| N021 | Results 4.4 | ResNet+A2 concat5 per_part_log `1.47 +/- 0.07`, P90 `2.71`, worst `6.6`, Hit@5 `99.7%`, Hit@10 `100%` | clean fusion tail gain | 补充实验一致 | Medium | 保留；强调 modest/conditional |
| N022 | Results 4.4 | A3 phase63 per_part_log `1.61 +/- 0.07`, P90 `2.97`, worst `7.4`, Hit@5 `99.2%`, Hit@10 `100%` | single-phase OCS fairness check | 补充实验一致 | Medium | 可保留正文或移 Supplementary |
| N023 | Results 4.4 | A4 all_raw fusion `1.49 +/- 0.10`, P90 `2.70`, worst `18.7`, Hit@5 `99.2%`, Hit@10 `99.9%` | stronger OCS features do not guarantee tail robustness | 补充实验一致 | Medium | 保留为 caution；避免说 all_raw operational |
| N024 | Results 4.4 | TinyCNN fusion: all_raw fusion `5.42 deg` vs OCS `3.98 deg` | weak image branch can hurt when OCS is strong | 项目总览支持 | Low | 可放 Supplementary；正文保留一句即可 |
| N025 | Results 4.4 | TinyCNN per_part fusion `4.10 +/- 0.77 deg`; OCS `5.91`; CNN `12.38` | intermediate OCS + image complementarity | 项目总览支持 | Medium | 若主线以 ResNet 为主，旧 TinyCNN 诊断可降级 |
| N026 | Results 4.4 | weak total_log late fusion `11.99 deg` vs OCS `36.69 deg` | weak OCS 时图像主导 | 项目总览支持 | Low | 建议 Supplementary |
| N027 | Results 4.4 | TinyCNN/OCS error correlation `r = 0.003` | complementary failure modes diagnostic | 项目总览支持；主稿已限定非 ResNet | Medium | 保留限定；若无 ResNet-pair correlation 不扩展 |
| N028 | Table 2 | Weighted kNN all_raw `21.84`, Hit@5 `47.9%`, Hit@10 占位 | classical baseline | 主稿占位未完成 | Medium | 补 Hit@10 或删除该行 |
| N029 | Results 4.5 | Gaussian noise sigma `0.03`: `85.49 deg`, Hit@5 `1.5%` | ResNet collapse persists | 补充实验有 std `±4.59`，主稿缺 std | Medium | 建议补 std 或统一表格不列 std |
| N030 | Results 4.5 | Gaussian noise sigma `0.05`: `85.97 deg`, Hit@5 `1.2%` | ResNet collapse persists | 补充实验有 std `±4.48`，主稿缺 std | Medium | 建议补 std 或统一表格 |
| N031 | Results 4.5 | Gaussian noise sigma `0.10`: `87.92 deg`, Hit@5 `1.0%` | ResNet collapse persists | 补充实验有 std `±2.36`，主稿缺 std | Medium | 建议补 std 或统一表格 |
| N032 | Results 4.5 | brightness `x0.50`: `3.45 deg`, Hit@5 `78.7%` | brightness scaling less destructive | 补充实验有 std `±0.27` | Low | 可保留；补 std 或统一格式 |
| N033 | Results 4.5 | brightness `x0.75`: `2.03 deg`, Hit@5 `94.8%` | mostly robust | 补充实验有 std `±0.13` | Low | 可保留 |
| N034 | Results 4.5 | brightness `x1.25`: `1.77 deg`, Hit@5 `97.5%` | mostly robust | 补充实验有 std `±0.05` | Low | 可保留 |
| N035 | Results 4.5 | brightness `x1.50`: `2.00 deg`, Hit@5 `95.8%` | mostly robust | 补充实验有 std `±0.03` | Low | 可保留 |
| N036 | Results 4.5 | OCS noise 0% gain `+1.97 deg`; values占位 | fusion gain baseline | 补充实验给出 OCS `5.91±0.22`, Hit@5 `73.8%`; fusion `3.93±0.46`, Hit@5 `86.3%` | High | 补表或删占位 |
| N037 | Results 4.5 | OCS noise 1%: OCS `5.50±0.39`, Hit@5 `75.3%`; fusion `3.77±0.49`, Hit@5 `88.1%`; gain `+1.73` | 轻微 OCS 噪声下 fusion 仍优 | 补充实验有，但主稿未列 | Low | 可作为 Supplementary 或补 Fig. 6 |
| N038 | Results 4.5 | OCS noise 5%: OCS `7.27±0.65`, Hit@5 `63.6%`; fusion `4.65±0.57`, Hit@5 `82.9%`; gain `+2.62` | fusion gain随噪声增加 | 补充实验有，主稿未列 | Low | 可作为 Supplementary 或图中数据 |
| N039 | Results 4.5 | OCS noise 10%: OCS `9.99 +/- 0.35`, fusion `6.69 +/- 1.34`, gain `+3.30`, Hit@5 占位 | moderate OCS noise | 补充实验给出 Hit@5 57.8/74.9 | Medium | 补 Hit@5 |
| N040 | Results 4.5 | OCS noise 20%: OCS `17.25 +/- 0.71`, fusion `10.96 +/- 2.51`, gain `+6.29`, Hit@5 占位 | high OCS noise | 补充实验给出 Hit@5 35.8/59.6 | Medium | 补 Hit@5 |
| N041 | Results 4.6 | phase63 fairness: OCS 6D `21.68 deg`, Hit@5 `20.7%`; fusion `6.79 deg`, Hit@5 `63.1%` | 回应图像/OCS 几何不对称 | 补充实验完成，主稿未填具体值 | Medium | 建议正文简述，完整表 Supplementary |
| N042 | Results 4.6 | random split: all_raw `1.67`, per_part `2.72`, image `4.20`, fusion `2.13`; Hit@5 98.2/95.1/72.5/98.6 | split 稳健性 | 补充实验完成 | Medium | 建议 Supplementary；正文一句 |
| N043 | Results 4.6 | BRDF sensitivity: metal roughness median `~30-42%`, max `46.2%`; F0 `~13-16%`, max `16.5%` | nominal material sensitivity | 补充实验完成 | Medium | 建议正文保留金属 roughness 结论，完整表 Supplementary |
| N044 | Results 4.6 | occlusion per geometry: 60.1/69.7/72.6/78.5 等 | 自遮挡重要性 | 补充实验完成 | Medium | 正文范围 + Supplementary 全表 |
| N045 | Results 4.6 / Limitations | roll sensitivity mean `20.3%`, max `26.2%`; full 3-DOF cost `×37` | fixed roll limitation | 补充实验完成 | Medium | 建议 limitation 中保留 |
| N046 | Project boundary | no real telescope validation; no atmosphere/detector/PSF/earthshine/background | field-performance边界 | 主稿多处一致 | High | 必须保留 |

## C. 引用核验总表

| ID | 位置 | 引用占位 | 支撑的句子/表格 | 风险等级 | 需要查证什么 | 建议关键词 |
|---|---|---|---|---|---|---|
| C001 | Introduction | `[CITATION: optical space object characterization]` | optical response depends on geometry/material/illumination/viewing/phase/self-occlusion | High | 是否有权威 SSA/space object optical characterization 文献支持 | optical characterization space objects attitude photometry BRDF |
| C002 | Introduction | `[CITATION: optical light-curve attitude inversion]` | OCS/light-curve-like measurements are compact and extensible across geometries | High | light curve / photometric attitude inversion 代表作 | space object light curve attitude inversion photometry |
| C003 | Introduction | `[CITATION: image-based spacecraft pose estimation]` | images preserve outline/layout/shadow/brightness/specular cues | High | spacecraft/satellite image-based pose estimation 文献 | spacecraft pose estimation resolved imagery synthetic training |
| C004 | Introduction | `[CITATION: BRDF-based space object photometry]` | need consistent geometry/material/BRDF/visibility assumptions | High | BRDF satellite photometry / space object brightness modeling | satellite BRDF photometry Cook Torrance space object |
| C005 | Introduction | `[CITATION: ground-based optical observation degradation]` | ground-based observations affected by seeing, tracking, sensor noise, blur, background | High | 真实地基光学退化来源 | ground based optical satellite observation seeing tracking PSF noise |
| C006 | References only | `[CITATION: multi-modal fusion robustness]` | Reference list 有占位但正文未明确使用 | Medium | 是否需要正文引用或删除该占位 | multimodal fusion robustness spacecraft attitude estimation |
| C007 | Related Work 2.1 / Table 1 | Yang et al. 2024/2025 Photonics `[to verify]` | satellite material reflectance / pBRDF / Cook-Torrance-related support | High | 年份、题名、期刊、是否确为 Photonics、是否真的讨论 pBRDF/Cook-Torrance | Yang Photonics satellite material reflectance pBRDF Cook-Torrance |
| C008 | Related Work 2.1 / Table 1 | Lu/Yao 2024 Universe `[to verify]` | LEO constellation brightness / BRDF photometric model / real observations | High | 作者、题名、Universe 年份、Starlink/LEO 模型、是否含 detailed self-occlusion | Lu Yao Universe 2024 Starlink BRDF photometric model |
| C009 | Related Work 2.1 / Table 1 | Fankhauser et al. 2023 AJ `[to verify]` | radiometric brightness, sunlight/earthshine | High | AJ 文献元数据与 earthshine/brightness model 内容 | Fankhauser 2023 Astronomical Journal satellite brightness earthshine |
| C010 | Related Work 2.2 / Table 1 | Wang et al. 2024 ASR `[to verify]` | lab photometry / scalar brightness attitude inversion | High | 是否为 ASR、目标对象、是否 attitude inversion | Wang 2024 Advances in Space Research photometry attitude inversion space debris |
| C011 | Related Work 2.2 / Table 1 | Burton et al. 2024 ASR `[to verify]` | particle swarm light-curve attitude estimation | High | 是否粒子群、对象、验证类型 | Burton 2024 ASR light curve particle swarm attitude estimation |
| C012 | Related Work 2.2 / Table 1 | Kumar et al. 2025 Acta Astronautica `[to verify]` | digital twin / LEO uncontrolled objects / sequential comparison | Medium | 年份、期刊、具体任务是否为 attitude/object understanding | Kumar 2025 Acta Astronautica digital twin light curve uncontrolled LEO |
| C013 | Related Work 2.3 / Table 1 | Dickinson 2025 RIT PhD `[to verify]` | 6DOF pose from resolved ground-based imagery | Medium | 学位论文是否公开、是否可替换为同行评议文献 | Dickinson 2025 RIT PhD satellite pose estimation resolved ground-based imagery |
| C014 | Related Work 2.4 / Table 1 | Liu et al. 2024 Remote Sensing `[to verify]` | visual-inertial tightly coupled fusion robustness | Medium | 是否与 spacecraft attitude estimation 相关，是否不偏离 optical OCS 主线 | Liu 2024 Remote Sensing visual inertial spacecraft attitude estimation fusion |
| C015 | Table 1 cells | 多个 `[to verify]`：target/data、BRDF/self-occlusion、validation type | 文献对比表每行字段 | High | 每个表格字段是否准确；不要凭题名猜测 | 使用 DOI/原文逐项核对 |
| C016 | Method 3.4 | material parameter sources currently uncited | nominal GGX/Cook-Torrance parameter setting | High | 是否有材料 reflectance / BRDF 参数文献或需声明 engineering nominal | spacecraft material BRDF roughness F0 solar panel optical |
| C017 | Method 3.5 | ray tracing / occlusion validation currently uncited | analytical ray tracing, BVH/Embree, self-intersection handling | Medium | 是否需要引用 ray tracing/Embree 或只作为实现说明 | Embree ray tracing BVH visibility self occlusion |
| C018 | Discussion / Limitations | real optical degradation support | seeing, PSF, detector response, tracking, background | High | 最好有 1-2 篇地基观测/SSA 光学观测文献 | ground-based SSA optical observation PSF seeing satellite tracking |

## D. 过度表述风险检查

| 检查项 | 当前状态 | 风险等级 | 审计意见 | 建议处理 |
|---|---|---|---|---|
| clean image 被写成真实场景性能 | 未发现明显越界；多处写 upper-bound / not field performance | Low | 主稿控制较好 | Codex 压缩时保留这些限定语 |
| OCS 被写成 universally robust | 未发现；主稿写“independent of image-pixel degradation in this benchmark”，并说明 real OCS 会受误差影响 | Low | 表述合格 | 保留“in this benchmark”和真实 OCS 误差来源 |
| fusion 被写成 universal superiority | 未发现；多处写 conditional complementarity | Low | 表述合格 | 不要在标题/摘要改成 fusion always improves |
| `all_raw` 被写成 operational feature | 未发现；主稿多处写 semi-oracle/diagnostic | Low | 表述合格 | 保留 semi-oracle 标签；表格注释不要删 |
| `r = 0.003` 被写成 ResNet pair 证据 | 未发现；主稿明确 earlier TinyCNN/OCS diagnostic | Low | 表述合格 | 如果要用于 ResNet 需补 ResNet-pair correlation |
| ResNet noise collapse 被写成真实 atmosphere 模拟 | 未发现；主稿写 controlled stress test | Low | 表述合格 | 不要把 Gaussian noise 扩展成完整真实退化模型 |
| no real telescope validation 被弱化 | 未发现；多处声明 | Low | 表述合格 | 投稿版仍需保留 |
| nominal material 被写成实测标定 | 未发现；写 nominal not calibrated | Low | 表述合格 | 补文献/敏感性，否则不要强物理外推 |
| phase63 单相位被写成跨相位泛化 | 未发现；写 outside primary scope | Low | 表述合格 | 保留 limitation |
| fixed roll 被写成 full 3-DOF | 未发现；写 yaw-pitch under fixed roll | Low | 表述合格 | 若标题出现 pose estimation，需正文限定 attitude/yaw-pitch |

## E. 优先处理顺序

1. 确认并写死 Euler/坐标约定、target encoding、angular error formula。三者是方法可复现和所有数值合法性的基础。
2. 填补或删除 Table 4 的 0% OCS-noise 占位，并补 10%/20% Hit@5。补充实验进度已有候选值，但需作者确认采用。
3. 全面核验 Table 1 与 References 的所有 `[to verify]`。未核验前不要进入投稿稿。
4. 回查主结果数值来源，尤其 TinyCNN 旧值 `12.38±0.74` 与补充实验同批复测 `11.87±0.69` 的最终采用版本。
5. 决定 Phase63 fairness、random split、BRDF sensitivity、occlusion、roll sensitivity 哪些进正文，哪些进 Supplementary。
6. 补齐模型训练细节和架构表，包括 MLP、TinyCNN、ResNet-18、feature fusion、late fusion、seed 和 split。
7. 给 nominal material parameters 补来源或明确工程 nominal，并把详细参数/敏感性放入 Supplementary。
8. 保留 clean-image upper-bound、no-real-validation、controlled stress-test 等限定语，防止后续语言压缩时过度承诺。
9. 确认 Data Availability、Author Contributions、Conflict of Interest 和目标期刊格式。
10. 若时间允许，补 ResNet-fusion under image degradation 或 cross-phase sanity test；若不补，明确留作 future work。

## 给 Codex 的整合建议

- 不建议直接把本输出并入主稿；建议先整合为 `阶段整合输出/01_作者确认与数值审计_整合清单.md`。
- v0.2 修订时应先处理 High 风险占位，再做语言压缩。
- 当前主稿的红线控制值得保留，尤其 `upper-bound`、`semi-oracle`、`conditional complementarity`、`no real telescope validation` 四类限定语。

# OCS + 图像联合仿真 · 文献库

> 研究方向: 空间目标 OCS / BRDF 建模 / 物理渲染 / 光变曲线姿态反演 / 多模态融合
> 最后更新: 2026-05-20 | 文献总量: ~53 篇 | 已下载 PDF: 10 篇

---

## 文件与文件夹说明

| 路径 | 作用 | 更新方式 |
|------|------|----------|
| `README.md` | 总索引（本文件） | 每次检索后覆盖更新 |
| `文献清单.md` | 全部文献：元数据 + 综述 + PDF状态 + 下载链接 | 增量追加，DOI 去重 |
| `references.bib` | BibTeX 数据库，直接导入 Zotero/Mendeley | 增量追加，DOI 去重 |
| `指令` | 文献检索流程与约束 | 手动修改 |
| `papers/` | **所有已下载 PDF**（当前 10 篇） | AI 自动下载 OA 论文存于此 |
| `01_BRDF与材料表征/` | 该主题 PDF，你自己放入 | 手动 |
| `02_光变曲线反演与姿态估计/` | 该主题 PDF，你自己放入 | 手动 |
| `03_物理渲染与仿真/` | 该主题 PDF，你自己放入 | 手动 |
| `04_深度学习与多模态融合/` | 该主题 PDF，你自己放入 | 手动 |
| `05_SSA综合观测与实测数据/` | 该主题 PDF，你自己放入 | 手动 |
| `06_中文核心文献/` | 该主题 PDF，你自己放入 | 手动 |

> PDF 存放：`papers/` 是 AI 下载 PDF 的位置。01-06 文件夹供你按主题手动整理 PDF，非必须。

---

## 统计

| 主题 | 数量 | 已下载 |
|------|------|--------|
| BRDF 与材料表征 | 9 | 2 |
| 光变曲线反演与姿态估计 | 17 | 3 |
| 物理渲染与仿真 | 7 | 1 |
| 深度学习与多模态融合 | 10 | 4 |
| SSA 综合观测与实测数据 | 5 | 0 |
| 中文核心文献 | 5 | 0 |
| **合计** | **53** | **10** |

---

## 项目-文献交叉映射

> 🟢 已下载　🟡 OA可获取　🟠 需权限　🔴 无公开PDF

```
模块A OCS计算 (Phong/GGX BRDF)
├── 🟡 Lu Yao 2024      — Starlink Phong BRDF 建模，数百万条实测验证 (Universe)
├── 🟡 Yang 2024         — 5种pBRDF卫星材料对比，验证Cook-Torrance适用性 (Photonics)
├── 🟠 JMO 2023          — Phong+五参数BRDF+Embree仿真，与在轨>80%相似度
├── 🟠 张玉双 2025       — GPU加速OCS框架(~58fps)，五参数Phong，全套光学量计算
├── 🟠 Shah 2024         — LEO老化航天材料BRDF实验室测量 (JAS)
├── 🟠 Shi 2022          — 多模态BRDF+材料反演，在轨故障卫星材料识别<10%误差
├── 🟠 Optical Tech 2024 — 偏振Cook-Torrance微面元BRDF，adjusted R²=0.9957
├── 🟠 李智 2024         — 《空间目标光学特性原理与应用》清华大学出版社，国内首部专著
└── 🔴 Ceniceros 2015    — 3种BRDF(Cook-Torrance/Ashikhmin) vs AFRL实测GEO光变

模块B Blender渲染
├── 🟠 Lu 2025           — 分形表面+BRDF+光线追踪，仿真与地基实测SSIM>85% (Opt. Express)
├── 🔴 SIRIUS 2024       — GPU加速高光谱RSO渲染，sBRDF+MLI，ENVISAT实测验证 (SPIE)
├── 🔴 Meyer 2024        — DLR高保真光变仿真+实测交叉验证 (AMOS)
├── 🟠 IRLA 2023         — 五参数BRDF+路径追踪全链路成像，Hubble验证
├── 🟢 SUNDIAL 2023      — NeRF卫星3D重建+直射/环境/复杂光分解 (CVPRW)
├── 🟠 CJSS 2022         — Phong BRDF+四元数球/锥/立方/柱光度曲线仿真
└── 🔴 Maxwell 2025      — ML驱动复杂几何光度建模 (AMOS, SCOUT Space)

模块C 姿态反演 (检索式/CNN)
├── 🟠 梁勇奇 2020       — 多站联合光度观测并行融合，与多观测几何设计对应 (宇航学报)
├── 🟠 谭凡教 2020       — BRDF多级融合+时谱信号+LM姿态反演 (物理学报)
├── 🟠 苏金宇 2020       — 材料辐照退化BRDF+遗传算法反演，含实测BRDF数据 (哈工大硕士)
├── 🟠 葛丰增 2017       — 傅里叶描述子轮廓匹配+粒子滤波，图像baseline (重庆大学硕士)
├── 🟠 单斌 2017         — 光度观测姿态+角速度联合估计，被引15次 (光学学报)
├── 🟠 Valenta 2022      — CNN+BRDF光变曲线姿态分类，~7500条/3材料/86.2% (JAS)
├── 🟡 Aerospace 2025    — 联合估计姿态+角速度+漫反射+大气厚度，光变反演最前沿
├── 🟠 Wang 2024         — CZ-4C实验室光度+遗传算法姿态搜索，2.5mag鲁棒 (Adv.Space Res.)
├── 🟠 Burton 2024       — PSO光变姿态估计，无需初值 (Adv.Space Res.) ★OA
├── 🟡 Marto 2024        — 高光谱光变→NN姿态反演，无需姿态先验 (AIAA SciTech)
├── 🟠 Yoshimura 2024    — Glint镜面闪光Kalman Filter约束，解决光变多模态歧义
├── 🔴 Hara 2024         — GPR非参数姿态估计baseline (AMOS)
├── 🟢 Dickinson 2025    — 6DOF Sim2Real姿态估计，平均5°/7.1Hz (RIT PhD)
├── 🟠 Kumar 2025        — 数字孪生+光变反演闭环，发现SL-14旋转异常加速 (Acta Astron.)
├── 🟡 Groves 2025       — Perceiver-VAE自监督，22.7万条MMT-9光变 (arXiv)
├── 🟠 Muinonen 2022     — 大相位角最大化姿态RMSE，指导yaw×pitch网格设计
├── 🟠 Physics-ML 2024   — 物理引导ML光变自旋估计，优于纯黑箱CNN (JAS)
└── 🔴 Rubio 2025        — 三轴稳定卫星光变反演监测 (AMOS, GMV)

BRDF统一升级 (LegacyPhong→GGX)
├── 🟡 Yang 2024         — Cook-Torrance卫星验证 (Photonics)
├── 🟠 Shah 2024         — 航天材料BRDF测量 (JAS)
├── 🟠 Optical Tech 2024 — 偏振Cook-Torrance微面元
└── 🟠 李智 2024         — 专著第3章BRDF建模

多模态融合与深度学习拓展
├── 🟢 Liu 2024          — 视觉+惯性紧耦合姿态估计，精度提升50% (Remote Sensing)
├── 🟢 Sosa 2025         — ViT+光流6DOF姿态估计 (arXiv/ASTRA)
├── 🟢 Xiong 2025        — 无监督航天器多曝光图像融合，姿态估计前处理 (arXiv)
├── 🟠 Zhang 2025        — BRDF嵌入NeRF任意光照/视角合成 (IJAG)
├── 🟠 Soufi 2024        — 双CNN星图增强+姿态确定 (Adv.Space Res.)
├── 🟠 Tang 2025         — 卷积+Transformer光度曲线→小行星3D点云 (A&A)
├── 🔴 Peng 2024         — 多光谱+全色融合NeRF，深度误差~17%
├── 🔴 Dickinson 2024    — 6DOF深度学习卫星姿态 (AMOS, RIT论文已下载)
└── 🔴 Yoshida 2025      — 无监督度量学习姿态估计 (AMOS, NEC)

SSA实测数据与验证基准
├── 🟠 Zhi 2024          — 1447条光变/404颗卫星，最大LEO光度数据集 (MNRAS)
├── 🟠 Horiuchi 2023     — 星链VisorSat多色测光UBVRI+JHK (PASJ)
├── 🟠 Fankhauser 2023   — 卫星视亮度完整模型(直射+地球反照+BRDF) (AJ)
├── 🟠 Reyes 2023        — 多色测光颜色指数航天器材料判别 (JAS)
└── 🟠 IR satellite 2024 — 3D重建+ANSYS热分析，三轴vs自旋姿态红外特性 (Appl. Opt.)
```

---

## 投稿建议

### 目标档次

| 档次 | 推荐期刊 | 定位 |
|------|----------|------|
| **冲刺** | *Nature Astronomy* (SCI一区, IF~15) | 方法学突破时可投 |
| **主攻** | *Advances in Space Research* (SCI二区, IF~2.6) | 最匹配方向，多篇光变反演/BRDF论文在此 |
| **主攻** | *Acta Astronautica* (SCI一区, IF~2.8) | 偏工程应用，2025光变反演论文 |
| **主攻** | *Optics Express* (SCI二区, IF~3.6) | 物理渲染/成像仿真 |
| **保底** | *J. Astronautical Sciences* (SCI三区, IF~1.5) | VOLTRON SSA专辑 |
| **保底** | *Remote Sensing* (MDPI, SCI二区, IF~5.0) | 多模态融合/姿态估计，OA |
| **中间站** | *AMOS Conference* (顶会) | SSA领域顶会，预印本→期刊中间站 |
| **备选** | *Photonics* (MDPI, SCI三区, IF~2.4) | BRDF/偏振方向，OA |
| **备选** | *Universe* (MDPI, SCI三区, IF~2.0) | 卫星光度建模，OA |
| **备选** | *Aerospace* (MDPI, SCI三区, IF~2.0) | 姿态估计/光变分析，OA |

### 推荐策略

1. **先投 AMOS 会议**（摘要+演讲）→ 获取社区反馈
2. **扩充后投期刊**：AMOS 论文扩展为完整期刊论文
3. **主攻 ASR / Acta Astronautica / Optics Express**，按贡献侧重选择：
   - 偏 OCS 物理 + 遮挡 → *Advances in Space Research*
   - 偏图像渲染 + BRDF → *Optics Express*
   - 偏姿态反演算法 → *Acta Astronautica*
   - 偏多模态融合 → *Remote Sensing*

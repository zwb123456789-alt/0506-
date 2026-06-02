# 02b references.bib 修订审计

> 修订日期：2026-06-01  
> 修订文件：`D:\我的文件\研究生学术\光学项目\0506新\文献\references.bib`  
> 修订依据：第 2 阶段 GPT 外部核验、Codex 单边审阅、第 2 阶段整合清单。  
> 结论：已修正本地 `references.bib` 中已确认错误的作者、年份、卷期、页码和 DOI。为避免破坏已有文档引用，本轮暂不重命名 BibTeX key。

## 1. 修订原则

1. 只修改已由第 2 阶段外部核验确认的字段。
2. 不让 Claude 基于旧 `references.bib` 作为第一判断来源。
3. 暂保留原 BibTeX key，避免影响已有 Markdown、阅读清单和交互记录中的 key 引用。
4. 对仍需全文确认的技术字段不在 bib 中强行补充。

## 2. 已修订条目

| BibTeX key | 修订内容 | 说明 |
|---|---|---|
| `yang2024_goniopolarimetric` | `volume 11 -> 12`; `year 2024 -> 2025`; DOI `10.3390/photonics11010017 -> 10.3390/photonics12010017`; relevance 降调 | key 暂未改名，但正文应写 Yang et al. 2025 |
| `wang2024_attitude_inversion_debris` | author `Wang, X. and others -> Wang, Shu-Shu; Lin, Hou-Yuan; Kang, An-Ming; Men, Jin-Rui; Zhao, Chang-Yin`; DOI `.04.009 -> .04.005` | 书目信息修正为 ASR 2024, 74(2), 949-963 |
| `advspaceres2024_pso_lightcurve` | author `Hanada, T. and others -> Burton, Alexander; Robinson, Liam; Frueh, Carolin`; DOI `.10.008 -> .09.008` | key 暂未改名；正文应写 Burton et al. 2024 |
| `kumar2025_leo_lightcurve` | author 从 `Kumar, A. and others` 改为完整作者列表；pages `1--15 -> 654--665`; DOI `.02.019 -> .04.018` | 修正为 Acta Astronautica 2025, 232, 654-665 |
| `remote2024_visual_inertial_fusion` | author `Liu, H. and others -> Yi, Jinhui; Ma, Yuebo; Long, Hongfeng; Zhu, Zijian; Zhao, Rujin` | key 暂未改名；正文应写 Yi et al. 2024 |
| `dickinson2024_6dof_pose` | 补全作者 Dickinson, Walvoord, Gartley；booktitle 改为完整 AMOS 名称；新增 DOI 和 URL | 用于 Table 1 主引用优先于 PhD |
| `fankhauser2023_satellite_brightness` | 补全作者名；新增 `number = {2}` | DOI 原本正确 |

## 3. 已核查未改条目

| BibTeX key | 状态 | 说明 |
|---|---|---|
| `lu2024_brdf_starlink` | 保持不变 | 作者、年份、卷期、页码、DOI 与第 2 阶段核验一致 |
| `dickinson2025_sim2real_6dof` | 保持不变 | 可作为 PhD 补充引用；Table 1 主行建议优先使用 AMOS 2024 |

## 4. 本轮校验结果

已用本地检索确认以下旧错误不再出现在 `references.bib`：

```text
photonics11010017
10.1016/j.asr.2024.04.009
10.1016/j.asr.2024.10.008
10.1016/j.actaastro.2025.02.019
author = {Liu, H. and others}
author = {Hanada, T. and others}
author = {Wang, X. and others}
pages = {1--15}
```

已读回确认以下新字段存在：

```text
10.3390/photonics12010017
10.1016/j.asr.2024.04.005
10.1016/j.asr.2024.09.008
10.1016/j.actaastro.2025.04.018
Yi, Jinhui and Ma, Yuebo and Long, Hongfeng and Zhu, Zijian and Zhao, Rujin
10.64861/XCUS5673
```

## 5. 仍需后续处理

1. BibTeX key 仍有历史命名不一致，例如 `yang2024_goniopolarimetric`、`advspaceres2024_pso_lightcurve`、`remote2024_visual_inertial_fusion`。本轮为避免破坏引用未重命名，后续可在 v0.2 定稿前统一 key。
2. `论文必读文献阅读清单.md` 和 `文献清单.md` 中仍可能保留 Yang 2024 等旧文字描述，后续文献清单清理时再统一。
3. Wang / Burton / Kumar / Fankhauser 的 Table 1 技术字段仍需全文核对，尤其 BRDF、self-occlusion、validation type。
4. 地基光学退化 / seeing / PSF / tracking / AO 文献缺口尚未解决。

## 6. 后续使用规则

从本审计文件生成后，v0.2 引用替换应以修订后的 `references.bib` 和第 2 阶段整合清单为准；不得再采用 Claude 第 2 阶段输出中基于旧 bib 的 Yang 2024、Hanada、Liu 或错误 DOI 版本。

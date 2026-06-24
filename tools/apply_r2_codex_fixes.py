# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import shutil
from pathlib import Path


PROJECT_ROOT = Path(r"D:\我的文件\研究生学术\光学项目\0506新\项目重启_v0.4_BlenderOCS")
SRC = PROJECT_ROOT / "06_书籍知识库_R2候选_2026-06-23"
DST = PROJECT_ROOT / "06_书籍知识库_R2-Codex修正版_2026-06-23"


CH3_SECTION_FIXES = {
    "微信图片_20260618141949_1709_74.png": ("63", "3.4 基于Torrance-Sparrow模型的改进BRDF经验模型", "Torrance-Sparrow、BRDF、五参数模型、经验模型"),
    "微信图片_20260618141957_1710_74.png": ("64", "3.4.1 Torrance-Sparrow五参数模型", "Torrance-Sparrow、五参数模型、式(3.18)、式(3.19)"),
    "微信图片_20260618142006_1711_74.png": ("65", "3.4.1 五参数模型局限与改进推导", "五参数模型、局限性、改进推导"),
    "微信图片_20260618142017_1712_74.png": ("66", "3.4.1 五参数模型局限与改进推导", "五参数模型、改进推导、Torrance-Sparrow"),
    "微信图片_20260618142024_1713_74.png": ("67", "3.4.1 改进六参数经验模型", "改进六参数经验模型、式(3.23)、BRDF"),
    "微信图片_20260618142036_1714_74.png": ("68", "3.4.2 改进模型验证与材料样例", "改进模型验证、材料样例、参数反演"),
    "微信图片_20260618142045_1715_74.png": ("69", "3.4.2 改进模型验证与材料样例", "改进模型验证、材料样例、BRDF分布"),
    "微信图片_20260618142054_1716_74.png": ("70", "3.4.2 改进模型验证与材料样例", "改进模型验证、材料样例、BRDF分布"),
}


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write(path: Path, text: str) -> None:
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def split_md_row(line: str) -> list[str] | None:
    if not line.startswith("|"):
        return None
    return [c.strip() for c in line.strip().strip("|").split("|")]


def join_md_row(cells: list[str]) -> str:
    return "| " + " | ".join(cells) + " |"


def clean_table_31_text(line: str) -> str:
    line = line.replace("表3.14种空间目标常用材质的BRDF峰值变化", "4 种空间目标常用材质的 BRDF 峰值变化；数值待逐格人工核对")
    line = line.replace("表3.14", "表 3.1")
    line = line.replace("表3.1", "表 3.1")
    line = line.replace("表 3.1（OCR修正）", "表 3.1")
    return line


def copy_tree(force: bool = False) -> None:
    if DST.exists():
        if not force:
            raise SystemExit(
                f"{DST} already exists. Re-run with --force to replace it, "
                "or use apply_r2_codex_index_consistency_fixes.py for in-place fixes."
            )
        shutil.rmtree(DST)
    shutil.copytree(SRC, DST)


def add_codex_banner(path: Path, title: str) -> None:
    text = read(path)
    banner = f"""<!-- R2-Codex修正版：依据 16_Codex审阅_R2候选知识库入库前问题清单.md 定向修正。 -->

"""
    if "R2-Codex修正版" not in text[:300]:
        write(path, banner + text)


def fix_00() -> None:
    path = DST / "00_书籍知识库总览_R2候选.md"
    text = read(path)
    text = text.replace("本候选稿基于原始书籍图片重新整理", "本 R2-Codex 修正版基于原始书籍图片和 Codex 审阅清单重新整理")
    insert = """## R2-Codex 审阅修正摘要

- 正式入库仍暂缓；本目录是 R2-Codex 修正版，不是正式 `06_书籍知识库/`。
- 第3章 p63-p67 小节归属已按 Codex 审阅清单修正为 Torrance-Sparrow / 改进模型分支。
- P0 核心项改为“位置已确认、公式细节待人工核对”口径，不再把 OCR 截断公式当作公式全文。
- 表 3.1 已明确为“4 种空间目标常用材质的 BRDF 峰值变化”，不是路线一 C 三部件材料参数表。
- 证据等级 A 只保留给页码、图片、主题和公式/表格细节均已人工确认的条目；多数公式项降为 B。

"""
    if "## R2-Codex 审阅修正摘要" not in text:
        text = text.replace("## 当前整理状态\n", insert + "## 当前整理状态\n")
    text = text.replace(
        "- A：原始图片清晰可见，页码/编号/内容均明确。\n- B：原始图片可见，但公式/表号/变量有部分模糊。\n- C：只在旧知识库中出现，原始图片未核实。\n- D：旧知识库与原始图片冲突，应撤回或重查。",
        "- A：页码、图片、内容主题清晰，且公式/表格细节已人工确认。\n- B：页码和主题清晰，但公式符号、变量、表号、数值仍依赖 OCR 或需人工确认。\n- C：仅为旧知识库线索或 OCR 关键词线索，原始图片尚未充分核实。\n- D：旧知识库与原始图片冲突，应撤回或重查。"
    )
    add_codex_banner(path, "00")
    write(path, text)


def fix_02() -> None:
    path = DST / "02_全书图片编号_书页页码_章节映射表_R2候选.md"
    lines = read(path).splitlines()
    out = []
    for line in lines:
        cells = split_md_row(line)
        if cells and len(cells) == 7 and cells[1] in CH3_SECTION_FIXES:
            page, section, keywords = CH3_SECTION_FIXES[cells[1]]
            cells[3] = page
            cells[4] = section
            cells[5] = keywords
            cells[6] = "Codex修正：第3章 p63-p70 不能继承为 3.3.1；按 Torrance-Sparrow / 改进模型分支处理"
            line = join_md_row(cells)
        out.append(line)
    note = """## Codex 修正说明

- 第3章 `1709-1716` 已按书页内容修正为 p63-p70 的 Torrance-Sparrow / 改进模型段。
- `1718` 虽然文件编号靠后，但图片书页为 p59，是改进冯模型关键页；不得按截图编号顺序推断书页顺序。
- 第3章仍有首页 `1686` 和 `1717` 页码未识别项，正式入库需保留待确认标记。
"""
    text = "\n".join(out)
    if "## Codex 修正说明" not in text:
        text += "\n\n" + note
    add_codex_banner(path, "02")
    write(path, text)


def fix_05() -> None:
    path = DST / "05_第3章_空间目标表面材质散射特性建模_精读笔记_R2候选.md"
    lines = read(path).splitlines()
    out = []
    for line in lines:
        cells = split_md_row(line)
        if cells and len(cells) == 7 and cells[1] in CH3_SECTION_FIXES:
            page, section, keywords = CH3_SECTION_FIXES[cells[1]]
            cells[0] = page
            cells[2] = section
            cells[3] = keywords
            if cells[6] == "A":
                cells[6] = "B"
            line = join_md_row(cells)
        line = clean_table_31_text(line)
        out.append(line)
    text = "\n".join(out)
    codex_section = """## Codex 审阅修正：第3章关键页归属

| 书页 | 图片文件 | 修正后归属 | 入库边界 |
| --- | --- | --- | --- |
| p56-p59 | 1703、1704、1705、1718 | 经典冯模型与改进冯模型关键段；p59 含式 (3.16)、式 (3.17) | 可作 Method 候选，但公式细节需人工核对 |
| p63 | 1709 | 3.4 基于 Torrance-Sparrow 模型的改进 BRDF 经验模型起点 | 不再归入 3.3.1 |
| p64 | 1710 | Torrance-Sparrow 五参数模型；式 (3.18)、式 (3.19) | 位置确认，公式全文待人工核对 |
| p65-p66 | 1711、1712 | 五参数模型局限与改进推导 | 作为 B2 对照分支，不阻塞 Phase 0 |
| p67 | 1713 | 改进六参数经验模型；式 (3.23) | 位置确认，公式全文待人工核对 |
| p68-p70 | 1714、1715、1716 | 3.4.2 改进模型验证与材料样例 | 不应写成当前路线已实现 |
| p55 | 1702 | 表 3.1：4 种空间目标常用材质的 BRDF 峰值变化 | 不是材料 BRDF 系数表，不是三部件参数表 |

"""
    if "## Codex 审阅修正：第3章关键页归属" not in text:
        text = text.replace("## 13. 逐页精读映射\n", codex_section + "## 13. 逐页精读映射\n")
    add_codex_banner(path, "05")
    write(path, text)


def fix_10() -> None:
    path = DST / "10_第1-7章_页码_公式_缺页待补清单_R2候选.md"
    text = read(path)
    insert = """## Codex 修正：第3章页码和截图顺序风险

| 项 | 修正后口径 | 入库处理 |
| --- | --- | --- |
| 第3章覆盖范围 | 候选覆盖 p42-p70，另含页码未识别首页/尾页 | 不再简单写作“完全连续无异常” |
| 1718 | 文件编号靠后，但图片书页为 p59 | 应接在 1703-1705 后，作为改进冯模型关键页 |
| 1709-1716 | p63-p70 的 Torrance-Sparrow / 改进模型段 | 不再继承 3.3.1 冯模型改进原理 |
| 1717 | 页码未识别 | 保留待作者确认 |
| 表 3.1 | p55 / 1702，BRDF 峰值变化表 | 不作为材料参数表入库 |

"""
    if "## Codex 修正：第3章页码和截图顺序风险" not in text:
        text = text.replace("## 公式编号待补\n", insert + "## 公式编号待补\n")
    add_codex_banner(path, "10")
    write(path, text)


def fix_11() -> None:
    path = DST / "11_第1-7章_公式_图表_模型索引_R2候选.md"
    lines = read(path).splitlines()
    out = []
    for line in lines:
        line = clean_table_31_text(line)
        cells = split_md_row(line)
        if cells and len(cells) >= 11 and cells[1] in {"公式", "表"} and cells[-1] == "A":
            cells[-1] = "B"
            line = join_md_row(cells)
        out.append(line)
    text = "\n".join(out)
    caveat = """## Codex 修正说明

- 本索引保留 OCR 抽取结果作为线索表，不直接作为正式公式全文或表格数值来源。
- 公式类条目默认降为 B：页码/位置可用，公式符号、上下标、分式、积分/求和范围需人工复核。
- 表 3.1 已按审阅清单修正为“4 种空间目标常用材质的 BRDF 峰值变化”，不是材料参数系数表。

"""
    if "## Codex 修正说明" not in text[:1000]:
        text = text.replace("\n\n| 编号 |", "\n\n" + caveat + "| 编号 |", 1)
    add_codex_banner(path, "11")
    write(path, text)


def fix_12() -> None:
    path = DST / "12_P0核心公式图表精确核对记录_R2候选.md"
    text = """# P0核心公式图表精确核对记录_R2-Codex修正版

本文件依据 `16_Codex审阅_R2候选知识库入库前问题清单.md` 重写。原则：只确认位置和用途，不把 OCR 截断文本写成公式全文；所有核心公式全文、变量上下标和表格数值均待人工核对。

## P0-1 OCS 定义

- 章节：第2章
- 书页：p35
- 图片文件：微信图片_20260618115809_1680_74.png
- 公式/图/表编号：式 (2.29)-(2.31) 附近，具体编号待人工复核
- 内容摘要：第2章 2.4.2 附近给出 OCS / 光学散射截面定义及相关理论。
- 变量/参数：OCS 及光照-观测几何量，具体变量待人工核对。
- 对 v0.4 的用途：路线一 C 前向模型的核心物理量定义。
- 可否用于 Method：可作为 Method 候选依据。
- 边界：公式全文和变量解释必须回看原图，不采信 OCR 截断公式。
- 待确认：式号、分式结构、变量含义。
- 证据等级：B

## P0-2 BRDF 定义

- 章节：第2章
- 书页：p32
- 图片文件：微信图片_20260618115748_1677_74.png
- 公式/图/表编号：式 (2.17)，图 2.16
- 内容摘要：给出 BRDF 作为辐射亮度与辐射照度比值的定义及几何关系。
- 变量/参数：入射/出射天顶角、方位角、辐射照度、辐射亮度、立体角等。
- 对 v0.4 的用途：BRDF 模型和材质散射建模的定义来源。
- 可否用于 Method：可作为 Method 候选依据。
- 边界：只引用定义和位置；公式排版需人工核对。
- 待确认：变量符号、单位、图 2.16 图题。
- 证据等级：B

## P0-3 BRDF 测量公式

- 章节：第3章
- 书页：p48-p50
- 图片文件：微信图片_20260618121352_1693_74.png；微信图片_20260618122246_1694_74.png；微信图片_20260618122310_1695_74.png
- 公式/图/表编号：式 (3.9)-(3.11) 附近；图 3.5
- 内容摘要：第3章 3.2 BRDF 测量相关内容，包括相对测量法和定标板 BRDF 曲线。
- 变量/参数：参考板/被测材质辐射量、BRDF、测量几何；具体符号待核对。
- 对 v0.4 的用途：材料 BRDF 数据来源和测量边界说明。
- 可否用于 Method：仅在写测量依据或数据来源时使用；当前路线一 C 不应声称复现实验测量。
- 边界：p48-p50 不是五参数冯模型段。
- 待确认：式号、测量公式全文、图 3.5 图题。
- 证据等级：B

## P0-4 经典冯模型

- 章节：第3章
- 书页：p56-p57
- 图片文件：微信图片_20260618135049_1703_74.png；微信图片_20260618135056_1704_74.png
- 公式/图/表编号：式 (3.14)、式 (3.15)，图 3.12，图 3.13/3.14 附近
- 内容摘要：经典冯模型及其角度关系、BRDF 峰值随入射天顶角变化的局限。
- 变量/参数：漫反射/镜面反射系数、镜向指数、入射角、反射角等，具体符号待核对。
- 对 v0.4 的用途：B0/B1 Phong-like baseline 与书中改进模型的对照。
- 可否用于 Method：可作为模型来源候选，不能宣称已完整复现书中参数。
- 边界：经典冯模型不是第3章 p48-p50 的内容。
- 待确认：式 (3.14)、式 (3.15) 全文。
- 证据等级：B

## P0-5 改进冯模型

- 章节：第3章
- 书页：p56-p59
- 图片文件：微信图片_20260618135049_1703_74.png；微信图片_20260618135056_1704_74.png；微信图片_20260618135104_1705_74.png；微信图片_20260618142222_1718_74.png
- 公式/图/表编号：关键公式为 p59 / 1718 的式 (3.16)、式 (3.17)
- 内容摘要：改进冯模型通过新增参数调节菲涅耳反射强度和镜面反射分量变化速度，并通过参数反演误差验证描述能力。
- 变量/参数：Pd、Ps、α、β、a、b 等；具体大小写和上下标待人工核对。
- 对 v0.4 的用途：路线一 C 的 B1 书中改进冯模型候选分支。
- 可否用于 Method：位置可进入 Method 依据；公式全文和参数范围必须人工确认后才能写入。
- 边界：不能写成“路线一 C 已采用书中三部件材料参数”。
- 待确认：式 (3.16)、式 (3.17) 全文和参数解释。
- 证据等级：B

## P0-6 Torrance-Sparrow 五参数模型

- 章节：第3章
- 书页：p63-p64
- 图片文件：微信图片_20260618141949_1709_74.png；微信图片_20260618141957_1710_74.png
- 公式/图/表编号：关键公式为 p64 / 1710 的式 (3.18)、式 (3.19)
- 内容摘要：第3章 3.4 开始基于 Torrance-Sparrow 模型构建改进 BRDF 经验模型，并引出五参数模型。
- 变量/参数：五参数模型变量待原图核对。
- 对 v0.4 的用途：B2 BRDF 对照分支，作为后续模型扩展。
- 可否用于 Method：当前不进入 Phase 0 Method 主线；可在 Discussion/Future Work 中说明。
- 边界：不得写成“完整书中五参数冯模型已实现”。
- 待确认：式 (3.18)、式 (3.19) 全文。
- 证据等级：B

## P0-7 改进六参数经验模型

- 章节：第3章
- 书页：p67
- 图片文件：微信图片_20260618142024_1713_74.png
- 公式/图/表编号：式 (3.23)
- 内容摘要：在五参数模型基础上进一步改进，形成改进六参数经验模型；p68-p70 主要为验证和材料样例。
- 变量/参数：六参数模型变量待人工核对。
- 对 v0.4 的用途：B2 后续 BRDF 对照分支。
- 可否用于 Method：暂不进入当前 Method 主线。
- 边界：p68-p70 不是模型定义主位置，主要是验证与样例。
- 待确认：式 (3.23) 全文、参数含义和适用范围。
- 证据等级：B

## P0-8 面元 OCS 求和与非分辨仿真

- 章节：第4章
- 书页：p73-p76 附近，另含第4章首页
- 图片文件：微信图片_20260618163949_1719_74.png；微信图片_20260618163957_1720_74.png；微信图片_20260618164004_1721_74.png；微信图片_20260618164010_1722_74.png
- 公式/图/表编号：式 (4.1) 及图 4.1 / 表 4.1 附近
- 内容摘要：第4章介绍 OCS 仿真计算一般流程、复杂空间目标 OCS 数值仿真和 OpenGL 拾取技术相关流程。
- 变量/参数：面元、OCS、光照方向、观测方向、材质 BRDF 等。
- 对 v0.4 的用途：路线一 C 前向仿真的主证据链。
- 可否用于 Method：可作为 Method 架构依据。
- 边界：具体实现仍以 v0.4 BlenderOCS 代码为准，书中流程不能写成代码已完整复现。
- 待确认：式 (4.1) 全文和图/表编号。
- 证据等级：B

## P0-9 表 3.1 材质 BRDF 峰值变化

- 章节：第3章
- 书页：p55
- 图片文件：微信图片_20260618135042_1702_74.png
- 公式/图/表编号：表 3.1
- 内容摘要：4 种空间目标常用材质的 BRDF 峰值变化。
- 变量/参数：峰值变化相关数据，数值待逐格人工核对。
- 对 v0.4 的用途：Discussion 中说明材质散射差异和模型选择动机。
- 可否用于 Method：暂不作为路线一 C 材料参数表。
- 边界：不是材料 BRDF 系数表；不是太阳能板/金属主体/MLI 三部件参数表。
- 待确认：表格数值、单位、4 种材质名称。
- 证据等级：B
"""
    write(path, "<!-- R2-Codex修正版：重写 P0 核对记录。 -->\n\n" + text)


def fix_13() -> None:
    path = DST / "13_书籍知识库对v0.4主线的方法支撑与路线把控_R2候选.md"
    text = read(path)
    insert = """## Codex 修正：路线一 C 当前口径

| 分支 | 当前口径 | 书中位置 | 入库边界 |
| --- | --- | --- | --- |
| B0 | project provisional Phong-like baseline | 项目历史 `materials.py` / 临时参数，不是书中已确认参数 | 用于 Phase 0 smoke test 和最小链路闭合 |
| B1 | 书中改进冯模型候选分支 | 第3章 p56-p59 / 1703、1704、1705、1718；式 (3.16)、式 (3.17) | 等公式细节和材料对应关系确认后再进 Method |
| B2 | Torrance-Sparrow 五参数 / 改进六参数模型 | 第3章 p63-p67 / 1709-1713；式 (3.18)、式 (3.19)、式 (3.23) | 后续 BRDF 对照分支，不阻塞 Phase 0 |

禁止写成：

```text
路线一 C 已采用书中三部件材料参数
路线一 C 已实现完整书中五参数冯模型
书中太阳能板/金属主体/MLI/隐身板参数已确认
```

"""
    if "## Codex 修正：路线一 C 当前口径" not in text:
        text = text.replace("## 总体判断\n", insert + "## 总体判断\n")
    add_codex_banner(path, "13")
    write(path, text)


def fix_14() -> None:
    path = DST / "14_旧知识库错误更正清单_R2候选.md"
    text = """# 旧知识库错误更正清单_R2-Codex修正版

本文件取代关键词批量生成的噪声表，只保留正式入库前必须处理的高价值错误。旧知识库仍只作为参考和对照，不作为权威来源。

| 旧文件/旧说法 | 新证据 | 新判断 | 建议处理 | 优先级 |
| --- | --- | --- | --- | --- |
| 将第3章 p48-p50 解释为五参数冯模型或核心经验模型段 | p48-p50 / 1693-1695 为 BRDF 测量、相对测量法、定标板 BRDF 曲线相关内容 | 旧说法错误 | 修正为 BRDF 测量段 | P0 |
| 将第3章 56-59 页的经典/改进冯模型定位不完整 | p56-p59 / 1703、1704、1705、1718；p59 含式 (3.16)、式 (3.17) | 旧说法缺关键页 1718 | 补入 p59 / 1718，作为 B1 关键证据 | P0 |
| 将第3章 63-67 页继承到 3.3.1 冯模型改进原理 | p63-p67 / 1709-1713 属于 3.4 Torrance-Sparrow / 改进模型分支 | 旧小节归属错误 | 修正 02、05、11、12 中对应条目 | P0 |
| Torrance-Sparrow 五参数模型位置不清 | p63-p64 / 1709-1710；关键公式为式 (3.18)、式 (3.19) | 位置确认，公式全文待核对 | 作为 B2 对照分支记录 | P0 |
| 改进六参数经验模型位置不清 | p67 / 1713；关键公式为式 (3.23) | 位置确认，p68-p70 为验证与样例 | 单列为 P0-7，不与五参数模型混写 | P0 |
| 将 p55 表 3.1 写成表 3.14 或材料参数系数表 | p55 / 1702；表 3.1 为 4 种空间目标常用材质的 BRDF 峰值变化 | OCR 表号错误，性质误判风险高 | 修正表号；降级为峰值变化表，不作材料参数库 | P0 |
| 声称书中太阳能电池阵、铝合金、MLI、隐身/吸波材料直接参数表已确认 | 第3章仅确认材料类别与 BRDF 峰值/测量/反演线索，未逐格确认三部件参数表 | 旧说法过强，应撤回 | 改为“待作者确认/需补证据” | P0 |
| 声称路线一 C 已采用书中三部件材料参数 | 当前 B0 参数来自项目临时 baseline，不是书中已确认材料参数 | 与证据不匹配 | 删除或改写为 provisional baseline | P0 |
"""
    write(path, "<!-- R2-Codex修正版：压缩旧知识库错误更正清单。 -->\n\n" + text)


def fix_15() -> None:
    path = DST / "15_本轮重新整理结论总表_R2候选.md"
    text = """# 本轮重新整理结论总表_R2-Codex修正版

| 项 | 结论 | 证据等级 | 是否可写入正式知识库 | 是否需 Codex 审阅 | 是否需作者确认 |
| --- | --- | --- | --- | --- | --- |
| R2 候选整体 | 候选底稿通过，已形成 R2-Codex 修正版 | B | 可作为正式入库前底稿 | 已审阅并修正关键项 | 是 |
| 第3章 p63-p67 | 已从 3.3.1 纠正为 Torrance-Sparrow / 改进模型分支 | B | 可写入正式知识库的位置索引 | 是 | 公式全文需确认 |
| P0 核心公式 | 已改为“位置确认、公式细节待人工核对”口径 | B | 只可写入位置与用途，不可写入 OCR 公式全文 | 是 | 是 |
| 表 3.1 | 已纠正为“4 种空间目标常用材质的 BRDF 峰值变化” | B | 可写入表位置和性质 | 是 | 数值需逐格确认 |
| 材料参数表 | 未确认太阳能板/铝合金/MLI/隐身板直接参数表 | C | 不可作为正式参数库 | 是 | 是 |
| 旧知识库对照 | 已压缩为高价值错误更正清单 | B | 可作为修正式入库依据 | 是 | 部分 |
| 路线一 C | B0 provisional baseline 不变；B1/B2 后置 | B | 可写入路线边界 | 是 | 部分 |
| 正式入库 | 仍暂缓，需要作者确认 P0 公式和表格数值 | B | 暂不覆盖正式 `06_书籍知识库/` | 是 | 是 |
"""
    write(path, "<!-- R2-Codex修正版：更新最终结论。 -->\n\n" + text)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create the R2-Codex revised directory. Existing output is preserved unless --force is set."
    )
    parser.add_argument("--force", action="store_true", help="replace the existing R2-Codex revised directory")
    args = parser.parse_args()

    copy_tree(force=args.force)
    fix_00()
    fix_02()
    fix_05()
    fix_10()
    fix_11()
    fix_12()
    fix_13()
    fix_14()
    fix_15()
    print(f"Wrote R2-Codex revised files to {DST}")


if __name__ == "__main__":
    main()

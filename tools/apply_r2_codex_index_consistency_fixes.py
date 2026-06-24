# -*- coding: utf-8 -*-
from __future__ import annotations

from pathlib import Path


BASE = Path(r"D:\我的文件\研究生学术\光学项目\0506新\项目重启_v0.4_BlenderOCS\06_书籍知识库_R2-Codex修正版_2026-06-23")

B2_USE = "B2 后续BRDF对照分支；Discussion/Future Work；不阻塞Phase 0"
B2_BOUNDARY = "B2 后续BRDF对照分支 / Discussion / Future Work；不写入 Phase 0 Method 主线；不声称 v0.4 已完整实现书中五参数或六参数模型"

B2_FILES = {
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
    line = line.replace("表3.1（OCR修正）", "表 3.1")
    line = line.replace("表3.1：4种空间目标常用材质的BRDF峰值变化（OCR曾误作表 3.1）", "4 种空间目标常用材质的 BRDF 峰值变化；数值待逐格人工核对")
    line = line.replace("表3.1：4种空间目标常用材质的BRDF峰值变化（OCR曾误作表3.1（OCR修正））", "4 种空间目标常用材质的 BRDF 峰值变化；数值待逐格人工核对")
    line = line.replace("表3.1：4种空间目标常用材质的BRDF峰值变化（OCR曾误作表3.14）", "4 种空间目标常用材质的 BRDF 峰值变化；数值待逐格人工核对")
    line = line.replace("表3.14种空间目标常用材质的BRDF峰值变化", "4 种空间目标常用材质的 BRDF 峰值变化；数值待逐格人工核对")
    line = line.replace("表3.14", "表 3.1")
    line = line.replace("表3.1", "表 3.1")
    return line


def is_formula_id(value: str) -> bool:
    return "(" in value and ")" in value and any(ch.isdigit() for ch in value)


def fix_05() -> None:
    path = BASE / "05_第3章_空间目标表面材质散射特性建模_精读笔记_R2候选.md"
    lines = read(path).splitlines()
    out: list[str] = []
    for line in lines:
        line = clean_table_31_text(line)
        cells = split_md_row(line)
        if cells:
            row_file = next((f for f in B2_FILES if f in line), "")
            if row_file:
                page, section, keywords = B2_FILES[row_file]
                if len(cells) == 7:
                    # Handles formula rows, chart rows, model rows, and the page mapping table.
                    if cells[0].isdigit() or cells[0] in {"图", "表", "模型", "公式"}:
                        if cells[0].isdigit():
                            cells[0] = page
                        if row_file in cells:
                            idx = cells.index(row_file)
                            # Page mapping table: file is column 2, section is column 3.
                            if idx == 1 and len(cells) >= 4:
                                cells[2] = section
                                cells[3] = keywords
                            # Formula/chart/model tables: file is column 2 or 3; use column is next-to-last.
                            cells[-2] = B2_USE
                        cells[-1] = "B"
                    line = join_md_row(cells)
            else:
                # Lower formula and table evidence when details are OCR-derived.
                if len(cells) == 7:
                    if cells[-1] == "A":
                        cells[-1] = "B"
                    if any(is_formula_id(c) for c in cells) or cells[0] in {"图", "表", "模型"} or "表 3.1" in line:
                        if "表 3.1" in line:
                            if cells[0] == "表":
                                cells[3] = "表 3.1"
                                cells[4] = "4 种空间目标常用材质的 BRDF 峰值变化；数值待逐格人工核对"
                                cells[-2] = "Discussion/背景参考"
                            elif len(cells) > 4:
                                cells[3] = "表 3.1"
                        line = join_md_row(cells)
        out.append(line)
    text = "\n".join(out)
    note = """## Codex 派生索引一致性修正

- p63-p70 / 1709-1716 的 Torrance-Sparrow 五参数、改进六参数、模型验证与材料样例条目，统一从当前路线一 C Phase 0 Method 主线移出。
- 这些内容仅作为 B2 后续 BRDF 对照分支、Discussion/Future Work 或模型扩展理论线索。
- 公式、参数、表格数值和 OCR 抽取图题未逐项人工核对前，证据等级统一不高于 B。
- 表 3.1 的正式口径为“4 种空间目标常用材质的 BRDF 峰值变化”，不是材料 BRDF 系数表，也不是路线一 C 三部件参数表。

"""
    if "## Codex 派生索引一致性修正" not in text:
        text = text.replace("## Codex 审阅修正：第3章关键页归属\n", note + "## Codex 审阅修正：第3章关键页归属\n")
    text = text.replace("| A |", "| B |")
    write(path, text)


def fix_11() -> None:
    path = BASE / "11_第1-7章_公式_图表_模型索引_R2候选.md"
    lines = read(path).splitlines()
    out: list[str] = []
    for line in lines:
        line = clean_table_31_text(line)
        cells = split_md_row(line)
        if cells and len(cells) >= 11:
            row_file = next((f for f in B2_FILES if f in line), "")
            typ = cells[1]
            if row_file:
                page, _, keywords = B2_FILES[row_file]
                cells[3] = page
                if typ in {"公式", "图", "表", "模型", "数据处理方法"}:
                    cells[7] = f"{keywords}；{B2_BOUNDARY}"
                    cells[9] = B2_USE
                    cells[10] = "B"
            if typ in {"公式", "图", "表", "模型", "数据处理方法"}:
                cells[10] = "B"
            if cells[-1] == "A":
                cells[-1] = "B"
            if typ == "图" and row_file:
                cells[10] = "B"
            if "表 3.1" in " ".join(cells):
                cells[5] = "表 3.1"
                cells[6] = "4 种空间目标常用材质的 BRDF 峰值变化"
                cells[7] = "数值待逐格人工核对；不得作为材料 BRDF 系数表或路线一 C 三部件参数表"
                cells[9] = "Discussion/背景参考"
                cells[10] = "B"
            line = join_md_row(cells)
        out.append(line)
    text = "\n".join(out)
    text = text.replace("不是材料参数系数表", "不是正式材料参数来源")
    note = """## Codex 派生索引一致性修正

- `1709-1716` 对应第3章 p63-p70，归入 3.4 / 3.4.1 / 3.4.2 的 B2 后续 BRDF 对照分支。
- 本索引不可作为公式全文、变量列表、参数数值或图表数值来源。
- 公式、表格和 OCR 抽取图题未人工核对前，证据等级统一不高于 B。
- 表 3.1 仅作为 BRDF 峰值变化线索，不作为正式材料参数来源。

"""
    if "## Codex 派生索引一致性修正" not in text:
        text = text.replace("## Codex 修正说明\n", note + "## Codex 修正说明\n")
    text = text.replace("| A |", "| B |")
    write(path, text)


def fix_13() -> None:
    path = BASE / "13_书籍知识库对v0.4主线的方法支撑与路线把控_R2候选.md"
    lines = read(path).splitlines()
    out: list[str] = []
    for line in lines:
        cells = split_md_row(line)
        if cells:
            row_file = next((f for f in B2_FILES if f in line), "")
            if row_file and len(cells) == 8:
                page, section, keywords = B2_FILES[row_file]
                cells[0] = f"{section}：{keywords}"
                cells[1] = f"第3章 p.{page} `{row_file}`"
                cells[2] = "B2后续对照，不进入Phase 0 Method主线"
                cells[3] = "弱相关"
                cells[4] = "可作后续参数/模型对照"
                cells[5] = "弱相关"
                cells[6] = "Discussion/Future Work"
                cells[7] = B2_BOUNDARY
                line = join_md_row(cells)
        out.append(line)
    text = "\n".join(out)
    if "1709-1716 不得在本表中正向归属为 3.3.1" not in text:
        text = text.replace(
            "禁止写成：\n",
            "派生表一致性要求：1709-1716 不得在本表中正向归属为 3.3.1；p63-p70 统一按 B2 后续 BRDF 对照分支处理。\n\n禁止写成：\n",
        )
    write(path, text)


def fix_15() -> None:
    path = BASE / "15_本轮重新整理结论总表_R2候选.md"
    text = read(path)
    if "派生索引一致性" not in text:
        text = text.replace(
            "| 正式入库 | 仍暂缓，需要作者确认 P0 公式和表格数值 | B | 暂不覆盖正式 `06_书籍知识库/` | 是 | 是 |",
            "| 派生索引一致性 | 05/11/13 已同步修正 p63-p70、B2 口径、表 3.1 和证据等级 | B | 可作为入库前复核底稿 | 是 | 部分 |\n| 正式入库 | 仍暂缓，需要作者确认 P0 公式和表格数值 | B | 暂不覆盖正式 `06_书籍知识库/` | 是 | 是 |",
        )
    write(path, text)


def main() -> None:
    fix_05()
    fix_11()
    fix_13()
    fix_15()
    print("Applied R2-Codex derived-index consistency fixes.")


if __name__ == "__main__":
    main()

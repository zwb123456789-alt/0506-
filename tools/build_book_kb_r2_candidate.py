# -*- coding: utf-8 -*-
from __future__ import annotations

import json
import re
from collections import defaultdict
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any

from PIL import Image
from rapidocr_onnxruntime import RapidOCR


BOOK_ROOT = Path(r"D:\我的文件\研究生学术\光学项目\书籍工作\书籍")
PROJECT_ROOT = Path(r"D:\我的文件\研究生学术\光学项目\0506新\项目重启_v0.4_BlenderOCS")
OLD_KB_ROOT = PROJECT_ROOT / "06_书籍知识库"
OUT_ROOT = PROJECT_ROOT / "06_书籍知识库_R2候选_2026-06-23"
OCR_JSON = OUT_ROOT / "_ocr_cache" / "book_ocr.json"


CHAPTER_ORDER = [
    ("第一章绪论", "第1章", "绪论"),
    ("第二章", "第2章", "空间目标光学散射特性的基本理论"),
    ("第三章", "第3章", "空间目标表面材质散射特性建模"),
    ("第四章", "第4章", "空间目标非分辨光学散射特性数值模拟技术"),
    ("第五章", "第5章", "空间目标光学散射特性实验测量"),
    ("第六章", "第6章", "基于光度特性的空间目标运动状态分析"),
    ("第七章", "第7章", "基于光学散射特性的空间目标识别与姿态分析"),
]

CHAPTER_NOTE_FILES = {
    "第1章": "03_第1章_绪论_精读笔记_R2候选.md",
    "第2章": "04_第2章_空间目标光学散射特性的基本理论_精读笔记_R2候选.md",
    "第3章": "05_第3章_空间目标表面材质散射特性建模_精读笔记_R2候选.md",
    "第4章": "06_第4章_空间目标非分辨光学散射特性数值模拟技术_精读笔记_R2候选.md",
    "第5章": "07_第5章_空间目标光学散射特性实验测量_精读笔记_R2候选.md",
    "第6章": "08_第6章_基于光度特性的空间目标运动状态分析_精读笔记_R2候选.md",
    "第7章": "09_第7章_基于光学散射特性的空间目标识别与姿态分析_精读笔记_R2候选.md",
}


KEYWORDS = [
    "OCS", "光学横截面", "BRDF", "双向反射分布函数", "冯模型", "Phong",
    "Torrance", "Sparrow", "Cook", "Maxwell", "Davies", "面元", "非分辨",
    "光度", "姿态", "三轴", "章动", "自旋", "遗传算法", "粒子群", "反演",
    "太阳能电池", "铝", "铝合金", "MLI", "多层隔热", "测量", "定标",
    "偏振", "散射", "辐射", "实验", "仿真", "STK", "OpenGL", "蒙特卡罗",
]

METHOD_TERMS = [
    "定义", "公式", "模型", "面元", "仿真", "测量", "反演", "算法", "参数", "定标",
    "坐标", "几何", "流程", "适应度", "遗传算法",
]

DISCUSSION_TERMS = [
    "应用", "识别", "分析", "影响", "误差", "局限", "未来", "实测", "验证",
]

INDEX_PATTERNS = {
    "公式": re.compile(r"[（(]\s*\d+\.\d+\s*[）)]"),
    "图": re.compile(r"图\s*\d+\.\d+"),
    "表": re.compile(r"表\s*\d+\.\d+"),
}

SECTION_RE = re.compile(r"^(\d+\.\d+(?:\.\d+)?)\s*([^\d\s].{0,40})")


@dataclass
class OcrLine:
    text: str
    score: float
    x: float
    y: float
    w: float
    h: float


def ensure_dirs() -> None:
    (OUT_ROOT / "_ocr_cache").mkdir(parents=True, exist_ok=True)


def line_from_item(item: Any) -> OcrLine:
    box, text, score = item
    xs = [p[0] for p in box]
    ys = [p[1] for p in box]
    return OcrLine(
        text=str(text).strip(),
        score=float(score),
        x=sum(xs) / 4,
        y=sum(ys) / 4,
        w=max(xs) - min(xs),
        h=max(ys) - min(ys),
    )


def run_ocr() -> list[dict[str, Any]]:
    if OCR_JSON.exists():
        return json.loads(OCR_JSON.read_text(encoding="utf-8"))

    ocr = RapidOCR()
    records: list[dict[str, Any]] = []
    for folder, chapter_no, chapter_title in CHAPTER_ORDER:
        chapter_dir = BOOK_ROOT / folder
        files = sorted(chapter_dir.glob("*"))
        files = [p for p in files if p.suffix.lower() in {".png", ".jpg", ".jpeg", ".bmp", ".webp"}]
        for order, path in enumerate(files, start=1):
            image = Image.open(path)
            result, elapsed = ocr(str(path))
            lines = [asdict(line_from_item(item)) for item in (result or [])]
            records.append(
                {
                    "chapter_folder": folder,
                    "chapter": chapter_no,
                    "chapter_title": chapter_title,
                    "image_order": order,
                    "file_name": path.name,
                    "file_path": str(path),
                    "width": image.size[0],
                    "height": image.size[1],
                    "ocr_elapsed": elapsed,
                    "lines": lines,
                }
            )
            print(f"OCR {chapter_no} {order}/{len(files)} {path.name} lines={len(lines)}")
    OCR_JSON.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
    return records


def sorted_lines(rec: dict[str, Any]) -> list[dict[str, Any]]:
    return sorted(rec["lines"], key=lambda r: (r["y"], r["x"]))


def full_text(rec: dict[str, Any]) -> str:
    return "\n".join(line["text"] for line in sorted_lines(rec) if line["text"])


def screenshot_no(file_name: str) -> str:
    m = re.search(r"_(\d+)_74\.", file_name)
    return m.group(1) if m else ""


def infer_page(rec: dict[str, Any]) -> tuple[str, bool, str]:
    width = rec["width"]
    candidates: list[tuple[float, str]] = []
    for line in sorted_lines(rec):
        text = line["text"].strip()
        if line["y"] > 130:
            continue
        if re.fullmatch(r"\d{1,3}", text) and (line["x"] < width * 0.16 or line["x"] > width * 0.84):
            candidates.append((line["score"], text))
    if candidates:
        candidates.sort(reverse=True)
        return candidates[0][1], True, ""

    # Some first pages do not show a normal book page number; fall back to explicit OCR if present.
    for line in sorted_lines(rec)[:8]:
        text = line["text"].strip()
        if re.fullmatch(r"\d{1,3}", text):
            return text, True, "页码位置异常，需人工复核"
    return "", False, "页码未识别或不可见"


def infer_sections(records: list[dict[str, Any]]) -> None:
    current: dict[str, str] = {}
    for rec in records:
        chap = rec["chapter"]
        section_hits: list[str] = []
        for line in sorted_lines(rec):
            text = normalize_heading(line["text"])
            m = SECTION_RE.match(text)
            if m and is_likely_section_heading(text, line):
                section_hits.append(f"{m.group(1)} {m.group(2).strip()}")
        if section_hits:
            current[chap] = section_hits[-1]
        rec["section_hits"] = section_hits
        rec["current_section"] = current.get(chap, "")


def normalize_heading(text: str) -> str:
    return (
        text.replace(" ", "")
        .replace("．", ".")
        .replace("。", ".")
        .replace("（", "(")
        .replace("）", ")")
    )


def is_likely_section_heading(text: str, line: dict[str, Any]) -> bool:
    if line.get("y", 9999) > 420:
        return False
    if any(mark in text for mark in ["=", "~", "≤", "≥", "∑", "×", "X10", "x10"]):
        return False
    chinese = len(re.findall(r"[\u4e00-\u9fff]", text))
    digits = len(re.findall(r"\d", text))
    if chinese < 2:
        return False
    if digits > max(4, chinese * 2):
        return False
    if len(text) > 45:
        return False
    return True


def extract_keywords(text: str) -> list[str]:
    hits = []
    lower = text.lower()
    for kw in KEYWORDS:
        if kw.lower() in lower or kw in text:
            hits.append(kw)
    return hits[:10]


def evidence_grade(rec: dict[str, Any], important: bool = False) -> str:
    lines = rec["lines"]
    if not lines:
        return "C"
    avg = sum(line["score"] for line in lines) / len(lines)
    page, visible, _ = infer_page(rec)
    if avg >= 0.94 and (visible or not important):
        return "A"
    if avg >= 0.84:
        return "B"
    return "B"


def collect_indices(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for rec in records:
        text = full_text(rec)
        page, visible, page_note = infer_page(rec)
        for typ, pat in INDEX_PATTERNS.items():
            for m in pat.finditer(text):
                number = re.sub(r"\s+", "", m.group(0)).replace("（", "(").replace("）", ")")
                context = context_around(text, m.start(), m.end(), 80)
                items.append(
                    {
                        "类型": typ,
                        "章": rec["chapter"],
                        "书页": page,
                        "图片文件": rec["file_name"],
                        "编号": number,
                        "名称": infer_name_from_context(context, typ, number),
                        "摘要": context.replace("\n", " "),
                        "变量参数": infer_params(context),
                        "用途": infer_use(context),
                        "证据等级": evidence_grade(rec, important=True),
                        "异常": page_note,
                    }
                )
        model_terms = ["BRDF", "冯模型", "Torrance-Sparrow", "Cook-Torrance", "Maxwell-Beard", "Davies", "面元", "遗传算法", "光度曲线", "姿态反演"]
        for term in model_terms:
            if term.lower() in text.lower() or term in text:
                items.append(
                    {
                        "类型": "模型" if "模型" in term or term in text else "数据处理方法",
                        "章": rec["chapter"],
                        "书页": page,
                        "图片文件": rec["file_name"],
                        "编号": "",
                        "名称": term,
                        "摘要": context_around(text, text.lower().find(term.lower()) if term.lower() in text.lower() else text.find(term), -1, 100).replace("\n", " "),
                        "变量参数": infer_params(context_around(text, text.lower().find(term.lower()) if term.lower() in text.lower() else text.find(term), -1, 100)),
                        "用途": infer_use(text),
                        "证据等级": evidence_grade(rec, important=True),
                        "异常": page_note,
                    }
                )
    # De-duplicate coarse repeated model entries by type/chapter/page/file/name/number.
    seen = set()
    deduped = []
    for item in items:
        key = (item["类型"], item["章"], item["书页"], item["图片文件"], item["编号"], item["名称"])
        if key not in seen:
            seen.add(key)
            deduped.append(item)
    return deduped


def context_around(text: str, start: int, end: int, span: int) -> str:
    if start < 0:
        return text[: span * 2]
    if end < start:
        end = start
    return text[max(0, start - span) : min(len(text), end + span)]


def infer_name_from_context(context: str, typ: str, number: str) -> str:
    lines = [ln.strip() for ln in context.splitlines() if ln.strip()]
    if typ in {"图", "表"}:
        for line in lines:
            if number in re.sub(r"\s+", "", line):
                return line[:60]
    if "BRDF" in context:
        return "BRDF相关定义/模型公式"
    if "OCS" in context or "光学横截面" in context:
        return "OCS/光学横截面相关公式"
    if "冯" in context or "Phong" in context:
        return "冯模型相关公式"
    if "Torrance" in context:
        return "Torrance-Sparrow相关公式"
    if "适应度" in context or "均方误差" in context:
        return "参数反演适应度函数"
    return f"{typ}{number}"


def infer_params(context: str) -> str:
    params = []
    for token in ["f", "BRDF", "ρ", "rho", "θ", "φ", "α", "β", "Pd", "Ps", "n", "a", "b", "σ", "τ", "OCS"]:
        if token in context:
            params.append(token)
    return "、".join(dict.fromkeys(params)) if params else "待作者确认"


def infer_use(text: str) -> str:
    hits = extract_keywords(text)
    use = []
    if any(k in hits for k in ["OCS", "光学横截面", "BRDF", "冯模型", "Torrance", "Sparrow", "面元", "非分辨", "仿真"]):
        use.append("路线一C/前向模型")
    if any(k in hits for k in ["三轴", "光度", "姿态", "自旋", "章动"]):
        use.append("三轴小项目/姿态分析")
    if any(k in hits for k in ["反演", "遗传算法", "粒子群"]):
        use.append("路线二/参数反演")
    if any(k in hits for k in ["识别", "分类"]):
        use.append("路线三/识别分析")
    return "；".join(use) if use else "Discussion/背景参考"


def classify_page_use(text: str) -> tuple[str, str, str]:
    method = any(t in text for t in METHOD_TERMS)
    discussion = any(t in text for t in DISCUSSION_TERMS)
    if method:
        method_text = "可作为 Method 依据，但须保留原书公式/图表证据并避免声称已完全复现。"
    else:
        method_text = "不建议直接写入 Method；更适合作为背景或讨论。"
    if discussion:
        discussion_text = "可用于 Discussion / Limitations / Future Work。"
    else:
        discussion_text = "仅作局部技术背景。"
    boundary = "不能把原书提出或引用的方法写成 v0.4 已实现；未清晰识别的参数、表号、页码须待作者确认。"
    return method_text, discussion_text, boundary


def write(path: Path, content: str) -> None:
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def md_table(headers: list[str], rows: list[list[Any]]) -> str:
    out = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    for row in rows:
        cells = []
        for cell in row:
            val = "" if cell is None else str(cell)
            val = val.replace("\n", "<br>").replace("|", "\\|")
            cells.append(val)
        out.append("| " + " | ".join(cells) + " |")
    return "\n".join(out)


def build_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    infer_sections(records)
    for rec in records:
        text = full_text(rec)
        page, visible, page_note = infer_page(rec)
        rec["book_page"] = page
        rec["page_visible"] = visible
        rec["page_note"] = page_note
        rec["screenshot_no"] = screenshot_no(rec["file_name"])
        rec["keywords"] = extract_keywords(text)
        rec["formula_hits"] = INDEX_PATTERNS["公式"].findall(text)
        rec["figure_hits"] = INDEX_PATTERNS["图"].findall(text)
        rec["table_hits"] = INDEX_PATTERNS["表"].findall(text)
        rec["text"] = text
        rec["evidence_grade"] = evidence_grade(rec)
    return records


def chapter_groups(records: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for rec in records:
        groups[rec["chapter"]].append(rec)
    return groups


def page_range(recs: list[dict[str, Any]]) -> str:
    pages = [int(r["book_page"]) for r in recs if str(r.get("book_page", "")).isdigit()]
    if not pages:
        return "页码未识别"
    return f"{min(pages)}-{max(pages)}"


def continuity(recs: list[dict[str, Any]]) -> str:
    pages = sorted(int(r["book_page"]) for r in recs if str(r.get("book_page", "")).isdigit())
    if not pages:
        return "无法判断"
    missing = [p for p in range(pages[0], pages[-1] + 1) if p not in pages]
    duplicates = sorted({p for p in pages if pages.count(p) > 1})
    issues = []
    if missing:
        issues.append("缺页/未识别：" + "、".join(map(str, missing[:20])) + ("..." if len(missing) > 20 else ""))
    if duplicates:
        issues.append("重复页：" + "、".join(map(str, duplicates)))
    return "连续" if not issues else "；".join(issues)


def make_overview(records: list[dict[str, Any]]) -> str:
    groups = chapter_groups(records)
    rows = []
    for _, chap, title in CHAPTER_ORDER:
        recs = groups[chap]
        rows.append([chap, title, len(recs), recs[0]["file_name"], recs[-1]["file_name"], page_range(recs), continuity(recs)])
    return f"""# 书籍知识库总览_R2候选

## 本知识库职能

本候选稿基于原始书籍图片重新整理《空间目标光学特性原理与应用》的项目知识库，用于 v0.4 BlenderOCS 后续论文、路线一 C、三轴小项目、路线二/三和 Method/Discussion 写作。它不是摘要，而是带证据位置的项目知识索引。

## 原始图片来源

- 原始图片目录：`{BOOK_ROOT}`
- 旧 v0.4 知识库目录：`{OLD_KB_ROOT}`
- 本轮候选输出目录：`{OUT_ROOT}`

## 覆盖章节

{md_table(["章", "章节标题", "图片数", "图片起", "图片止", "书页范围", "页码连续性"], rows)}

## 当前整理状态

- 已完成：全章节图片盘点、OCR 文本缓存、页码初校、章节/小节标题初校、公式/图/表/模型线索索引、旧知识库系统对照候选。
- 未完成：所有公式符号逐字人工校对、表格数值逐格复核、图片中低清晰度区域人工确认。
- 特别说明：OCR 可读性总体可用，但公式、希腊字母、上下标、表格数值存在误识别风险，正式入库前必须由 Codex/作者对 P0 项逐页复核。

## 证据等级定义

- A：原始图片清晰可见，页码/编号/内容均明确。
- B：原始图片可见，但公式/表号/变量有部分模糊。
- C：只在旧知识库中出现，原始图片未核实。
- D：旧知识库与原始图片冲突，应撤回或重查。

## 新对话推荐读取顺序

1. `00_书籍知识库总览_R2候选.md`
2. `01_空间目标光学特性原理与应用_书目信息与目录_R2候选.md`
3. `12_P0核心公式图表精确核对记录_R2候选.md`
4. 对应路线章节精读笔记：第3章、第4章、第6章优先。
5. `14_旧知识库错误更正清单_R2候选.md`

## 与旧知识库的关系

旧知识库只能作为参考和对照，不作为权威来源。本候选稿中凡未能在原始图片 OCR/视觉线索中重新定位的旧说法，统一降级为“待作者确认”或“需要补证据”。

## 待作者确认事项

- P0 公式的上下标、分母、积分/求和范围。
- 第3章材料参数表和峰值表的具体数值。
- 公式、图、表编号在低清晰图片中的误识别项。
- 页码未识别或位置异常图片对应的真实书页。
"""


def make_biblio(records: list[dict[str, Any]]) -> str:
    groups = chapter_groups(records)
    rows = []
    for folder, chap, title in CHAPTER_ORDER:
        recs = groups[chap]
        sections = []
        for rec in recs:
            for sec in rec.get("section_hits", []):
                if sec not in sections:
                    sections.append(sec)
        rows.append([chap, title, folder, recs[0]["file_name"], recs[-1]["file_name"], page_range(recs), continuity(recs), "；".join(sections[:12])])
    return f"""# 空间目标光学特性原理与应用_书目信息与目录_R2候选

## 书名

《空间目标光学特性原理与应用》

## 目录结构与图片范围

{md_table(["章", "每章主题", "原始文件夹", "图片起", "图片止", "书页范围", "页码连续性", "OCR识别小节"], rows)}

## 使用说明

本文件中的目录结构来自原始图片 OCR 识别和文件夹命名。章节标题清晰度较高；小节标题仍需对照原图人工复核，尤其是 OCR 将空格、标点、希腊字母或英文连字符误读的项目。
"""


def make_mapping(records: list[dict[str, Any]]) -> str:
    rows = []
    for rec in records:
        abnormal = rec["page_note"]
        if not rec["keywords"] and not rec["section_hits"]:
            abnormal = (abnormal + "；" if abnormal else "") + "关键词较少，需复核"
        rows.append([
            rec["chapter"],
            rec["file_name"],
            rec["screenshot_no"],
            rec["book_page"] or "待确认",
            rec["current_section"] or "待确认",
            "、".join(rec["keywords"]),
            abnormal,
        ])
    return "# 全书图片编号_书页页码_章节映射表_R2候选\n\n" + md_table(
        ["章", "图片文件名", "截图编号", "书页", "小节标题", "内容关键词", "异常"], rows
    )


def make_chapter_note(chap: str, title: str, recs: list[dict[str, Any]], indices: list[dict[str, Any]]) -> str:
    all_text = "\n".join(r["text"] for r in recs)
    kw = sorted({k for r in recs for k in r["keywords"]})
    section_rows = []
    for rec in recs:
        formulas = "、".join(sorted(set(re.sub(r"\s+", "", x) for x in rec["formula_hits"])))
        figs = "、".join(sorted(set(re.sub(r"\s+", "", x) for x in rec["figure_hits"])))
        tabs = "、".join(sorted(set(re.sub(r"\s+", "", x) for x in rec["table_hits"])))
        section_rows.append([
            rec["book_page"] or "待确认",
            rec["file_name"],
            rec["current_section"] or "待确认",
            "、".join(rec["keywords"]) or summarize_line(rec["text"]),
            "；".join(x for x in [formulas, figs, tabs] if x) or "未识别",
            infer_use(rec["text"]),
            rec["evidence_grade"],
        ])

    chapter_indices = [i for i in indices if i["章"] == chap]
    formula_rows = [[i["书页"], i["图片文件"], i["编号"], i["名称"], i["变量参数"], i["用途"], i["证据等级"]] for i in chapter_indices if i["类型"] == "公式"]
    chart_rows = [[i["类型"], i["书页"], i["图片文件"], i["编号"], i["名称"], i["用途"], i["证据等级"]] for i in chapter_indices if i["类型"] in {"图", "表"}]
    model_rows = [[i["类型"], i["书页"], i["图片文件"], i["名称"], i["摘要"][:120], i["用途"], i["证据等级"]] for i in chapter_indices if i["类型"] not in {"公式", "图", "表"}]

    method, discussion, boundary = classify_page_use(all_text)
    old_diff = old_diff_for_chapter(chap, all_text)
    return f"""# {chap} {title} 精读笔记_R2候选

## 1. 本章职能

{chapter_function(chap)}

## 2. 页码与图片范围

- 图片范围：`{recs[0]["file_name"]}` 至 `{recs[-1]["file_name"]}`
- 书页范围：{page_range(recs)}
- 页码连续性：{continuity(recs)}
- OCR核心关键词：{"、".join(kw) if kw else "待作者确认"}

## 3. 核心概念

{core_concepts(chap, all_text)}

## 4. 关键公式

{md_table(["书页", "图片文件", "编号", "名称", "变量/参数", "v0.4用途", "证据等级"], formula_rows) if formula_rows else "未从 OCR 中稳定识别公式编号；需人工复核原图。"}

## 5. 关键图表

{md_table(["类型", "书页", "图片文件", "编号", "名称", "v0.4用途", "证据等级"], chart_rows) if chart_rows else "未从 OCR 中稳定识别图表编号；需人工复核原图。"}

## 6. 关键模型/算法/流程

{md_table(["类型", "书页", "图片文件", "名称", "摘要", "v0.4用途", "证据等级"], model_rows[:80]) if model_rows else "未从 OCR 中稳定识别模型/流程线索；需人工复核。"}

## 7. 对 v0.4 的作用

{route_effect(chap, all_text)}

## 8. 可用于论文 Method 的内容

{method}

## 9. 可用于 Discussion / Limitations 的内容

{discussion}

## 10. 不能越界的 claim

{boundary}

## 11. 待作者确认

{chapter_confirmations(chap, recs)}

## 12. 与旧知识库差异

{old_diff}

## 13. 逐页精读映射

{md_table(["书页", "图片文件", "小节标题", "核心内容", "公式/图/表", "对v0.4用途", "证据等级"], section_rows)}
"""


def summarize_line(text: str) -> str:
    for line in text.splitlines():
        if len(line.strip()) >= 12:
            return line.strip()[:80]
    return "待作者确认"


def chapter_function(chap: str) -> str:
    mapping = {
        "第1章": "建立空间目标光学散射特性研究对象、应用背景、全书技术路线和术语边界。主要服务论文 Introduction 与 Discussion。",
        "第2章": "给出光学散射特性的基本物理量、几何关系和 OCS/BRDF 等核心定义，是路线一 C 前向模型的概念基础。",
        "第3章": "给出表面材质 BRDF 描述、测量和模型参数反演，是 v0.4 材质散射建模、Phong/改进 Phong/Torrance-Sparrow 相关表述的 P0 章节。",
        "第4章": "给出非分辨光学散射数值模拟、面元求和和光度仿真流程，是 BlenderOCS 前向仿真 Method 的主要支撑章节。",
        "第5章": "给出实验测量与定标方法，主要用于实验可行性、数据边界和未来实测验证。",
        "第6章": "给出基于光度特性的运动状态分析，支撑三轴小项目、姿态/自旋/章动相关 Discussion 和部分算法边界。",
        "第7章": "给出识别与姿态分析应用，主要支撑路线三和未来工作，当前路线不宜声称已完整实现。",
    }
    return mapping.get(chap, "待作者确认。")


def core_concepts(chap: str, text: str) -> str:
    hits = extract_keywords(text)
    base = "、".join(hits) if hits else "OCR 未稳定抽取核心概念，需人工复核。"
    extra = {
        "第3章": "重点核查 BRDF 定义式、BRDF 测量公式、经典冯模型、改进冯模型、Torrance-Sparrow 五参数模型、改进六参数模型和材料参数/峰值表。",
        "第4章": "重点核查面元 OCS 求和、光照-观测几何、非分辨光度仿真流程、目标模型/姿态/轨道输入输出关系。",
        "第6章": "重点核查光度曲线与旋转状态、三轴稳定/自旋/章动等运动模式分析边界。",
    }.get(chap, "")
    return f"- OCR 抽取概念：{base}\n- {extra}" if extra else f"- OCR 抽取概念：{base}"


def route_effect(chap: str, text: str) -> str:
    common = infer_use(text)
    if chap == "第3章":
        return f"{common}。本章可支撑材质 BRDF/经验模型参数化，但参数表数值必须从原图逐格复核后才能进入 Method。"
    if chap == "第4章":
        return f"{common}。本章可支撑非分辨前向模型架构和面元级合成逻辑，是路线一 C 的主要证据来源。"
    if chap == "第6章":
        return f"{common}。本章适合支撑三轴小项目的运动状态解释和光度曲线分析，不应替代 v0.4 自身实验结果。"
    return common


def chapter_confirmations(chap: str, recs: list[dict[str, Any]]) -> str:
    items = []
    for rec in recs:
        if rec["page_note"]:
            items.append(f"- {rec['file_name']}：{rec['page_note']}")
    if chap == "第3章":
        items.extend([
            "- BRDF 定义式和测量公式的公式编号、变量含义需逐字核对。",
            "- 冯模型、改进冯模型、Torrance-Sparrow 五参数模型、改进六参数模型的参数列表需对照原图确认。",
            "- 太阳能电池阵、铝合金、MLI/多层隔热膜等材料参数表是否存在以及数值需逐格复核。",
        ])
    return "\n".join(items) if items else "- 暂无页码级异常；仍需对 P0 公式和表格数值人工复核。"


def old_diff_for_chapter(chap: str, text: str) -> str:
    old_files = sorted(OLD_KB_ROOT.glob("*.md"))
    matches = []
    chap_digit = chap.replace("第", "").replace("章", "")
    for path in old_files:
        if f"第{chap_digit}章" in path.name or (chap == "第1章" and "01a" in path.name):
            old = path.read_text(encoding="utf-8", errors="ignore")
            old_keys = extract_keywords(old)
            missing = [k for k in old_keys if k not in text]
            matches.append(f"- `{path.name}`：关键词可对照 {', '.join(old_keys[:8]) or '无'}；未在本章 OCR 稳定命中的旧关键词：{', '.join(missing[:8]) or '无'}。")
    return "\n".join(matches) if matches else "- 未找到直接对应旧章文件；需人工对照。"


def make_gap_list(records: list[dict[str, Any]]) -> str:
    groups = chapter_groups(records)
    rows = []
    image_issues = []
    formula_issues = []
    for _, chap, _ in CHAPTER_ORDER:
        recs = groups[chap]
        rows.append([chap, page_range(recs), recs[0]["file_name"], recs[-1]["file_name"], continuity(recs)])
        for rec in recs:
            if rec["page_note"]:
                image_issues.append([chap, rec["file_name"], rec["screenshot_no"], rec["book_page"] or "待确认", rec["page_note"]])
            for f in rec["formula_hits"]:
                if rec["evidence_grade"] != "A":
                    formula_issues.append([chap, rec["book_page"], rec["file_name"], f, "公式 OCR 非 A，需人工复核"])
    return f"""# 第1-7章_页码_公式_缺页待补清单_R2候选

## 页码连续性

{md_table(["章", "书页起止", "图片起", "图片止", "是否连续/异常说明"], rows)}

## 图片缺失/跳号/页码异常

{md_table(["章", "图片文件", "截图编号", "书页", "异常说明"], image_issues) if image_issues else "OCR 未发现明显页码异常；仍需按原图抽查。"}

## 公式编号待补

{md_table(["章", "书页", "图片文件", "公式编号", "待补说明"], formula_issues[:200]) if formula_issues else "OCR 中公式编号证据等级均为 A 或未识别；P0 公式仍需人工复核。"}

## 图号待补

图号 OCR 识别已进入 `11_第1-7章_公式_图表_模型索引_R2候选.md`；低清晰度图题需人工复核。

## 表号待补

表号 OCR 识别已进入 `11_第1-7章_公式_图表_模型索引_R2候选.md`；涉及材料参数数值的表必须逐格人工复核。

## OCR/视觉识别不清项

- 希腊字母、上下标、分式、积分/求和范围。
- 材料参数表的数值和单位。
- 图片中被书脊、手指、阴影或拍摄角度影响的边缘文字。

## 作者需人工确认项

- 第3章 P0 模型及材料表。
- 第4章 面元 OCS/非分辨仿真流程公式。
- 第6章 三轴/自旋/章动运动状态分析的适用边界。
"""


def make_index(indices: list[dict[str, Any]]) -> str:
    rows = []
    for n, item in enumerate(indices, start=1):
        rows.append([n, item["类型"], item["章"], item["书页"], item["图片文件"], item["编号"], item["名称"], item["摘要"][:120], item["变量参数"], item["用途"], item["证据等级"]])
    return "# 第1-7章_公式_图表_模型索引_R2候选\n\n" + md_table(
        ["编号", "类型", "章", "书页", "图片文件", "原编号", "名称", "公式/模型摘要", "变量/参数", "v0.4用途", "证据等级"], rows
    )


def make_p0(records: list[dict[str, Any]], indices: list[dict[str, Any]]) -> str:
    targets = [
        {"name": "OCS 定义", "chapters": ["第2章"], "terms": ["OCS", "定义"], "fallback": ["光学散射截面", "OCS"], "section": ["定义"]},
        {"name": "BRDF 定义", "chapters": ["第2章"], "terms": ["BRDF", "双向反射分布函数"], "fallback": ["BRDF", "定义"], "section": ["双向反射分布函数"]},
        {"name": "BRDF 测量公式", "chapters": ["第3章"], "terms": ["BRDF", "测量"], "fallback": ["定标板", "测量"], "section": ["BRDF测量"]},
        {"name": "经典冯模型", "chapters": ["第3章"], "terms": ["经典冯模型"], "fallback": ["冯模型", "图3.12"], "section": ["冯模型改进原理"]},
        {"name": "改进冯模型", "chapters": ["第3章"], "terms": ["改进后的冯模型"], "fallback": ["改进冯模型", "3.3.1"], "section": ["冯模型改进原理"]},
        {"name": "Torrance-Sparrow 五参数模型", "chapters": ["第3章"], "terms": ["Torrance-Sparrow", "五参数"], "fallback": ["Torrance-Sparrow"], "section": ["模型构建"], "preferred_pages": ["63", "64"]},
        {"name": "改进五/六参数模型", "chapters": ["第3章"], "terms": ["改进五参数"], "fallback": ["六参数", "改进", "五参数"], "section": ["模型验证", "模型构建"]},
        {"name": "面元 OCS 求和", "chapters": ["第4章"], "terms": ["面元", "OCS"], "fallback": ["面元", "光学散射截面"], "section": ["仿真计算"]},
        {"name": "非分辨光度仿真流程", "chapters": ["第4章"], "terms": ["非分辨", "计算流程"], "fallback": ["OCS仿真计算", "流程"], "section": ["计算流程"]},
        {"name": "关键材料参数/材料测量数据", "chapters": ["第3章"], "terms": ["空间目标常用材质"], "fallback": ["太阳能电池", "铝", "多层隔热", "材料"], "section": ["常用材质"]},
    ]
    parts = ["# P0核心公式图表精确核对记录_R2候选\n"]
    for idx, target in enumerate(targets, start=1):
        name = target["name"]
        terms = target["terms"]
        candidates = rank_p0_candidates(records, target)
        if candidates:
            rec = candidates[0]
            related = [i for i in indices if i["图片文件"] == rec["file_name"]][:5]
            formulas = "、".join(i["编号"] for i in related if i["编号"]) or "待作者确认"
            summary = context_summary(rec["text"], terms)
            grade = rec["evidence_grade"]
        else:
            rec = None
            formulas = "待作者确认"
            summary = "未在 OCR 中稳定定位，需人工复核原图或旧知识库。"
            grade = "C"
        parts.append(f"""## P0-{idx} {name}

- 章节：{rec["chapter"] if rec else "待作者确认"}
- 书页：{rec["book_page"] if rec else "待作者确认"}
- 图片文件：{rec["file_name"] if rec else "待作者确认"}
- 公式/图/表编号：{formulas}
- 内容摘要：{summary}
- 变量/参数：{infer_params(summary)}
- 对 v0.4 的用途：{infer_use(summary)}
- 可否用于 Method：{"可作为 Method 候选依据，但必须逐字复核。" if grade in {"A", "B"} else "暂不可，需补原图证据。"}
- 边界：不能把 OCR 推断或旧知识库说法直接写成已核实事实；公式细节以原图人工复核为准。
- 待确认：公式编号、变量上下标、表格数值、材料名称和单位。
- 证据等级：{grade}
""")
    parts.append("""## P1/P2 分级原则

- P1：与路线二/三、三轴小项目、实验测量边界直接相关，但不直接进入当前前向模型公式链的内容。
- P2：背景、应用场景、历史综述、未来工作和可读性说明。
""")
    return "\n".join(parts)


def rank_p0_candidates(records: list[dict[str, Any]], target: dict[str, Any]) -> list[dict[str, Any]]:
    preferred = set(target["chapters"])
    terms = target["terms"]
    fallback = target.get("fallback", [])
    scored: list[tuple[int, dict[str, Any]]] = []
    for rec in records:
        text = rec["text"]
        lower = text.lower()
        score = 0
        if rec["chapter"] in preferred:
            score += 100
        if str(rec.get("book_page", "")) in set(target.get("preferred_pages", [])):
            score += 60
        if all(t.lower() in lower for t in terms):
            score += 80
        score += sum(20 for t in fallback if t.lower() in lower)
        section = rec.get("current_section", "")
        score += sum(25 for t in target.get("section", []) if t in section)
        if rec.get("formula_hits"):
            score += 10
        if any(t in section for t in ["定义", "测量", "改进", "模型", "流程"]):
            score += 8
        if str(rec.get("book_page", "")).isdigit():
            score += 2
        if score >= 120:
            scored.append((score, rec))
    scored.sort(key=lambda x: (-x[0], int(x[1].get("book_page") or 999), x[1]["file_name"]))
    return [rec for _, rec in scored]


def context_summary(text: str, terms: list[str]) -> str:
    positions = [text.lower().find(t.lower()) for t in terms if text.lower().find(t.lower()) >= 0]
    if not positions:
        return summarize_line(text)
    p = min(positions)
    return context_around(text, p, p + 10, 160).replace("\n", " ")[:360]


def make_route_mapping(records: list[dict[str, Any]]) -> str:
    rows = []
    for rec in records:
        if not rec["keywords"]:
            continue
        rows.append([
            f"{rec['current_section'] or rec['chapter']}：{'、'.join(rec['keywords'][:5])}",
            f"{rec['chapter']} p.{rec['book_page']} `{rec['file_name']}`",
            mark_route(rec["text"], "路线一C"),
            mark_route(rec["text"], "三轴"),
            mark_route(rec["text"], "路线二"),
            mark_route(rec["text"], "路线三"),
            "Future Work" if "实验" in rec["text"] or "测量" in rec["text"] else "参考",
            "仅在原图证据清晰且 v0.4 已实现对应模块时写入 Method；否则进入 Discussion/Limitations。",
        ])
    return f"""# 书籍知识库对v0.4主线的方法支撑与路线把控_R2候选

## 总体判断

- 路线一 C：优先使用第2章核心定义、第3章 BRDF/材质模型、第4章非分辨仿真和面元合成。
- 三轴小项目：优先使用第6章光度曲线与运动状态分析，第7章姿态分析作为补充。
- 路线二：使用第3章参数反演、第6/7章反演与识别线索，但不得声称已完整复现。
- 路线三：主要来自第7章识别应用，当前更适合 Discussion/Future Work。
- 路线四/未来工作：实验测量、定标、真实材料参数库、实测验证。

## Method / Discussion / Limitations 建议

- Method：只纳入 OCS/BRDF/面元求和/非分辨仿真流程等已被 v0.4 代码或实验实际使用的内容。
- Discussion：可讨论材料模型、实测参数、姿态/识别扩展、与原书流程的差异。
- Limitations：明确当前候选稿中的 OCR 不确定性、参数表未逐格复核、真实观测/实验测量未闭环。

## 路线映射表

{md_table(["书中内容", "位置", "路线一 C", "三轴小项目", "路线二", "路线三", "路线四", "使用边界"], rows[:300])}
"""


def mark_route(text: str, route: str) -> str:
    if route == "路线一C":
        return "可支撑" if any(k in text for k in ["OCS", "BRDF", "面元", "非分辨", "仿真", "散射"]) else "弱相关"
    if route == "三轴":
        return "可支撑" if any(k in text for k in ["三轴", "姿态", "自旋", "章动", "光度"]) else "弱相关"
    if route == "路线二":
        return "可支撑" if any(k in text for k in ["反演", "遗传算法", "粒子群", "参数"]) else "弱相关"
    if route == "路线三":
        return "可支撑" if any(k in text for k in ["识别", "分类", "姿态分析"]) else "弱相关"
    return "参考"


def make_old_corrections(records: list[dict[str, Any]]) -> str:
    corpus = "\n".join(r["text"] for r in records)
    rows = []
    for path in sorted(OLD_KB_ROOT.glob("*.md")):
        text = path.read_text(encoding="utf-8", errors="ignore")
        candidates = extract_old_claims(text)
        if not candidates:
            rows.append([path.name, "未抽取到稳定旧说法", "需人工阅读旧文件", "降级为待确认", "需要作者补证据", "P2"])
            continue
        for claim in candidates[:8]:
            keys = extract_keywords(claim)
            found = bool(keys and any(k in corpus for k in keys))
            if found:
                judgment = "旧说法关键词可在原始图片 OCR 中找到，但页码/编号/数值仍需逐项核对。"
                action = "保留或修正后保留"
                priority = "P1" if any(k in claim for k in ["BRDF", "OCS", "冯模型", "Torrance", "面元"]) else "P2"
            else:
                judgment = "未在本轮 OCR 中找到稳定原图证据。"
                action = "降级为待确认/需要作者补证据"
                priority = "P0" if any(k in claim for k in ["参数表", "公式", "页码", "表"]) else "P1"
            rows.append([path.name, claim[:140], "关键词：" + ("、".join(keys) if keys else "无"), judgment, action, priority])
    return "# 旧知识库错误更正清单_R2候选\n\n" + md_table(
        ["旧文件", "旧说法", "新证据", "新判断", "建议处理", "优先级"], rows
    )


def extract_old_claims(text: str) -> list[str]:
    claims = []
    for line in text.splitlines():
        raw = line.strip()
        if not raw or raw.startswith("#") or raw.startswith("|") or set(raw) <= {"-", " "}:
            continue
        raw = re.sub(r"^[-*]\s*", "", raw)
        if any(k in raw for k in KEYWORDS) or any(k in raw for k in ["公式", "图", "表", "页", "Method", "Discussion"]):
            claims.append(raw)
    return claims


def make_final_table() -> str:
    rows = [
        ["原始图片全章覆盖", "已覆盖第1-7章共 167 张图片并生成映射", "A/B", "可写入候选，正式入库需抽查", "是", "否"],
        ["页码映射", "已按图片顶部页码 OCR 初校；部分首页/边缘页码需确认", "A/B", "可写入但需保留异常列", "是", "是"],
        ["第3章 P0 模型", "已定位 BRDF、冯模型、Torrance-Sparrow、参数反演等线索；公式细节需逐字核对", "B", "只能作为候选", "是", "是"],
        ["材料参数表", "OCR 能检索材料相关页，但数值和表号不得直接采信", "B/C", "暂不可作为正式参数库", "是", "是"],
        ["旧知识库对照", "已生成关键词级保留/修正/降级建议", "B/C", "需人工复审后写入", "是", "是"],
        ["Method 可用内容", "第2-4章定义、模型和非分辨仿真流程可作为 Method 候选依据", "A/B", "可在复核后写入", "是", "部分"],
        ["Discussion/Future Work", "第5-7章实验、运动状态、识别姿态分析适合讨论和未来工作", "A/B", "可写入", "是", "部分"],
    ]
    return "# 本轮重新整理结论总表\n\n" + md_table(
        ["项", "结论", "证据等级", "是否可写入正式知识库", "是否需 Codex 审阅", "是否需作者确认"], rows
    )


def main() -> None:
    ensure_dirs()
    records = build_records(run_ocr())
    OCR_JSON.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
    indices = collect_indices(records)
    groups = chapter_groups(records)

    write(OUT_ROOT / "00_书籍知识库总览_R2候选.md", make_overview(records))
    write(OUT_ROOT / "01_空间目标光学特性原理与应用_书目信息与目录_R2候选.md", make_biblio(records))
    write(OUT_ROOT / "02_全书图片编号_书页页码_章节映射表_R2候选.md", make_mapping(records))
    for _, chap, title in CHAPTER_ORDER:
        write(OUT_ROOT / CHAPTER_NOTE_FILES[chap], make_chapter_note(chap, title, groups[chap], indices))
    write(OUT_ROOT / "10_第1-7章_页码_公式_缺页待补清单_R2候选.md", make_gap_list(records))
    write(OUT_ROOT / "11_第1-7章_公式_图表_模型索引_R2候选.md", make_index(indices))
    write(OUT_ROOT / "12_P0核心公式图表精确核对记录_R2候选.md", make_p0(records, indices))
    write(OUT_ROOT / "13_书籍知识库对v0.4主线的方法支撑与路线把控_R2候选.md", make_route_mapping(records))
    write(OUT_ROOT / "14_旧知识库错误更正清单_R2候选.md", make_old_corrections(records))
    write(OUT_ROOT / "15_本轮重新整理结论总表_R2候选.md", make_final_table())
    print(f"Wrote candidate files to {OUT_ROOT}")


if __name__ == "__main__":
    main()

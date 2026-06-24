# -*- coding: utf-8 -*-
from __future__ import annotations

from pathlib import Path


BASE = Path(r"D:\我的文件\研究生学术\光学项目\0506新\项目重启_v0.4_BlenderOCS\06_书籍知识库_R2-Codex修正版_2026-06-23")


def scan(files: list[Path], terms: list[str]) -> list[tuple[str, int, str]]:
    hits: list[tuple[str, int, str]] = []
    for path in files:
        for lineno, line in enumerate(path.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
            if any(term in line for term in terms):
                hits.append((path.name, lineno, line[:260]))
    return hits


def main() -> None:
    md_files = sorted(BASE.glob("*.md"))
    focused = [p for p in md_files if p.name.startswith(("05_", "11_", "13_"))]
    positive_files = [p for p in md_files if p.name.startswith(("05_", "11_", "12_", "13_", "15_"))]
    print(f"base_exists={BASE.exists()} md_count={len(md_files)} focused={[p.name for p in focused]}")

    checks = [
        (
            "bad_table_positive_files",
            positive_files,
            ["表3.1（OCR修正）", "OCR曾误作表3.1", "表3.14种", "材料参数系数表"],
        ),
        (
            "seq_051113",
            focused,
            ["1709", "1710", "1711", "1712", "1713", "1714", "1715", "1716", "3.3.1"],
        ),
        (
            "route_051113",
            focused,
            ["Torrance-Sparrow", "五参数", "六参数", "路线一C/前向模型", "路线一 C"],
        ),
    ]

    for label, files, terms in checks:
        hits = scan(files, terms)
        print(f"## {label}: {len(hits)}")
        for name, lineno, line in hits[:80]:
            print(f"{name}:{lineno}: {line}")

    a_files = [p for p in md_files if p.name.startswith(("05_", "11_"))]
    a_hits = []
    for path in a_files:
        for lineno, line in enumerate(path.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
            if line.rstrip().endswith("| A |"):
                a_hits.append((path.name, lineno, line[:260]))
    print(f"## evidence_A_05_11: {len(a_hits)}")
    for name, lineno, line in a_hits[:80]:
        print(f"{name}:{lineno}: {line}")


if __name__ == "__main__":
    main()

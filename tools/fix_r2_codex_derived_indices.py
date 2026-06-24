#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修正 R2-Codex 修正版派生索引一致性问题

依据：06_书籍知识库_R2-Codex修正版_2026-06-23/17_Codex审阅_R2修正版派生索引一致性问题清单.md

主要修正：
1. 文件13：p63-p67 从 3.3.1 更正为 3.4
2. 文件05：表3.1替换污染清理
3. 文件05：证据等级从 A 降为 B
4. 文件05：p63-p70 从路线一C主线移出
5. 文件11：同步修正派生索引

执行时间：2026-06-23
"""

import os
import sys
import shutil
from pathlib import Path

# 设置标准输出为UTF-8
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 源目录和目标目录
SRC_DIR = Path(r"d:\我的文件\研究生学术\光学项目\0506新\项目重启_v0.4_BlenderOCS\06_书籍知识库_R2-Codex修正版_2026-06-23")
OUTPUT_DIR = SRC_DIR  # 直接在原目录修改

def fix_file_13_p63_p67_section():
    """修正文件13中 p63-p67 的小节归属"""
    file_path = SRC_DIR / "13_书籍知识库对v0.4主线的方法支撑与路线把控_R2候选.md"

    print(f"修正文件13：{file_path}")

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 修正 p63 / 1709
    content = content.replace(
        "| 3.3.1 冯模型改进原理及方法：BRDF、冯模型、Torrance、Sparrow、面元 | 第3章 p.63 `微信图片_20260618141949_1709_74.png` | 可支撑 | 弱相关 | 可支撑 | 弱相关 | 参考 |",
        "| 3.4 基于Torrance-Sparrow模型的改进BRDF经验模型：BRDF、Torrance、Sparrow、面元 | 第3章 p.63 `微信图片_20260618141949_1709_74.png` | 参考 | 弱相关 | 弱相关 | 弱相关 | Discussion/Future Work |"
    )

    # 修正 p64 / 1710
    content = content.replace(
        "| 3.3.1 冯模型改进原理及方法：BRDF、Torrance、Sparrow、面元、测量 | 第3章 p.64 `微信图片_20260618141957_1710_74.png` | 可支撑 | 弱相关 | 可支撑 | 弱相关 | Future Work |",
        "| 3.4.1 Torrance-Sparrow五参数模型：BRDF、Torrance、Sparrow、式(3.18)、式(3.19) | 第3章 p.64 `微信图片_20260618141957_1710_74.png` | 参考 | 弱相关 | 弱相关 | 弱相关 | B2后续BRDF对照分支/Discussion |"
    )

    # 修正 p65 / 1711
    content = content.replace(
        "| 3.3.1 冯模型改进原理及方法：BRDF、Torrance、Sparrow、反演、测量 | 第3章 p.65 `微信图片_20260618142006_1711_74.png` | 可支撑 | 弱相关 | 可支撑 | 弱相关 | Future Work |",
        "| 3.4.1 五参数模型局限与改进推导：BRDF、Torrance、Sparrow、反演 | 第3章 p.65 `微信图片_20260618142006_1711_74.png` | 参考 | 弱相关 | 弱相关 | 弱相关 | B2后续BRDF对照分支/Discussion |"
    )

    # 修正 p66 / 1712
    content = content.replace(
        "| 3.3.1 冯模型改进原理及方法：BRDF、冯模型、Torrance、Sparrow、面元 | 第3章 p.66 `微信图片_20260618142017_1712_74.png` | 可支撑 | 弱相关 | 可支撑 | 弱相关 | 参考 |",
        "| 3.4.1 五参数模型局限与改进推导：BRDF、Torrance、Sparrow、面元 | 第3章 p.66 `微信图片_20260618142017_1712_74.png` | 参考 | 弱相关 | 弱相关 | 弱相关 | B2后续BRDF对照分支/Discussion |"
    )

    # 修正 p67 / 1713
    content = content.replace(
        "| 3.3.1 冯模型改进原理及方法：散射 | 第3章 p.67 `微信图片_20260618142024_1713_74.png` | 可支撑 | 弱相关 | 可支撑 | 弱相关 | 参考 |",
        "| 3.4.1 改进六参数经验模型：式(3.23) | 第3章 p.67 `微信图片_20260618142024_1713_74.png` | 参考 | 弱相关 | 弱相关 | 弱相关 | B2后续BRDF对照分支/Discussion |"
    )

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print("[OK] 文件13修正完成：p63-p67小节归属已更新")

def fix_file_05_table_and_sections():
    """修正文件05中的表3.1替换污染和p63-p70路线映射"""
    file_path = SRC_DIR / "05_第3章_空间目标表面材质散射特性建模_精读笔记_R2候选.md"

    print(f"修正文件05：{file_path}")

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 修正表3.1替换污染
    content = content.replace(
        "表3.1（OCR修正）",
        "表3.1"
    )
    content = content.replace(
        "表3.1：4种空间目标常用材质的BRDF峰值变化（OCR曾误作表3.1（OCR修正））",
        "表3.1：4种空间目标常用材质的BRDF峰值变化"
    )

    # 修正 p63 小节标题
    content = content.replace(
        "#### p63 / 1709 - 3.3.1 冯模型改进原理及方法",
        "#### p63 / 1709 - 3.4 基于Torrance-Sparrow模型的改进BRDF经验模型"
    )

    # 修正 p64 小节标题
    content = content.replace(
        "#### p64 / 1710 - 3.3.1 冯模型改进原理及方法",
        "#### p64 / 1710 - 3.4.1 Torrance-Sparrow五参数模型"
    )

    # 修正 p65 小节标题
    content = content.replace(
        "#### p65 / 1711 - 3.3.1 冯模型改进原理及方法",
        "#### p65 / 1711 - 3.4.1 五参数模型局限与改进推导"
    )

    # 修正 p66 小节标题
    content = content.replace(
        "#### p66 / 1712 - 3.3.1 冯模型改进原理及方法",
        "#### p66 / 1712 - 3.4.1 五参数模型局限与改进推导"
    )

    # 修正 p67 小节标题
    content = content.replace(
        "#### p67 / 1713 - 3.3.1 冯模型改进原理及方法",
        "#### p67 / 1713 - 3.4.1 改进六参数经验模型"
    )

    # 将 p63-p70 的路线一C标注改为 B2后续分支
    # 这需要逐行处理，将包含 1709-1716 且有 "路线一C/前向模型" 的行改为 "B2后续BRDF对照分支/Discussion"
    lines = content.split('\n')
    modified_lines = []

    for line in lines:
        # 检查是否是 p63-p70 相关的表格行
        if any(f"171{i}" in line for i in range(9, 17)):  # 1709-1716
            if "路线一C/前向模型" in line or "路线一 C" in line:
                line = line.replace("路线一C/前向模型", "B2后续BRDF对照分支/Discussion")
                line = line.replace("路线一 C", "B2后续分支")
            # 将证据等级 A 降为 B
            if "| A |" in line:
                line = line.replace("| A |", "| B |")

        modified_lines.append(line)

    content = '\n'.join(modified_lines)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print("[OK] 文件05修正完成：表3.1清理、p63-p70小节标题和路线映射已更新")

def fix_file_11_derived_index():
    """修正文件11大索引中的派生条目"""
    file_path = SRC_DIR / "11_第1-7章_公式_图表_模型索引_R2候选.md"

    print(f"修正文件11：{file_path}")

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 将 1709-1716 相关条目的 3.3.1 改为 3.4 / 3.4.1 / 3.4.2
    lines = content.split('\n')
    modified_lines = []

    for line in lines:
        # 1709: 3.3.1 -> 3.4
        if "1709" in line and "3.3.1" in line:
            line = line.replace("3.3.1", "3.4")

        # 1710-1713: 3.3.1 -> 3.4.1
        if any(f"171{i}" in line for i in [0, 1, 2, 3]) and "3.3.1" in line:
            line = line.replace("3.3.1", "3.4.1")

        # 1714-1716: 保持 3.4.2

        # 将 p63-p70 相关条目的路线一C标注改为 B2后续分支
        if any(f"171{i}" in line for i in range(9, 17)):
            if "路线一C" in line or "路线一 C" in line:
                line = line.replace("路线一C", "B2后续BRDF对照分支")
                line = line.replace("路线一 C", "B2后续分支")
            # 将证据等级 A 降为 B
            if "| A |" in line:
                line = line.replace("| A |", "| B |")

        modified_lines.append(line)

    content = '\n'.join(modified_lines)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print("[OK] 文件11修正完成：1709-1716派生索引已同步更新")

def run_validation_checks():
    """运行验收检查"""
    print("\n" + "="*60)
    print("运行验收检查...")
    print("="*60 + "\n")

    print("注意：验收检查需要ripgrep(rg)工具。")
    print("请手动运行以下命令进行验收：")
    print()
    print("1. 检查表3.1替换污染：")
    print(f'   rg -n --glob "*.md" "表3\\.1（OCR修正）|OCR曾误作表3\\.1|表3\\.14种" "{SRC_DIR}"')
    print()
    print("2. 检查p63-p67小节归属：")
    print(f'   rg -n --glob "*.md" "1709.*3\\.3\\.1|1710.*3\\.3\\.1|1711.*3\\.3\\.1|1712.*3\\.3\\.1|1713.*3\\.3\\.1" "{SRC_DIR}"')
    print()
    print("3. 检查p63-p70路线一C标注：")
    print(f'   rg -n "171[0-6].*路线一C/前向模型|171[0-6].*路线一 C.*Method" "{SRC_DIR}/05_第3章_空间目标表面材质散射特性建模_精读笔记_R2候选.md"')
    print(f'   rg -n "171[0-6].*路线一C/前向模型|171[0-6].*路线一 C.*Method" "{SRC_DIR}/11_第1-7章_公式_图表_模型索引_R2候选.md"')
    print(f'   rg -n "171[0-6].*路线一C/前向模型|171[0-6].*路线一 C.*Method" "{SRC_DIR}/13_书籍知识库对v0.4主线的方法支撑与路线把控_R2候选.md"')
    print()
    print("="*60)
    print("验收检查说明完成")
    print("="*60)

def main():
    """主函数"""
    print("="*60)
    print("开始修正 R2-Codex 修正版派生索引一致性问题")
    print("="*60 + "\n")

    # 执行修正
    fix_file_13_p63_p67_section()
    print()

    fix_file_05_table_and_sections()
    print()

    fix_file_11_derived_index()
    print()

    # 运行验收检查
    run_validation_checks()

    print("\n✅ 所有修正已完成")
    print(f"修正后文件位于：{SRC_DIR}")

if __name__ == "__main__":
    main()

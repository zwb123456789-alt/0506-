#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Zotero v0.4 必读文献分析脚本（只读模式）
由于本地 API 限制，本脚本只进行分析和匹配，生成操作指南
"""

import os
import re
import sys
from pyzotero import zotero
from collections import defaultdict

# 设置输出编码为 UTF-8
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 初始化 Zotero 连接
z = zotero.Zotero('0', 'user', local=True)

# 项目配置
PROJECT_COLLECTION_KEY = 'IUI8GQFL'  # "光学项目"集合 key
PDF_DIR = r"D:\我的文件\研究生学术\光学项目\0506新\项目重启_v0.4_BlenderOCS\03_项目说明与规划材料\05_参考材料\03_文献与引用材料\papers"
REPORT_PATH = r"D:\我的文件\研究生学术\光学项目\0506新\项目重启_v0.4_BlenderOCS\03_项目说明与规划材料\05_参考材料\03_文献与引用材料\Zotero_v0.4必读文献整理报告.md"

# 子集合定义
READING_LIST_NAME = "v0.4_BlenderOCS_必读文献"
SUB_COLLECTIONS = [
    "01_可观测性_信息下界",
    "02_光变姿态反演_baseline",
    "03_真实光度_BRDF_亮度模型",
    "04_图像姿态_Sim2Real",
    "05_融合_多模态_置信一致性",
    "06_FutureWork_三轴_神经渲染_自监督"
]

# 必读文献分配清单
READING_ASSIGNMENTS = {
    "01_可观测性_信息下界": [
        "JOSAA_2003_Gerwe_Idell_orientation_Cramer_Rao.pdf",
        "ICML_2017_Guo_calibration_modern_neural_networks.pdf",
        "FnTML_2023_Angelopoulos_Bates_conformal_prediction_intro.pdf"
    ],
    "02_光变姿态反演_baseline": [
        "JGCD_2009_Wetterer_Jah_attitude_determination_light_curves.pdf",
        "TAES_2017_Piergentili_attitude_lightcurve_measurements.pdf",
        "Burton 2024.pdf",
        "Wang 2024.pdf",
        "ASR_2022_Clark_RSO_attitude_optical_property_light_curves.pdf",
        "JGCD_2014_Linares_shape_tracking_lightcurve_angles.pdf"
    ],
    "03_真实光度_BRDF_亮度模型": [
        "Fankhauser_2023_Satellite_Optical_Brightness_arXiv2305.11123.pdf",
        "lu2024_brdf_starlink.pdf",
        "yang2024_goniopolarimetric.pdf",
        "JGCD_2023_Dianetti_Crassidis_polarized_light_curves.pdf",
        "aerospace-13-00418-v2.pdf"
    ],
    "04_图像姿态_Sim2Real": [
        "dickinson2025_sim2real_6dof.pdf",
        "IEEEAero_2022_Park_SPEEDplus_spacecraft_pose_domain_gap.pdf",
        "ASR_2024_Park_DAmico_SPNv2_domain_gap_pose_estimation.pdf",
        "Acta_2023_Bechini_dataset_generation_validation_spacecraft_pose.pdf",
        "Acta_2021_PasqualettoCassinis_CNN_pose_tightly_loosely_coupled.pdf"
    ],
    "05_融合_多模态_置信一致性": [
        "TAES_2022_Rondao_ChiNet_multimodal_spacecraft_pose.pdf",
        "liu2024_visual_inertial_fusion.pdf",
        "Fusion_2014_Linares_space_object_classification_characterization_MMAE.pdf",
        "aerospace2025_joint_estimation.pdf",
        "marto2024_hyperspectral_lightcurve.pdf"
    ],
    "06_FutureWork_三轴_神经渲染_自监督": [
        "Kumar_2025_Light_curves_sequential_comparison_ActaAstronautica_10.1016-j.actaastro.2025.04.018.pdf",
        "AMOS_2024_deAndres_attitude_monitoring_three_axis_light_curves.pdf",
        "groves2025_selfsupervised_ssa.pdf",
        "behari2023_sundial.pdf",
        "AandA_2025_Tang_asteroid_shape_inversion_deep_learning.pdf",
        "AMOS_2019_Furfaro_shape_identification_light_curve_inversion.pdf"
    ]
}

# 标签映射
COLLECTION_TAGS = {
    "01_可观测性_信息下界": ["可观测性"],
    "02_光变姿态反演_baseline": ["光变反演"],
    "03_真实光度_BRDF_亮度模型": ["真实光度限制"],
    "04_图像姿态_Sim2Real": ["图像姿态baseline"],
    "05_融合_多模态_置信一致性": ["fusion负结果解释"],
    "06_FutureWork_三轴_神经渲染_自监督": ["future-work"]
}

def normalize_filename(filename):
    """标准化文件名用于匹配"""
    # 去掉扩展名
    name = os.path.splitext(filename)[0]
    # 转小写，去掉特殊字符
    name = re.sub(r'[^a-z0-9]', '', name.lower())
    return name

def extract_keywords(filename):
    """从文件名提取关键词"""
    name = os.path.splitext(filename)[0]
    # 提取年份
    year_match = re.search(r'(19|20)\d{2}', name)
    year = year_match.group(0) if year_match else None

    # 提取第一作者（通常在开头或下划线后）
    author_match = re.match(r'^([A-Z][a-z]+)', name)
    if not author_match:
        author_match = re.search(r'_([A-Z][a-z]+)_', name)
    author = author_match.group(1) if author_match else None

    # 提取主题关键词
    keywords = []
    topic_words = ['attitude', 'lightcurve', 'light_curve', 'pose', 'spacecraft',
                   'BRDF', 'calibration', 'sim2real', 'domain_gap', 'fusion',
                   'multimodal', 'inversion', 'Cramer', 'conformal', 'neural']
    for word in topic_words:
        if word.lower() in name.lower():
            keywords.append(word)

    return year, author, keywords

def match_pdf_to_item(pdf_filename, zotero_items):
    """匹配 PDF 文件到 Zotero 条目"""
    pdf_norm = normalize_filename(pdf_filename)
    pdf_year, pdf_author, pdf_keywords = extract_keywords(pdf_filename)

    matches = []
    for item in zotero_items:
        match_score = 0
        match_reasons = []

        # 检查附件文件名
        if 'data' in item:
            # 检查附件
            children = z.children(item['key'])
            for child in children:
                if child['data'].get('itemType') == 'attachment':
                    att_title = child['data'].get('title', '')
                    if normalize_filename(att_title) == pdf_norm:
                        match_score += 100
                        match_reasons.append('附件完全匹配')
                        break

        # 检查标题
        title = item['data'].get('title', '')
        title_norm = normalize_filename(title)

        if pdf_norm == title_norm:
            match_score += 90
            match_reasons.append('标题完全匹配')
        elif len(pdf_norm) > 15 and pdf_norm in title_norm:
            match_score += 70
            match_reasons.append('标题包含文件名')
        elif len(title_norm) > 15 and title_norm in pdf_norm:
            match_score += 70
            match_reasons.append('文件名包含标题')

        # 检查年份
        item_year = item['data'].get('date', '')
        if pdf_year and pdf_year in str(item_year):
            match_score += 20
            match_reasons.append(f'年份匹配({pdf_year})')

        # 检查作者
        creators = item['data'].get('creators', [])
        if pdf_author and creators:
            first_author_last = creators[0].get('lastName', '')
            if pdf_author.lower() in first_author_last.lower():
                match_score += 30
                match_reasons.append(f'作者匹配({pdf_author})')

        # 检查关键词
        for keyword in pdf_keywords:
            if keyword.lower() in title.lower():
                match_score += 5
                match_reasons.append(f'关键词匹配({keyword})')

        if match_score > 0:
            matches.append((match_score, match_reasons, item))

    # 按分数排序
    matches.sort(key=lambda x: x[0], reverse=True)
    return matches

def main():
    print("="*80)
    print("Zotero v0.4 必读文献分析（只读模式）")
    print("="*80)
    print()

    # 步骤 1: 读取 PDF 文件列表
    print("步骤 1: 读取 PDF 目录...")
    pdf_files = [f for f in os.listdir(PDF_DIR) if f.lower().endswith('.pdf')]
    print(f"✓ 找到 {len(pdf_files)} 个 PDF 文件")
    print()

    # 步骤 2: 读取 Zotero "光学项目"集合条目
    print("步骤 2: 读取 Zotero 集合...")
    try:
        items = z.collection_items_top(PROJECT_COLLECTION_KEY)
        print(f"✓ 读取到 {len(items)} 个 top-level 条目")
    except Exception as e:
        print(f"✗ 读取集合失败: {e}")
        return
    print()

    # 步骤 3: 建立匹配关系
    print("步骤 3: 匹配 PDF 文件到 Zotero 条目...")
    pdf_to_item = {}  # PDF文件名 -> (score, reasons, item)
    unmatched_pdfs = []
    ambiguous_matches = {}

    for pdf in pdf_files:
        matches = match_pdf_to_item(pdf, items)
        if len(matches) == 0:
            unmatched_pdfs.append(pdf)
        elif len(matches) == 1 or (len(matches) > 1 and matches[0][0] > matches[1][0] + 20):
            # 只有一个匹配，或者最佳匹配明显优于第二名
            pdf_to_item[pdf] = matches[0]
        else:
            # 有多个相近的匹配
            ambiguous_matches[pdf] = matches[:3]  # 保留前3个
            pdf_to_item[pdf] = matches[0]  # 使用得分最高的

    print(f"✓ 成功匹配: {len(pdf_to_item)}")
    print(f"  未匹配: {len(unmatched_pdfs)}")
    print(f"  有歧义: {len(ambiguous_matches)}")
    print()

    # 检查所有需要的文献是否都有匹配
    print("步骤 4: 检查必读文献匹配状态...")
    all_required_pdfs = []
    for pdf_list in READING_ASSIGNMENTS.values():
        all_required_pdfs.extend(pdf_list)

    missing_required = [pdf for pdf in all_required_pdfs if pdf not in pdf_to_item]
    print(f"✓ 必读文献: {len(all_required_pdfs)} 个")
    print(f"  已匹配: {len(all_required_pdfs) - len(missing_required)}")
    print(f"  缺失: {len(missing_required)}")
    print()

    print("="*80)
    print("生成报告...")
    print("="*80)

    # 生成报告
    with open(REPORT_PATH, 'w', encoding='utf-8') as f:
        f.write("# Zotero v0.4 必读文献整理报告\n\n")
        f.write(f"生成时间: 2026-06-29\n\n")
        f.write("**注意:** 由于 Zotero 本地 API 限制，本脚本只进行了分析和匹配。")
        f.write("集合创建和条目添加需要手动在 Zotero 中完成。\n\n")
        f.write("---\n\n")

        # 需要创建的集合结构
        f.write("## 1. 需要创建的 Zotero 集合结构\n\n")
        f.write("请在 Zotero 中手动创建以下集合结构：\n\n")
        f.write("```\n")
        f.write("光学项目 (IUI8GQFL)\n")
        f.write(f"└── {READING_LIST_NAME}\n")
        for sub_name in SUB_COLLECTIONS:
            f.write(f"    ├── {sub_name}\n")
        f.write("```\n\n")
        f.write("**操作步骤:**\n")
        f.write("1. 在 Zotero 中右键点击「光学项目」集合\n")
        f.write("2. 选择「新建子集合」\n")
        f.write(f"3. 输入名称: `{READING_LIST_NAME}`\n")
        f.write(f"4. 在「{READING_LIST_NAME}」下重复创建 6 个子集合\n\n")
        f.write("---\n\n")

        # 每个子集合需要添加的文献
        f.write("## 2. 各子集合文献添加清单\n\n")
        f.write("创建集合后，按以下清单将文献拖入对应子集合：\n\n")

        for sub_name in SUB_COLLECTIONS:
            f.write(f"### {sub_name}\n\n")
            pdf_list = READING_ASSIGNMENTS[sub_name]
            tags = ["v0.4必读", "R82后主线"] + COLLECTION_TAGS.get(sub_name, [])

            f.write(f"**需要的标签:** {', '.join(f'`{t}`' for t in tags)}\n\n")
            f.write("**文献清单:**\n\n")

            for pdf in pdf_list:
                if pdf in pdf_to_item:
                    score, reasons, item = pdf_to_item[pdf]
                    title = item['data'].get('title', '(无标题)')
                    item_key = item['key']
                    year = item['data'].get('date', 'N/A')
                    creators = item['data'].get('creators', [])
                    author = creators[0].get('lastName', '?') if creators else '?'

                    f.write(f"- ✓ `{pdf}`\n")
                    f.write(f"  - **Zotero 条目:** {title}\n")
                    f.write(f"  - **Key:** `{item_key}`\n")
                    f.write(f"  - **作者/年份:** {author} ({year})\n")
                    f.write(f"  - **匹配得分:** {score} ({', '.join(reasons)})\n")

                    if pdf in ambiguous_matches:
                        f.write(f"  - ⚠️ **有歧义** - 其他可能匹配:\n")
                        for alt_score, alt_reasons, alt_item in ambiguous_matches[pdf][1:]:
                            alt_title = alt_item['data'].get('title', '(无标题)')
                            f.write(f"    - [{alt_score}] {alt_title}\n")
                else:
                    f.write(f"- ✗ `{pdf}` - **未找到匹配的 Zotero 条目**\n")
            f.write("\n")

        f.write("---\n\n")

        # 完整匹配表
        f.write("## 3. PDF 文件 -> Zotero 条目完整匹配表\n\n")
        f.write(f"总计: {len(pdf_files)} 个 PDF，匹配成功 {len(pdf_to_item)} 个\n\n")

        # 按匹配得分分组
        f.write("### 高置信度匹配 (得分 ≥ 80)\n\n")
        high_conf = [(pdf, data) for pdf, data in pdf_to_item.items() if data[0] >= 80]
        high_conf.sort(key=lambda x: x[1][0], reverse=True)

        for pdf, (score, reasons, item) in high_conf:
            title = item['data'].get('title', '(无标题)')
            f.write(f"- **{score}** `{pdf}`\n")
            f.write(f"  - {title}\n")
            f.write(f"  - Key: `{item['key']}`\n")
            f.write(f"  - 匹配原因: {', '.join(reasons)}\n")

        if not high_conf:
            f.write("（无）\n")
        f.write("\n")

        f.write("### 中等置信度匹配 (得分 40-79)\n\n")
        mid_conf = [(pdf, data) for pdf, data in pdf_to_item.items() if 40 <= data[0] < 80]
        mid_conf.sort(key=lambda x: x[1][0], reverse=True)

        for pdf, (score, reasons, item) in mid_conf:
            title = item['data'].get('title', '(无标题)')
            f.write(f"- **{score}** `{pdf}`\n")
            f.write(f"  - {title}\n")
            f.write(f"  - Key: `{item['key']}`\n")
            f.write(f"  - 匹配原因: {', '.join(reasons)}\n")

        if not mid_conf:
            f.write("（无）\n")
        f.write("\n")

        f.write("### 低置信度匹配 (得分 < 40)\n\n")
        low_conf = [(pdf, data) for pdf, data in pdf_to_item.items() if data[0] < 40]
        low_conf.sort(key=lambda x: x[1][0], reverse=True)

        for pdf, (score, reasons, item) in low_conf:
            title = item['data'].get('title', '(无标题)')
            f.write(f"- **{score}** `{pdf}` ⚠️\n")
            f.write(f"  - {title}\n")
            f.write(f"  - Key: `{item['key']}`\n")
            f.write(f"  - 匹配原因: {', '.join(reasons)}\n")

        if not low_conf:
            f.write("（无）\n")
        f.write("\n")

        f.write("---\n\n")

        # 未匹配 PDF 清单
        f.write("## 4. 未匹配 PDF 清单\n\n")
        if unmatched_pdfs:
            f.write(f"共 {len(unmatched_pdfs)} 个未匹配的 PDF：\n\n")
            for pdf in sorted(unmatched_pdfs):
                year, author, keywords = extract_keywords(pdf)
                f.write(f"- `{pdf}`\n")
                if year or author or keywords:
                    f.write(f"  - 提取信息: 年份={year}, 作者={author}, 关键词={keywords}\n")
            f.write("\n**处理建议:**\n")
            f.write("1. 检查这些 PDF 是否已导入 Zotero「光学项目」集合\n")
            f.write("2. 如果已导入但未匹配，可能是文件名与条目标题差异过大\n")
            f.write("3. 可以在 Zotero 中搜索上述提取的年份/作者信息来定位\n")
            f.write("4. 如果确实不在 Zotero 中，需要先导入这些文献\n")
        else:
            f.write("✓ 所有 PDF 均已匹配！\n")

        f.write("\n---\n\n")

        # 有歧义的匹配
        f.write("## 5. 有歧义的匹配清单\n\n")
        if ambiguous_matches:
            f.write(f"共 {len(ambiguous_matches)} 个有多重候选的 PDF（已选择得分最高的）：\n\n")
            for pdf, matches in sorted(ambiguous_matches.items()):
                f.write(f"### `{pdf}`\n\n")
                for i, (score, reasons, item) in enumerate(matches, 1):
                    title = item['data'].get('title', '(无标题)')
                    mark = "**[已选择]**" if i == 1 else ""
                    f.write(f"{i}. {mark} **得分 {score}** - {title}\n")
                    f.write(f"   - Key: `{item['key']}`\n")
                    f.write(f"   - 匹配原因: {', '.join(reasons)}\n")
                f.write("\n**建议:** 请手动确认第 1 个匹配是否正确。\n\n")
        else:
            f.write("✓ 所有匹配均无歧义！\n")

        f.write("\n---\n\n")

        # 执行状态
        f.write("## 6. 执行状态说明\n\n")
        f.write("### 已完成的操作\n\n")
        f.write("- ✓ 读取项目内 PDF 目录（38 个文件）\n")
        f.write("- ✓ 读取 Zotero「光学项目」集合条目\n")
        f.write("- ✓ 建立 PDF -> Zotero item 匹配关系（使用多维度评分算法）\n")
        f.write("- ✓ 分析必读文献匹配状态\n")
        f.write("- ✓ 生成本报告\n\n")

        f.write("### 需要手动完成的操作\n\n")
        f.write("**原因:** Zotero 本地 API 不支持写入操作（集合创建、条目添加、标签编辑）\n\n")
        f.write("**操作清单:**\n\n")
        f.write("1. **创建集合结构** - 参见第 1 节\n")
        f.write("2. **添加文献到子集合** - 参见第 2 节，按 Key 在 Zotero 中定位条目并拖入对应集合\n")
        f.write("3. **添加标签** - 为每个子集合中的文献添加对应标签（参见第 2 节）\n")
        f.write("4. **验证歧义匹配** - 检查第 5 节中的歧义项，确认匹配正确性\n")
        f.write("5. **处理未匹配文献** - 参见第 4 节，导入或修正未匹配的 PDF\n\n")

        f.write("### 未执行的操作（符合安全要求）\n\n")
        f.write("- 未删除任何 Zotero 条目\n")
        f.write("- 未移动已有条目\n")
        f.write("- 未为找不到匹配的 PDF 创建低质量条目\n")
        f.write("- 未直接修改 zotero.sqlite\n")
        f.write("- 未修改论文正文\n")
        f.write("- 未启动训练\n\n")

        f.write("### 快速操作提示\n\n")
        f.write("在 Zotero 中按 Key 定位条目的方法：\n")
        f.write("1. 点击 Zotero 窗口右上角的搜索框\n")
        f.write("2. 选择「高级搜索」\n")
        f.write("3. 添加条件：「项目 ID」「是」「<Key>」\n")
        f.write("4. 搜索结果中会显示对应条目\n\n")
        f.write("批量添加标签的方法：\n")
        f.write("1. 在目标子集合中选中所有条目（Ctrl+A）\n")
        f.write("2. 右键 -> 「添加标签」\n")
        f.write("3. 输入标签名称（如 `v0.4必读`）\n")
        f.write("4. 重复添加其他标签\n\n")

        # 统计摘要
        f.write("---\n\n")
        f.write("## 7. 统计摘要\n\n")
        f.write(f"- **项目 PDF 总数:** {len(pdf_files)}\n")
        f.write(f"- **Zotero 条目总数:** {len(items)}\n")
        f.write(f"- **成功匹配:** {len(pdf_to_item)} ({len(pdf_to_item)/len(pdf_files)*100:.1f}%)\n")
        f.write(f"- **未匹配:** {len(unmatched_pdfs)} ({len(unmatched_pdfs)/len(pdf_files)*100:.1f}%)\n")
        f.write(f"- **有歧义:** {len(ambiguous_matches)} ({len(ambiguous_matches)/len(pdf_files)*100:.1f}%)\n")
        f.write(f"- **必读文献总数:** {len(all_required_pdfs)}\n")
        f.write(f"- **必读文献匹配:** {len(all_required_pdfs) - len(missing_required)}/{len(all_required_pdfs)}\n")
        f.write(f"- **必读文献缺失:** {len(missing_required)}\n\n")

        if missing_required:
            f.write("**缺失的必读文献:**\n\n")
            for pdf in missing_required:
                f.write(f"- `{pdf}`\n")

    print(f"\n✓ 报告已生成: {REPORT_PATH}")
    print("\n" + "="*80)
    print("任务完成！")
    print("="*80)
    print()
    print("后续步骤:")
    print("1. 查看报告了解匹配状态")
    print("2. 在 Zotero 中手动创建集合结构")
    print("3. 按报告清单将文献添加到对应子集合")
    print("4. 为文献添加标签")
    print()

if __name__ == "__main__":
    main()

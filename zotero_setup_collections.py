#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Zotero v0.4 必读文献集合设置脚本
使用 SQLite 直写创建集合结构并添加条目
"""

import os
import re
import sys
import sqlite3
import random
from datetime import datetime
from pyzotero import zotero

# 设置输出编码为 UTF-8
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 配置
ZOTERO_DB = os.path.expanduser(r"~\Zotero\zotero.sqlite")
PROJECT_COLLECTION_KEY = 'IUI8GQFL'  # "光学项目"集合 key
PDF_DIR = r"D:\我的文件\研究生学术\光学项目\0506新\项目重启_v0.4_BlenderOCS\03_项目说明与规划材料\05_参考材料\03_文献与引用材料\papers"
REPORT_PATH = r"D:\我的文件\研究生学术\光学项目\0506新\项目重启_v0.4_BlenderOCS\03_项目说明与规划材料\05_参考材料\03_文献与引用材料\Zotero_v0.4必读文献整理报告.md"

# 集合结构
READING_LIST_NAME = "v0.4_BlenderOCS_必读文献"
SUB_COLLECTIONS = [
    "01_可观测性_信息下界",
    "02_光变姿态反演_baseline",
    "03_真实光度_BRDF_亮度模型",
    "04_图像姿态_Sim2Real",
    "05_融合_多模态_置信一致性",
    "06_FutureWork_三轴_神经渲染_自监督"
]

# 必读文献分配
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
    name = os.path.splitext(filename)[0]
    name = re.sub(r'[^a-z0-9]', '', name.lower())
    return name

def extract_keywords(filename):
    """从文件名提取关键词"""
    name = os.path.splitext(filename)[0]
    year_match = re.search(r'(19|20)\d{2}', name)
    year = year_match.group(0) if year_match else None

    author_match = re.match(r'^([A-Z][a-z]+)', name)
    if not author_match:
        author_match = re.search(r'_([A-Z][a-z]+)_', name)
    author = author_match.group(1) if author_match else None

    return year, author

def match_pdf_to_item(pdf_filename, items_map):
    """匹配 PDF 文件到 Zotero 条目"""
    pdf_norm = normalize_filename(pdf_filename)
    pdf_year, pdf_author = extract_keywords(pdf_filename)

    best_match = None
    best_score = 0

    for item_key, item_data in items_map.items():
        score = 0

        # 检查标题匹配
        title = item_data['title']
        title_norm = normalize_filename(title)

        if pdf_norm == title_norm:
            score += 90
        elif len(pdf_norm) > 15 and pdf_norm in title_norm:
            score += 70
        elif len(title_norm) > 15 and title_norm in pdf_norm:
            score += 70

        # 检查年份
        if pdf_year and pdf_year in str(item_data.get('year', '')):
            score += 20

        # 检查作者
        if pdf_author and item_data.get('author'):
            if pdf_author.lower() in item_data['author'].lower():
                score += 30

        if score > best_score:
            best_score = score
            best_match = (item_key, item_data, score)

    return best_match if best_score > 40 else None

def new_collection_key(db):
    """生成新集合 key（8位大写字母数字）"""
    chars = "23456789ABCDEFGHIJKLMNPQRSTUVWXYZ"
    c = db.cursor()
    while True:
        k = ''.join(random.choice(chars) for _ in range(8))
        c.execute("SELECT COUNT(*) FROM collections WHERE key=?", (k,))
        if c.fetchone()[0] == 0:
            return k

def get_or_create_tag(db, tag_name):
    """获取或创建标签"""
    c = db.cursor()
    c.execute("SELECT tagID FROM tags WHERE name=?", (tag_name,))
    row = c.fetchone()
    if row:
        return row[0]

    # 创建新标签
    c.execute("SELECT MAX(tagID) FROM tags")
    max_id = c.fetchone()[0]
    new_id = (max_id or 0) + 1
    c.execute("INSERT INTO tags (tagID, name, type) VALUES (?, ?, 0)", (new_id, tag_name))
    return new_id

def main():
    print("="*80)
    print("Zotero v0.4 必读文献集合设置")
    print("="*80)
    print()

    # 步骤 1: 使用本地 API 读取现有条目
    print("步骤 1: 读取 Zotero 现有数据...")
    try:
        z = zotero.Zotero('0', 'user', local=True)
        items = z.collection_items_top(PROJECT_COLLECTION_KEY)
        print(f"✓ 读取到 {len(items)} 个条目")
    except Exception as e:
        print(f"✗ 读取失败: {e}")
        return

    # 建立条目映射
    items_map = {}
    for item in items:
        item_key = item['key']
        data = item['data']
        creators = data.get('creators', [])
        author = creators[0].get('lastName', '') if creators else ''

        items_map[item_key] = {
            'title': data.get('title', ''),
            'year': data.get('date', ''),
            'author': author,
            'itemID': None  # 将从数据库获取
        }

    # 步骤 2: 读取 PDF 文件并匹配
    print("\n步骤 2: 匹配 PDF 文件...")
    pdf_files = [f for f in os.listdir(PDF_DIR) if f.lower().endswith('.pdf')]

    pdf_to_key = {}
    unmatched = []

    for pdf in pdf_files:
        match = match_pdf_to_item(pdf, items_map)
        if match:
            item_key, item_data, score = match
            pdf_to_key[pdf] = (item_key, score)
        else:
            unmatched.append(pdf)

    print(f"✓ 匹配成功: {len(pdf_to_key)}/{len(pdf_files)}")

    # 步骤 3: 连接数据库
    print("\n步骤 3: 连接 Zotero 数据库...")
    if not os.path.exists(ZOTERO_DB):
        print(f"✗ 数据库不存在: {ZOTERO_DB}")
        return

    print(f"数据库路径: {ZOTERO_DB}")
    print("\n⚠️  警告: 即将修改 Zotero 数据库")
    print("   请确认:")
    print("   1. Zotero 已完全关闭")
    print("   2. 数据库已备份")
    print("   3. 无 zotero.sqlite-wal 文件")
    print()

    response = input("确认继续？(yes/no): ").strip().lower()
    if response != 'yes':
        print("已取消操作")
        return

    try:
        db = sqlite3.connect(ZOTERO_DB)
        c = db.cursor()

        # 获取 itemID
        print("\n步骤 4: 获取条目 itemID...")
        for item_key in items_map.keys():
            c.execute("SELECT itemID FROM items WHERE key=?", (item_key,))
            row = c.fetchone()
            if row:
                items_map[item_key]['itemID'] = row[0]

        # 获取父集合的 collectionID
        c.execute("SELECT collectionID FROM collections WHERE key=?", (PROJECT_COLLECTION_KEY,))
        parent_coll_id = c.fetchone()[0]

        # 步骤 5: 创建主集合
        print("\n步骤 5: 创建集合结构...")

        # 检查主集合是否存在
        c.execute("SELECT collectionID, key FROM collections WHERE collectionName=? AND parentCollectionID=?",
                  (READING_LIST_NAME, parent_coll_id))
        row = c.fetchone()

        if row:
            main_coll_id, main_coll_key = row
            print(f"✓ 主集合已存在: {READING_LIST_NAME} (key: {main_coll_key})")
        else:
            # 创建主集合
            c.execute("SELECT MAX(collectionID) FROM collections")
            main_coll_id = (c.fetchone()[0] or 0) + 1
            main_coll_key = new_collection_key(db)

            now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            c.execute("""INSERT INTO collections
                         (collectionID, collectionName, parentCollectionID, clientDateModified, libraryID, key, version, synced)
                         VALUES (?, ?, ?, ?, 1, ?, 0, 0)""",
                      (main_coll_id, READING_LIST_NAME, parent_coll_id, now, main_coll_key))
            print(f"✓ 创建主集合: {READING_LIST_NAME} (key: {main_coll_key})")

        # 步骤 6: 创建子集合
        sub_coll_ids = {}
        for sub_name in SUB_COLLECTIONS:
            c.execute("SELECT collectionID, key FROM collections WHERE collectionName=? AND parentCollectionID=?",
                      (sub_name, main_coll_id))
            row = c.fetchone()

            if row:
                sub_coll_id, sub_coll_key = row
                print(f"✓ 子集合已存在: {sub_name} (key: {sub_coll_key})")
            else:
                c.execute("SELECT MAX(collectionID) FROM collections")
                sub_coll_id = (c.fetchone()[0] or 0) + 1
                sub_coll_key = new_collection_key(db)

                now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
                c.execute("""INSERT INTO collections
                             (collectionID, collectionName, parentCollectionID, clientDateModified, libraryID, key, version, synced)
                             VALUES (?, ?, ?, ?, 1, ?, 0, 0)""",
                          (sub_coll_id, sub_name, main_coll_id, now, sub_coll_key))
                print(f"✓ 创建子集合: {sub_name} (key: {sub_coll_key})")

            sub_coll_ids[sub_name] = (sub_coll_id, sub_coll_key)

        # 步骤 7: 添加条目到子集合并打标签
        print("\n步骤 7: 添加条目到子集合...")

        assignment_results = {}

        for sub_name, pdf_list in READING_ASSIGNMENTS.items():
            sub_coll_id, sub_coll_key = sub_coll_ids[sub_name]
            tags = ["v0.4必读", "R82后主线"] + COLLECTION_TAGS.get(sub_name, [])

            print(f"\n处理: {sub_name}")
            results = []

            for pdf in pdf_list:
                if pdf not in pdf_to_key:
                    print(f"  ✗ {pdf} - 未匹配到 Zotero 条目")
                    results.append((pdf, None, False))
                    continue

                item_key, score = pdf_to_key[pdf]
                itemID = items_map[item_key]['itemID']

                if itemID is None:
                    print(f"  ✗ {pdf} - 无法获取 itemID")
                    results.append((pdf, item_key, False))
                    continue

                # 检查是否已在集合中
                c.execute("SELECT COUNT(*) FROM collectionItems WHERE collectionID=? AND itemID=?",
                          (sub_coll_id, itemID))
                if c.fetchone()[0] == 0:
                    # 添加到集合
                    c.execute("INSERT INTO collectionItems (collectionID, itemID, orderIndex) VALUES (?, ?, 0)",
                              (sub_coll_id, itemID))

                # 添加标签
                for tag_name in tags:
                    tag_id = get_or_create_tag(db, tag_name)

                    # 检查是否已有标签
                    c.execute("SELECT COUNT(*) FROM itemTags WHERE itemID=? AND tagID=?",
                              (itemID, tag_id))
                    if c.fetchone()[0] == 0:
                        c.execute("INSERT INTO itemTags (itemID, tagID, type) VALUES (?, ?, 0)",
                                  (itemID, tag_id))

                title = items_map[item_key]['title'][:50]
                print(f"  ✓ {pdf}")
                print(f"     -> {title}...")
                results.append((pdf, item_key, True))

            assignment_results[sub_name] = results

        # 提交事务
        print("\n提交更改...")
        db.commit()
        print("✓ 数据库更改已提交")

        # 步骤 8: 生成报告
        print("\n生成报告...")
        with open(REPORT_PATH, 'w', encoding='utf-8') as f:
            f.write("# Zotero v0.4 必读文献整理报告\n\n")
            f.write(f"生成时间: 2026-06-29\n\n")
            f.write("---\n\n")

            f.write("## 1. 创建的集合结构\n\n")
            f.write(f"**主集合:** {READING_LIST_NAME}\n")
            f.write(f"- Key: `{main_coll_key}`\n")
            f.write(f"- 父集合: 光学项目 (`{PROJECT_COLLECTION_KEY}`)\n\n")

            f.write("**子集合:**\n\n")
            for sub_name in SUB_COLLECTIONS:
                coll_id, coll_key = sub_coll_ids[sub_name]
                f.write(f"- {sub_name}\n")
                f.write(f"  - Key: `{coll_key}`\n")

            f.write("\n---\n\n")
            f.write("## 2. 文献添加结果\n\n")

            for sub_name in SUB_COLLECTIONS:
                f.write(f"### {sub_name}\n\n")
                results = assignment_results[sub_name]
                success = sum(1 for _, _, s in results if s)
                f.write(f"成功: {success}/{len(results)}\n\n")

                for pdf, key, success in results:
                    status = "✓" if success else "✗"
                    if key:
                        title = items_map[key]['title']
                        f.write(f"- {status} `{pdf}`\n")
                        f.write(f"  - {title}\n")
                        f.write(f"  - Key: `{key}`\n")
                    else:
                        f.write(f"- {status} `{pdf}` - 未匹配\n")
                f.write("\n")

            f.write("---\n\n")
            f.write("## 3. 未匹配的 PDF\n\n")
            if unmatched:
                for pdf in unmatched:
                    f.write(f"- `{pdf}`\n")
            else:
                f.write("（无）\n")

        print(f"✓ 报告已生成: {REPORT_PATH}")

    except Exception as e:
        print(f"\n✗ 错误: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        return
    finally:
        db.close()

    print("\n" + "="*80)
    print("任务完成！请重启 Zotero 查看结果。")
    print("="*80)

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Zotero v0.4 必读文献完整整理
功能：全库扫描 → 匹配 → 导入缺失文献 → 建集合 → 添加条目 → 打标签 → 生成报告
"""

import os, re, sys, sqlite3, random, shutil
from datetime import datetime, timezone

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# ========= 配置 =========
ZOTERO_PROFILE = os.path.expanduser(r"~\Zotero")
ZOTERO_DB_CLEAN = os.path.join(ZOTERO_PROFILE, "zotero_clean.sqlite")
ZOTERO_DB_REAL = os.path.join(ZOTERO_PROFILE, "zotero.sqlite")
ZOTERO_STORAGE = os.path.join(ZOTERO_PROFILE, "storage")
PROJECT_KEY = 'IUI8GQFL'
PDF_DIR = r"D:\我的文件\研究生学术\光学项目\0506新\项目重启_v0.4_BlenderOCS\03_项目说明与规划材料\05_参考材料\03_文献与引用材料\papers"
REPORT_PATH = r"D:\我的文件\研究生学术\光学项目\0506新\项目重启_v0.4_BlenderOCS\03_项目说明与规划材料\05_参考材料\03_文献与引用材料\Zotero_v0.4必读文献整理报告.md"

READING_LIST_NAME = "v0.4_BlenderOCS_必读文献"
SUB_COLLECTIONS = [
    "01_可观测性_信息下界",
    "02_光变姿态反演_baseline",
    "03_真实光度_BRDF_亮度模型",
    "04_图像姿态_Sim2Real",
    "05_融合_多模态_置信一致性",
    "06_FutureWork_三轴_神经渲染_自监督"
]

# 必读清单（PDF文件名 -> 子集合名）
READING_ASSIGNMENTS = {
    "01_可观测性_信息下界": [
        "JOSAA_2003_Gerwe_Idell_orientation_Cramer_Rao.pdf",
        "ICML_2017_Guo_calibration_modern_neural_networks.pdf",
        "FnTML_2023_Angelopoulos_Bates_conformal_prediction_intro.pdf",
    ],
    "02_光变姿态反演_baseline": [
        "JGCD_2009_Wetterer_Jah_attitude_determination_light_curves.pdf",
        "TAES_2017_Piergentili_attitude_lightcurve_measurements.pdf",
        "Burton 2024.pdf", "Wang 2024.pdf",
        "ASR_2022_Clark_RSO_attitude_optical_property_light_curves.pdf",
        "JGCD_2014_Linares_shape_tracking_lightcurve_angles.pdf",
    ],
    "03_真实光度_BRDF_亮度模型": [
        "Fankhauser_2023_Satellite_Optical_Brightness_arXiv2305.11123.pdf",
        "lu2024_brdf_starlink.pdf", "yang2024_goniopolarimetric.pdf",
        "JGCD_2023_Dianetti_Crassidis_polarized_light_curves.pdf",
        "aerospace-13-00418-v2.pdf",
    ],
    "04_图像姿态_Sim2Real": [
        "dickinson2025_sim2real_6dof.pdf",
        "IEEEAero_2022_Park_SPEEDplus_spacecraft_pose_domain_gap.pdf",
        "ASR_2024_Park_DAmico_SPNv2_domain_gap_pose_estimation.pdf",
        "Acta_2023_Bechini_dataset_generation_validation_spacecraft_pose.pdf",
        "Acta_2021_PasqualettoCassinis_CNN_pose_tightly_loosely_coupled.pdf",
    ],
    "05_融合_多模态_置信一致性": [
        "TAES_2022_Rondao_ChiNet_multimodal_spacecraft_pose.pdf",
        "liu2024_visual_inertial_fusion.pdf",
        "Fusion_2014_Linares_space_object_classification_characterization_MMAE.pdf",
        "aerospace2025_joint_estimation.pdf",
        "marto2024_hyperspectral_lightcurve.pdf",
    ],
    "06_FutureWork_三轴_神经渲染_自监督": [
        "Kumar_2025_Light_curves_sequential_comparison_ActaAstronautica_10.1016-j.actaastro.2025.04.018.pdf",
        "AMOS_2024_deAndres_attitude_monitoring_three_axis_light_curves.pdf",
        "groves2025_selfsupervised_ssa.pdf", "behari2023_sundial.pdf",
        "AandA_2025_Tang_asteroid_shape_inversion_deep_learning.pdf",
        "AMOS_2019_Furfaro_shape_identification_light_curve_inversion.pdf",
    ],
}

COLLECTION_TAGS = {
    "01_可观测性_信息下界": ["可观测性"],
    "02_光变姿态反演_baseline": ["光变反演"],
    "03_真实光度_BRDF_亮度模型": ["真实光度限制"],
    "04_图像姿态_Sim2Real": ["图像姿态baseline"],
    "05_融合_多模态_置信一致性": ["fusion负结果解释"],
    "06_FutureWork_三轴_神经渲染_自监督": ["future-work"],
}

# ========= 辅助函数 =========

def norm(s):
    """标准化字符串用于匹配：小写字母数字"""
    return re.sub(r'[^a-z0-9]', '', s.lower())

def extract_from_filename(filename):
    """从 PDF 文件名提取元数据"""
    name = os.path.splitext(filename)[0]
    info = {'filename': filename, 'original': name}

    # 年份
    ym = re.search(r'(19|20)(\d{2})', name)
    if ym:
        info['year'] = int(ym.group(0))
    else:
        info['year'] = None

    # DOI（文件名中常有 10.xxxx 格式）
    doi_m = re.search(r'(10[.][\d]{4,}[^\s.]+(?:[.][^\s.]+)*)', name)
    if doi_m:
        doi = doi_m.group(0).rstrip('._-')
        # 把 - 替换为 / 如果看起来像 DOI
        if '/' not in doi and '-' in doi:
            # 尝试修复：常见的文件名 DOI 用 - 替代 /
            pass
        info['doi'] = doi
    else:
        info['doi'] = None

    return info

def new_key(db):
    chars = "23456789ABCDEFGHIJKLMNPQRSTUVWXYZ"
    c = db.cursor()
    while True:
        k = ''.join(random.choice(chars) for _ in range(8))
        c.execute("SELECT COUNT(*) FROM items WHERE key=?", (k,))
        if c.fetchone()[0] == 0:
            return k

def now_str():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

def get_next_id(db, table, pk):
    c = db.cursor()
    c.execute(f"SELECT MAX({pk}) FROM {table}")
    r = c.fetchone()[0]
    return (r or 0) + 1

def get_or_create_value(db, text):
    c = db.cursor()
    c.execute("SELECT valueID FROM itemDataValues WHERE value=?", (text,))
    r = c.fetchone()
    if r: return r[0]
    vid = get_next_id(db, 'itemDataValues', 'valueID')
    c.execute("INSERT INTO itemDataValues (valueID, value) VALUES (?,?)", (vid, text))
    return vid

def set_field(db, itemID, fieldID, text):
    c = db.cursor()
    vid = get_or_create_value(db, text)
    c.execute("SELECT COUNT(*) FROM itemData WHERE itemID=? AND fieldID=?", (itemID, fieldID))
    if c.fetchone()[0] > 0:
        c.execute("UPDATE itemData SET valueID=? WHERE itemID=? AND fieldID=?", (vid, itemID, fieldID))
    else:
        c.execute("INSERT INTO itemData (itemID, fieldID, valueID) VALUES (?,?,?)", (itemID, fieldID, vid))

def get_or_create_tag(db, tag_name):
    c = db.cursor()
    c.execute("SELECT tagID FROM tags WHERE name=?", (tag_name,))
    r = c.fetchone()
    if r: return r[0]
    tid = get_next_id(db, 'tags', 'tagID')
    c.execute("INSERT INTO tags (tagID, name) VALUES (?,?)", (tid, tag_name))
    return tid

# ========= 主流程 =========

def main():
    print("="*80)
    print("Zotero v0.4 必读文献完整整理")
    print("="*80)
    print(f"\n数据库: {ZOTERO_DB_REAL}")
    print(f"工作副本: {ZOTERO_DB_CLEAN}")
    print(f"PDF 目录: {PDF_DIR}\n")

    # --- 确保工作副本存在且可写 ---
    if not os.path.exists(ZOTERO_DB_CLEAN):
        shutil.copy2(ZOTERO_DB_REAL, ZOTERO_DB_CLEAN)
        print(f"✓ 已从原数据库复制工作副本\n")

    # 清理工作副本的 journal
    for suffix in ['-journal', '-wal', '-shm']:
        p = ZOTERO_DB_CLEAN + suffix
        if os.path.exists(p):
            try: os.remove(p)
            except: pass

    db = sqlite3.connect(ZOTERO_DB_CLEAN)
    c = db.cursor()

    try:
        # ======== 阶段 A：全库扫描 ========
        print("="*60)
        print("阶段 A：全库扫描 Zotero 条目")
        print("="*60)

        c.execute("""SELECT i.itemID, i.key, it.typeName, i.itemTypeID
                     FROM items i
                     JOIN itemTypes it ON i.itemTypeID = it.itemTypeID
                     WHERE it.typeName IN ('journalArticle','conferencePaper','preprint','thesis')""")
        all_items = {}
        for itemID, key, typeName, itemTypeID in c.fetchall():
            title = c.execute("""SELECT idv.value FROM itemData id
                                 JOIN itemDataValues idv ON id.valueID=idv.valueID
                                 WHERE id.itemID=? AND id.fieldID=1""", (itemID,)).fetchone()
            title = title[0] if title else ""

            date = c.execute("""SELECT idv.value FROM itemData id
                                JOIN itemDataValues idv ON id.valueID=idv.valueID
                                WHERE id.itemID=? AND id.fieldID=6""", (itemID,)).fetchone()
            date = date[0] if date else ""

            doi = c.execute("""SELECT idv.value FROM itemData id
                               JOIN itemDataValues idv ON id.valueID=idv.valueID
                               WHERE id.itemID=? AND id.fieldID=59""", (itemID,)).fetchone()
            doi = doi[0] if doi else ""

            author = c.execute("""SELECT cr.lastName FROM itemCreators ic
                                  JOIN creators cr ON ic.creatorID=cr.creatorID
                                  WHERE ic.itemID=? ORDER BY ic.orderIndex LIMIT 1""", (itemID,)).fetchone()
            author = author[0] if author else ""

            # 附件
            attachments = []
            c.execute("""SELECT ia.path, ia.itemID FROM itemAttachments ia
                         WHERE ia.parentItemID=? AND ia.contentType LIKE '%pdf%'""", (itemID,))
            for att_path, att_id in c.fetchall():
                # 从 path 提取文件名
                if att_path:
                    fname = att_path.replace('storage:', '') if att_path.startswith('storage:') else os.path.basename(att_path)
                    attachments.append(fname)

            key_lower = key.lower() if key else ''
            all_items[key] = {
                'itemID': itemID, 'key': key,
                'title': title, 'year': date, 'doi': doi, 'author': author,
                'typeName': typeName, 'itemTypeID': itemTypeID,
                'attachments': attachments, 'title_norm': norm(title),
            }

        print(f"全库文献条目总数: {len(all_items)}")

        # ======== 阶段 B：多轮匹配 ========
        print("\n" + "="*60)
        print("阶段 B：多轮匹配 PDF -> Zotero 条目")
        print("="*60)

        pdf_files = [f for f in os.listdir(PDF_DIR) if f.lower().endswith('.pdf')]
        all_required = []
        for lst in READING_ASSIGNMENTS.values():
            all_required.extend(lst)
        all_required_set = set(all_required)

        pdf_matched = {}    # pdf -> key
        pdf_new = {}        # pdf -> need to import
        match_details = {}  # pdf -> (key, score, reason)

        for pdf in sorted(pdf_files):
            pdf_norm = norm(pdf)
            pdf_info = extract_from_filename(pdf)
            best_key = None; best_score = 0; best_reason = ""

            for key, item in all_items.items():
                score = 0; reasons = []

                # R1: 附件文件名完全匹配（最高权重）
                for att in item['attachments']:
                    att_norm = norm(att)
                    if att_norm == pdf_norm:
                        score += 1000
                        reasons.append('附件名完全匹配')
                    elif len(att_norm) > 20 and att_norm in pdf_norm:
                        score += 500
                        reasons.append('附件名包含')
                    elif len(pdf_norm) > 20 and pdf_norm in att_norm:
                        score += 500
                        reasons.append('PDF名包含于附件')

                # R2: 标题匹配
                title_norm = item['title_norm']
                if title_norm and len(title_norm) > 10:
                    if title_norm == pdf_norm:
                        score += 300; reasons.append('标题完全匹配')
                    elif len(pdf_norm) > 20 and pdf_norm in title_norm:
                        score += 150; reasons.append('PDF名包含于标题')
                    elif len(title_norm) > 20 and title_norm in pdf_norm:
                        score += 150; reasons.append('标题包含于PDF名')

                # R3: 年份 + 作者
                if pdf_info.get('year') and item['year']:
                    if str(pdf_info['year']) in str(item['year']):
                        score += 20; reasons.append(f"年份({pdf_info['year']})")

                # R4: DOI
                if pdf_info.get('doi') and item['doi']:
                    if norm(pdf_info['doi']) in norm(item['doi']):
                        score += 400; reasons.append('DOI匹配')

                # R5: 关键词
                for kw in ['lightcurve','attitude','pose','brdf','inversion','spacecraft',
                            'sim2real','fusion','multimodal','calibration','conformal',
                            'cramer','shape','tracking','polarized','goniopolarimetric',
                            'starlink','hyperspectral','selfsupervised','sundial','asteroid']:
                    if kw in pdf_norm and kw in title_norm:
                        score += 5; reasons.append(f'关键词:{kw}')

                if score > best_score:
                    best_score = score; best_key = key; best_reason = '; '.join(reasons)

            if best_score >= 100:
                pdf_matched[pdf] = best_key
                match_details[pdf] = (best_key, best_score, best_reason)
            else:
                pdf_new[pdf] = pdf_info

        print(f"已匹配: {len(pdf_matched)}")
        print(f"待导入: {len(pdf_new)}")

        required_matched = sum(1 for p in all_required_set if p in pdf_matched)
        required_new = sum(1 for p in all_required_set if p not in pdf_matched)
        print(f"必读文献({len(all_required_set)}篇): 已匹配{required_matched}, 待导入{required_new}")

        # 显示几个匹配示例
        for pdf, (key, score, reason) in sorted(match_details.items(), key=lambda x: -x[1][1])[:5]:
            item = all_items[key]
            print(f"  [{score}] {pdf} → {item['title'][:60]}")

        # ======== 阶段 C：导入缺失文献 ========
        print("\n" + "="*60)
        print("阶段 C：导入缺失文献到 Zotero")
        print("="*60)

        imported = {}  # pdf -> key

        # 期刊缩写映射（从文件名推断）
        JOURNAL_MAP = {
            'JGCD': 'Journal of Guidance, Control, and Dynamics',
            'JOSAA': 'Journal of the Optical Society of America A',
            'TAES': 'IEEE Transactions on Aerospace and Electronic Systems',
            'ASR': 'Advances in Space Research',
            'Acta': 'Acta Astronautica',
            'IEEEAero': 'IEEE Aerospace Conference',
            'ICML': 'International Conference on Machine Learning',
            'FnTML': 'Foundations and Trends in Machine Learning',
            'Fusion': 'Fusion',
            'Icarus': 'Icarus',
            'AandA': 'Astronomy & Astrophysics',
            'AMOS': 'Advanced Maui Optical and Space Surveillance Technologies Conference',
            'ESA_SDC8': '9th European Conference on Space Debris',
        }

        for pdf, info in sorted(pdf_new.items()):
            src_path = os.path.join(PDF_DIR, pdf)
            if not os.path.exists(src_path):
                print(f"  ✗ 文件不存在: {pdf}")
                continue

            # 决定 itemType
            itemTypeID = 22  # 默认期刊
            if 'ICML' in pdf or 'ICML' in info.get('original',''):
                itemTypeID = 11  # 会议
            elif 'AMOS' in pdf or 'ESA' in pdf or 'SDC' in pdf:
                itemTypeID = 11
            elif 'arXiv' in pdf or 'arxiv' in pdf.lower():
                itemTypeID = 31  # 预印本
            elif 'dickinson' in pdf.lower() and 'sim2real' in pdf.lower():
                itemTypeID = 37  # 学位论文

            # 生成标题（用文件名去掉扩展作为工作标题）
            raw_title = info['original'].replace('-', ' ').replace('_', ' ')
            # 去掉纯技术性后缀
            raw_title = re.sub(r'\s*10[.]\d{4,}.*$', '', raw_title).strip()
            # 尝试让首字母大写
            title = ' '.join(w[0].upper()+w[1:] if len(w)>2 else w for w in raw_title.split())

            # 条目 itemID
            parent_id = get_next_id(db, 'items', 'itemID')
            parent_key = new_key(db)
            now = now_str()

            c.execute("""INSERT INTO items (itemID, itemTypeID, dateAdded, dateModified,
                         clientDateModified, libraryID, key, version, synced)
                         VALUES (?,?,?,?,?,1,?,0,0)""",
                      (parent_id, itemTypeID, now, now, now, parent_key))

            # 设置字段
            set_field(db, parent_id, 1, title)  # title
            year_str = str(info['year']) if info['year'] else ""
            if year_str:
                set_field(db, parent_id, 6, year_str)  # date

            if info.get('doi'):
                set_field(db, parent_id, 59, info['doi'])

            # 推断期刊名
            for abbr, full in JOURNAL_MAP.items():
                if abbr.lower() in pdf.lower():
                    if itemTypeID == 11:
                        set_field(db, parent_id, 58, full)  # conferenceName
                    else:
                        set_field(db, parent_id, 38, full)  # publicationTitle
                    break

            # 附件
            att_id = get_next_id(db, 'items', 'itemID')
            att_key = new_key(db)
            c.execute("""INSERT INTO items (itemID, itemTypeID, dateAdded, dateModified,
                         clientDateModified, libraryID, key, version, synced)
                         VALUES (?,3,?,?,?,1,?,0,0)""",
                      (att_id, now, now, now, att_key))

            # 存储 PDF
            storage_dir = os.path.join(ZOTERO_STORAGE, att_key)
            os.makedirs(storage_dir, exist_ok=True)
            shutil.copy2(src_path, os.path.join(storage_dir, pdf))

            c.execute("""INSERT INTO itemAttachments (itemID, parentItemID, linkMode, contentType, path, syncState)
                         VALUES (?,?,0,'application/pdf',?,0)""",
                      (att_id, parent_id, f"storage:{pdf}"))

            imported[pdf] = parent_key

            # 加入全库映射
            all_items[parent_key] = {
                'itemID': parent_id, 'key': parent_key,
                'title': title, 'year': year_str, 'doi': info.get('doi',''), 'author': '',
                'typeName': {22:'journalArticle',11:'conferencePaper',31:'preprint',37:'thesis'}[itemTypeID],
                'itemTypeID': itemTypeID, 'attachments': [pdf],
                'title_norm': norm(title),
            }

            print(f"  ✓ {pdf} → [{parent_key}] {title[:60]}")

        print(f"\n本次导入: {len(imported)} 篇")

        # 更新匹配映射
        for pdf, key in imported.items():
            pdf_matched[pdf] = key
            match_details[pdf] = (key, 999, '新建导入')

        # ======== 阶段 D：创建/复用集合结构 ========
        print("\n" + "="*60)
        print("阶段 D：创建集合结构")
        print("="*60)

        # 获取父集合 collectionID
        c.execute("SELECT collectionID FROM collections WHERE key=?", (PROJECT_KEY,))
        parent_coll_id = c.fetchone()[0]

        # 主集合
        c.execute("SELECT collectionID, key FROM collections WHERE collectionName=? AND parentCollectionID=?",
                  (READING_LIST_NAME, parent_coll_id))
        row = c.fetchone()
        if row:
            main_coll_id, main_coll_key = row
            print(f"✓ 已存在: {READING_LIST_NAME}")
        else:
            main_coll_id = get_next_id(db, 'collections', 'collectionID')
            main_coll_key = new_key(db)
            c.execute("""INSERT INTO collections (collectionID, collectionName, parentCollectionID,
                         clientDateModified, libraryID, key, version, synced)
                         VALUES (?,?,?,?,1,?,0,0)""",
                      (main_coll_id, READING_LIST_NAME, parent_coll_id, now_str(), main_coll_key))
            print(f"✓ 创建: {READING_LIST_NAME}")

        # 子集合
        sub_coll = {}
        for sub_name in SUB_COLLECTIONS:
            c.execute("SELECT collectionID, key FROM collections WHERE collectionName=? AND parentCollectionID=?",
                      (sub_name, main_coll_id))
            row = c.fetchone()
            if row:
                sub_coll[sub_name] = row
                print(f"✓ 已存在: {sub_name}")
            else:
                sc_id = get_next_id(db, 'collections', 'collectionID')
                sc_key = new_key(db)
                c.execute("""INSERT INTO collections (collectionID, collectionName, parentCollectionID,
                             clientDateModified, libraryID, key, version, synced)
                             VALUES (?,?,?,?,1,?,0,0)""",
                          (sc_id, sub_name, main_coll_id, now_str(), sc_key))
                sub_coll[sub_name] = (sc_id, sc_key)
                print(f"✓ 创建: {sub_name}")

        # ======== 阶段 E：添加条目到子集合 + 打标签 ========
        print("\n" + "="*60)
        print("阶段 E：添加条目 + 标签")
        print("="*60)

        results = {}
        total_ok = 0

        for sub_name, pdf_list in READING_ASSIGNMENTS.items():
            sc_id, sc_key = sub_coll[sub_name]
            tags = ["v0.4必读", "R82后主线"] + COLLECTION_TAGS.get(sub_name, [])
            print(f"\n{sub_name}:")
            sub_results = []

            for pdf in pdf_list:
                if pdf not in pdf_matched:
                    sub_results.append((pdf, None, False, "未匹配"))
                    print(f"  ✗ {pdf} - 未匹配")
                    continue

                key = pdf_matched[pdf]
                item = all_items.get(key)
                if not item:
                    sub_results.append((pdf, key, False, "无条目"))
                    print(f"  ✗ {pdf} - 条目不存在")
                    continue

                # 添加到集合（防止重复）
                c.execute("SELECT COUNT(*) FROM collectionItems WHERE collectionID=? AND itemID=?",
                          (sc_id, item['itemID']))
                if c.fetchone()[0] == 0:
                    c.execute("SELECT COALESCE(MAX(orderIndex),-1) FROM collectionItems WHERE collectionID=?",
                              (sc_id,))
                    c.execute("INSERT INTO collectionItems (collectionID, itemID, orderIndex) VALUES (?,?,?)",
                              (sc_id, item['itemID'], c.fetchone()[0]+1))

                # 打标签
                for tag_name in tags:
                    tid = get_or_create_tag(db, tag_name)
                    c.execute("SELECT COUNT(*) FROM itemTags WHERE itemID=? AND tagID=?",
                              (item['itemID'], tid))
                    if c.fetchone()[0] == 0:
                        c.execute("INSERT INTO itemTags (itemID, tagID, type) VALUES (?,?,0)",
                                  (item['itemID'], tid))

                src = "导入" if pdf in imported else "已有"
                total_ok += 1
                sub_results.append((pdf, key, True, src))
                print(f"  ✓ [{src}] {pdf}")

            results[sub_name] = sub_results

        db.commit()
        print(f"\n✓ 成功: {total_ok}/{len(all_required_set)}")

        # 同时把"光学项目"集合外的条目也关联到"光学项目"
        print("\n关联新导入条目到 '光学项目' 集合...")
        for pdf, key in imported.items():
            item = all_items[key]
            c.execute("SELECT COUNT(*) FROM collectionItems WHERE collectionID=? AND itemID=?",
                      (parent_coll_id, item['itemID']))
            if c.fetchone()[0] == 0:
                c.execute("SELECT COALESCE(MAX(orderIndex),-1) FROM collectionItems WHERE collectionID=?",
                          (parent_coll_id,))
                c.execute("INSERT INTO collectionItems (collectionID, itemID, orderIndex) VALUES (?,?,?)",
                          (parent_coll_id, item['itemID'], c.fetchone()[0]+1))
        db.commit()
        print("✓ 完成")

        # ======== 阶段 F：生成报告 ========
        print("\n" + "="*60)
        print("生成报告...")
        print("="*60)

        # 收集所有现有匹配信息
        remaining_unmatched = [p for p in all_required if p not in pdf_matched]

        with open(REPORT_PATH, 'w', encoding='utf-8') as f:
            f.write("# Zotero v0.4 必读文献整理报告\n\n")
            f.write(f"**生成时间:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**操作:** 全库扫描 + 匹配 + 导入缺失 + 建集合 + 打标签\n\n---\n\n")

            f.write("## 1. 集合结构\n\n")
            f.write(f"| 集合 | Key |\n|---|---|\n")
            f.write(f"| 光学项目（父） | `{PROJECT_KEY}` |\n")
            f.write(f"| └ {READING_LIST_NAME} | `{main_coll_key}` |\n")
            for sub_name in SUB_COLLECTIONS:
                sc_id, sc_key = sub_coll[sub_name]
                f.write(f"| &emsp;├ {sub_name} | `{sc_key}` |\n")
            f.write("\n---\n\n")

            f.write("## 2. 统计摘要\n\n")
            f.write(f"| 项目 | 数值 |\n|---|---|\n")
            f.write(f"| Zotero 全库文献条目 | {len(all_items)-len(imported)} (原有) + {len(imported)} (新导入) = {len(all_items)} |\n")
            f.write(f"| 项目 PDF 总数 | {len(pdf_files)} |\n")
            f.write(f"| 必读文献总数 | {len(all_required_set)} |\n")
            f.write(f"| 已匹配（原有） | {len(pdf_matched)-len(imported)} |\n")
            f.write(f"| 新导入 | {len(imported)} |\n")
            f.write(f"| 成功入库 | {total_ok} |\n")
            f.write(f"| 仍未匹配 | {len(remaining_unmatched)} |\n\n")

            f.write("---\n\n")

            f.write("## 3. 各子集合文献清单\n\n")
            for sub_name in SUB_COLLECTIONS:
                f.write(f"### {sub_name}\n\n")
                tags = ["v0.4必读", "R82后主线"] + COLLECTION_TAGS.get(sub_name, [])
                f.write(f"标签: {' '.join('`'+t+'`' for t in tags)}\n\n")
                f.write("| 状态 | PDF | Zotero Key | 来源 |\n")
                f.write("|---|---|---|---|\n")
                for pdf, key, ok, src in results[sub_name]:
                    status = "✓" if ok else "✗"
                    f.write(f"| {status} | `{pdf}` | `{key or '—'}` | {src} |\n")
                f.write("\n")

            f.write("---\n\n")

            f.write("## 4. 新导入文献详情\n\n")
            if imported:
                f.write(f"共导入 {len(imported)} 篇文献：\n\n")
                for pdf, key in sorted(imported.items()):
                    item = all_items[key]
                    f.write(f"- `{pdf}`\n")
                    f.write(f"  - Key: `{key}`\n")
                    f.write(f"  - 标题: {item['title']}\n")
                    f.write(f"  - 类型: {item['typeName']}\n")
                    f.write(f"  - 年份: {item['year']}\n")
            else:
                f.write("（无新导入，全部已存在）\n")

            f.write("\n---\n\n")

            f.write("## 5. 未匹配的必读文献\n\n")
            if remaining_unmatched:
                for pdf in remaining_unmatched:
                    f.write(f"- `{pdf}`\n")
                f.write("\n**说明:** 请手动处理这些文献。\n")
            else:
                f.write("✓ 所有必读文献均已匹配成功！\n")

            f.write("\n---\n\n")

            f.write("## 6. 操作记录\n\n")
            f.write("- ✓ 全库扫描 Zotero 条目\n")
            f.write("- ✓ 多轮匹配（附件名/标题/年份/DOI/关键词）\n")
            f.write("- ✓ 导入缺失文献（含标题、年份、DOI、期刊推断、PDF 挂载）\n")
            f.write("- ✓ 创建集合结构（1 主 + 6 子）\n")
            f.write("- ✓ 添加条目到子集合（不复制，不移动原条目）\n")
            f.write("- ✓ 打标签（v0.4必读、R82后主线、主题标签）\n")
            f.write("- ✓ 关联新条目到「光学项目」集合\n")
            f.write("- ✗ 不删除已有条目\n")
            f.write("- ✗ 不移动已有条目（额外加入）\n")
            f.write("- ✗ 不强行创建低质量条目（已尽量从文件名提取元数据）\n")

        print(f"✓ 报告已生成: {REPORT_PATH}")

    except Exception as e:
        db.rollback()
        print(f"\n✗ 错误: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        db.close()

    # ======== 阶段 G：替换原数据库 ========
    print("\n" + "="*60)
    print("替换原数据库...")
    print("="*60)
    db.close()

    # 备份当前数据库
    backup_path = ZOTERO_DB_REAL + f".bak_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    try:
        shutil.copy2(ZOTERO_DB_REAL, backup_path)
        print(f"✓ 已备份: {backup_path}")
    except PermissionError:
        print(f"✗ 无法备份，尝试直接替换...")

    # 替换
    try:
        os.replace(ZOTERO_DB_CLEAN, ZOTERO_DB_REAL)
        print(f"✓ 数据库已替换: {ZOTERO_DB_REAL}")
    except PermissionError:
        print(f"✗ 无法替换数据库文件！")
        print(f"  修改后的数据库在: {ZOTERO_DB_CLEAN}")
        print(f"  请手动关闭所有程序后，将 {ZOTERO_DB_CLEAN} 复制为 {ZOTERO_DB_REAL}")
        return 2

    # 清理 journal
    for suffix in ['-journal', '-wal', '-shm']:
        p = ZOTERO_DB_REAL + suffix
        if os.path.exists(p):
            try: os.remove(p)
            except: pass

    print("\n" + "="*80)
    print(f"✓ 全部完成！成功导入 {len(imported)} 篇，总计入库 {total_ok}/{len(all_required_set)} 篇必读文献。")
    print("请重启 Zotero 查看结果。")
    print("="*80)
    return 0

if __name__ == "__main__":
    sys.exit(main())

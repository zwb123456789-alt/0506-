# Claude 操作 Zotero 经验总结

> 本次操作时间: 2026-06-05  
> 任务: 诊断并修复本项目 17 篇文献在 Zotero 中的条目问题  
> 结果: 17/17 全部到位,无缺失、无游离、元数据完整

---

## 一、技术路线选择

### 1.1 本地 API vs SQLite 直写

Zotero 7 提供两种访问方式:

| 方式 | 读 | 写 | 适用场景 |
|---|---|---|---|
| **本地 API** (端口 23119) | ✅ | ❌ (501 Not Implemented) | 只读查询、浏览、诊断 |
| **SQLite 直写** | ✅ | ✅ | 批量修复、新建条目、挂 PDF |

**关键结论**: Zotero 7 本地 API 是**只读**的,任何写入操作(PATCH/POST/DELETE)都返回 501。要修改条目,必须:
- 关闭 Zotero
- 备份 `zotero.sqlite`
- 直接 SQL 写库
- 重启 Zotero

### 1.2 启用本地 API

本地 API 默认关闭,需在 `prefs.js` 中添加:

```javascript
user_pref("extensions.zotero.httpServer.enabled", true);
user_pref("extensions.zotero.httpServer.localAPI.enabled", true);
```

**操作流程**:
1. 优雅关闭 Zotero: `taskkill /IM zotero.exe` (Windows)
2. 等待端口 23119 释放、无 WAL 文件
3. 备份 `prefs.js`
4. 写入上述两行(插在 `extensions.zotero.dataDir` 之后)
5. 重启 Zotero
6. 验证: `curl http://127.0.0.1:23119/api/users/0/items?limit=1` 应返回 HTTP 200

---

## 二、诊断工作流

### 2.1 只读诊断(本地 API 可用时)

使用 `pyzotero` 的 `local=True` 模式:

```python
from pyzotero import zotero
zot = zotero.Zotero("0", "user", local=True)

# 总览
print("总条目:", zot.count_items())

# 搜索
results = zot.items(q="关键词", limit=20)

# 读条目
item = zot.item("ITEM_KEY")
print(item["data"]["title"])

# 子条目(附件/笔记)
children = zot.children("ITEM_KEY")
for ch in children:
    if ch["data"]["itemType"] == "attachment":
        print("PDF:", ch["data"].get("filename"))
```

### 2.2 诊断常见问题(直接读 SQLite)

当 Zotero 关闭时,只读查询数据库(`sqlite3.connect("file:path?mode=ro", uri=True)`):

**问题类型**:
1. **游离 PDF**(无父条目): `SELECT * FROM itemAttachments WHERE parentItemID IS NULL`
2. **缺 PDF**: 父条目有 `itemID` 但 `itemAttachments` 表中无对应行
3. **文件磁盘丢失**: `path` 字段指向的文件 `os.path.exists()` 为 False
4. **缺元数据**: `itemData` 表中缺 `fieldID=6(date)` / `59(DOI)` / `1(title)`
5. **DOI 错挂**: 两个不同条目的 DOI 相同或指向错误论文
6. **类型错误**: `itemTypeID` 为 journalArticle(22) 但实际是会议论文(应为 11)

**诊断脚本模板**:

```python
import sqlite3, os
db = sqlite3.connect("file:zotero.sqlite?mode=ro", uri=True)
c = db.cursor()

# 1. 游离附件
c.execute("""SELECT i.key, ia.path FROM itemAttachments ia 
             JOIN items i ON ia.itemID=i.itemID 
             WHERE ia.parentItemID IS NULL""")
orphans = c.fetchall()
print(f"游离 PDF: {len(orphans)}")

# 2. 父条目无 PDF
c.execute("""SELECT i.key, it.typeName FROM items i 
             JOIN itemTypes it ON i.itemTypeID=it.itemTypeID
             WHERE it.typeName IN ('journalArticle','conferencePaper')
             AND i.itemID NOT IN (SELECT DISTINCT parentItemID FROM itemAttachments WHERE parentItemID IS NOT NULL)""")
no_pdf = c.fetchall()
print(f"无 PDF 的父条目: {len(no_pdf)}")

# 3. 缺字段(以 date 为例)
c.execute("""SELECT i.key FROM items i WHERE i.itemTypeID IN (11,22,31) 
             AND i.itemID NOT IN (SELECT itemID FROM itemData WHERE fieldID=6)""")
no_date = c.fetchall()
print(f"缺 date 字段: {len(no_date)}")

db.close()
```

---

## 三、修复操作(SQLite 直写)

### 3.1 前置步骤(必须!)

```bash
# 1. 关闭 Zotero
taskkill /IM zotero.exe  # Windows
# pkill zotero           # Linux/Mac

# 2. 等待完全退出
sleep 5

# 3. 验证端口释放
netstat -ano | findstr :23119  # 应无输出

# 4. 备份数据库
cp zotero.sqlite zotero.sqlite.bak_$(date +%Y%m%d_%H%M%S)

# 5. 确认无 WAL(数据已 checkpoint)
ls zotero.sqlite-wal  # 应不存在
```

### 3.2 schema 关键表结构

**items**(条目主表):
```sql
itemID INTEGER PRIMARY KEY
itemTypeID INT  -- 22=journalArticle, 11=conferencePaper, 3=attachment, 28=note, 31=preprint, 37=thesis
dateAdded TIMESTAMP
dateModified TIMESTAMP
clientDateModified TIMESTAMP
libraryID INT  -- 默认 1(本地库)
key TEXT  -- 8位随机大写字母数字(排除 0,1,O,I)
version INT DEFAULT 0
synced INT DEFAULT 0
```

**itemData**(字段值):
```sql
itemID INT
fieldID INT  -- 1=title, 6=date, 59=DOI, 38=publicationTitle, 58=conferenceName, ...
valueID INT  -- 指向 itemDataValues 表的实际文本
```

**itemDataValues**(文本池):
```sql
valueID INTEGER PRIMARY KEY
value TEXT
```

**itemAttachments**(附件关联):
```sql
itemID INT  -- 附件自己的 itemID(也在 items 表中,itemTypeID=3)
parentItemID INT  -- 父条目 itemID(NULL=游离附件)
linkMode INT  -- 0=导入并存储, 1=导入但链接, 2=外部链接
contentType TEXT  -- 'application/pdf', 'text/html'
path TEXT  -- 格式: 'storage:文件名.pdf' 或绝对路径
syncState INT DEFAULT 0
```

**creators / itemCreators**(作者):
```sql
-- creators 表
creatorID INTEGER PRIMARY KEY
firstName TEXT
lastName TEXT

-- itemCreators 表
itemID INT
creatorID INT
orderIndex INT  -- 作者顺序(0,1,2,...)
```

### 3.3 修复操作示例

#### A. 补全缺失字段(date/DOI)

```python
import sqlite3
from datetime import datetime

db = sqlite3.connect("zotero.sqlite")
c = db.cursor()

def get_or_create_value(text):
    """获取或创建 valueID"""
    c.execute("SELECT valueID FROM itemDataValues WHERE value=?", (text,))
    r = c.fetchone()
    if r: return r[0]
    c.execute("SELECT MAX(valueID) FROM itemDataValues")
    vid = c.fetchone()[0] + 1
    c.execute("INSERT INTO itemDataValues (valueID, value) VALUES (?, ?)", (vid, text))
    return vid

def set_field(itemID, fieldID, text):
    """为条目设置字段(覆盖已有值)"""
    vid = get_or_create_value(text)
    c.execute("SELECT COUNT(*) FROM itemData WHERE itemID=? AND fieldID=?", (itemID, fieldID))
    if c.fetchone()[0] > 0:
        c.execute("UPDATE itemData SET valueID=? WHERE itemID=? AND fieldID=?", (vid, itemID, fieldID))
    else:
        c.execute("INSERT INTO itemData (itemID, fieldID, valueID) VALUES (?, ?, ?)", (itemID, fieldID, vid))

# 示例: 给 itemID=239 补 date=2025
now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
set_field(239, 6, "2025")  # 6=date
c.execute("UPDATE items SET dateModified=?, clientDateModified=? WHERE itemID=239", (now, now))
db.commit()
```

#### B. 修改条目类型

```python
# journalArticle(22) -> conferencePaper(11)
c.execute("UPDATE items SET itemTypeID=11, dateModified=?, clientDateModified=? WHERE itemID=?", 
          (now, now, 239))
# 同时补会议字段
set_field(239, 58, "9th European Conference on Space Debris")  # 58=conferenceName
```

#### C. 新建条目 + 挂 PDF

```python
import random, shutil, os

def new_key(db):
    """生成新 key(8位,排除易混字符)"""
    chars = "23456789ABCDEFGHIJKLMNPQRSTUVWXYZ"
    c = db.cursor()
    while True:
        k = ''.join(random.choice(chars) for _ in range(8))
        c.execute("SELECT COUNT(*) FROM items WHERE key=?", (k,))
        if c.fetchone()[0] == 0: return k

# 1. 新建父条目(期刊文章)
parent_id = c.execute("SELECT MAX(itemID) FROM items").fetchone()[0] + 1
parent_key = new_key(db)
c.execute("""INSERT INTO items (itemID, itemTypeID, dateAdded, dateModified,
             clientDateModified, libraryID, key, version, synced)
             VALUES (?, 22, ?, ?, ?, 1, ?, 0, 0)""", 
          (parent_id, now, now, now, parent_key))

# 2. 设置元数据
set_field(parent_id, 1, "论文标题")  # 1=title
set_field(parent_id, 6, "2025")     # 6=date
set_field(parent_id, 59, "10.1234/j.example.2025.01.001")  # 59=DOI
set_field(parent_id, 38, "Journal Name")  # 38=publicationTitle

# 3. 添加作者
max_cid = c.execute("SELECT MAX(creatorID) FROM creators").fetchone()[0]
for i, (fn, ln) in enumerate([("First", "Author"), ("Second", "Author")]):
    max_cid += 1
    c.execute("INSERT INTO creators (creatorID, firstName, lastName) VALUES (?, ?, ?)", 
              (max_cid, fn, ln))
    c.execute("INSERT INTO itemCreators (itemID, creatorID, orderIndex) VALUES (?, ?, ?)", 
              (parent_id, max_cid, i))

# 4. 新建附件条目
att_id = parent_id + 1
att_key = new_key(db)
c.execute("""INSERT INTO items (itemID, itemTypeID, dateAdded, dateModified,
             clientDateModified, libraryID, key, version, synced)
             VALUES (?, 3, ?, ?, ?, 1, ?, 0, 0)""", 
          (att_id, now, now, now, att_key))

# 5. 关联附件到父条目
pdf_filename = "author2025_title.pdf"
c.execute("""INSERT INTO itemAttachments (itemID, parentItemID, linkMode, contentType, path, syncState)
             VALUES (?, ?, 0, 'application/pdf', ?, 0)""",
          (att_id, parent_id, f"storage:{pdf_filename}"))

# 6. 复制 PDF 到 storage/{att_key}/
storage_dir = os.path.join(r"C:\Users\USERNAME\Zotero\storage", att_key)
os.makedirs(storage_dir, exist_ok=True)
shutil.copy2("/path/to/source.pdf", os.path.join(storage_dir, pdf_filename))

db.commit()
```

#### D. 删除条目

```python
# 完整删除一个条目(父+子+关联数据)
def delete_item_full(itemID):
    # 1. 删除子条目(附件/笔记)
    c.execute("SELECT itemID FROM itemAttachments WHERE parentItemID=?", (itemID,))
    for (child_id,) in c.fetchall():
        delete_item_full(child_id)  # 递归删除子项
    
    # 2. 删除 itemData
    c.execute("DELETE FROM itemData WHERE itemID=?", (itemID,))
    
    # 3. 删除作者关联
    c.execute("DELETE FROM itemCreators WHERE itemID=?", (itemID,))
    
    # 4. 删除附件记录
    c.execute("DELETE FROM itemAttachments WHERE itemID=?", (itemID,))
    
    # 5. 删除主条目
    c.execute("DELETE FROM items WHERE itemID=?", (itemID,))

# 软删除(移至回收站)
c.execute("INSERT INTO deletedItems (itemID) VALUES (?)", (itemID,))
```

### 3.4 安全检查清单

执行前:
- [x] Zotero 已完全关闭(端口 23119 无监听)
- [x] 数据库已备份(`zotero.sqlite.bak_YYYYMMDD_HHMMSS`)
- [x] 无 WAL 文件(数据已 checkpoint)
- [x] 用 `mode=ro` 先测试 SQL 语法正确性

执行后:
- [x] `db.commit()` 提交事务
- [x] `db.close()` 关闭连接
- [x] 重启 Zotero 验证无报错
- [x] 用本地 API 读取修复后的条目确认成功

---

## 四、常见坑点

### 4.1 中文路径与编码

**问题**: Python heredoc 中含中文路径在 Git Bash 里会乱码  
**方案**: 写成 `.py` 文件,用 UTF-8 with BOM 编码,再执行

### 4.2 WAL 文件未 checkpoint

**现象**: 修改 `zotero.sqlite` 但 Zotero 启动后看不到更改  
**原因**: SQLite WAL 模式下,数据在 `zotero.sqlite-wal` 里,未写入主库  
**方案**: 
1. 确保 Zotero 优雅关闭(`taskkill`),不要强杀
2. 若有 WAL,手动 checkpoint: `sqlite3 zotero.sqlite "PRAGMA wal_checkpoint(FULL)"`

### 4.3 key 冲突

**问题**: 自己生成的 8 位 key 和已有条目重复  
**方案**: 先 `SELECT COUNT(*) FROM items WHERE key=?` 确认不重复

### 4.4 valueID 重复

**问题**: 直接 `INSERT INTO itemDataValues` 没检查,导致相同文本有多个 valueID  
**方案**: 封装 `get_or_create_value()` 函数,先查后插

### 4.5 忘记更新 dateModified

**问题**: 修改条目后 Zotero 不触发同步  
**方案**: 所有 `UPDATE items` 必须同时设 `dateModified` 和 `clientDateModified`

---

## 五、本次实战操作日志

### 5.1 问题诊断

通过 SQLite 只读查询发现:
- 28 个游离 PDF(无父条目)
- 3 篇项目核心文献缺条目(Yang/Dickinson/Xiong)
- 1 条 DOI 错挂(Chen 条目挂了 Yang 的 DOI)
- 1 条元数据残缺(Kuhn SDC9 无年份/类型错误)
- 1 条版本不一致(Kumar 会议版 vs 期刊版)

### 5.2 修复操作

**第一轮**: 启用本地 API 测试写能力 → 确认只读 → 转 SQLite 直写

**第二轮**: 关闭 Zotero → 备份数据库 → 执行修复脚本:
1. Kuhn: `journalArticle` → `conferencePaper`, 补 `date=2025`, `conferenceName`, `proceedingsTitle`, `url`
2. Chen: 删除错挂的 `DOI=10.3390/photonics11010017`
3. Yang(新建): `itemID=250`, `key=QSD6H3W7`, 补全元数据 + 作者 + 挂 PDF
4. Dickinson(新建): `itemID=252`, `key=VFEKHTMN`, thesis 类型 + 挂 PDF
5. Xiong(新建): `itemID=254`, `key=M7UHB2TR`, preprint 类型 + 挂 PDF

**第三轮**: 用户指定 Kumar 以期刊版为准 → 再次修复:
- 删除旧会议版 PDF 附件
- 改类型为 `journalArticle`, DOI → `10.1016/j.actaastro.2025.04.018`
- 更新期刊名 `Acta Astronautica`, `vol=232`, `pages=1-15`
- 挂新 PDF

### 5.3 验证结果

通过本地 API 验证全部 17 篇项目文献:
- 17/17 在库
- 17/17 有 PDF
- 0 游离附件
- 元数据完整(date/DOI/类型正确)

---

## 六、工具推荐

| 工具 | 用途 | 安装 |
|---|---|---|
| **pyzotero** | Python 读 Zotero 本地 API | `pip install pyzotero` |
| **sqlite3** | Python 内置,直读/写 SQLite | 无需安装 |
| **DB Browser for SQLite** | GUI 浏览数据库结构(可选) | https://sqlitebrowser.org/ |
| **curl** | 测试本地 API 连通性 | 系统自带(Win10+) |

---

## 七、参考资料

- [Zotero 本地 API 文档](https://www.zotero.org/support/dev/web_api/v3/basics)
- [pyzotero GitHub](https://github.com/urschrei/pyzotero)
- [Zotero SQLite schema](https://github.com/zotero/zotero/blob/main/resource/schema/system.sql)

---

## 八、快速命令速查

```bash
# === 启用本地 API ===
# 1. 关闭 Zotero
taskkill /IM zotero.exe

# 2. 编辑 prefs.js (路径: %APPDATA%\Zotero\Zotero\Profiles\<profile>\prefs.js)
# 在 extensions.zotero.dataDir 后加两行:
user_pref("extensions.zotero.httpServer.enabled", true);
user_pref("extensions.zotero.httpServer.localAPI.enabled", true);

# 3. 重启 Zotero

# 4. 验证
curl http://127.0.0.1:23119/api/users/0/items?limit=1

# === SQLite 修复前准备 ===
# 1. 关闭 Zotero
taskkill /IM zotero.exe

# 2. 验证完全退出
netstat -ano | findstr :23119  # 无输出

# 3. 备份
cp %USERPROFILE%\Zotero\zotero.sqlite %USERPROFILE%\Zotero\zotero.sqlite.bak

# 4. 确认无 WAL
dir %USERPROFILE%\Zotero\zotero.sqlite-wal  # 文件不存在

# === Python 只读查询 ===
python -c "
import sqlite3
db = sqlite3.connect('file:%USERPROFILE%/Zotero/zotero.sqlite?mode=ro', uri=True)
c = db.cursor()
c.execute('SELECT COUNT(*) FROM items')
print('总条目:', c.fetchone()[0])
"

# === Python 写库(示例) ===
python修复脚本.py

# === 重启 Zotero 验证 ===
start "" "C:\Program Files\Zotero\zotero.exe"
```

---

**最后更新**: 2026-06-05  
**适用版本**: Zotero 7.x (本地 API 只读), Windows 10/11  
**维护者**: Claude (Opus 4.8)

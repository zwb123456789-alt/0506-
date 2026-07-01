# Zotero v0.4 必读文献集合设置 - 操作指南

## 当前状态

- ✓ 分析脚本已创建：`zotero_setup_collections.py`
- ⚠️ Zotero 正在运行（需要关闭才能操作数据库）

## 操作步骤

### 第 1 步：关闭 Zotero

在命令行执行：

```bash
taskkill /IM zotero.exe
```

然后等待 5-10 秒，验证完全关闭：

```bash
tasklist | grep -i zotero
```

应该没有输出。

### 第 2 步：备份数据库

```bash
cd %USERPROFILE%\Zotero
copy zotero.sqlite zotero.sqlite.bak_20260629
```

### 第 3 步：确认无 WAL 文件

```bash
dir %USERPROFILE%\Zotero\zotero.sqlite-wal
```

应该显示"找不到文件"。如果存在，说明数据未完全写入，需要手动 checkpoint：

```bash
sqlite3 %USERPROFILE%\Zotero\zotero.sqlite "PRAGMA wal_checkpoint(FULL);"
```

### 第 4 步：运行脚本

```bash
cd "D:\我的文件\研究生学术\光学项目\0506新"
python zotero_setup_collections.py
```

脚本会：
1. 使用本地 API 读取"光学项目"集合的现有条目
2. 匹配 PDF 文件到 Zotero 条目
3. 提示确认操作（需要输入 `yes`）
4. 创建集合结构：
   - v0.4_BlenderOCS_必读文献
   - 6 个子集合
5. 将匹配的条目添加到对应子集合
6. 为条目添加标签：
   - v0.4必读
   - R82后主线
   - 主题标签（可观测性、光变反演等）
7. 生成报告

### 第 5 步：重启 Zotero 验证

```bash
start "" "C:\Program Files\Zotero\zotero.exe"
```

打开 Zotero 后：
1. 展开"光学项目"集合
2. 查看是否有"v0.4_BlenderOCS_必读文献"及其 6 个子集合
3. 检查各子集合中是否有对应的文献条目
4. 随机选几个条目，查看标签是否正确添加

## 安全措施

- ✓ 脚本使用事务，出错会自动回滚
- ✓ 数据库有备份
- ✓ 只添加集合和关联，不删除任何条目
- ✓ 不移动条目（只是额外加入新集合）

## 如果出错

1. 关闭 Zotero
2. 恢复备份：
   ```bash
   cd %USERPROFILE%\Zotero
   copy /Y zotero.sqlite.bak_20260629 zotero.sqlite
   ```
3. 重启 Zotero

## 预期结果

- 创建 1 个主集合 + 6 个子集合
- 约 29 篇必读文献被添加到对应子集合
- 每篇文献有 2-3 个标签
- 生成详细报告：`Zotero_v0.4必读文献整理报告.md`

## 注意

根据经验总结文档，这是**唯一可行的方法**：
- Zotero 本地 API 只能读，不能写
- 必须通过 SQLite 直写来创建集合和添加条目
- 操作前必须关闭 Zotero

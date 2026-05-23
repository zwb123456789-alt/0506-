## 🤖 Assistant


```markdown
# 人工遮挡抽查工具方案 · 给 Claude Opus 的工程执行说明

> 项目：OCS + 图像联合仿真项目  
> 当前任务：建立一个基于真实 STL 和候选面元表的“人工遮挡抽查工具”，用于可视化核验太阳方向 / 探测器方向射线是否被模型遮挡，并输出自动化抽查报告。  
> 推荐实现方式：**Blender Python 脚本 + CSV 输入 + PNG/.blend/CSV/Markdown 输出**。

---

## 1. 背景与目标

当前项目已经完成：

- 模块 A：STL → OCS / 遮挡率 / 图表 / JSON·CSV；
- 模块 B：Blender 批量渲染；
- 模块 C：姿态反演 MVP；
- 遮挡验证 V3.1：合成验证 11 项全部 PASS，真实模型 epsilon 敏感性已完成。

目前发现一个关键问题：

```text
ocs_core.py / occlusion.py 中 compute_single_attitude 使用 exclude_parts={mat_name}
导致当前部件被整体排除，从而忽略同部件内自遮挡。
```

这会造成：

```text
金属主体挡住金属主体 → 被忽略
太阳能板挡住太阳能板 → 被忽略
隐身板挡住隐身板 → 被忽略
```

已有真实模型 epsilon 敏感性结果显示同部件遮挡差异显著。因此，在进入 BRDF 精确化前，需要用真实模型做人工可视化抽查，以确认差异是否确实来自同部件遮挡漏判。

本任务的目标是实现一个工程工具：

```text
读取真实 STL + 候选面元 CSV
↓
导入 Blender 场景
↓
应用姿态
↓
显示检测点、太阳方向射线、探测器方向射线、遮挡命中点
↓
自动 ray_cast 复算遮挡
↓
输出可旋转 .blend、PNG 图像和 CSV/Markdown 抽查报告
```

---

## 2. 工程目录约定

项目根路径：

```text
D:\我的文件\研究生学术\光学项目\0506新\
```

建议新增目录：

```text
0506新/
└── ocs_project/
    └── 05_manual_review/
        ├── manual_review_blender.py
        ├── run_manual_review.bat
        ├── review_config.json          # 可选
        └── README_manual_review.md
```

输出目录：

```text
0506新/
└── 结果/
    └── 人工遮挡抽查/
        └── run_YYYYMMDD_HHMMSS/
            ├── review_report.csv
            ├── review_report.md
            ├── figures/
            │   ├── case_0001_overview.png
            │   ├── case_0001_sun_view.png       # 第二阶段可加
            │   ├── case_0001_det_view.png       # 第二阶段可加
            │   └── ...
            └── blender_files/
                ├── case_0001.blend
                └── ...
```

---

## 3. 输入数据

### 3.1 STL 模型

真实 STL 已有，路径通常为：

```text
D:\我的文件\研究生学术\光学项目\0506新\建模\jinshuzhuti.stl
D:\我的文件\研究生学术\光学项目\0506新\建模\taiyangnengban.stl
D:\我的文件\研究生学术\光学项目\0506新\建模\yinshenban.stl
```

部件名称：

| 部件名 | 含义 |
|---|---|
| `jinshuzhuti` | 金属主体 |
| `taiyangnengban` | 太阳能板 |
| `yinshenban` | 隐身板 |

---

### 3.2 候选抽查表

输入 CSV：

```text
结果/遮挡验证/run_20260512_124848/manual_review_candidates.csv
```

当前已有字段：

```csv
part_zh_en,
epsilon_mm,
face_id,
yaw_pitch_roll_zh_en,
sun_dir,
det_dir,
origin_x_mm,
origin_y_mm,
origin_z_mm,
sun_current_hit,
det_current_hit,
sun_reference_hit,
det_reference_hit,
priority,
disagree_on
```

典型行示例：

```csv
jinshuzhuti,1.0,15849,"0,0,0 / M=I","Sun=[0.958, 0.0, 0.287]","Det=[0.445, -0.891, 0.089]",85.423,573.5,325.1502,False,False,True,True,High,sun+det
```

---

## 4. 抽查策略

不需要人工看全部候选。建议分层抽样。

第一版工具支持筛选：

```text
priority = High
epsilon_mm = 1.0
max_cases = 30
```

推荐主抽查 epsilon：

```text
epsilon_mm = 1.0
```

可补充：

```text
epsilon_mm = 0.1
```

不建议第一轮人工主看：

```text
1e-6、1e-4、5.0
```

原因：

- `1e-6 mm` / `1e-4 mm` 太接近表面，容易自相交；
- `5 mm` 偏移过大，可能改变薄结构遮挡关系；
- `0.1 mm` / `1.0 mm` 更适合工程容差验证。

建议第一轮抽查规模：

| 类别 | 数量 |
|---|---:|
| `jinshuzhuti`，`sun+det` 分歧 | 5 |
| `jinshuzhuti`，仅 `sun` 分歧 | 2 |
| `jinshuzhuti`，仅 `+det` 分歧 | 2 |
| `taiyangnengban`，`sun+det` 分歧 | 5 |
| `taiyangnengban`，仅 `sun` 分歧 | 3 |
| `taiyangnengban`，仅 `+det` 分歧 | 3 |
| `yinshenban`，`sun+det` 分歧 | 3 |
| `yinshenban`，仅 `sun` 分歧 | 3 |
| `yinshenban`，仅 `+det` 分歧 | 3 |
| Low/none 阴性对照 | 每个部件 2 |

MVP 阶段也可以更简单：

```text
从 priority=High 且 epsilon=1.0 中取前 30 个。
```

---

## 5. 核心功能要求

`manual_review_blender.py` 需要实现：

### 5.1 导入真实模型

导入三个 STL：

```python
jinshuzhuti.stl
taiyangnengban.stl
yinshenban.stl
```

建议保持 STL 原始单位：

```text
mm
```

人工抽查阶段不要做 `mm → m` 转换，避免和 CSV 坐标混淆。

---

### 5.2 应用姿态

CSV 中 `yaw_pitch_roll_zh_en` 当前格式：

```text
"0,0,0 / M=I"
```

需要解析出：

```text
yaw_deg, pitch_deg, roll_deg
```

目前大多为：

```text
yaw=0, pitch=0, roll=0
```

但脚本需要保留姿态接口。

姿态矩阵应与模块 B 保持一致：

```text
R = Rz @ Ry @ Rx
```

模块 B 约定：

```text
rotate satellite, keep sun & camera fixed
```

人工抽查脚本中，如果保持 mm 单位，则：

```python
sat_root.matrix_world = R4
```

不使用 `1e-3` 缩放。

---

### 5.3 读取太阳方向和探测器方向

CSV 当前格式：

```text
sun_dir = "Sun=[0.958, 0.0, 0.287]"
det_dir = "Det=[0.445, -0.891, 0.089]"
```

脚本需要解析为三维向量：

```python
sun_dir = [0.958, 0.0, 0.287]
det_dir = [0.445, -0.891, 0.089]
```

约定：

```text
遮挡检测射线方向 = 从检测点指向太阳/探测器的方向
```

即：

```python
ray_dir_sun = normalize(sun_dir)
ray_dir_det = normalize(det_dir)
```

如果后续发现方向反了，再统一改为 `-sun_dir` / `-det_dir`。第一版应在报告中明确写出：

```text
Ray is cast from facet point toward Sun/Detector direction as listed in CSV.
```

---

### 5.4 读取检测点

CSV 当前字段：

```text
origin_x_mm
origin_y_mm
origin_z_mm
```

第一版约定：

```text
CSV 中 origin_x/y/z_mm 已经是当前射线起点，且与 STL 场景坐标一致。
```

因此直接使用：

```python
origin = Vector((origin_x_mm, origin_y_mm, origin_z_mm))
```

不再额外偏移。

---

### 5.5 可视化内容

每个 case 的 Blender 场景需要显示：

| 元素 | 显示方式 |
|---|---|
| 三个 STL 模型 | 分颜色半透明显示 |
| 当前检测点 | 黄色或红色小球 |
| 太阳方向射线 | 橙色 cylinder/curve |
| 探测器方向射线 | 蓝色 cylinder/curve |
| 太阳方向命中点 | 红色小球或叉号 |
| 探测器方向命中点 | 红色小球或叉号 |
| 未命中射线 | 延伸固定长度，末端可标注 clear |
| 当前 case 信息 | 可选：文本标注 |

推荐颜色：

| 对象 | 颜色 |
|---|---|
| `jinshuzhuti` | 银灰色，alpha=0.45~0.6 |
| `taiyangnengban` | 深蓝色，alpha=0.45~0.6 |
| `yinshenban` | 绿色或紫色，alpha=0.45~0.6 |
| 检测点 | 黄色 |
| 太阳射线 | 橙色 |
| 探测器射线 | 蓝色 |
| 命中点 | 红色 |

---

### 5.6 遮挡复算

使用 Blender 的：

```python
bpy.context.scene.ray_cast(...)
```

对两条射线分别复算：

```text
Sun ray
Detector ray
```

返回信息：

```text
hit: True/False
hit_location
hit_object
hit_face_index
hit_distance_mm
```

第一版可以用最近命中结果。

需要处理自相交：

```text
如果命中距离小于 self_hit_tol_mm，则标记为 SELF_HIT_SUSPECTED 或忽略。
```

建议参数：

```text
self_hit_tol_mm = 1e-3 或 1e-2
max_ray_dist_mm = 5000 或 10000
```

第一版逻辑：

```python
raw_hit = scene.ray_cast(...)

if raw_hit and hit_distance < self_hit_tol_mm:
    filtered_hit = False
    note = "SELF_HIT_IGNORED"
else:
    filtered_hit = raw_hit
```

注意：Blender `scene.ray_cast` 只返回最近命中。如果最近命中是自相交，严格来说应该继续找下一个交点；第一版可先忽略并标记，第二版再用 BVH/trimesh 取所有交点。

---

## 6. 报告判定标准

报告中需要输出：

```text
应遮挡 / 实际为遮挡 / 验证成功 / 验证失败
```

定义如下：

```text
应遮挡 = reference_hit
实际遮挡 = Blender manual tool filtered hit
验证成功 = 应遮挡 == 实际遮挡
验证失败 = 应遮挡 != 实际遮挡
```

对太阳方向和探测器方向分别判断：

```python
sun_should_hit = sun_reference_hit
sun_actual_hit = sun_tool_hit_filtered
sun_pass = (sun_should_hit == sun_actual_hit)

det_should_hit = det_reference_hit
det_actual_hit = det_tool_hit_filtered
det_pass = (det_should_hit == det_actual_hit)

overall_pass = sun_pass and det_pass
```

同时报告中也要保留当前算法结果：

```text
sun_current_hit
det_current_hit
```

这样可以诊断：

| current | reference | manual_tool | 解释 |
|---:|---:|---:|---|
| False | True | True | 当前算法漏判遮挡，参考算法/人工工具支持遮挡 |
| False | True | False | 参考结果可能误判，需检查方向/姿态/单位 |
| True | True | True | 一致遮挡 |
| False | False | False | 一致无遮挡 |
| True | False | True | 当前算法和人工工具认为遮挡，参考可能漏判 |

建议增加诊断标签：

```python
def diagnose(current, reference, manual):
    if reference == manual:
        if current == manual:
            return "ALL_MATCH"
        elif current is False and manual is True:
            return "CURRENT_MISSED_OCCLUSION"
        elif current is True and manual is False:
            return "CURRENT_FALSE_OCCLUSION"
    else:
        return "REFERENCE_DISAGREE_WITH_MANUAL"
```

---

## 7. 输出文件要求

每个 case 输出：

```text
figures/case_0001_<part>_f<face_id>_eps<epsilon>_overview.png
blender_files/case_0001_<part>_f<face_id>_eps<epsilon>.blend
```

第二阶段可增加：

```text
figures/case_0001_<part>_f<face_id>_eps<epsilon>_sun_view.png
figures/case_0001_<part>_f<face_id>_eps<epsilon>_det_view.png
```

总报告：

```text
review_report.csv
review_report.md
```

---

## 8. `review_report.csv` 字段

建议字段：

```csv
case_id,
part,
face_id,
epsilon_mm,
yaw_deg,
pitch_deg,
roll_deg,
origin_x_mm,
origin_y_mm,
origin_z_mm,
sun_dir_x,
sun_dir_y,
sun_dir_z,
det_dir_x,
det_dir_y,
det_dir_z,
sun_current_hit,
sun_reference_hit,
sun_tool_raw_hit,
sun_tool_filtered_hit,
sun_hit_object,
sun_hit_face_index,
sun_hit_distance_mm,
sun_pass,
sun_diagnosis,
det_current_hit,
det_reference_hit,
det_tool_raw_hit,
det_tool_filtered_hit,
det_hit_object,
det_hit_face_index,
det_hit_distance_mm,
det_pass,
det_diagnosis,
overall_pass,
priority,
disagree_on,
overview_png,
blend_file,
notes
```

---

## 9. `review_report.md` 格式

Markdown 报告建议包含：

```markdown
# 人工遮挡抽查报告

- 输入 CSV：...
- STL 模型目录：...
- 输出目录：...
- 抽查数量：...
- epsilon 筛选：...
- priority 筛选：...
- 射线约定：从检测点沿 CSV 中 Sun/Det 方向发射
- 单位约定：mm
- 自相交过滤阈值：...

## 总览统计

| 项目 | 数量 |
|---|---:|
| 总 case 数 | N |
| overall PASS | N |
| overall FAIL | N |
| sun PASS | N |
| sun FAIL | N |
| det PASS | N |
| det FAIL | N |

## Case 0001

- 部件：...
- face_id：...
- epsilon：...
- 姿态：yaw=..., pitch=..., roll=...
- 检测点：[..., ..., ...] mm
- 太阳方向：[..., ..., ...]
- 探测器方向：[..., ..., ...]

| 方向 | 当前算法 | 应遮挡(reference) | 工具实际遮挡 | 命中对象 | 命中距离/mm | 结果 | 诊断 |
|---|---:|---:|---:|---|---:|---|---|
| Sun | False | True | True | jinshuzhuti | 123.4 | PASS | CURRENT_MISSED_OCCLUSION |
| Det | False | True | False | None | - | FAIL | REFERENCE_DISAGREE_WITH_MANUAL |

图像：`figures/...overview.png`  
Blender 文件：`blender_files/...blend`
```

---

## 10. 运行方式

Blender 路径：

```text
D:\Program Files\Blender Foundation\Blender 5.0\blender.exe
```

建议 `run_manual_review.bat`：

```bat
@echo off
set BLENDER="D:\Program Files\Blender Foundation\Blender 5.0\blender.exe"
set SCRIPT="D:\我的文件\研究生学术\光学项目\0506新\ocs_project\05_manual_review\manual_review_blender.py"
set INPUT="D:\我的文件\研究生学术\光学项目\0506新\结果\遮挡验证\run_20260512_124848\manual_review_candidates.csv"
set MODEL_DIR="D:\我的文件\研究生学术\光学项目\0506新\建模"
set OUTDIR="D:\我的文件\研究生学术\光学项目\0506新\结果\人工遮挡抽查"

%BLENDER% --background --python %SCRIPT% -- ^
  --input %INPUT% ^
  --model_dir %MODEL_DIR% ^
  --outdir %OUTDIR% ^
  --max_cases 30 ^
  --epsilon_filter 1.0 ^
  --priority High ^
  --max_ray_dist_mm 10000 ^
  --self_hit_tol_mm 0.001

pause
```

打开某个 case 检查：

```bat
"D:\Program Files\Blender Foundation\Blender 5.0\blender.exe" "...\case_0001_jinshuzhuti_f15849_eps1p0.blend"
```

---

## 11. `manual_review_blender.py` 的建议命令行参数

需要支持：

```text
--input                 输入 manual_review_candidates.csv
--model_dir             STL 所在目录
--outdir                输出根目录
--max_cases             最大处理案例数
--epsilon_filter        epsilon 筛选，例如 1.0
--priority              priority 筛选，例如 High
--max_ray_dist_mm       射线最大长度，默认 10000
--self_hit_tol_mm       自相交过滤阈值，默认 0.001
--save_blend            是否保存 .blend，默认 True
--render_png            是否渲染 PNG，默认 True
```

可选第二阶段参数：

```text
--sample_strategy stratified
--cases_per_group ...
--make_sun_view
--make_det_view
--highlight_face
```

---

## 12. 脚本结构建议

`manual_review_blender.py` 内部建议函数：

```python
def parse_args():
    ...

def make_run_dir(outdir):
    ...

def load_cases(csv_path, max_cases, priority, epsilon_filter):
    ...

def parse_yaw_pitch_roll(text):
    ...

def parse_vec_from_text(text):
    ...

def str_to_bool(x):
    ...

def clear_scene():
    ...

def make_mat(name, color, alpha):
    ...

def import_stl(path, name, mat):
    ...

def create_sat_root(objects, yaw, pitch, roll):
    ...

def attitude_matrix(yaw, pitch, roll):
    ...

def create_marker_sphere(name, loc, radius, mat):
    ...

def create_cylinder_between(name, p1, p2, radius, mat):
    ...

def ray_cast_scene(origin, direction, max_dist_mm, self_hit_tol_mm):
    ...

def visualize_case(case, ray_results):
    ...

def setup_camera_overview(target, model_extent):
    ...

def render_png(path):
    ...

def save_blend(path):
    ...

def diagnose(current, reference, manual):
    ...

def write_csv_report(rows, path):
    ...

def write_md_report(rows, path):
    ...

def main():
    ...
```

---

## 13. 实现注意事项

### 13.1 单位

人工抽查工具第一版保持：

```text
mm 单位
```

不要像模块 B 那样转成 m。

因此：

```python
origin = Vector((origin_x_mm, origin_y_mm, origin_z_mm))
max_ray_dist_mm = 10000
```

---

### 13.2 姿态和坐标

当前 CSV 多数是：

```text
yaw,pitch,roll = 0,0,0
```

所以第一版不会暴露坐标系问题。

但脚本仍应实现：

```text
R = Rz @ Ry @ Rx
```

并把三个 STL 作为 `Sat_Root` 子对象统一旋转。

如果后续输入的 origin 是模型本体系点，需要做：

```python
origin_world = R @ origin_body
```

但当前第一版约定：

```text
origin_x/y/z_mm 与当前 Blender 场景坐标一致。
```

由于当前姿态是 `M=I`，该约定成立。

---

### 13.3 方向符号

必须在报告中记录射线方向约定：

```text
ray = origin + t * direction, t > 0
direction = CSV 中 Sun/Det 向量
```

如果可视化发现明显反向，再统一修正。

---

### 13.4 face_id 高亮

第一版不强制高亮 `face_id`。

原因：

```text
Blender 导入 STL 后 mesh polygon index 未必与原 Python/trimesh face_id 完全一致。
```

第一版只画检测点和射线即可满足主要目标。

第二阶段可实现：

1. 用 CSV `face_id` 尝试高亮 Blender polygon；
2. 同时用 `origin` 找最近面；
3. 比较二者是否一致；
4. 如果不一致，报告中标记。

---

### 13.5 自相交处理

当前项目核心问题不是简单 epsilon，而是：

```text
不应排除整个当前部件，应只排除起始三角面或极近距离命中。
```

人工工具第一版使用：

```python
if hit_distance < self_hit_tol_mm:
    filtered_hit = False
    note = "SELF_HIT_IGNORED"
else:
    filtered_hit = raw_hit
```

第二阶段可改为 BVH/trimesh 获取所有 hits 后过滤：

```python
valid_hits = [
    hit for hit in all_hits
    if hit.distance >= self_hit_tol_mm
    and not (hit.part == current_part and hit.face_id == current_face_id)
]
```

---

## 14. MVP 验收标准

第一版完成后，应满足：

1. 能在 Blender 5.0 headless 下运行；
2. 能读取当前 `manual_review_candidates.csv`；
3. 能筛选 `priority=High`、`epsilon=1.0`、最多 30 条；
4. 能导入三个 STL；
5. 每个 case 能生成：
   - overview PNG；
   - 可打开旋转的 `.blend`；
6. PNG 中能看见：
   - 模型；
   - 检测点；
   - 太阳射线；
   - 探测器射线；
   - 命中点；
7. 能输出 `review_report.csv`；
8. 能输出 `review_report.md`；
9. 报告中有：
   - 应遮挡；
   - 实际遮挡；
   - 当前算法结果；
   - PASS/FAIL；
   - 诊断标签；
10. 输出目录位于：

```text
D:\我的文件\研究生学术\光学项目\0506新\结果\人工遮挡抽查\run_YYYYMMDD_HHMMSS\
```

---

## 15. 第一版建议不做的事

MVP 阶段暂不需要：

- 精确 BRDF；
- 真实光照渲染；
- OSL；
- 高亮真实 `face_id`；
- 多视角 sun_view/det_view；
- HTML 交互网页；
- 全量候选抽查；
- CNN/反演相关功能。

先完成几何可视化和自动报告。

---

## 16. 后续第二阶段增强

MVP 跑通后可增加：

1. 高亮检测面元；
2. 高亮命中面元；
3. 太阳方向视角图；
4. 探测器方向视角图；
5. 多 epsilon 对比图；
6. 分层抽样策略；
7. 用 BVH/trimesh 获取所有交点并精确过滤当前面元；
8. 输出交互式 HTML；
9. 汇总统计图：
   - current vs reference vs manual；
   - 不同部件 PASS/FAIL；
   - 不同 disagree_on 类型 PASS/FAIL。

---

## 17. 与 `occlusion.py` 修正的关系

人工抽查工具的目的不是替代遮挡算法，而是为修正遮挡算法提供证据。

如果报告中大量出现：

```text
current_hit = False
reference_hit = True
manual_tool_hit = True
diagnosis = CURRENT_MISSED_OCCLUSION
```

则说明当前算法确实漏判遮挡，尤其是同部件遮挡。

下一步应修改：

```python
exclude_parts={mat_name}
```

为：

```text
不排除当前部件；
只过滤起始三角面或极近距离自交点。
```

正确遮挡逻辑应为：

```python
hits = intersect_all(origin, direction)

valid_hits = []
for hit in hits:
    if hit.distance < self_hit_tol:
        continue
    if hit.part == current_part and hit.face_id == current_face_id:
        continue
    valid_hits.append(hit)

blocked = len(valid_hits) > 0
nearest_hit = min(valid_hits, key=lambda h: h.distance) if valid_hits else None
```

---

## 18. 给 Claude Opus 的执行指令

请基于以上说明，直接实现：

```text
D:\我的文件\研究生学术\光学项目\0506新\ocs_project\05_manual_review\manual_review_blender.py
D:\我的文件\研究生学术\光学项目\0506新\ocs_project\05_manual_review\run_manual_review.bat
D:\我的文件\研究生学术\光学项目\0506新\ocs_project\05_manual_review\README_manual_review.md
```

优先完成 MVP，不要引入过多复杂功能。

实现后请进行一次 smoke test：

```text
max_cases = 3
epsilon_filter = 1.0
priority = High
```

检查是否生成：

```text
review_report.csv
review_report.md
figures/*.png
blender_files/*.blend
```

如果 Blender headless 渲染有问题，先保证 `.blend` 和 `review_report.csv` 输出，再处理 PNG 渲染。

---

## 19. 最重要的工程原则

1. **所有输出写入 `结果/`，不要写到工程代码目录。**
2. **保持 mm 单位，避免 m/mm 混淆。**
3. **姿态矩阵与模块 B 保持一致：`R = Rz @ Ry @ Rx`。**
4. **射线方向先按 CSV 中方向直接发射。**
5. **报告中必须同时保留 current/reference/manual 三套结果。**
6. **第一版不追求美观，先追求可复现、可诊断。**
7. **不要依赖画图 AI 判断遮挡；遮挡必须由 STL 几何 + 射线求交给出。**
```


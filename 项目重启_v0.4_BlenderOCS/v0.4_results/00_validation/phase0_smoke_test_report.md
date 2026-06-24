# Phase 0 单姿态 Smoke Test 报告

测试时间：2026-06-23 15:51:54  
测试类型：single_pose_smoke_test  
执行状态：✅ 通过

---

## 1. 执行环境

| 项 | 信息 |
|---|---|
| Conda 环境 | ocs_sim |
| Python 版本 | 3.9.25 |
| Python Executable | C:\Users\97466\.conda\envs\ocs_sim\python.exe |
| numpy 版本 | 1.26.4 |
| scipy 版本 | 1.13.1 |
| trimesh 版本 | 3.23.5 |
| tqdm 版本 | 4.67.3 |
| Blender 版本 | 4.2.3 LTS (build date: 2024-10-15) |
| Blender Executable | D:\Program Files\Blender Foundation\Blender 4.2\blender.exe |

---

## 2. 测试姿态

本轮只测试单姿态：

| 参数 | 值 |
|---|---|
| Yaw（偏航角） | 0° |
| Pitch（俯仰角） | 0° |
| Roll（滚转角） | 0° |
| record_id | yaw000_pitch+000 |

旋转矩阵 R (M→I)：

```
[1.0  0.0  0.0]
[0.0  1.0  0.0]
[0.0  0.0  1.0]
```

---

## 3. STL 加载测试

### 3.1 路径检查

三部件 STL 文件均存在：

| 部件 | 路径 | 状态 |
|---|---|---|
| jinshuzhuti | D:\我的文件\研究生学术\光学项目\0506新\建模\真实模型\jinshuzhuti.stl | ✅ |
| taiyangnengban | D:\我的文件\研究生学术\光学项目\0506新\建模\真实模型\taiyangnengban.stl | ✅ |
| yinshenban | D:\我的文件\研究生学术\光学项目\0506新\建模\真实模型\yinshenban.stl | ✅ |

### 3.2 加载结果

| 项 | 值 |
|---|---|
| 精度级别 | full（不抽稀） |
| decimate_ratio | 1.0 |
| 总面元数 | 481,502 |
| 加载耗时 | 0.57 秒 |

### 3.3 部件详细信息

**jinshuzhuti（金属主体）**

| 项 | 值 |
|---|---|
| 顶点数 | 227,645 |
| 面元数 | 459,634 |
| 包围盒（mm） | 1521.8 × 650.0 × 1257.2 |
| 最大尺寸（mm） | 1521.8 |

**taiyangnengban（太阳能板）**

| 项 | 值 |
|---|---|
| 顶点数 | 8,160 |
| 面元数 | 16,824 |
| 包围盒（mm） | 784.4 × 595.0 × 44.0 |
| 最大尺寸（mm） | 784.4 |

**yinshenban（隐身板）**

| 项 | 值 |
|---|---|
| 顶点数 | 2,462 |
| 面元数 | 5,044 |
| 包围盒（mm） | 380.0 × 51.0 × 800.0 |
| 最大尺寸（mm） | 800.0 |

---

## 4. BRDF 材料参数检查

当前使用 B0 baseline（phong_like_provisional_baseline）：

**jinshuzhuti（金属主体）**

| 参数 | 值 |
|---|---|
| brdf_model | phong_like_provisional_baseline |
| rho_d（漫反射系数） | 0.20 |
| rho_s（镜面反射系数） | 0.60 |
| n（Phong 指数） | 80 |
| brdf_branch | B0_baseline |

**taiyangnengban（太阳能板）**

| 参数 | 值 |
|---|---|
| brdf_model | phong_like_provisional_baseline |
| rho_d（漫反射系数） | 0.15 |
| rho_s（镜面反射系数） | 0.10 |
| n（Phong 指数） | 20 |
| brdf_branch | B0_baseline |

**yinshenban（隐身板）**

| 参数 | 值 |
|---|---|
| brdf_model | phong_like_provisional_baseline |
| rho_d（漫反射系数） | 0.08 |
| rho_s（镜面反射系数） | 0.02 |
| n（Phong 指数） | 10 |
| brdf_branch | B0_baseline |

---

## 5. Blender 调用测试

| 项 | 状态 |
|---|---|
| Blender 可执行文件存在 | ✅ |
| Blender 版本获取 | ✅ |
| Blender 版本 | 4.2.3 LTS |
| Blender 构建日期 | 2024-10-15 |
| Blender 构建时间 | 01:37:33 |

**说明**：
- 本轮只检查 Blender 可执行文件存在性和版本信息
- 未执行实际渲染
- 未生成 EXR/PNG 文件

---

## 6. 测试边界确认

本轮 smoke test 严格遵守以下边界：

✅ **已执行**：
- ocs_sim 环境下 Python、numpy、scipy、trimesh、tqdm 版本复核
- geometry_loader、config_v0_4、materials_v0_4、attitude_grid 模块导入验证
- 三部件 STL 路径存在性检查
- 单姿态（yaw=0, pitch=0, roll=0）设置
- STL 加载（不抽稀）
- mesh 基本信息记录（顶点数、面元数、包围盒）
- BRDF B0 baseline 材料参数检查
- Blender 可执行文件存在性和版本获取

❌ **未执行**（按红线要求）：
- 未运行全量 2664 姿态
- 未生成 EXR/PNG/npy 数据
- 未执行 Blender 实际渲染
- 未训练任何模型
- 未修改 13/14/24/25 号文件
- 未修改 CLAUDE.md
- 未修改书籍知识库
- 未把 B0 写成书中五参数冯模型或书中材料参数
- 未使用 latest-run 自动发现
- 未把单姿态 smoke test 写成路线一结果、论文结论或可观测性结论

---

## 7. 资源估计（单姿态）

基于当前 smoke test 结果，单姿态资源估计如下：

| 项 | 值 | 备注 |
|---|---|---|
| STL 加载耗时 | 0.57 秒 | 不抽稀，full accuracy |
| 总面元数 | 481,502 | 三部件总和 |
| 金属主体面元 | 459,634 | 占总量 95.5% |
| 太阳能板面元 | 16,824 | 占总量 3.5% |
| 隐身板面元 | 5,044 | 占总量 1.0% |

**全量 2664 姿态粗估**（仅供参考，未实际执行）：

- 如果每姿态 STL 加载耗时相同：0.57 秒 × 2664 ≈ 25 分钟
- 实际执行时可能有缓存优化，具体耗时需实际测量

**重要说明**：
- 本估计仅基于 STL 加载环节
- 未包含 Blender 渲染耗时（本轮未执行）
- 未包含数据后处理耗时
- 未包含模型训练耗时
- 全量执行前需先完成 depth round-trip sanity check

---

## 8. 下一步建议

基于本轮 smoke test 结果，建议下一步：

1. **Codex 复审本报告**：确认 smoke test 是否满足 Phase 0 最低验收点

2. **如通过，进入 depth round-trip sanity check**：
   - 选择 20 个代表性姿态
   - 执行 Blender 实际渲染
   - 验证 depth map 一致性
   - 校准 DEPTH_EPSILON_M_FINAL

3. **如 depth sanity check 通过，规划全量生成**：
   - 2664 姿态全量渲染
   - EXR/PNG/npy 数据生成
   - corpus-level I_scale 统计（两阶段流程）

4. **不建议跳过 depth sanity check 直接全量生成**

---

## 9. 附录：生成文件清单

本轮 smoke test 生成以下文件：

1. **smoke test 脚本**：
   - `06_v0.4_code/10_validation/phase0_smoke_test.py`

2. **输出报告**：
   - `v0.4_results/00_validation/phase0_smoke_test_report.md`（本文件）
   - `v0.4_results/00_validation/resource_estimate_single_pose.json`

3. **待生成 Claude 执行报告**：
   - `04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/10_1C-E05_单姿态smoke_test_Claude输出.md`

---

## 10. 测试结论

✅ **Phase 0 单姿态 smoke test 通过**

关键验证点均已确认：
- ocs_sim 环境正常
- 三部件 STL 加载成功
- geometry_loader、config、materials、attitude_grid 模块导入正常
- Blender 4.2.3 LTS 可调用
- B0 baseline 材料参数加载正常
- 单姿态旋转矩阵计算正常

本轮未发现阻断性问题，可进入下一阶段（需 Codex 复审确认）。

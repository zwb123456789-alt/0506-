# 阶段2 Claude提示词：高轨与STK场景需求设计

请只设计需求，不运行 STK，不实施仿真。

## 任务目标

判断是否需要 STK，并设计一个可服务本小项目的高轨/GEO观测场景与数据导出接口。

## 基本思路

STK 不作为最终光度模型，而作为轨道与观测几何生成器。OCS/BRDF/STL 仍由原项目代码负责。

## 必须回答

1. 是否建议建立 STK 场景？为什么？
2. 推荐优先场景：
   - GEO 定点卫星；
   - IGSO；
   - 高椭圆轨道；
   - 简化高轨距离模型。
3. STK 中需要设置哪些对象：
   - 地球；
   - 卫星；
   - 地面站；
   - 太阳；
   - 传感器/观测方向；
   - STL模型可视化。
4. 需要从 STK 导出哪些字段：
   - 时间；
   - range_km；
   - phase_angle_deg；
   - sun vector；
   - observer/detector vector；
   - target attitude；
   - azimuth/elevation；
   - eclipse flag；
   - visibility/access interval。
5. STK 导出字段如何转成 OCS 代码所需输入？
6. 如果不使用 STK，最小替代方案是什么？

## 输出要求

输出《阶段2_高轨与STK场景需求设计.md》，包含：

- STK 必要性判断；
- 推荐场景；
- 参数表；
- 导出字段表；
- 与 OCS 管线接口；
- 风险和待确认项。

## 禁止

- 不运行 STK；
- 不导入 STL；
- 不生成轨道数据；
- 不修改原大项目文件。

## 交付物

保存为：

```text
06_Claude执行方案/Claude输出/阶段2_高轨与STK场景需求设计.md
```

## 交给 Codex 审阅时重点

- STK 是否被正确定位为几何生成器；
- 导出字段是否足够支持 OCS 和星等换算；
- 是否遗漏距离、相位角、地影、观测站条件。

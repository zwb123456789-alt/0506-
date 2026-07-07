# 23B EXR 通道 smoke 摘要

读取文件：yaw2425_pitchp0225_roll+015_camera.exr

结论：全部目标通道可提取

| channel | readable | shape | finite | min | max |
|---|---|---|---|---|---|
| ViewLayer.IndexOB.X | YES | 256x256 | 65536 | 0.0 | 3.0 |
| ViewLayer.Normal.X | YES | 256x256 | 65536 | -0.7823604941368103 | 0.9993911981582642 |
| ViewLayer.Normal.Y | YES | 256x256 | 65536 | -0.9958751201629639 | 0.32437774538993835 |
| ViewLayer.Normal.Z | YES | 256x256 | 65536 | -0.9705173969268799 | 0.9990963935852051 |
| ViewLayer.Position.X | YES | 256x256 | 65536 | -0.2705264389514923 | 0.9191424250602722 |
| ViewLayer.Position.Y | YES | 256x256 | 65536 | -1.3366906642913818 | 0.20521840453147888 |
| ViewLayer.Position.Z | YES | 256x256 | 65536 | -0.5504974126815796 | 0.7071613669395447 |
| ViewLayer.Depth.Z | YES | 256x256 | 65536 | 6.199014663696289 | 10000000000.0 |

说明：本轮仅确认 IndexOB / Normal(X,Y,Z) / Position(X,Y,Z) / Depth.Z 是否可提取，
供 P4-PHYS-B 光路归因使用；本轮不做 part/material 归因。

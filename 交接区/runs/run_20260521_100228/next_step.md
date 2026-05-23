HOG image-only baseline 完成：Top1@5°=74.79%, Top5@5°=98.11%, mean=4.31°。

下一步：
1. 跑 OCS+image 联合反演（inv_joint.py），alpha sweep 得最佳融合权重
2. 与 OCS-only、image-only 对比，形成完整消融表
3. 论文定位：HOG image-only 已与 OCS per_part MLP 相当（74.79% vs 73.8%），OCS+image 联合预期可超越 OCS all raw MLP（90.7%）

暂停条件：OCS+image 联合完成后暂停。

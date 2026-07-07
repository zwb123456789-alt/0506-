# p4physA roll stability summary

## R1 top-1 roll profile (yaw=245.0, pitch=+30.0)

| roll | ocs_total |
|------|-----------|
|  -60 | 0.029717 |
|  -45 | 0.021436 |
|  -30 | 0.023280 |
|  -15 | 0.026256 |
|   +0 | 0.040841 |
|  +15 | 0.208377 |
|  +30 | 0.040846 |
|  +45 | 0.025590 |
|  +60 | 0.021980 |

Peak: roll=+15, ocs=0.208377
Sharpness ratio vs neighbors: 5.10x
glint_flag=0, saturation_flag=1 at peak

结论：
1. R1(245,30)的roll=+15是极度尖锐峰，与roll=0(0.04084)和roll=+30(0.04085)相比约高5x。
2. 现有roll档位(-60, -45, -30, -15, 0, 15, 30, 45, 60)无法判断峰值是否在+10/+12.5/+17.5/+20上偏移。
3. R1不能在未做光路诊断前直接称为glint尖峰（glint_flag=0，saturation_flag=1），
   应写作 roll-sharp / saturation-associated high-brightness candidate。

## R4 roll profile (yaw=147.5, pitch=+12.5)

R4极度鲁棒：所有roll值ocs_total在0.191-0.202之间，变化幅度<5.5%。
roll=-60: 0.201582
roll=-45: 0.201541
roll=-30: 0.201028
roll=-15: 0.201822
roll=+0: 0.201146
roll=+15: 0.197404
roll=+30: 0.194140
roll=+45: 0.192735
roll=+60: 0.191399

结论：R4是roll-robust高亮区，不是单峰；与R1的尖峰形成鲜明对比，
代表两类不同高亮机制（R1: saturation-associated sharp peak；R4: broad robust bright region）。

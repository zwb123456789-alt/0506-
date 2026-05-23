@echo off
REM 模块 B 一键调用：默认冒烟 5 帧；想跑全量删掉 --limit 5
set BLENDER="D:\Program Files\Blender Foundation\Blender 5.0\blender.exe"
set SCRIPT="%~dp0render_batch.py"
%BLENDER% --background --python %SCRIPT% -- --limit 5 --res 256 --samples 16

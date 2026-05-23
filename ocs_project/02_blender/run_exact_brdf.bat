@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

:: ============================================================
:: 模块 B exact BRDF 渲染 + 后处理（一键脚本）
:: 用法：
::   run_exact_brdf.bat              -> limit=3 res=128 smoke
::   run_exact_brdf.bat 5 256        -> limit=5 res=256
::   run_exact_brdf.bat 0 256        -> 全量 res=256
:: ============================================================

:: 环境
call conda activate ocs_sim

:: 路径
set BLENDER=D:\Program Files\Blender Foundation\Blender 4.2\blender.exe
set SCRIPT_DIR=%~dp0
set PROJECT_ROOT=D:\我的文件\研究生学术\光学项目\0506新
set OUTPUT_ROOT=%PROJECT_ROOT%\结果\模块B_渲染

:: 参数
set LIMIT=%1
if "%LIMIT%"=="" set LIMIT=3
set RES=%2
if "%RES%"=="" set RES=128

:: Step 1: 渲染几何通道
echo [Step 1] 渲染几何通道（limit=%LIMIT% res=%RES%）...
"%BLENDER%" --background --python "%SCRIPT_DIR%render_geometry_passes.py" -- --limit %LIMIT% --res %RES%
if errorlevel 1 (
    echo [FAIL] 渲染失败
    exit /b 1
)

:: Step 2: 找最新的 exact_brdf 输出目录（按修改时间倒序）
set LATEST=
for /f "delims=" %%d in ('dir /b /ad /o-d "%OUTPUT_ROOT%\run_*_exact_brdf" 2^>nul') do (
    if not defined LATEST set LATEST=%%d
)
if not defined LATEST (
    echo [FAIL] 未找到 exact_brdf 输出目录于 %OUTPUT_ROOT%
    exit /b 1
)
set OUT_DIR=%OUTPUT_ROOT%\%LATEST%
echo [INFO] OUT_DIR = %OUT_DIR%

:: Step 3: Python 后处理
echo [Step 3] BRDF 后处理...
python "%SCRIPT_DIR%brdf_postprocess.py" "%OUT_DIR%" --res %RES%
if errorlevel 1 (
    echo [FAIL] 后处理失败
    exit /b 1
)

echo.
echo DONE: %OUT_DIR%
endlocal

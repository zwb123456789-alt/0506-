@echo off
chcp 65001 >nul
cd /d "D:\我的文件\研究生学术\光学项目\0506新\ocs_project\03_inversion"
C:\Users\97466\.conda\envs\ocs_sim\python.exe -u summarize_paper_results.py > _run_summarize_log.txt 2>&1
echo Exit code: %ERRORLEVEL% >> _run_summarize_log.txt

@echo off
setlocal
cd /d %~dp0
if /I "%CONDA_DEFAULT_ENV%"=="dms-cpu" (
    python main.py
) else (
    conda run -n dms-cpu python main.py
)
endlocal

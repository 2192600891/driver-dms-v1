@echo off
setlocal
cd /d %~dp0

conda create -y -n dms-cpu python=3.10
conda install -y -n dms-cpu -c conda-forge dlib
conda run -n dms-cpu python -m pip install --upgrade pip
conda run -n dms-cpu python -m pip install -r requirements-cpu.txt

echo.
echo CPU environment is ready. Start with: run_cpu.bat
endlocal

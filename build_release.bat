@echo off
setlocal

set VERSION=1.0.3
set REPO=SaintHazzard/Script-filtrado-dinamicas
set BUILD_DIR=build
set DIST_DIR=dist
set RELEASE_DIR=releases

echo ============================
echo 📄 Compilando versión %VERSION%
echo ============================

pip install pyinstaller > nul
pyinstaller --onefile main.py --noconfirm > nul

set RELEASE_PATH=%RELEASE_DIR%\v%VERSION%
mkdir %RELEASE_PATH%

move /Y %DIST_DIR%\main.exe %RELEASE_PATH%\consolidado-dinamicas-v%VERSION%.exe > nul

rmdir /s /q %BUILD_DIR%
del main.spec

(
echo {
echo   "version": "%VERSION%",
echo   "url": "https://github.com/%REPO%/releases/download/v%VERSION%/consolidado-dinamicas-v%VERSION%.exe"
echo }
) > version.json

echo

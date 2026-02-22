@echo off
setlocal

cd /d %~dp0\..

if not exist .venv (
  py -m venv .venv
)

call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install pyinstaller

pyinstaller --clean --noconfirm --onefile --name CSVoiceIntake ^
  --add-data "templates;templates" ^
  --add-data "static;static" ^
  windows_app.py

echo.
echo Build complete. EXE path: dist\CSVoiceIntake.exe

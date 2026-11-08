@echo off
rem Gera dist\RaizesNumericas.exe, que roda em Windows sem Python instalado.
cd /d "%~dp0.."
python -m pip install --quiet --disable-pip-version-check -e . pyinstaller || exit /b 1
python -m PyInstaller --noconfirm --onefile --windowed --name RaizesNumericas scripts\abrir_interface.py

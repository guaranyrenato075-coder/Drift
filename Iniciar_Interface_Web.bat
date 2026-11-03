@echo off
title Servidor Drift IA - Piloto Automatico
cd /d "%~dp0drift-ai-editor"
echo ========================================================
echo    Iniciando Servidor Drift IA em http://127.0.0.1:8765
echo ========================================================
python web_ui.py
pause


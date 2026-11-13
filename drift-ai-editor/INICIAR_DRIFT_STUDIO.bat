@echo off
chcp 65001 >nul
title Drift - Editor Nativo
cls

echo ======================================================================
echo                      INICIANDO DRIFT SOFTWARE
echo ======================================================================
echo.
echo [1/2] Ativando motor de Inteligencia Artificial em segundo plano...
cd /d "%~dp0"
start "Drift AI Daemon" /min python web_ui.py

echo [2/2] Abrindo o Software Nativo Drift...
cd /d "D:\CUTWIREDRIFT\Drift"
start "" "D:\CUTWIREDRIFT\Drift\drift.exe"

echo.
echo [OK] O Software Nativo Drift foi aberto com sucesso na sua tela!
timeout /t 3 /nobreak >nul
exit

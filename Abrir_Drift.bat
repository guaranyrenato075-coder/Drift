@echo off
title Abrindo Drift Video Editor...
set QSG_RHI_BACKEND=opengl
cd /d "%~dp0Drift"
start "" "%~dp0Drift\drift.exe" %*
exit


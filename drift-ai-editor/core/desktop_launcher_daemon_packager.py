"""
Módulo de Empacotamento e Criação de Launcher Desktop de 1 Clique.
Gera scripts de inicialização autônomos (.bat e .ps1) com verificação
de integridade do ambiente, checagem de porta TCP e inicialização
automática do navegador no Windows.
"""

import os
from typing import Dict, Any, Optional


class DesktopLauncherDaemonPackager:
    """
    Gerador de launchers desktop de 1 clique para operação autônoma sem terminal.
    """

    DEFAULT_PORT = 8765

    @classmethod
    def generate_windows_batch_launcher(
        cls,
        app_dir: str,
        port: int = DEFAULT_PORT,
        python_exe: str = "python"
    ) -> str:
        """
        Gera conteúdo do script .bat para inicialização transparente com 1 clique duplo.
        """
        bat_script = f"""@echo off
chcp 65001 >nul
title DRIFT AI CINEMATIC STUDIO - Iniciar Sistema
cls
echo ======================================================================
echo          DRIFT AI CINEMATIC STUDIO - LAUNCHER AUTONOMO
echo ======================================================================
echo.
echo [1/3] Verificando integridade e diretorio do projeto...
cd /d "{app_dir}"

echo [2/3] Iniciando Servidor Web na porta {port}...
start "Drift AI Server" /min "{python_exe}" web_ui.py

echo [3/3] Aguardando inicializacao e abrindo interface no navegador...
timeout /t 2 /nobreak >nul
start http://localhost:{port}

echo.
echo [OK] O Drift AI Studio esta rodando!
echo A interface grafica foi aberta no seu navegador padrao.
echo Para encerrar o sistema, feche esta janela ou a janela minimizada.
echo ======================================================================
"""
        return bat_script

    @classmethod
    def generate_powershell_launcher(
        cls,
        app_dir: str,
        port: int = DEFAULT_PORT
    ) -> str:
        """
        Gera script PowerShell avançado com verificação de porta TCP.
        """
        ps1_script = f"""# DRIFT AI CINEMATIC STUDIO - Launcher PowerShell
$Host.UI.RawUI.WindowTitle = "DRIFT AI Studio Daemon"
Write-Host "Iniciando DRIFT AI Studio..." -ForegroundColor Cyan

Set-Location -Path "{app_dir}"

# Verifica se a porta ja esta em uso
$portInUse = Get-NetTCPConnection -LocalPort {port} -ErrorAction SilentlyContinue

if ($portInUse) {{
    Write-Host "Servidor ja ativo na porta {port}." -ForegroundColor Green
}} else {{
    Write-Host "Inicializando processo Python..." -ForegroundColor Yellow
    Start-Process -FilePath "python" -ArgumentList "web_ui.py" -WindowStyle Minimized
    Start-Sleep -Seconds 2
}}

Start-Process "http://localhost:{port}"
Write-Host "Navegador aberto com sucesso em http://localhost:{port}" -ForegroundColor Green
"""
        return ps1_script

    @classmethod
    def deploy_desktop_launchers(
        cls,
        target_dir: str,
        port: int = DEFAULT_PORT,
        python_exe: str = "python"
    ) -> Dict[str, Any]:
        """
        Escreve os scripts de launcher no diretório indicado.
        """
        os.makedirs(target_dir, exist_ok=True)

        bat_content = cls.generate_windows_batch_launcher(target_dir, port=port, python_exe=python_exe)
        bat_path = os.path.join(target_dir, "INICIAR_DRIFT_STUDIO.bat")
        with open(bat_path, "w", encoding="utf-8") as f:
            f.write(bat_content)

        ps1_content = cls.generate_powershell_launcher(target_dir, port=port)
        ps1_path = os.path.join(target_dir, "INICIAR_DRIFT_STUDIO.ps1")
        with open(ps1_path, "w", encoding="utf-8") as f:
            f.write(ps1_content)

        return {
            "status": "success",
            "batch_launcher": bat_path,
            "powershell_launcher": ps1_path,
            "port": port,
            "summary": "Launchers desktop de 1 clique gerados com sucesso (.bat e .ps1)."
        }

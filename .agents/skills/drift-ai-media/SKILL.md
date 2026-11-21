---
name: drift-ai-media
description: Arquitetura, pipeline de mídia com IA e validação multiplataforma (Android, macOS, Windows) do projeto Drift. Use ao implementar edição de vídeo/áudio, sincronização, transcrição ou corrigir falhas no CTest/CI.
---

# Diretrizes de Engenharia — CutWire Drift

## 1. Camada de Mídia e IA (Local-First & Decoupled)

- **Desacoplamento de Core:** 
  O motor de vídeo/áudio do Drift é implementado em C++20 / Qt 6 / CMake. O subsistema de automação de inteligência artificial (`drift-ai-editor`) roda desacoplado como um serviço local via **Model Context Protocol (MCP)** e endpoints HTTP assíncronos.
  - Nunca acople dependências pesadas de IA (PyTorch, bibliotecas Python nativas de SO) diretamente na árvore de compilação C++ compartilhada do desktop/mobile.
  - A comunicação entre o QML (`ScriptAiTab.qml`) e o módulo de IA é feita via requisições assíncronas JSON para o MCP Client / WebUI local (`127.0.0.1:8765`), garantindo builds limpos e portáveis em **Android, macOS e Windows**.

- **Pipeline de Áudio e Montagem:**
  - *Transcrição Acústica e Alinhamento:* Extrair faixa de voz mono (WAV/MP3) → segmentar carimbos temporais de fala por palavra → ancorar início e fim de cena nos limites exatos dos cues de legenda para sincronização matemática frame-perfect (`0.000000s` de resíduo).
  - *Mitigação de Monotonia Visual:* Alternar dinamicamente entre imagens de alta resolução com animações Ken Burns variadas (zooms e pans controlados) e vídeos B-Roll históricos autênticos.
  - *Normalização e Silenciamento:* Faixas de vídeo de apoio devem ter áudio nativo silenciado (`volume: 0.0`) na timeline para não sobrepor a narração master.

## 2. Qualidade, Testes e CI Multiplataforma (GitHub Actions)

- **Validação Obrigatória:**
  - Execute a suíte de testes unitários do editor de IA (`python -m unittest discover`) e os testes nativos do C++ (`ctest --test-dir build --output-on-failure`).
  - Nunca deixe caminhos de arquivo dependentes de separador de SO (sempre normalize barras `/` vs `\`).

- **Compatibilidade de Runners no GitHub Actions:**
  - **macOS:** Utilize runners Apple Silicon válidos (`macos-14` ou `macos-15`). Nunca aponte para versões inexistentes (`macos-26`).
  - **Android:** Ao instalar kits Qt para Android via `aqtinstall`, assegure permissão de execução (`chmod +x`) em `$KIT/bin` e `$KIT/libexec` para que o utilitário `qt-cmake` seja executável pelo script de compilação `build.sh`.
  - **Resiliência de Dependências Externas:** Downloads de pacotes do repositório público `Drift-Addons` devem possuir fallback direto com `curl -fsSL` caso o `gh release download` falhe por falta de permissões de token em forks.

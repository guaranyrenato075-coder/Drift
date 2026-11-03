# Drift AI Editor - Roteiro, Narração e Montagem Automática com IA

Sistema completo de edição audiovisual com inteligência artificial para o **CutWire Drift**, operando sobre a API nativa MCP (Model Context Protocol).

---

## 🚀 Recursos Implementados

1. **Roteiro Estruturado e Texto Corrido:**
   - Suporte a formato com tags (`CENA 01`, `NARRAÇÃO:`, `DESCRIÇÃO VISUAL:`, `DURAÇÃO:`) ou prosa contínua.
   - **Gerador de Roteiro com IA:** cria roteiros prontos por tema (Estoicismo, Tecnologia, Universo, Produtividade, etc.).
2. **Motor de Voz Nativo Chatterbox (Local):**
   - Síntese vocal em português (`pt`) e mais 20 idiomas sem custo de API externa.
   - Medição da duração real por cena.
   - **Clonagem de Voz (`add_voice`):** clone sua própria voz a partir de 5 a 15 segundos de áudio.
3. **Busca Híbrida de Mídia (Vídeos e Imagens):**
   - Integração com **Pexels**, **Pixabay**, **Wikimedia Commons** e **NASA**.
   - Filtro configurável: *Apenas Vídeos*, *Apenas Imagens* ou *Vídeos e Imagens*.
   - Download seguro, validação de integridade e cache local atômico.
4. **Montagem Cinematográfica na Timeline do Drift:**
   - **Efeito Ken Burns:** zoom suave e dinâmico automático em fotos/imagens estáticas.
   - **Transições Cinematográficas:** *Crossfade*, *Luma Fade* ou *Dip* aplicadas automaticamente entre cenas.
   - **Trilha Sonora com Auto-Ducking (`duck_under`):** a música de fundo abaixa suavemente de volume enquanto o narrador fala.
   - **Legendas Sincronizadas:** cues temporizados palavra a palavra ou por cena.
   - **Silenciamento dos Vídeos de Apoio:** áudio nativo de stock silenciado para não sujar a narração.

---

## 🛠️ Como Utilizar

### Interface Visual Interativa (Web UI)
Inicie o painel:
```powershell
python drift-ai-editor\web_ui.py
```
O navegador abrirá automaticamente em [http://127.0.0.1:8765](http://127.0.0.1:8765).

### Linha de Comando (CLI)
```powershell
# 1. Verificar status do Chatterbox e MCP
python drift-ai-editor\main.py status

# 2. Criar projeto a partir de roteiro
python drift-ai-editor\main.py plan --script "CENA 01`nNARRAÇÃO: Olá mundo.`nDESCRIÇÃO VISUAL: Céu azul." --aspect-ratio 16:9 --media-type all

# 3. Gerar vozes locais Chatterbox
python drift-ai-editor\main.py voice --project-id <ID>

# 4. Buscar mídias correspondentes
python drift-ai-editor\main.py search --project-id <ID>

# 5. Montar timeline no Drift
python drift-ai-editor\main.py build --project-id <ID>
```

---

## 🧪 Testes Automatizados
```powershell
python -m unittest discover -s drift-ai-editor/tests -p "test_*.py"
```
Todos os 21 testes unitários passam com **OK**.

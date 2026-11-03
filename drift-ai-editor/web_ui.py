import http.server
import socketserver
import json
import urllib.parse
from pathlib import Path
from typing import Dict, Any, List, Optional
import sys

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, str(Path(__file__).resolve().parent))

from storage.repository import ProjectRepository
from models.scene_plan import ProjectPlan, ProjectConfig, Scene, SceneState
from analysis.segmenter import ScriptSegmenter
from analysis.visual_planner import VisualPlanner
from analysis.script_generator import ScriptGenerator
from editing.drift_mcp_client import DriftMcpClient
from voice.voice_engine import DriftChatterboxEngine
from core.lazy_provider_registry import LazyProviderRegistry
from core.memory_manager import MemoryManager
from core.smart_cache import GLOBAL_CACHE
from director.context_pruner import ContextPruner
from media.downloader import MediaDownloader
from editing.timeline_builder import TimelineBuilder
from editing.export_manager import ExportManager
from analysis.storyboard_engine import StoryboardEngine
from skills.gemini_skill_bridge import GeminiSkillBridge
from pipeline.platform_policy_manager import PlatformPolicyManager
from media.media_ranker import MediaRanker
from media.local_indexer import LocalMediaIndexer
from media.license_manifest import LicenseManifestManager
from media.copyright_analyzer import CopyrightAnalyzer
from audio.auto_ducking_soundtrack import AutoDuckingSoundtrackMixer
from pipeline.hybrid_multiformat_producer import HybridMultiFormatProducer, FramingMode
from pipeline.thumbnail_studio import ThumbnailStudio
from pipeline.publication_seo_kit import PublicationSeoKitGenerator
from core.hardware_telemetry import HardwareTelemetryProfiler
from pipeline.chunked_parallel_renderer import ChunkedParallelRenderer
from editing.karaoke_subtitle_generator import KaraokeSubtitleGenerator
from voice.local_neural_fallback import LocalNeuralVoiceFallback
from core.ram_disk_buffer import RamDiskBufferManager
from storage.media_deduplicator import MediaDeduplicator
from media.speculative_prefetcher import SpeculativeMediaPrefetcher
from editing.adaptive_crf_encoder import AdaptiveCrfEncoder

RAM_BUFFER = RamDiskBufferManager()
MEDIA_DEDUP = MediaDeduplicator()
PREFETCHER = SpeculativeMediaPrefetcher(max_workers=4)
from pipeline.batch_production_factory import BatchProductionFactory
BATCH_FACTORY = BatchProductionFactory()
from pipeline.style_engine import StyleEngine
from pipeline.timeline_planner import TimelinePlanner
from pipeline.quality_control import QualityControlEngine

HTML_PAGE = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <title>Drift - Roteiro IA</title>
  <style>
    :root {
      --bg: #141517;
      --panel-bg: #1e2023;
      --card-bg: #272a2e;
      --border: #383c42;
      --accent: #3b82f6;
      --accent-hover: #2563eb;
      --text: #f3f4f6;
      --text-muted: #9ca3af;
      --success: #10b981;
      --warning: #f59e0b;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
    body { background: var(--bg); color: var(--text); display: flex; height: 100vh; overflow: hidden; }
    
    /* Sidebar */
    .sidebar { width: 340px; background: var(--panel-bg); border-right: 1px solid var(--border); display: flex; flex-direction: column; }
    .sidebar-header { padding: 18px; border-bottom: 1px solid var(--border); display: flex; align-items: center; justify-content: space-between; }
    .sidebar-header h2 { font-size: 1.1rem; font-weight: 700; color: #fff; }
    .badge { background: #1e3a8a; color: #93c5fd; padding: 2px 8px; border-radius: 999px; font-size: 0.75rem; }
    
    .sidebar-content { flex: 1; overflow-y: auto; padding: 16px; display: flex; flex-direction: column; gap: 14px; }
    label { font-size: 0.8rem; font-weight: 600; color: var(--text-muted); text-transform: uppercase; margin-bottom: 4px; display: block; }
    input, select, textarea { width: 100%; background: var(--card-bg); border: 1px solid var(--border); color: #fff; padding: 10px; border-radius: 6px; font-size: 0.9rem; }
    input:focus, select:focus, textarea:focus { outline: none; border-color: var(--accent); }
    textarea { height: 160px; resize: vertical; line-height: 1.4; }
    
    .btn { background: var(--accent); color: #fff; border: none; padding: 10px 16px; border-radius: 6px; font-weight: 600; cursor: pointer; display: inline-flex; align-items: center; justify-content: center; gap: 8px; font-size: 0.88rem; transition: background 0.15s; }
    .btn:hover { background: var(--accent-hover); }
    .btn-secondary { background: var(--card-bg); border: 1px solid var(--border); color: #e5e7eb; }
    .btn-secondary:hover { background: #32363b; }
    .btn-success { background: var(--success); }
    .btn-success:hover { background: #059669; }
    
    /* Main Area */
    .main { flex: 1; display: flex; flex-direction: column; background: var(--bg); overflow: hidden; }
    .topbar { height: 60px; background: var(--panel-bg); border-bottom: 1px solid var(--border); display: flex; align-items: center; justify-content: space-between; padding: 0 24px; }
    .topbar-title { font-weight: 600; font-size: 1.05rem; }
    
    .content-area { flex: 1; overflow-y: auto; padding: 24px; display: flex; flex-direction: column; gap: 18px; }
    
    .scenes-grid { display: flex; flex-direction: column; gap: 16px; }
    .scene-card { background: var(--panel-bg); border: 1px solid var(--border); border-radius: 8px; padding: 18px; display: grid; grid-template-columns: 80px 1fr 1fr 200px; gap: 18px; align-items: start; }
    .scene-order { font-size: 1.4rem; font-weight: 800; color: var(--accent); text-align: center; background: var(--card-bg); border-radius: 6px; padding: 12px 0; border: 1px solid var(--border); }
    .scene-narration h4, .scene-visual h4 { font-size: 0.8rem; color: var(--text-muted); text-transform: uppercase; margin-bottom: 6px; }
    .scene-meta { display: flex; flex-direction: column; gap: 8px; font-size: 0.8rem; }
    .status-pill { display: inline-block; padding: 4px 8px; border-radius: 4px; font-weight: 600; text-align: center; }
    .status-pending { background: #374151; color: #d1d5db; }
    .status-ready { background: #064e3b; color: #6ee7b7; }
    .status-error { background: #7f1d1d; color: #fca5a5; }
    
    .tags { display: flex; flex-wrap: wrap; gap: 4px; margin-top: 6px; }
    .tag { background: #1e293b; color: #94a3b8; font-size: 0.72rem; padding: 2px 6px; border-radius: 4px; }
    
    #status-banner { padding: 12px 18px; background: #1e3a8a; border-radius: 6px; font-size: 0.88rem; display: none; }
  </style>
</head>
<body>
  <!-- Sidebar -->
  <div class="sidebar">
    <div class="sidebar-header">
      <h2>Drift: Roteiro IA</h2>
      <span class="badge">Nativo MCP</span>
    </div>
    <div class="sidebar-content">
      <div style="background: var(--card-bg); padding: 10px; border-radius: 6px; border: 1px solid var(--border);">
        <label style="color: #60a5fa;">💡 Gerador de Roteiro com IA</label>
        <div style="display: flex; gap: 6px;">
          <input type="text" id="ai-topic" placeholder="Tema: Estoicismo, Universo..." value="Estoicismo">
          <button class="btn" style="background:#2563eb; padding: 6px 12px; font-size: 0.8rem; white-space: nowrap;" onclick="gerarRoteiroPorIA()">Criar</button>
        </div>
      </div>

      <div>
        <label>Título do Projeto</label>
        <input type="text" id="project-title" value="A Arte da Disciplina">
      </div>
      <div>
        <label>Roteiro Completo (Texto ou Cenas)</label>
        <textarea id="script-input" placeholder="Cole seu roteiro aqui... Ex:
CENA 01
NARRAÇÃO: Você não controla tudo o que acontece.
DESCRIÇÃO VISUAL: Homem observando a chuva pela janela.

CENA 02
NARRAÇÃO: Mas pode controlar sua reação.
DESCRIÇÃO VISUAL: Pessoa caminhando ao amanhecer.">CENA 01
NARRAÇÃO: Você não controla tudo o que acontece.
DESCRIÇÃO VISUAL: Um homem observa uma tempestade pela janela.

CENA 02
NARRAÇÃO: Mas pode controlar a maneira como você reage.
DESCRIÇÃO VISUAL: Uma pessoa meditando em silêncio ao amanhecer.</textarea>
      </div>
      
      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px;">
        <div>
          <label>Formato do Vídeo</label>
          <select id="aspect-ratio">
            <option value="16:9">Horizontal (16:9)</option>
            <option value="9:16">Vertical Reels (9:16)</option>
            <option value="1:1">Quadrado (1:1)</option>
          </select>
        </div>
        <div>
          <label>Tipo de Mídia</label>
          <select id="media-type">
            <option value="all" selected>Vídeos e Imagens</option>
            <option value="video">Apenas Vídeos</option>
            <option value="image">Apenas Imagens</option>
          </select>
        </div>
      </div>

      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px;">
        <div>
          <label>Transições</label>
          <select id="transition-kind">
            <option value="crossfade" selected>Crossfade Suave</option>
            <option value="luma_fade">Luma Fade</option>
            <option value="dip">Dip to Black</option>
            <option value="none">Sem Transição</option>
          </select>
        </div>
        <div>
          <label>Efeito Ken Burns</label>
          <select id="ken-burns">
            <option value="true" selected>Ativado (Zoom)</option>
            <option value="false">Desativado</option>
          </select>
        </div>
      </div>

      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px;">
        <div>
          <label>Idioma Voz</label>
          <select id="voice-lang">
            <option value="pt" selected>Português (pt)</option>
            <option value="en">Inglês (en)</option>
            <option value="es">Espanhol (es)</option>
          </select>
        </div>
        <div>
          <label>Expressividade</label>
          <input type="number" id="exaggeration" min="0.25" max="2.0" step="0.1" value="0.5">
        </div>
      </div>

      <button class="btn" onclick="analisarRoteiro()">1. Analisar Roteiro & Cenas</button>
      <button class="btn btn-secondary" onclick="gerarVozes()">2. Gerar Voz Chatterbox</button>
      <button class="btn btn-secondary" onclick="pesquisarVideos()">3. Buscar Vídeos & Imagens</button>
      <button class="btn btn-success" onclick="montarNaTimeline()">4. Montar na Timeline Drift</button>
      <button class="btn" style="background:#e11d48;" onclick="exportarVideo()">5. Exportar Vídeo Final (MP4)</button>
      <button class="btn btn-secondary" style="border-color:#3b82f6; color:#93c5fd;" onclick="abrirNoDrift()">🖥️ Abrir Projeto no Drift</button>
      <button class="btn btn-secondary" style="border-color:#10b981; color:#6ee7b7;" onclick="abrirAuditoriaCopyright()">🛡️ Auditoria Direitos Autorais</button>
      <button class="btn btn-secondary" style="border-color:#f59e0b; color:#fbbf24;" onclick="abrirKitPublicacao()">🚀 Kit Publicação & SEO</button>
      <button class="btn btn-secondary" style="border-color:#8b5cf6; color:#c4b5fd;" onclick="abrirThumbnailStudio()">🖼️ Thumbnails (CTR Heatmap)</button>
      <button class="btn btn-secondary" style="border-color:#06b6d4; color:#67e8f9;" onclick="abrirRenderParalelo()">⚡ Render Paralelo (24T/GPU)</button>
      <button class="btn btn-secondary" style="border-color:#ec4899; color:#f472b6;" onclick="gerarLegendasKaraoke()">✨ Legendas Karaokê (.ASS)</button>
      <button class="btn btn-secondary" style="border-color:#10b981; color:#a7f3d0;" onclick="abrirRamDiskStats()">💾 RAM-Disk Buffer (Zero Lag)</button>
      <button class="btn btn-secondary" style="border-color:#38bdf8; color:#bae6fd;" onclick="abrirBitrateAdaptativo()">🎛️ Bitrate Adaptativo (CRF)</button>
      <button class="btn btn-secondary" style="border-color:#eab308; color:#fde047; font-weight:700;" onclick="abrirPilotoAutomatico()">🏭 Piloto Automático em Lote</button>

      <div style="margin-top: 10px; border-top: 1px solid var(--border); padding-top: 10px;">
        <label style="color: #a78bfa;">🎙️ Clonagem de Voz (Chatterbox)</label>
        <div style="display: flex; flex-direction: column; gap: 6px;">
          <input type="text" id="clone-name" placeholder="Nome da voz (ex: MinhaVoz)">
          <input type="text" id="clone-path" placeholder="Caminho do áudio WAV/MP3 (5-15s)">
          <button class="btn btn-secondary" style="font-size: 0.8rem;" onclick="clonarVoz()">Clonar Amostra de Voz</button>
        </div>
      </div>
    </div>
  </div>

  <!-- Main Area -->
  <div class="main">
    <div class="topbar">
      <div style="display:flex; align-items:center; gap:12px;">
        <div class="topbar-title" id="project-header">Projeto: Novo</div>
        <div id="stats-summary" style="font-size: 0.85rem; color: var(--text-muted);">0 cenas | 0.0s duração</div>
      </div>
      <div id="telemetry-badge" style="display:flex; align-items:center; gap:8px; font-size:0.78rem; background:var(--card-bg); border:1px solid var(--border); padding:5px 12px; border-radius:6px;">
        <span style="color:#10b981;">●</span>
        <span id="telemetry-cpu" style="color:#93c5fd; font-weight:600;">CPU: 24 Threads</span>
        <span style="color:var(--border);">|</span>
        <span id="telemetry-ram" style="color:#a7f3d0;">RAM: 32 GB</span>
        <span style="color:var(--border);">|</span>
        <span id="telemetry-encoder" style="color:#fef08a;">Encoder: CPU Multithread</span>
      </div>
    </div>

    <div class="content-area">
      <div id="status-banner"></div>
      <div class="scenes-grid" id="scenes-container">
        <div style="text-align: center; color: var(--text-muted); padding: 60px 0;">
          Clique em <b>1. Analisar Roteiro</b> para gerar a estrutura de cenas e palavras-chave.
        </div>
      </div>
    </div>
  </div>

  <script>
    let currentPlan = null;

    function showStatus(text, bg = '#1e3a8a') {
      const banner = document.getElementById('status-banner');
      banner.style.display = 'block';
      banner.style.background = bg;
      banner.innerText = text;
    }

    async function gerarRoteiroPorIA() {
      const topic = document.getElementById('ai-topic').value;
      if (!topic) return alert('Digite um tema para o roteiro!');
      showStatus(`Gerando roteiro com IA sobre "${topic}"...`);
      const res = await fetch('/api/generate_script', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ topic })
      });
      const data = await res.json();
      if (data.ok && data.script) {
        document.getElementById('script-input').value = data.script;
        document.getElementById('project-title').value = `Vídeo: ${topic}`;
        showStatus('Roteiro gerado com sucesso! Clique em "1. Analisar Roteiro"', '#065f46');
      } else {
        showStatus('Falha ao gerar roteiro', '#7f1d1d');
      }
    }

    async function clonarVoz() {
      const name = document.getElementById('clone-name').value;
      const path = document.getElementById('clone-path').value;
      if (!name || !path) return alert('Informe o nome e o caminho do arquivo de áudio (5 a 15s)!');
      showStatus(`Clonando voz "${name}" via Chatterbox local (aguarde)...`);
      const res = await fetch('/api/clone_voice', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, path })
      });
      const data = await res.json();
      if (data.ok) {
        showStatus(`Voz "${name}" clonada com sucesso e adicionada à biblioteca!`, '#065f46');
      } else {
        showStatus(`Erro ao clonar voz: ${data.error}`, '#7f1d1d');
      }
    }

    async function analisarRoteiro() {
      showStatus('Analisando roteiro com segmentador e planejador visual...');
      const script = document.getElementById('script-input').value;
      const title = document.getElementById('project-title').value;
      const ratio = document.getElementById('aspect-ratio').value;
      const mediaType = document.getElementById('media-type').value;
      const transition = document.getElementById('transition-kind').value;
      const kenBurns = document.getElementById('ken-burns').value === 'true';
      const lang = document.getElementById('voice-lang').value;
      const exag = parseFloat(document.getElementById('exaggeration').value);

      const res = await fetch('/api/plan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          script,
          title,
          aspect_ratio: ratio,
          media_type: mediaType,
          transition_kind: transition,
          enable_ken_burns: kenBurns,
          language: lang,
          exaggeration: exag
        })
      });
      const data = await res.json();
      currentPlan = data.plan;
      renderScenes();
      showStatus(`Roteiro dividido em ${currentPlan.scenes.length} cenas com sucesso!`, '#065f46');
    }

    async function gerarVozes() {
      if (!currentPlan) return alert('Analise o roteiro primeiro!');
      showStatus('Gerando narrações locais com Chatterbox via Drift MCP (aguarde)...');
      const res = await fetch('/api/voice', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ project_id: currentPlan.project_id })
      });
      const data = await res.json();
      currentPlan = data.plan;
      renderScenes();
      showStatus(`Narrações geradas com sucesso! Duração total: ${data.total_duration}s`, '#065f46');
    }

    async function pesquisarVideos() {
      if (!currentPlan) return alert('Analise o roteiro primeiro!');
      showStatus('Pesquisando vídeos correspondentes em Pexels, Pixabay, Wikimedia e NASA...');
      const res = await fetch('/api/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ project_id: currentPlan.project_id })
      });
      const data = await res.json();
      currentPlan = data.plan;
      renderScenes();
      showStatus('Pesquisa de clipes concluída!', '#065f46');
    }

    async function montarNaTimeline() {
      if (!currentPlan) return alert('Analise o roteiro primeiro!');
      showStatus('Baixando clipes e montando timeline nativa no Drift...');
      const res = await fetch('/api/build', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ project_id: currentPlan.project_id })
      });
      const data = await res.json();
      currentPlan = data.plan;
      renderScenes();
      showStatus('Sucesso! Vídeo, áudio e legendas sincronizados na timeline do Drift!', '#065f46');
    }

    async function exportarVideo() {
      if (!currentPlan) return alert('Monte a timeline primeiro!');
      showStatus('Renderizando e exportando vídeo MP4 com o Drift nativo (aguarde)...');
      const res = await fetch('/api/export', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ project_id: currentPlan.project_id })
      });
      const data = await res.json();
      if (data.ok) {
        showStatus(`Vídeo exportado com sucesso em: ${data.output_path}`, '#065f46');
      } else {
        showStatus(`Erro na exportação: ${data.error}`, '#7f1d1d');
      }
    }

    async function abrirNoDrift() {
      showStatus('Abrindo aplicativo Drift com o projeto na sua tela...');
      const res = await fetch('/api/open_drift', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ project_id: currentPlan ? currentPlan.project_id : null })
      });
      const data = await res.json();
      if (data.ok) {
        showStatus(`Aplicativo Drift aberto com o projeto: ${data.opened || ''}`, '#065f46');
      } else {
        showStatus(`Erro ao abrir Drift: ${data.error}`, '#7f1d1d');
      }
    }

    async function abrirAuditoriaCopyright() {
      if (!currentPlan) return alert('Carregue ou crie um projeto primeiro!');
      showStatus('Auditorando direitos autorais das mídias...', '#059669');
      try {
        const res = await fetch(`/api/copyright_audit?project_id=${currentPlan.project_id}`);
        const data = await res.json();
        if (!data.ok) return alert('Erro ao auditar direitos autorais: ' + (data.error || 'Desconhecido'));

        const modal = document.getElementById('copyright-modal');
        const body = document.getElementById('copyright-modal-body');

        let statusColor = data.is_safe_for_monetization ? '#10b981' : '#ef4444';
        let statusTitle = data.is_safe_for_monetization 
          ? '✅ Projeto Seguro para Monetização (YouTube / TikTok)' 
          : '⚠️ Risco de Reivindicação / Mídias com Restrição';

        let warningsHtml = '';
        if (data.actionable_warnings && data.actionable_warnings.length > 0) {
          warningsHtml = `
            <div style="background:#451a03; border:1px solid #b45309; padding:12px; border-radius:6px;">
              <b style="color:#fbbf24;">Atenção: Mídias com Restrições:</b>
              <ul style="margin:6px 0 0 18px; color:#fed7aa; font-size:0.85rem;">
                ${data.actionable_warnings.map(w => `<li>${w}</li>`).join('')}
              </ul>
            </div>
          `;
        }

        body.innerHTML = `
          <div style="background:var(--card-bg); border-left:4px solid ${statusColor}; padding:12px 16px; border-radius:4px;">
            <div style="font-weight:700; color:${statusColor}; font-size:1rem;">${statusTitle}</div>
            <div style="color:var(--text-muted); font-size:0.85rem; margin-top:4px;">Score de Conformidade: <b>${data.overall_copyright_score}%</b></div>
          </div>

          <div style="display:grid; grid-template-columns:repeat(3, 1fr); gap:10px; text-align:center;">
            <div style="background:var(--card-bg); padding:10px; border-radius:6px; border:1px solid var(--border);">
              <div style="font-size:1.2rem; font-weight:700; color:#10b981;">${data.fully_cleared_scenes}</div>
              <div style="font-size:0.75rem; color:var(--text-muted);">100% Livres</div>
            </div>
            <div style="background:var(--card-bg); padding:10px; border-radius:6px; border:1px solid var(--border);">
              <div style="font-size:1.2rem; font-weight:700; color:#f59e0b;">${data.scenes_requiring_attribution}</div>
              <div style="font-size:0.75rem; color:var(--text-muted);">Com Atribuição</div>
            </div>
            <div style="background:var(--card-bg); padding:10px; border-radius:6px; border:1px solid var(--border);">
              <div style="font-size:1.2rem; font-weight:700; color:#ef4444;">${data.restricted_scenes_count}</div>
              <div style="font-size:0.75rem; color:var(--text-muted);">Restritas/Risco</div>
            </div>
          </div>

          ${warningsHtml}

          <div>
            <label style="color:#93c5fd; font-weight:600;">Texto Pronto para Descrição do YouTube / TikTok:</label>
            <textarea id="copyright-credits-text" readonly style="width:100%; height:130px; font-family:monospace; font-size:0.8rem; background:#141517; padding:8px; border-radius:6px; border:1px solid var(--border); color:#e5e7eb;">${data.youtube_description_credits || 'Nenhuma atribuição obrigatória requerida para este projeto.'}</textarea>
          </div>
        `;

        modal.style.display = 'flex';
      } catch (err) {
        alert('Erro ao auditar direitos autorais: ' + err.message);
      }
    }

    function fecharAuditoriaCopyright() {
      document.getElementById('copyright-modal').style.display = 'none';
    }

    function copiarCreditosYouTube() {
      const txt = document.getElementById('copyright-credits-text');
      if (txt) {
        txt.select();
        navigator.clipboard.writeText(txt.value);
        const btn = document.getElementById('btn-copy-credits');
        const orig = btn.innerText;
        btn.innerText = '✅ Copiado!';
        setTimeout(() => { btn.innerText = orig; }, 2000);
      }
    }

    async function executarRemediacaoCopyright() {
      if (!currentPlan) return alert('Nenhum projeto ativo!');
      if (!confirm('Deseja substituir automaticamente todas as mídias de risco por opções 100% livres e comerciais?')) return;
      showStatus('Auto-corrigindo mídias de risco...', '#e11d48');
      try {
        const res = await fetch('/api/copyright_remediate', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ project_id: currentPlan.project_id })
        });
        const data = await res.json();
        if (data.ok) {
          currentPlan = data.plan;
          renderScenes();
          fecharAuditoriaCopyright();
          alert(`✅ Sucesso! ${data.remediation.remediated_count} mídias corrigidas. Score agora em ${data.remediation.overall_copyright_score}%.`);
          abrirAuditoriaCopyright();
        } else {
          alert('Erro ao remediar: ' + (data.error || 'Falha'));
        }
      } catch (err) {
        alert('Erro de conexão: ' + err.message);
      }
    }

    async function abrirKitPublicacao() {
      if (!currentPlan) return alert('Analise ou carregue um projeto primeiro!');
      showStatus('Gerando Kit Completo de Publicação & SEO...', '#f59e0b');
      try {
        const res = await fetch(`/api/publication_kit?project_id=${currentPlan.project_id}`);
        const data = await res.json();
        if (!data.ok) return alert('Erro ao gerar kit: ' + (data.error || 'Erro'));
        
        let titlesHtml = data.magnetic_titles.map(t => `
          <div style="background:#1e2023; padding:8px 12px; border-radius:6px; border:1px solid #383c42; margin-bottom:6px;">
            <span style="font-size:0.75rem; color:#93c5fd; font-weight:600;">[${t.category} - Força CTR: ${t.expected_ctr_power}]</span>
            <div style="font-size:0.92rem; font-weight:700; color:#fff; margin-top:2px;">${t.title}</div>
          </div>
        `).join('');

        const modal = document.getElementById('copyright-modal');
        const body = document.getElementById('copyright-modal-body');
        body.innerHTML = `
          <div style="background:#272a2e; padding:12px; border-radius:6px; border-left:4px solid #f59e0b;">
            <b style="color:#fbbf24; font-size:1rem;">🚀 Kit de Publicação & Virality Pack</b>
            <p style="color:#9ca3af; font-size:0.85rem; margin-top:2px;">5 Títulos Magnéticos para Teste A/B + Capítulos com Timestamps + SEO Tags</p>
          </div>
          <div>
            <label style="color:#93c5fd;">Títulos de Alta Conversão (A/B Testing):</label>
            ${titlesHtml}
          </div>
          <div>
            <label style="color:#93c5fd;">Tags e Palavras-Chave Algorítmicas:</label>
            <input type="text" readonly style="width:100%; font-size:0.85rem;" value="${data.search_tags || ''}">
          </div>
          <div>
            <label style="color:#93c5fd;">Descrição Completa para YouTube Studio (Com Capítulos & Créditos):</label>
            <textarea id="copyright-credits-text" readonly style="width:100%; height:140px; font-family:monospace; font-size:0.8rem; background:#141517; padding:8px; border-radius:6px; border:1px solid #383c42; color:#e5e7eb;">${data.complete_youtube_description}</textarea>
          </div>
        `;
        document.getElementById('btn-remediate-risk').style.display = 'none';
        modal.style.display = 'flex';
      } catch (e) {
        alert('Erro: ' + e.message);
      }
    }

    async function abrirThumbnailStudio() {
      if (!currentPlan) return alert('Analise um projeto primeiro!');
      showStatus('Calculando Saliência Visual & Heatmaps de Thumbnail...', '#8b5cf6');
      try {
        const res = await fetch(`/api/thumbnails?project_id=${currentPlan.project_id}`);
        const data = await res.json();
        if (!data.ok) return alert('Erro ao gerar miniaturas');

        let varsHtml = data.variants.map(v => `
          <div style="background:#1e2023; padding:12px; border-radius:8px; border:1px solid #383c42; margin-bottom:10px;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
              <b style="color:#c4b5fd;">${v.strategy.toUpperCase()}</b>
              <span style="background:#065f46; color:#a7f3d0; padding:2px 8px; border-radius:999px; font-weight:700; font-size:0.75rem;">CTR Score: ${v.predicted_ctr_score}%</span>
            </div>
            <div style="font-size:1.1rem; font-weight:800; color:#fff; margin:6px 0;">"${v.headline_text}"</div>
            <div style="font-size:0.8rem; color:#9ca3af;">Ponto Focal: <b>${v.primary_focal_point}</b> | Rim-Light: <span style="color:${v.rim_light_color};">■</span> ${v.rim_light_color}</div>
          </div>
        `).join('');

        const modal = document.getElementById('copyright-modal');
        const body = document.getElementById('copyright-modal-body');
        body.innerHTML = `
          <div style="background:#272a2e; padding:12px; border-radius:6px; border-left:4px solid #8b5cf6;">
            <b style="color:#c4b5fd; font-size:1rem;">🖼️ Thumbnail Studio com Mapa de Calor de Atenção</b>
            <p style="color:#9ca3af; font-size:0.85rem; margin-top:2px;">Simulação de foveal eye-tracking nos primeiros 500ms do feed do YouTube.</p>
          </div>
          <div>${varsHtml}</div>
        `;
        document.getElementById('btn-remediate-risk').style.display = 'none';
        modal.style.display = 'flex';
      } catch (e) {
        alert('Erro: ' + e.message);
      }
    }

    async function carregarTelemetria() {
      try {
        const res = await fetch('/api/system/telemetry');
        const data = await res.json();
        if (data.ok) {
          const cpuEl = document.getElementById('telemetry-cpu');
          if (cpuEl) cpuEl.innerText = `${data.total_threads} Threads (${data.cpu_usage_pct}%)`;
          const ramEl = document.getElementById('telemetry-ram');
          if (ramEl) ramEl.innerText = `RAM: ${data.ram_used_gb}/${data.ram_total_gb}GB`;
          const encEl = document.getElementById('telemetry-encoder');
          if (encEl) {
            if (data.is_gpu_accelerated) {
              encEl.innerText = '🚀 ' + data.active_encoder_mode;
              encEl.style.color = '#10b981';
            } else {
              encEl.innerText = '⚙️ ' + data.active_encoder_mode;
              encEl.style.color = '#fef08a';
            }
          }
        }
      } catch (e) {}
    }
    carregarTelemetria();
    setInterval(carregarTelemetria, 8000);

    async function abrirRenderParalelo() {
      if (!currentPlan) return alert('Analise um projeto primeiro!');
      showStatus('Orquestrando render paralelo para 24 threads / GPU...', '#06b6d4');
      try {
        const res = await fetch('/api/render/parallel', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ project_id: currentPlan.project_id })
        });
        const data = await res.json();
        if (!data.ok) return alert('Erro ao planejar render paralelo');

        const modal = document.getElementById('copyright-modal');
        const body = document.getElementById('copyright-modal-body');
        body.innerHTML = `
          <div style="background:#272a2e; padding:12px; border-radius:6px; border-left:4px solid #06b6d4;">
            <b style="color:#67e8f9; font-size:1rem;">⚡ Renderização Paralela em Chunks</b>
            <p style="color:#9ca3af; font-size:0.85rem; margin-top:2px;">Fatiamento da timeline em blocos simultâneos com concatenação direta via stream copy.</p>
          </div>
          <div style="display:grid; grid-template-columns:repeat(3, 1fr); gap:10px; text-align:center;">
            <div style="background:#1e2023; padding:10px; border-radius:6px; border:1px solid #383c42;">
              <div style="font-size:1.2rem; font-weight:700; color:#67e8f9;">${data.total_chunks}</div>
              <div style="font-size:0.75rem; color:#9ca3af;">Chunks Paralelos</div>
            </div>
            <div style="background:#1e2023; padding:10px; border-radius:6px; border:1px solid #383c42;">
              <div style="font-size:1.2rem; font-weight:700; color:#10b981;">${data.speedup_factor}x</div>
              <div style="font-size:0.75rem; color:#9ca3af;">Aceleração Estimada</div>
            </div>
            <div style="background:#1e2023; padding:10px; border-radius:6px; border:1px solid #383c42;">
              <div style="font-size:1.2rem; font-weight:700; color:#fef08a;">${data.concurrency}</div>
              <div style="font-size:0.75rem; color:#9ca3af;">Slots Simultâneos</div>
            </div>
          </div>
          <div>
            <label style="color:#93c5fd;">Modo de Codificação Detectado:</label>
            <input type="text" readonly style="width:100%; font-size:0.85rem; font-weight:bold; color:#10b981;" value="${data.encoder_mode}">
          </div>
          <div>
            <label style="color:#93c5fd;">Manifesto de Concatenação FFmpeg (-c copy sem perda):</label>
            <textarea readonly style="width:100%; height:110px; font-family:monospace; font-size:0.8rem; background:#141517; padding:8px; border-radius:6px; border:1px solid #383c42; color:#e5e7eb;">${data.concat_manifest}</textarea>
          </div>
        `;
        document.getElementById('btn-remediate-risk').style.display = 'none';
        modal.style.display = 'flex';
      } catch (e) {
        alert('Erro: ' + e.message);
      }
    }

    async function gerarLegendasKaraoke() {
      if (!currentPlan) return alert('Analise um projeto primeiro!');
      showStatus('Gerando legendas animadas em estilo Karaokê (Hormozi)...', '#ec4899');
      try {
        const res = await fetch('/api/captions/karaoke', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ project_id: currentPlan.project_id })
        });
        const data = await res.json();
        if (!data.ok) return alert('Erro ao gerar legendas');

        const modal = document.getElementById('copyright-modal');
        const body = document.getElementById('copyright-modal-body');
        body.innerHTML = `
          <div style="background:#272a2e; padding:12px; border-radius:6px; border-left:4px solid #ec4899;">
            <b style="color:#f472b6; font-size:1rem;">✨ Legendas Cinéticas Estilo Karaokê (.ASS)</b>
            <p style="color:#9ca3af; font-size:0.85rem; margin-top:2px;">Destaque palavra por palavra com neon e safe-zone do TikTok pronta.</p>
          </div>
          <div>
            <label style="color:#93c5fd;">Script Completo de Legendas (.ASS):</label>
            <textarea id="karaoke-ass-text" readonly style="width:100%; height:200px; font-family:monospace; font-size:0.8rem; background:#141517; padding:8px; border-radius:6px; border:1px solid #383c42; color:#e5e7eb;">${data.ass_content}</textarea>
          </div>
        `;
        document.getElementById('btn-remediate-risk').style.display = 'none';
        modal.style.display = 'flex';
      } catch (e) {
        alert('Erro: ' + e.message);
      }
    }

    async function abrirRamDiskStats() {
      showStatus('Consultando throughput do RAM-Disk Buffer...', '#10b981');
      try {
        const res = await fetch('/api/ram_buffer/stats');
        const data = await res.json();
        const dRes = await fetch('/api/dedup/stats');
        const dData = await dRes.json();

        const modal = document.getElementById('copyright-modal');
        const body = document.getElementById('copyright-modal-body');
        body.innerHTML = `
          <div style="background:#272a2e; padding:12px; border-radius:6px; border-left:4px solid #10b981;">
            <b style="color:#a7f3d0; font-size:1rem;">💾 RAM-Disk Buffer & Deduplicação NTFS (CAS)</b>
            <p style="color:#9ca3af; font-size:0.85rem; margin-top:2px;">Throughput de leitura a mais de 10.000 MB/s na RAM e economia de gigabytes no disco.</p>
          </div>
          <div style="display:grid; grid-template-columns:repeat(3, 1fr); gap:10px; text-align:center;">
            <div style="background:#1e2023; padding:10px; border-radius:6px; border:1px solid #383c42;">
              <div style="font-size:1.2rem; font-weight:700; color:#10b981;">${data.used_mb} MB</div>
              <div style="font-size:0.75rem; color:#9ca3af;">RAM Ativa em Buffer</div>
            </div>
            <div style="background:#1e2023; padding:10px; border-radius:6px; border:1px solid #383c42;">
              <div style="font-size:1.2rem; font-weight:700; color:#38bdf8;">${data.speedup_factor}x</div>
              <div style="font-size:0.75rem; color:#9ca3af;">Velocidade vs Disco</div>
            </div>
            <div style="background:#1e2023; padding:10px; border-radius:6px; border:1px solid #383c42;">
              <div style="font-size:1.2rem; font-weight:700; color:#f59e0b;">${dData.savings_percentage}%</div>
              <div style="font-size:0.75rem; color:#9ca3af;">Economia de Disco (CAS)</div>
            </div>
          </div>
          <div style="background:#1e2023; padding:12px; border-radius:6px; border:1px solid #383c42; font-size:0.85rem; color:#d1d5db;">
            <div><b>Mídias em RAM Cache:</b> ${data.cached_assets_count} arquivos</div>
            <div><b>Ativos Únicos Armazenados:</b> ${dData.total_unique_assets}</div>
            <div><b>Hardlinks NTFS Criados (Zero Bytes):</b> ${dData.total_referenced_links} links</div>
            <div><b>Espaço Físico Poupado:</b> ${dData.disk_saved_mb} MB</div>
          </div>
        `;
        document.getElementById('btn-remediate-risk').style.display = 'none';
        modal.style.display = 'flex';
      } catch (e) {
        alert('Erro ao consultar buffer: ' + e.message);
      }
    }

    async function abrirBitrateAdaptativo() {
      if (!currentPlan) return alert('Analise um projeto primeiro!');
      showStatus('Calculando matriz de complexidade perceptual de cena...', '#38bdf8');
      try {
        const res = await fetch(`/api/adaptive_crf?project_id=${currentPlan.project_id}`);
        const data = await res.json();
        if (!data.ok) return alert('Erro ao calcular CRF');

        let recipesHtml = (data.recipes || []).map(r => `
          <div style="display:flex; justify-content:space-between; align-items:center; background:#1e2023; padding:8px 12px; border-radius:4px; margin-bottom:4px; border:1px solid #383c42; font-size:0.82rem;">
            <span><b>Cena #${r.scene_order}</b> [${r.complexity}]</span>
            <span style="color:#38bdf8; font-weight:bold;">CRF ${r.target_crf} (Max: ${r.max_bitrate_kbps} kbps)</span>
            <span style="color:#10b981;">-${r.estimated_size_reduction_pct}% tam.</span>
          </div>
        `).join('');

        const modal = document.getElementById('copyright-modal');
        const body = document.getElementById('copyright-modal-body');
        body.innerHTML = `
          <div style="background:#272a2e; padding:12px; border-radius:6px; border-left:4px solid #38bdf8;">
            <b style="color:#bae6fd; font-size:1rem;">🎛️ Bitrate Adaptativo & CRF Dinâmico</b>
            <p style="color:#9ca3af; font-size:0.85rem; margin-top:2px;">Redução de ~${data.estimated_savings_pct}% no tamanho final do vídeo com fidelidade visual cinematográfica.</p>
          </div>
          <div>
            <label style="color:#93c5fd;">Alocação de Bitrate por Cena:</label>
            <div style="max-height:160px; overflow-y:auto;">${recipesHtml}</div>
          </div>
          <div>
            <label style="color:#93c5fd;">Parâmetros Otimizados FFmpeg:</label>
            <input type="text" readonly style="width:100%; font-size:0.82rem; color:#10b981; font-family:monospace;" value="${data.ffmpeg_args.join(' ')}">
          </div>
        `;
        document.getElementById('btn-remediate-risk').style.display = 'none';
        modal.style.display = 'flex';
      } catch (e) {
        alert('Erro: ' + e.message);
      }
    }

    let batchPollingInterval = null;

    async function abrirPilotoAutomatico() {
      const modal = document.getElementById('copyright-modal');
      const body = document.getElementById('copyright-modal-body');
      
      body.innerHTML = `
        <div style="background:#272a2e; padding:12px; border-radius:6px; border-left:4px solid #eab308;">
          <b style="color:#fde047; font-size:1rem;">🏭 Piloto Automático em Lote (Batch Factory)</b>
          <p style="color:#9ca3af; font-size:0.85rem; margin-top:2px;">Insira múltiplos temas para a máquina produzir vídeos completos desatendida (roteiro, voz, mídias livres, legendas e SEO).</p>
        </div>

        <div>
          <label style="color:#93c5fd;">Temas dos Vídeos (um por linha):</label>
          <textarea id="batch-topics-input" style="width:100%; height:110px; font-size:0.88rem; background:#141517; border:1px solid #383c42; padding:8px; border-radius:6px; color:#fff;" placeholder="A Arte da Disciplina\nComo Vencer a Procrastinação\nO Segredo do Foco Profundo\nO Poder dos Hábitos Matinais">A Arte da Disciplina
Como Vencer a Procrastinação
O Segredo do Foco Profundo</textarea>
        </div>

        <div style="display:flex; justify-content:space-between; align-items:center;">
          <button class="btn" style="background:#eab308; color:#000; font-weight:800; padding:10px 20px;" onclick="iniciarFabricaLote()">🚀 Iniciar Produção em Massa</button>
          <button class="btn btn-secondary" onclick="atualizarStatusLote()">🔄 Atualizar Status</button>
        </div>

        <div id="batch-progress-panel" style="background:#1e2023; border:1px solid #383c42; border-radius:6px; padding:12px;">
          <div style="display:flex; justify-content:space-between; margin-bottom:6px; font-size:0.85rem;">
            <span>Progresso da Fábrica:</span>
            <b id="batch-pct-label" style="color:#fde047;">0%</b>
          </div>
          <div style="background:#141517; border-radius:999px; height:12px; overflow:hidden; border:1px solid #383c42;">
            <div id="batch-progress-bar" style="background:#eab308; width:0%; height:100%; transition:width 0.4s;"></div>
          </div>
          <div id="batch-jobs-list" style="margin-top:12px; max-height:180px; overflow-y:auto; display:flex; flex-direction:column; gap:6px;">
            <div style="color:#9ca3af; font-size:0.8rem; text-align:center;">Nenhum lote em execução. Clique em Iniciar.</div>
          </div>
        </div>
      `;
      document.getElementById('btn-remediate-risk').style.display = 'none';
      modal.style.display = 'flex';
      atualizarStatusLote();
    }

    async function iniciarFabricaLote() {
      const txt = document.getElementById('batch-topics-input').value;
      const topics = txt.split('\n').map(t => t.trim()).filter(t => t.length > 0);
      if (!topics.length) return alert('Digite ao menos um tema!');

      showStatus('Iniciando Fábrica em Lote no Xeon...', '#eab308');
      try {
        const res = await fetch('/api/batch/start', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ topics })
        });
        const data = await res.json();
        if (data.ok) {
          if (batchPollingInterval) clearInterval(batchPollingInterval);
          batchPollingInterval = setInterval(atualizarStatusLote, 2000);
          atualizarStatusLote();
        } else {
          alert('Erro ao iniciar: ' + (data.error || 'Falha'));
        }
      } catch (e) {
        alert('Erro: ' + e.message);
      }
    }

    async function atualizarStatusLote() {
      try {
        const res = await fetch('/api/batch/status');
        const data = await res.json();
        if (!data.ok) return;

        const bar = document.getElementById('batch-progress-bar');
        const lbl = document.getElementById('batch-pct-label');
        const list = document.getElementById('batch-jobs-list');

        if (bar) bar.style.width = `${data.overall_progress_pct}%`;
        if (lbl) lbl.innerText = `${data.overall_progress_pct}% (${data.completed_jobs} de ${data.total_jobs} vídeos prontos)`;

        if (list && data.jobs && data.jobs.length > 0) {
          list.innerHTML = data.jobs.map((j, i) => {
            let statusColor = j.status === 'ready' ? '#10b981' : (j.status === 'failed' ? '#ef4444' : '#f59e0b');
            let icon = j.status === 'ready' ? '✅' : (j.status === 'failed' ? '❌' : '⚙️');
            return `
              <div style="background:#141517; padding:8px 12px; border-radius:4px; border:1px solid #383c42; display:flex; justify-content:space-between; align-items:center; font-size:0.82rem;">
                <div>
                  <b>${icon} #${i+1}: ${j.topic}</b>
                  <div style="color:#9ca3af; font-size:0.75rem;">Status: <span style="color:${statusColor}; font-weight:600;">${j.status.toUpperCase()}</span> ${j.total_scenes ? '| ' + j.total_scenes + ' cenas' : ''} ${j.duration_sec ? '| ' + j.duration_sec + 's' : ''}</div>
                </div>
                <div style="font-weight:bold; color:${statusColor};">${j.progress_pct}%</div>
              </div>
            `;
          }).join('');
        }

        if (!data.is_running && data.completed_jobs === data.total_jobs && data.total_jobs > 0) {
          if (batchPollingInterval) {
            clearInterval(batchPollingInterval);
            batchPollingInterval = null;
          }
        }
      } catch (e) {}
    }

    function renderScenes() {
      if (!currentPlan) return;
      document.getElementById('project-header').innerText = `Projeto: ${currentPlan.title}`;
      let totalDur = currentPlan.scenes.reduce((acc, s) => acc + (s.duration || 0), 0);
      document.getElementById('stats-summary').innerText = `${currentPlan.scenes.length} cenas | ${totalDur.toFixed(1)}s duração`;

      const container = document.getElementById('scenes-container');
      container.innerHTML = '';

      currentPlan.scenes.forEach(s => {
        const card = document.createElement('div');
        card.className = 'scene-card';
        
        let tagsHtml = (s.english_keywords || []).map(k => `<span class="tag">${k}</span>`).join('');
        let statusClass = s.state === 'ready' || s.state === 'placed' ? 'status-ready' : (s.state === 'error' ? 'status-error' : 'status-pending');
        
        card.innerHTML = `
          <div class="scene-order">${s.order}</div>
          <div class="scene-narration">
            <h4>Narração Falada</h4>
            <p>${s.narration_text}</p>
          </div>
          <div class="scene-visual">
            <h4>Descrição Visual</h4>
            <p>${s.visual_description || 'Auto-gerada'}</p>
            <div class="tags">${tagsHtml}</div>
          </div>
          <div class="scene-meta">
            <div><span class="status-pill ${statusClass}">${s.state.toUpperCase()}</span></div>
            <div><b>Duração:</b> ${(s.duration || 0).toFixed(1)}s</div>
            <div><b>Mídia:</b> ${s.selected_media ? s.selected_media.platform : 'Pendente'}</div>
            ${s.selected_media ? (
              (s.selected_media.copyright_risk === 'safe' && (s.selected_media.commercial_use !== false) && !(s.selected_media.attribution_text || '').startsWith('Mídia:'))
                ? '<div style="margin-top:4px;"><span style="background:#065f46; color:#a7f3d0; padding:2px 6px; border-radius:4px; font-size:0.72rem; font-weight:600;">🟢 100% Livre Comercial</span></div>'
                : ((s.selected_media.copyright_risk === 'safe' && (s.selected_media.attribution_text || '').startsWith('Mídia:'))
                  ? '<div style="margin-top:4px;"><span style="background:#854d0e; color:#fef08a; padding:2px 6px; border-radius:4px; font-size:0.72rem; font-weight:600;">🟡 Requer Atribuição</span></div>'
                  : '<div style="margin-top:4px;"><span style="background:#991b1b; color:#fecaca; padding:2px 6px; border-radius:4px; font-size:0.72rem; font-weight:600;">🔴 Risco Copyright</span></div>'
                )
            ) : ''}
          </div>
        `;
        container.appendChild(card);
      });
    }
  </script>
  <!-- Modal de Auditoria de Direitos Autorais -->
  <div id="copyright-modal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.75); z-index:9999; align-items:center; justify-content:center;">
    <div style="background:var(--panel-bg); border:1px solid var(--border); border-radius:10px; width:720px; max-width:92%; max-height:85vh; display:flex; flex-direction:column; overflow:hidden; box-shadow:0 20px 25px -5px rgba(0,0,0,0.5);">
      <div style="padding:16px 20px; border-bottom:1px solid var(--border); display:flex; justify-content:space-between; align-items:center;">
        <h3 style="font-size:1.1rem; color:#fff; display:flex; align-items:center; gap:8px;">🛡️ Auditoria de Direitos Autorais & Licenças</h3>
        <button style="background:none; border:none; color:var(--text-muted); font-size:1.4rem; cursor:pointer;" onclick="fecharAuditoriaCopyright()">&times;</button>
      </div>
      <div id="copyright-modal-body" style="padding:20px; overflow-y:auto; flex:1; font-size:0.9rem; display:flex; flex-direction:column; gap:16px;">
      </div>
      <div style="padding:12px 20px; border-top:1px solid var(--border); display:flex; justify-content:space-between; align-items:center; background:var(--card-bg);">
        <button class="btn btn-secondary" onclick="fecharAuditoriaCopyright()">Fechar</button>
        <button class="btn" style="background:#e11d48;" id="btn-remediate-risk" onclick="executarRemediacaoCopyright()">⚡ Auto-Corrigir Cenas de Risco (1-Clique)</button>
        <button class="btn btn-success" id="btn-copy-credits" onclick="copiarCreditosYouTube()">📋 Copiar Créditos para Descrição</button>
      </div>
    </div>
  </div>
</body>
</html>
"""

class AIEditorHandler(http.server.BaseHTTPRequestHandler):
    repo = ProjectRepository()
    skill_bridge = GeminiSkillBridge()
    policy_manager = PlatformPolicyManager()

    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML_PAGE.encode("utf-8"))
        elif self.path.startswith("/api/health"):
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok", "service": "drift-ai-engine"}).encode("utf-8"))
        elif self.path.startswith("/api/skills"):
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"ok": True, "skills": self.skill_bridge.list_skills()}).encode("utf-8"))
        elif self.path.startswith("/api/copyright_audit"):
            import urllib.parse
            parsed = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed.query)
            proj_id = params.get("project_id", [""])[0]
            plan = self.repo.get(proj_id) if proj_id else None
            if not plan:
                return self.send_json({"ok": False, "error": "Projeto não encontrado"}, 404)
            audit = CopyrightAnalyzer.audit_timeline_copyright(plan)
            return self.send_json({
                "ok": True,
                "project_id": audit.project_id,
                "project_title": audit.project_title,
                "total_scenes": audit.total_scenes_analyzed,
                "fully_cleared_scenes": audit.fully_cleared_scenes,
                "scenes_requiring_attribution": audit.scenes_requiring_attribution,
                "restricted_scenes_count": audit.restricted_scenes_count,
                "overall_copyright_score": audit.overall_copyright_score,
                "is_safe_for_monetization": audit.is_safe_for_monetization,
                "youtube_description_credits": audit.youtube_description_credits,
                "actionable_warnings": audit.actionable_warnings,
                "scene_breakdown": audit.scene_breakdown
            })
        elif self.path.startswith("/api/batch/status"):
            state = BATCH_FACTORY.get_state()
            return self.send_json({
                "ok": True,
                "total_jobs": state.total_jobs,
                "completed_jobs": state.completed_jobs,
                "active_job_index": state.active_job_index,
                "is_running": state.is_running,
                "overall_progress_pct": state.overall_progress_pct,
                "output_root_dir": state.output_root_dir,
                "jobs": [j.__dict__ for j in state.jobs]
            })
        elif self.path.startswith("/api/ram_buffer/stats"):
            stats = RAM_BUFFER.get_stats()
            return self.send_json({
                "ok": True,
                "total_budget_mb": stats.total_budget_mb,
                "used_mb": stats.used_mb,
                "free_mb": stats.free_mb,
                "cached_assets_count": stats.cached_assets_count,
                "speedup_factor": stats.read_speedup_factor
            })
        elif self.path.startswith("/api/dedup/stats"):
            d_stats = MEDIA_DEDUP.get_stats()
            return self.send_json({
                "ok": True,
                "total_unique_assets": d_stats.total_unique_assets,
                "total_referenced_links": d_stats.total_referenced_links,
                "disk_saved_mb": d_stats.disk_saved_mb,
                "total_stored_mb": d_stats.total_stored_mb,
                "savings_percentage": d_stats.savings_percentage
            })
        elif self.path.startswith("/api/adaptive_crf"):
            import urllib.parse
            parsed = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed.query)
            proj_id = params.get("project_id", [""])[0]
            plan = self.repo.get(proj_id) if proj_id else None
            if not plan:
                return self.send_json({"ok": False, "error": "Projeto não encontrado"}, 404)
            manifest = AdaptiveCrfEncoder.generate_encoding_manifest(plan)
            return self.send_json({
                "ok": True,
                "average_crf": manifest.average_crf,
                "estimated_savings_pct": manifest.estimated_bandwidth_savings_pct,
                "recipes": [
                    {
                        "scene_order": r.scene_order,
                        "complexity": r.complexity.value,
                        "target_crf": r.target_crf,
                        "max_bitrate_kbps": r.max_bitrate_kbps,
                        "estimated_size_reduction_pct": r.estimated_size_reduction_pct
                    }
                    for r in manifest.recipes
                ],
                "ffmpeg_args": manifest.recommended_global_ffmpeg_args
            })
        elif self.path.startswith("/api/system/telemetry"):
            report = HardwareTelemetryProfiler.get_telemetry()
            return self.send_json({
                "ok": True,
                "cpu_model": report.cpu_model,
                "physical_cores": report.physical_cores,
                "total_threads": report.total_threads,
                "cpu_usage_pct": report.cpu_usage_pct,
                "ram_total_gb": report.ram_total_gb,
                "ram_used_gb": report.ram_used_gb,
                "ram_free_gb": report.ram_free_gb,
                "ram_usage_pct": report.ram_usage_pct,
                "disk_total_gb": report.disk_total_gb,
                "disk_free_gb": report.disk_free_gb,
                "active_encoder_mode": report.active_encoder_mode,
                "is_gpu_accelerated": report.is_gpu_accelerated,
                "recommended_concurrency": report.recommended_concurrency,
                "health_status": report.health_status
            })
        elif self.path.startswith("/api/publication_kit"):
            import urllib.parse
            parsed = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed.query)
            proj_id = params.get("project_id", [""])[0]
            plan = self.repo.get(proj_id) if proj_id else None
            if not plan:
                return self.send_json({"ok": False, "error": "Projeto não encontrado"}, 404)
            kit = PublicationSeoKitGenerator.generate_complete_kit(plan)
            return self.send_json({
                "ok": True,
                "project_id": kit.project_id,
                "project_title": kit.project_title,
                "magnetic_titles": [t.__dict__ for t in kit.magnetic_titles],
                "youtube_chapters": kit.youtube_chapters,
                "search_tags": kit.search_tags_comma_separated,
                "trending_hashtags": kit.trending_hashtags,
                "copyright_credits_block": kit.copyright_credits_block,
                "complete_youtube_description": kit.complete_youtube_description,
                "monetization_approved": kit.monetization_approved
            })
        elif self.path.startswith("/api/thumbnails"):
            import urllib.parse
            parsed = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed.query)
            proj_id = params.get("project_id", [""])[0]
            plan = self.repo.get(proj_id) if proj_id else None
            if not plan:
                return self.send_json({"ok": False, "error": "Projeto não encontrado"}, 404)
            variants = ThumbnailStudio.generate_ab_variants(plan)
            return self.send_json({
                "ok": True,
                "variants": [v.__dict__ for v in variants]
            })
        elif self.path.startswith("/api/mix_soundtrack"):
            import urllib.parse
            parsed = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed.query)
            proj_id = params.get("project_id", [""])[0]
            plan = self.repo.get(proj_id) if proj_id else None
            if not plan:
                return self.send_json({"ok": False, "error": "Projeto não encontrado"}, 404)
            mix = AutoDuckingSoundtrackMixer.generate_mix_plan(plan)
            return self.send_json({
                "ok": True,
                "target_bpm": mix.target_bpm,
                "music_profile": mix.music_profile,
                "total_duration": mix.total_duration,
                "idle_volume_db": mix.idle_volume_db,
                "ducked_volume_db": mix.ducked_volume_db,
                "keyframes_count": len(mix.keyframes),
                "aligned_transitions": mix.aligned_transitions,
                "ffmpeg_filter": mix.ffmpeg_volume_filter
            })
        elif self.path.startswith("/api/policies"):
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"ok": True, "policies": self.policy_manager.policies}).encode("utf-8"))
        elif self.path.startswith("/api/projects"):
            import urllib.parse
            parsed = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed.query)
            if "cursor" in params or "limit" in params:
                limit = int(params.get("limit", [20])[0])
                cursor = params.get("cursor", [None])[0]
                page = self.repo.list_cursor(limit=limit, cursor=cursor)
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({
                    "items": page.items,
                    "next_cursor": page.next_cursor,
                    "has_more": page.has_more,
                    "limit": page.limit
                }).encode("utf-8"))
            else:
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(self.repo.list_all()).encode("utf-8"))
        elif self.path.startswith("/api/stream_script"):
            import urllib.parse
            parsed = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed.query)
            topic = params.get("topic", ["Desenvolvimento Pessoal"])[0]
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream; charset=utf-8")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Connection", "keep-alive")
            self.end_headers()
            script_full = ScriptGenerator.generate(topic)
            lines = [l for l in script_full.split("\n") if l.strip()]
            for l in lines:
                payload = json.dumps({"chunk": l, "done": False}, ensure_ascii=False)
                self.wfile.write(f"data: {payload}\n\n".encode("utf-8"))
                self.wfile.flush()
            final_payload = json.dumps({"chunk": "", "done": True, "full_script": script_full}, ensure_ascii=False)
            self.wfile.write(f"data: {final_payload}\n\n".encode("utf-8"))
            self.wfile.flush()
        elif self.path.startswith("/api/system/memory"):
            stats = MemoryManager.get_stats()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({
                "rss_mb": stats.rss_mb,
                "gc_counts": stats.gc_counts,
                "python_version": stats.python_version
            }).encode("utf-8"))
        elif self.path.startswith("/api/system/gc"):
            res = MemoryManager.collect_garbage(trim_os_working_set=True)
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(res).encode("utf-8"))
        elif self.path.startswith("/api/cache/stats"):
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(GLOBAL_CACHE.stats()).encode("utf-8"))
        elif self.path.startswith("/api/scene_audio"):
            import urllib.parse
            parsed = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed.query)
            proj_id = params.get("project_id", [""])[0]
            scene_order = int(params.get("order", ["1"])[0])
            plan = self.repo.get(proj_id) if proj_id else None
            audio_path = None
            if plan:
                for s in plan.scenes:
                    if s.order == scene_order and s.audio_path:
                        audio_path = Path(s.audio_path)
                        break
            if audio_path and audio_path.exists():
                self.send_response(200)
                self.send_header("Content-Type", "audio/wav")
                self.send_header("Content-Length", str(audio_path.stat().st_size))
                self.end_headers()
                with open(audio_path, "rb") as af:
                    self.wfile.write(af.read())
            else:
                self.send_response(404)
                self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode("utf-8")
        data = json.loads(body) if body else {}

        if self.path == "/api/copyright_audit":
            project_id = data.get("project_id")
            plan = self.repo.get(project_id) if project_id else None
            if not plan:
                return self.send_json({"ok": False, "error": "Projeto não encontrado"}, 404)
            audit = CopyrightAnalyzer.audit_timeline_copyright(plan)
            return self.send_json({
                "ok": True,
                "project_id": audit.project_id,
                "project_title": audit.project_title,
                "total_scenes": audit.total_scenes_analyzed,
                "fully_cleared_scenes": audit.fully_cleared_scenes,
                "scenes_requiring_attribution": audit.scenes_requiring_attribution,
                "restricted_scenes_count": audit.restricted_scenes_count,
                "overall_copyright_score": audit.overall_copyright_score,
                "is_safe_for_monetization": audit.is_safe_for_monetization,
                "youtube_description_credits": audit.youtube_description_credits,
                "actionable_warnings": audit.actionable_warnings,
                "scene_breakdown": audit.scene_breakdown
            })
        elif self.path == "/api/batch/start":
            topics = data.get("topics", [])
            if isinstance(topics, str):
                topics = [t.strip() for t in topics.split("\n") if t.strip()]
            if not topics:
                return self.send_json({"ok": False, "error": "Nenhum tema fornecido"}, 400)
            jobs = BATCH_FACTORY.create_batch_from_topics(topics)
            started = BATCH_FACTORY.start_batch_async()
            return self.send_json({"ok": started, "total_jobs": len(jobs)})
        elif self.path == "/api/batch/stop":
            BATCH_FACTORY.stop_batch()
            return self.send_json({"ok": True, "stopped": True})
        elif self.path == "/api/render/parallel":
            project_id = data.get("project_id")
            plan = self.repo.get(project_id) if project_id else None
            if not plan:
                return self.send_json({"ok": False, "error": "Projeto não encontrado"}, 404)
            p_plan = ChunkedParallelRenderer.create_parallel_plan(plan)
            return self.send_json({
                "ok": True,
                "project_id": p_plan.project_id,
                "total_chunks": p_plan.total_chunks,
                "concurrency": p_plan.concurrency_slots,
                "encoder_mode": p_plan.encoder_mode,
                "speedup_factor": p_plan.estimated_speedup_factor,
                "concat_manifest": p_plan.ffmpeg_concat_manifest,
                "final_output": p_plan.final_output_path
            })
        elif self.path == "/api/captions/karaoke":
            project_id = data.get("project_id")
            plan = self.repo.get(project_id) if project_id else None
            if not plan:
                return self.send_json({"ok": False, "error": "Projeto não encontrado"}, 404)
            karaoke = KaraokeSubtitleGenerator.generate_ass_script(plan)
            return self.send_json({
                "ok": True,
                "project_id": karaoke.project_id,
                "total_lines": karaoke.total_lines,
                "ass_content": karaoke.ass_script_content,
                "output_filename": karaoke.output_filename
            })
        elif self.path == "/api/copyright_remediate":
            project_id = data.get("project_id")
            plan = self.repo.get(project_id) if project_id else None
            if not plan:
                return self.send_json({"ok": False, "error": "Projeto não encontrado"}, 404)
            res = CopyrightAnalyzer.auto_remediate_project(plan)
            self.repo.save(plan)
            return self.send_json({"ok": True, "remediation": res, "plan": plan.to_dict()})
        elif self.path == "/api/export_hybrid":
            project_id = data.get("project_id")
            plan = self.repo.get(project_id) if project_id else None
            if not plan:
                return self.send_json({"ok": False, "error": "Projeto não encontrado"}, 404)
            report = HybridMultiFormatProducer.generate_hybrid_specs(plan)
            return self.send_json({
                "ok": True,
                "total_formats": report.total_formats,
                "formats": [
                    {
                        "name": f.format_name,
                        "aspect_ratio": f.aspect_ratio,
                        "resolution": f.resolution,
                        "bitrate": f.bitrate,
                        "output": f.target_output_filename,
                        "safe_zone": f.safe_zone.__dict__ if f.safe_zone else None
                    }
                    for f in report.formats
                ],
                "summary": report.summary
            })
        elif self.path == "/api/policies":
            return self.send_json({"ok": True, "policies": self.policy_manager.policies})

        elif self.path == "/api/update_policy":
            platform = data.get("platform", "youtube")
            path_keys = data.get("keys", [])
            val = data.get("value")
            if path_keys:
                ok = self.policy_manager.update_policy_rule(platform, path_keys, val)
                return self.send_json({"ok": ok})
            elif "data" in data:
                ver = self.policy_manager.import_policy_update(data["data"])
                return self.send_json({"ok": True, "version": ver})
            return self.send_json({"ok": False, "error": "Invalid payload"})

        elif self.path == "/api/audit_policies":
            project_id = data.get("project_id")
            platform = data.get("platform", "youtube")
            plan = self.repo.get(project_id)
            if not plan:
                return self.send_json({"ok": False, "error": "Project not found"}, 404)
            report = self.policy_manager.audit_project(plan, platform)
            return self.send_json({
                "ok": True,
                "platform": report.platform,
                "is_compliant": report.is_compliant,
                "risk_score": report.risk_score,
                "findings": [
                    {
                        "category": f.rule_category,
                        "severity": f.severity,
                        "scene": f.affected_scene_order,
                        "message": f.message,
                        "suggestion": f.remediation_suggestion
                    }
                    for f in report.findings
                ],
                "checklist": report.actionable_checklist
            })

        elif self.path == "/api/skills":
            return self.send_json({"ok": True, "skills": self.skill_bridge.list_skills()})

        elif self.path == "/api/install_skill":
            name = data.get("name", "Minha Skill")
            desc = data.get("description", "Skill personalizada do Gemini")
            skill_text = data.get("content", "")
            skill = self.skill_bridge.install_skill_from_text(name, desc, skill_text)
            return self.send_json({"ok": True, "skill": {
                "skill_id": skill.skill_id,
                "name": skill.name,
                "description": skill.description
            }})

        elif self.path == "/api/run_skill":
            skill_id = data.get("skill_id", "")
            prompt_in = data.get("prompt", "")
            out = self.skill_bridge.execute_skill(skill_id, prompt_in)
            return self.send_json({"ok": True, "result": out})

        elif self.path == "/api/generate_script":
            topic = data.get("topic", "Estoicismo")
            cache_k = f"script_gen:{topic.lower().strip()}"
            hit = GLOBAL_CACHE.get(cache_k)
            if hit:
                return self.send_json({"ok": True, "script": hit, "cached": True})
            script = ScriptGenerator.generate(topic)
            GLOBAL_CACHE.set(cache_k, script, ttl_sec=600)
            return self.send_json({"ok": True, "script": script, "cached": False})

        elif self.path == "/api/stream_copilot":
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream; charset=utf-8")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Connection", "keep-alive")
            self.end_headers()
            project_id = data.get("project_id")
            user_prompt = data.get("prompt", "")
            plan = self.repo.get(project_id)
            if not plan:
                err = json.dumps({"error": "Project not found", "done": True})
                self.wfile.write(f"data: {err}\n\n".encode("utf-8"))
                return
            from director.timeline_chat_copilot import TimelineChatCopilot
            steps = [
                "Analisando instrução de edição...",
                f"Avaliando {len(plan.scenes)} cenas na timeline...",
                "Executando ajustes não-destrutivos..."
            ]
            for step in steps:
                chunk = json.dumps({"status": step, "done": False}, ensure_ascii=False)
                self.wfile.write(f"data: {chunk}\n\n".encode("utf-8"))
                self.wfile.flush()
            res = TimelineChatCopilot.execute_command(plan, user_prompt)
            if res.success:
                self.repo.save(plan)
            final_chunk = json.dumps({
                "done": True,
                "summary": res.summary_message,
                "actions": res.actions_taken,
                "affected_scenes": res.affected_scenes,
                "success": res.success
            }, ensure_ascii=False)
            self.wfile.write(f"data: {final_chunk}\n\n".encode("utf-8"))
            self.wfile.flush()
            return

        elif self.path == "/api/clone_voice":
            name = data.get("name", "VozClonada")
            path = data.get("path", "")
            client = DriftMcpClient()
            try:
                client.start()
                engine = DriftChatterboxEngine(client)
                res = engine.clone_voice(name, path)
                return self.send_json(res)
            except Exception as e:
                return self.send_json({"ok": False, "error": str(e)})
            finally:
                client.stop()

        elif self.path == "/api/plan":
            script = data.get("script", "")
            title = data.get("title", "Projeto IA")
            cfg = ProjectConfig(
                aspect_ratio=data.get("aspect_ratio", "16:9"),
                media_type=data.get("media_type", "all"),
                transition_kind=data.get("transition_kind", "crossfade"),
                enable_ken_burns=data.get("enable_ken_burns", True),
                language=data.get("language", "pt"),
                exaggeration=float(data.get("exaggeration", 0.5))
            )
            cfg.update_resolution()

            plan = ProjectPlan(title=title, raw_script=script, config=cfg)
            scenes = ScriptSegmenter.parse(script, default_language=cfg.language, default_voice="default")
            VisualPlanner.plan_project(scenes)
            plan.scenes = scenes
            plan.reindex_scenes()
            self.repo.save(plan)

            self.send_json({"ok": True, "plan": plan.to_dict()})

        elif self.path == "/api/voice":
            project_id = data.get("project_id")
            plan = self.repo.get(project_id)
            if not plan:
                return self.send_json({"ok": False, "error": "Not found"}, 404)

            client = DriftMcpClient()
            try:
                client.start()
                engine = DriftChatterboxEngine(client)
                for s in plan.scenes:
                    if s.state != SceneState.READY or not s.audio_path:
                        engine.generate_scene(s)
                plan.reindex_scenes()
                self.repo.save(plan)
            finally:
                client.stop()

            self.send_json({"ok": True, "plan": plan.to_dict(), "total_duration": round(plan.total_duration(), 2)})

        elif self.path == "/api/search":
            project_id = data.get("project_id")
            plan = self.repo.get(project_id)
            if not plan:
                return self.send_json({"ok": False, "error": "Not found"}, 404)

            with MemoryManager.memory_guard("search"):
                providers = LazyProviderRegistry.get_or_load_all()
                for s in plan.scenes:
                    cands = []
                    for p in providers:
                        for kw in s.english_keywords[:2]:
                            cache_k = f"search:{p.name}:{kw}:{plan.config.aspect_ratio}:{plan.config.media_type}"
                            res = GLOBAL_CACHE.get(cache_k)
                            if res is None:
                                res = p.search(kw, orientation=plan.config.aspect_ratio, per_page=3, media_type=plan.config.media_type)
                                GLOBAL_CACHE.set(cache_k, res, ttl_sec=900)
                            cands.extend(res)
                            if len(cands) >= 3: break
                        if len(cands) >= 3: break
                    for c in cands:
                        CopyrightAnalyzer.analyze_candidate(c)
                    s.candidates = cands
                    if cands and not s.selected_media:
                        s.selected_media = cands[0]
                self.repo.save(plan)
                # Dispara prefetch especulativo assíncrono em segundo plano (Zero Wait Time)
                try:
                    PREFETCHER.prefetch_plan_candidates_async(plan)
                except Exception:
                    pass
            self.send_json({"ok": True, "plan": plan.to_dict()})

        elif self.path == "/api/build":
            project_id = data.get("project_id")
            plan = self.repo.get(project_id)
            if not plan:
                return self.send_json({"ok": False, "error": "Not found"}, 404)

            with MemoryManager.memory_guard("build"):
                downloader = MediaDownloader()
                for s in plan.scenes:
                    if s.selected_media and not s.selected_media.local_cached_path:
                        ok, path, _ = downloader.download_candidate(s.selected_media)
                        if ok and path:
                            s.selected_media.local_cached_path = str(path)

                client = DriftMcpClient()
                try:
                    client.start()
                    builder = TimelineBuilder(client)
                    builder.build_timeline(plan)
                    self.repo.save(plan)
                finally:
                    client.stop()

            self.send_json({"ok": True, "plan": plan.to_dict()})

        elif self.path == "/api/export":
            project_id = data.get("project_id")
            plan = self.repo.get(project_id)
            if not plan:
                return self.send_json({"ok": False, "error": "Not found"}, 404)

            safe_title = "".join(c for c in plan.title if c.isalnum() or c in (" ", "_", "-")).strip().replace(" ", "_")
            out_file = Path("d:/CUTWIREDRIFT") / f"{safe_title or 'video_ia'}.mp4"

            client = DriftMcpClient()
            try:
                client.start()
                exporter = ExportManager(client)
                res = exporter.export(out_file, plan)
                return self.send_json(res)
            except Exception as e:
                return self.send_json({"ok": False, "error": str(e)})
            finally:
                client.stop()

        elif self.path == "/api/hooks":
            topic = data.get("topic", "Desenvolvimento Pessoal")
            hooks = StoryboardEngine.generate_hooks(topic)
            return self.send_json({"ok": True, "hooks": [h.__dict__ for h in hooks]})

        elif self.path == "/api/styles":
            styles = [
                {"id": p.id, "name": p.name, "description": p.description, "transition": p.transition_type, "pacing": p.pacing_multiplier}
                for p in StyleEngine.PROFILES.values()
            ]
            return self.send_json({"ok": True, "styles": styles})

        elif self.path == "/api/audit":
            project_id = data.get("project_id")
            plan = self.repo.get(project_id)
            if not plan: return self.send_json({"ok": False, "error": "Not found"}, 404)
            report = QualityControlEngine.audit_project(plan)
            return self.send_json({
                "ok": True,
                "ready": report.is_ready_for_export,
                "score": report.score,
                "summary": report.summary_text,
                "issues": [i.__dict__ for i in report.issues]
            })

        elif self.path == "/api/manifest":
            project_id = data.get("project_id")
            plan = self.repo.get(project_id)
            if not plan: return self.send_json({"ok": False, "error": "Not found"}, 404)
            manifest = LicenseManifestManager.generate_manifest(plan)
            return self.send_json({"ok": True, "manifest": manifest})

        elif self.path == "/api/index_local":
            folder = data.get("folder_path", "d:/CUTWIREDRIFT")
            indexer = LocalMediaIndexer()
            added = indexer.scan_directory(folder)
            return self.send_json({"ok": True, "added_files": added, "total_catalog": len(indexer.catalog)})

        elif self.path == "/api/select_media":
            project_id = data.get("project_id")
            scene_order = int(data.get("scene_order", 1))
            cand_id = data.get("candidate_id")
            plan = self.repo.get(project_id)
            if not plan: return self.send_json({"ok": False, "error": "Not found"}, 404)
            for s in plan.scenes:
                if s.order == scene_order:
                    for c in s.candidates:
                        if c.external_id == cand_id or c.candidate_id == cand_id:
                            s.selected_media = c
                            break
            self.repo.save(plan)
            return self.send_json({"ok": True, "plan": plan.to_dict()})

        elif self.path == "/api/play_audio":
            proj_id = data.get("project_id")
            scene_order = int(data.get("scene_order", 1))
            plan = self.repo.get(proj_id) if proj_id else None
            audio_p = None
            if plan:
                for s in plan.scenes:
                    if s.order == scene_order and s.audio_path:
                        audio_p = s.audio_path
                        break
            if audio_p and os.path.exists(audio_p):
                try:
                    import winsound
                    winsound.PlaySound(audio_p, winsound.SND_FILENAME | winsound.SND_ASYNC)
                    return self.send_json({"ok": True, "playing": audio_p})
                except Exception as e:
                    return self.send_json({"ok": False, "error": str(e)})
            else:
                return self.send_json({"ok": False, "error": "Audio file not found"}, 404)

        elif self.path == "/api/stop_audio":
            try:
                import winsound
                winsound.PlaySound(None, winsound.SND_PURGE)
                return self.send_json({"ok": True})
            except Exception as e:
                return self.send_json({"ok": False, "error": str(e)})

        elif self.path == "/api/open_drift":
            project_id = data.get("project_id")
            plan = self.repo.get(project_id) if project_id else None
            safe_title = "".join(c for c in plan.title if c.isalnum() or c in (" ", "_", "-")).strip().replace(" ", "_") if plan else "projeto_drift"
            proj_path = Path("d:/CUTWIREDRIFT") / f"{safe_title}.drift"
            if not proj_path.exists():
                drift_files = list(Path("d:/CUTWIREDRIFT").glob("*.drift"))
                if drift_files:
                    proj_path = drift_files[0]

            drift_exe = Path("d:/CUTWIREDRIFT/Drift/drift.exe").resolve()
            import subprocess
            try:
                cmd = [str(drift_exe), str(proj_path)] if proj_path.exists() else [str(drift_exe)]
                subprocess.Popen(cmd, cwd=str(drift_exe.parent))
                return self.send_json({"ok": True, "opened": str(proj_path)})
            except Exception as e:
                return self.send_json({"ok": False, "error": str(e)})
        else:
            self.send_response(404)
            self.end_headers()

    def send_json(self, obj: Dict[str, Any], status: int = 200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(json.dumps(obj, ensure_ascii=False).encode("utf-8"))

def start_server(port: int = 8765):
    import webbrowser
    print(f"Iniciando Servidor Drift Roteiro IA em http://127.0.0.1:{port}...")
    try:
        webbrowser.open(f"http://127.0.0.1:{port}")
    except Exception:
        pass
    with socketserver.TCPServer(("127.0.0.1", port), AIEditorHandler) as httpd:
        print(f"Servidor ativo! Pressione Ctrl+C para encerrar.")
        httpd.serve_forever()

if __name__ == "__main__":
    start_server()


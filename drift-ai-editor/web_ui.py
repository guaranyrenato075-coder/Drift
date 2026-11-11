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
from director.long_form_retention_director import LongFormRetentionDirector
from pipeline.smart_provider_router import SmartProviderRouter
from pipeline.concurrent_provider_search import ConcurrentProviderSearch
from storage.disk_space_guard import DiskSpaceGuard
from editing.color_grading_engine import ColorGradingEngine
from audio.sound_fx_foley import SoundFXAutoFoley
from pipeline.auto_chaptering import AutoChapteringEngine
from audio.smart_audio_denoise_enhancer import SmartAudioDenoiseEnhancer
from analysis.scene_pacing_auditor import ScenePacingAuditor
from analysis.script_tone_polisher import ScriptTonePolisher
from editing.safe_zone_framing import SafeZoneMultiFormatFraming
from audio.audio_stem_splitter import AudioStemSplitter
from pipeline.clickbait_title_generator import ClickbaitTitleHookGenerator
from editing.broll_bouncer import BrollBouncer
from storage.project_packager_zip import ProjectPackagerZip
from editing.subtitle_styler import AITranscriptionSubtitleStyler
from editing.smart_transition_director import SmartSceneTransitionDirector
from pipeline.shorts_extractor import ContentRepurposerShortsExtractor
from pipeline.thumbnail_composer import AutoThumbnailVisualComposer
from pipeline.hashtag_tag_cloud_generator import AIHashtagTagCloudGenerator
from editing.smart_ken_burns_director import SmartSceneKenBurnsDirector
from editing.watermark_branding_engine import VideoWatermarkBrandingEngine, BrandingConfig
from pipeline.preset_video_templates import OneClickPresetVideoTemplates
from audio.dynamic_ducking_punch_director import DynamicZoomPunchAudioDuckingDirector
from analysis.retention_heatmap_auditor import VisualRetentionHeatmapAuditor
from editing.smart_color_matcher import SmartLutCinematicColorMatcher
from pipeline.multi_export_orchestrator import SocialMediaMultiExportPresets
from pipeline.story_hook_split_tester import AIStoryHookABSplitTester
from audio.beat_drop_scene_sync import SoundtrackBeatDropSceneSync
from voice.emotion_inflection_director import AIVoiceEmotionInflectionDirector
from editing.chapter_card_generator import AutoVideoChapterCardGenerator
from pipeline.thumbnail_variator_ab import AIAutomatedThumbnailVariatorAB
from core.hardware_gpu_tuner import AdaptiveHardwareGPUAutoTuner
from editing.retention_pacer import SmartAudienceRetentionPacer
from pipeline.youtube_community_packager import AutoYouTubeCommunityPostPackager
from audio.spatial_audio_panner import BinauralSpatialAudioPanner
from editing.end_screen_card_director import AIAutomatedEndScreenCardDirector
from audio.loudness_broadcast_normalizer import SmartLoudnessBroadcastNormalizer
from analysis.vocabulary_hook_auditor import ViralHookVocabularyAuditor
from editing.dynamic_broll_pacer import DynamicBrollPacer
from audio.sound_design_foley_director import SoundDesignFoleyAutoDirector
from editing.color_film_stock_emulator import AutoColorToneFilmStockEmulator
from pipeline.ctr_metadata_seo_optimizer import CTRMetadataSEOOptimizer
from audio.voice_denoise_spectral_isolator import AIVoiceDenoiseSpectralIsolator
from editing.smart_scene_transition_director import SmartSceneTransitionDirector
from pipeline.youtube_shorts_repurposer import YouTubeShortsRepurposer
from core.render_crash_recovery_guard import AutoRenderCrashRecoveryGuard
from pipeline.video_bitrate_bandwidth_optimizer import VideoBitrateBandwidthOptimizer
from analysis.visual_artifact_glitch_detector import VisualArtifactGlitchDetector
from audio.soundfx_doppler_pan_automator import SoundFXDopplerPanAutomator
from analysis.audience_dropoff_predictor import AudienceDropoffPredictor
from editing.dynamic_subtitles_word_highlighter import DynamicSubtitlesWordHighlighter
from editing.smart_visual_pacing_bpm_aligner import SmartVisualPacingBPMAligner
from analysis.narrative_tension_curve_auditor import NarrativeTensionCurveAuditor
from pipeline.auto_video_watermark_branding_director import AutoVideoWatermarkBrandingDirector
from editing.hdr_to_sdr_tone_mapper import HDRToSDRToneMapper
from analysis.thumbnail_face_detector import AIAutomatedThumbnailFaceDetector
from audio.soundtrack_auto_loop_stretcher import SoundtrackAutoLoopStretcher
from pipeline.auto_social_cutpack_exporter import AutoSocialCutpackExporter
from editing.cinematic_lower_thirds_animator import CinematicLowerThirdsAnimator
from analysis.visual_symmetry_aesthetic_auditor import VisualSymmetryAestheticAuditor
from audio.stereo_to_51_surround_upmixer import StereoTo51SurroundUpmixer
from pipeline.auto_color_palette_mood_extractor import AutoColorPaletteMoodExtractor
from editing.nle_timeline_xml_edl_exporter import NLETimelineXMLEdlExporter
from audio.dynamic_audio_ducking_sidechain_engine import DynamicAudioDuckingSidechainEngine
from pipeline.youtube_thumbnail_ab_grid_renderer import YouTubeThumbnailABGridRenderer
from core.desktop_launcher_daemon_packager import DesktopLauncherDaemonPackager
from editing.smart_selective_rerender_cache import SmartSelectiveRerenderCache
from core.cpu_thread_affinity_governor import CPUThreadAffinityGovernor
from pipeline.pre_render_deadweight_pruner import PreRenderDeadweightPruner
from storage.ssd_write_fatigue_mitigator import SSDWriteFatigueMitigator
from audio.lossless_audio_pass_through_engine import LosslessAudioPassThroughEngine
from core.thermal_adaptive_render_pacer import ThermalAdaptiveRenderPacer
from media.smart_proxy_resolution_scaler import SmartProxyResolutionScaler
from storage.sqlite_wal_checkpoint_governor import SQLiteWALCheckpointGovernor
from pipeline.zero_copy_frame_pipe_allocator import ZeroCopyFramePipeAllocator
from core.ram_working_set_trimmer import RamWorkingSetTrimmer
from editing.variable_framerate_jitter_smoother import VariableFramerateJitterSmoother
from storage.compact_json_delta_patcher import CompactJsonDeltaPatcher
from editing.smart_keyframe_interval_aligner import SmartKeyframeIntervalAligner
from pipeline.gpu_vram_leak_sentinel import GPUVRAMLeakSentinel
from core.nvme_trim_io_coalescer import NVMeTrimIOCoalescer
from media.smart_color_space_fast_matrix import SmartColorSpaceFastMatrix
from core.windows_timer_resolution_optimizer import WindowsTimerResolutionOptimizer
from editing.audio_peak_fast_integer_scanner import AudioPeakFastIntegerScanner
from media.speculative_disk_seek_canceller import SpeculativeDiskSeekCanceller
from pipeline.gpu_compute_memory_barrier_guard import GPUComputeMemoryBarrierGuard
from core.thermal_throttling_prediction_governor import ThermalThrottlingPredictionGovernor
from storage.sparse_zero_copy_frame_pipe import SparseZeroCopyFramePipe
from editing.timeline_visual_viewport_culler import TimelineVisualViewportCuller
from media.audio_resample_subsampling_bypass import AudioResampleSubsamplingBypass
from core.cpu_cache_l3_affinity_balancer import CPUCacheL3AffinityBalancer
from editing.lossless_audio_crossfade_integer_lut import LosslessAudioCrossfadeIntegerLUT
from media.mp4_moov_atom_early_detector import MP4MoovAtomEarlyDetector
from pipeline.gpu_shader_warmup_pipeline_cache import GPUShaderWarmupPipelineCache
from core.numa_node_memory_locality_binder import NUMANodeMemoryLocalityBinder
from editing.bezier_easing_fixed_point_evaluator import BezierEasingFixedPointEvaluator
from media.prores_dnxhr_passthrough_muxer import ProResDNxHRPassthroughMuxer
from storage.journal_page_wear_leveling_mitigator import JournalPageWearLevelingMitigator
from audio.multi_chapter_mood_soundtrack import MultiChapterMoodSoundtrackOrchestrator
from editing.smart_ken_burns_punchin import SmartKenBurnsPunchInEngine
from pipeline.render_checkpoint_manager import RenderCheckpointManager
from pipeline.multilingual_audio_packager import MultilingualAudioPackager
from audio.smart_silence_breath_stripper import SmartSilenceBreathStripper
from editing.motion_infographics_generator import MotionInfographicsGenerator
from media.b_roll_gap_filler import BRollGapFiller
from core.eco_governor import EcoGovernor
from pipeline.mega_duration_architect import MegaDurationArchitect, MegaProductionPlan, MegaChapter
from core.ram_working_set_flusher import RamWorkingSetFlusher
from editing.draft_proxy_engine import DraftProxyEngine
from editing.lossless_stream_copy_detector import LosslessStreamCopyDetector
from core.disk_io_governor import DiskIoGovernor
from editing.fast_decode_optimizer import FastDecodeOptimizer
from core.sleep_inhibit_governor import SleepInhibitGovernor
from storage.rolling_cache_purge import RollingCachePurgeManager
from core.thermal_duty_cycle import ThermalDutyCyclePacer
from core.zero_gpu_occlusion_governor import ZeroGpuOcclusionGovernor
from core.compact_metadata_indexer import CompactMetadataIndexer
from audio.direct_clock_resampler import DirectClockAudioResampler
from editing.lazy_timeline_virtualizer import LazyTimelineVirtualizer
from audio.flac_in_memory_scratchpad import FlacInMemoryScratchpad
from storage.zero_fragmentation_preallocator import ZeroFragmentationPreallocator
from core.green_wattage_capper import GreenWattageCapper

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

      <div style="margin-bottom: 8px;">
        <label>Gradação de Cor (LUT Cinematográfico)</label>
        <select id="color-grading">
          <option value="warm_documentary" selected>Warm Documentary (História & Arte)</option>
          <option value="teal_and_orange">Teal & Orange (Blockbuster)</option>
          <option value="deep_space">Deep Space Contrast (Cosmos & Sci-Fi)</option>
          <option value="nordic_moody">Nordic Moody (Suspense & Mistério)</option>
          <option value="vintage_35mm">Vintage 35mm (Cinema Retrô)</option>
          <option value="neutral">Natural / Sem Gradação</option>
        </select>
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
      <button class="btn btn-secondary" style="border-color:#38bdf8; color:#38bdf8; font-weight:600;" onclick="abrirCapitulosYouTube()">⏱️ Capítulos YouTube & Timestamps</button>
      <button class="btn btn-secondary" style="border-color:#c084fc; color:#e9d5ff; font-weight:600;" onclick="abrirFoleySonoro()">🔊 Foley & Efeitos Sonoros (SFX)</button>
      <button class="btn btn-secondary" style="border-color:#10b981; color:#a7f3d0; font-weight:600;" onclick="abrirAuditoriaRitmo()">⚡ Auditoria de Ritmo & WPM</button>
      <button class="btn btn-secondary" style="border-color:#f59e0b; color:#fde047; font-weight:600;" onclick="abrirPolidorTom()">✍️ Polidor de Tom de Roteiro</button>
      <button class="btn btn-secondary" style="border-color:#ec4899; color:#f472b6; font-weight:600;" onclick="abrirGeradorTitulos()">🎣 Títulos Virais & Thumbnails (CTR)</button>
      <button class="btn btn-secondary" style="border-color:#38bdf8; color:#bae6fd; font-weight:600;" onclick="abrirStemsMixer()">🎛️ Stems de Áudio Separados</button>
      <button class="btn btn-secondary" style="border-color:#a855f7; color:#d8b4fe; font-weight:600;" onclick="injetarCutawaysBroll()">🎬 Injetar Cutaways B-Roll (Anti-Tédio)</button>
      <button class="btn btn-secondary" style="border-color:#10b981; color:#6ee7b7; font-weight:700;" onclick="baixarPacoteZip()">📦 Baixar Pacote Completo (.ZIP)</button>
      <button class="btn btn-secondary" style="border-color:#f59e0b; color:#fde047; font-weight:600;" onclick="abrirEstilosLegenda()">✨ Estilos de Legenda (.ASS)</button>
      <button class="btn btn-secondary" style="border-color:#3b82f6; color:#93c5fd; font-weight:600;" onclick="abrirDiretorTransicoes()">🎭 Diretor de Transições</button>
      <button class="btn btn-secondary" style="border-color:#ec4899; color:#f472b6; font-weight:600;" onclick="abrirExtratorShorts()">✂️ Extrair Cortes Shorts (9:16)</button>
      <button class="btn btn-secondary" style="border-color:#10b981; color:#a7f3d0; font-weight:600;" onclick="comporThumbnailVisual()">🖼️ Gerar Thumbnail Visual HD</button>
      <button class="btn btn-secondary" style="border-color:#38bdf8; color:#bae6fd; font-weight:600;" onclick="abrirSeoTags()">🏷️ Gerador de Tags & SEO YouTube</button>
      <button class="btn btn-secondary" style="border-color:#a855f7; color:#e9d5ff; font-weight:600;" onclick="abrirKenBurnsDirector()">🎥 Diretor de Câmera Ken Burns</button>
      <button class="btn btn-secondary" style="border-color:#ec4899; color:#fbcfe8; font-weight:600;" onclick="abrirBrandingModal()">🛡️ Marca D'água & Branding</button>
      <button class="btn" style="background:#7c3aed; color:#fff; font-weight:700;" onclick="abrirTemplatesModal()">⚡ Templates de Canal em 1-Clique</button>
      <button class="btn btn-secondary" style="border-color:#f59e0b; color:#fde68a; font-weight:600;" onclick="abrirDuckingPunchModal()">🎙️ Punch-In & Auto-Ducking BGM</button>
      <button class="btn btn-secondary" style="border-color:#10b981; color:#a7f3d0; font-weight:600;" onclick="abrirRetentionModal()">📊 Curva de Retenção & Heatmap</button>
      <button class="btn btn-secondary" style="border-color:#06b6d4; color:#a5f3fc; font-weight:600;" onclick="abrirColorMatcherModal()">🎨 Color Matcher de Acervos (5600K)</button>
      <button class="btn" style="background:#2563eb; color:#fff; font-weight:700;" onclick="abrirMultiExportModal()">📱 Multi-Export Simultâneo (1-Clique)</button>
      <button class="btn btn-secondary" style="border-color:#d946ef; color:#f5d0fe; font-weight:600;" onclick="abrirHookTesterModal()">🎣 Testador A/B de Ganchos (5s)</button>
      <button class="btn btn-secondary" style="border-color:#f59e0b; color:#fde68a; font-weight:600;" onclick="abrirBeatSyncModal()">🎵 Sincronizador de Beat Musical</button>
      <button class="btn btn-secondary" style="border-color:#8b5cf6; color:#ddd6fe; font-weight:600;" onclick="abrirVoiceEmotionModal()">🎭 Diretor de Emoção da Voz IA</button>
      <button class="btn" style="background:#059669; color:#fff; font-weight:700;" onclick="abrirChapterCardsModal()">🎬 Cartelas de Capítulos HD</button>
      <button class="btn btn-secondary" style="border-color:#f43f5e; color:#fecdd3; font-weight:600;" onclick="abrirQuadThumbnailsModal()">🖼️ Quad-Thumbnails A/B/C/D</button>
      <button class="btn btn-secondary" style="border-color:#eab308; color:#fef08a; font-weight:600;" onclick="abrirHardwareTunerModal()">⚡ Auto-Tuner GPU/CPU Hardware</button>
      <button class="btn btn-secondary" style="border-color:#ef4444; color:#fecaca; font-weight:600;" onclick="abrirRetentionPacerModal()">💓 Ritmo Cardíaco & Dopamina</button>
      <button class="btn" style="background:#0284c7; color:#fff; font-weight:700;" onclick="abrirCommunityPostModal()">📢 Posts de Comunidade & Enquetes</button>
      <button class="btn btn-secondary" style="border-color:#06b6d4; color:#a5f3fc; font-weight:600;" onclick="abrirSpatialAudioModal()">🎧 Áudio Espacial 3D (8D)</button>
      <button class="btn btn-secondary" style="border-color:#f59e0b; color:#fde68a; font-weight:600;" onclick="abrirEndScreenModal()">🎬 Telas Finais YouTube (End-Screen)</button>
      <button class="btn btn-secondary" style="border-color:#10b981; color:#a7f3d0; font-weight:600;" onclick="abrirLoudnessModal()">🎚️ Normalizador -14 LUFS (EBU R128)</button>
      <button class="btn" style="background:#7c3aed; color:#fff; font-weight:700;" onclick="abrirVocabularyModal()">🧠 Auditor Neuro-Linguístico</button>
      <button class="btn btn-secondary" style="border-color:#38bdf8; color:#bae6fd; font-weight:600;" onclick="abrirBrollPacerModal()">🎞️ Cadência Dinâmica B-Roll</button>
      <button class="btn btn-secondary" style="border-color:#ec4899; color:#fbcfe8; font-weight:600;" onclick="abrirFoleyModal()">🔊 Sound Design & Foley</button>
      <button class="btn btn-secondary" style="border-color:#eab308; color:#fef08a; font-weight:600;" onclick="abrirFilmStockModal()">📽️ Emulador de Película 35mm</button>
      <button class="btn btn-secondary" style="border-color:#14b8a6; color:#99f6e4; font-weight:600;" onclick="abrirCTROptimizerModal()">📈 Metadados SEO & Títulos CTR</button>
      <button class="btn btn-secondary" style="border-color:#6366f1; color:#c7d2fe; font-weight:600;" onclick="abrirDenoiseModal()">🎙️ Denoise Espectral de Voz</button>
      <button class="btn btn-secondary" style="border-color:#f97316; color:#ffedd5; font-weight:600;" onclick="abrirTransitionsModal()">🔀 Transições Cinemáticas (IA)</button>
      <button class="btn btn-secondary" style="border-color:#e11d48; color:#ffe4e6; font-weight:600;" onclick="abrirShortsModal()">📱 Repurpose Shorts 9:16</button>
      <button class="btn btn-secondary" style="border-color:#22c55e; color:#bbf7d0; font-weight:600;" onclick="abrirRecoveryModal()">🛡️ Checkpoint & Crash Recovery</button>
      <button class="btn btn-secondary" style="border-color:#3b82f6; color:#bfdbfe; font-weight:600;" onclick="abrirBitrateModal()">🚀 Otimizador Bitrate & Compressão</button>
      <button class="btn btn-secondary" style="border-color:#a855f7; color:#f3e8ff; font-weight:600;" onclick="abrirQCModal()">🔍 Controle de Qualidade (QC Vídeo)</button>
      <button class="btn btn-secondary" style="border-color:#06b6d4; color:#cffafe; font-weight:600;" onclick="abrirDopplerModal()">🏎️ Áudio Doppler 3D (SFX)</button>
      <button class="btn btn-secondary" style="border-color:#eab308; color:#fef9c3; font-weight:600;" onclick="abrirDropoffModal()">📉 Preditor de Abandono (Drop-Off)</button>
      <button class="btn btn-secondary" style="border-color:#ec4899; color:#fce7f3; font-weight:600;" onclick="abrirDynamicSubtitlesModal()">💬 Legendas Dinâmicas (Karaoke)</button>
      <button class="btn btn-secondary" style="border-color:#8b5cf6; color:#ede9fe; font-weight:600;" onclick="abrirBPMAlignerModal()">🎵 Alinhador de Cortes por BPM</button>
      <button class="btn btn-secondary" style="border-color:#f43f5e; color:#ffe4e6; font-weight:600;" onclick="abrirTensionCurveModal()">📈 Curva de Tensão (3 Atos)</button>
      <button class="btn btn-secondary" style="border-color:#10b981; color:#d1fae5; font-weight:600;" onclick="abrirWatermarkModal()">🛡️ Marca d'Água & Anti-Pirataria</button>
      <button class="btn btn-secondary" style="border-color:#f59e0b; color:#fef3c7; font-weight:600;" onclick="abrirHDRToneMapModal()">🎨 Tone Mapping HDR ➔ SDR</button>
      <button class="btn btn-secondary" style="border-color:#38bdf8; color:#e0f2fe; font-weight:600;" onclick="abrirFaceDetectorModal()">👤 Foco Facial em Miniaturas</button>
      <button class="btn btn-secondary" style="border-color:#a855f7; color:#f5d0fe; font-weight:600;" onclick="abrirSoundtrackLoopModal()">🔁 Loop Infinito de Trilha</button>
      <button class="btn btn-secondary" style="border-color:#06b6d4; color:#cffafe; font-weight:600;" onclick="abrirCutpackModal()">📦 Exportador de Cutpack Social</button>
      <button class="btn btn-secondary" style="border-color:#f43f5e; color:#ffe4e6; font-weight:600;" onclick="abrirLowerThirdsModal()">🏷️ Lower Thirds Animados</button>
      <button class="btn btn-secondary" style="border-color:#10b981; color:#d1fae5; font-weight:600;" onclick="abrirSymmetryModal()">📐 Auditoria Estética & Simetria</button>
      <button class="btn btn-secondary" style="border-color:#6366f1; color:#e0e7ff; font-weight:600;" onclick="abrirSurroundModal()">🔊 Áudio Surround 5.1 (Cinema)</button>
      <button class="btn btn-secondary" style="border-color:#ec4899; color:#fce7f3; font-weight:600;" onclick="abrirPaletteModal()">🎨 Paleta Cromática de Humor</button>
      <button class="btn btn-secondary" style="border-color:#eab308; color:#fef08a; font-weight:600;" onclick="abrirNLEModal()">🎬 Exportar NLE (DaVinci/Premiere)</button>
      <button class="btn btn-secondary" style="border-color:#14b8a6; color:#ccfbf1; font-weight:600;" onclick="abrirDuckingModal()">🎚️ Sidechain Audio Ducking</button>
      <button class="btn btn-secondary" style="border-color:#8b5cf6; color:#ede9fe; font-weight:600;" onclick="abrirThumbnailsABModal()">🖼️ Grade A/B de Thumbnails</button>
      <button class="btn btn-secondary" style="border-color:#22c55e; color:#dcfce7; font-weight:600;" onclick="gerarLauncherDesktop()">⚡ Gerar Launcher Desktop 1-Clique</button>
      <button class="btn btn-secondary" style="border-color:#38bdf8; color:#e0f2fe; font-weight:600;" onclick="abrirAffinityModal()">🛡️ Afinidade CPU & PC Frio</button>
      <button class="btn btn-secondary" style="border-color:#fbbf24; color:#fef3c7; font-weight:600;" onclick="abrirSelectiveRerenderModal()">⚡ Render Seletivo (Zero GPU Waste)</button>
      <button class="btn btn-secondary" style="border-color:#f472b6; color:#fce7f3; font-weight:600;" onclick="abrirPrunerModal()">🧹 Poda de Cenas Inertes</button>
      <button class="btn btn-secondary" style="border-color:#4ade80; color:#dcfce7; font-weight:600;" onclick="abrirSSDFatigueModal()">💾 Preservação de SSD (Zero Wear)</button>
      <button class="btn btn-secondary" style="border-color:#a3e635; color:#ecfccb; font-weight:600;" onclick="abrirAudioPassThroughModal()">🎵 Áudio Pass-Through (Zero CPU)</button>
      <button class="btn btn-secondary" style="border-color:#f97316; color:#ffedd5; font-weight:600;" onclick="abrirThermalPacerModal()">🌡️ Pacer Térmico Anti-Aquecimento</button>
      <button class="btn btn-secondary" style="border-color:#06b6d4; color:#cffafe; font-weight:600;" onclick="abrirSmartProxyModal()">👁️ Proxies Leves (Economia 70% RAM)</button>
      <button class="btn btn-secondary" style="border-color:#9333ea; color:#f3e8ff; font-weight:600;" onclick="executarWALCheckpoint()">🗄️ Manutenção WAL do SQLite</button>
      <button class="btn btn-secondary" style="border-color:#38bdf8; color:#e0f2fe; font-weight:600;" onclick="abrirZeroCopyModal()">🚀 Pipe de Quadros Zero-Copy (Zero I/O)</button>
      <button class="btn btn-secondary" style="border-color:#10b981; color:#d1fae5; font-weight:600;" onclick="executarLimpezaWorkingSet()">🧹 Desalocar RAM (EmptyWorkingSet)</button>
      <button class="btn btn-secondary" style="border-color:#f59e0b; color:#fef3c7; font-weight:600;" onclick="abrirVFROptimizerModal()">⏱️ Estabilizador VFR Anti-Jitter</button>
      <button class="btn btn-secondary" style="border-color:#ec4899; color:#fce7f3; font-weight:600;" onclick="abrirDeltaPatcherModal()">🧩 Gravador Delta JSON (Poupa 95% SSD)</button>
      <button class="btn btn-secondary" style="border-color:#f43f5e; color:#ffe4e6; font-weight:600;" onclick="abrirKeyframeAlignerModal()">✂️ Alinhador de Keyframe I-Frame</button>
      <button class="btn btn-secondary" style="border-color:#8b5cf6; color:#ede9fe; font-weight:600;" onclick="abrirVRAMSentinelModal()">🛡️ Sentinela Anti-Vazamento VRAM</button>
      <button class="btn btn-secondary" style="border-color:#14b8a6; color:#ccfbf1; font-weight:600;" onclick="abrirNVMeCoalescerModal()">⚡ Coalescedor 4KB NVMe SSD</button>
      <button class="btn btn-secondary" style="border-color:#eab308; color:#fef08a; font-weight:600;" onclick="abrirColorMatrixModal()">🎨 Matriz Cromática Rápida SIMD</button>
      <button class="btn btn-secondary" style="border-color:#0284c7; color:#e0f2fe; font-weight:600;" onclick="abrirTimerOptimizerModal()">⏱️ Timer do Windows (Eco Idle)</button>
      <button class="btn btn-secondary" style="border-color:#16a34a; color:#dcfce7; font-weight:600;" onclick="abrirAudioPeakModal()">🔊 Scanner de Picos Inteiro (Zero Float)</button>
      <button class="btn btn-secondary" style="border-color:#dc2626; color:#fee2e2; font-weight:600;" onclick="abrirSeekCancellerModal()">🛑 Cancelador de Seeks no SSD</button>
      <button class="btn btn-secondary" style="border-color:#7c3aed; color:#ede9fe; font-weight:600;" onclick="abrirGPUBarrierModal()">🛡️ Barreira de Memória GPU (No Stall)</button>
      <button class="btn btn-secondary" style="border-color:#ea580c; color:#ffedd5; font-weight:600;" onclick="abrirThermalGovernorModal()">🔥 Prevenção Throttling CPU/GPU</button>
      <button class="btn btn-secondary" style="border-color:#0284c7; color:#e0f2fe; font-weight:600;" onclick="abrirSparsePipeModal()">🧊 Pipe Zero-Copy 1080p (Pool RAM)</button>
      <button class="btn btn-secondary" style="border-color:#65a30d; color:#ecfccb; font-weight:600;" onclick="abrirViewportCullerModal()">✂️ Culling de Linha do Tempo O(log N)</button>
      <button class="btn btn-secondary" style="border-color:#0d9488; color:#ccfbf1; font-weight:600;" onclick="abrirAudioBypassModal()">🎵 Bypass Reamostragem (Bitstream)</button>
      <button class="btn btn-secondary" style="border-color:#6366f1; color:#e0e7ff; font-weight:600;" onclick="abrirCPUAffinityModal()">🧠 Afinidade L3 CPU (Zero Bus Traffic)</button>
      <button class="btn btn-secondary" style="border-color:#f43f5e; color:#ffe4e6; font-weight:600;" onclick="abrirAudioCrossfadeModal()">🎶 Crossfade Inteiro LUT (No FPU Load)</button>
      <button class="btn btn-secondary" style="border-color:#38bdf8; color:#e0f2fe; font-weight:600;" onclick="abrirMoovDetectorModal()">⚡ Leitura FastStart MOOV (SSD Shield)</button>
      <button class="btn btn-secondary" style="border-color:#a855f7; color:#f3e8ff; font-weight:600;" onclick="abrirShaderWarmupModal()">🛡️ Aquecimento de Shaders GPU (No Stutter)</button>
      <button class="btn btn-secondary" style="border-color:#14b8a6; color:#ccfbf1; font-weight:600;" onclick="abrirNUMABindingModal()">🧬 Localidade NUMA RAM/CPU (Zero Hops)</button>
      <button class="btn btn-secondary" style="border-color:#f59e0b; color:#fef3c7; font-weight:600;" onclick="abrirBezierFixedModal()">📐 Bezier Easing Q16.16 (Zero FPU Load)</button>
      <button class="btn btn-secondary" style="border-color:#22c55e; color:#dcfce7; font-weight:600;" onclick="abrirProResPassthroughModal()">🎬 Passthrough ProRes/DNxHR (Zero Render)</button>
      <button class="btn btn-secondary" style="border-color:#ec4899; color:#fce7f3; font-weight:600;" onclick="abrirWearMitigatorModal()">🛡️ Proteção de Desgaste NAND 64KB (WAF Shield)</button>

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
        <span style="color:var(--border);">|</span>
        <span id="telemetry-disk" style="color:#a7f3d0;">🛡️ Disco C: Saudável</span>
      </div>
    </div>

    <div class="content-area">
      <div id="status-banner"></div>

      <!-- Live Preview Player -->
      <div id="preview-player-panel" style="background:var(--panel-bg); border:1px solid var(--border); border-radius:8px; padding:12px 16px; margin-bottom:16px; display:none; flex-direction:column; gap:10px; box-shadow:0 4px 6px -1px rgba(0,0,0,0.3);">
        <div style="display:flex; justify-content:space-between; align-items:center;">
          <div style="display:flex; align-items:center; gap:8px;">
            <span style="font-size:1.1rem;">📺</span>
            <span style="font-weight:700; color:#fff; font-size:0.95rem;">Live Preview Player</span>
            <span id="preview-scene-indicator" style="background:#1e293b; color:#93c5fd; border:1px solid #334155; font-size:0.75rem; padding:2px 8px; border-radius:12px;">Cena 1 de 1</span>
            <span id="preview-provider-badge"></span>
            <label style="font-size:0.75rem; color:var(--text-muted); display:flex; align-items:center; gap:4px; cursor:pointer; margin-left:8px;">
              <input type="checkbox" id="chk-safe-zone" onchange="toggleSafeZoneOverlay(this.checked)"> Safe Zone 9:16
            </label>
          </div>
          <div style="font-size:0.8rem; color:var(--text-muted); font-family:monospace;" id="preview-timing">00:00 / 00:00</div>
        </div>
        
        <div style="display:grid; grid-template-columns: 280px 1fr; gap:16px; align-items:center;">
          <div id="preview-media-container" style="background:#090d16; border-radius:6px; height:158px; display:flex; align-items:center; justify-content:center; overflow:hidden; border:1px solid var(--border); position:relative;">
            <img id="preview-media-img" src="" alt="Cena" style="width:100%; height:100%; object-fit:cover; display:none;" />
            <div id="preview-no-media" style="color:var(--text-muted); font-size:0.8rem; text-align:center; padding:10px;">Sem mídia selecionada</div>
            <div id="preview-safe-zone-overlay" style="display:none; position:absolute; top:14%; bottom:22%; left:5%; right:16%; border:1px dashed rgba(239, 68, 68, 0.7); pointer-events:none; box-shadow:inset 0 0 10px rgba(239, 68, 68, 0.2);"></div>
          </div>
          <div style="display:flex; flex-direction:column; gap:8px;">
            <div style="font-size:0.8rem; color:#94a3b8; font-weight:600;">Narração Falada:</div>
            <div id="preview-narration-text" style="font-size:0.88rem; color:#f1f5f9; line-height:1.45; max-height:64px; overflow-y:auto; background:var(--card-bg); padding:8px 12px; border-radius:4px; border:1px solid var(--border);"></div>
            <div style="display:flex; align-items:center; gap:8px; margin-top:4px;">
              <button class="btn btn-secondary" style="padding:4px 10px; font-size:0.8rem;" onclick="previewPrevScene()">◀ Anterior</button>
              <button class="btn" style="padding:4px 14px; font-size:0.8rem; background:#10b981;" id="btn-preview-audio" onclick="togglePlayPreviewAudio()">▶ Ouvir Áudio</button>
              <button class="btn btn-secondary" style="padding:4px 10px; font-size:0.8rem;" onclick="previewNextScene()">Próxima ▶</button>
              <audio id="preview-audio-player" style="display:none;" onended="onPreviewAudioEnded()"></audio>
            </div>
          </div>
        </div>
      </div>
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

    function getProviderBadge(platform) {
      if (!platform) return '<span style="color:var(--text-muted);">Pendente</span>';
      const p = platform.toLowerCase();
      if (p.includes('nasa')) return '<span style="background:#1e3a8a; color:#bfdbfe; padding:2px 6px; border-radius:4px; font-size:0.75rem; font-weight:700;">🚀 NASA</span>';
      if (p.includes('harvard')) return '<span style="background:#581c87; color:#e9d5ff; padding:2px 6px; border-radius:4px; font-size:0.75rem; font-weight:700;">🎓 Harvard Art</span>';
      if (p.includes('rijksmuseum') || p.includes('rijks')) return '<span style="background:#7c2d12; color:#fed7aa; padding:2px 6px; border-radius:4px; font-size:0.75rem; font-weight:700;">🏛️ Rijksmuseum</span>';
      if (p.includes('foodiesfeed')) return '<span style="background:#831843; color:#fbcfe8; padding:2px 6px; border-radius:4px; font-size:0.75rem; font-weight:700;">🍲 Foodiesfeed</span>';
      if (p.includes('nps')) return '<span style="background:#064e3b; color:#a7f3d0; padding:2px 6px; border-radius:4px; font-size:0.75rem; font-weight:700;">🌲 NPS Wild</span>';
      if (p.includes('artvee')) return '<span style="background:#701a75; color:#f5d0fe; padding:2px 6px; border-radius:4px; font-size:0.75rem; font-weight:700;">🎨 Artvee</span>';
      if (p.includes('wikimedia')) return '<span style="background:#065f46; color:#a7f3d0; padding:2px 6px; border-radius:4px; font-size:0.75rem; font-weight:700;">🌐 Wikimedia</span>';
      if (p.includes('metropolitan') || p.includes('met')) return '<span style="background:#991b1b; color:#fecaca; padding:2px 6px; border-radius:4px; font-size:0.75rem; font-weight:700;">🏛️ The Met</span>';
      if (p.includes('pexels')) return '<span style="background:#065f46; color:#a7f3d0; padding:2px 6px; border-radius:4px; font-size:0.75rem; font-weight:700;">📹 Pexels</span>';
      if (p.includes('pixabay')) return '<span style="background:#15803d; color:#bbf7d0; padding:2px 6px; border-radius:4px; font-size:0.75rem; font-weight:700;">📷 Pixabay</span>';
      if (p.includes('europeana')) return '<span style="background:#1d4ed8; color:#dbeafe; padding:2px 6px; border-radius:4px; font-size:0.75rem; font-weight:700;">🇪🇺 Europeana</span>';
      return `<span style="background:#374151; color:#f3f4f6; padding:2px 6px; border-radius:4px; font-size:0.75rem; font-weight:600;">📁 ${platform}</span>`;
    }

    async function selectCandidate(candId, sceneOrder) {
      if (!currentPlan) return;
      try {
        const res = await fetch('/api/select_media', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ project_id: currentPlan.project_id, scene_order: sceneOrder, candidate_id: candId })
        });
        const data = await res.json();
        if (data.ok) {
          currentPlan = data.plan;
          renderScenes();
        }
      } catch (e) {
        console.error(e);
      }
    }

    async function checkDiskHealth() {
      try {
        const res = await fetch('/api/disk_health');
        const data = await res.json();
        if (data.ok && data.health) {
          const diskEl = document.getElementById('telemetry-disk');
          if (diskEl) {
            diskEl.innerText = `🛡️ C: ${data.health.free_gb.toFixed(1)}GB livre`;
            diskEl.style.color = data.health.is_critical ? '#ef4444' : (data.health.is_warning ? '#f59e0b' : '#a7f3d0');
          }
        }
      } catch(e) {}
    }
    setTimeout(checkDiskHealth, 1000);
    setInterval(checkDiskHealth, 20000);

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
        
        let candidatesHtml = '';
        if (s.candidates && s.candidates.length > 1) {
          candidatesHtml = `<div style="margin-top:8px; border-top:1px dashed var(--border); padding-top:6px;">
            <div style="font-size:0.72rem; color:var(--text-muted); margin-bottom:4px;">Alternativas (${s.candidates.length}):</div>
            <div style="display:flex; gap:6px; flex-wrap:wrap;">` +
            s.candidates.map(c => {
              let isSel = s.selected_media && (s.selected_media.candidate_id === c.candidate_id || s.selected_media.external_id === c.external_id);
              let border = isSel ? '2px solid #10b981' : '1px solid var(--border)';
              let candId = c.candidate_id || c.external_id;
              return `<button style="background:var(--card-bg); border:${border}; border-radius:4px; padding:3px 6px; cursor:pointer; font-size:0.7rem; color:#fff;" onclick="selectCandidate('${candId}', ${s.order})">${getProviderBadge(c.platform)}</button>`;
            }).join('') + `</div></div>`;
        }

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
            ${candidatesHtml}
          </div>
          <div class="scene-meta">
            <div><span class="status-pill ${statusClass}">${s.state.toUpperCase()}</span></div>
            <div><b>Duração:</b> ${(s.duration || 0).toFixed(1)}s</div>
            <div><b>Mídia:</b> ${s.selected_media ? getProviderBadge(s.selected_media.platform) : 'Pendente'}</div>
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
      updatePreviewPlayer();
    }

    let currentPreviewSceneIndex = 0;
    let isPreviewAudioPlaying = false;

    function updatePreviewPlayer() {
      if (!currentPlan || !currentPlan.scenes || currentPlan.scenes.length === 0) {
        document.getElementById('preview-player-panel').style.display = 'none';
        return;
      }
      document.getElementById('preview-player-panel').style.display = 'flex';
      if (currentPreviewSceneIndex >= currentPlan.scenes.length) currentPreviewSceneIndex = 0;
      if (currentPreviewSceneIndex < 0) currentPreviewSceneIndex = currentPlan.scenes.length - 1;

      const scene = currentPlan.scenes[currentPreviewSceneIndex];
      document.getElementById('preview-scene-indicator').innerText = `Cena ${scene.order} de ${currentPlan.scenes.length}`;
      document.getElementById('preview-narration-text').innerText = scene.narration_text || '(Sem narração falada)';

      const badgeEl = document.getElementById('preview-provider-badge');
      const imgEl = document.getElementById('preview-media-img');
      const noMediaEl = document.getElementById('preview-no-media');

      if (scene.selected_media) {
        badgeEl.innerHTML = getProviderBadge(scene.selected_media.platform);
        if (scene.selected_media.thumbnail_url || scene.selected_media.url) {
          imgEl.src = scene.selected_media.thumbnail_url || scene.selected_media.url;
          imgEl.style.display = 'block';
          noMediaEl.style.display = 'none';
        } else {
          imgEl.style.display = 'none';
          noMediaEl.style.display = 'block';
          noMediaEl.innerText = `Mídia: ${scene.selected_media.platform}`;
        }
      } else {
        badgeEl.innerHTML = '<span style="color:var(--text-muted); font-size:0.75rem;">Mídia Pendente</span>';
        imgEl.style.display = 'none';
        noMediaEl.style.display = 'block';
        noMediaEl.innerText = 'Sem mídia selecionada';
      }

      // Timing acumulado
      let cumulative = 0;
      for (let i = 0; i < currentPreviewSceneIndex; i++) {
        cumulative += currentPlan.scenes[i].duration || 0;
      }
      let totalDur = currentPlan.scenes.reduce((acc, s) => acc + (s.duration || 0), 0);
      const fmt = (s) => {
        let m = Math.floor(s / 60);
        let sec = Math.floor(s % 60);
        return `${m < 10 ? '0' : ''}${m}:${sec < 10 ? '0' : ''}${sec}`;
      };
      document.getElementById('preview-timing').innerText = `${fmt(cumulative)} / ${fmt(totalDur)}`;

      const btn = document.getElementById('btn-preview-audio');
      btn.innerText = '▶ Ouvir Áudio';
      btn.style.background = '#10b981';
      isPreviewAudioPlaying = false;
    }

    function previewNextScene() {
      if (!currentPlan || !currentPlan.scenes.length) return;
      currentPreviewSceneIndex = (currentPreviewSceneIndex + 1) % currentPlan.scenes.length;
      updatePreviewPlayer();
    }

    function previewPrevScene() {
      if (!currentPlan || !currentPlan.scenes.length) return;
      currentPreviewSceneIndex = (currentPreviewSceneIndex - 1 + currentPlan.scenes.length) % currentPlan.scenes.length;
      updatePreviewPlayer();
    }

    async function togglePlayPreviewAudio() {
      if (!currentPlan) return;
      const scene = currentPlan.scenes[currentPreviewSceneIndex];
      const btn = document.getElementById('btn-preview-audio');
      if (isPreviewAudioPlaying) {
        await fetch('/api/stop_audio', { method: 'POST', body: '{}' });
        btn.innerText = '▶ Ouvir Áudio';
        btn.style.background = '#10b981';
        isPreviewAudioPlaying = false;
      } else {
        btn.innerText = '⏹ Parar Áudio';
        btn.style.background = '#ef4444';
        isPreviewAudioPlaying = true;
        try {
          await fetch('/api/play_audio', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ project_id: currentPlan.project_id, scene_order: scene.order })
          });
        } catch (e) {}
      }
    }

    function onPreviewAudioEnded() {
      const btn = document.getElementById('btn-preview-audio');
      btn.innerText = '▶ Ouvir Áudio';
      btn.style.background = '#10b981';
      isPreviewAudioPlaying = false;
    }

    async function abrirCapitulosYouTube() {
      if (!currentPlan) return alert('Analise o roteiro primeiro!');
      const res = await fetch(`/api/chapters?project_id=${currentPlan.project_id}`);
      const data = await res.json();
      if (data.ok) {
        document.getElementById('youtube-chapters-text').value = data.youtube_description;
        document.getElementById('chapters-modal').style.display = 'flex';
      }
    }
    function fecharCapitulosYouTube() {
      document.getElementById('chapters-modal').style.display = 'none';
    }
    function copiarCapitulosYouTube() {
      const area = document.getElementById('youtube-chapters-text');
      area.select();
      navigator.clipboard.writeText(area.value);
      alert('Capítulos & Timestamps copiados para a área de transferência!');
    }

    async function abrirFoleySonoro() {
      if (!currentPlan) return alert('Analise o roteiro primeiro!');
      const res = await fetch(`/api/foley/analyze?project_id=${currentPlan.project_id}`);
      const data = await res.json();
      if (data.ok) {
        const body = document.getElementById('foley-modal-body');
        if (!data.cues || data.cues.length === 0) {
          body.innerHTML = '<div style="color:var(--text-muted); text-align:center; padding:20px;">Nenhum efeito foley específico detectado no texto. A produção utilizará a trilha padrão.</div>';
        } else {
          body.innerHTML = data.cues.map(c => `
            <div style="background:var(--card-bg); border:1px solid var(--border); border-radius:6px; padding:10px 14px; display:flex; justify-content:space-between; align-items:center;">
              <div>
                <div style="font-weight:600; color:#fff;">🔊 Cena ${c.scene_order}: ${c.label}</div>
                <div style="font-size:0.8rem; color:var(--text-muted); margin-top:2px;">Gatilho: <b>"${c.trigger_keyword}"</b> | Início: ${c.relative_start_sec}s (${c.duration_sec}s dur)</div>
              </div>
              <div style="background:#1e1b4b; color:#c084fc; font-size:0.75rem; padding:4px 8px; border-radius:4px; font-weight:700;">${c.suggested_volume_db} dB</div>
            </div>
          `).join('');
        }
        document.getElementById('foley-modal').style.display = 'flex';
      }
    }
    function fecharFoleySonoro() {
      document.getElementById('foley-modal').style.display = 'none';
    }

    function toggleSafeZoneOverlay(enabled) {
      const ov = document.getElementById('preview-safe-zone-overlay');
      if (ov) ov.style.display = enabled ? 'block' : 'none';
    }

    async function abrirAuditoriaRitmo() {
      if (!currentPlan) return alert('Analise o roteiro primeiro!');
      const res = await fetch(`/api/pacing_audit?project_id=${currentPlan.project_id}`);
      const data = await res.json();
      if (data.ok) {
        document.getElementById('pacing-score').innerText = `${data.overall_retention_score}/100`;
        document.getElementById('pacing-score').style.color = data.overall_retention_score >= 80 ? '#10b981' : (data.overall_retention_score >= 60 ? '#f59e0b' : '#ef4444');
        document.getElementById('pacing-summary').innerText = data.summary;
        document.getElementById('pacing-wpm').innerText = `${data.average_wpm} WPM Médio`;
        
        const list = document.getElementById('pacing-scenes-list');
        list.innerHTML = data.scene_metrics.map(m => {
          let badgeColor = m.risk_level === 'safe' ? '#065f46' : (m.risk_level === 'moderate' ? '#854d0e' : '#991b1b');
          let textColor = m.risk_level === 'safe' ? '#a7f3d0' : (m.risk_level === 'moderate' ? '#fef08a' : '#fecaca');
          return `
            <div style="background:var(--card-bg); border:1px solid var(--border); border-radius:6px; padding:10px 14px; display:flex; flex-direction:column; gap:4px;">
              <div style="display:flex; justify-content:space-between; align-items:center;">
                <span style="font-weight:700; color:#fff;">Cena ${m.scene_order} (${m.duration_sec}s | ${m.word_count} palavras)</span>
                <span style="background:${badgeColor}; color:${textColor}; padding:2px 8px; border-radius:4px; font-size:0.75rem; font-weight:700;">${m.wpm} WPM - ${m.risk_level.toUpperCase()}</span>
              </div>
              <div style="font-size:0.8rem; color:var(--text-muted);">${m.actionable_recommendation}</div>
            </div>
          `;
        }).join('');

        document.getElementById('pacing-modal').style.display = 'flex';
      }
    }
    function fecharAuditoriaRitmo() {
      document.getElementById('pacing-modal').style.display = 'none';
    }

    function abrirPolidorTom() {
      if (!currentPlan) return alert('Analise o roteiro primeiro!');
      document.getElementById('tone-modal').style.display = 'flex';
    }
    function fecharPolidorTom() {
      document.getElementById('tone-modal').style.display = 'none';
    }
    async function aplicarPolimentoTom() {
      if (!currentPlan) return;
      const toneId = document.getElementById('tone-select').value;
      showStatus('Polindo estilo e ganchos do roteiro...', '#d97706');
      try {
        const res = await fetch('/api/polish_tone', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ project_id: currentPlan.project_id, tone_id: toneId })
        });
        const data = await res.json();
        if (data.ok) {
          currentPlan = data.plan;
          renderScenes();
          fecharPolidorTom();
          showStatus('Roteiro polido com sucesso para alto engajamento!', '#059669');
          setTimeout(() => { document.getElementById('status-banner').style.display = 'none'; }, 3000);
        }
      } catch (e) {
        alert('Erro ao polir roteiro: ' + e);
      }
    }

    async function abrirGeradorTitulos() {
      if (!currentPlan) return alert('Analise o roteiro primeiro!');
      const res = await fetch(`/api/titles/generate?project_id=${currentPlan.project_id}`);
      const data = await res.json();
      if (data.ok) {
        document.getElementById('titles-topic-badge').innerText = `Tópico Base: ${data.base_topic}`;
        const container = document.getElementById('titles-list-container');
        container.innerHTML = data.titles.map(t => `
          <div style="background:var(--card-bg); border:1px solid var(--border); border-radius:6px; padding:12px 14px; display:flex; flex-direction:column; gap:6px;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
              <span style="font-size:0.75rem; color:#93c5fd; font-weight:700;">${t.category.toUpperCase()}</span>
              <span style="background:#065f46; color:#a7f3d0; padding:2px 8px; border-radius:4px; font-size:0.75rem; font-weight:700;">CTR Estimado: ${t.estimated_ctr}</span>
            </div>
            <div style="font-size:0.95rem; font-weight:700; color:#fff; line-height:1.4;">${t.headline}</div>
            <div style="display:flex; justify-content:space-between; align-items:center; margin-top:4px;">
              <span style="font-size:0.8rem; color:var(--text-muted);">Selo Thumbnail: <b style="color:#fde047;">"${t.thumbnail_hook}"</b></span>
              <button class="btn btn-secondary" style="padding:4px 10px; font-size:0.75rem;" onclick="aplicarTituloSugerido('${encodeURIComponent(t.headline)}')">Adotar Este Título</button>
            </div>
          </div>
        `).join('');

        const badgesEl = document.getElementById('thumbnail-badges-container');
        badgesEl.innerHTML = data.thumbnail_badge_options.map(b => `<span style="background:#701a75; color:#f5d0fe; padding:4px 10px; border-radius:4px; font-weight:800; font-size:0.75rem;">${b}</span>`).join(' ');

        document.getElementById('titles-modal').style.display = 'flex';
      }
    }
    function fecharGeradorTitulos() {
      document.getElementById('titles-modal').style.display = 'none';
    }
    function aplicarTituloSugerido(encodedTitle) {
      const title = decodeURIComponent(encodedTitle);
      if (currentPlan) {
        currentPlan.title = title;
        document.getElementById('project-header').innerText = `Projeto: ${title}`;
        fecharGeradorTitulos();
        showStatus(`Título atualizado para: "${title}"`, '#059669');
        setTimeout(() => { document.getElementById('status-banner').style.display = 'none'; }, 3000);
      }
    }

    async function abrirStemsMixer() {
      if (!currentPlan) return alert('Analise o roteiro primeiro!');
      const res = await fetch(`/api/stems/manifest?project_id=${currentPlan.project_id}`);
      const data = await res.json();
      if (data.ok) {
        document.getElementById('stems-modal').style.display = 'flex';
      }
    }
    function fecharStemsMixer() {
      document.getElementById('stems-modal').style.display = 'none';
    }

    async function injetarCutawaysBroll() {
      if (!currentPlan) return alert('Analise o roteiro primeiro!');
      showStatus('Analisando cenas e agendando cutaways B-Roll...', '#d97706');
      try {
        const res = await fetch('/api/broll/bounce', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ project_id: currentPlan.project_id, threshold_sec: 4.5 })
        });
        const data = await res.json();
        if (data.ok) {
          showStatus(`Sucesso! ${data.cutaways_injected} cortes de B-Roll cutaway injetados (+${data.retention_boost_estimate_pct}% retenção estimada).`, '#059669');
          setTimeout(() => { document.getElementById('status-banner').style.display = 'none'; }, 4000);
        }
      } catch (e) {
        alert('Erro ao injetar B-Roll: ' + e);
      }
    }

    async function baixarPacoteZip() {
      if (!currentPlan) return alert('Analise o roteiro primeiro!');
      showStatus('Empacotando projeto completo em arquivo .ZIP...', '#2563eb');
      try {
        const res = await fetch('/api/project/package_zip', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ project_id: currentPlan.project_id })
        });
        const data = await res.json();
        if (data.ok) {
          showStatus(`Pacote ZIP criado com sucesso! ${data.file_count} arquivos em: ${data.zip_path}`, '#059669');
          alert(`Pacote do projeto compactado com sucesso!\n\nArquivo: ${data.zip_path}\nTotal de Arquivos: ${data.file_count}\nTamanho Compactado: ${(data.compressed_bytes / (1024*1024)).toFixed(2)} MB`);
        }
      } catch (e) {
        alert('Erro ao empacotar projeto: ' + e);
      }
    }

    function abrirEstilosLegenda() {
      if (!currentPlan) return alert('Analise o roteiro primeiro!');
      document.getElementById('subtitles-style-modal').style.display = 'flex';
    }
    function fecharEstilosLegenda() {
      document.getElementById('subtitles-style-modal').style.display = 'none';
    }
    async function aplicarEstiloLegenda() {
      if (!currentPlan) return;
      const styleId = document.getElementById('sub-style-select').value;
      showStatus('Gerando legendas (.ASS) estilizadas...', '#2563eb');
      try {
        const res = await fetch('/api/subtitles/generate_styled', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ project_id: currentPlan.project_id, style_id: styleId })
        });
        const data = await res.json();
        if (data.ok) {
          fecharEstilosLegenda();
          showStatus(`Legendas ${styleId.toUpperCase()} geradas com sucesso!`, '#059669');
          setTimeout(() => { document.getElementById('status-banner').style.display = 'none'; }, 3500);
          alert(`Legendas dinâmicas exportadas com sucesso!\n\nArquivo: ${data.file_path || 'legendas.ass'}\nEstilo: ${data.style_name}`);
        }
      } catch (e) {
        alert('Erro ao gerar legendas: ' + e);
      }
    }

    async function abrirDiretorTransicoes() {
      if (!currentPlan) return alert('Analise o roteiro primeiro!');
      const res = await fetch(`/api/transitions/plan?project_id=${currentPlan.project_id}`);
      const data = await res.json();
      if (data.ok) {
        const list = document.getElementById('transitions-plan-list');
        if (!data.transitions || data.transitions.length === 0) {
          list.innerHTML = '<div style="color:var(--text-muted); text-align:center; padding:15px;">Adicione pelo menos 2 cenas para orquestrar transições.</div>';
        } else {
          list.innerHTML = data.transitions.map(t => `
            <div style="background:var(--card-bg); border:1px solid var(--border); border-radius:6px; padding:10px 14px; display:flex; justify-content:space-between; align-items:center;">
              <div>
                <div style="font-weight:700; color:#fff;">Cena ${t.from_scene_order} ➔ Cena ${t.to_scene_order}: <span style="color:#60a5fa;">${t.transition_type.toUpperCase()}</span> (${t.duration_sec}s)</div>
                <div style="font-size:0.8rem; color:var(--text-muted); margin-top:2px;">${t.narrative_reason}</div>
              </div>
            </div>
          `).join('');
        }
        document.getElementById('transitions-modal').style.display = 'flex';
      }
    }
    function fecharDiretorTransicoes() {
      document.getElementById('transitions-modal').style.display = 'none';
    }

    async function abrirExtratorShorts() {
      if (!currentPlan) return alert('Analise o roteiro primeiro!');
      const res = await fetch(`/api/shorts/extract?project_id=${currentPlan.project_id}`);
      const data = await res.json();
      if (data.ok) {
        const list = document.getElementById('shorts-extract-list');
        if (!data.shorts || data.shorts.length === 0) {
          list.innerHTML = '<div style="color:var(--text-muted); text-align:center; padding:15px;">Roteiro muito curto para extração de Shorts múltiplos.</div>';
        } else {
          list.innerHTML = data.shorts.map(s => `
            <div style="background:var(--card-bg); border:1px solid var(--border); border-radius:6px; padding:12px 14px; display:flex; flex-direction:column; gap:6px;">
              <div style="display:flex; justify-content:space-between; align-items:center;">
                <span style="font-weight:700; color:#fff;">${s.title}</span>
                <span style="background:#065f46; color:#a7f3d0; padding:2px 8px; border-radius:4px; font-size:0.75rem; font-weight:700;">Score Viral: ${s.viral_hook_score}/100</span>
              </div>
              <div style="font-size:0.8rem; color:var(--text-muted);">Cenas ${s.start_scene_order} a ${s.end_scene_order} | Duração: ${s.total_duration_sec}s | Formato: 9:16 Vertical</div>
              <div style="font-size:0.75rem; color:#93c5fd;">Tags: ${s.recommended_hashtags}</div>
            </div>
          `).join('');
        }
        document.getElementById('shorts-extractor-modal').style.display = 'flex';
      }
    }
    function fecharExtratorShorts() {
      document.getElementById('shorts-extractor-modal').style.display = 'none';
    }

    async function comporThumbnailVisual() {
      if (!currentPlan) return alert('Analise o roteiro primeiro!');
      showStatus('Renderizando capa/thumbnail visual em alta resolução 1280x720...', '#7c3aed');
      try {
        const res = await fetch('/api/thumbnail/compose', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ project_id: currentPlan.project_id, headline_text: 'A VERDADE' })
        });
        const data = await res.json();
        if (data.ok) {
          showStatus(`Thumbnail gerada com sucesso! Arquivo: ${data.output_image_path}`, '#059669');
          alert(`Thumbnail 1280x720 composta com sucesso!\n\nArquivo: ${data.output_image_path}\nTexto: "${data.headline_text}"\nHero Platform: ${data.hero_platform}`);
        }
      } catch (e) {
        alert('Erro ao compor thumbnail: ' + e);
      }
    }

    // === NOVAS FUNÇÕES: SEO TAGS, KEN BURNS, BRANDING, TEMPLATES ===
    async function abrirSeoTags() {
      const topic = currentPlan ? (currentPlan.title || 'Vídeo Educativo') : 'Vídeo Educativo';
      const projId = currentPlan ? currentPlan.project_id : '';
      const modal = document.getElementById('seo-tags-modal');
      const listEl = document.getElementById('seo-tags-content');
      listEl.innerHTML = '<div style="color:var(--text-muted); text-align:center; padding:20px;">Carregando tags e hashtags otimizadas...</div>';
      modal.style.display = 'flex';

      try {
        const url = `/api/seo/generate?project_id=${encodeURIComponent(projId)}&topic=${encodeURIComponent(topic)}`;
        const res = await fetch(url);
        const data = await res.json();
        if (!data.ok) throw new Error(data.error || 'Erro ao gerar tags');
        const r = data.result;

        listEl.innerHTML = `
          <div style="background:#1e293b; border-left:4px solid #38bdf8; padding:12px; border-radius:6px;">
            <div style="font-weight:700; color:#38bdf8; font-size:0.95rem;">🎯 Otimização de Busca YouTube Studio (Limite: 500 chars)</div>
            <div style="font-size:0.8rem; color:#cbd5e1; margin-top:4px;">Copie a string exata para colar direto na caixa de tags do YouTube Studio:</div>
            <div style="position:relative; margin-top:8px;">
              <textarea id="yt-studio-tags-area" readonly style="width:100%; height:90px; background:#0f172a; border:1px solid #334155; color:#f8fafc; font-family:monospace; font-size:0.82rem; padding:8px; border-radius:4px;">${r.youtube_studio_tags_string}</textarea>
              <div style="display:flex; justify-content:space-between; align-items:center; margin-top:6px;">
                <span style="font-size:0.75rem; color:${r.char_count <= 500 ? '#10b981' : '#ef4444'}; font-weight:700;">${r.char_count}/500 caracteres</span>
                <button class="btn btn-secondary" style="font-size:0.78rem;" onclick="copiarYtTags()">📋 Copiar Tags para YouTube Studio</button>
              </div>
            </div>
          </div>

          <div style="background:var(--card-bg); border:1px solid var(--border); padding:12px; border-radius:6px;">
            <div style="font-weight:700; color:#a7f3d0; font-size:0.85rem; margin-bottom:6px;">#️⃣ Hashtags Virais Recomendadas:</div>
            <div style="display:flex; flex-wrap:wrap; gap:6px;">
              ${r.hashtags.map(h => `<span style="background:#064e3b; color:#6ee7b7; padding:3px 8px; border-radius:12px; font-size:0.78rem; font-weight:600;">${h}</span>`).join('')}
            </div>
          </div>

          <div style="background:var(--card-bg); border:1px solid var(--border); padding:12px; border-radius:6px;">
            <div style="font-weight:700; color:#c084fc; font-size:0.85rem; margin-bottom:6px;">🔍 Palavras-chave de Cauda Longa:</div>
            <div style="display:flex; flex-wrap:wrap; gap:6px;">
              ${r.long_tail_keywords.map(k => `<span style="background:#3b0764; color:#d8b4fe; padding:3px 8px; border-radius:4px; font-size:0.75rem;">${k}</span>`).join('')}
            </div>
          </div>
        `;
      } catch (e) {
        listEl.innerHTML = `<div style="color:#ef4444; padding:10px;">Falha ao gerar tags: ${e.message}</div>`;
      }
    }
    function fecharSeoTags() {
      document.getElementById('seo-tags-modal').style.display = 'none';
    }
    function copiarYtTags() {
      const el = document.getElementById('yt-studio-tags-area');
      if (el) {
        el.select();
        document.execCommand('copy');
        alert('Tags copiadas para a área de transferência!');
      }
    }

    async function abrirKenBurnsDirector() {
      if (!currentPlan) return alert('Analise ou carregue um roteiro primeiro!');
      const modal = document.getElementById('ken-burns-director-modal');
      const contentEl = document.getElementById('ken-burns-director-content');
      contentEl.innerHTML = '<div style="color:var(--text-muted); text-align:center; padding:20px;">Calculando vetores de câmera cinematográfica por cena...</div>';
      modal.style.display = 'flex';

      try {
        const res = await fetch(`/api/camera/plan?project_id=${encodeURIComponent(currentPlan.project_id)}`);
        const data = await res.json();
        if (!data.ok) throw new Error(data.error || 'Erro ao planejar movimentos de câmera');
        const plan = data.plan;

        contentEl.innerHTML = `
          <div style="background:#2e1065; border-left:4px solid #a855f7; padding:12px; border-radius:6px;">
            <div style="font-weight:700; color:#d8b4fe; font-size:0.95rem;">🎥 Direção Automática de Câmera Ken Burns</div>
            <div style="font-size:0.8rem; color:#e9d5ff; margin-top:2px;">
              Total de Cenas: <b>${plan.total_scenes}</b> | Movimentos Calculados: <b>${plan.distribution ? Object.entries(plan.distribution).map(([k,v]) => `${k}: ${v}`).join(' | ') : 'Cinematográfico'}</b>
            </div>
          </div>
          <div style="display:flex; flex-direction:column; gap:8px; max-height:400px; overflow-y:auto; margin-top:8px;">
            ${(plan.scenes || []).map(s => `
              <div style="background:var(--card-bg); border:1px solid var(--border); padding:10px; border-radius:6px; font-size:0.82rem;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                  <b style="color:#fff;">Cena #${s.scene_order}: ${s.camera_movement}</b>
                  <span style="background:#581c87; color:#f3e8ff; padding:2px 8px; border-radius:4px; font-weight:700; font-size:0.75rem;">Zoom: ${s.zoom_start.toFixed(2)}x ➔ ${s.zoom_end.toFixed(2)}x</span>
                </div>
                <div style="color:var(--text-muted); font-size:0.75rem; margin-top:4px;">${s.narration_snippet || ''}</div>
                <div style="margin-top:6px; background:#0f172a; padding:6px; border-radius:4px; font-family:monospace; font-size:0.72rem; color:#38bdf8; word-break:break-all;">
                  ${s.ffmpeg_zoompan_expr}
                </div>
              </div>
            `).join('')}
          </div>
        `;
      } catch (e) {
        contentEl.innerHTML = `<div style="color:#ef4444; padding:10px;">Falha: ${e.message}</div>`;
      }
    }
    function fecharKenBurnsDirector() {
      document.getElementById('ken-burns-director-modal').style.display = 'none';
    }

    function abrirBrandingModal() {
      document.getElementById('branding-modal').style.display = 'flex';
    }
    function fecharBrandingModal() {
      document.getElementById('branding-modal').style.display = 'none';
    }
    async function salvarBrandingConfig() {
      if (!currentPlan) return alert('Analise ou carregue um roteiro primeiro!');
      const watermark_path = document.getElementById('branding-logo-path').value.trim();
      const position = document.getElementById('branding-pos').value;
      const opacity = parseFloat(document.getElementById('branding-opacity').value) || 0.85;
      const scale_pct = parseFloat(document.getElementById('branding-scale').value) || 15.0;
      const enable_intro_lower_third = document.getElementById('branding-lower-third-check').checked;
      const channel_name = document.getElementById('branding-channel-name').value.trim();
      const channel_handle = document.getElementById('branding-channel-handle').value.trim();

      showStatus('Aplicando marca d\'água e branding visual...', '#ec4899');
      try {
        const res = await fetch('/api/branding/apply', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            project_id: currentPlan.project_id,
            watermark_path,
            position,
            opacity,
            scale_pct,
            enable_intro_lower_third,
            channel_name,
            channel_handle
          })
        });
        const data = await res.json();
        if (data.ok) {
          showStatus('Branding e Marca D\'água salvos no projeto!', '#10b981');
          alert('Configuração de marca d\'água e lower-third intro salva com sucesso!');
          fecharBrandingModal();
        } else {
          alert('Erro: ' + (data.error || 'Falha ao salvar branding'));
        }
      } catch (e) {
        alert('Erro ao salvar branding: ' + e.message);
      }
    }

    async function abrirTemplatesModal() {
      const modal = document.getElementById('templates-modal');
      const grid = document.getElementById('templates-cards-grid');
      grid.innerHTML = '<div style="color:var(--text-muted); text-align:center; padding:20px;">Carregando templates de canal...</div>';
      modal.style.display = 'flex';

      try {
        const res = await fetch('/api/templates/list');
        const data = await res.json();
        if (!data.ok) throw new Error(data.error || 'Erro ao listar templates');

        grid.innerHTML = (data.templates || []).map(t => `
          <div style="background:var(--card-bg); border:1px solid var(--border); border-radius:8px; padding:16px; display:flex; flex-direction:column; justify-content:space-between; gap:10px;">
            <div>
              <div style="display:flex; justify-content:space-between; align-items:center;">
                <h4 style="color:#fff; font-size:1.05rem;">${t.name}</h4>
                <span style="background:#7c3aed; color:#fff; font-size:0.75rem; padding:2px 8px; border-radius:4px; font-weight:700;">${t.aspect_ratio}</span>
              </div>
              <p style="color:var(--text-muted); font-size:0.8rem; margin-top:6px;">${t.description}</p>
              <div style="margin-top:10px; font-size:0.75rem; display:flex; flex-direction:column; gap:4px; color:#cbd5e1;">
                <div>🎨 <b>Estilo de Cor:</b> ${t.color_grade}</div>
                <div>🔤 <b>Tipografia:</b> ${t.subtitle_font} (${t.subtitle_color})</div>
                <div>🎵 <b>Gênero Musical:</b> ${t.bgm_genre} (Volume: ${Math.round(t.bgm_volume * 100)}%)</div>
                <div>📹 <b>Câmera:</b> ${t.camera_style} | Transições: ${t.transition_type}</div>
              </div>
            </div>
            <button class="btn" style="background:#7c3aed; color:#fff; font-weight:700; width:100%; margin-top:10px;" onclick="aplicarTemplateCanal('${t.id}')">
              ⚡ Aplicar Este Template
            </button>
          </div>
        `).join('');
      } catch (e) {
        grid.innerHTML = `<div style="color:#ef4444; padding:10px;">Falha ao carregar templates: ${e.message}</div>`;
      }
    }
    function fecharTemplatesModal() {
      document.getElementById('templates-modal').style.display = 'none';
    }
    async function aplicarTemplateCanal(templateId) {
      if (!currentPlan) return alert('Analise ou carregue um roteiro primeiro!');
      showStatus(`Aplicando template ${templateId} ao projeto...`, '#7c3aed');
      try {
        const res = await fetch('/api/templates/apply', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ project_id: currentPlan.project_id, template_id: templateId })
        });
        const data = await res.json();
        if (data.ok) {
          showStatus(`Template ${templateId} aplicado com sucesso!`, '#10b981');
          alert(`Template "${templateId}" aplicado ao projeto!\n\nProporção: ${data.config.aspect_ratio}\nCores, legendas, trilha e Ken Burns padronizados para este canal.`);
          fecharTemplatesModal();
        } else {
          alert('Erro: ' + (data.error || 'Falha ao aplicar template'));
        }
      } catch (e) {
        alert('Erro ao aplicar template: ' + e.message);
      }
    }

    // === MASTER STUDIO: DUCKING PUNCH, RETENTION HEATMAP, COLOR MATCHER, MULTI-EXPORT ===
    async function abrirDuckingPunchModal() {
      if (!currentPlan) return alert('Analise ou carregue um roteiro primeiro!');
      const modal = document.getElementById('ducking-punch-modal');
      const contentEl = document.getElementById('ducking-punch-content');
      contentEl.innerHTML = '<div style="color:var(--text-muted); text-align:center; padding:20px;">Analisando curva vocal e calculando sidechain ducking...</div>';
      modal.style.display = 'flex';

      try {
        const res = await fetch(`/api/ducking/plan?project_id=${encodeURIComponent(currentPlan.project_id)}`);
        const data = await res.json();
        if (!data.ok) throw new Error(data.error || 'Erro ao gerar plano de punch-in');
        const d = data.plan;

        contentEl.innerHTML = `
          <div style="background:#451a03; border-left:4px solid #f59e0b; padding:12px; border-radius:6px;">
            <div style="font-weight:700; color:#fde68a; font-size:0.95rem;">🎙️ Sidechain Ducking Dinâmico & Micro Punch-Ins</div>
            <div style="font-size:0.8rem; color:#fef3c7; margin-top:2px;">
              Trilha BGM atenuada em -14dB durante fala | <b>${d.total_punch_triggers}</b> palavras-chave de ênfase vocal detectadas.
            </div>
          </div>
          <div style="background:var(--card-bg); border:1px solid var(--border); padding:10px; border-radius:6px; margin-top:8px;">
            <b style="color:#93c5fd; font-size:0.85rem;">Filtro de Ducking FFmpeg (Automático):</b>
            <div style="font-family:monospace; font-size:0.75rem; color:#10b981; background:#0f172a; padding:6px; border-radius:4px; margin-top:4px; word-break:break-all;">
              ${d.sidechain_ducking_filter}
            </div>
          </div>
          <div style="margin-top:8px;">
            <b style="color:#fff; font-size:0.85rem;">Gatilhos de Punch-In Detectados:</b>
            <div style="display:flex; flex-direction:column; gap:6px; max-height:240px; overflow-y:auto; margin-top:6px;">
              ${(d.triggers || []).map(t => `
                <div style="background:var(--card-bg); border:1px solid var(--border); padding:8px; border-radius:4px; display:flex; justify-content:space-between; align-items:center; font-size:0.8rem;">
                  <div>
                    <span style="background:#78350f; color:#fef3c7; font-weight:700; padding:2px 6px; border-radius:4px;">Cena #${t.scene_order}</span>
                    <b style="color:#f59e0b; margin-left:6px;">"${t.trigger_word}"</b>
                    <span style="color:var(--text-muted); font-size:0.75rem; margin-left:6px;">às ${t.timestamp_offset_sec}s</span>
                  </div>
                  <span style="background:#1e3a8a; color:#bfdbfe; font-size:0.72rem; padding:2px 6px; border-radius:4px; font-weight:700;">Zoom: ${t.zoom_level}x (${t.duration_sec}s)</span>
                </div>
              `).join('')}
            </div>
          </div>
        `;
      } catch (e) {
        contentEl.innerHTML = `<div style="color:#ef4444; padding:10px;">Falha: ${e.message}</div>`;
      }
    }
    function fecharDuckingPunchModal() {
      document.getElementById('ducking-punch-modal').style.display = 'none';
    }

    async function abrirRetentionModal() {
      if (!currentPlan) return alert('Analise ou carregue um roteiro primeiro!');
      const modal = document.getElementById('retention-modal');
      const contentEl = document.getElementById('retention-content');
      contentEl.innerHTML = '<div style="color:var(--text-muted); text-align:center; padding:20px;">Auditando curva de retenção do YouTube...</div>';
      modal.style.display = 'flex';

      try {
        const res = await fetch(`/api/retention/audit?project_id=${encodeURIComponent(currentPlan.project_id)}`);
        const data = await res.json();
        if (!data.ok) throw new Error(data.error || 'Erro na auditoria de retenção');
        const r = data.result;

        const gradeColor = r.overall_pacing_grade === 'A+' ? '#10b981' : (r.overall_pacing_grade === 'B' ? '#f59e0b' : '#ef4444');

        contentEl.innerHTML = `
          <div style="background:#064e3b; border-left:4px solid #10b981; padding:12px; border-radius:6px; display:flex; justify-content:space-between; align-items:center;">
            <div>
              <div style="font-weight:700; color:#a7f3d0; font-size:0.95rem;">📊 Curva Preditiva de Retenção & Atenção Visual</div>
              <div style="font-size:0.8rem; color:#d1fae5; margin-top:2px;">
                Duração: <b>${r.total_timeline_duration_sec}s</b> | Retenção Média Prevista: <b>${r.average_predicted_retention_pct}%</b>
              </div>
            </div>
            <div style="text-align:center; background:#022c22; padding:6px 14px; border-radius:8px;">
              <div style="font-size:0.7rem; color:#a7f3d0;">Nota de Ritmo:</div>
              <b style="font-size:1.4rem; color:${gradeColor};">${r.overall_pacing_grade}</b>
            </div>
          </div>
          <div style="margin-top:10px;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
              <b style="color:#fff; font-size:0.85rem;">Zonas de Risco de Queda de Audiência (${r.total_risk_zones_found}):</b>
              ${r.total_risk_zones_found > 0 ? `<button class="btn btn-secondary" style="font-size:0.75rem; border-color:#10b981; color:#a7f3d0;" onclick="remediarRetencaoAuto()">⚡ Auto-Corrigir Zonas Mortas (1-Clique)</button>` : ''}
            </div>
            <div style="display:flex; flex-direction:column; gap:6px; max-height:220px; overflow-y:auto; margin-top:8px;">
              ${r.total_risk_zones_found === 0 ? '<div style="color:#10b981; font-size:0.82rem; padding:10px;">✅ Nenhuma zona morta detectada! Ritmo cinematográfico perfeito.</div>' : ''}
              ${(r.risk_zones || []).map(z => `
                <div style="background:var(--card-bg); border:1px solid #374151; padding:8px 10px; border-radius:6px; font-size:0.8rem;">
                  <div style="display:flex; justify-content:space-between;">
                    <span style="font-weight:700; color:#f87171;">Cena #${z.scene_order} (${z.start_sec}s - ${z.end_sec}s)</span>
                    <span style="background:#7f1d1d; color:#fecaca; font-weight:700; font-size:0.7rem; padding:2px 6px; border-radius:4px;">Risco ${z.risk_level}</span>
                  </div>
                  <div style="color:var(--text-muted); font-size:0.75rem; margin-top:3px;">${z.reason}</div>
                  <div style="color:#6ee7b7; font-size:0.72rem; margin-top:3px;">💡 Sugestão: ${z.remediation_suggestion}</div>
                </div>
              `).join('')}
            </div>
          </div>
        `;
      } catch (e) {
        contentEl.innerHTML = `<div style="color:#ef4444; padding:10px;">Falha: ${e.message}</div>`;
      }
    }
    function fecharRetentionModal() {
      document.getElementById('retention-modal').style.display = 'none';
    }
    async function remediarRetencaoAuto() {
      if (!currentPlan) return;
      showStatus('Auto-corrigindo zonas de risco de atenção...', '#10b981');
      try {
        const res = await fetch('/api/retention/remediate', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ project_id: currentPlan.project_id })
        });
        const data = await res.json();
        if (data.ok) {
          showStatus(`Zonas mortas corrigidas: ${data.remediated_scenes_count} cenas otimizadas!`, '#10b981');
          alert(`Sucesso!\n\n${data.remediated_scenes_count} cenas foram aceleradas com cortes dinâmicos de punch-in e transições orgânicas.`);
          abrirRetentionModal();
        }
      } catch (e) {
        alert('Erro ao remediar: ' + e.message);
      }
    }

    async function abrirColorMatcherModal() {
      if (!currentPlan) return alert('Analise ou carregue um roteiro primeiro!');
      const modal = document.getElementById('color-matcher-modal');
      const contentEl = document.getElementById('color-matcher-content');
      contentEl.innerHTML = '<div style="color:var(--text-muted); text-align:center; padding:20px;">Harmonizando temperatura de cores para 5600K Daylight...</div>';
      modal.style.display = 'flex';

      try {
        const res = await fetch(`/api/color/harmonize?project_id=${encodeURIComponent(currentPlan.project_id)}`);
        const data = await res.json();
        if (!data.ok) throw new Error(data.error || 'Erro ao harmonizar cores');
        const c = data.result;

        contentEl.innerHTML = `
          <div style="background:#083344; border-left:4px solid #06b6d4; padding:12px; border-radius:6px;">
            <div style="font-weight:700; color:#a5f3fc; font-size:0.95rem;">🎨 Color Matcher de Acervos Heterogêneos (Padrão 5600K)</div>
            <div style="font-size:0.8rem; color:#cffafe; margin-top:2px;">
              Alinhamento cromático unificado: <b>${c.target_aesthetic}</b> em <b>${c.total_scenes_harmonized}</b> cenas.
            </div>
          </div>
          <div style="display:flex; flex-direction:column; gap:8px; max-height:360px; overflow-y:auto; margin-top:8px;">
            ${(c.recipes || []).map(r => `
              <div style="background:var(--card-bg); border:1px solid var(--border); padding:10px; border-radius:6px; font-size:0.82rem;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                  <b style="color:#fff;">Cena #${r.scene_order} (Viés: ${r.detected_color_bias})</b>
                  <span style="background:#155e75; color:#cffafe; font-size:0.72rem; padding:2px 6px; border-radius:4px; font-weight:700;">${r.target_temperature}</span>
                </div>
                <div style="color:#94a3b8; font-size:0.75rem; margin-top:3px;">${r.explanation}</div>
                <div style="font-family:monospace; font-size:0.72rem; color:#38bdf8; background:#0f172a; padding:4px 6px; border-radius:4px; margin-top:4px;">
                  ${r.ffmpeg_filter}
                </div>
              </div>
            `).join('')}
          </div>
        `;
      } catch (e) {
        contentEl.innerHTML = `<div style="color:#ef4444; padding:10px;">Falha: ${e.message}</div>`;
      }
    }
    function fecharColorMatcherModal() {
      document.getElementById('color-matcher-modal').style.display = 'none';
    }

    async function abrirMultiExportModal() {
      if (!currentPlan) return alert('Analise ou carregue um roteiro primeiro!');
      const modal = document.getElementById('multiexport-modal');
      const listEl = document.getElementById('multiexport-presets-list');
      listEl.innerHTML = '<div style="color:var(--text-muted); text-align:center; padding:20px;">Carregando formatos de renderização...</div>';
      modal.style.display = 'flex';

      try {
        const res = await fetch('/api/multiexport/presets');
        const data = await res.json();
        if (!data.ok) throw new Error(data.error || 'Erro ao listar presets');

        listEl.innerHTML = (data.presets || []).map(p => `
          <div style="background:var(--card-bg); border:1px solid var(--border); padding:12px; border-radius:6px; display:flex; justify-content:space-between; align-items:center;">
            <div>
              <div style="display:flex; align-items:center; gap:8px;">
                <input type="checkbox" id="chk-export-${p.preset_id}" checked style="width:16px; height:16px;">
                <b style="color:#fff; font-size:0.95rem;">${p.name}</b>
                <span style="background:#1e3a8a; color:#bfdbfe; font-size:0.72rem; padding:2px 6px; border-radius:4px; font-weight:700;">${p.aspect_ratio}</span>
              </div>
              <div style="color:var(--text-muted); font-size:0.8rem; margin-top:4px; margin-left:24px;">${p.recommended_use}</div>
            </div>
            <span style="font-size:0.75rem; color:#10b981; font-weight:700;">${p.audio_lufs} LUFS</span>
          </div>
        `).join('');
      } catch (e) {
        listEl.innerHTML = `<div style="color:#ef4444; padding:10px;">Falha: ${e.message}</div>`;
      }
    }
    function fecharMultiExportModal() {
      document.getElementById('multiexport-modal').style.display = 'none';
    }
    async function executarMultiExport() {
      if (!currentPlan) return;
      const checkboxes = document.querySelectorAll('[id^="chk-export-"]');
      const selected = [];
      checkboxes.forEach(c => {
        if (c.checked) selected.push(c.id.replace('chk-export-', ''));
      });
      if (!selected.length) return alert('Selecione pelo menos uma plataforma para exportar!');

      showStatus('Orquestrando exportações multiplataforma...', '#2563eb');
      try {
        const res = await fetch('/api/multiexport/render', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ project_id: currentPlan.project_id, presets: selected })
        });
        const data = await res.json();
        if (data.ok) {
          showStatus(`Manifesto de renderização gerado com ${data.manifest.total_exports_planned} formatos!`, '#10b981');
          alert(`Orquestração de Multi-Export pronta!\n\n${data.manifest.total_exports_planned} arquivos agendados:\n` + data.manifest.export_tasks.map(t => `• ${t.name} -> ${t.output_file}`).join('\n'));
          fecharMultiExportModal();
        } else {
          alert('Erro: ' + (data.error || 'Falha na exportação'));
        }
      } catch (e) {
        alert('Erro ao exportar: ' + e.message);
      }
    }

    // === TITAN STUDIO: HOOK A/B TESTER, BEAT DROP SYNC, VOICE EMOTIONS, CHAPTER CARDS ===
    async function abrirHookTesterModal() {
      if (!currentPlan) return alert('Analise ou carregue um roteiro primeiro!');
      const modal = document.getElementById('hook-tester-modal');
      const listEl = document.getElementById('hook-tester-list');
      listEl.innerHTML = '<div style="color:var(--text-muted); text-align:center; padding:20px;">Formulando 3 variações psicológicas de gancho inicial...</div>';
      modal.style.display = 'flex';

      try {
        const res = await fetch(`/api/hooks/variations?project_id=${encodeURIComponent(currentPlan.project_id)}`);
        const data = await res.json();
        if (!data.ok) throw new Error(data.error || 'Erro ao gerar ganchos');

        listEl.innerHTML = (data.variations || []).map(v => `
          <div style="background:var(--card-bg); border:1px solid var(--border); border-radius:8px; padding:14px; display:flex; flex-direction:column; gap:8px;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
              <b style="color:#f5d0fe; font-size:0.95rem;">${v.title}</b>
              <span style="background:#86198f; color:#fdf4ff; padding:2px 8px; border-radius:4px; font-weight:700; font-size:0.75rem;">Impacto: ${v.estimated_hook_power}/100</span>
            </div>
            <div style="background:#18181b; padding:10px; border-left:3px solid #d946ef; border-radius:4px; font-size:0.85rem; color:#fff;">
              "${v.narration_text}"
            </div>
            <div style="display:flex; justify-content:space-between; align-items:center; font-size:0.75rem; color:var(--text-muted); margin-top:2px;">
              <span>🎭 <b>Emoção Alvo:</b> ${v.target_emotion}</span>
              <button class="btn" style="background:#d946ef; color:#fff; font-size:0.78rem; font-weight:700;" onclick="aplicarGanchoAberto('${v.hook_id}')">⚡ Usar Este Gancho no Início</button>
            </div>
          </div>
        `).join('');
      } catch (e) {
        listEl.innerHTML = `<div style="color:#ef4444; padding:10px;">Falha: ${e.message}</div>`;
      }
    }
    function fecharHookTesterModal() {
      document.getElementById('hook-tester-modal').style.display = 'none';
    }
    async function aplicarGanchoAberto(hookId) {
      if (!currentPlan) return;
      showStatus('Aplicando gancho de abertura...', '#d946ef');
      try {
        const res = await fetch('/api/hooks/apply', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ project_id: currentPlan.project_id, hook_id: hookId })
        });
        const data = await res.json();
        if (data.ok) {
          showStatus('Gancho aplicado com sucesso à Cena #1!', '#10b981');
          alert('Gancho aplicado com sucesso!\n\nA Cena #1 foi reconfigurada para prender a atenção nos primeiros 5 segundos.');
          fecharHookTesterModal();
        } else {
          alert('Erro: ' + data.error);
        }
      } catch (e) {
        alert('Erro ao aplicar gancho: ' + e.message);
      }
    }

    async function abrirBeatSyncModal() {
      if (!currentPlan) return alert('Analise ou carregue um roteiro primeiro!');
      const modal = document.getElementById('beat-sync-modal');
      const contentEl = document.getElementById('beat-sync-content');
      contentEl.innerHTML = '<div style="color:var(--text-muted); text-align:center; padding:20px;">Calculando compassos e quantização rítmica...</div>';
      modal.style.display = 'flex';

      try {
        const bpm = 90.0;
        const res = await fetch(`/api/beat/sync?project_id=${encodeURIComponent(currentPlan.project_id)}&bpm=${bpm}`);
        const data = await res.json();
        if (!data.ok) throw new Error(data.error || 'Erro no sync de beat');
        const s = data.result;

        contentEl.innerHTML = `
          <div style="background:#451a03; border-left:4px solid #f59e0b; padding:12px; border-radius:6px; display:flex; justify-content:space-between; align-items:center;">
            <div>
              <div style="font-weight:700; color:#fde68a; font-size:0.95rem;">🎵 Sincronizador de Beat Musical (Trailer Cut)</div>
              <div style="font-size:0.8rem; color:#fef3c7; margin-top:2px;">
                Tempo: <b>${s.tempo_bpm} BPM</b> | Intervalo de Batida: <b>${s.beat_duration_sec}s</b> | Cortes Quantizados: <b>${s.total_cuts_quantized}</b>
              </div>
            </div>
            <button class="btn" style="background:#f59e0b; color:#000; font-weight:800; font-size:0.8rem;" onclick="aplicarBeatSync(${s.tempo_bpm})">⚡ Alinhar Timeline Agora</button>
          </div>
          <div style="display:flex; flex-direction:column; gap:6px; max-height:300px; overflow-y:auto; margin-top:8px;">
            ${(s.cut_points || []).map(c => `
              <div style="background:var(--card-bg); border:1px solid var(--border); padding:8px 10px; border-radius:4px; display:flex; justify-content:space-between; align-items:center; font-size:0.8rem;">
                <b style="color:#fff;">Cena #${c.scene_order}</b>
                <span style="color:var(--text-muted);">Duração: ${c.original_duration.toFixed(2)}s ➔ <b style="color:#10b981;">${c.quantized_duration.toFixed(2)}s</b></span>
                <span style="background:#1e3a8a; color:#bfdbfe; font-size:0.72rem; padding:2px 6px; border-radius:4px;">${c.target_musical_bar} compassos (Shift: ${c.time_shift_ms}ms)</span>
              </div>
            `).join('')}
          </div>
        `;
      } catch (e) {
        contentEl.innerHTML = `<div style="color:#ef4444; padding:10px;">Falha: ${e.message}</div>`;
      }
    }
    function fecharBeatSyncModal() {
      document.getElementById('beat-sync-modal').style.display = 'none';
    }
    async function aplicarBeatSync(bpm) {
      if (!currentPlan) return;
      showStatus('Quantizando cortes da timeline nos tempos musicais...', '#f59e0b');
      try {
        const res = await fetch('/api/beat/apply', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ project_id: currentPlan.project_id, bpm })
        });
        const data = await res.json();
        if (data.ok) {
          showStatus('Timeline sincronizada no ritmo exato do beat!', '#10b981');
          alert('Sucesso!\n\nAs durações das cenas foram matematicamente arredondadas para os tempos e compassos da música.');
          fecharBeatSyncModal();
        }
      } catch (e) {
        alert('Erro ao aplicar sync: ' + e.message);
      }
    }

    async function abrirVoiceEmotionModal() {
      if (!currentPlan) return alert('Analise ou carregue um roteiro primeiro!');
      const modal = document.getElementById('voice-emotion-modal');
      const listEl = document.getElementById('voice-emotion-list');
      listEl.innerHTML = '<div style="color:var(--text-muted); text-align:center; padding:20px;">Mapeando curvas de prosódia e dinâmica vocal...</div>';
      modal.style.display = 'flex';

      try {
        const res = await fetch(`/api/voice/emotions?project_id=${encodeURIComponent(currentPlan.project_id)}`);
        const data = await res.json();
        if (!data.ok) throw new Error(data.error || 'Erro nas inflexões de voz');
        const v = data.result;

        listEl.innerHTML = `
          <div style="background:#2e1065; border-left:4px solid #8b5cf6; padding:12px; border-radius:6px;">
            <div style="font-weight:700; color:#ddd6fe; font-size:0.95rem;">🎭 Diretor Neural de Inflexão Emocional da Voz</div>
            <div style="font-size:0.8rem; color:#ede9fe; margin-top:2px;">
              Prosódia SSML contextual por cena: velocidade, tom (pitch) e pausas respiratórias dinâmicas em <b>${v.total_scenes_directed}</b> cenas.
            </div>
          </div>
          <div style="display:flex; flex-direction:column; gap:6px; max-height:360px; overflow-y:auto; margin-top:8px;">
            ${(v.inflections || []).map(i => `
              <div style="background:var(--card-bg); border:1px solid var(--border); padding:10px; border-radius:6px; font-size:0.82rem;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                  <b style="color:#fff;">Cena #${i.scene_order}: <span style="color:#c084fc;">${i.narrative_mood}</span></b>
                  <span style="background:#581c87; color:#f3e8ff; font-size:0.72rem; padding:2px 6px; border-radius:4px; font-weight:700;">Speed: ${i.speed_factor}x | Pitch: ${i.pitch_adjustment_hz}</span>
                </div>
                <div style="font-family:monospace; font-size:0.72rem; color:#a7f3d0; background:#0f172a; padding:6px; border-radius:4px; margin-top:4px; word-break:break-all;">
                  ${i.ssml_prosody_snippet}
                </div>
              </div>
            `).join('')}
          </div>
        `;
      } catch (e) {
        listEl.innerHTML = `<div style="color:#ef4444; padding:10px;">Falha: ${e.message}</div>`;
      }
    }
    function fecharVoiceEmotionModal() {
      document.getElementById('voice-emotion-modal').style.display = 'none';
    }

    async function abrirChapterCardsModal() {
      if (!currentPlan) return alert('Analise ou carregue um roteiro primeiro!');
      const modal = document.getElementById('chapter-cards-modal');
      const listEl = document.getElementById('chapter-cards-list');
      listEl.innerHTML = '<div style="color:var(--text-muted); text-align:center; padding:20px;">Gerando cartelas cinematográficas de capítulos...</div>';
      modal.style.display = 'flex';

      try {
        const res = await fetch(`/api/chapters/cards?project_id=${encodeURIComponent(currentPlan.project_id)}`);
        const data = await res.json();
        if (!data.ok) throw new Error(data.error || 'Erro nas cartelas de capítulos');
        const c = data.result;

        listEl.innerHTML = `
          <div style="background:#064e3b; border-left:4px solid #059669; padding:12px; border-radius:6px;">
            <div style="font-weight:700; color:#a7f3d0; font-size:0.95rem;">🎬 Cartelas de Transição de Capítulos (Title Sequences)</div>
            <div style="font-size:0.8rem; color:#d1fae5; margin-top:2px;">
              Numeração em algarismos romanos, tipografia dourada e efeito sonoro de impacto foley embutido.
            </div>
          </div>
          <div style="display:flex; flex-direction:column; gap:8px; max-height:360px; overflow-y:auto; margin-top:8px;">
            ${(c.cards || []).map(card => `
              <div style="background:var(--card-bg); border:1px solid var(--border); padding:12px; border-radius:6px; display:flex; justify-content:space-between; align-items:center;">
                <div>
                  <div style="font-size:0.75rem; color:#fbbf24; font-weight:700;">CAPÍTULO ${card.roman_numeral}</div>
                  <b style="color:#fff; font-size:0.95rem; margin-top:2px; display:block;">${card.chapter_title}</b>
                  <div style="font-size:0.72rem; color:var(--text-muted); margin-top:4px;">Duração: ${card.card_duration_sec}s | Áudio: ${card.foley_sound_effect}</div>
                </div>
                <span style="background:#065f46; color:#a7f3d0; font-size:0.75rem; padding:4px 8px; border-radius:4px; font-weight:700;">Pronto para Render</span>
              </div>
            `).join('')}
          </div>
        `;
      } catch (e) {
        listEl.innerHTML = `<div style="color:#ef4444; padding:10px;">Falha: ${e.message}</div>`;
      }
    }
    function fecharChapterCardsModal() {
      document.getElementById('chapter-cards-modal').style.display = 'none';
    }

    // === APEX STUDIO: QUAD-THUMBNAILS, GPU TUNER, RETENTION PACER, COMMUNITY KIT ===
    async function abrirQuadThumbnailsModal() {
      if (!currentPlan) return alert('Analise ou carregue um roteiro primeiro!');
      const modal = document.getElementById('quad-thumbnails-modal');
      const grid = document.getElementById('quad-thumbnails-grid');
      grid.innerHTML = '<div style="color:var(--text-muted); text-align:center; padding:20px;">Gerando suite quad de thumbnails para Test & Compare do YouTube...</div>';
      modal.style.display = 'flex';

      try {
        const res = await fetch(`/api/thumbnails/quad?project_id=${encodeURIComponent(currentPlan.project_id)}`);
        const data = await res.json();
        if (!data.ok) throw new Error(data.error || 'Erro nas thumbnails');
        const q = data.suite;

        grid.innerHTML = (q.variants || []).map(v => `
          <div style="background:var(--card-bg); border:1px solid var(--border); border-radius:8px; padding:12px; display:flex; flex-direction:column; justify-content:space-between; gap:8px;">
            <div>
              <div style="display:flex; justify-content:space-between; align-items:center;">
                <b style="color:#fecdd3; font-size:0.9rem;">${v.name}</b>
                <span style="background:#881337; color:#ffe4e6; font-size:0.75rem; padding:2px 6px; border-radius:4px; font-weight:700;">+${v.estimated_ctr_boost_pct}% CTR</span>
              </div>
              <div style="background:#0f172a; border-radius:6px; padding:16px 12px; text-align:center; margin-top:8px; border:1px solid #334155;">
                <span style="font-size:1.1rem; font-weight:900; color:#fbbf24; text-shadow:2px 2px 0 #000;">${v.headline_text}</span>
              </div>
              <div style="font-size:0.75rem; color:#94a3b8; margin-top:6px;">🎯 Foco: ${v.foveal_focus_zone}</div>
            </div>
            <div style="font-family:monospace; font-size:0.7rem; color:#38bdf8; background:#1e293b; padding:4px 6px; border-radius:4px; word-break:break-all;">
              ${v.overlay_filter}
            </div>
          </div>
        `).join('');
      } catch (e) {
        grid.innerHTML = `<div style="color:#ef4444; padding:10px;">Falha: ${e.message}</div>`;
      }
    }
    function fecharQuadThumbnailsModal() {
      document.getElementById('quad-thumbnails-modal').style.display = 'none';
    }

    async function abrirHardwareTunerModal() {
      const modal = document.getElementById('hardware-tuner-modal');
      const contentEl = document.getElementById('hardware-tuner-content');
      contentEl.innerHTML = '<div style="color:var(--text-muted); text-align:center; padding:20px;">Sondando aceleração de hardware GPU/CPU...</div>';
      modal.style.display = 'flex';

      try {
        const res = await fetch('/api/hardware/profile');
        const data = await res.json();
        if (!data.ok) throw new Error(data.error || 'Erro no profiler');
        const p = data.profile;

        contentEl.innerHTML = `
          <div style="background:#422006; border-left:4px solid #eab308; padding:12px; border-radius:6px;">
            <div style="font-weight:700; color:#fef08a; font-size:0.95rem;">⚡ Perfil Ativo: ${p.hardware_acceleration_name}</div>
            <div style="font-size:0.8rem; color:#fef9c3; margin-top:2px;">
              Plataforma: <b>${p.platform_system}</b> | Encoder Otimizado: <b>${p.recommended_encoder}</b> | Threads: <b>${p.cpu_thread_allocation}</b>
            </div>
          </div>
          <div style="background:var(--card-bg); border:1px solid var(--border); padding:12px; border-radius:6px; display:flex; flex-direction:column; gap:8px; margin-top:8px;">
            <b style="color:#93c5fd; font-size:0.85rem;">Parâmetros de Linha de Comando FFmpeg Calculados:</b>
            <div style="font-family:monospace; font-size:0.78rem; color:#10b981; background:#0f172a; padding:8px; border-radius:4px; word-break:break-all;">
              ${p.ffmpeg_video_flags}
            </div>
            <div style="font-size:0.75rem; color:var(--text-muted);">
              🛡️ Modo Anti-Congelamento ativo: memória buffer limitada a ${p.memory_limit_mb}MB com liberação automática de páginas sujas.
            </div>
          </div>
        `;
      } catch (e) {
        contentEl.innerHTML = `<div style="color:#ef4444; padding:10px;">Falha: ${e.message}</div>`;
      }
    }
    function fecharHardwareTunerModal() {
      document.getElementById('hardware-tuner-modal').style.display = 'none';
    }

    async function abrirRetentionPacerModal() {
      if (!currentPlan) return alert('Analise ou carregue um roteiro primeiro!');
      const modal = document.getElementById('retention-pacer-modal');
      const listEl = document.getElementById('retention-pacer-list');
      listEl.innerHTML = '<div style="color:var(--text-muted); text-align:center; padding:20px;">Calculando ondas de dopamina e alternância de ritmo...</div>';
      modal.style.display = 'flex';

      try {
        const res = await fetch(`/api/pacing/waves?project_id=${encodeURIComponent(currentPlan.project_id)}`);
        const data = await res.json();
        if (!data.ok) throw new Error(data.error || 'Erro no pacer');
        const pw = data.pacing;

        listEl.innerHTML = `
          <div style="background:#450a0a; border-left:4px solid #ef4444; padding:12px; border-radius:6px; display:flex; justify-content:space-between; align-items:center;">
            <div>
              <div style="font-weight:700; color:#fecaca; font-size:0.95rem;">💓 Hollywood Dopamine Wave (Ondas de Pacing)</div>
              <div style="font-size:0.8rem; color:#fee2e2; margin-top:2px;">
                Cenas Contemplativas (4s-5s) alternadas com Rajadas de Alta Energia (1.5s-2s) | Duração Otimizada: <b>${pw.total_timeline_duration_sec}s</b>
              </div>
            </div>
            <button class="btn" style="background:#ef4444; color:#fff; font-weight:700; font-size:0.8rem;" onclick="aplicarPacingDopamina()">⚡ Aplicar Pacing à Timeline</button>
          </div>
          <div style="display:flex; flex-direction:column; gap:6px; max-height:300px; overflow-y:auto; margin-top:8px;">
            ${(pw.pacing_beats || []).map(b => `
              <div style="background:var(--card-bg); border:1px solid var(--border); padding:8px 10px; border-radius:4px; display:flex; justify-content:space-between; align-items:center; font-size:0.8rem;">
                <div>
                  <b style="color:#fff;">Cena #${b.scene_order}</b>
                  <span style="margin-left:8px; color:#fca5a5; font-weight:600;">[${b.rhythm_phase.toUpperCase()}]</span>
                  <span style="margin-left:6px; font-size:0.75rem; color:var(--text-muted);">${b.dopamine_target}</span>
                </div>
                <span style="background:#1e293b; color:#93c5fd; padding:2px 8px; border-radius:4px; font-weight:700;">${b.optimized_duration}s (${b.recommended_cut_tempo})</span>
              </div>
            `).join('')}
          </div>
        `;
      } catch (e) {
        listEl.innerHTML = `<div style="color:#ef4444; padding:10px;">Falha: ${e.message}</div>`;
      }
    }
    function fecharRetentionPacerModal() {
      document.getElementById('retention-pacer-modal').style.display = 'none';
    }
    async function aplicarPacingDopamina() {
      if (!currentPlan) return;
      showStatus('Aplicando modulação de ritmo de dopamina à timeline...', '#ef4444');
      try {
        const res = await fetch('/api/pacing/apply', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ project_id: currentPlan.project_id })
        });
        const data = await res.json();
        if (data.ok) {
          showStatus('Pacing cinematográfico aplicado!', '#10b981');
          alert('Sucesso!\n\nAs durações das cenas foram recalculadas em ondas de tensão, contemplação e rajadas de informação.');
          fecharRetentionPacerModal();
        }
      } catch (e) {
        alert('Erro ao aplicar pacing: ' + e.message);
      }
    }

    async function abrirCommunityPostModal() {
      if (!currentPlan) return alert('Analise ou carregue um roteiro primeiro!');
      const modal = document.getElementById('community-post-modal');
      const contentEl = document.getElementById('community-post-content');
      contentEl.innerHTML = '<div style="color:var(--text-muted); text-align:center; padding:20px;">Gerando kit de engajamento para a aba Comunidade do YouTube...</div>';
      modal.style.display = 'flex';

      try {
        const res = await fetch(`/api/community/kit?project_id=${encodeURIComponent(currentPlan.project_id)}`);
        const data = await res.json();
        if (!data.ok) throw new Error(data.error || 'Erro no kit de comunidade');
        const kit = data.kit;

        contentEl.innerHTML = `
          <div style="background:#0c4a6e; border-left:4px solid #0284c7; padding:12px; border-radius:6px;">
            <div style="font-weight:700; color:#bae6fd; font-size:0.95rem;">📢 Kit de Publicação para Aba Comunidade do YouTube</div>
            <div style="font-size:0.8rem; color:#e0f2fe; margin-top:2px;">
              ${kit.recommended_publish_timing}
            </div>
          </div>

          <div style="background:var(--card-bg); border:1px solid var(--border); padding:12px; border-radius:6px; display:flex; flex-direction:column; gap:6px; margin-top:8px;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
              <b style="color:#fde047; font-size:0.9rem;">📊 1. Enquete de Múltipla Escolha:</b>
              <button class="btn btn-secondary" style="font-size:0.75rem;" onclick="copiarPostComunidade('poll')">📋 Copiar Pergunta & Opções</button>
            </div>
            <div style="font-weight:600; color:#fff; font-size:0.85rem;" id="comm-poll-q">${kit.poll.poll_question}</div>
            <div style="display:flex; flex-direction:column; gap:4px; margin-top:4px;" id="comm-poll-opts">
              ${kit.poll.options.map((opt, i) => `<div style="background:#0f172a; padding:6px 10px; border-radius:4px; font-size:0.8rem; color:#cbd5e1;">Opção ${i+1}: ${opt}</div>`).join('')}
            </div>
          </div>

          <div style="background:var(--card-bg); border:1px solid var(--border); padding:12px; border-radius:6px; display:flex; flex-direction:column; gap:6px; margin-top:8px;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
              <b style="color:#38bdf8; font-size:0.9rem;">🚨 2. Teaser com Imagem de Bastidor:</b>
              <button class="btn btn-secondary" style="font-size:0.75rem;" onclick="copiarPostComunidade('teaser')">📋 Copiar Texto do Teaser</button>
            </div>
            <textarea id="comm-teaser-text" readonly style="width:100%; height:90px; background:#0f172a; border:1px solid #334155; color:#fff; font-size:0.82rem; padding:8px; border-radius:4px;">${kit.teaser_post_text}</textarea>
          </div>

          <div style="background:var(--card-bg); border:1px solid var(--border); padding:12px; border-radius:6px; display:flex; flex-direction:column; gap:6px; margin-top:8px;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
              <b style="color:#a7f3d0; font-size:0.9rem;">💬 3. Pergunta Aberta para Comentários:</b>
              <button class="btn btn-secondary" style="font-size:0.75rem;" onclick="copiarPostComunidade('discussion')">📋 Copiar Pergunta</button>
            </div>
            <div style="background:#0f172a; padding:8px 10px; border-radius:4px; font-size:0.82rem; color:#e2e8f0;" id="comm-discussion-text">${kit.open_discussion_question}</div>
          </div>
        `;
      } catch (e) {
        contentEl.innerHTML = `<div style="color:#ef4444; padding:10px;">Falha: ${e.message}</div>`;
      }
    }
    function fecharCommunityPostModal() {
      document.getElementById('community-post-modal').style.display = 'none';
    }
    function copiarPostComunidade(tipo) {
      let txt = '';
      if (tipo === 'poll') {
        const q = document.getElementById('comm-poll-q').innerText;
        const opts = Array.from(document.getElementById('comm-poll-opts').children).map(c => c.innerText).join('\n');
        txt = `${q}\n\n${opts}`;
      } else if (tipo === 'teaser') {
        txt = document.getElementById('comm-teaser-text').value;
      } else if (tipo === 'discussion') {
        txt = document.getElementById('comm-discussion-text').innerText;
      }
      navigator.clipboard.writeText(txt);
      alert('Texto copiado com sucesso para a área de transferência!');
    }

    // === OMEGA STUDIO: SPATIAL AUDIO 8D, END SCREEN, LOUDNORM -14 LUFS, VOCABULARY AUDITOR ===
    async function abrirSpatialAudioModal() {
      if (!currentPlan) return alert('Analise ou carregue um roteiro primeiro!');
      const modal = document.getElementById('spatial-audio-modal');
      const listEl = document.getElementById('spatial-audio-list');
      listEl.innerHTML = '<div style="color:var(--text-muted); text-align:center; padding:20px;">Calculando trajetórias estéreo 3D e modelagem binaural 8D...</div>';
      modal.style.display = 'flex';

      try {
        const res = await fetch(`/api/audio/spatial?project_id=${encodeURIComponent(currentPlan.project_id)}`);
        const data = await res.json();
        if (!data.ok) throw new Error(data.error || 'Erro no áudio espacial');
        const s = data.manifest;

        listEl.innerHTML = `
          <div style="background:#083344; border-left:4px solid #06b6d4; padding:12px; border-radius:6px;">
            <div style="font-weight:700; color:#a5f3fc; font-size:0.95rem;">🎧 ${s.binaural_mode}</div>
            <div style="font-size:0.8rem; color:#cffafe; margin-top:2px;">
              Panning dinâmico e expansão de campo estéreo aplicado em <b>${s.total_spatial_events}</b> cenas para imersão em fones de ouvido.
            </div>
          </div>
          <div style="display:flex; flex-direction:column; gap:6px; max-height:360px; overflow-y:auto; margin-top:8px;">
            ${(s.events || []).map(e => `
              <div style="background:var(--card-bg); border:1px solid var(--border); padding:8px 10px; border-radius:4px; font-size:0.8rem;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                  <b style="color:#fff;">Cena #${e.scene_order}: <span style="color:#38bdf8;">${e.pan_trajectory}</span></b>
                  <span style="background:#164e63; color:#a5f3fc; font-size:0.72rem; padding:2px 6px; border-radius:4px; font-weight:700;">${e.duration_sec}s</span>
                </div>
                <div style="color:var(--text-muted); font-size:0.75rem; margin-top:3px;">${e.narrative_justification}</div>
                <div style="font-family:monospace; font-size:0.7rem; color:#10b981; background:#0f172a; padding:4px 6px; border-radius:4px; margin-top:4px; word-break:break-all;">
                  ${e.ffmpeg_pan_filter}
                </div>
              </div>
            `).join('')}
          </div>
        `;
      } catch (e) {
        listEl.innerHTML = `<div style="color:#ef4444; padding:10px;">Falha: ${e.message}</div>`;
      }
    }
    function fecharSpatialAudioModal() {
      document.getElementById('spatial-audio-modal').style.display = 'none';
    }

    async function abrirEndScreenModal() {
      if (!currentPlan) return alert('Analise ou carregue um roteiro primeiro!');
      const modal = document.getElementById('end-screen-modal');
      const contentEl = document.getElementById('end-screen-content');
      contentEl.innerHTML = '<div style="color:var(--text-muted); text-align:center; padding:20px;">Planejando tela final com safe zone do YouTube Studio...</div>';
      modal.style.display = 'flex';

      try {
        const res = await fetch(`/api/endscreen/plan?project_id=${encodeURIComponent(currentPlan.project_id)}`);
        const data = await res.json();
        if (!data.ok) throw new Error(data.error || 'Erro na tela final');
        const es = data.plan;

        contentEl.innerHTML = `
          <div style="background:#451a03; border-left:4px solid #f59e0b; padding:12px; border-radius:6px;">
            <div style="font-weight:700; color:#fde68a; font-size:0.95rem;">🎬 Telas Finais Cinematográficas (Últimos ${es.end_screen_duration_sec}s)</div>
            <div style="font-size:0.8rem; color:#fef3c7; margin-top:2px;">
              Áreas demarcadas milimetricamente para os cards nativos do YouTube Studio sem obstruir o conteúdo.
            </div>
          </div>
          <div style="background:var(--card-bg); border:1px solid var(--border); padding:12px; border-radius:6px; display:flex; flex-direction:column; gap:8px; margin-top:8px;">
            <div>
              <b style="color:#93c5fd; font-size:0.85rem;">Chamada para Ação (CTA Headline):</b>
              <div style="color:#fff; font-size:0.95rem; font-weight:700; margin-top:3px;">"${es.cta_headline}"</div>
            </div>
            <div style="display:grid; grid-template-columns:1fr 1fr; gap:8px; margin-top:4px;">
              <div style="background:#0f172a; padding:8px; border-radius:4px; font-size:0.78rem;">
                <b style="color:#fbbf24;">📦 Card Próximo Vídeo (16:9):</b>
                <div style="color:#cbd5e1; font-family:monospace; margin-top:2px;">${es.youtube_box_coordinates}</div>
              </div>
              <div style="background:#0f172a; padding:8px; border-radius:4px; font-size:0.78rem;">
                <b style="color:#38bdf8;">🔘 Card Inscrever-se (Canal):</b>
                <div style="color:#cbd5e1; font-family:monospace; margin-top:2px;">${es.subscribe_coordinates}</div>
              </div>
            </div>
            <div style="font-family:monospace; font-size:0.72rem; color:#10b981; background:#0f172a; padding:6px; border-radius:4px; margin-top:4px; word-break:break-all;">
              ${es.ffmpeg_outro_filter}
            </div>
          </div>
        `;
      } catch (e) {
        contentEl.innerHTML = `<div style="color:#ef4444; padding:10px;">Falha: ${e.message}</div>`;
      }
    }
    function fecharEndScreenModal() {
      document.getElementById('end-screen-modal').style.display = 'none';
    }

    async function abrirLoudnessModal() {
      if (!currentPlan) return alert('Analise ou carregue um roteiro primeiro!');
      const modal = document.getElementById('loudness-modal');
      const contentEl = document.getElementById('loudness-content');
      contentEl.innerHTML = '<div style="color:var(--text-muted); text-align:center; padding:20px;">Calculando normalização EBU R128 e ITU-R BS.1770-4...</div>';
      modal.style.display = 'flex';

      try {
        const res = await fetch(`/api/audio/loudness?project_id=${encodeURIComponent(currentPlan.project_id)}`);
        const data = await res.json();
        if (!data.ok) throw new Error(data.error || 'Erro no normalizador de loudness');
        const l = data.loudness;

        contentEl.innerHTML = `
          <div style="background:#064e3b; border-left:4px solid #10b981; padding:12px; border-radius:6px;">
            <div style="font-weight:700; color:#a7f3d0; font-size:0.95rem;">🎚️ Normalização Padrão Mundial: ${l.selected_target}</div>
            <div style="font-size:0.8rem; color:#d1fae5; margin-top:2px;">
              Proteção total contra a penalidade algorítmica de volume do YouTube: Integrated Loudness em <b>${l.target_lufs} LUFS</b> | True Peak: <b>${l.target_true_peak} dBTP</b>.
            </div>
          </div>
          <div style="display:flex; flex-direction:column; gap:8px; max-height:300px; overflow-y:auto; margin-top:8px;">
            ${(l.all_presets || []).map(p => `
              <div style="background:var(--card-bg); border:1px solid var(--border); padding:10px; border-radius:6px; display:flex; justify-content:space-between; align-items:center;">
                <div>
                  <b style="color:#fff; font-size:0.9rem;">${p.platform_name}</b>
                  <div style="font-size:0.75rem; color:var(--text-muted); margin-top:2px;">LRA: ${p.loudness_range_lra} | True Peak: ${p.true_peak_dbtp} dBTP | Bitrate: ${p.recommended_bitrate}</div>
                </div>
                <span style="font-family:monospace; font-size:0.75rem; color:#10b981; background:#0f172a; padding:4px 8px; border-radius:4px;">${p.ffmpeg_loudnorm_filter}</span>
              </div>
            `).join('')}
          </div>
        `;
      } catch (e) {
        contentEl.innerHTML = `<div style="color:#ef4444; padding:10px;">Falha: ${e.message}</div>`;
      }
    }
    function fecharLoudnessModal() {
      document.getElementById('loudness-modal').style.display = 'none';
    }

    async function abrirVocabularyModal() {
      if (!currentPlan) return alert('Analise ou carregue um roteiro primeiro!');
      const modal = document.getElementById('vocabulary-modal');
      const listEl = document.getElementById('vocabulary-list');
      listEl.innerHTML = '<div style="color:var(--text-muted); text-align:center; padding:20px;">Varrendo roteiro em busca de frases passivas e clichês...</div>';
      modal.style.display = 'flex';

      try {
        const res = await fetch(`/api/vocabulary/audit?project_id=${encodeURIComponent(currentPlan.project_id)}`);
        const data = await res.json();
        if (!data.ok) throw new Error(data.error || 'Erro no auditor de vocabulário');
        const v = data.result;

        const gradeColor = v.script_grade === 'A+' ? '#10b981' : (v.script_grade === 'B+' ? '#f59e0b' : '#ef4444');

        listEl.innerHTML = `
          <div style="background:#2e1065; border-left:4px solid #7c3aed; padding:12px; border-radius:6px; display:flex; justify-content:space-between; align-items:center;">
            <div>
              <div style="font-weight:700; color:#ddd6fe; font-size:0.95rem;">🧠 Auditor Neuro-Linguístico de Roteiro</div>
              <div style="font-size:0.8rem; color:#ede9fe; margin-top:2px;">
                Pontuação de Impacto: <b>${v.neuro_linguistic_score}/100</b> | Termos Fracos Encontrados: <b>${v.total_weak_phrases_found}</b>
              </div>
            </div>
            <div style="text-align:center; background:#1e1b4b; padding:6px 14px; border-radius:8px;">
              <div style="font-size:0.7rem; color:#c4b5fd;">Nota do Roteiro:</div>
              <b style="font-size:1.4rem; color:${gradeColor};">${v.script_grade}</b>
            </div>
          </div>
          <div style="margin-top:10px;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
              <b style="color:#fff; font-size:0.85rem;">Substituições Neuro-Linguísticas Recomendadas:</b>
              ${v.total_weak_phrases_found > 0 ? `<button class="btn" style="background:#7c3aed; color:#fff; font-weight:700; font-size:0.75rem;" onclick="aprimorarVocabularioAuto()">⚡ Polir Vocabulário Automaticamente</button>` : ''}
            </div>
            <div style="display:flex; flex-direction:column; gap:6px; max-height:280px; overflow-y:auto; margin-top:8px;">
              ${v.total_weak_phrases_found === 0 ? '<div style="color:#10b981; font-size:0.82rem; padding:10px;">✅ Vocabulário perfeito! Nenhum clichê ou frase passiva detectada.</div>' : ''}
              ${(v.issues || []).map(i => `
                <div style="background:var(--card-bg); border:1px solid var(--border); padding:8px 10px; border-radius:6px; font-size:0.8rem;">
                  <div style="display:flex; justify-content:space-between;">
                    <span style="color:#ef4444; text-decoration:line-through; font-weight:600;">"${i.weak_phrase}"</span>
                    <span style="color:#10b981; font-weight:700;">➔ "${i.suggested_replacement}"</span>
                  </div>
                  <div style="color:var(--text-muted); font-size:0.72rem; margin-top:3px;">Cena #${i.scene_order}: ${i.justification} (+${i.impact_gain_pct}% engajamento)</div>
                </div>
              `).join('')}
            </div>
          </div>
        `;
      } catch (e) {
        listEl.innerHTML = `<div style="color:#ef4444; padding:10px;">Falha: ${e.message}</div>`;
      }
    }
    function fecharVocabularyModal() {
      document.getElementById('vocabulary-modal').style.display = 'none';
    }
    async function aprimorarVocabularioAuto() {
      if (!currentPlan) return;
      showStatus('Substituindo frases passivas por gatilhos hipnóticos...', '#7c3aed');
      try {
        const res = await fetch('/api/vocabulary/enhance', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ project_id: currentPlan.project_id })
        });
        const data = await res.json();
        if (data.ok) {
          showStatus(`Roteiro aprimorado com sucesso! ${data.total_phrases_enhanced} termos polidos.`, '#10b981');
          alert(`Sucesso!\n\n${data.total_phrases_enhanced} termos passivos foram substituídos por gatilhos de alta conversão.`);
          abrirVocabularyModal();
        }
      } catch (e) {
        alert('Erro ao aprimorar: ' + e.message);
      }
    }

    async function abrirBrollPacerModal() {
      if (!currentPlan) return alert('Analise ou carregue um roteiro primeiro!');
      const modal = document.getElementById('broll-pacer-modal');
      const listEl = document.getElementById('broll-pacer-list');
      listEl.innerHTML = '<div style="color:var(--text-muted); text-align:center; padding:20px;">Analisando cadência de B-rolls e risco de fadiga visual...</div>';
      modal.style.display = 'flex';

      try {
        const res = await fetch(`/api/broll/pacing?project_id=${currentPlan.project_id}`);
        const data = await res.json();
        if (data.ok && data.pacing) {
          const p = data.pacing;
          let html = `
            <div style="background:var(--card-bg); border:1px solid var(--border); border-radius:8px; padding:12px; margin-bottom:12px;">
              <div style="display:flex; justify-content:space-between; align-items:center;">
                <span style="font-weight:700; color:#38bdf8;">Nota de Pacing Visual:</span>
                <span style="font-weight:800; color:${p.fatigue_risk === 'LOW' ? '#10b981' : p.fatigue_risk === 'MODERATE' ? '#f59e0b' : '#ef4444'};">${p.pacing_grade}</span>
              </div>
              <div style="font-size:0.85rem; color:var(--text-muted); margin-top:4px;">
                Cenas analisadas: ${p.total_scenes} | Riscos de estagnação: ${p.static_risk_count} | Limiar: ${p.max_static_threshold}s
              </div>
            </div>
            <div style="font-weight:700; font-size:0.9rem; margin-bottom:8px; color:var(--text-main);">Pontos Recomendados para Inserção de B-Roll:</div>
          `;
          if (p.recommendations.length === 0) {
            html += '<div style="color:#10b981; padding:12px; text-align:center;">✨ Excelente! Não há cenas longas com risco de fadiga visual.</div>';
          } else {
            p.recommendations.forEach(r => {
              html += `
                <div style="background:rgba(56,189,248,0.06); border:1px solid rgba(56,189,248,0.25); border-radius:6px; padding:10px; margin-bottom:8px;">
                  <div style="display:flex; justify-content:space-between; font-weight:600; font-size:0.88rem; color:#bae6fd;">
                    <span>Cena #${r.scene_index} (Aos ${r.insert_time}s)</span>
                    <span style="color:#38bdf8;">Duração: ${r.duration}s</span>
                  </div>
                  <div style="font-size:0.82rem; color:var(--text-muted); margin-top:4px;">${r.reason}</div>
                  <div style="font-size:0.82rem; color:#fde68a; margin-top:4px;">🔍 Sugestão de busca B-Roll: <b>"${r.suggested_query}"</b></div>
                </div>
              `;
            });
          }
          listEl.innerHTML = html;
        } else {
          listEl.innerHTML = `<div style="color:#ef4444;">Erro ao carregar pacing: ${data.error || 'Desconhecido'}</div>`;
        }
      } catch (e) {
        listEl.innerHTML = `<div style="color:#ef4444;">Erro na requisição: ${e.message}</div>`;
      }
    }
    function fecharBrollPacerModal() {
      document.getElementById('broll-pacer-modal').style.display = 'none';
    }
    async function aplicarBrollSlotsAuto() {
      if (!currentPlan) return;
      showStatus('Inserindo pontos de corte para B-roll na timeline...', '#38bdf8');
      try {
        const res = await fetch('/api/broll/insert_slots', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ project_id: currentPlan.project_id })
        });
        const data = await res.json();
        if (data.ok) {
          showStatus(`B-Roll Slots criados com sucesso! ${data.slots_created} marcações aplicadas.`, '#10b981');
          alert(`Sucesso!\n\n${data.slots_created} slots automáticos de B-roll foram adicionados para manter a retenção máxima.`);
          fecharBrollPacerModal();
        }
      } catch (e) {
        alert('Erro ao aplicar: ' + e.message);
      }
    }

    async function abrirFoleyModal() {
      if (!currentPlan) return alert('Analise ou carregue um roteiro primeiro!');
      const modal = document.getElementById('foley-modal');
      const listEl = document.getElementById('foley-list');
      listEl.innerHTML = '<div style="color:var(--text-muted); text-align:center; padding:20px;">Varrendo timeline para orquestrar Sound Design e Foley...</div>';
      modal.style.display = 'flex';

      try {
        const res = await fetch(`/api/audio/foley?project_id=${currentPlan.project_id}`);
        const data = await res.json();
        if (data.ok && data.foley) {
          const f = data.foley;
          let html = `
            <div style="background:var(--card-bg); border:1px solid var(--border); border-radius:8px; padding:12px; margin-bottom:12px;">
              <div style="display:flex; justify-content:space-between; align-items:center;">
                <span style="font-weight:700; color:#ec4899;">Densidade de Foley:</span>
                <span style="font-weight:800; color:#fbcfe8;">${f.sound_density} cues / min</span>
              </div>
              <div style="font-size:0.85rem; color:var(--text-muted); margin-top:4px;">${f.mix_guideline}</div>
            </div>
            <div style="font-weight:700; font-size:0.9rem; margin-bottom:8px; color:var(--text-main);">Trilha de SFX Sincronizada (${f.total_cues} eventos):</div>
          `;
          f.cues.forEach(c => {
            html += `
              <div style="background:rgba(236,72,153,0.06); border:1px solid rgba(236,72,153,0.25); border-radius:6px; padding:10px; margin-bottom:8px;">
                <div style="display:flex; justify-content:space-between; font-weight:600; font-size:0.88rem; color:#fbcfe8;">
                  <span>⏱️ ${c.timestamp}s — ${c.sample}</span>
                  <span style="color:#ec4899;">${c.volume_db} dB</span>
                </div>
                <div style="font-size:0.82rem; color:var(--text-muted); margin-top:4px;">${c.description} (Categoria: ${c.category})</div>
              </div>
            `;
          });
          listEl.innerHTML = html;
        } else {
          listEl.innerHTML = `<div style="color:#ef4444;">Erro ao carregar foley: ${data.error || 'Desconhecido'}</div>`;
        }
      } catch (e) {
        listEl.innerHTML = `<div style="color:#ef4444;">Erro na requisição: ${e.message}</div>`;
      }
    }
    function fecharFoleyModal() {
      document.getElementById('foley-modal').style.display = 'none';
    }

    async function abrirFilmStockModal() {
      if (!currentPlan) return alert('Analise ou carregue um roteiro primeiro!');
      const modal = document.getElementById('film-stock-modal');
      const listEl = document.getElementById('film-stock-list');
      listEl.innerHTML = '<div style="color:var(--text-muted); text-align:center; padding:20px;">Carregando perfis analógicos de película...</div>';
      modal.style.display = 'flex';

      try {
        const res = await fetch('/api/film_stock/list');
        const data = await res.json();
        if (data.ok && data.stocks) {
          let html = '<div style="display:flex; flex-direction:column; gap:10px;">';
          for (const [key, stock] of Object.entries(data.stocks)) {
            html += `
              <div style="background:var(--card-bg); border:1px solid var(--border); border-radius:8px; padding:12px; display:flex; justify-content:space-between; align-items:center;">
                <div style="flex:1;">
                  <div style="font-weight:700; color:#fef08a; font-size:0.95rem;">${stock.name}</div>
                  <div style="font-size:0.82rem; color:var(--text-muted); margin-top:3px;">${stock.description}</div>
                  <div style="font-size:0.75rem; color:#94a3b8; margin-top:4px; font-family:monospace;">Granulação: ${stock.grain_default} | Contraste: ${stock.contrast}x | Saturação: ${stock.saturation}x</div>
                </div>
                <button class="btn" style="background:#eab308; color:#000; font-weight:700; margin-left:12px;" onclick="aplicarFilmStockSelecionado('${key}')">Aplicar</button>
              </div>
            `;
          }
          html += '</div>';
          listEl.innerHTML = html;
        } else {
          listEl.innerHTML = `<div style="color:#ef4444;">Erro ao carregar películas.</div>`;
        }
      } catch (e) {
        listEl.innerHTML = `<div style="color:#ef4444;">Erro na requisição: ${e.message}</div>`;
      }
    }
    function fecharFilmStockModal() {
      document.getElementById('film-stock-modal').style.display = 'none';
    }
    async function aplicarFilmStockSelecionado(stockKey) {
      if (!currentPlan) return;
      showStatus('Aplicando perfil de película e curvas FFmpeg...', '#eab308');
      try {
        const res = await fetch('/api/film_stock/apply', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ project_id: currentPlan.project_id, film_stock: stockKey })
        });
        const data = await res.json();
        if (data.ok) {
          showStatus(`Película ${stockKey} aplicada com sucesso!`, '#10b981');
          alert(`Sucesso!\n\nPerfil de película "${stockKey}" aplicado ao projeto com filtros estocásticos de granulação e curvas analógicas.`);
          fecharFilmStockModal();
        }
      } catch (e) {
        alert('Erro ao aplicar: ' + e.message);
      }
    }

    async function abrirCTROptimizerModal() {
      if (!currentPlan) return alert('Analise ou carregue um roteiro primeiro!');
      const modal = document.getElementById('ctr-optimizer-modal');
      const contentEl = document.getElementById('ctr-optimizer-content');
      contentEl.innerHTML = '<div style="color:var(--text-muted); text-align:center; padding:20px;">Gerando títulos de alto CTR, tags SEO e descrição estruturada...</div>';
      modal.style.display = 'flex';

      try {
        const res = await fetch(`/api/metadata/seo?project_id=${currentPlan.project_id}`);
        const data = await res.json();
        if (data.ok && data.metadata) {
          const m = data.metadata;
          let html = `
            <div style="background:var(--card-bg); border:1px solid var(--border); border-radius:8px; padding:12px; margin-bottom:12px;">
              <div style="display:flex; justify-content:space-between; align-items:center;">
                <span style="font-weight:700; color:#14b8a6;">Potencial Estimado de CTR:</span>
                <span style="font-weight:800; color:#99f6e4;">${m.ctr_potential_index} (SEO Score: ${m.seo_score}/100)</span>
              </div>
            </div>
            <div style="font-weight:700; font-size:0.9rem; margin-bottom:8px; color:var(--text-main);">5 Títulos com Fórmulas Psicológicas de CTR:</div>
          `;
          m.title_variants.forEach(tv => {
            html += `
              <div style="background:rgba(20,184,166,0.06); border:1px solid rgba(20,184,166,0.25); border-radius:6px; padding:10px; margin-bottom:8px;">
                <div style="display:flex; justify-content:space-between; font-weight:700; font-size:0.9rem; color:#99f6e4;">
                  <span>"${tv.title}"</span>
                  <span style="color:#14b8a6;">CTR: ${tv.ctr_potential}</span>
                </div>
                <div style="font-size:0.8rem; color:var(--text-muted); margin-top:2px;">Gatilho: ${tv.formula}</div>
              </div>
            `;
          });
          html += `
            <div style="font-weight:700; font-size:0.9rem; margin-top:12px; margin-bottom:8px; color:var(--text-main);">Descrição Pronta para YouTube Studio (Com Capítulos Automáticos):</div>
            <textarea id="ctr-desc-text" readonly style="width:100%; height:130px; background:#0f172a; border:1px solid var(--border); border-radius:6px; color:#e2e8f0; font-size:0.82rem; padding:10px; font-family:monospace; resize:none;">${m.structured_description}</textarea>
            <div style="display:flex; justify-content:flex-end; margin-top:6px;">
              <button class="btn btn-secondary" style="font-size:0.8rem;" onclick="copiarTextoDescricao()">📋 Copiar Descrição</button>
            </div>
            <div style="font-weight:700; font-size:0.9rem; margin-top:12px; margin-bottom:8px; color:var(--text-main);">Tags SEO Recomendadas (${m.recommended_tags.length}):</div>
            <div style="background:var(--card-bg); border:1px solid var(--border); border-radius:6px; padding:10px; font-size:0.82rem; color:#bae6fd;">
              ${m.recommended_tags.join(', ')}
            </div>
          `;
          contentEl.innerHTML = html;
        } else {
          contentEl.innerHTML = `<div style="color:#ef4444;">Erro ao gerar SEO: ${data.error || 'Desconhecido'}</div>`;
        }
      } catch (e) {
        contentEl.innerHTML = `<div style="color:#ef4444;">Erro na requisição: ${e.message}</div>`;
      }
    }
    function fecharCTROptimizerModal() {
      document.getElementById('ctr-optimizer-modal').style.display = 'none';
    }
    function copiarTextoDescricao() {
      const el = document.getElementById('ctr-desc-text');
      if (el) {
        navigator.clipboard.writeText(el.value).then(() => {
          alert('Descrição copiada para a área de transferência!');
        });
      }
    }

    async function abrirDenoiseModal() {
      if (!currentPlan) return alert('Analise ou carregue um roteiro primeiro!');
      const modal = document.getElementById('denoise-modal');
      const listEl = document.getElementById('denoise-list');
      listEl.innerHTML = '<div style="color:var(--text-muted); text-align:center; padding:20px;">Carregando perfis de isolamento espectral de ruído...</div>';
      modal.style.display = 'flex';

      try {
        const res = await fetch('/api/voice/denoise/profiles');
        const data = await res.json();
        if (data.ok && data.profiles) {
          let html = '<div style="display:flex; flex-direction:column; gap:10px;">';
          for (const [key, p] of Object.entries(data.profiles)) {
            html += `
              <div style="background:var(--card-bg); border:1px solid var(--border); border-radius:8px; padding:12px; display:flex; justify-content:space-between; align-items:center;">
                <div style="flex:1;">
                  <div style="font-weight:700; color:#c7d2fe; font-size:0.95rem;">${p.name}</div>
                  <div style="font-size:0.82rem; color:var(--text-muted); margin-top:3px;">${p.description}</div>
                  <div style="font-size:0.75rem; color:#818cf8; margin-top:4px; font-family:monospace;">Corte: ${p.highpass_hz}Hz - ${p.lowpass_hz}Hz | Redução: -${p.noise_reduction_db}dB | Gate: ${p.gate_threshold_db}dB</div>
                </div>
                <button class="btn" style="background:#6366f1; color:#fff; font-weight:700; margin-left:12px;" onclick="aplicarDenoiseSelecionado('${key}')">Aplicar</button>
              </div>
            `;
          }
          html += '</div>';
          listEl.innerHTML = html;
        } else {
          listEl.innerHTML = `<div style="color:#ef4444;">Erro ao carregar perfis de denoise.</div>`;
        }
      } catch (e) {
        listEl.innerHTML = `<div style="color:#ef4444;">Erro na requisição: ${e.message}</div>`;
      }
    }
    function fecharDenoiseModal() {
      document.getElementById('denoise-modal').style.display = 'none';
    }
    async function aplicarDenoiseSelecionado(profileKey) {
      if (!currentPlan) return;
      showStatus('Aplicando isolamento espectral à locução...', '#6366f1');
      try {
        const res = await fetch('/api/voice/denoise/apply', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ project_id: currentPlan.project_id, profile: profileKey })
        });
        const data = await res.json();
        if (data.ok) {
          showStatus(`Denoise ${profileKey} configurado com sucesso!`, '#10b981');
          alert(`Sucesso!\n\nPerfil de filtragem vocal "${profileKey}" associado ao projeto com ganho estimado de +${data.estimated_snr_gain_db}dB SNR.`);
          fecharDenoiseModal();
        }
      } catch (e) {
        alert('Erro ao aplicar denoise: ' + e.message);
      }
    }

    async function abrirTransitionsModal() {
      if (!currentPlan) return alert('Analise ou carregue um roteiro primeiro!');
      const modal = document.getElementById('transitions-modal');
      const listEl = document.getElementById('transitions-list');
      listEl.innerHTML = '<div style="color:var(--text-muted); text-align:center; padding:20px;">Orquestrando transições cinemáticas entre cenas...</div>';
      modal.style.display = 'flex';

      try {
        const res = await fetch(`/api/transitions/plan?project_id=${currentPlan.project_id}`);
        const data = await res.json();
        if (data.ok && data.transitions) {
          const t = data.transitions;
          let html = `
            <div style="background:var(--card-bg); border:1px solid var(--border); border-radius:8px; padding:12px; margin-bottom:12px; display:flex; justify-content:space-between; align-items:center;">
              <span style="font-weight:700; color:#f97316;">Score de Fluidez Cinemática:</span>
              <span style="font-weight:800; color:#ffedd5;">${t.smoothness_score}% (${t.total_transitions} cortes adaptativos)</span>
            </div>
            <div style="font-weight:700; font-size:0.9rem; margin-bottom:8px; color:var(--text-main);">Mapa de Transições de Cena:</div>
          `;
          t.transitions.forEach(tr => {
            html += `
              <div style="background:rgba(249,115,22,0.06); border:1px solid rgba(249,115,22,0.25); border-radius:6px; padding:10px; margin-bottom:8px;">
                <div style="display:flex; justify-content:space-between; font-weight:700; font-size:0.88rem; color:#ffedd5;">
                  <span>Cena #${tr.from_scene_index} ➔ Cena #${tr.to_scene_index} (Aos ${tr.cut_timestamp}s)</span>
                  <span style="color:#f97316;">${tr.name} (${tr.duration}s)</span>
                </div>
                <div style="font-size:0.82rem; color:var(--text-muted); margin-top:4px;">Motivo: ${tr.reason}</div>
              </div>
            `;
          });
          listEl.innerHTML = html;
        } else {
          listEl.innerHTML = `<div style="color:#ef4444;">Erro ao planejar transições: ${data.error || 'Desconhecido'}</div>`;
        }
      } catch (e) {
        listEl.innerHTML = `<div style="color:#ef4444;">Erro na requisição: ${e.message}</div>`;
      }
    }
    function fecharTransitionsModal() {
      document.getElementById('transitions-modal').style.display = 'none';
    }

    async function abrirShortsModal() {
      if (!currentPlan) return alert('Analise ou carregue um roteiro primeiro!');
      const modal = document.getElementById('shorts-modal');
      const listEl = document.getElementById('shorts-list');
      listEl.innerHTML = '<div style="color:var(--text-muted); text-align:center; padding:20px;">Localizando picos de retenção para gerar Shorts 9:16...</div>';
      modal.style.display = 'flex';

      try {
        const res = await fetch(`/api/shorts/generate?project_id=${currentPlan.project_id}`);
        const data = await res.json();
        if (data.ok && data.shorts) {
          const s = data.shorts;
          let html = `
            <div style="background:var(--card-bg); border:1px solid var(--border); border-radius:8px; padding:12px; margin-bottom:12px; display:flex; justify-content:space-between; align-items:center;">
              <span style="font-weight:700; color:#e11d48;">Formato Vertical:</span>
              <span style="font-weight:800; color:#ffe4e6;">${s.export_resolution} (${s.total_shorts_generated} clipes gerados)</span>
            </div>
            <div style="font-weight:700; font-size:0.9rem; margin-bottom:8px; color:var(--text-main);">Clipes Virais Extraídos do Vídeo:</div>
          `;
          s.shorts.forEach(c => {
            html += `
              <div style="background:rgba(225,29,72,0.06); border:1px solid rgba(225,29,72,0.25); border-radius:6px; padding:12px; margin-bottom:10px;">
                <div style="display:flex; justify-content:space-between; font-weight:700; font-size:0.92rem; color:#ffe4e6;">
                  <span>${c.title}</span>
                  <span style="color:#e11d48;">Viral Score: ${c.viral_potential_score}%</span>
                </div>
                <div style="font-size:0.82rem; color:#fde68a; margin-top:4px;">🎯 Gancho Visual no Topo: <b>"${c.hook_headline}"</b></div>
                <div style="font-size:0.8rem; color:var(--text-muted); margin-top:3px;">
                  Intervalo: ${c.start_time}s até ${c.end_time}s (Duração: ${c.duration}s) | Layout: Blur Stack Background
                </div>
              </div>
            `;
          });
          listEl.innerHTML = html;
        } else {
          listEl.innerHTML = `<div style="color:#ef4444;">Erro ao gerar Shorts: ${data.error || 'Desconhecido'}</div>`;
        }
      } catch (e) {
        listEl.innerHTML = `<div style="color:#ef4444;">Erro na requisição: ${e.message}</div>`;
      }
    }
    function fecharShortsModal() {
      document.getElementById('shorts-modal').style.display = 'none';
    }

    async function abrirRecoveryModal() {
      if (!currentPlan) return alert('Analise ou carregue um roteiro primeiro!');
      const modal = document.getElementById('recovery-modal');
      const contentEl = document.getElementById('recovery-content');
      contentEl.innerHTML = '<div style="color:var(--text-muted); text-align:center; padding:20px;">Consultando checkpoints de renderização atômica...</div>';
      modal.style.display = 'flex';

      try {
        const res = await fetch(`/api/render/recovery/status?project_id=${currentPlan.project_id}`);
        const data = await res.json();
        if (data.ok && data.status) {
          const st = data.status;
          let html = `
            <div style="background:var(--card-bg); border:1px solid var(--border); border-radius:8px; padding:14px; margin-bottom:12px;">
              <div style="display:flex; justify-content:space-between; align-items:center;">
                <span style="font-weight:700; color:#22c55e;">Status de Tolerância a Falhas:</span>
                <span style="font-weight:800; color:${st.has_resumable_checkpoint ? '#f59e0b' : '#22c55e'};">
                  ${st.has_resumable_checkpoint ? 'CHECKPOINT RECUPERÁVEL DETECTADO' : 'PRONTO / SEM INTERRUPÇÕES'}
                </span>
              </div>
              <div style="font-size:0.85rem; color:var(--text-muted); margin-top:6px;">${st.message}</div>
            </div>
          `;
          if (st.has_resumable_checkpoint) {
            html += `
              <div style="background:rgba(34,197,94,0.06); border:1px solid rgba(34,197,94,0.25); border-radius:6px; padding:12px; margin-bottom:12px;">
                <div style="font-weight:700; color:#bbf7d0; font-size:0.9rem;">Dados do Checkpoint Salvo:</div>
                <div style="font-size:0.82rem; color:var(--text-muted); margin-top:4px;">Progresso concluído antes da parada: <b>${st.progress_percent}%</b></div>
                <div style="font-size:0.82rem; color:var(--text-muted); margin-top:2px;">Cenas já salvas em disco: <b>${st.saved_chunks_count} de ${st.total_scenes}</b></div>
                <div style="font-size:0.82rem; color:#fde68a; margin-top:4px;">🚀 O próximo render iniciará automaticamente a partir da <b>Cena #${st.resume_from_scene_index}</b>.</div>
              </div>
              <div style="display:flex; justify-content:flex-end;">
                <button class="btn btn-secondary" style="border-color:#ef4444; color:#fca5a5; font-size:0.8rem;" onclick="limparRecoveryCheckpoint()">🗑️ Descartar Checkpoint e Reiniciar do Zero</button>
              </div>
            `;
          } else {
            html += `
              <div style="color:var(--text-muted); font-size:0.85rem; line-height:1.5;">
                O guardião de crash recovery salva o progresso a cada cena compilada. Caso o computador seja reiniciado ou o processo sofra interrupção forçada, você poderá retomar o render sem perder os blocos já processados.
              </div>
            `;
          }
          contentEl.innerHTML = html;
        } else {
          contentEl.innerHTML = `<div style="color:#ef4444;">Erro ao consultar recovery: ${data.error || 'Desconhecido'}</div>`;
        }
      } catch (e) {
        contentEl.innerHTML = `<div style="color:#ef4444;">Erro na requisição: ${e.message}</div>`;
      }
    }
    function fecharRecoveryModal() {
      document.getElementById('recovery-modal').style.display = 'none';
    }
    async function limparRecoveryCheckpoint() {
      if (!currentPlan) return;
      if (!confirm('Deseja realmente descartar o checkpoint salvo e reiniciar a fila de render?')) return;
      try {
        const res = await fetch('/api/render/recovery/clear', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ project_id: currentPlan.project_id })
        });
        const data = await res.json();
        if (data.ok) {
          alert('Checkpoint limpo com sucesso.');
          abrirRecoveryModal();
        }
      } catch (e) {
        alert('Erro ao limpar checkpoint: ' + e.message);
      }
    }

    async function abrirBitrateModal() {
      if (!currentPlan) return alert('Analise ou carregue um roteiro primeiro!');
      const modal = document.getElementById('bitrate-modal');
      const listEl = document.getElementById('bitrate-list');
      listEl.innerHTML = '<div style="color:var(--text-muted); text-align:center; padding:20px;">Calculando taxas ideais de compressão e largura de banda...</div>';
      modal.style.display = 'flex';
      calcularBitrateCustom('youtube_1080p_pro');
    }
    function fecharBitrateModal() {
      document.getElementById('bitrate-modal').style.display = 'none';
    }
    async function calcularBitrateCustom(profileKey) {
      const listEl = document.getElementById('bitrate-list');
      try {
        const res = await fetch(`/api/bitrate/calculate?project_id=${currentPlan.project_id}&profile=${profileKey}`);
        const data = await res.json();
        if (data.ok && data.bitrate_plan) {
          const bp = data.bitrate_plan;
          const p = bp.profile_details;
          listEl.innerHTML = `
            <div style="background:var(--card-bg); border:1px solid var(--border); border-radius:8px; padding:14px; margin-bottom:12px;">
              <div style="display:flex; justify-content:space-between; align-items:center;">
                <span style="font-weight:700; color:#3b82f6; font-size:1rem;">Perfil Ativo: ${p.name}</span>
                <span style="font-weight:800; color:#bfdbfe; font-size:1.1rem;">~${bp.estimated_file_size_mb} MB</span>
              </div>
              <div style="font-size:0.84rem; color:var(--text-muted); margin-top:4px;">${p.description}</div>
              <div style="font-size:0.78rem; color:#93c5fd; margin-top:6px; font-family:monospace;">
                Resolução: ${p.resolution} @ ${p.fps}fps | Alvo: ${p.target_bitrate_kbps}k | Max: ${p.max_bitrate_kbps}k | Codec: ${p.codec}
              </div>
            </div>
            <div style="font-weight:700; font-size:0.9rem; margin-bottom:8px; color:var(--text-main);">Alternar Perfil de Compressão:</div>
            <div style="display:flex; gap:8px; flex-wrap:wrap; margin-bottom:14px;">
              <button class="btn btn-secondary" style="font-size:0.8rem;" onclick="calcularBitrateCustom('youtube_1080p_pro')">YouTube 1080p Pro</button>
              <button class="btn btn-secondary" style="font-size:0.8rem;" onclick="calcularBitrateCustom('youtube_4k_ultra')">YouTube 4K Ultra</button>
              <button class="btn btn-secondary" style="font-size:0.8rem;" onclick="calcularBitrateCustom('web_fast_stream')">Web Fast Mobile</button>
              <button class="btn btn-secondary" style="font-size:0.8rem;" onclick="calcularBitrateCustom('archive_lossless_prores')">Master ProRes 422</button>
            </div>
            <div style="font-weight:700; font-size:0.88rem; margin-bottom:6px; color:var(--text-main);">Cadeia de Argumentos FFmpeg Gerada:</div>
            <textarea readonly style="width:100%; height:80px; background:#0f172a; border:1px solid var(--border); border-radius:6px; color:#93c5fd; font-size:0.8rem; padding:8px; font-family:monospace; resize:none;">${bp.ffmpeg_compression_args}</textarea>
          `;
        } else {
          listEl.innerHTML = `<div style="color:#ef4444;">Erro ao calcular bitrate.</div>`;
        }
      } catch (e) {
        listEl.innerHTML = `<div style="color:#ef4444;">Erro na requisição: ${e.message}</div>`;
      }
    }

    async function abrirQCModal() {
      if (!currentPlan) return alert('Analise ou carregue um roteiro primeiro!');
      const modal = document.getElementById('qc-modal');
      const listEl = document.getElementById('qc-list');
      listEl.innerHTML = '<div style="color:var(--text-muted); text-align:center; padding:20px;">Executando auditoria QC (Quality Control) pré-render...</div>';
      modal.style.display = 'flex';

      try {
        const res = await fetch(`/api/video/qc?project_id=${currentPlan.project_id}`);
        const data = await res.json();
        if (data.ok && data.qc) {
          const qc = data.qc;
          const statusColor = qc.qc_score >= 90 ? '#10b981' : (qc.qc_score >= 70 ? '#f59e0b' : '#ef4444');
          let html = `
            <div style="background:var(--card-bg); border:1px solid var(--border); border-radius:8px; padding:12px; margin-bottom:12px; display:flex; justify-content:space-between; align-items:center;">
              <div>
                <div style="font-weight:700; color:#a855f7; font-size:0.95rem;">Auditoria de Conformidade Broadcast</div>
                <div style="font-size:0.82rem; color:var(--text-muted); margin-top:2px;">${qc.broadcast_standards} | Cenas inspecionadas: ${qc.total_scenes_checked}</div>
              </div>
              <div style="text-align:right;">
                <div style="font-weight:800; font-size:1.2rem; color:${statusColor};">${qc.qc_score}/100</div>
                <div style="font-size:0.72rem; color:var(--text-muted);">${qc.qc_status}</div>
              </div>
            </div>
            <div style="font-weight:700; font-size:0.9rem; margin-bottom:8px; color:var(--text-main);">Anomalias e Riscos Detectados (${qc.anomalies_found}):</div>
          `;
          if (qc.anomalies.length === 0) {
            html += '<div style="color:#10b981; padding:16px; text-align:center;">✨ Nenhum risco de quadro preto, congelamento ou flicker detectado! Vídeo 100% íntegro para broadcast.</div>';
          } else {
            qc.anomalies.forEach(a => {
              const borderCol = a.severity === 'CRITICAL' ? '#ef4444' : '#f59e0b';
              html += `
                <div style="background:rgba(168,85,247,0.06); border-left:4px solid ${borderCol}; border-radius:4px; padding:10px; margin-bottom:8px;">
                  <div style="display:flex; justify-content:space-between; font-weight:700; font-size:0.88rem; color:#f3e8ff;">
                    <span>Cena #${a.scene_index} (Aos ${a.timestamp}s) — ${a.type}</span>
                    <span style="color:${borderCol}; font-size:0.78rem;">[${a.severity}]</span>
                  </div>
                  <div style="font-size:0.82rem; color:var(--text-muted); margin-top:3px;">${a.description}</div>
                </div>
              `;
            });
          }
          listEl.innerHTML = html;
        } else {
          listEl.innerHTML = `<div style="color:#ef4444;">Erro ao executar QC.</div>`;
        }
      } catch (e) {
        listEl.innerHTML = `<div style="color:#ef4444;">Erro na requisição: ${e.message}</div>`;
      }
    }
    function fecharQCModal() {
      document.getElementById('qc-modal').style.display = 'none';
    }

    async function abrirDopplerModal() {
      const modal = document.getElementById('doppler-modal');
      modal.style.display = 'flex';
      calcularDopplerCustom();
    }
    function fecharDopplerModal() {
      document.getElementById('doppler-modal').style.display = 'none';
    }
    async function calcularDopplerCustom() {
      const spd = document.getElementById('doppler-speed') ? document.getElementById('doppler-speed').value : '140';
      const dir = document.getElementById('doppler-dir') ? document.getElementById('doppler-dir').value : 'left_to_right';
      const contentEl = document.getElementById('doppler-content');
      contentEl.innerHTML = '<div style="color:var(--text-muted); text-align:center; padding:10px;">Calculando física acústica Doppler 3D...</div>';

      try {
        const res = await fetch(`/api/audio/doppler/calculate?speed=${spd}&direction=${dir}`);
        const data = await res.json();
        if (data.ok && data.doppler) {
          const d = data.doppler;
          contentEl.innerHTML = `
            <div style="background:var(--card-bg); border:1px solid var(--border); border-radius:8px; padding:12px; margin-bottom:12px;">
              <div style="display:flex; justify-content:space-between; font-weight:700; color:#06b6d4;">
                <span>Variação de Pitch de Aproximação:</span>
                <span style="color:#cffafe;">+${Math.round((d.approach_pitch_ratio - 1) * 100)}% (${d.approach_pitch_ratio}x)</span>
              </div>
              <div style="display:flex; justify-content:space-between; font-weight:700; color:#06b6d4; margin-top:4px;">
                <span>Variação de Pitch de Afastamento:</span>
                <span style="color:#cffafe;">-${Math.round((1 - d.recede_pitch_ratio) * 100)}% (${d.recede_pitch_ratio}x)</span>
              </div>
              <div style="font-size:0.8rem; color:var(--text-muted); margin-top:6px;">
                Trajetória espacial: Pan de <b>${d.start_pan === -1 ? 'Esquerda' : 'Direita'}</b> para <b>${d.end_pan === 1 ? 'Direita' : 'Esquerda'}</b>.
              </div>
            </div>
            <div style="font-weight:700; font-size:0.88rem; margin-bottom:6px; color:var(--text-main);">Filtro FFmpeg 3D Doppler:</div>
            <textarea readonly style="width:100%; height:70px; background:#0f172a; border:1px solid var(--border); border-radius:6px; color:#a5f3fc; font-size:0.8rem; padding:8px; font-family:monospace; resize:none;">${d.ffmpeg_filter}</textarea>
          `;
        }
      } catch (e) {
        contentEl.innerHTML = `<div style="color:#ef4444;">Erro ao calcular Doppler: ${e.message}</div>`;
      }
    }

    async function abrirDropoffModal() {
      if (!currentPlan) return alert('Analise ou carregue um roteiro primeiro!');
      const modal = document.getElementById('dropoff-modal');
      const listEl = document.getElementById('dropoff-list');
      listEl.innerHTML = '<div style="color:var(--text-muted); text-align:center; padding:20px;">Modelando curva preditiva de abandono de audiência...</div>';
      modal.style.display = 'flex';

      try {
        const res = await fetch(`/api/audience/dropoff/predict?project_id=${currentPlan.project_id}`);
        const data = await res.json();
        if (data.ok && data.dropoff) {
          const d = data.dropoff;
          let html = `
            <div style="background:var(--card-bg); border:1px solid var(--border); border-radius:8px; padding:12px; margin-bottom:12px; display:flex; justify-content:space-between; align-items:center;">
              <div>
                <div style="font-weight:700; color:#eab308; font-size:0.95rem;">Retenção Média Estimada</div>
                <div style="font-size:0.82rem; color:var(--text-muted); margin-top:2px;">Benchmark: ${d.benchmark_status} | Duração: ${d.total_duration}s</div>
              </div>
              <div style="font-weight:800; font-size:1.3rem; color:#fef9c3;">${d.predicted_average_retention}</div>
            </div>
            <div style="font-weight:700; font-size:0.9rem; margin-bottom:8px; color:var(--text-main);">Pontos Críticos de Risco de Queda (${d.dropoff_risks_count}):</div>
          `;
          if (d.dropoff_hotspots.length === 0) {
            html += '<div style="color:#10b981; padding:16px; text-align:center;">✨ Excelente! Roteiro dinâmico e sem zonas de tédio detectadas.</div>';
          } else {
            d.dropoff_hotspots.forEach(h => {
              html += `
                <div style="background:rgba(234,179,8,0.06); border:1px solid rgba(234,179,8,0.25); border-radius:6px; padding:10px; margin-bottom:8px;">
                  <div style="display:flex; justify-content:space-between; font-weight:700; font-size:0.88rem; color:#fef9c3;">
                    <span>⏱️ Aos ${h.timestamp}s (Cena #${h.scene_index})</span>
                    <span style="color:#ef4444;">Risco de Abandono: ${h.risk_percent}%</span>
                  </div>
                  <div style="font-size:0.82rem; color:var(--text-muted); margin-top:3px;">Causa: ${h.cause}</div>
                  <div style="font-size:0.82rem; color:#86efac; margin-top:4px;">💡 Solução Recomendada: <b>${h.remedy}</b></div>
                </div>
              `;
            });
          }
          listEl.innerHTML = html;
        } else {
          listEl.innerHTML = `<div style="color:#ef4444;">Erro ao prever abandono.</div>`;
        }
      } catch (e) {
        listEl.innerHTML = `<div style="color:#ef4444;">Erro na requisição: ${e.message}</div>`;
      }
    }
    function fecharDropoffModal() {
      document.getElementById('dropoff-modal').style.display = 'none';
    }

    async function abrirDynamicSubtitlesModal() {
      if (!currentPlan) return alert('Analise ou carregue um roteiro primeiro!');
      const modal = document.getElementById('dynamic-subtitles-modal');
      modal.style.display = 'flex';
      gerarSubtitlesASS('hormozi_bold_yellow');
    }
    function fecharDynamicSubtitlesModal() {
      document.getElementById('dynamic-subtitles-modal').style.display = 'none';
    }
    async function gerarSubtitlesASS(styleKey) {
      const contentEl = document.getElementById('dynamic-subtitles-content');
      contentEl.innerHTML = '<div style="color:var(--text-muted); text-align:center; padding:15px;">Gerando script .ASS com tags de karaoke e realce palavra por palavra...</div>';
      try {
        const res = await fetch(`/api/subtitles/karaoke/generate?project_id=${currentPlan.project_id}&style=${styleKey}`);
        const data = await res.json();
        if (data.ok && data.subtitles) {
          const sub = data.subtitles;
          const st = sub.style_details;
          contentEl.innerHTML = `
            <div style="background:var(--card-bg); border:1px solid var(--border); border-radius:8px; padding:12px; margin-bottom:12px;">
              <div style="display:flex; justify-content:space-between; align-items:center;">
                <span style="font-weight:700; color:#ec4899;">Estilo Selecionado: ${st.name}</span>
                <span style="font-size:0.8rem; color:#fce7f3; font-family:monospace;">${st.font_name} ${st.font_size}pt</span>
              </div>
              <div style="font-size:0.8rem; color:var(--text-muted); margin-top:4px;">
                Cores ASS: Primária ${st.primary_color} | Realce Ativo ${st.highlight_color} | Borda: ${st.outline_width}px
              </div>
            </div>
            <div style="font-weight:700; font-size:0.88rem; margin-bottom:6px; color:var(--text-main);">Escolha o Estilo Visual de Realce:</div>
            <div style="display:flex; gap:8px; flex-wrap:wrap; margin-bottom:12px;">
              <button class="btn btn-secondary" style="font-size:0.8rem;" onclick="gerarSubtitlesASS('hormozi_bold_yellow')">Hormozi Yellow</button>
              <button class="btn btn-secondary" style="font-size:0.8rem;" onclick="gerarSubtitlesASS('mrbeast_impact_green')">MrBeast Green</button>
              <button class="btn btn-secondary" style="font-size:0.8rem;" onclick="gerarSubtitlesASS('cyberpunk_neon_cyan')">Cyberpunk Cyan</button>
              <button class="btn btn-secondary" style="font-size:0.8rem;" onclick="gerarSubtitlesASS('minimal_cinema_white')">Minimal Cinema</button>
            </div>
            <div style="font-weight:700; font-size:0.88rem; margin-bottom:6px; color:var(--text-main);">Prévia do Script .ASS Gerado (${sub.total_dialogue_events} falas):</div>
            <textarea readonly style="width:100%; height:110px; background:#0f172a; border:1px solid var(--border); border-radius:6px; color:#fbcfe8; font-size:0.75rem; padding:8px; font-family:monospace; resize:none;">${sub.ass_content}</textarea>
          `;
        }
      } catch (e) {
        contentEl.innerHTML = `<div style="color:#ef4444;">Erro ao gerar legendas: ${e.message}</div>`;
      }
    }

    async function abrirBPMAlignerModal() {
      if (!currentPlan) return alert('Analise ou carregue um roteiro primeiro!');
      const modal = document.getElementById('bpm-aligner-modal');
      modal.style.display = 'flex';
    }
    function fecharBPMAlignerModal() {
      document.getElementById('bpm-aligner-modal').style.display = 'none';
    }
    async function aplicarAlinhamentoBPM() {
      if (!currentPlan) return;
      const bpmVal = document.getElementById('bpm-input') ? document.getElementById('bpm-input').value : '120';
      const modeVal = document.getElementById('bpm-mode') ? document.getElementById('bpm-mode').value : 'full_measure';
      const listEl = document.getElementById('bpm-aligner-list');
      listEl.innerHTML = '<div style="color:var(--text-muted); text-align:center; padding:15px;">Quantizando cortes de cena na grade de compasso...</div>';
      try {
        const res = await fetch('/api/bpm/align', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ project_id: currentPlan.project_id, bpm: parseFloat(bpmVal), alignment_mode: modeVal })
        });
        const data = await res.json();
        if (data.ok && data.alignment) {
          const al = data.alignment;
          let html = `
            <div style="background:var(--card-bg); border:1px solid var(--border); border-radius:8px; padding:12px; margin-bottom:12px;">
              <div style="display:flex; justify-content:space-between; font-weight:700; color:#8b5cf6;">
                <span>Grade Musical: ${al.bpm} BPM (${al.alignment_mode})</span>
                <span>Intervalo: ${al.grid_interval_seconds}s</span>
              </div>
              <div style="font-size:0.82rem; color:var(--text-muted); margin-top:4px;">
                Duração Original: ${al.original_total_duration}s ➔ Nova Duração Alinhada: <b>${al.aligned_total_duration}s</b>
              </div>
            </div>
            <div style="font-weight:700; font-size:0.88rem; margin-bottom:8px; color:var(--text-main);">Ajustes de Cena Quantizados:</div>
          `;
          al.adjustments.forEach(adj => {
            html += `
              <div style="background:rgba(139,92,246,0.06); border:1px solid rgba(139,92,246,0.25); border-radius:6px; padding:8px 12px; margin-bottom:6px; display:flex; justify-content:space-between; font-size:0.85rem;">
                <span>Cena #${adj.scene_index}: <b>${adj.original_duration}s</b> ➔ <b style="color:#c4b5fd;">${adj.aligned_duration}s</b></span>
                <span style="color:${adj.delta >= 0 ? '#86efac' : '#fca5a5'}; font-size:0.8rem;">${adj.delta >= 0 ? '+' : ''}${adj.delta}s (${adj.measure_units} compassos)</span>
              </div>
            `;
          });
          listEl.innerHTML = html;
          showStatus(`Cenas quantizadas a ${al.bpm} BPM com sucesso!`, '#10b981');
        }
      } catch (e) {
        listEl.innerHTML = `<div style="color:#ef4444;">Erro ao quantizar BPM: ${e.message}</div>`;
      }
    }

    async function abrirTensionCurveModal() {
      if (!currentPlan) return alert('Analise ou carregue um roteiro primeiro!');
      const modal = document.getElementById('tension-curve-modal');
      const listEl = document.getElementById('tension-curve-list');
      listEl.innerHTML = '<div style="color:var(--text-muted); text-align:center; padding:20px;">Mapeando curva de tensão narrativa de 3 atos...</div>';
      modal.style.display = 'flex';

      try {
        const res = await fetch(`/api/narrative/tension/audit?project_id=${currentPlan.project_id}`);
        const data = await res.json();
        if (data.ok && data.narrative) {
          const n = data.narrative;
          let html = `
            <div style="background:var(--card-bg); border:1px solid var(--border); border-radius:8px; padding:12px; margin-bottom:12px; display:flex; justify-content:space-between; align-items:center;">
              <div>
                <div style="font-weight:700; color:#f43f5e; font-size:0.95rem;">Arco Dramático (Jornada do Herói)</div>
                <div style="font-size:0.8rem; color:var(--text-muted); margin-top:2px;">Tensão Média: ${n.average_tension}/100 | Clímax: Cena #${n.climax_scene_index} (${n.peak_tension_score}/100)</div>
              </div>
              <span style="font-weight:800; font-size:0.95rem; color:${n.narrative_health === 'EXCELLENT' ? '#10b981' : '#f59e0b'};">${n.narrative_health}</span>
            </div>
            <div style="font-weight:700; font-size:0.88rem; margin-bottom:8px; color:var(--text-main);">Progressão Dramática Cena a Cena:</div>
          `;
          n.tension_curve.forEach(pt => {
            html += `
              <div style="background:rgba(244,63,94,0.06); border:1px solid rgba(244,63,94,0.25); border-radius:6px; padding:10px; margin-bottom:8px;">
                <div style="display:flex; justify-content:space-between; font-weight:700; font-size:0.88rem; color:#ffe4e6;">
                  <span>Cena #${pt.scene_index} — ${pt.act}</span>
                  <span style="color:#f43f5e;">Tensão: ${pt.tension_score}/100</span>
                </div>
                <div style="width:100%; height:6px; background:#1e293b; border-radius:3px; margin-top:6px; overflow:hidden;">
                  <div style="width:${pt.tension_score}%; height:100%; background:linear-gradient(90deg, #f43f5e, #fb7185); border-radius:3px;"></div>
                </div>
              </div>
            `;
          });
          listEl.innerHTML = html;
        }
      } catch (e) {
        listEl.innerHTML = `<div style="color:#ef4444;">Erro ao auditar tensão: ${e.message}</div>`;
      }
    }
    function fecharTensionCurveModal() {
      document.getElementById('tension-curve-modal').style.display = 'none';
    }

    async function abrirWatermarkModal() {
      const modal = document.getElementById('watermark-modal');
      modal.style.display = 'flex';
    }
    function fecharWatermarkModal() {
      document.getElementById('watermark-modal').style.display = 'none';
    }
    async function aplicarWatermarkConfig() {
      if (!currentPlan) return alert('Analise ou carregue um roteiro primeiro!');
      const posVal = document.getElementById('wm-pos') ? document.getElementById('wm-pos').value : 'bottom_right';
      const opVal = document.getElementById('wm-opacity') ? document.getElementById('wm-opacity').value : '0.55';
      const pathVal = document.getElementById('wm-path') ? document.getElementById('wm-path').value : 'assets/branding/logo_watermark.png';

      try {
        const res = await fetch('/api/watermark/apply', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            project_id: currentPlan.project_id,
            position: posVal,
            opacity: parseFloat(opVal),
            watermark_path: pathVal
          })
        });
        const data = await res.json();
        if (data.ok) {
          alert('Marca d\'água configurada com sucesso com margens seguras e fade-in gradual.');
          fecharWatermarkModal();
        }
      } catch (e) {
        alert('Erro ao aplicar marca d\'água: ' + e.message);
      }
    }

    async function abrirHDRToneMapModal() {
      if (!currentPlan) return alert('Analise ou carregue um roteiro primeiro!');
      const modal = document.getElementById('hdr-tonemap-modal');
      const listEl = document.getElementById('hdr-tonemap-list');
      listEl.innerHTML = '<div style="color:var(--text-muted); text-align:center; padding:15px;">Carregando algoritmos de Tone Mapping HDR Rec.709...</div>';
      modal.style.display = 'flex';

      try {
        const res = await fetch('/api/hdr/presets');
        const data = await res.json();
        if (data.ok && data.presets) {
          let html = '<div style="display:flex; flex-direction:column; gap:10px;">';
          for (const [key, p] of Object.entries(data.presets)) {
            html += `
              <div style="background:var(--card-bg); border:1px solid var(--border); border-radius:8px; padding:12px; display:flex; justify-content:space-between; align-items:center;">
                <div style="flex:1;">
                  <div style="font-weight:700; color:#fef3c7; font-size:0.95rem;">${p.name}</div>
                  <div style="font-size:0.82rem; color:var(--text-muted); margin-top:3px;">${p.description}</div>
                  <div style="font-size:0.75rem; color:#f59e0b; margin-top:4px; font-family:monospace;">Curva: ${p.tonemap} | Desaturação: ${p.desat} | Pico NPL: ${p.peak}</div>
                </div>
                <button class="btn" style="background:#f59e0b; color:#0f172a; font-weight:700; margin-left:12px;" onclick="aplicarHDRPreset('${key}')">Aplicar</button>
              </div>
            `;
          }
          html += '</div>';
          listEl.innerHTML = html;
        }
      } catch (e) {
        listEl.innerHTML = `<div style="color:#ef4444;">Erro ao carregar HDR presets: ${e.message}</div>`;
      }
    }
    function fecharHDRToneMapModal() {
      document.getElementById('hdr-tonemap-modal').style.display = 'none';
    }
    async function aplicarHDRPreset(presetKey) {
      if (!currentPlan) return;
      showStatus('Configurando tone mapping HDR Rec.709...', '#f59e0b');
      try {
        const res = await fetch('/api/hdr/apply', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ project_id: currentPlan.project_id, preset: presetKey })
        });
        const data = await res.json();
        if (data.ok) {
          showStatus(`Tone mapping ${presetKey} aplicado com sucesso!`, '#10b981');
          alert(`Sucesso!\n\nAlgoritmo de Tone Mapping "${presetKey}" configurado no renderizador zscale para compatibilidade universal SDR Rec.709.`);
          fecharHDRToneMapModal();
        }
      } catch (e) {
        alert('Erro ao aplicar: ' + e.message);
      }
    }

    async function abrirFaceDetectorModal() {
      if (!currentPlan) return alert('Analise ou carregue um roteiro primeiro!');
      const modal = document.getElementById('face-detector-modal');
      const listEl = document.getElementById('face-detector-list');
      listEl.innerHTML = '<div style="color:var(--text-muted); text-align:center; padding:20px;">Detectando expressões faciais de alto CTR e alinhando aos terços...</div>';
      modal.style.display = 'flex';

      try {
        const res = await fetch(`/api/thumbnail/face/detect?project_id=${currentPlan.project_id}`);
        const data = await res.json();
        if (data.ok && data.faces) {
          const f = data.faces;
          let html = `
            <div style="background:var(--card-bg); border:1px solid var(--border); border-radius:8px; padding:12px; margin-bottom:12px; display:flex; justify-content:space-between; align-items:center;">
              <span style="font-weight:700; color:#38bdf8;">Enquadramento de Miniatura:</span>
              <span style="font-weight:800; color:#e0f2fe;">${f.framing_standard}</span>
            </div>
            <div style="font-weight:700; font-size:0.9rem; margin-bottom:8px; color:var(--text-main);">Melhores Momentos Faciais para Thumbnail (${f.top_thumbnail_candidates.length}):</div>
          `;
          f.top_thumbnail_candidates.forEach(c => {
            html += `
              <div style="background:rgba(56,189,248,0.06); border:1px solid rgba(56,189,248,0.25); border-radius:6px; padding:12px; margin-bottom:10px;">
                <div style="display:flex; justify-content:space-between; font-weight:700; font-size:0.92rem; color:#e0f2fe;">
                  <span>Candidato #${c.candidate_index} — Cena #${c.scene_index} (Aos ${c.timestamp}s)</span>
                  <span style="color:#38bdf8;">Expressão: ${c.expression_type.toUpperCase()} (${c.ctr_expressiveness_score}% CTR)</span>
                </div>
                <div style="font-size:0.82rem; color:var(--text-muted); margin-top:4px;">
                  Âncora: <b>${c.rule_of_thirds_anchor === 'right_third' ? 'Terço Direito' : 'Terço Esquerdo'}</b> (deixa espaço livre para título)
                </div>
                <div style="font-size:0.75rem; color:#bae6fd; font-family:monospace; margin-top:4px;">
                  Filtro Crop: ${c.suggested_crop_filter} | Contraste: ${c.contrast_boost_filter}
                </div>
              </div>
            `;
          });
          listEl.innerHTML = html;
        }
      } catch (e) {
        listEl.innerHTML = `<div style="color:#ef4444;">Erro ao detectar rostos: ${e.message}</div>`;
      }
    }
    function fecharFaceDetectorModal() {
      document.getElementById('face-detector-modal').style.display = 'none';
    }

    async function abrirSoundtrackLoopModal() {
      if (!currentPlan) return alert('Analise ou carregue um roteiro primeiro!');
      const modal = document.getElementById('soundtrack-loop-modal');
      modal.style.display = 'flex';
      aplicarLoopStretcher();
    }
    function fecharSoundtrackLoopModal() {
      document.getElementById('soundtrack-loop-modal').style.display = 'none';
    }
    async function aplicarLoopStretcher() {
      const musicDur = document.getElementById('music-dur-input') ? document.getElementById('music-dur-input').value : '90';
      const crossVal = document.getElementById('music-cross-input') ? document.getElementById('music-cross-input').value : '3.0';
      const contentEl = document.getElementById('soundtrack-loop-content');
      contentEl.innerHTML = '<div style="color:var(--text-muted); text-align:center; padding:15px;">Calculando loops perfeitos sem cortes bruscos...</div>';

      try {
        const res = await fetch(`/api/soundtrack/loop/calculate?project_id=${currentPlan.project_id}&music_duration=${musicDur}&crossfade=${crossVal}`);
        const data = await res.json();
        if (data.ok && data.loop_plan) {
          const lp = data.loop_plan;
          contentEl.innerHTML = `
            <div style="background:var(--card-bg); border:1px solid var(--border); border-radius:8px; padding:12px; margin-bottom:12px;">
              <div style="display:flex; justify-content:space-between; font-weight:700; color:#a855f7;">
                <span>Duração do Vídeo: ${lp.video_duration}s</span>
                <span>Duração da Música: ${lp.soundtrack_duration}s</span>
              </div>
              <div style="font-size:0.85rem; color:#f5d0fe; margin-top:6px;">
                ${lp.needs_loop ? `🔁 Necessário <b>${lp.loops_required} loops</b> com <b>${lp.seamless_transitions_count} transições acrossfade (${lp.crossfade_seconds}s)</b>.` : '✨ A música cobre todo o vídeo sem necessidade de loop!'}
              </div>
            </div>
            <div style="font-weight:700; font-size:0.88rem; margin-bottom:6px; color:var(--text-main);">Filtro de Áudio FFmpeg Gerado:</div>
            <textarea readonly style="width:100%; height:75px; background:#0f172a; border:1px solid var(--border); border-radius:6px; color:#f5d0fe; font-size:0.78rem; padding:8px; font-family:monospace; resize:none;">${lp.ffmpeg_filter}</textarea>
          `;
        }
      } catch (e) {
        contentEl.innerHTML = `<div style="color:#ef4444;">Erro ao calcular loop: ${e.message}</div>`;
      }
    }

    async function abrirCutpackModal() {
      if (!currentPlan) return alert('Analise ou carregue um roteiro primeiro!');
      const modal = document.getElementById('cutpack-modal');
      const listEl = document.getElementById('cutpack-list');
      listEl.innerHTML = '<div style="color:var(--text-muted); text-align:center; padding:20px;">Gerando matriz de entregáveis multiformato para redes sociais...</div>';
      modal.style.display = 'flex';

      try {
        const res = await fetch(`/api/cutpack/plan?project_id=${currentPlan.project_id}`);
        const data = await res.json();
        if (data.ok && data.cutpack) {
          const cp = data.cutpack;
          let html = `
            <div style="background:var(--card-bg); border:1px solid var(--border); border-radius:8px; padding:12px; margin-bottom:12px; display:flex; justify-content:space-between; align-items:center;">
              <span style="font-weight:700; color:#06b6d4;">Matriz Transmídia:</span>
              <span style="font-weight:800; color:#cffafe;">${cp.total_cutpack_deliverables} formatos prontos para render em lote</span>
            </div>
            <div style="font-weight:700; font-size:0.9rem; margin-bottom:8px; color:var(--text-main);">Entregáveis Otimizados por Rede Social:</div>
          `;
          cp.jobs.forEach(j => {
            html += `
              <div style="background:rgba(6,182,212,0.06); border:1px solid rgba(6,182,212,0.25); border-radius:6px; padding:10px 12px; margin-bottom:8px;">
                <div style="display:flex; justify-content:space-between; font-weight:700; font-size:0.88rem; color:#cffafe;">
                  <span>${j.platform} (${j.aspect_ratio})</span>
                  <span style="color:#06b6d4;">${j.resolution} — ${j.duration_seconds}s</span>
                </div>
                <div style="font-size:0.75rem; color:#94a3b8; font-family:monospace; margin-top:4px;">
                  Arquivo: ${j.target_filename}
                </div>
              </div>
            `;
          });
          listEl.innerHTML = html;
        }
      } catch (e) {
        listEl.innerHTML = `<div style="color:#ef4444;">Erro ao gerar cutpack: ${e.message}</div>`;
      }
    }
    function fecharCutpackModal() {
      document.getElementById('cutpack-modal').style.display = 'none';
    }

    async function abrirLowerThirdsModal() {
      if (!currentPlan) return alert('Analise ou carregue um roteiro primeiro!');
      const modal = document.getElementById('lower-thirds-modal');
      modal.style.display = 'flex';
      gerarLowerThirdsPorEstilo('tech_cyber_bar');
    }
    function fecharLowerThirdsModal() {
      document.getElementById('lower-thirds-modal').style.display = 'none';
    }
    async function gerarLowerThirdsPorEstilo(styleKey) {
      const contentEl = document.getElementById('lower-thirds-content');
      contentEl.innerHTML = '<div style="color:var(--text-muted); text-align:center; padding:15px;">Gerando grafismos animados Lower Thirds...</div>';

      try {
        const res = await fetch(`/api/lower_thirds/generate?project_id=${currentPlan.project_id}&style=${styleKey}`);
        const data = await res.json();
        if (data.ok && data.lower_thirds) {
          const lt = data.lower_thirds;
          let html = `
            <div style="font-weight:700; font-size:0.88rem; margin-bottom:8px; color:var(--text-main);">Escolha o Estilo de Motion Graphics:</div>
            <div style="display:flex; gap:8px; flex-wrap:wrap; margin-bottom:12px;">
              <button class="btn btn-secondary" style="font-size:0.8rem;" onclick="gerarLowerThirdsPorEstilo('tech_cyber_bar')">Tech Cyber</button>
              <button class="btn btn-secondary" style="font-size:0.8rem;" onclick="gerarLowerThirdsPorEstilo('broadcast_news_slate')">Broadcast News</button>
              <button class="btn btn-secondary" style="font-size:0.8rem;" onclick="gerarLowerThirdsPorEstilo('documentary_minimal')">Documentary</button>
              <button class="btn btn-secondary" style="font-size:0.8rem;" onclick="gerarLowerThirdsPorEstilo('gold_luxury_serif')">Gold Luxury</button>
            </div>
            <div style="font-weight:700; font-size:0.88rem; margin-bottom:8px; color:var(--text-main);">Grafismos Programados na Timeline (${lt.total_lower_thirds}):</div>
          `;
          lt.overlays.forEach(o => {
            html += `
              <div style="background:rgba(244,63,94,0.06); border:1px solid rgba(244,63,94,0.25); border-radius:6px; padding:10px; margin-bottom:8px;">
                <div style="display:flex; justify-content:space-between; font-weight:700; font-size:0.88rem; color:#ffe4e6;">
                  <span>"${o.title}" ${o.subtitle ? '— ' + o.subtitle : ''}</span>
                  <span style="color:#f43f5e;">⏱️ ${o.start_time}s até ${o.end_time}s (${o.duration}s)</span>
                </div>
                <div style="font-size:0.75rem; color:#94a3b8; font-family:monospace; margin-top:4px;">
                  FFmpeg: ${o.ffmpeg_filter}
                </div>
              </div>
            `;
          });
          contentEl.innerHTML = html;
        }
      } catch (e) {
        contentEl.innerHTML = `<div style="color:#ef4444;">Erro ao gerar Lower Thirds: ${e.message}</div>`;
      }
    }

    async function abrirSymmetryModal() {
      if (!currentPlan) return alert('Analise ou carregue um roteiro primeiro!');
      const modal = document.getElementById('symmetry-modal');
      const listEl = document.getElementById('symmetry-list');
      listEl.innerHTML = '<div style="color:var(--text-muted); text-align:center; padding:20px;">Avaliando equilíbrio visual e simetria cinematográfica...</div>';
      modal.style.display = 'flex';

      try {
        const res = await fetch(`/api/aesthetic/symmetry/audit?project_id=${currentPlan.project_id}`);
        const data = await res.json();
        if (data.ok && data.aesthetic) {
          const a = data.aesthetic;
          let html = `
            <div style="background:var(--card-bg); border:1px solid var(--border); border-radius:8px; padding:12px; margin-bottom:12px; display:flex; justify-content:space-between; align-items:center;">
              <div>
                <div style="font-weight:700; color:#10b981; font-size:0.95rem;">Auditoria Estética de Simetria</div>
                <div style="font-size:0.82rem; color:var(--text-muted); margin-top:2px;">${a.composition_philosophy}</div>
              </div>
              <div style="text-align:right;">
                <div style="font-weight:800; font-size:1.2rem; color:#86efac;">${a.average_aesthetic_score}/100</div>
                <div style="font-size:0.72rem; color:var(--text-muted);">${a.overall_aesthetic_grade}</div>
              </div>
            </div>
            <div style="font-weight:700; font-size:0.9rem; margin-bottom:8px; color:var(--text-main);">Avaliação Cena a Cena (${a.total_scenes_audited}):</div>
          `;
          a.evaluations.forEach(ev => {
            html += `
              <div style="background:rgba(16,185,129,0.06); border:1px solid rgba(16,185,129,0.25); border-radius:6px; padding:10px; margin-bottom:8px;">
                <div style="display:flex; justify-content:space-between; font-weight:700; font-size:0.88rem; color:#d1fae5;">
                  <span>Cena #${ev.scene_index} — ${ev.composition_style}</span>
                  <span style="color:#10b981;">${ev.composition_score}/100</span>
                </div>
                <div style="font-size:0.8rem; color:var(--text-muted); margin-top:3px;">${ev.recommendation}</div>
              </div>
            `;
          });
          listEl.innerHTML = html;
        }
      } catch (e) {
        listEl.innerHTML = `<div style="color:#ef4444;">Erro ao auditar simetria: ${e.message}</div>`;
      }
    }
    function fecharSymmetryModal() {
      document.getElementById('symmetry-modal').style.display = 'none';
    }

    async function abrirSurroundModal() {
      const modal = document.getElementById('surround-modal');
      modal.style.display = 'flex';
      calcularSurroundPreview();
    }
    function fecharSurroundModal() {
      document.getElementById('surround-modal').style.display = 'none';
    }
    async function calcularSurroundPreview() {
      const boostVal = document.getElementById('surround-boost') ? document.getElementById('surround-boost').value : '2.0';
      const contentEl = document.getElementById('surround-content');
      contentEl.innerHTML = '<div style="color:var(--text-muted); text-align:center; padding:15px;">Gerando matriz de descorrelação surround 5.1...</div>';

      try {
        const res = await fetch(`/api/audio/surround51/calculate?boost=${boostVal}`);
        const data = await res.json();
        if (data.ok && data.surround) {
          const s = data.surround;
          contentEl.innerHTML = `
            <div style="background:var(--card-bg); border:1px solid var(--border); border-radius:8px; padding:12px; margin-bottom:12px;">
              <div style="display:flex; justify-content:space-between; font-weight:700; color:#6366f1;">
                <span>Padrão Multicanal: ${s.standard}</span>
                <span style="color:#e0e7ff;">${s.channels_count} Canais (${s.channel_layout})</span>
              </div>
              <div style="font-size:0.8rem; color:var(--text-muted); margin-top:4px;">
                Corte LFE: ${s.lfe_cutoff_hz}Hz | Delay Traseiro: ${s.surround_delay_ms}ms | Ganho Vocal Central: +${s.center_boost_db}dB
              </div>
            </div>
            <div style="font-weight:700; font-size:0.88rem; margin-bottom:6px; color:var(--text-main);">Matriz de Canais FFmpeg:</div>
            <textarea readonly style="width:100%; height:75px; background:#0f172a; border:1px solid var(--border); border-radius:6px; color:#c7d2fe; font-size:0.75rem; padding:8px; font-family:monospace; resize:none;">${s.ffmpeg_audio_filter}</textarea>
          `;
        }
      } catch (e) {
        contentEl.innerHTML = `<div style="color:#ef4444;">Erro ao calcular surround: ${e.message}</div>`;
      }
    }
    async function aplicarSurroundUpmix() {
      if (!currentPlan) return alert('Analise ou carregue um roteiro primeiro!');
      const boostVal = document.getElementById('surround-boost') ? document.getElementById('surround-boost').value : '2.0';
      try {
        const res = await fetch('/api/audio/surround51/apply', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ project_id: currentPlan.project_id, boost: parseFloat(boostVal) })
        });
        const data = await res.json();
        if (data.ok) {
          alert('Upmix surround 5.1 configurado com sucesso para a exportação de áudio master!');
          fecharSurroundModal();
        }
      } catch (e) {
        alert('Erro ao aplicar: ' + e.message);
      }
    }

    async function abrirPaletteModal() {
      if (!currentPlan) return alert('Analise ou carregue um roteiro primeiro!');
      const modal = document.getElementById('palette-modal');
      const contentEl = document.getElementById('palette-content');
      contentEl.innerHTML = '<div style="color:var(--text-muted); text-align:center; padding:20px;">Extraindo paleta de cores cromática e psicologia do humor...</div>';
      modal.style.display = 'flex';

      try {
        const res = await fetch(`/api/palette/mood/extract?project_id=${currentPlan.project_id}`);
        const data = await res.json();
        if (data.ok && data.palette) {
          const p = data.palette;
          let swatchesHtml = '<div style="display:flex; height:65px; border-radius:8px; overflow:hidden; margin:14px 0; border:1px solid var(--border);">';
          p.hex_colors.forEach(col => {
            swatchesHtml += `
              <div style="flex:1; background:${col}; display:flex; align-items:flex-end; justify-content:center; padding-bottom:6px;">
                <span style="background:rgba(0,0,0,0.65); color:#fff; font-size:0.65rem; padding:2px 4px; border-radius:3px; font-family:monospace;">${col}</span>
              </div>
            `;
          });
          swatchesHtml += '</div>';

          contentEl.innerHTML = `
            <div style="background:var(--card-bg); border:1px solid var(--border); border-radius:8px; padding:14px;">
              <div style="font-weight:700; color:#ec4899; font-size:1.05rem;">${p.palette_name}</div>
              <div style="font-size:0.85rem; color:var(--text-muted); margin-top:3px;">Atmosfera: <b>${p.mood}</b></div>
              ${swatchesHtml}
              <div style="font-size:0.8rem; color:var(--text-muted);">
                Essa paleta cromática foi calculada a partir dos termos narrativos e da densidade temática do roteiro para orientar a correção de cor (LUTs) e o design de miniaturas.
              </div>
            </div>
          `;
        }
      } catch (e) {
        contentEl.innerHTML = `<div style="color:#ef4444;">Erro ao extrair paleta: ${e.message}</div>`;
      }
    }
    function fecharPaletteModal() {
      document.getElementById('palette-modal').style.display = 'none';
    }

    // NLE Exporter
    function abrirNLEModal() {
      if (!currentPlan) return alert('Analise ou carregue um roteiro primeiro!');
      document.getElementById('nle-modal').style.display = 'flex';
    }
    function fecharNLEModal() {
      document.getElementById('nle-modal').style.display = 'none';
    }
    async function exportarNLETimeline() {
      if (!currentPlan) return;
      const fps = document.getElementById('nle-fps') ? document.getElementById('nle-fps').value : '30';
      const resEl = document.getElementById('nle-result');
      resEl.innerHTML = '<div style="color:var(--text-muted); text-align:center;">Gerando EDL CMX 3600 e XML Final Cut/Premiere...</div>';
      try {
        const res = await fetch(`/api/nle/export?project_id=${currentPlan.project_id}&fps=${fps}`);
        const data = await res.json();
        if (data.ok && data.export) {
          const exp = data.export;
          resEl.innerHTML = `
            <div style="background:var(--card-bg); border:1px solid var(--border); border-radius:8px; padding:12px;">
              <div style="color:#22c55e; font-weight:700;">✅ Linhas do tempo geradas com sucesso!</div>
              <div style="font-size:0.85rem; color:var(--text-muted); margin:6px 0;">Cortes: ${exp.scene_count} cenas | Duração total: ${exp.total_duration_sec}s | Taxa: ${exp.fps} fps</div>
              <div style="margin-top:8px; font-size:0.8rem; font-family:monospace; color:#fde047; word-break:break-all;">
                📄 EDL: ${exp.files.cmx3600_edl}<br>
                🎞️ XML Premiere/DaVinci: ${exp.files.premiere_davinci_xml}
              </div>
            </div>
          `;
        } else {
          resEl.innerHTML = `<div style="color:#ef4444;">Erro: ${data.error || 'Falha ao exportar'}</div>`;
        }
      } catch (e) {
        resEl.innerHTML = `<div style="color:#ef4444;">Erro de conexão: ${e.message}</div>`;
      }
    }

    // Audio Ducking Sidechain
    function abrirDuckingModal() {
      document.getElementById('ducking-modal').style.display = 'flex';
      calcularDuckingPreview();
    }
    function fecharDuckingModal() {
      document.getElementById('ducking-modal').style.display = 'none';
    }
    async function calcularDuckingPreview() {
      const preset = document.getElementById('ducking-preset') ? document.getElementById('ducking-preset').value : 'broadcast_standard';
      const contentEl = document.getElementById('ducking-preview-content');
      contentEl.innerHTML = '<div style="color:var(--text-muted); text-align:center;">Calculando curva dinâmica de atenuação...</div>';
      try {
        const res = await fetch(`/api/audio/ducking/preview?preset=${preset}`);
        const data = await res.json();
        if (data.ok && data.ducking) {
          const d = data.ducking;
          contentEl.innerHTML = `
            <div style="background:var(--card-bg); border:1px solid var(--border); border-radius:8px; padding:12px;">
              <div style="font-weight:700; color:#14b8a6;">Preset: ${d.preset_applied}</div>
              <div style="font-size:0.85rem; color:var(--text-muted); margin:4px 0;">${d.config.description}</div>
              <div style="display:flex; gap:12px; margin-top:8px; font-size:0.8rem;">
                <span style="color:#67e8f9;">Atenuação: ${d.config.ducking_depth_db}dB</span>
                <span style="color:#a7f3d0;">Ataque: ${d.config.attack_ms}ms</span>
                <span style="color:#fde047;">Release: ${d.config.release_ms}ms</span>
                <span style="color:#c4b5fd;">Ratio: ${d.config.ratio}:1</span>
              </div>
              <div style="margin-top:10px; font-weight:700; font-size:0.8rem; color:var(--text-main);">Filtro FFmpeg Sidechain:</div>
              <textarea readonly style="width:100%; height:60px; background:#0f172a; border:1px solid var(--border); border-radius:6px; color:#5eead4; font-size:0.75rem; padding:6px; font-family:monospace; resize:none;">${d.sidechain_filter}</textarea>
            </div>
          `;
        }
      } catch (e) {
        contentEl.innerHTML = `<div style="color:#ef4444;">Erro ao calcular: ${e.message}</div>`;
      }
    }
    async function aplicarDuckingSidechain() {
      if (!currentPlan) return alert('Analise ou carregue um roteiro primeiro!');
      const preset = document.getElementById('ducking-preset') ? document.getElementById('ducking-preset').value : 'broadcast_standard';
      try {
        const res = await fetch('/api/audio/ducking/apply', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ project_id: currentPlan.project_id, preset: preset })
        });
        const data = await res.json();
        if (data.ok) {
          alert('Configuração de sidechain ducking aplicada com sucesso ao projeto!');
          fecharDuckingModal();
        }
      } catch (e) {
        alert('Erro ao aplicar: ' + e.message);
      }
    }

    // Thumbnails A/B Grid
    function abrirThumbnailsABModal() {
      if (!currentPlan) return alert('Analise ou carregue um roteiro primeiro!');
      document.getElementById('thumbnails-ab-modal').style.display = 'flex';
      gerarThumbnailsAB();
    }
    function fecharThumbnailsABModal() {
      document.getElementById('thumbnails-ab-modal').style.display = 'none';
    }
    async function gerarThumbnailsAB() {
      if (!currentPlan) return;
      const contentEl = document.getElementById('thumbnails-ab-content');
      contentEl.innerHTML = '<div style="color:var(--text-muted); text-align:center; padding:20px;">Gerando variações estratégicas A/B/C/D para CTR máximo...</div>';
      try {
        const res = await fetch(`/api/thumbnails/ab_grid?project_id=${currentPlan.project_id}`);
        const data = await res.json();
        if (data.ok && data.ab_grid) {
          const g = data.ab_grid;
          let cardsHtml = '<div style="display:grid; grid-template-columns:1fr 1fr; gap:12px; margin-top:10px;">';
          g.matrix.forEach(v => {
            cardsHtml += `
              <div style="background:var(--card-bg); border:1px solid var(--border); border-radius:8px; padding:12px; display:flex; flex-direction:column; gap:6px;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                  <span style="font-weight:700; color:#c084fc; font-size:0.9rem;">${v.name}</span>
                  <span style="background:rgba(34,197,94,0.2); color:#4ade80; font-size:0.75rem; padding:2px 6px; border-radius:4px; font-weight:700;">${v.estimated_ctr_boost}</span>
                </div>
                <div style="font-size:0.8rem; color:var(--text-muted);">${v.visual_style}</div>
                <div style="background:#111827; border:1px solid #374151; border-radius:6px; padding:6px; font-size:0.8rem; color:#fde047;">
                  Texto na Thumb: <b>"${v.suggested_overlay_text}"</b>
                </div>
                <div style="font-size:0.75rem; color:#9ca3af;">Público-Alvo: ${v.optimal_audience}</div>
              </div>
            `;
          });
          cardsHtml += '</div>';

          contentEl.innerHTML = `
            <div>
              <div style="font-size:0.85rem; color:var(--text-muted);">${g.testing_protocol}</div>
              ${cardsHtml}
            </div>
          `;
        }
      } catch (e) {
        contentEl.innerHTML = `<div style="color:#ef4444;">Erro ao gerar variações: ${e.message}</div>`;
      }
    }

    // Desktop Launcher
    async function gerarLauncherDesktop() {
      try {
        const res = await fetch('/api/launcher/deploy', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ port: 8765 })
        });
        const data = await res.json();
        if (data.ok && data.launcher) {
          alert(`⚡ Launchers de 1 clique gerados com sucesso!\n\nArquivo .BAT: ${data.launcher.batch_launcher}\nArquivo PowerShell: ${data.launcher.powershell_launcher}\n\nVocê pode dar um duplo clique no arquivo .bat para abrir o Drift AI Studio sem abrir o terminal!`);
        } else {
          alert('Erro ao gerar launcher: ' + (data.error || 'Falha'));
        }
      } catch (e) {
        alert('Erro ao requisitar launcher: ' + e.message);
      }
    }

    // CPU Thread Affinity & Thermal Governor
    function abrirAffinityModal() {
      document.getElementById('affinity-modal').style.display = 'flex';
      calcularAffinity();
    }
    function fecharAffinityModal() {
      document.getElementById('affinity-modal').style.display = 'none';
    }
    async function calcularAffinity() {
      const profile = document.getElementById('affinity-profile') ? document.getElementById('affinity-profile').value : 'balanced';
      const contentEl = document.getElementById('affinity-content');
      contentEl.innerHTML = '<div style="color:var(--text-muted); text-align:center;">Detectando topologia de núcleos e arrefecimento térmico...</div>';
      try {
        const res = await fetch(`/api/hardware/affinity/calculate?profile=${profile}`);
        const data = await res.json();
        if (data.ok && data.affinity) {
          const a = data.affinity;
          contentEl.innerHTML = `
            <div style="background:var(--card-bg); border:1px solid var(--border); border-radius:8px; padding:12px;">
              <div style="display:flex; justify-content:space-between; align-items:center;">
                <span style="font-weight:700; color:#38bdf8;">Núcleos do Sistema: ${a.total_cpu_cores}</span>
                <span style="background:rgba(56,189,248,0.2); color:#bae6fd; font-size:0.75rem; padding:2px 6px; border-radius:4px; font-weight:700;">${a.cooling_profile.toUpperCase()}</span>
              </div>
              <div style="display:flex; gap:16px; margin:8px 0; font-size:0.85rem;">
                <span style="color:#4ade80;">Render: ${a.allocated_render_threads} núcleos</span>
                <span style="color:#fde047;">Windows/UI Livre: ${a.reserved_os_cores} núcleos</span>
                <span style="color:#c084fc;">Máscara: ${a.hex_affinity_mask}</span>
              </div>
              <div style="font-size:0.8rem; color:var(--text-muted);">${a.summary}</div>
              <div style="margin-top:10px; font-size:0.75rem; font-family:monospace; color:#93c5fd; background:#0f172a; padding:6px; border-radius:4px;">
                FFmpeg Flags: ${a.ffmpeg_thread_args}
              </div>
            </div>
          `;
        }
      } catch (e) {
        contentEl.innerHTML = `<div style="color:#ef4444;">Erro ao calcular: ${e.message}</div>`;
      }
    }

    // Selective Rerender Cache
    function abrirSelectiveRerenderModal() {
      if (!currentPlan) return alert('Analise ou carregue um roteiro primeiro!');
      document.getElementById('selective-rerender-modal').style.display = 'flex';
      analisarRerenderSeletivo();
    }
    function fecharSelectiveRerenderModal() {
      document.getElementById('selective-rerender-modal').style.display = 'none';
    }
    async function analisarRerenderSeletivo() {
      if (!currentPlan) return;
      const contentEl = document.getElementById('selective-rerender-content');
      contentEl.innerHTML = '<div style="color:var(--text-muted); text-align:center;">Comparando fingerprints criptográficos SHA-256 da timeline...</div>';
      try {
        const res = await fetch(`/api/selective_rerender/analyze?project_id=${currentPlan.project_id}`);
        const data = await res.json();
        if (data.ok && data.rerender_analysis) {
          const r = data.rerender_analysis;
          contentEl.innerHTML = `
            <div style="background:var(--card-bg); border:1px solid var(--border); border-radius:8px; padding:12px;">
              <div style="display:flex; justify-content:space-between; align-items:center;">
                <span style="font-weight:700; color:#fbbf24;">Estratégia: ${r.stitch_strategy}</span>
                <span style="background:rgba(251,191,36,0.2); color:#fde047; font-size:0.85rem; padding:3px 8px; border-radius:4px; font-weight:700;">-${r.gpu_energy_saved_pct}% Uso GPU</span>
              </div>
              <div style="font-size:0.85rem; color:var(--text-muted); margin:8px 0;">
                Cenas Intactas em Cache: <b>${r.cached_scenes_count}</b> (${r.cached_duration_sec}s) | Exigem Render: <b>${r.rerender_scenes_count}</b> (${r.rerender_duration_sec}s)
              </div>
              <div style="font-size:0.8rem; color:#86efac; background:#064e3b; padding:8px; border-radius:6px;">
                💡 ${r.summary}
              </div>
            </div>
          `;
        }
      } catch (e) {
        contentEl.innerHTML = `<div style="color:#ef4444;">Erro ao analisar: ${e.message}</div>`;
      }
    }

    // Deadweight Pruner
    function abrirPrunerModal() {
      if (!currentPlan) return alert('Analise ou carregue um roteiro primeiro!');
      document.getElementById('pruner-modal').style.display = 'flex';
      analisarPodaInertes();
    }
    function fecharPrunerModal() {
      document.getElementById('pruner-modal').style.display = 'none';
    }
    async function analisarPodaInertes() {
      if (!currentPlan) return;
      const contentEl = document.getElementById('pruner-content');
      contentEl.innerHTML = '<div style="color:var(--text-muted); text-align:center;">Auditando cortes inertes e mídias vazias...</div>';
      try {
        const res = await fetch(`/api/pruner/analyze?project_id=${currentPlan.project_id}`);
        const data = await res.json();
        if (data.ok && data.pruner) {
          const p = data.pruner;
          let detailsHtml = '';
          if (p.pruned_details && p.pruned_details.length > 0) {
            detailsHtml = '<div style="margin-top:8px; font-size:0.75rem; color:#fca5a5;">Itens podados: ' + p.pruned_details.map(d => `Cena ${d.original_index} (${d.reason})`).join(', ') + '</div>';
          }
          contentEl.innerHTML = `
            <div style="background:var(--card-bg); border:1px solid var(--border); border-radius:8px; padding:12px;">
              <div style="font-weight:700; color:#f472b6;">Cenas Analisadas: ${p.initial_scenes_count} -> ${p.final_scenes_count}</div>
              <div style="font-size:0.85rem; color:var(--text-muted); margin:6px 0;">
                Cenas Inertes Eliminadas: <b>${p.deadweight_scenes_removed}</b> | Tempo de Render Desperdiçado Poupado: <b>${p.saved_render_time_sec}s</b>
              </div>
              ${detailsHtml}
              <div style="margin-top:8px; font-size:0.8rem; color:#d1d5db;">${p.summary}</div>
            </div>
          `;
        }
      } catch (e) {
        contentEl.innerHTML = `<div style="color:#ef4444;">Erro ao auditar: ${e.message}</div>`;
      }
    }
    async function executarPodaInertes() {
      if (!currentPlan) return;
      try {
        const res = await fetch('/api/pruner/apply', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ project_id: currentPlan.project_id })
        });
        const data = await res.json();
        if (data.ok) {
          alert('Poda concluída! Cenas redundantes foram removidas e a timeline foi otimizada para o hardware.');
          carregarRoteiro(currentPlan.project_id);
          fecharPrunerModal();
        }
      } catch (e) {
        alert('Erro ao aplicar poda: ' + e.message);
      }
    }

    // SSD Write Fatigue Mitigator
    function abrirSSDFatigueModal() {
      document.getElementById('ssd-fatigue-modal').style.display = 'flex';
      calcularEconomiaSSD();
    }
    function fecharSSDFatigueModal() {
      document.getElementById('ssd-fatigue-modal').style.display = 'none';
    }
    async function calcularEconomiaSSD() {
      const contentEl = document.getElementById('ssd-fatigue-content');
      contentEl.innerHTML = '<div style="color:var(--text-muted); text-align:center;">Calculando ciclo de gravação NAND Flash e alocação volátil...</div>';
      try {
        const res = await fetch(`/api/ssd/fatigue/estimate?mb=1200`);
        const data = await res.json();
        if (data.ok && data.ssd_report) {
          const s = data.ssd_report;
          contentEl.innerHTML = `
            <div style="background:var(--card-bg); border:1px solid var(--border); border-radius:8px; padding:12px;">
              <div style="display:flex; justify-content:space-between; align-items:center;">
                <span style="font-weight:700; color:#4ade80;">Modo: ${s.scratchpad_mode}</span>
                <span style="background:rgba(74,222,128,0.2); color:#86efac; font-size:0.85rem; padding:3px 8px; border-radius:4px; font-weight:700;">-${s.ssd_life_extension_pct}% Desgaste</span>
              </div>
              <div style="display:flex; gap:16px; margin:10px 0; font-size:0.85rem;">
                <span style="color:#f87171;">Sem Mitigação: ${s.estimated_ssd_wear_without_mitigation_mb} MB</span>
                <span style="color:#4ade80;">Com Buffer RAM: ${s.ssd_wear_with_mitigation_mb} MB</span>
                <span style="color:#fde047;">Poupado: ${s.saved_ssd_writes_mb} MB</span>
              </div>
              <div style="font-size:0.8rem; color:var(--text-muted);">${s.recommendation}</div>
            </div>
          `;
        }
      } catch (e) {
        contentEl.innerHTML = `<div style="color:#ef4444;">Erro ao estimar: ${e.message}</div>`;
      }
    }

    // Audio Pass-Through
    function abrirAudioPassThroughModal() {
      document.getElementById('audio-passthrough-modal').style.display = 'flex';
      avaliarAudioPassThrough();
    }
    function fecharAudioPassThroughModal() {
      document.getElementById('audio-passthrough-modal').style.display = 'none';
    }
    async function avaliarAudioPassThrough() {
      const codec = document.getElementById('audio-pt-codec') ? document.getElementById('audio-pt-codec').value : 'aac';
      const contentEl = document.getElementById('audio-pt-content');
      contentEl.innerHTML = '<div style="color:var(--text-muted); text-align:center;">Verificando compatibilidade de bitstream para cópia direta...</div>';
      try {
        const res = await fetch(`/api/audio/passthrough/evaluate?codec=${codec}`);
        const data = await res.json();
        if (data.ok && data.evaluation) {
          const ev = data.evaluation;
          contentEl.innerHTML = `
            <div style="background:var(--card-bg); border:1px solid var(--border); border-radius:8px; padding:12px;">
              <div style="display:flex; justify-content:space-between; align-items:center;">
                <span style="font-weight:700; color:#a3e635;">Fidelidade: ${ev.audio_fidelity}</span>
                <span style="background:rgba(163,230,53,0.2); color:#bef264; font-size:0.8rem; padding:2px 8px; border-radius:4px; font-weight:700;">-${ev.cpu_load_reduction_pct}% CPU Áudio</span>
              </div>
              <div style="font-size:0.85rem; color:var(--text-muted); margin:8px 0;">${ev.reason}</div>
              <div style="margin-top:6px; font-size:0.75rem; font-family:monospace; color:#fde047; background:#0f172a; padding:6px; border-radius:4px;">
                FFmpeg Audio Flag: ${ev.ffmpeg_audio_flags}
              </div>
            </div>
          `;
        }
      } catch (e) {
        contentEl.innerHTML = `<div style="color:#ef4444;">Erro ao avaliar: ${e.message}</div>`;
      }
    }

    // Thermal Adaptive Pacer
    function abrirThermalPacerModal() {
      document.getElementById('thermal-pacer-modal').style.display = 'flex';
      calcularThermalPacer();
    }
    function fecharThermalPacerModal() {
      document.getElementById('thermal-pacer-modal').style.display = 'none';
    }
    async function calcularThermalPacer() {
      const prof = document.getElementById('thermal-pacer-prof') ? document.getElementById('thermal-pacer-prof').value : 'silent_eco';
      const contentEl = document.getElementById('thermal-pacer-content');
      contentEl.innerHTML = '<div style="color:var(--text-muted); text-align:center;">Mapeando curvas de calor e ciclos de resfriamento...</div>';
      try {
        const res = await fetch(`/api/hardware/thermal_pacer/calculate?profile=${prof}&work_sec=45`);
        const data = await res.json();
        if (data.ok && data.pacer) {
          const p = data.pacer;
          contentEl.innerHTML = `
            <div style="background:var(--card-bg); border:1px solid var(--border); border-radius:8px; padding:12px;">
              <div style="display:flex; justify-content:space-between; align-items:center;">
                <span style="font-weight:700; color:#f97316;">${p.profile_name}</span>
                <span style="background:rgba(249,115,22,0.2); color:#fdba74; font-size:0.8rem; padding:2px 8px; border-radius:4px; font-weight:700;">Meta: < ${p.target_max_temp_c}°C</span>
              </div>
              <div style="display:flex; gap:16px; margin:8px 0; font-size:0.85rem;">
                <span style="color:#93c5fd;">Ventoinhas: ${p.fan_noise_estimate}</span>
                <span style="color:#a7f3d0;">Pausa Preventiva: ${p.pause_ms}ms</span>
              </div>
              <div style="font-size:0.8rem; color:var(--text-muted);">${p.advice}</div>
            </div>
          `;
        }
      } catch (e) {
        contentEl.innerHTML = `<div style="color:#ef4444;">Erro ao calcular: ${e.message}</div>`;
      }
    }

    // Smart Proxy Scaler
    function abrirSmartProxyModal() {
      document.getElementById('smart-proxy-modal').style.display = 'flex';
      calcularSmartProxy();
    }
    function fecharSmartProxyModal() {
      document.getElementById('smart-proxy-modal').style.display = 'none';
    }
    async function calcularSmartProxy() {
      const tier = document.getElementById('smart-proxy-tier') ? document.getElementById('smart-proxy-tier').value : 'ultra_light_540p';
      const contentEl = document.getElementById('smart-proxy-content');
      contentEl.innerHTML = '<div style="color:var(--text-muted); text-align:center;">Calculando amostragem de resolução leve...</div>';
      try {
        const res = await fetch(`/api/media/proxy/calculate?tier=${tier}`);
        const data = await res.json();
        if (data.ok && data.proxy_config) {
          const pc = data.proxy_config;
          contentEl.innerHTML = `
            <div style="background:var(--card-bg); border:1px solid var(--border); border-radius:8px; padding:12px;">
              <div style="display:flex; justify-content:space-between; align-items:center;">
                <span style="font-weight:700; color:#06b6d4;">${pc.tier_name}</span>
                <span style="background:rgba(6,182,212,0.2); color:#67e8f9; font-size:0.8rem; padding:2px 8px; border-radius:4px; font-weight:700;">-${pc.ram_reduction_pct}% RAM</span>
              </div>
              <div style="font-size:0.85rem; color:var(--text-muted); margin:8px 0;">
                Resolução Nativa: <b>${pc.source_resolution}</b> -> Proxy Leve: <b>${pc.proxy_resolution}</b>
              </div>
              <div style="font-size:0.75rem; font-family:monospace; color:#a5f3fc; background:#0f172a; padding:6px; border-radius:4px;">
                FFmpeg Downsample: -vf ${pc.ffmpeg_scale_filter} -b:v ${pc.recommended_bitrate}
              </div>
              <div style="margin-top:8px; font-size:0.8rem; color:#86efac;">${pc.summary}</div>
            </div>
          `;
        }
      } catch (e) {
        contentEl.innerHTML = `<div style="color:#ef4444;">Erro ao calcular proxy: ${e.message}</div>`;
      }
    }

    // SQLite WAL Checkpoint
    async function executarWALCheckpoint() {
      try {
        const res = await fetch('/api/db/wal_checkpoint', { method: 'POST' });
        const data = await res.json();
        if (data.ok && data.checkpoint) {
          const cp = data.checkpoint;
          alert(`🗄️ Manutenção WAL do Banco SQLite concluída com sucesso!\n\nEspaço liberado: ${cp.space_freed_kb} KB\nPáginas salvas: ${cp.pages_checkpointed}\n\nO banco de dados foi desfragmentado sem bloquear as leituras do editor.`);
        } else {
          alert('Erro ao executar checkpoint: ' + (data.error || 'Falha'));
        }
      } catch (e) {
        alert('Erro ao requisitar checkpoint: ' + e.message);
      }
    }

    // Zero-Copy Frame Pipe
    function abrirZeroCopyModal() {
      document.getElementById('zero-copy-modal').style.display = 'flex';
      calcularZeroCopyPipe();
    }
    function fecharZeroCopyModal() {
      document.getElementById('zero-copy-modal').style.display = 'none';
    }
    async function calcularZeroCopyPipe() {
      const contentEl = document.getElementById('zero-copy-content');
      contentEl.innerHTML = '<div style="color:var(--text-muted); text-align:center;">Mapeando canal de memória IPC...</div>';
      try {
        const res = await fetch(`/api/pipeline/zero_copy/calculate?w=1920&h=1080&fps=30`);
        const data = await res.json();
        if (data.ok && data.pipe) {
          const p = data.pipe;
          contentEl.innerHTML = `
            <div style="background:var(--card-bg); border:1px solid var(--border); border-radius:8px; padding:12px;">
              <div style="display:flex; justify-content:space-between; align-items:center;">
                <span style="font-weight:700; color:#38bdf8;">${p.ipc_transport}</span>
                <span style="background:rgba(56,189,248,0.2); color:#7dd3fc; font-size:0.8rem; padding:2px 8px; border-radius:4px; font-weight:700;">-${p.ssd_io_saved_pct}% Escritas SSD</span>
              </div>
              <div style="font-size:0.85rem; color:var(--text-muted); margin:8px 0;">
                Resolução: <b>${p.resolution} @ ${p.fps}fps</b> | Throughput RAM: <b>${p.raw_stream_bandwidth_mb_s} MB/s</b>
              </div>
              <div style="font-size:0.75rem; font-family:monospace; color:#fde047; background:#0f172a; padding:6px; border-radius:4px;">
                FFmpeg Memory Pipe: ${p.pipe_input_args}
              </div>
              <div style="margin-top:8px; font-size:0.8rem; color:#86efac;">${p.summary}</div>
            </div>
          `;
        }
      } catch (e) {
        contentEl.innerHTML = `<div style="color:#ef4444;">Erro ao calcular pipe: ${e.message}</div>`;
      }
    }

    // RAM Working Set Trimmer
    async function executarLimpezaWorkingSet() {
      try {
        const res = await fetch('/api/system/ram/trim', { method: 'POST' });
        const data = await res.json();
        if (data.ok && data.trim) {
          const t = data.trim;
          alert(`🧹 Memória RAM liberada com sucesso!\n\nObjetos Python coletados: ${t.python_gc_objects_freed}\nWorking Set devolvido ao Windows: ${t.win32_empty_working_set_applied ? 'SIM (EmptyWorkingSet ativado)' : 'Padrão'}\n\nO consumo de memória física foi reduzido ao nível basal!`);
        } else {
          alert('Erro ao desalocar RAM: ' + (data.error || 'Falha'));
        }
      } catch (e) {
        alert('Erro ao requisitar limpeza: ' + e.message);
      }
    }

    // VFR Jitter Smoother
    function abrirVFROptimizerModal() {
      document.getElementById('vfr-modal').style.display = 'flex';
      calcularVFROptimizer();
    }
    function fecharVFROptimizerModal() {
      document.getElementById('vfr-modal').style.display = 'none';
    }
    async function calcularVFROptimizer() {
      const fps = document.getElementById('vfr-fps') ? document.getElementById('vfr-fps').value : '30';
      const contentEl = document.getElementById('vfr-content');
      contentEl.innerHTML = '<div style="color:var(--text-muted); text-align:center;">Calculando matriz vetorial de timestamps...</div>';
      try {
        const res = await fetch(`/api/editing/vfr/calculate?fps=${fps}`);
        const data = await res.json();
        if (data.ok && data.vfr) {
          const v = data.vfr;
          contentEl.innerHTML = `
            <div style="background:var(--card-bg); border:1px solid var(--border); border-radius:8px; padding:12px;">
              <div style="display:flex; justify-content:space-between; align-items:center;">
                <span style="font-weight:700; color:#f59e0b;">Taxa Constante: ${v.target_constant_fps} FPS</span>
                <span style="background:rgba(245,158,11,0.2); color:#fcd34d; font-size:0.8rem; padding:2px 8px; border-radius:4px; font-weight:700;">Complexidade: O(1)</span>
              </div>
              <div style="font-size:0.85rem; color:var(--text-muted); margin:8px 0;">${v.summary}</div>
              <div style="font-size:0.75rem; font-family:monospace; color:#fed7aa; background:#0f172a; padding:6px; border-radius:4px;">
                Filtros: ${v.combined_filter_string} ${v.ffmpeg_demuxer_flags}
              </div>
            </div>
          `;
        }
      } catch (e) {
        contentEl.innerHTML = `<div style="color:#ef4444;">Erro ao calcular VFR: ${e.message}</div>`;
      }
    }

    // JSON Delta Patcher
    function abrirDeltaPatcherModal() {
      if (!currentPlan) return alert('Analise ou carregue um roteiro primeiro!');
      document.getElementById('delta-patcher-modal').style.display = 'flex';
      calcularDeltaPatcher();
    }
    function fecharDeltaPatcherModal() {
      document.getElementById('delta-patcher-modal').style.display = 'none';
    }
    async function calcularDeltaPatcher() {
      if (!currentPlan) return;
      const contentEl = document.getElementById('delta-patcher-content');
      contentEl.innerHTML = '<div style="color:var(--text-muted); text-align:center;">Comparando nós de dados e calculando diff RFC 6902...</div>';
      try {
        const res = await fetch(`/api/storage/delta/calculate?project_id=${currentPlan.project_id}`);
        const data = await res.json();
        if (data.ok && data.delta) {
          const d = data.delta;
          contentEl.innerHTML = `
            <div style="background:var(--card-bg); border:1px solid var(--border); border-radius:8px; padding:12px;">
              <div style="display:flex; justify-content:space-between; align-items:center;">
                <span style="font-weight:700; color:#ec4899;">Operações Delta: ${d.operations_count}</span>
                <span style="background:rgba(236,72,153,0.2); color:#f472b6; font-size:0.8rem; padding:2px 8px; border-radius:4px; font-weight:700;">-${d.bandwidth_and_ssd_savings_pct}% Volume SSD</span>
              </div>
              <div style="display:flex; gap:16px; margin:8px 0; font-size:0.85rem;">
                <span style="color:#9ca3af;">JSON Cru: ${d.original_payload_bytes} Bytes</span>
                <span style="color:#4ade80;">Patch Delta: ${d.delta_payload_bytes} Bytes</span>
              </div>
              <div style="font-size:0.8rem; color:var(--text-muted);">${d.summary}</div>
            </div>
          `;
        }
      } catch (e) {
        contentEl.innerHTML = `<div style="color:#ef4444;">Erro ao calcular delta: ${e.message}</div>`;
      }
    }

    // Keyframe Interval Aligner
    function abrirKeyframeAlignerModal() {
      document.getElementById('keyframe-aligner-modal').style.display = 'flex';
      calcularKeyframeAligner();
    }
    function fecharKeyframeAlignerModal() {
      document.getElementById('keyframe-aligner-modal').style.display = 'none';
    }
    async function calcularKeyframeAligner() {
      const cutSec = document.getElementById('kf-cut-sec') ? document.getElementById('kf-cut-sec').value : '4.05';
      const contentEl = document.getElementById('kf-align-content');
      contentEl.innerHTML = '<div style="color:var(--text-muted); text-align:center;">Detectando GOP e alinhando corte a I-Frames...</div>';
      try {
        const res = await fetch(`/api/editing/keyframe/align?cut_sec=${cutSec}&fps=30`);
        const data = await res.json();
        if (data.ok && data.alignment) {
          const a = data.alignment;
          contentEl.innerHTML = `
            <div style="background:var(--card-bg); border:1px solid var(--border); border-radius:8px; padding:12px;">
              <div style="display:flex; justify-content:space-between; align-items:center;">
                <span style="font-weight:700; color:#f43f5e;">Estratégia: ${a.ffmpeg_cut_strategy}</span>
                <span style="background:rgba(244,63,94,0.2); color:#fda4af; font-size:0.8rem; padding:2px 8px; border-radius:4px; font-weight:700;">-${a.cpu_energy_saved_pct}% CPU</span>
              </div>
              <div style="font-size:0.85rem; color:var(--text-muted); margin:8px 0;">
                Corte Solicitado: <b>${a.requested_cut_sec}s</b> -> Alinhado ao I-Frame: <b>${a.aligned_cut_sec}s</b> (Offset: ${a.drift_offset_ms}ms)
              </div>
              <div style="font-size:0.8rem; color:#86efac;">${a.summary}</div>
            </div>
          `;
        }
      } catch (e) {
        contentEl.innerHTML = `<div style="color:#ef4444;">Erro ao calcular keyframe: ${e.message}</div>`;
      }
    }

    // GPU VRAM Leak Sentinel
    function abrirVRAMSentinelModal() {
      document.getElementById('vram-sentinel-modal').style.display = 'flex';
      calcularVRAMSentinel();
    }
    function fecharVRAMSentinelModal() {
      document.getElementById('vram-sentinel-modal').style.display = 'none';
    }
    async function calcularVRAMSentinel() {
      const contentEl = document.getElementById('vram-sentinel-content');
      contentEl.innerHTML = '<div style="color:var(--text-muted); text-align:center;">Inspecionando alocação de buffers gráficos D3D11/NVENC...</div>';
      try {
        const res = await fetch(`/api/hardware/vram/inspect?vram_mb=1800`);
        const data = await res.json();
        if (data.ok && data.vram_status) {
          const v = data.vram_status;
          contentEl.innerHTML = `
            <div style="background:var(--card-bg); border:1px solid var(--border); border-radius:8px; padding:12px;">
              <div style="display:flex; justify-content:space-between; align-items:center;">
                <span style="font-weight:700; color:#8b5cf6;">Aceleração: ${v.hardware_backend.toUpperCase()}</span>
                <span style="background:rgba(139,92,246,0.2); color:#c4b5fd; font-size:0.8rem; padding:2px 8px; border-radius:4px; font-weight:700;">${v.reset_strategy}</span>
              </div>
              <div style="font-size:0.85rem; color:var(--text-muted); margin:8px 0;">
                VRAM Ocupada Estimada: <b>${v.estimated_retained_vram_mb} MB</b> | Recuperável pós-render: <b>${v.reclaimable_vram_mb} MB</b>
              </div>
              <div style="font-size:0.75rem; font-family:monospace; color:#ddd6fe; background:#0f172a; padding:6px; border-radius:4px;">
                Flags de Decodificação Hardware: ${v.ffmpeg_hw_flags}
              </div>
              <div style="margin-top:8px; font-size:0.8rem; color:#d8b4fe;">${v.summary}</div>
            </div>
          `;
        }
      } catch (e) {
        contentEl.innerHTML = `<div style="color:#ef4444;">Erro ao inspecionar VRAM: ${e.message}</div>`;
      }
    }

    // NVMe 4KB Trim & I/O Coalescer
    function abrirNVMeCoalescerModal() {
      document.getElementById('nvme-coalescer-modal').style.display = 'flex';
      calcularNVMeCoalescer();
    }
    function fecharNVMeCoalescerModal() {
      document.getElementById('nvme-coalescer-modal').style.display = 'none';
    }
    async function calcularNVMeCoalescer() {
      const bytesIn = document.getElementById('nvme-input-bytes') ? document.getElementById('nvme-input-bytes').value : '5400';
      const contentEl = document.getElementById('nvme-coalescer-content');
      contentEl.innerHTML = '<div style="color:var(--text-muted); text-align:center;">Calculando alinhamento de setores 4KB NVMe...</div>';
      try {
        const res = await fetch(`/api/hardware/nvme/coalesce?bytes=${bytesIn}`);
        const data = await res.json();
        if (data.ok && data.coalesce) {
          const c = data.coalesce;
          contentEl.innerHTML = `
            <div style="background:var(--card-bg); border:1px solid var(--border); border-radius:8px; padding:12px;">
              <div style="display:flex; justify-content:space-between; align-items:center;">
                <span style="font-weight:700; color:#14b8a6;">Setores de 4KB: ${c.sectors_4k_count} blocos</span>
                <span style="background:rgba(20,184,166,0.2); color:#5eead4; font-size:0.8rem; padding:2px 8px; border-radius:4px; font-weight:700;">-${c.nand_flash_wear_reduction_pct}% Desgaste NAND</span>
              </div>
              <div style="font-size:0.85rem; color:var(--text-muted); margin:8px 0;">
                Tamanho Original: <b>${c.unaligned_input_bytes} Bytes</b> -> Alinhado (4K): <b>${c.aligned_output_bytes} Bytes</b> (+${c.padding_bytes}B padding)
              </div>
              <div style="font-size:0.8rem; color:#99f6e4;">${c.summary}</div>
            </div>
          `;
        }
      } catch (e) {
        contentEl.innerHTML = `<div style="color:#ef4444;">Erro ao calcular alinhamento: ${e.message}</div>`;
      }
    }

    // Color Space Fast Matrix
    function abrirColorMatrixModal() {
      document.getElementById('color-matrix-modal').style.display = 'flex';
      calcularColorMatrix();
    }
    function fecharColorMatrixModal() {
      document.getElementById('color-matrix-modal').style.display = 'none';
    }
    async function calcularColorMatrix() {
      const srcSpace = document.getElementById('color-src') ? document.getElementById('color-src').value : 'bt601';
      const tgtSpace = document.getElementById('color-tgt') ? document.getElementById('color-tgt').value : 'bt709';
      const contentEl = document.getElementById('color-matrix-content');
      contentEl.innerHTML = '<div style="color:var(--text-muted); text-align:center;">Calculando matriz de conversão vetorial SIMD...</div>';
      try {
        const res = await fetch(`/api/media/color_matrix/calculate?src=${srcSpace}&tgt=${tgtSpace}`);
        const data = await res.json();
        if (data.ok && data.matrix) {
          const m = data.matrix;
          contentEl.innerHTML = `
            <div style="background:var(--card-bg); border:1px solid var(--border); border-radius:8px; padding:12px;">
              <div style="display:flex; justify-content:space-between; align-items:center;">
                <span style="font-weight:700; color:#eab308;">${m.source_name} -> ${m.target_name}</span>
                <span style="background:rgba(234,179,8,0.2); color:#fef08a; font-size:0.8rem; padding:2px 8px; border-radius:4px; font-weight:700;">-${m.cpu_overhead_vs_3d_lut_reduction_pct}% Carga vs 3D LUT</span>
              </div>
              <div style="font-size:0.85rem; color:var(--text-muted); margin:8px 0;">${m.algorithm}</div>
              <div style="font-size:0.75rem; font-family:monospace; color:#fde047; background:#0f172a; padding:6px; border-radius:4px;">
                FFmpeg SIMD Filter: -vf ${m.fast_ffmpeg_filter}
              </div>
              <div style="margin-top:8px; font-size:0.8rem; color:#fef9c3;">${m.summary}</div>
            </div>
          `;
        }
      } catch (e) {
        contentEl.innerHTML = `<div style="color:#ef4444;">Erro ao calcular matriz: ${e.message}</div>`;
      }
    }

    // --- Funções do Pacote Hardware-Armor Pinnacle ---
    async function abrirTimerOptimizerModal() {
      document.getElementById('timer-optimizer-modal').style.display = 'flex';
      alternarTimerResolution(null);
    }
    function fecharTimerOptimizerModal() {
      document.getElementById('timer-optimizer-modal').style.display = 'none';
    }
    async function alternarTimerResolution(mode) {
      const contentEl = document.getElementById('timer-optimizer-content');
      contentEl.innerHTML = '<div style="color:var(--text-muted); text-align:center;">Consultando resolução do timer do Windows...</div>';
      try {
        const url = mode === null ? '/api/system/timer_resolution' : `/api/system/timer_resolution?high_precision=${mode ? 1 : 0}`;
        const res = await fetch(url);
        const data = await res.json();
        if (data.ok && data.result) {
          const r = data.result;
          contentEl.innerHTML = `
            <div style="background:var(--card-bg); border:1px solid var(--border); border-radius:8px; padding:12px;">
              <div style="display:flex; justify-content:space-between; align-items:center;">
                <span style="font-weight:700; color:${r.high_precision_mode ? '#38bdf8' : '#4ade80'};">${r.current_state}</span>
                <span style="background:${r.high_precision_mode ? 'rgba(56,189,248,0.2)' : 'rgba(74,222,128,0.2)'}; color:${r.high_precision_mode ? '#bae6fd' : '#bbf7d0'}; font-size:0.8rem; padding:2px 8px; border-radius:4px; font-weight:700;">
                  ${r.target_resolution_ms}ms Tick
                </span>
              </div>
              <div style="font-size:0.85rem; color:var(--text-muted); margin:8px 0;">
                Economia Basal de CPU: <strong>${r.cpu_idle_power_savings_pct}%</strong> | Suporte WinMM: ${r.applied_via_winmm ? 'Ativo' : 'Simulado/Nativo'}
              </div>
              <div style="margin-top:8px; font-size:0.8rem; color:#e2e8f0;">${r.summary}</div>
              <div style="margin-top:12px; display:flex; gap:8px;">
                <button class="btn btn-secondary" onclick="alternarTimerResolution(0)" ${!r.high_precision_mode ? 'disabled' : ''}>Forçar Modo Idle (15.6ms)</button>
                <button class="btn btn-primary" onclick="alternarTimerResolution(1)" ${r.high_precision_mode ? 'disabled' : ''}>Ativar Alta Precisão (1.0ms)</button>
              </div>
            </div>
          `;
        }
      } catch (e) {
        contentEl.innerHTML = `<div style="color:#ef4444;">Erro ao gerenciar timer: ${e.message}</div>`;
      }
    }

    async function abrirAudioPeakModal() {
      document.getElementById('audio-peak-modal').style.display = 'flex';
      calcularAudioPeak();
    }
    function fecharAudioPeakModal() {
      document.getElementById('audio-peak-modal').style.display = 'none';
    }
    async function calcularAudioPeak() {
      const amp = document.getElementById('audio-peak-amp')?.value || '28000';
      const contentEl = document.getElementById('audio-peak-content');
      contentEl.innerHTML = '<div style="color:var(--text-muted); text-align:center;">Varrendo amostras de áudio com matemática inteira...</div>';
      try {
        const res = await fetch(`/api/audio/peak_scan?amplitude=${amp}`);
        const data = await res.json();
        if (data.ok && data.scan) {
          const s = data.scan;
          contentEl.innerHTML = `
            <div style="background:var(--card-bg); border:1px solid var(--border); border-radius:8px; padding:12px;">
              <div style="display:flex; justify-content:space-between; align-items:center;">
                <span style="font-weight:700; color:${s.has_clipping ? '#ef4444' : '#4ade80'};">
                  ${s.peak_dbfs} dBFS ${s.has_clipping ? '(CLIPPING)' : '(NORMAL)'}
                </span>
                <span style="background:rgba(74,222,128,0.2); color:#bbf7d0; font-size:0.8rem; padding:2px 8px; border-radius:4px; font-weight:700;">
                  -${s.cpu_overhead_reduction_pct}% Sobrecarga de CPU
                </span>
              </div>
              <div style="font-size:0.85rem; color:var(--text-muted); margin:8px 0;">
                Amostras: ${s.samples_count.toLocaleString()} | Pico Inteiro: ${s.peak_integer} / ${s.max_int16_limit} | Headroom: ${s.headroom_db} dB
              </div>
              <div style="margin-top:8px; font-size:0.8rem; color:#e2e8f0;">${s.summary}</div>
            </div>
          `;
        }
      } catch (e) {
        contentEl.innerHTML = `<div style="color:#ef4444;">Erro na varredura inteira: ${e.message}</div>`;
      }
    }

    async function abrirSeekCancellerModal() {
      document.getElementById('seek-canceller-modal').style.display = 'flex';
      simularCancelamentoSeeks();
    }
    function fecharSeekCancellerModal() {
      document.getElementById('seek-canceller-modal').style.display = 'none';
    }
    async function simularCancelamentoSeeks() {
      const contentEl = document.getElementById('seek-canceller-content');
      contentEl.innerHTML = '<div style="color:var(--text-muted); text-align:center;">Avaliando requisições pendentes na linha do tempo...</div>';
      try {
        const res = await fetch('/api/media/seek_cancel?pending=intro,cena1,cena2,cena3,outro&visible=cena2,cena3');
        const data = await res.json();
        if (data.ok && data.canceller) {
          const c = data.canceller;
          contentEl.innerHTML = `
            <div style="background:var(--card-bg); border:1px solid var(--border); border-radius:8px; padding:12px;">
              <div style="display:flex; justify-content:space-between; align-items:center;">
                <span style="font-weight:700; color:#38bdf8;">${c.cancelled_obsolete_seeks} I/O Seeks Obsoletos Descartados</span>
                <span style="background:rgba(56,189,248,0.2); color:#bae6fd; font-size:0.8rem; padding:2px 8px; border-radius:4px; font-weight:700;">
                  -${c.io_queue_pressure_reduction_pct}% Pressão no SSD
                </span>
              </div>
              <div style="font-size:0.85rem; color:var(--text-muted); margin:8px 0;">
                Requisições ativas mantidas: ${c.active_seeks_remaining} | Descartadas: ${c.cancelled_clip_ids.join(', ')}
              </div>
              <div style="margin-top:8px; font-size:0.8rem; color:#e2e8f0;">${c.summary}</div>
            </div>
          `;
        }
      } catch (e) {
        contentEl.innerHTML = `<div style="color:#ef4444;">Erro no cancelamento de busca: ${e.message}</div>`;
      }
    }

    async function abrirGPUBarrierModal() {
      document.getElementById('gpu-barrier-modal').style.display = 'flex';
      calcularGPUBarrier();
    }
    function fecharGPUBarrierModal() {
      document.getElementById('gpu-barrier-modal').style.display = 'none';
    }
    async function calcularGPUBarrier() {
      const hw = document.getElementById('gpu-barrier-hw')?.value || 'd3d11va';
      const fps = document.getElementById('gpu-barrier-fps')?.value || '60';
      const contentEl = document.getElementById('gpu-barrier-content');
      contentEl.innerHTML = '<div style="color:var(--text-muted); text-align:center;">Calculando barreira de sincronização de VRAM...</div>';
      try {
        const res = await fetch(`/api/pipeline/gpu_barrier/calculate?hw=${hw}&fps=${fps}`);
        const data = await res.json();
        if (data.ok && data.barrier) {
          const b = data.barrier;
          contentEl.innerHTML = `
            <div style="background:var(--card-bg); border:1px solid var(--border); border-radius:8px; padding:12px;">
              <div style="display:flex; justify-content:space-between; align-items:center;">
                <span style="font-weight:700; color:#a855f7;">${b.hw_acceleration.toUpperCase()} | ${b.target_fps} FPS</span>
                <span style="background:rgba(168,85,247,0.2); color:#e9d5ff; font-size:0.8rem; padding:2px 8px; border-radius:4px; font-weight:700;">
                  -${b.gpu_stall_reduction_pct}% Stalls Térmicos
                </span>
              </div>
              <div style="font-size:0.85rem; color:var(--text-muted); margin:8px 0;">
                Orçamento de Quadro: ${b.frame_time_budget_ms} ms | Buffer em Anel VRAM: ${b.vram_ring_buffer_frames} frames
              </div>
              <div style="font-size:0.75rem; font-family:monospace; color:#d8b4fe; background:#0f172a; padding:6px; border-radius:4px;">
                FFmpeg Sync Flags: ${b.ffmpeg_sync_args}
              </div>
              <div style="margin-top:8px; font-size:0.8rem; color:#f3e8ff;">${b.summary}</div>
            </div>
          `;
        }
      } catch (e) {
        contentEl.innerHTML = `<div style="color:#ef4444;">Erro na barreira de GPU: ${e.message}</div>`;
      }
    }

    // --- Funções do Pacote Hardware-Armor Apex ---
    async function abrirThermalGovernorModal() {
      document.getElementById('thermal-governor-modal').style.display = 'flex';
      avaliarThermalGovernor();
    }
    function fecharThermalGovernorModal() {
      document.getElementById('thermal-governor-modal').style.display = 'none';
    }
    async function avaliarThermalGovernor() {
      const temp = document.getElementById('thermal-governor-temp')?.value || '82';
      const contentEl = document.getElementById('thermal-governor-content');
      contentEl.innerHTML = '<div style="color:var(--text-muted); text-align:center;">Avaliando telemetria e gradiente térmico...</div>';
      try {
        const res = await fetch(`/api/system/thermal_governor/evaluate?temp=${temp}`);
        const data = await res.json();
        if (data.ok && data.governor) {
          const g = data.governor;
          const badgeColor = g.thermal_state === 'CRITICAL' ? '#ef4444' : (g.thermal_state === 'SAFE' ? '#22c55e' : '#f97316');
          contentEl.innerHTML = `
            <div style="background:var(--card-bg); border:1px solid var(--border); border-radius:8px; padding:12px;">
              <div style="display:flex; justify-content:space-between; align-items:center;">
                <span style="font-weight:700; color:${badgeColor};">${g.thermal_state} (${g.current_temp_celsius}°C)</span>
                <span style="background:rgba(234,88,12,0.2); color:#ffedd5; font-size:0.8rem; padding:2px 8px; border-radius:4px; font-weight:700;">
                  Pausa: ${g.recommended_micro_pause_ms} ms
                </span>
              </div>
              <div style="font-size:0.85rem; color:var(--text-muted); margin:8px 0;">
                Risco de Throttling: <strong>${g.throttling_risk}</strong> | Redução Térmica Estimada: -${g.estimated_temp_reduction_celsius}°C
              </div>
              <div style="font-size:0.8rem; color:#4ade80;">${g.hardware_health}</div>
              <div style="margin-top:8px; font-size:0.8rem; color:#fed7aa;">${g.summary}</div>
            </div>
          `;
        }
      } catch (e) {
        contentEl.innerHTML = `<div style="color:#ef4444;">Erro no governador térmico: ${e.message}</div>`;
      }
    }

    async function abrirSparsePipeModal() {
      document.getElementById('sparse-pipe-modal').style.display = 'flex';
      consultarSparsePipe();
    }
    function fecharSparsePipeModal() {
      document.getElementById('sparse-pipe-modal').style.display = 'none';
    }
    async function consultarSparsePipe() {
      const contentEl = document.getElementById('sparse-pipe-content');
      contentEl.innerHTML = '<div style="color:var(--text-muted); text-align:center;">Verificando pool de quadros zero-copy...</div>';
      try {
        const res = await fetch('/api/storage/sparse_pipe/metrics');
        const data = await res.json();
        if (data.ok && data.pipe) {
          const p = data.pipe;
          contentEl.innerHTML = `
            <div style="background:var(--card-bg); border:1px solid var(--border); border-radius:8px; padding:12px;">
              <div style="display:flex; justify-content:space-between; align-items:center;">
                <span style="font-weight:700; color:#38bdf8;">Resolução: ${p.resolution} (Pool: ${p.pool_depth} frames)</span>
                <span style="background:rgba(56,189,248,0.2); color:#bae6fd; font-size:0.8rem; padding:2px 8px; border-radius:4px; font-weight:700;">
                  -${p.gc_pressure_reduction_pct}% Pausas de GC
                </span>
              </div>
              <div style="font-size:0.85rem; color:var(--text-muted); margin:8px 0;">
                RAM Estática em Uso: ${p.static_ram_footprint_mb} MB | Alocações Transitórias Evitadas: <strong>${p.ram_churn_prevented_mb} MB</strong>
              </div>
              <div style="margin-top:8px; font-size:0.8rem; color:#bae6fd;">${p.summary}</div>
            </div>
          `;
        }
      } catch (e) {
        contentEl.innerHTML = `<div style="color:#ef4444;">Erro no pipe zero-copy: ${e.message}</div>`;
      }
    }

    async function abrirViewportCullerModal() {
      document.getElementById('viewport-culler-modal').style.display = 'flex';
      simularViewportCuller();
    }
    function fecharViewportCullerModal() {
      document.getElementById('viewport-culler-modal').style.display = 'none';
    }
    async function simularViewportCuller() {
      const contentEl = document.getElementById('viewport-culler-content');
      contentEl.innerHTML = '<div style="color:var(--text-muted); text-align:center;">Calculando geometria de viewport O(log N)...</div>';
      try {
        const res = await fetch('/api/editing/viewport_culler/simulate');
        const data = await res.json();
        if (data.ok && data.culler) {
          const c = data.culler;
          contentEl.innerHTML = `
            <div style="background:var(--card-bg); border:1px solid var(--border); border-radius:8px; padding:12px;">
              <div style="display:flex; justify-content:space-between; align-items:center;">
                <span style="font-weight:700; color:#84cc16;">${c.culled_clips_count} de ${c.total_clips} Clipes Ocultados da GPU</span>
                <span style="background:rgba(132,204,22,0.2); color:#d9f99d; font-size:0.8rem; padding:2px 8px; border-radius:4px; font-weight:700;">
                  -${c.ui_render_savings_pct}% Carga Gráfica
                </span>
              </div>
              <div style="font-size:0.85rem; color:var(--text-muted); margin:8px 0;">
                Clipes Visíveis Renderizados: ${c.visible_clips_count} (${c.visible_clip_ids.join(', ')})
              </div>
              <div style="margin-top:8px; font-size:0.8rem; color:#ecfccb;">${c.summary}</div>
            </div>
          `;
        }
      } catch (e) {
        contentEl.innerHTML = `<div style="color:#ef4444;">Erro no culling de viewport: ${e.message}</div>`;
      }
    }

    async function abrirAudioBypassModal() {
      document.getElementById('audio-bypass-modal').style.display = 'flex';
      calcularAudioBypass();
    }
    function fecharAudioBypassModal() {
      document.getElementById('audio-bypass-modal').style.display = 'none';
    }
    async function calcularAudioBypass() {
      const srcHz = document.getElementById('audio-bypass-src')?.value || '48000';
      const tgtHz = document.getElementById('audio-bypass-tgt')?.value || '48000';
      const contentEl = document.getElementById('audio-bypass-content');
      contentEl.innerHTML = '<div style="color:var(--text-muted); text-align:center;">Verificando grafo de filtragem de áudio...</div>';
      try {
        const res = await fetch(`/api/media/audio_bypass/evaluate?src_hz=${srcHz}&tgt_hz=${tgtHz}`);
        const data = await res.json();
        if (data.ok && data.bypass) {
          const b = data.bypass;
          contentEl.innerHTML = `
            <div style="background:var(--card-bg); border:1px solid var(--border); border-radius:8px; padding:12px;">
              <div style="display:flex; justify-content:space-between; align-items:center;">
                <span style="font-weight:700; color:${b.can_bypass_resample ? '#14b8a6' : '#f59e0b'};">${b.mode}</span>
                <span style="background:rgba(20,184,166,0.2); color:#99f6e4; font-size:0.8rem; padding:2px 8px; border-radius:4px; font-weight:700;">
                  -${b.cpu_audio_processing_savings_pct}% Ciclos de CPU
                </span>
              </div>
              <div style="font-size:0.75rem; font-family:monospace; color:#5eead4; background:#0f172a; padding:6px; border-radius:4px; margin:8px 0;">
                FFmpeg Audio Filter: -af "${b.ffmpeg_audio_filter}"
              </div>
              <div style="margin-top:8px; font-size:0.8rem; color:#ccfbf1;">${b.summary}</div>
            </div>
          `;
        }
      } catch (e) {
        contentEl.innerHTML = `<div style="color:#ef4444;">Erro no bypass de áudio: ${e.message}</div>`;
      }
    }

    // --- Funções do Pacote Hardware-Armor Quantum ---
    async function abrirCPUAffinityModal() {
      document.getElementById('cpu-affinity-modal').style.display = 'flex';
      calcularCPUAffinity();
    }
    function fecharCPUAffinityModal() {
      document.getElementById('cpu-affinity-modal').style.display = 'none';
    }
    async function calcularCPUAffinity() {
      const contentEl = document.getElementById('cpu-affinity-content');
      contentEl.innerHTML = '<div style="color:var(--text-muted); text-align:center;">Calculando topologia de núcleos e cluster L3...</div>';
      try {
        const res = await fetch('/api/core/cpu_affinity/calculate');
        const data = await res.json();
        if (data.ok && data.affinity) {
          const a = data.affinity;
          contentEl.innerHTML = `
            <div style="background:var(--card-bg); border:1px solid var(--border); border-radius:8px; padding:12px;">
              <div style="display:flex; justify-content:space-between; align-items:center;">
                <span style="font-weight:700; color:#818cf8;">Cluster Primário L3: Núcleos [${a.primary_affinity_cores.join(', ')}]</span>
                <span style="background:rgba(99,102,241,0.2); color:#c7d2fe; font-size:0.8rem; padding:2px 8px; border-radius:4px; font-weight:700;">
                  -${a.bus_traffic_reduction_pct}% Tráfego de Barramento
                </span>
              </div>
              <div style="font-size:0.85rem; color:var(--text-muted); margin:8px 0;">
                Núcleos Detectados: ${a.logical_cores_detected} | Máscara de Afinidade: <code>${a.affinity_mask_hex}</code> | Ganho Cache Hit: +${a.cache_hit_rate_boost_pct}%
              </div>
              <div style="margin-top:8px; font-size:0.8rem; color:#e0e7ff;">${a.summary}</div>
            </div>
          `;
        }
      } catch (e) {
        contentEl.innerHTML = `<div style="color:#ef4444;">Erro ao balancear L3: ${e.message}</div>`;
      }
    }

    async function abrirAudioCrossfadeModal() {
      document.getElementById('audio-crossfade-modal').style.display = 'flex';
      calcularAudioCrossfade();
    }
    function fecharAudioCrossfadeModal() {
      document.getElementById('audio-crossfade-modal').style.display = 'none';
    }
    async function calcularAudioCrossfade() {
      const progress = document.getElementById('audio-crossfade-prog')?.value || '0.5';
      const contentEl = document.getElementById('audio-crossfade-content');
      contentEl.innerHTML = '<div style="color:var(--text-muted); text-align:center;">Consultando tabela inteira de crossfade...</div>';
      try {
        const res = await fetch(`/api/editing/audio_crossfade/benchmark?progress=${progress}`);
        const data = await res.json();
        if (data.ok && data.crossfade) {
          const c = data.crossfade;
          contentEl.innerHTML = `
            <div style="background:var(--card-bg); border:1px solid var(--border); border-radius:8px; padding:12px;">
              <div style="display:flex; justify-content:space-between; align-items:center;">
                <span style="font-weight:700; color:#fb7185;">Ganho Fade Out: ${c.fade_out_coeff} | Fade In: ${c.fade_in_coeff}</span>
                <span style="background:rgba(244,63,94,0.2); color:#fecdd3; font-size:0.8rem; padding:2px 8px; border-radius:4px; font-weight:700;">
                  -${c.fpu_cpu_load_reduction_pct}% Carga da FPU
                </span>
              </div>
              <div style="font-size:0.85rem; color:var(--text-muted); margin:8px 0;">
                Curva: ${c.curve_type} (${c.table_size_steps} degraus inteiros) | Operações FPU Poupadas: <strong>${c.trig_ops_eliminated_per_second.toLocaleString()} /s</strong>
              </div>
              <div style="margin-top:8px; font-size:0.8rem; color:#ffe4e6;">${c.summary}</div>
            </div>
          `;
        }
      } catch (e) {
        contentEl.innerHTML = `<div style="color:#ef4444;">Erro no crossfade inteiro: ${e.message}</div>`;
      }
    }

    async function abrirMoovDetectorModal() {
      document.getElementById('moov-detector-modal').style.display = 'flex';
      analisarMoovDetector();
    }
    function fecharMoovDetectorModal() {
      document.getElementById('moov-detector-modal').style.display = 'none';
    }
    async function analisarMoovDetector() {
      const sizeMb = document.getElementById('moov-file-size')?.value || '4000';
      const contentEl = document.getElementById('moov-detector-content');
      contentEl.innerHTML = '<div style="color:var(--text-muted); text-align:center;">Inspecionando posição do átomo MOOV no arquivo...</div>';
      try {
        const res = await fetch(`/api/media/moov_detector/analyze?size_mb=${sizeMb}`);
        const data = await res.json();
        if (data.ok && data.detector) {
          const d = data.detector;
          contentEl.innerHTML = `
            <div style="background:var(--card-bg); border:1px solid var(--border); border-radius:8px; padding:12px;">
              <div style="display:flex; justify-content:space-between; align-items:center;">
                <span style="font-weight:700; color:#38bdf8;">Arquivo de ${d.file_size_mb} MB (${d.moov_location})</span>
                <span style="background:rgba(56,189,248,0.2); color:#bae6fd; font-size:0.8rem; padding:2px 8px; border-radius:4px; font-weight:700;">
                  -${d.ssd_read_reduction_pct}% Leituras no SSD
                </span>
              </div>
              <div style="font-size:0.85rem; color:var(--text-muted); margin:8px 0;">
                Bytes Lidos para Indexação: ${d.bytes_read_for_index.toLocaleString()} B | Volume Desnecessário Poupado no SSD: <strong>${d.ssd_io_saved_mb} MB</strong>
              </div>
              <div style="margin-top:8px; font-size:0.8rem; color:#e0f2fe;">${d.summary}</div>
            </div>
          `;
        }
      } catch (e) {
        contentEl.innerHTML = `<div style="color:#ef4444;">Erro no detector MOOV: ${e.message}</div>`;
      }
    }

    async function abrirShaderWarmupModal() {
      document.getElementById('shader-warmup-modal').style.display = 'flex';
      aquecerShadersGPU();
    }
    function fecharShaderWarmupModal() {
      document.getElementById('shader-warmup-modal').style.display = 'none';
    }
    async function aquecerShadersGPU() {
      const contentEl = document.getElementById('shader-warmup-content');
      contentEl.innerHTML = '<div style="color:var(--text-muted); text-align:center;">Pré-aquecendo bytecode de shaders de aceleração por hardware...</div>';
      try {
        const res = await fetch('/api/pipeline/shader_warmup/execute');
        const data = await res.json();
        if (data.ok && data.warmup) {
          const w = data.warmup;
          contentEl.innerHTML = `
            <div style="background:var(--card-bg); border:1px solid var(--border); border-radius:8px; padding:12px;">
              <div style="display:flex; justify-content:space-between; align-items:center;">
                <span style="font-weight:700; color:#c084fc;">${w.total_shaders_cached} Shaders em Cache Persistente</span>
                <span style="background:rgba(192,132,252,0.2); color:#f3e8ff; font-size:0.8rem; padding:2px 8px; border-radius:4px; font-weight:700;">
                  -${w.stutter_reduction_pct}% Micro-Stutters
                </span>
              </div>
              <div style="font-size:0.85rem; color:var(--text-muted); margin:8px 0;">
                Estado: <strong>${w.timeline_playback_readiness}</strong> | Shaders compilados: ${w.cached_shader_keys.join(', ')}
              </div>
              <div style="margin-top:8px; font-size:0.8rem; color:#f5f3ff;">${w.summary}</div>
            </div>
          `;
        }
      } catch (e) {
        contentEl.innerHTML = `<div style="color:#ef4444;">Erro no aquecimento de shaders: ${e.message}</div>`;
      }
    }

    // --- Funções do Pacote Hardware-Armor Titanium ---
    async function abrirNUMABindingModal() {
      document.getElementById('numa-binding-modal').style.display = 'flex';
      consultarNUMABinding();
    }
    function fecharNUMABindingModal() {
      document.getElementById('numa-binding-modal').style.display = 'none';
    }
    async function consultarNUMABinding() {
      const contentEl = document.getElementById('numa-binding-content');
      contentEl.innerHTML = '<div style="color:var(--text-muted); text-align:center;">Mapeando afinidade de nós NUMA e topologia RAM...</div>';
      try {
        const res = await fetch('/api/core/numa/topology');
        const data = await res.json();
        if (data.ok && data.topology) {
          const t = data.topology;
          contentEl.innerHTML = `
            <div style="background:var(--card-bg); border:1px solid var(--border); border-radius:8px; padding:12px;">
              <div style="display:flex; justify-content:space-between; align-items:center;">
                <span style="font-weight:700; color:#14b8a6;">${t.numa_nodes_count} Nó(s) NUMA (${t.detected_cores} Núcleos)</span>
                <span style="background:rgba(20,184,166,0.2); color:#99f6e4; font-size:0.8rem; padding:2px 8px; border-radius:4px; font-weight:700;">
                  -${t.cross_node_traffic_reduction_pct}% Tráfego Inter-Socket
                </span>
              </div>
              <div style="font-size:0.85rem; color:var(--text-muted); margin:8px 0;">
                Ganho de Latência RAM: <strong>+${t.memory_latency_improvement_pct}%</strong> | Mapeamento: ${JSON.stringify(t.node_assignments)}
              </div>
              <div style="margin-top:8px; font-size:0.8rem; color:#ccfbf1;">${t.summary}</div>
            </div>
          `;
        }
      } catch (e) {
        contentEl.innerHTML = `<div style="color:#ef4444;">Erro na topologia NUMA: ${e.message}</div>`;
      }
    }

    async function abrirBezierFixedModal() {
      document.getElementById('bezier-fixed-modal').style.display = 'flex';
      avaliarBezierFixed();
    }
    function fecharBezierFixedModal() {
      document.getElementById('bezier-fixed-modal').style.display = 'none';
    }
    async function avaliarBezierFixed() {
      const prog = document.getElementById('bezier-prog')?.value || '0.5';
      const contentEl = document.getElementById('bezier-fixed-content');
      contentEl.innerHTML = '<div style="color:var(--text-muted); text-align:center;">Calculando curva Bezier Q16.16...</div>';
      try {
        const res = await fetch(`/api/editing/bezier_fixed/evaluate?progress=${prog}`);
        const data = await res.json();
        if (data.ok && data.bezier) {
          const b = data.bezier;
          contentEl.innerHTML = `
            <div style="background:var(--card-bg); border:1px solid var(--border); border-radius:8px; padding:12px;">
              <div style="display:flex; justify-content:space-between; align-items:center;">
                <span style="font-weight:700; color:#f59e0b;">Progresso: ${(prog * 100).toFixed(0)}% -> Easing: ${(b.eased_value * 100).toFixed(1)}%</span>
                <span style="background:rgba(245,158,11,0.2); color:#fef08a; font-size:0.8rem; padding:2px 8px; border-radius:4px; font-weight:700;">
                  -${b.fpu_workload_reduction_pct}% Carga da FPU
                </span>
              </div>
              <div style="font-size:0.85rem; color:var(--text-muted); margin:8px 0;">
                Formato: <strong>${b.format}</strong> | Ciclos de FPU poupados: <strong>${b.fpu_cycles_saved.toLocaleString()}</strong>
              </div>
              <div style="margin-top:8px; font-size:0.8rem; color:#fef3c7;">${b.summary}</div>
            </div>
          `;
        }
      } catch (e) {
        contentEl.innerHTML = `<div style="color:#ef4444;">Erro no Bezier Q16.16: ${e.message}</div>`;
      }
    }

    async function abrirProResPassthroughModal() {
      document.getElementById('prores-passthrough-modal').style.display = 'flex';
      calcularProResPassthrough();
    }
    function fecharProResPassthroughModal() {
      document.getElementById('prores-passthrough-modal').style.display = 'none';
    }
    async function calcularProResPassthrough() {
      const codec = document.getElementById('prores-codec')?.value || 'prores';
      const graded = document.getElementById('prores-graded')?.value === '1';
      const contentEl = document.getElementById('prores-passthrough-content');
      contentEl.innerHTML = '<div style="color:var(--text-muted); text-align:center;">Avaliando viabilidade de stream copy direto...</div>';
      try {
        const res = await fetch(`/api/media/passthrough/evaluate?codec=${codec}&graded=${graded ? 1 : 0}`);
        const data = await res.json();
        if (data.ok && data.passthrough) {
          const p = data.passthrough;
          contentEl.innerHTML = `
            <div style="background:var(--card-bg); border:1px solid var(--border); border-radius:8px; padding:12px;">
              <div style="display:flex; justify-content:space-between; align-items:center;">
                <span style="font-weight:700; color:${p.can_passthrough ? '#22c55e' : '#f59e0b'};">${p.codec.toUpperCase()} (${p.can_passthrough ? 'STREAM COPY' : 'ENCODE'})</span>
                <span style="background:rgba(34,197,94,0.2); color:#bbf7d0; font-size:0.8rem; padding:2px 8px; border-radius:4px; font-weight:700;">
                  -${p.render_workload_saved_pct}% Carga de Render
                </span>
              </div>
              <div style="font-size:0.75rem; font-family:monospace; color:#86efac; background:#0f172a; padding:6px; border-radius:4px; margin:8px 0;">
                FFmpeg Export Flag: ${p.ffmpeg_video_flag}
              </div>
              <div style="font-size:0.85rem; color:var(--text-muted); margin-bottom:8px;">
                Preservação: <strong>${p.quality_preservation}</strong> | Redução no tempo de export: <strong>${p.export_time_reduction_pct}%</strong>
              </div>
              <div style="font-size:0.8rem; color:#dcfce7;">${p.summary}</div>
            </div>
          `;
        }
      } catch (e) {
        contentEl.innerHTML = `<div style="color:#ef4444;">Erro no passthrough: ${e.message}</div>`;
      }
    }

    async function abrirWearMitigatorModal() {
      document.getElementById('wear-mitigator-modal').style.display = 'flex';
      simularWearMitigator();
    }
    function fecharWearMitigatorModal() {
      document.getElementById('wear-mitigator-modal').style.display = 'none';
    }
    async function simularWearMitigator() {
      const contentEl = document.getElementById('wear-mitigator-content');
      contentEl.innerHTML = '<div style="color:var(--text-muted); text-align:center;">Simulando consolidação de escritas em blocos SLC 64KB...</div>';
      try {
        const res = await fetch('/api/storage/wear_mitigator/simulate');
        const data = await res.json();
        if (data.ok && data.mitigator) {
          const m = data.mitigator;
          contentEl.innerHTML = `
            <div style="background:var(--card-bg); border:1px solid var(--border); border-radius:8px; padding:12px;">
              <div style="display:flex; justify-content:space-between; align-items:center;">
                <span style="font-weight:700; color:#ec4899;">Alinhamento Ótimo: ${m.optimal_block_alignment_kb} KB</span>
                <span style="background:rgba(236,72,153,0.2); color:#fbcfe8; font-size:0.8rem; padding:2px 8px; border-radius:4px; font-weight:700;">
                  -${m.nand_write_amplification_reduction_pct}% Ciclos NAND
                </span>
              </div>
              <div style="font-size:0.85rem; color:var(--text-muted); margin:8px 0;">
                ${m.simulated_raw_writes} pequenas escritas transformadas em <strong>${m.consolidated_aligned_flushes} gravações consolidadas</strong>
              </div>
              <div style="font-size:0.8rem; color:#4ade80;">${m.ssd_wear_leveling_protection}</div>
              <div style="margin-top:8px; font-size:0.8rem; color:#fce7f3;">${m.summary}</div>
            </div>
          `;
        }
      } catch (e) {
        contentEl.innerHTML = `<div style="color:#ef4444;">Erro no mitigador de desgaste: ${e.message}</div>`;
      }
    }
  </script>

  <!-- Modal de Estilos de Legenda -->
  <div id="subtitles-style-modal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.75); z-index:9999; align-items:center; justify-content:center;">
    <div style="background:var(--panel-bg); border:1px solid var(--border); border-radius:10px; width:560px; max-width:92%; max-height:85vh; display:flex; flex-direction:column; overflow:hidden; box-shadow:0 20px 25px -5px rgba(0,0,0,0.5);">
      <div style="padding:16px 20px; border-bottom:1px solid var(--border); display:flex; justify-content:space-between; align-items:center;">
        <h3 style="font-size:1.1rem; color:#fff; display:flex; align-items:center; gap:8px;">✨ Estilos Visuais de Legenda Dinâmica (.ASS)</h3>
        <button style="background:none; border:none; color:var(--text-muted); font-size:1.4rem; cursor:pointer;" onclick="fecharEstilosLegenda()">&times;</button>
      </div>
      <div style="padding:20px; overflow-y:auto; flex:1; display:flex; flex-direction:column; gap:12px;">
        <div style="font-size:0.85rem; color:var(--text-muted);">Selecione o design tipográfico para as legendas karaokê:</div>
        <select id="sub-style-select" style="padding:10px; background:var(--card-bg); border:1px solid var(--border); color:#fff; border-radius:6px; font-size:0.9rem;">
          <option value="hormozi_viral" selected>🔥 Hormozi / MrBeast Pop (Amarelo + Verde, Contorno Preto Grosso)</option>
          <option value="neon_glow">⚡ Neon Glow (Ciano & Magenta Cyberpunk)</option>
          <option value="cinema_classic">🎬 Cinema Classic (Netflix / Documentário Elegante)</option>
          <option value="minimalist_clean">💎 Minimalist Clean (Contemporâneo & Discreto)</option>
        </select>
        <div style="font-size:0.8rem; color:#94a3b8; line-height:1.4; background:var(--card-bg); padding:10px; border-radius:6px; border:1px solid var(--border);">
          💡 <b>Impacto:</b> O estilo <b>Hormozi / MrBeast</b> eleva a retenção em vídeos de formato vertical destacando a primeira palavra com cor contrastante.
        </div>
      </div>
      <div style="padding:12px 20px; border-top:1px solid var(--border); display:flex; justify-content:space-between; align-items:center; background:var(--card-bg);">
        <button class="btn btn-secondary" onclick="fecharEstilosLegenda()">Cancelar</button>
        <button class="btn btn-success" onclick="aplicarEstiloLegenda()">✨ Exportar Legendas Estilizadas</button>
      </div>
    </div>
  </div>

  <!-- Modal de Diretor de Transições -->
  <div id="transitions-modal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.75); z-index:9999; align-items:center; justify-content:center;">
    <div style="background:var(--panel-bg); border:1px solid var(--border); border-radius:10px; width:680px; max-width:92%; max-height:85vh; display:flex; flex-direction:column; overflow:hidden; box-shadow:0 20px 25px -5px rgba(0,0,0,0.5);">
      <div style="padding:16px 20px; border-bottom:1px solid var(--border); display:flex; justify-content:space-between; align-items:center;">
        <h3 style="font-size:1.1rem; color:#fff; display:flex; align-items:center; gap:8px;">🎭 Orquestração Inteligente de Transições</h3>
        <button style="background:none; border:none; color:var(--text-muted); font-size:1.4rem; cursor:pointer;" onclick="fecharDiretorTransicoes()">&times;</button>
      </div>
      <div style="padding:20px; overflow-y:auto; flex:1; display:flex; flex-direction:column; gap:10px;">
        <div style="font-size:0.85rem; color:var(--text-muted);">Transições contextuais dinâmicas calculadas com base nas mudanças dramáticas e temporais:</div>
        <div id="transitions-plan-list" style="display:flex; flex-direction:column; gap:8px;"></div>
      </div>
      <div style="padding:12px 20px; border-top:1px solid var(--border); display:flex; justify-content:flex-end; align-items:center; background:var(--card-bg);">
        <button class="btn btn-secondary" onclick="fecharDiretorTransicoes()">Fechar</button>
      </div>
    </div>
  </div>

  <!-- Modal de Extrator de Shorts -->
  <div id="shorts-extractor-modal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.75); z-index:9999; align-items:center; justify-content:center;">
    <div style="background:var(--panel-bg); border:1px solid var(--border); border-radius:10px; width:700px; max-width:92%; max-height:85vh; display:flex; flex-direction:column; overflow:hidden; box-shadow:0 20px 25px -5px rgba(0,0,0,0.5);">
      <div style="padding:16px 20px; border-bottom:1px solid var(--border); display:flex; justify-content:space-between; align-items:center;">
        <h3 style="font-size:1.1rem; color:#fff; display:flex; align-items:center; gap:8px;">✂️ Cortes Virais Automáticos para Shorts / TikTok (9:16)</h3>
        <button style="background:none; border:none; color:var(--text-muted); font-size:1.4rem; cursor:pointer;" onclick="fecharExtratorShorts()">&times;</button>
      </div>
      <div style="padding:20px; overflow-y:auto; flex:1; display:flex; flex-direction:column; gap:12px;">
        <div style="font-size:0.85rem; color:var(--text-muted);">Segmentos de 30-55s com maior densidade de ganchos virais detectados pela IA:</div>
        <div id="shorts-extract-list" style="display:flex; flex-direction:column; gap:10px;"></div>
      </div>
      <div style="padding:12px 20px; border-top:1px solid var(--border); display:flex; justify-content:flex-end; align-items:center; background:var(--card-bg);">
        <button class="btn btn-secondary" onclick="fecharExtratorShorts()">Fechar</button>
      </div>
    </div>
  </div>

  <!-- Modal de Títulos Virais & Thumbnails -->
  <div id="titles-modal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.75); z-index:9999; align-items:center; justify-content:center;">
    <div style="background:var(--panel-bg); border:1px solid var(--border); border-radius:10px; width:720px; max-width:92%; max-height:85vh; display:flex; flex-direction:column; overflow:hidden; box-shadow:0 20px 25px -5px rgba(0,0,0,0.5);">
      <div style="padding:16px 20px; border-bottom:1px solid var(--border); display:flex; justify-content:space-between; align-items:center;">
        <h3 style="font-size:1.1rem; color:#fff; display:flex; align-items:center; gap:8px;">🎣 Gerador de Títulos Virais & Thumbnails (Alto CTR)</h3>
        <button style="background:none; border:none; color:var(--text-muted); font-size:1.4rem; cursor:pointer;" onclick="fecharGeradorTitulos()">&times;</button>
      </div>
      <div style="padding:20px; overflow-y:auto; flex:1; display:flex; flex-direction:column; gap:14px;">
        <div style="display:flex; justify-content:space-between; align-items:center;">
          <span id="titles-topic-badge" style="background:#1e3a8a; color:#bfdbfe; font-size:0.8rem; padding:4px 10px; border-radius:12px; font-weight:700;">Tópico: Carregando...</span>
          <span style="font-size:0.75rem; color:var(--text-muted);">Baseado em Fórmulas Psicológicas do YouTube</span>
        </div>
        <div id="titles-list-container" style="display:flex; flex-direction:column; gap:10px;"></div>
        <div style="background:var(--card-bg); border:1px solid var(--border); padding:12px; border-radius:6px; margin-top:6px;">
          <div style="font-size:0.8rem; color:#94a3b8; font-weight:700; margin-bottom:8px;">🔥 Selos de Impacto para Estampar na Thumbnail:</div>
          <div id="thumbnail-badges-container" style="display:flex; gap:8px; flex-wrap:wrap;"></div>
        </div>
      </div>
      <div style="padding:12px 20px; border-top:1px solid var(--border); display:flex; justify-content:flex-end; align-items:center; background:var(--card-bg);">
        <button class="btn btn-secondary" onclick="fecharGeradorTitulos()">Fechar</button>
      </div>
    </div>
  </div>

  <!-- Modal de Stems Mixer -->
  <div id="stems-modal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.75); z-index:9999; align-items:center; justify-content:center;">
    <div style="background:var(--panel-bg); border:1px solid var(--border); border-radius:10px; width:640px; max-width:92%; max-height:85vh; display:flex; flex-direction:column; overflow:hidden; box-shadow:0 20px 25px -5px rgba(0,0,0,0.5);">
      <div style="padding:16px 20px; border-bottom:1px solid var(--border); display:flex; justify-content:space-between; align-items:center;">
        <h3 style="font-size:1.1rem; color:#fff; display:flex; align-items:center; gap:8px;">🎛️ Mixer de Stems Isolados (Multi-Pista)</h3>
        <button style="background:none; border:none; color:var(--text-muted); font-size:1.4rem; cursor:pointer;" onclick="fecharStemsMixer()">&times;</button>
      </div>
      <div style="padding:20px; overflow-y:auto; flex:1; display:flex; flex-direction:column; gap:14px;">
        <div style="font-size:0.85rem; color:var(--text-muted);">Três pistas independentes masterizadas a 48kHz / 24-bit para interoperabilidade com DaVinci Resolve, Premiere e Drift:</div>
        
        <div style="background:var(--card-bg); border:1px solid var(--border); padding:12px; border-radius:6px; display:flex; justify-content:space-between; align-items:center;">
          <div>
            <div style="font-weight:700; color:#fff;">🎙️ Pista 1: Voz & Narração (Dialogue)</div>
            <div style="font-size:0.75rem; color:var(--text-muted);">Voz neural limpa com isolamento acústico</div>
          </div>
          <span style="background:#065f46; color:#a7f3d0; padding:2px 8px; border-radius:4px; font-weight:700; font-size:0.8rem;">0.0 dB (Master)</span>
        </div>

        <div style="background:var(--card-bg); border:1px solid var(--border); padding:12px; border-radius:6px; display:flex; justify-content:space-between; align-items:center;">
          <div>
            <div style="font-weight:700; color:#fff;">🎵 Pista 2: Trilha Sonora (Soundtrack)</div>
            <div style="font-size:0.75rem; color:var(--text-muted);">Música de fundo com ducking dinâmico automático</div>
          </div>
          <span style="background:#1e3a8a; color:#bfdbfe; padding:2px 8px; border-radius:4px; font-weight:700; font-size:0.8rem;">-14.0 dB</span>
        </div>

        <div style="background:var(--card-bg); border:1px solid var(--border); padding:12px; border-radius:6px; display:flex; justify-content:space-between; align-items:center;">
          <div>
            <div style="font-weight:700; color:#fff;">🔊 Pista 3: Efeitos Sonoros & Foley (SFX)</div>
            <div style="font-size:0.75rem; color:var(--text-muted);">Micro-efeitos sincronizados aos timestamps das ações</div>
          </div>
          <span style="background:#581c87; color:#e9d5ff; padding:2px 8px; border-radius:4px; font-weight:700; font-size:0.8rem;">-16.0 dB</span>
        </div>
      </div>
      <div style="padding:12px 20px; border-top:1px solid var(--border); display:flex; justify-content:flex-end; align-items:center; background:var(--card-bg);">
        <button class="btn btn-secondary" onclick="fecharStemsMixer()">Fechar</button>
      </div>
    </div>
  </div>

  <!-- Modal de Auditoria de Ritmo & WPM -->
  <div id="pacing-modal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.75); z-index:9999; align-items:center; justify-content:center;">
    <div style="background:var(--panel-bg); border:1px solid var(--border); border-radius:10px; width:680px; max-width:92%; max-height:85vh; display:flex; flex-direction:column; overflow:hidden; box-shadow:0 20px 25px -5px rgba(0,0,0,0.5);">
      <div style="padding:16px 20px; border-bottom:1px solid var(--border); display:flex; justify-content:space-between; align-items:center;">
        <h3 style="font-size:1.1rem; color:#fff; display:flex; align-items:center; gap:8px;">⚡ Auditoria de Ritmo & Retenção de Público</h3>
        <button style="background:none; border:none; color:var(--text-muted); font-size:1.4rem; cursor:pointer;" onclick="fecharAuditoriaRitmo()">&times;</button>
      </div>
      <div style="padding:20px; overflow-y:auto; flex:1; display:flex; flex-direction:column; gap:14px;">
        <div style="display:grid; grid-template-columns:1fr 1fr; gap:12px;">
          <div style="background:var(--card-bg); border:1px solid var(--border); padding:12px; border-radius:6px; text-align:center;">
            <div style="font-size:0.75rem; color:var(--text-muted);">SCORE GERAL DE RETENÇÃO</div>
            <div id="pacing-score" style="font-size:1.8rem; font-weight:800; color:#10b981; margin-top:4px;">100/100</div>
          </div>
          <div style="background:var(--card-bg); border:1px solid var(--border); padding:12px; border-radius:6px; text-align:center;">
            <div style="font-size:0.75rem; color:var(--text-muted);">VELOCIDADE MÉDIA VOCAL</div>
            <div id="pacing-wpm" style="font-size:1.8rem; font-weight:800; color:#38bdf8; margin-top:4px;">145 WPM</div>
          </div>
        </div>
        <div id="pacing-summary" style="font-size:0.85rem; color:#cbd5e1; background:rgba(30,58,138,0.2); border:1px solid #1e3a8a; padding:10px 14px; border-radius:6px;"></div>
        <div style="font-weight:600; color:#fff; font-size:0.9rem;">Análise Cena a Cena:</div>
        <div id="pacing-scenes-list" style="display:flex; flex-direction:column; gap:8px;"></div>
      </div>
      <div style="padding:12px 20px; border-top:1px solid var(--border); display:flex; justify-content:flex-end; align-items:center; background:var(--card-bg);">
        <button class="btn btn-secondary" onclick="fecharAuditoriaRitmo()">Fechar</button>
      </div>
    </div>
  </div>

  <!-- Modal de Polimento de Tom -->
  <div id="tone-modal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.75); z-index:9999; align-items:center; justify-content:center;">
    <div style="background:var(--panel-bg); border:1px solid var(--border); border-radius:10px; width:560px; max-width:92%; max-height:85vh; display:flex; flex-direction:column; overflow:hidden; box-shadow:0 20px 25px -5px rgba(0,0,0,0.5);">
      <div style="padding:16px 20px; border-bottom:1px solid var(--border); display:flex; justify-content:space-between; align-items:center;">
        <h3 style="font-size:1.1rem; color:#fff; display:flex; align-items:center; gap:8px;">✍️ Polidor de Tom de Roteiro (IA)</h3>
        <button style="background:none; border:none; color:var(--text-muted); font-size:1.4rem; cursor:pointer;" onclick="fecharPolidorTom()">&times;</button>
      </div>
      <div style="padding:20px; overflow-y:auto; flex:1; display:flex; flex-direction:column; gap:12px;">
        <div style="font-size:0.85rem; color:var(--text-muted);">Selecione o arquétipo narrativo para reestruturar as frases e ganchos:</div>
        <select id="tone-select" style="padding:10px; background:var(--card-bg); border:1px solid var(--border); color:#fff; border-radius:6px; font-size:0.9rem;">
          <option value="shorts_viral" selected>⚡ Viral Dinâmico (Shorts / Reels / TikTok)</option>
          <option value="bbc_documentary">🏛️ Documentário Solene (Estilo BBC / History)</option>
          <option value="mystery_investigation">🕵️ Investigação & Suspense (True Crime / Sci-Fi)</option>
          <option value="didactic_friendly">🎓 Didático & Inspirador (Educação & Negócios)</option>
        </select>
        <div style="font-size:0.8rem; color:#94a3b8; line-height:1.4; background:var(--card-bg); padding:10px; border-radius:6px; border:1px solid var(--border);">
          💡 <b>Dica:</b> O modo <b>Viral Dinâmico</b> injeta um gancho nos primeiros 3 segundos e encurta as orações para maximizar o percentual de visualização média (AVD).
        </div>
      </div>
      <div style="padding:12px 20px; border-top:1px solid var(--border); display:flex; justify-content:space-between; align-items:center; background:var(--card-bg);">
        <button class="btn btn-secondary" onclick="fecharPolidorTom()">Cancelar</button>
        <button class="btn btn-success" onclick="aplicarPolimentoTom()">✨ Aplicar Novo Tom</button>
      </div>
    </div>
  </div>

  <!-- Modal de Capítulos YouTube -->
  <div id="chapters-modal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.75); z-index:9999; align-items:center; justify-content:center;">
    <div style="background:var(--panel-bg); border:1px solid var(--border); border-radius:10px; width:640px; max-width:92%; max-height:85vh; display:flex; flex-direction:column; overflow:hidden; box-shadow:0 20px 25px -5px rgba(0,0,0,0.5);">
      <div style="padding:16px 20px; border-bottom:1px solid var(--border); display:flex; justify-content:space-between; align-items:center;">
        <h3 style="font-size:1.1rem; color:#fff; display:flex; align-items:center; gap:8px;">⏱️ Capítulos YouTube & Timestamps</h3>
        <button style="background:none; border:none; color:var(--text-muted); font-size:1.4rem; cursor:pointer;" onclick="fecharCapitulosYouTube()">&times;</button>
      </div>
      <div style="padding:20px; overflow-y:auto; flex:1; display:flex; flex-direction:column; gap:10px;">
        <div style="font-size:0.85rem; color:var(--text-muted);">Copie e cole na descrição do YouTube para gerar as divisões clicáveis na barra de progresso:</div>
        <textarea id="youtube-chapters-text" style="width:100%; height:240px; background:var(--card-bg); border:1px solid var(--border); color:#fff; padding:10px; border-radius:6px; font-family:monospace; font-size:0.85rem; resize:none;" readonly></textarea>
      </div>
      <div style="padding:12px 20px; border-top:1px solid var(--border); display:flex; justify-content:space-between; align-items:center; background:var(--card-bg);">
        <button class="btn btn-secondary" onclick="fecharCapitulosYouTube()">Fechar</button>
        <button class="btn btn-success" onclick="copiarCapitulosYouTube()">📋 Copiar Capítulos (1-Clique)</button>
      </div>
    </div>
  </div>

  <!-- Modal de Foley SFX -->
  <div id="foley-modal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.75); z-index:9999; align-items:center; justify-content:center;">
    <div style="background:var(--panel-bg); border:1px solid var(--border); border-radius:10px; width:680px; max-width:92%; max-height:85vh; display:flex; flex-direction:column; overflow:hidden; box-shadow:0 20px 25px -5px rgba(0,0,0,0.5);">
      <div style="padding:16px 20px; border-bottom:1px solid var(--border); display:flex; justify-content:space-between; align-items:center;">
        <h3 style="font-size:1.1rem; color:#fff; display:flex; align-items:center; gap:8px;">🔊 Foley & Efeitos Sonoros Detectados</h3>
        <button style="background:none; border:none; color:var(--text-muted); font-size:1.4rem; cursor:pointer;" onclick="fecharFoleySonoro()">&times;</button>
      </div>
      <div id="foley-modal-body" style="padding:20px; overflow-y:auto; flex:1; display:flex; flex-direction:column; gap:10px;">
      </div>
      <div style="padding:12px 20px; border-top:1px solid var(--border); display:flex; justify-content:flex-end; align-items:center; background:var(--card-bg);">
        <button class="btn btn-secondary" onclick="fecharFoleySonoro()">Fechar</button>
      </div>
    </div>
  </div>
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

  <!-- Modal de Gerador de Tags & SEO YouTube -->
  <div id="seo-tags-modal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.75); z-index:9999; align-items:center; justify-content:center;">
    <div style="background:var(--panel-bg); border:1px solid var(--border); border-radius:10px; width:720px; max-width:92%; max-height:85vh; display:flex; flex-direction:column; overflow:hidden; box-shadow:0 20px 25px -5px rgba(0,0,0,0.5);">
      <div style="padding:16px 20px; border-bottom:1px solid var(--border); display:flex; justify-content:space-between; align-items:center;">
        <h3 style="font-size:1.1rem; color:#fff; display:flex; align-items:center; gap:8px;">🏷️ Gerador de Tags & SEO YouTube Studio</h3>
        <button style="background:none; border:none; color:var(--text-muted); font-size:1.4rem; cursor:pointer;" onclick="fecharSeoTags()">&times;</button>
      </div>
      <div id="seo-tags-content" style="padding:20px; overflow-y:auto; flex:1; display:flex; flex-direction:column; gap:14px;">
      </div>
      <div style="padding:12px 20px; border-top:1px solid var(--border); display:flex; justify-content:flex-end; align-items:center; background:var(--card-bg);">
        <button class="btn btn-secondary" onclick="fecharSeoTags()">Fechar</button>
      </div>
    </div>
  </div>

  <!-- Modal de Diretor de Câmera Ken Burns -->
  <div id="ken-burns-director-modal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.75); z-index:9999; align-items:center; justify-content:center;">
    <div style="background:var(--panel-bg); border:1px solid var(--border); border-radius:10px; width:760px; max-width:92%; max-height:85vh; display:flex; flex-direction:column; overflow:hidden; box-shadow:0 20px 25px -5px rgba(0,0,0,0.5);">
      <div style="padding:16px 20px; border-bottom:1px solid var(--border); display:flex; justify-content:space-between; align-items:center;">
        <h3 style="font-size:1.1rem; color:#fff; display:flex; align-items:center; gap:8px;">🎥 Diretor Inteligente de Câmera Ken Burns</h3>
        <button style="background:none; border:none; color:var(--text-muted); font-size:1.4rem; cursor:pointer;" onclick="fecharKenBurnsDirector()">&times;</button>
      </div>
      <div id="ken-burns-director-content" style="padding:20px; overflow-y:auto; flex:1; display:flex; flex-direction:column; gap:14px;">
      </div>
      <div style="padding:12px 20px; border-top:1px solid var(--border); display:flex; justify-content:flex-end; align-items:center; background:var(--card-bg);">
        <button class="btn btn-secondary" onclick="fecharKenBurnsDirector()">Fechar</button>
      </div>
    </div>
  </div>

  <!-- Modal de Marca D'água & Branding -->
  <div id="branding-modal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.75); z-index:9999; align-items:center; justify-content:center;">
    <div style="background:var(--panel-bg); border:1px solid var(--border); border-radius:10px; width:640px; max-width:92%; max-height:85vh; display:flex; flex-direction:column; overflow:hidden; box-shadow:0 20px 25px -5px rgba(0,0,0,0.5);">
      <div style="padding:16px 20px; border-bottom:1px solid var(--border); display:flex; justify-content:space-between; align-items:center;">
        <h3 style="font-size:1.1rem; color:#fff; display:flex; align-items:center; gap:8px;">🛡️ Identidade Visual & Marca D'água</h3>
        <button style="background:none; border:none; color:var(--text-muted); font-size:1.4rem; cursor:pointer;" onclick="fecharBrandingModal()">&times;</button>
      </div>
      <div style="padding:20px; overflow-y:auto; flex:1; display:flex; flex-direction:column; gap:14px;">
        <div style="background:#1e293b; padding:10px; border-radius:6px; font-size:0.82rem; color:#93c5fd;">
          Adicione um logotipo translúcido em todos os frames e um lower-third profissional de introdução nos primeiros 5 segundos.
        </div>
        <div>
          <label style="color:#cbd5e1; font-size:0.85rem;">Caminho da Imagem / Logo (PNG transparente):</label>
          <input type="text" id="branding-logo-path" value="assets/logo.png" style="width:100%; margin-top:4px; background:#0f172a; border:1px solid #334155; color:#fff; padding:6px 10px; border-radius:4px; font-size:0.85rem;">
        </div>
        <div style="display:grid; grid-template-columns:1fr 1fr; gap:12px;">
          <div>
            <label style="color:#cbd5e1; font-size:0.85rem;">Posição da Marca d'Água:</label>
            <select id="branding-pos" style="width:100%; margin-top:4px; background:#0f172a; border:1px solid #334155; color:#fff; padding:6px 10px; border-radius:4px; font-size:0.85rem;">
              <option value="top_right" selected>Canto Superior Direito</option>
              <option value="bottom_right">Canto Inferior Direito</option>
              <option value="top_left">Canto Superior Esquerdo</option>
              <option value="bottom_left">Canto Inferior Esquerdo</option>
            </select>
          </div>
          <div>
            <label style="color:#cbd5e1; font-size:0.85rem;">Opacidade (0.1 a 1.0):</label>
            <input type="number" id="branding-opacity" step="0.05" min="0.1" max="1.0" value="0.85" style="width:100%; margin-top:4px; background:#0f172a; border:1px solid #334155; color:#fff; padding:6px 10px; border-radius:4px; font-size:0.85rem;">
          </div>
        </div>
        <div style="display:grid; grid-template-columns:1fr 1fr; gap:12px;">
          <div>
            <label style="color:#cbd5e1; font-size:0.85rem;">Escala (% da largura do vídeo):</label>
            <input type="number" id="branding-scale" step="1" min="5" max="40" value="15" style="width:100%; margin-top:4px; background:#0f172a; border:1px solid #334155; color:#fff; padding:6px 10px; border-radius:4px; font-size:0.85rem;">
          </div>
          <div style="display:flex; align-items:center; margin-top:20px; gap:8px;">
            <input type="checkbox" id="branding-lower-third-check" checked style="width:18px; height:18px;">
            <label for="branding-lower-third-check" style="color:#cbd5e1; font-size:0.85rem; font-weight:600;">Ativar Lower-Third Intro (0s-5s)</label>
          </div>
        </div>
        <div style="display:grid; grid-template-columns:1fr 1fr; gap:12px;">
          <div>
            <label style="color:#cbd5e1; font-size:0.85rem;">Nome do Canal (Lower-Third):</label>
            <input type="text" id="branding-channel-name" value="Drift Cinematic Studio" style="width:100%; margin-top:4px; background:#0f172a; border:1px solid #334155; color:#fff; padding:6px 10px; border-radius:4px; font-size:0.85rem;">
          </div>
          <div>
            <label style="color:#cbd5e1; font-size:0.85rem;">Arroba / Handle do Canal:</label>
            <input type="text" id="branding-channel-handle" value="@driftcinematic" style="width:100%; margin-top:4px; background:#0f172a; border:1px solid #334155; color:#fff; padding:6px 10px; border-radius:4px; font-size:0.85rem;">
          </div>
        </div>
      </div>
      <div style="padding:12px 20px; border-top:1px solid var(--border); display:flex; justify-content:space-between; align-items:center; background:var(--card-bg);">
        <button class="btn btn-secondary" onclick="fecharBrandingModal()">Cancelar</button>
        <button class="btn" style="background:#ec4899; color:#fff; font-weight:700;" onclick="salvarBrandingConfig()">💾 Salvar & Aplicar Branding</button>
      </div>
    </div>
  </div>

  <!-- Modal de Templates de Canal em 1-Clique -->
  <div id="templates-modal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.75); z-index:9999; align-items:center; justify-content:center;">
    <div style="background:var(--panel-bg); border:1px solid var(--border); border-radius:10px; width:840px; max-width:92%; max-height:85vh; display:flex; flex-direction:column; overflow:hidden; box-shadow:0 20px 25px -5px rgba(0,0,0,0.5);">
      <div style="padding:16px 20px; border-bottom:1px solid var(--border); display:flex; justify-content:space-between; align-items:center;">
        <h3 style="font-size:1.1rem; color:#fff; display:flex; align-items:center; gap:8px;">⚡ Templates de Canal em 1-Clique</h3>
        <button style="background:none; border:none; color:var(--text-muted); font-size:1.4rem; cursor:pointer;" onclick="fecharTemplatesModal()">&times;</button>
      </div>
      <div style="padding:20px; overflow-y:auto; flex:1;">
        <div style="font-size:0.85rem; color:var(--text-muted); margin-bottom:14px;">
          Selecione a identidade completa do seu canal. Um clique padroniza cores, tipografia de legendas, proporção de tela, filtros Ken Burns e trilha sonora BGM:
        </div>
        <div id="templates-cards-grid" style="display:grid; grid-template-columns:1fr 1fr; gap:16px;">
        </div>
      </div>
      <div style="padding:12px 20px; border-top:1px solid var(--border); display:flex; justify-content:flex-end; align-items:center; background:var(--card-bg);">
        <button class="btn btn-secondary" onclick="fecharTemplatesModal()">Fechar</button>
      </div>
    </div>
  </div>

  <!-- Modal de Ducking & Punch-In -->
  <div id="ducking-punch-modal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.75); z-index:9999; align-items:center; justify-content:center;">
    <div style="background:var(--panel-bg); border:1px solid var(--border); border-radius:10px; width:720px; max-width:92%; max-height:85vh; display:flex; flex-direction:column; overflow:hidden; box-shadow:0 20px 25px -5px rgba(0,0,0,0.5);">
      <div style="padding:16px 20px; border-bottom:1px solid var(--border); display:flex; justify-content:space-between; align-items:center;">
        <h3 style="font-size:1.1rem; color:#fff; display:flex; align-items:center; gap:8px;">🎙️ Sidechain Ducking Dinâmico & Punch-Ins</h3>
        <button style="background:none; border:none; color:var(--text-muted); font-size:1.4rem; cursor:pointer;" onclick="fecharDuckingPunchModal()">&times;</button>
      </div>
      <div id="ducking-punch-content" style="padding:20px; overflow-y:auto; flex:1; display:flex; flex-direction:column; gap:12px;">
      </div>
      <div style="padding:12px 20px; border-top:1px solid var(--border); display:flex; justify-content:flex-end; align-items:center; background:var(--card-bg);">
        <button class="btn btn-secondary" onclick="fecharDuckingPunchModal()">Fechar</button>
      </div>
    </div>
  </div>

  <!-- Modal de Curva de Retenção & Heatmap -->
  <div id="retention-modal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.75); z-index:9999; align-items:center; justify-content:center;">
    <div style="background:var(--panel-bg); border:1px solid var(--border); border-radius:10px; width:760px; max-width:92%; max-height:85vh; display:flex; flex-direction:column; overflow:hidden; box-shadow:0 20px 25px -5px rgba(0,0,0,0.5);">
      <div style="padding:16px 20px; border-bottom:1px solid var(--border); display:flex; justify-content:space-between; align-items:center;">
        <h3 style="font-size:1.1rem; color:#fff; display:flex; align-items:center; gap:8px;">📊 Auditoria de Retenção Visual & Preditor do YouTube</h3>
        <button style="background:none; border:none; color:var(--text-muted); font-size:1.4rem; cursor:pointer;" onclick="fecharRetentionModal()">&times;</button>
      </div>
      <div id="retention-content" style="padding:20px; overflow-y:auto; flex:1; display:flex; flex-direction:column; gap:14px;">
      </div>
      <div style="padding:12px 20px; border-top:1px solid var(--border); display:flex; justify-content:flex-end; align-items:center; background:var(--card-bg);">
        <button class="btn btn-secondary" onclick="fecharRetentionModal()">Fechar</button>
      </div>
    </div>
  </div>

  <!-- Modal de Color Matcher de Acervos -->
  <div id="color-matcher-modal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.75); z-index:9999; align-items:center; justify-content:center;">
    <div style="background:var(--panel-bg); border:1px solid var(--border); border-radius:10px; width:740px; max-width:92%; max-height:85vh; display:flex; flex-direction:column; overflow:hidden; box-shadow:0 20px 25px -5px rgba(0,0,0,0.5);">
      <div style="padding:16px 20px; border-bottom:1px solid var(--border); display:flex; justify-content:space-between; align-items:center;">
        <h3 style="font-size:1.1rem; color:#fff; display:flex; align-items:center; gap:8px;">🎨 Color Matcher & Harmonização Cromática 5600K</h3>
        <button style="background:none; border:none; color:var(--text-muted); font-size:1.4rem; cursor:pointer;" onclick="fecharColorMatcherModal()">&times;</button>
      </div>
      <div id="color-matcher-content" style="padding:20px; overflow-y:auto; flex:1; display:flex; flex-direction:column; gap:12px;">
      </div>
      <div style="padding:12px 20px; border-top:1px solid var(--border); display:flex; justify-content:flex-end; align-items:center; background:var(--card-bg);">
        <button class="btn btn-secondary" onclick="fecharColorMatcherModal()">Fechar</button>
      </div>
    </div>
  </div>

  <!-- Modal de Multi-Export Simultâneo -->
  <div id="multiexport-modal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.75); z-index:9999; align-items:center; justify-content:center;">
    <div style="background:var(--panel-bg); border:1px solid var(--border); border-radius:10px; width:760px; max-width:92%; max-height:85vh; display:flex; flex-direction:column; overflow:hidden; box-shadow:0 20px 25px -5px rgba(0,0,0,0.5);">
      <div style="padding:16px 20px; border-bottom:1px solid var(--border); display:flex; justify-content:space-between; align-items:center;">
        <h3 style="font-size:1.1rem; color:#fff; display:flex; align-items:center; gap:8px;">📱 Multi-Export Simultâneo Multiplataforma</h3>
        <button style="background:none; border:none; color:var(--text-muted); font-size:1.4rem; cursor:pointer;" onclick="fecharMultiExportModal()">&times;</button>
      </div>
      <div style="padding:20px; overflow-y:auto; flex:1;">
        <div style="color:var(--text-muted); font-size:0.85rem; margin-bottom:12px;">
          Selecione as redes para gerar versões otimizadas simultâneas (proporção, safe zone e LUFS calibrados):
        </div>
        <div id="multiexport-presets-list" style="display:flex; flex-direction:column; gap:10px;"></div>
      </div>
      <div style="padding:12px 20px; border-top:1px solid var(--border); display:flex; justify-content:space-between; align-items:center; background:var(--card-bg);">
        <button class="btn btn-secondary" onclick="fecharMultiExportModal()">Cancelar</button>
        <button class="btn" style="background:#2563eb; color:#fff; font-weight:700;" onclick="executarMultiExport()">🚀 Exportar em Lote para Redes</button>
      </div>
    </div>
  </div>

  <!-- Modal de Testador A/B de Ganchos -->
  <div id="hook-tester-modal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.75); z-index:9999; align-items:center; justify-content:center;">
    <div style="background:var(--panel-bg); border:1px solid var(--border); border-radius:10px; width:740px; max-width:92%; max-height:85vh; display:flex; flex-direction:column; overflow:hidden; box-shadow:0 20px 25px -5px rgba(0,0,0,0.5);">
      <div style="padding:16px 20px; border-bottom:1px solid var(--border); display:flex; justify-content:space-between; align-items:center;">
        <h3 style="font-size:1.1rem; color:#fff; display:flex; align-items:center; gap:8px;">🎣 Testador A/B de Ganchos dos Primeiros 5 Segundos</h3>
        <button style="background:none; border:none; color:var(--text-muted); font-size:1.4rem; cursor:pointer;" onclick="fecharHookTesterModal()">&times;</button>
      </div>
      <div style="padding:20px; overflow-y:auto; flex:1;">
        <div style="color:var(--text-muted); font-size:0.85rem; margin-bottom:12px;">
          Selecione o arquétipo de abertura psicológica que melhor se adapta à proposta do seu vídeo:
        </div>
        <div id="hook-tester-list" style="display:flex; flex-direction:column; gap:12px;"></div>
      </div>
      <div style="padding:12px 20px; border-top:1px solid var(--border); display:flex; justify-content:flex-end; align-items:center; background:var(--card-bg);">
        <button class="btn btn-secondary" onclick="fecharHookTesterModal()">Fechar</button>
      </div>
    </div>
  </div>

  <!-- Modal de Sincronizador de Beat Musical -->
  <div id="beat-sync-modal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.75); z-index:9999; align-items:center; justify-content:center;">
    <div style="background:var(--panel-bg); border:1px solid var(--border); border-radius:10px; width:720px; max-width:92%; max-height:85vh; display:flex; flex-direction:column; overflow:hidden; box-shadow:0 20px 25px -5px rgba(0,0,0,0.5);">
      <div style="padding:16px 20px; border-bottom:1px solid var(--border); display:flex; justify-content:space-between; align-items:center;">
        <h3 style="font-size:1.1rem; color:#fff; display:flex; align-items:center; gap:8px;">🎵 Sincronizador de Beat Drop & Cortes no Tempo</h3>
        <button style="background:none; border:none; color:var(--text-muted); font-size:1.4rem; cursor:pointer;" onclick="fecharBeatSyncModal()">&times;</button>
      </div>
      <div id="beat-sync-content" style="padding:20px; overflow-y:auto; flex:1; display:flex; flex-direction:column; gap:12px;"></div>
      <div style="padding:12px 20px; border-top:1px solid var(--border); display:flex; justify-content:flex-end; align-items:center; background:var(--card-bg);">
        <button class="btn btn-secondary" onclick="fecharBeatSyncModal()">Fechar</button>
      </div>
    </div>
  </div>

  <!-- Modal de Diretor de Emoção da Voz IA -->
  <div id="voice-emotion-modal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.75); z-index:9999; align-items:center; justify-content:center;">
    <div style="background:var(--panel-bg); border:1px solid var(--border); border-radius:10px; width:740px; max-width:92%; max-height:85vh; display:flex; flex-direction:column; overflow:hidden; box-shadow:0 20px 25px -5px rgba(0,0,0,0.5);">
      <div style="padding:16px 20px; border-bottom:1px solid var(--border); display:flex; justify-content:space-between; align-items:center;">
        <h3 style="font-size:1.1rem; color:#fff; display:flex; align-items:center; gap:8px;">🎭 Diretor de Inflexão Emocional da Voz IA</h3>
        <button style="background:none; border:none; color:var(--text-muted); font-size:1.4rem; cursor:pointer;" onclick="fecharVoiceEmotionModal()">&times;</button>
      </div>
      <div id="voice-emotion-list" style="padding:20px; overflow-y:auto; flex:1; display:flex; flex-direction:column; gap:12px;"></div>
      <div style="padding:12px 20px; border-top:1px solid var(--border); display:flex; justify-content:flex-end; align-items:center; background:var(--card-bg);">
        <button class="btn btn-secondary" onclick="fecharVoiceEmotionModal()">Fechar</button>
      </div>
    </div>
  </div>

  <!-- Modal de Cartelas de Capítulos HD -->
  <div id="chapter-cards-modal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.75); z-index:9999; align-items:center; justify-content:center;">
    <div style="background:var(--panel-bg); border:1px solid var(--border); border-radius:10px; width:720px; max-width:92%; max-height:85vh; display:flex; flex-direction:column; overflow:hidden; box-shadow:0 20px 25px -5px rgba(0,0,0,0.5);">
      <div style="padding:16px 20px; border-bottom:1px solid var(--border); display:flex; justify-content:space-between; align-items:center;">
        <h3 style="font-size:1.1rem; color:#fff; display:flex; align-items:center; gap:8px;">🎬 Cartelas de Transição de Capítulos HD</h3>
        <button style="background:none; border:none; color:var(--text-muted); font-size:1.4rem; cursor:pointer;" onclick="fecharChapterCardsModal()">&times;</button>
      </div>
      <div id="chapter-cards-list" style="padding:20px; overflow-y:auto; flex:1; display:flex; flex-direction:column; gap:12px;"></div>
      <div style="padding:12px 20px; border-top:1px solid var(--border); display:flex; justify-content:flex-end; align-items:center; background:var(--card-bg);">
        <button class="btn btn-secondary" onclick="fecharChapterCardsModal()">Fechar</button>
      </div>
    </div>
  </div>

  <!-- Modal de Quad-Thumbnails A/B/C/D -->
  <div id="quad-thumbnails-modal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.75); z-index:9999; align-items:center; justify-content:center;">
    <div style="background:var(--panel-bg); border:1px solid var(--border); border-radius:10px; width:820px; max-width:92%; max-height:85vh; display:flex; flex-direction:column; overflow:hidden; box-shadow:0 20px 25px -5px rgba(0,0,0,0.5);">
      <div style="padding:16px 20px; border-bottom:1px solid var(--border); display:flex; justify-content:space-between; align-items:center;">
        <h3 style="font-size:1.1rem; color:#fff; display:flex; align-items:center; gap:8px;">🖼️ Suite de 4 Thumbnails (YouTube Test & Compare)</h3>
        <button style="background:none; border:none; color:var(--text-muted); font-size:1.4rem; cursor:pointer;" onclick="fecharQuadThumbnailsModal()">&times;</button>
      </div>
      <div style="padding:20px; overflow-y:auto; flex:1;">
        <div style="color:var(--text-muted); font-size:0.85rem; margin-bottom:12px;">
          4 variações psicológicas prontas para upload no teste automático de CTR do YouTube Studio:
        </div>
        <div id="quad-thumbnails-grid" style="display:grid; grid-template-columns:1fr 1fr; gap:12px;"></div>
      </div>
      <div style="padding:12px 20px; border-top:1px solid var(--border); display:flex; justify-content:flex-end; align-items:center; background:var(--card-bg);">
        <button class="btn btn-secondary" onclick="fecharQuadThumbnailsModal()">Fechar</button>
      </div>
    </div>
  </div>

  <!-- Modal de Auto-Tuner GPU/CPU Hardware -->
  <div id="hardware-tuner-modal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.75); z-index:9999; align-items:center; justify-content:center;">
    <div style="background:var(--panel-bg); border:1px solid var(--border); border-radius:10px; width:700px; max-width:92%; max-height:85vh; display:flex; flex-direction:column; overflow:hidden; box-shadow:0 20px 25px -5px rgba(0,0,0,0.5);">
      <div style="padding:16px 20px; border-bottom:1px solid var(--border); display:flex; justify-content:space-between; align-items:center;">
        <h3 style="font-size:1.1rem; color:#fff; display:flex; align-items:center; gap:8px;">⚡ Auto-Tuner de Hardware GPU/CPU & Encoders</h3>
        <button style="background:none; border:none; color:var(--text-muted); font-size:1.4rem; cursor:pointer;" onclick="fecharHardwareTunerModal()">&times;</button>
      </div>
      <div id="hardware-tuner-content" style="padding:20px; overflow-y:auto; flex:1; display:flex; flex-direction:column; gap:12px;"></div>
      <div style="padding:12px 20px; border-top:1px solid var(--border); display:flex; justify-content:flex-end; align-items:center; background:var(--card-bg);">
        <button class="btn btn-secondary" onclick="fecharHardwareTunerModal()">Fechar</button>
      </div>
    </div>
  </div>

  <!-- Modal de Ritmo Cardíaco & Dopamina -->
  <div id="retention-pacer-modal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.75); z-index:9999; align-items:center; justify-content:center;">
    <div style="background:var(--panel-bg); border:1px solid var(--border); border-radius:10px; width:740px; max-width:92%; max-height:85vh; display:flex; flex-direction:column; overflow:hidden; box-shadow:0 20px 25px -5px rgba(0,0,0,0.5);">
      <div style="padding:16px 20px; border-bottom:1px solid var(--border); display:flex; justify-content:space-between; align-items:center;">
        <h3 style="font-size:1.1rem; color:#fff; display:flex; align-items:center; gap:8px;">💓 Diretor de Ritmo Cardíaco & Dopamina (Hollywood Pacing)</h3>
        <button style="background:none; border:none; color:var(--text-muted); font-size:1.4rem; cursor:pointer;" onclick="fecharRetentionPacerModal()">&times;</button>
      </div>
      <div id="retention-pacer-list" style="padding:20px; overflow-y:auto; flex:1; display:flex; flex-direction:column; gap:10px;"></div>
      <div style="padding:12px 20px; border-top:1px solid var(--border); display:flex; justify-content:flex-end; align-items:center; background:var(--card-bg);">
        <button class="btn btn-secondary" onclick="fecharRetentionPacerModal()">Fechar</button>
      </div>
    </div>
  </div>

  <!-- Modal de Posts de Comunidade & Enquetes -->
  <div id="community-post-modal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.75); z-index:9999; align-items:center; justify-content:center;">
    <div style="background:var(--panel-bg); border:1px solid var(--border); border-radius:10px; width:760px; max-width:92%; max-height:85vh; display:flex; flex-direction:column; overflow:hidden; box-shadow:0 20px 25px -5px rgba(0,0,0,0.5);">
      <div style="padding:16px 20px; border-bottom:1px solid var(--border); display:flex; justify-content:space-between; align-items:center;">
        <h3 style="font-size:1.1rem; color:#fff; display:flex; align-items:center; gap:8px;">📢 Kit para Aba Comunidade do YouTube</h3>
        <button style="background:none; border:none; color:var(--text-muted); font-size:1.4rem; cursor:pointer;" onclick="fecharCommunityPostModal()">&times;</button>
      </div>
      <div id="community-post-content" style="padding:20px; overflow-y:auto; flex:1; display:flex; flex-direction:column; gap:12px;"></div>
      <div style="padding:12px 20px; border-top:1px solid var(--border); display:flex; justify-content:flex-end; align-items:center; background:var(--card-bg);">
        <button class="btn btn-secondary" onclick="fecharCommunityPostModal()">Fechar</button>
      </div>
    </div>
  </div>

  <!-- Modal de Áudio Espacial 3D (8D) -->
  <div id="spatial-audio-modal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.75); z-index:9999; align-items:center; justify-content:center;">
    <div style="background:var(--panel-bg); border:1px solid var(--border); border-radius:10px; width:760px; max-width:92%; max-height:85vh; display:flex; flex-direction:column; overflow:hidden; box-shadow:0 20px 25px -5px rgba(0,0,0,0.5);">
      <div style="padding:16px 20px; border-bottom:1px solid var(--border); display:flex; justify-content:space-between; align-items:center;">
        <h3 style="font-size:1.1rem; color:#fff; display:flex; align-items:center; gap:8px;">🎧 Áudio Espacial 3D & Efeitos Binaurais 8D</h3>
        <button style="background:none; border:none; color:var(--text-muted); font-size:1.4rem; cursor:pointer;" onclick="fecharSpatialAudioModal()">&times;</button>
      </div>
      <div id="spatial-audio-list" style="padding:20px; overflow-y:auto; flex:1; display:flex; flex-direction:column; gap:12px;"></div>
      <div style="padding:12px 20px; border-top:1px solid var(--border); display:flex; justify-content:flex-end; align-items:center; background:var(--card-bg);">
        <button class="btn btn-secondary" onclick="fecharSpatialAudioModal()">Fechar</button>
      </div>
    </div>
  </div>

  <!-- Modal de Telas Finais YouTube -->
  <div id="end-screen-modal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.75); z-index:9999; align-items:center; justify-content:center;">
    <div style="background:var(--panel-bg); border:1px solid var(--border); border-radius:10px; width:760px; max-width:92%; max-height:85vh; display:flex; flex-direction:column; overflow:hidden; box-shadow:0 20px 25px -5px rgba(0,0,0,0.5);">
      <div style="padding:16px 20px; border-bottom:1px solid var(--border); display:flex; justify-content:space-between; align-items:center;">
        <h3 style="font-size:1.1rem; color:#fff; display:flex; align-items:center; gap:8px;">🎬 Diretor de Telas Finais YouTube (End-Screen)</h3>
        <button style="background:none; border:none; color:var(--text-muted); font-size:1.4rem; cursor:pointer;" onclick="fecharEndScreenModal()">&times;</button>
      </div>
      <div id="end-screen-content" style="padding:20px; overflow-y:auto; flex:1; display:flex; flex-direction:column; gap:12px;"></div>
      <div style="padding:12px 20px; border-top:1px solid var(--border); display:flex; justify-content:flex-end; align-items:center; background:var(--card-bg);">
        <button class="btn btn-secondary" onclick="fecharEndScreenModal()">Fechar</button>
      </div>
    </div>
  </div>

  <!-- Modal de Normalização de Loudness (-14 LUFS) -->
  <div id="loudness-modal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.75); z-index:9999; align-items:center; justify-content:center;">
    <div style="background:var(--panel-bg); border:1px solid var(--border); border-radius:10px; width:760px; max-width:92%; max-height:85vh; display:flex; flex-direction:column; overflow:hidden; box-shadow:0 20px 25px -5px rgba(0,0,0,0.5);">
      <div style="padding:16px 20px; border-bottom:1px solid var(--border); display:flex; justify-content:space-between; align-items:center;">
        <h3 style="font-size:1.1rem; color:#fff; display:flex; align-items:center; gap:8px;">🎚️ Normalizador de Volume Broadcast (-14 LUFS / EBU R128)</h3>
        <button style="background:none; border:none; color:var(--text-muted); font-size:1.4rem; cursor:pointer;" onclick="fecharLoudnessModal()">&times;</button>
      </div>
      <div id="loudness-content" style="padding:20px; overflow-y:auto; flex:1; display:flex; flex-direction:column; gap:12px;"></div>
      <div style="padding:12px 20px; border-top:1px solid var(--border); display:flex; justify-content:flex-end; align-items:center; background:var(--card-bg);">
        <button class="btn btn-secondary" onclick="fecharLoudnessModal()">Fechar</button>
      </div>
    </div>
  </div>

  <!-- Modal de Auditor Neuro-Linguístico de Roteiro -->
  <div id="vocabulary-modal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.75); z-index:9999; align-items:center; justify-content:center;">
    <div style="background:var(--panel-bg); border:1px solid var(--border); border-radius:10px; width:760px; max-width:92%; max-height:85vh; display:flex; flex-direction:column; overflow:hidden; box-shadow:0 20px 25px -5px rgba(0,0,0,0.5);">
      <div style="padding:16px 20px; border-bottom:1px solid var(--border); display:flex; justify-content:space-between; align-items:center;">
        <h3 style="font-size:1.1rem; color:#fff; display:flex; align-items:center; gap:8px;">🧠 Auditor Neuro-Linguístico de Roteiro (Viral Hooks)</h3>
        <button style="background:none; border:none; color:var(--text-muted); font-size:1.4rem; cursor:pointer;" onclick="fecharVocabularyModal()">&times;</button>
      </div>
      <div id="vocabulary-list" style="padding:20px; overflow-y:auto; flex:1; display:flex; flex-direction:column; gap:12px;"></div>
      <div style="padding:12px 20px; border-top:1px solid var(--border); display:flex; justify-content:space-between; align-items:center; background:var(--card-bg);">
        <button class="btn" style="background:#7c3aed; color:#fff; font-weight:700;" onclick="aprimorarVocabularioAuto()">✨ Aprimorar Roteiro Automaticamente</button>
        <button class="btn btn-secondary" onclick="fecharVocabularyModal()">Fechar</button>
      </div>
    </div>
  </div>

  <!-- Modal de Cadência Dinâmica B-Roll -->
  <div id="broll-pacer-modal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.75); z-index:9999; align-items:center; justify-content:center;">
    <div style="background:var(--panel-bg); border:1px solid var(--border); border-radius:10px; width:760px; max-width:92%; max-height:85vh; display:flex; flex-direction:column; overflow:hidden; box-shadow:0 20px 25px -5px rgba(0,0,0,0.5);">
      <div style="padding:16px 20px; border-bottom:1px solid var(--border); display:flex; justify-content:space-between; align-items:center;">
        <h3 style="font-size:1.1rem; color:#fff; display:flex; align-items:center; gap:8px;">🎞️ Cadência Dinâmica B-Roll & Prevenção de Fadiga Visual</h3>
        <button style="background:none; border:none; color:var(--text-muted); font-size:1.4rem; cursor:pointer;" onclick="fecharBrollPacerModal()">&times;</button>
      </div>
      <div id="broll-pacer-list" style="padding:20px; overflow-y:auto; flex:1; display:flex; flex-direction:column; gap:12px;"></div>
      <div style="padding:12px 20px; border-top:1px solid var(--border); display:flex; justify-content:space-between; align-items:center; background:var(--card-bg);">
        <button class="btn" style="background:#38bdf8; color:#0f172a; font-weight:700;" onclick="aplicarBrollSlotsAuto()">✨ Inserir B-Roll Slots Automaticamente</button>
        <button class="btn btn-secondary" onclick="fecharBrollPacerModal()">Fechar</button>
      </div>
    </div>
  </div>

  <!-- Modal de Sound Design & Foley -->
  <div id="foley-modal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.75); z-index:9999; align-items:center; justify-content:center;">
    <div style="background:var(--panel-bg); border:1px solid var(--border); border-radius:10px; width:760px; max-width:92%; max-height:85vh; display:flex; flex-direction:column; overflow:hidden; box-shadow:0 20px 25px -5px rgba(0,0,0,0.5);">
      <div style="padding:16px 20px; border-bottom:1px solid var(--border); display:flex; justify-content:space-between; align-items:center;">
        <h3 style="font-size:1.1rem; color:#fff; display:flex; align-items:center; gap:8px;">🔊 Diretor de Sound Design & Foley Automático</h3>
        <button style="background:none; border:none; color:var(--text-muted); font-size:1.4rem; cursor:pointer;" onclick="fecharFoleyModal()">&times;</button>
      </div>
      <div id="foley-list" style="padding:20px; overflow-y:auto; flex:1; display:flex; flex-direction:column; gap:12px;"></div>
      <div style="padding:12px 20px; border-top:1px solid var(--border); display:flex; justify-content:flex-end; align-items:center; background:var(--card-bg);">
        <button class="btn btn-secondary" onclick="fecharFoleyModal()">Fechar</button>
      </div>
    </div>
  </div>

  <!-- Modal de Emulador de Película 35mm -->
  <div id="film-stock-modal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.75); z-index:9999; align-items:center; justify-content:center;">
    <div style="background:var(--panel-bg); border:1px solid var(--border); border-radius:10px; width:760px; max-width:92%; max-height:85vh; display:flex; flex-direction:column; overflow:hidden; box-shadow:0 20px 25px -5px rgba(0,0,0,0.5);">
      <div style="padding:16px 20px; border-bottom:1px solid var(--border); display:flex; justify-content:space-between; align-items:center;">
        <h3 style="font-size:1.1rem; color:#fff; display:flex; align-items:center; gap:8px;">📽️ Emulador de Película Analógica & Granulação Estocástica</h3>
        <button style="background:none; border:none; color:var(--text-muted); font-size:1.4rem; cursor:pointer;" onclick="fecharFilmStockModal()">&times;</button>
      </div>
      <div id="film-stock-list" style="padding:20px; overflow-y:auto; flex:1; display:flex; flex-direction:column; gap:12px;"></div>
      <div style="padding:12px 20px; border-top:1px solid var(--border); display:flex; justify-content:flex-end; align-items:center; background:var(--card-bg);">
        <button class="btn btn-secondary" onclick="fecharFilmStockModal()">Fechar</button>
      </div>
    </div>
  </div>

  <!-- Modal de Otimizador de Metadados SEO & CTR -->
  <div id="ctr-optimizer-modal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.75); z-index:9999; align-items:center; justify-content:center;">
    <div style="background:var(--panel-bg); border:1px solid var(--border); border-radius:10px; width:780px; max-width:92%; max-height:85vh; display:flex; flex-direction:column; overflow:hidden; box-shadow:0 20px 25px -5px rgba(0,0,0,0.5);">
      <div style="padding:16px 20px; border-bottom:1px solid var(--border); display:flex; justify-content:space-between; align-items:center;">
        <h3 style="font-size:1.1rem; color:#fff; display:flex; align-items:center; gap:8px;">📈 Otimizador de Títulos CTR, Capítulos e Tags SEO</h3>
        <button style="background:none; border:none; color:var(--text-muted); font-size:1.4rem; cursor:pointer;" onclick="fecharCTROptimizerModal()">&times;</button>
      </div>
      <div id="ctr-optimizer-content" style="padding:20px; overflow-y:auto; flex:1; display:flex; flex-direction:column; gap:12px;"></div>
      <div style="padding:12px 20px; border-top:1px solid var(--border); display:flex; justify-content:flex-end; align-items:center; background:var(--card-bg);">
        <button class="btn btn-secondary" onclick="fecharCTROptimizerModal()">Fechar</button>
      </div>
    </div>
  </div>

  <!-- Modal de Denoise Espectral de Voz -->
  <div id="denoise-modal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.75); z-index:9999; align-items:center; justify-content:center;">
    <div style="background:var(--panel-bg); border:1px solid var(--border); border-radius:10px; width:760px; max-width:92%; max-height:85vh; display:flex; flex-direction:column; overflow:hidden; box-shadow:0 20px 25px -5px rgba(0,0,0,0.5);">
      <div style="padding:16px 20px; border-bottom:1px solid var(--border); display:flex; justify-content:space-between; align-items:center;">
        <h3 style="font-size:1.1rem; color:#fff; display:flex; align-items:center; gap:8px;">🎙️ Isolamento Espectral de Ruído & Denoise Vocal</h3>
        <button style="background:none; border:none; color:var(--text-muted); font-size:1.4rem; cursor:pointer;" onclick="fecharDenoiseModal()">&times;</button>
      </div>
      <div id="denoise-list" style="padding:20px; overflow-y:auto; flex:1; display:flex; flex-direction:column; gap:12px;"></div>
      <div style="padding:12px 20px; border-top:1px solid var(--border); display:flex; justify-content:flex-end; align-items:center; background:var(--card-bg);">
        <button class="btn btn-secondary" onclick="fecharDenoiseModal()">Fechar</button>
      </div>
    </div>
  </div>

  <!-- Modal de Transições Cinemáticas Inteligentes -->
  <div id="transitions-modal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.75); z-index:9999; align-items:center; justify-content:center;">
    <div style="background:var(--panel-bg); border:1px solid var(--border); border-radius:10px; width:760px; max-width:92%; max-height:85vh; display:flex; flex-direction:column; overflow:hidden; box-shadow:0 20px 25px -5px rgba(0,0,0,0.5);">
      <div style="padding:16px 20px; border-bottom:1px solid var(--border); display:flex; justify-content:space-between; align-items:center;">
        <h3 style="font-size:1.1rem; color:#fff; display:flex; align-items:center; gap:8px;">🔀 Diretor de Transições Cinemáticas Inteligentes</h3>
        <button style="background:none; border:none; color:var(--text-muted); font-size:1.4rem; cursor:pointer;" onclick="fecharTransitionsModal()">&times;</button>
      </div>
      <div id="transitions-list" style="padding:20px; overflow-y:auto; flex:1; display:flex; flex-direction:column; gap:12px;"></div>
      <div style="padding:12px 20px; border-top:1px solid var(--border); display:flex; justify-content:flex-end; align-items:center; background:var(--card-bg);">
        <button class="btn btn-secondary" onclick="fecharTransitionsModal()">Fechar</button>
      </div>
    </div>
  </div>

  <!-- Modal de Repurpose para YouTube Shorts 9:16 -->
  <div id="shorts-modal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.75); z-index:9999; align-items:center; justify-content:center;">
    <div style="background:var(--panel-bg); border:1px solid var(--border); border-radius:10px; width:760px; max-width:92%; max-height:85vh; display:flex; flex-direction:column; overflow:hidden; box-shadow:0 20px 25px -5px rgba(0,0,0,0.5);">
      <div style="padding:16px 20px; border-bottom:1px solid var(--border); display:flex; justify-content:space-between; align-items:center;">
        <h3 style="font-size:1.1rem; color:#fff; display:flex; align-items:center; gap:8px;">📱 Repurposer de Vídeos Verticais (Shorts / Reels)</h3>
        <button style="background:none; border:none; color:var(--text-muted); font-size:1.4rem; cursor:pointer;" onclick="fecharShortsModal()">&times;</button>
      </div>
      <div id="shorts-list" style="padding:20px; overflow-y:auto; flex:1; display:flex; flex-direction:column; gap:12px;"></div>
      <div style="padding:12px 20px; border-top:1px solid var(--border); display:flex; justify-content:flex-end; align-items:center; background:var(--card-bg);">
        <button class="btn btn-secondary" onclick="fecharShortsModal()">Fechar</button>
      </div>
    </div>
  </div>

  <!-- Modal de Checkpoint & Crash Recovery -->
  <div id="recovery-modal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.75); z-index:9999; align-items:center; justify-content:center;">
    <div style="background:var(--panel-bg); border:1px solid var(--border); border-radius:10px; width:760px; max-width:92%; max-height:85vh; display:flex; flex-direction:column; overflow:hidden; box-shadow:0 20px 25px -5px rgba(0,0,0,0.5);">
      <div style="padding:16px 20px; border-bottom:1px solid var(--border); display:flex; justify-content:space-between; align-items:center;">
        <h3 style="font-size:1.1rem; color:#fff; display:flex; align-items:center; gap:8px;">🛡️ Resiliência & Recuperação de Renderização Interrompida</h3>
        <button style="background:none; border:none; color:var(--text-muted); font-size:1.4rem; cursor:pointer;" onclick="fecharRecoveryModal()">&times;</button>
      </div>
      <div id="recovery-content" style="padding:20px; overflow-y:auto; flex:1; display:flex; flex-direction:column; gap:12px;"></div>
      <div style="padding:12px 20px; border-top:1px solid var(--border); display:flex; justify-content:flex-end; align-items:center; background:var(--card-bg);">
        <button class="btn btn-secondary" onclick="fecharRecoveryModal()">Fechar</button>
      </div>
    </div>
  </div>

  <!-- Modal de Otimizador de Bitrate & Compressão -->
  <div id="bitrate-modal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.75); z-index:9999; align-items:center; justify-content:center;">
    <div style="background:var(--panel-bg); border:1px solid var(--border); border-radius:10px; width:760px; max-width:92%; max-height:85vh; display:flex; flex-direction:column; overflow:hidden; box-shadow:0 20px 25px -5px rgba(0,0,0,0.5);">
      <div style="padding:16px 20px; border-bottom:1px solid var(--border); display:flex; justify-content:space-between; align-items:center;">
        <h3 style="font-size:1.1rem; color:#fff; display:flex; align-items:center; gap:8px;">🚀 Otimizador Preditivo de Bitrate & Compressão (VBR)</h3>
        <button style="background:none; border:none; color:var(--text-muted); font-size:1.4rem; cursor:pointer;" onclick="fecharBitrateModal()">&times;</button>
      </div>
      <div id="bitrate-list" style="padding:20px; overflow-y:auto; flex:1; display:flex; flex-direction:column; gap:12px;"></div>
      <div style="padding:12px 20px; border-top:1px solid var(--border); display:flex; justify-content:flex-end; align-items:center; background:var(--card-bg);">
        <button class="btn btn-secondary" onclick="fecharBitrateModal()">Fechar</button>
      </div>
    </div>
  </div>

  <!-- Modal de Controle de Qualidade (QC Vídeo) -->
  <div id="qc-modal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.75); z-index:9999; align-items:center; justify-content:center;">
    <div style="background:var(--panel-bg); border:1px solid var(--border); border-radius:10px; width:760px; max-width:92%; max-height:85vh; display:flex; flex-direction:column; overflow:hidden; box-shadow:0 20px 25px -5px rgba(0,0,0,0.5);">
      <div style="padding:16px 20px; border-bottom:1px solid var(--border); display:flex; justify-content:space-between; align-items:center;">
        <h3 style="font-size:1.1rem; color:#fff; display:flex; align-items:center; gap:8px;">🔍 Auditoria QC & Detecção de Anomalias Visuais</h3>
        <button style="background:none; border:none; color:var(--text-muted); font-size:1.4rem; cursor:pointer;" onclick="fecharQCModal()">&times;</button>
      </div>
      <div id="qc-list" style="padding:20px; overflow-y:auto; flex:1; display:flex; flex-direction:column; gap:12px;"></div>
      <div style="padding:12px 20px; border-top:1px solid var(--border); display:flex; justify-content:flex-end; align-items:center; background:var(--card-bg);">
        <button class="btn btn-secondary" onclick="fecharQCModal()">Fechar</button>
      </div>
    </div>
  </div>

  <!-- Modal de Áudio Doppler 3D -->
  <div id="doppler-modal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.75); z-index:9999; align-items:center; justify-content:center;">
    <div style="background:var(--panel-bg); border:1px solid var(--border); border-radius:10px; width:720px; max-width:92%; max-height:85vh; display:flex; flex-direction:column; overflow:hidden; box-shadow:0 20px 25px -5px rgba(0,0,0,0.5);">
      <div style="padding:16px 20px; border-bottom:1px solid var(--border); display:flex; justify-content:space-between; align-items:center;">
        <h3 style="font-size:1.1rem; color:#fff; display:flex; align-items:center; gap:8px;">🏎️ Automação de Efeito Doppler & Pan Estéreo 3D</h3>
        <button style="background:none; border:none; color:var(--text-muted); font-size:1.4rem; cursor:pointer;" onclick="fecharDopplerModal()">&times;</button>
      </div>
      <div style="padding:16px 20px; background:var(--card-bg); border-bottom:1px solid var(--border); display:flex; gap:16px; align-items:center;">
        <div>
          <label style="font-size:0.8rem; color:var(--text-muted);">Velocidade (km/h):</label>
          <input type="number" id="doppler-speed" value="140" style="width:90px; padding:6px; background:#0f172a; border:1px solid var(--border); border-radius:4px; color:#fff; font-size:0.85rem;">
        </div>
        <div>
          <label style="font-size:0.8rem; color:var(--text-muted);">Direção Espacial:</label>
          <select id="doppler-dir" style="padding:6px; background:#0f172a; border:1px solid var(--border); border-radius:4px; color:#fff; font-size:0.85rem;">
            <option value="left_to_right">Esquerda ➔ Direita</option>
            <option value="right_to_left">Direita ➔ Esquerda</option>
          </select>
        </div>
        <button class="btn" style="background:#06b6d4; color:#0f172a; font-weight:700; margin-top:16px;" onclick="calcularDopplerCustom()">Recalcular</button>
      </div>
      <div id="doppler-content" style="padding:20px; overflow-y:auto; flex:1; display:flex; flex-direction:column; gap:12px;"></div>
      <div style="padding:12px 20px; border-top:1px solid var(--border); display:flex; justify-content:flex-end; align-items:center; background:var(--card-bg);">
        <button class="btn btn-secondary" onclick="fecharDopplerModal()">Fechar</button>
      </div>
    </div>
  </div>

  <!-- Modal de Preditor de Abandono (Drop-Off) -->
  <div id="dropoff-modal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.75); z-index:9999; align-items:center; justify-content:center;">
    <div style="background:var(--panel-bg); border:1px solid var(--border); border-radius:10px; width:760px; max-width:92%; max-height:85vh; display:flex; flex-direction:column; overflow:hidden; box-shadow:0 20px 25px -5px rgba(0,0,0,0.5);">
      <div style="padding:16px 20px; border-bottom:1px solid var(--border); display:flex; justify-content:space-between; align-items:center;">
        <h3 style="font-size:1.1rem; color:#fff; display:flex; align-items:center; gap:8px;">📉 Preditor de Abandono de Audiência (Drop-off Curve)</h3>
        <button style="background:none; border:none; color:var(--text-muted); font-size:1.4rem; cursor:pointer;" onclick="fecharDropoffModal()">&times;</button>
      </div>
      <div id="dropoff-list" style="padding:20px; overflow-y:auto; flex:1; display:flex; flex-direction:column; gap:12px;"></div>
      <div style="padding:12px 20px; border-top:1px solid var(--border); display:flex; justify-content:flex-end; align-items:center; background:var(--card-bg);">
        <button class="btn btn-secondary" onclick="fecharDropoffModal()">Fechar</button>
      </div>
    </div>
  </div>

  <!-- Modal de Legendas Dinâmicas (Karaoke) -->
  <div id="dynamic-subtitles-modal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.75); z-index:9999; align-items:center; justify-content:center;">
    <div style="background:var(--panel-bg); border:1px solid var(--border); border-radius:10px; width:760px; max-width:92%; max-height:85vh; display:flex; flex-direction:column; overflow:hidden; box-shadow:0 20px 25px -5px rgba(0,0,0,0.5);">
      <div style="padding:16px 20px; border-bottom:1px solid var(--border); display:flex; justify-content:space-between; align-items:center;">
        <h3 style="font-size:1.1rem; color:#fff; display:flex; align-items:center; gap:8px;">💬 Legendas Animadas Dinâmicas (Karaoke .ASS)</h3>
        <button style="background:none; border:none; color:var(--text-muted); font-size:1.4rem; cursor:pointer;" onclick="fecharDynamicSubtitlesModal()">&times;</button>
      </div>
      <div id="dynamic-subtitles-content" style="padding:20px; overflow-y:auto; flex:1; display:flex; flex-direction:column; gap:12px;"></div>
      <div style="padding:12px 20px; border-top:1px solid var(--border); display:flex; justify-content:flex-end; align-items:center; background:var(--card-bg);">
        <button class="btn btn-secondary" onclick="fecharDynamicSubtitlesModal()">Fechar</button>
      </div>
    </div>
  </div>

  <!-- Modal de Alinhador de Cortes por BPM -->
  <div id="bpm-aligner-modal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.75); z-index:9999; align-items:center; justify-content:center;">
    <div style="background:var(--panel-bg); border:1px solid var(--border); border-radius:10px; width:760px; max-width:92%; max-height:85vh; display:flex; flex-direction:column; overflow:hidden; box-shadow:0 20px 25px -5px rgba(0,0,0,0.5);">
      <div style="padding:16px 20px; border-bottom:1px solid var(--border); display:flex; justify-content:space-between; align-items:center;">
        <h3 style="font-size:1.1rem; color:#fff; display:flex; align-items:center; gap:8px;">🎵 Alinhador de Cortes na Grade Musical (BPM)</h3>
        <button style="background:none; border:none; color:var(--text-muted); font-size:1.4rem; cursor:pointer;" onclick="fecharBPMAlignerModal()">&times;</button>
      </div>
      <div style="padding:14px 20px; background:var(--card-bg); border-bottom:1px solid var(--border); display:flex; gap:16px; align-items:center;">
        <div>
          <label style="font-size:0.8rem; color:var(--text-muted);">BPM da Trilha:</label>
          <input type="number" id="bpm-input" value="120" style="width:80px; padding:6px; background:#0f172a; border:1px solid var(--border); border-radius:4px; color:#fff; font-size:0.85rem;">
        </div>
        <div>
          <label style="font-size:0.8rem; color:var(--text-muted);">Modo de Alinhamento:</label>
          <select id="bpm-mode" style="padding:6px; background:#0f172a; border:1px solid var(--border); border-radius:4px; color:#fff; font-size:0.85rem;">
            <option value="full_measure">Compasso Inteiro (4 Tempos)</option>
            <option value="two_measures">Dois Compassos (8 Tempos Épicos)</option>
            <option value="quarter_note">Semínima (1 Tempo Rápido)</option>
          </select>
        </div>
        <button class="btn" style="background:#8b5cf6; color:#fff; font-weight:700; margin-top:16px;" onclick="aplicarAlinhamentoBPM()">Quantizar Cenas</button>
      </div>
      <div id="bpm-aligner-list" style="padding:20px; overflow-y:auto; flex:1; display:flex; flex-direction:column; gap:12px;"></div>
      <div style="padding:12px 20px; border-top:1px solid var(--border); display:flex; justify-content:flex-end; align-items:center; background:var(--card-bg);">
        <button class="btn btn-secondary" onclick="fecharBPMAlignerModal()">Fechar</button>
      </div>
    </div>
  </div>

  <!-- Modal de Curva de Tensão (3 Atos) -->
  <div id="tension-curve-modal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.75); z-index:9999; align-items:center; justify-content:center;">
    <div style="background:var(--panel-bg); border:1px solid var(--border); border-radius:10px; width:760px; max-width:92%; max-height:85vh; display:flex; flex-direction:column; overflow:hidden; box-shadow:0 20px 25px -5px rgba(0,0,0,0.5);">
      <div style="padding:16px 20px; border-bottom:1px solid var(--border); display:flex; justify-content:space-between; align-items:center;">
        <h3 style="font-size:1.1rem; color:#fff; display:flex; align-items:center; gap:8px;">📈 Curva de Tensão Narrativa (Hollywood 3-Act Arc)</h3>
        <button style="background:none; border:none; color:var(--text-muted); font-size:1.4rem; cursor:pointer;" onclick="fecharTensionCurveModal()">&times;</button>
      </div>
      <div id="tension-curve-list" style="padding:20px; overflow-y:auto; flex:1; display:flex; flex-direction:column; gap:12px;"></div>
      <div style="padding:12px 20px; border-top:1px solid var(--border); display:flex; justify-content:flex-end; align-items:center; background:var(--card-bg);">
        <button class="btn btn-secondary" onclick="fecharTensionCurveModal()">Fechar</button>
      </div>
    </div>
  </div>

  <!-- Modal de Marca d'Água & Anti-Pirataria -->
  <div id="watermark-modal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.75); z-index:9999; align-items:center; justify-content:center;">
    <div style="background:var(--panel-bg); border:1px solid var(--border); border-radius:10px; width:720px; max-width:92%; max-height:85vh; display:flex; flex-direction:column; overflow:hidden; box-shadow:0 20px 25px -5px rgba(0,0,0,0.5);">
      <div style="padding:16px 20px; border-bottom:1px solid var(--border); display:flex; justify-content:space-between; align-items:center;">
        <h3 style="font-size:1.1rem; color:#fff; display:flex; align-items:center; gap:8px;">🛡️ Marca d'Água de Branding & Proteção Copyright</h3>
        <button style="background:none; border:none; color:var(--text-muted); font-size:1.4rem; cursor:pointer;" onclick="fecharWatermarkModal()">&times;</button>
      </div>
      <div style="padding:20px; display:flex; flex-direction:column; gap:12px;">
        <div>
          <label style="font-size:0.85rem; color:var(--text-muted);">Caminho do Arquivo de Logo (PNG Transparente):</label>
          <input type="text" id="wm-path" value="assets/branding/logo_watermark.png" style="width:100%; padding:8px; background:#0f172a; border:1px solid var(--border); border-radius:6px; color:#fff; font-size:0.85rem; margin-top:4px;">
        </div>
        <div style="display:flex; gap:16px;">
          <div style="flex:1;">
            <label style="font-size:0.85rem; color:var(--text-muted);">Posição na Tela:</label>
            <select id="wm-pos" style="width:100%; padding:8px; background:#0f172a; border:1px solid var(--border); border-radius:6px; color:#fff; font-size:0.85rem; margin-top:4px;">
              <option value="bottom_right">Canto Inferior Direito (Padrão)</option>
              <option value="top_right">Canto Superior Direito</option>
              <option value="bottom_left">Canto Inferior Esquerdo</option>
              <option value="top_left">Canto Superior Esquerdo</option>
            </select>
          </div>
          <div style="flex:1;">
            <label style="font-size:0.85rem; color:var(--text-muted);">Opacidade (0.1 a 1.0):</label>
            <input type="number" id="wm-opacity" step="0.05" min="0.1" max="1.0" value="0.55" style="width:100%; padding:8px; background:#0f172a; border:1px solid var(--border); border-radius:6px; color:#fff; font-size:0.85rem; margin-top:4px;">
          </div>
        </div>
        <div style="background:rgba(16,185,129,0.06); border:1px solid rgba(16,185,129,0.25); border-radius:6px; padding:10px; font-size:0.82rem; color:#a7f3d0; margin-top:4px;">
          🔒 O filtro aplicará Safe Margin de 35px para não colidir com controles do player do YouTube, além de fade-in transparente suave de 1.5s.
        </div>
      </div>
      <div style="padding:12px 20px; border-top:1px solid var(--border); display:flex; justify-content:space-between; align-items:center; background:var(--card-bg);">
        <button class="btn" style="background:#10b981; color:#0f172a; font-weight:700;" onclick="aplicarWatermarkConfig()">Aplicar Marca d'Água</button>
        <button class="btn btn-secondary" onclick="fecharWatermarkModal()">Fechar</button>
      </div>
    </div>
  </div>

  <!-- Modal de Tone Mapping HDR Rec.709 -->
  <div id="hdr-tonemap-modal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.75); z-index:9999; align-items:center; justify-content:center;">
    <div style="background:var(--panel-bg); border:1px solid var(--border); border-radius:10px; width:760px; max-width:92%; max-height:85vh; display:flex; flex-direction:column; overflow:hidden; box-shadow:0 20px 25px -5px rgba(0,0,0,0.5);">
      <div style="padding:16px 20px; border-bottom:1px solid var(--border); display:flex; justify-content:space-between; align-items:center;">
        <h3 style="font-size:1.1rem; color:#fff; display:flex; align-items:center; gap:8px;">🎨 Tone Mapping HDR / Log ➔ SDR Rec.709</h3>
        <button style="background:none; border:none; color:var(--text-muted); font-size:1.4rem; cursor:pointer;" onclick="fecharHDRToneMapModal()">&times;</button>
      </div>
      <div id="hdr-tonemap-list" style="padding:20px; overflow-y:auto; flex:1; display:flex; flex-direction:column; gap:12px;"></div>
      <div style="padding:12px 20px; border-top:1px solid var(--border); display:flex; justify-content:flex-end; align-items:center; background:var(--card-bg);">
        <button class="btn btn-secondary" onclick="fecharHDRToneMapModal()">Fechar</button>
      </div>
    </div>
  </div>

  <!-- Modal de Foco Facial em Miniaturas -->
  <div id="face-detector-modal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.75); z-index:9999; align-items:center; justify-content:center;">
    <div style="background:var(--panel-bg); border:1px solid var(--border); border-radius:10px; width:760px; max-width:92%; max-height:85vh; display:flex; flex-direction:column; overflow:hidden; box-shadow:0 20px 25px -5px rgba(0,0,0,0.5);">
      <div style="padding:16px 20px; border-bottom:1px solid var(--border); display:flex; justify-content:space-between; align-items:center;">
        <h3 style="font-size:1.1rem; color:#fff; display:flex; align-items:center; gap:8px;">👤 Detector de Expressões Faciais & Crop Regra dos Terços</h3>
        <button style="background:none; border:none; color:var(--text-muted); font-size:1.4rem; cursor:pointer;" onclick="fecharFaceDetectorModal()">&times;</button>
      </div>
      <div id="face-detector-list" style="padding:20px; overflow-y:auto; flex:1; display:flex; flex-direction:column; gap:12px;"></div>
      <div style="padding:12px 20px; border-top:1px solid var(--border); display:flex; justify-content:flex-end; align-items:center; background:var(--card-bg);">
        <button class="btn btn-secondary" onclick="fecharFaceDetectorModal()">Fechar</button>
      </div>
    </div>
  </div>

  <!-- Modal de Loop Infinito de Trilha -->
  <div id="soundtrack-loop-modal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.75); z-index:9999; align-items:center; justify-content:center;">
    <div style="background:var(--panel-bg); border:1px solid var(--border); border-radius:10px; width:720px; max-width:92%; max-height:85vh; display:flex; flex-direction:column; overflow:hidden; box-shadow:0 20px 25px -5px rgba(0,0,0,0.5);">
      <div style="padding:16px 20px; border-bottom:1px solid var(--border); display:flex; justify-content:space-between; align-items:center;">
        <h3 style="font-size:1.1rem; color:#fff; display:flex; align-items:center; gap:8px;">🔁 Extensor e Loop Infinito de Trilha Sonora</h3>
        <button style="background:none; border:none; color:var(--text-muted); font-size:1.4rem; cursor:pointer;" onclick="fecharSoundtrackLoopModal()">&times;</button>
      </div>
      <div style="padding:14px 20px; background:var(--card-bg); border-bottom:1px solid var(--border); display:flex; gap:16px; align-items:center;">
        <div>
          <label style="font-size:0.8rem; color:var(--text-muted);">Duração da Música (s):</label>
          <input type="number" id="music-dur-input" value="90" style="width:80px; padding:6px; background:#0f172a; border:1px solid var(--border); border-radius:4px; color:#fff; font-size:0.85rem;">
        </div>
        <div>
          <label style="font-size:0.8rem; color:var(--text-muted);">Crossfade Suave (s):</label>
          <input type="number" step="0.5" id="music-cross-input" value="3.0" style="width:70px; padding:6px; background:#0f172a; border:1px solid var(--border); border-radius:4px; color:#fff; font-size:0.85rem;">
        </div>
        <button class="btn" style="background:#a855f7; color:#fff; font-weight:700; margin-top:16px;" onclick="aplicarLoopStretcher()">Recalcular Loops</button>
      </div>
      <div id="soundtrack-loop-content" style="padding:20px; overflow-y:auto; flex:1; display:flex; flex-direction:column; gap:12px;"></div>
      <div style="padding:12px 20px; border-top:1px solid var(--border); display:flex; justify-content:flex-end; align-items:center; background:var(--card-bg);">
        <button class="btn btn-secondary" onclick="fecharSoundtrackLoopModal()">Fechar</button>
      </div>
    </div>
  </div>

  <!-- Modal de Exportador de Cutpack Social -->
  <div id="cutpack-modal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.75); z-index:9999; align-items:center; justify-content:center;">
    <div style="background:var(--panel-bg); border:1px solid var(--border); border-radius:10px; width:760px; max-width:92%; max-height:85vh; display:flex; flex-direction:column; overflow:hidden; box-shadow:0 20px 25px -5px rgba(0,0,0,0.5);">
      <div style="padding:16px 20px; border-bottom:1px solid var(--border); display:flex; justify-content:space-between; align-items:center;">
        <h3 style="font-size:1.1rem; color:#fff; display:flex; align-items:center; gap:8px;">📦 Exportador de Cutpack Social Omnichannel</h3>
        <button style="background:none; border:none; color:var(--text-muted); font-size:1.4rem; cursor:pointer;" onclick="fecharCutpackModal()">&times;</button>
      </div>
      <div id="cutpack-list" style="padding:20px; overflow-y:auto; flex:1; display:flex; flex-direction:column; gap:12px;"></div>
      <div style="padding:12px 20px; border-top:1px solid var(--border); display:flex; justify-content:flex-end; align-items:center; background:var(--card-bg);">
        <button class="btn btn-secondary" onclick="fecharCutpackModal()">Fechar</button>
      </div>
    </div>
  </div>

  <!-- Modal de Lower Thirds Animados -->
  <div id="lower-thirds-modal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.75); z-index:9999; align-items:center; justify-content:center;">
    <div style="background:var(--panel-bg); border:1px solid var(--border); border-radius:10px; width:760px; max-width:92%; max-height:85vh; display:flex; flex-direction:column; overflow:hidden; box-shadow:0 20px 25px -5px rgba(0,0,0,0.5);">
      <div style="padding:16px 20px; border-bottom:1px solid var(--border); display:flex; justify-content:space-between; align-items:center;">
        <h3 style="font-size:1.1rem; color:#fff; display:flex; align-items:center; gap:8px;">🏷️ Lower Thirds & Grafismos Animados</h3>
        <button style="background:none; border:none; color:var(--text-muted); font-size:1.4rem; cursor:pointer;" onclick="fecharLowerThirdsModal()">&times;</button>
      </div>
      <div id="lower-thirds-content" style="padding:20px; overflow-y:auto; flex:1; display:flex; flex-direction:column; gap:12px;"></div>
      <div style="padding:12px 20px; border-top:1px solid var(--border); display:flex; justify-content:flex-end; align-items:center; background:var(--card-bg);">
        <button class="btn btn-secondary" onclick="fecharLowerThirdsModal()">Fechar</button>
      </div>
    </div>
  </div>

  <!-- Modal de Auditoria Estética & Simetria -->
  <div id="symmetry-modal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.75); z-index:9999; align-items:center; justify-content:center;">
    <div style="background:var(--panel-bg); border:1px solid var(--border); border-radius:10px; width:760px; max-width:92%; max-height:85vh; display:flex; flex-direction:column; overflow:hidden; box-shadow:0 20px 25px -5px rgba(0,0,0,0.5);">
      <div style="padding:16px 20px; border-bottom:1px solid var(--border); display:flex; justify-content:space-between; align-items:center;">
        <h3 style="font-size:1.1rem; color:#fff; display:flex; align-items:center; gap:8px;">📐 Auditoria de Simetria e Composição Estética</h3>
        <button style="background:none; border:none; color:var(--text-muted); font-size:1.4rem; cursor:pointer;" onclick="fecharSymmetryModal()">&times;</button>
      </div>
      <div id="symmetry-list" style="padding:20px; overflow-y:auto; flex:1; display:flex; flex-direction:column; gap:12px;"></div>
      <div style="padding:12px 20px; border-top:1px solid var(--border); display:flex; justify-content:flex-end; align-items:center; background:var(--card-bg);">
        <button class="btn btn-secondary" onclick="fecharSymmetryModal()">Fechar</button>
      </div>
    </div>
  </div>

  <!-- Modal de Áudio Surround 5.1 -->
  <div id="surround-modal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.75); z-index:9999; align-items:center; justify-content:center;">
    <div style="background:var(--panel-bg); border:1px solid var(--border); border-radius:10px; width:720px; max-width:92%; max-height:85vh; display:flex; flex-direction:column; overflow:hidden; box-shadow:0 20px 25px -5px rgba(0,0,0,0.5);">
      <div style="padding:16px 20px; border-bottom:1px solid var(--border); display:flex; justify-content:space-between; align-items:center;">
        <h3 style="font-size:1.1rem; color:#fff; display:flex; align-items:center; gap:8px;">🔊 Upmix Surround 5.1 (Home Theater & Cinema)</h3>
        <button style="background:none; border:none; color:var(--text-muted); font-size:1.4rem; cursor:pointer;" onclick="fecharSurroundModal()">&times;</button>
      </div>
      <div style="padding:14px 20px; background:var(--card-bg); border-bottom:1px solid var(--border); display:flex; gap:16px; align-items:center;">
        <div>
          <label style="font-size:0.8rem; color:var(--text-muted);">Ganho Canal Central Vocal (dB):</label>
          <input type="number" step="0.5" id="surround-boost" value="2.0" style="width:70px; padding:6px; background:#0f172a; border:1px solid var(--border); border-radius:4px; color:#fff; font-size:0.85rem;">
        </div>
        <button class="btn" style="background:#6366f1; color:#fff; font-weight:700; margin-top:16px;" onclick="calcularSurroundPreview()">Recalcular Matriz</button>
      </div>
      <div id="surround-content" style="padding:20px; overflow-y:auto; flex:1; display:flex; flex-direction:column; gap:12px;"></div>
      <div style="padding:12px 20px; border-top:1px solid var(--border); display:flex; justify-content:space-between; align-items:center; background:var(--card-bg);">
        <button class="btn" style="background:#6366f1; color:#fff; font-weight:700;" onclick="aplicarSurroundUpmix()">Aplicar 5.1 ao Master</button>
        <button class="btn btn-secondary" onclick="fecharSurroundModal()">Fechar</button>
      </div>
    </div>
  </div>

  <!-- Modal de Paleta Cromática de Humor -->
  <div id="palette-modal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.75); z-index:9999; align-items:center; justify-content:center;">
    <div style="background:var(--panel-bg); border:1px solid var(--border); border-radius:10px; width:720px; max-width:92%; max-height:85vh; display:flex; flex-direction:column; overflow:hidden; box-shadow:0 20px 25px -5px rgba(0,0,0,0.5);">
      <div style="padding:16px 20px; border-bottom:1px solid var(--border); display:flex; justify-content:space-between; align-items:center;">
        <h3 style="font-size:1.1rem; color:#fff; display:flex; align-items:center; gap:8px;">🎨 Extrator de Paleta Cromática e Psicologia de Humor</h3>
        <button style="background:none; border:none; color:var(--text-muted); font-size:1.4rem; cursor:pointer;" onclick="fecharPaletteModal()">&times;</button>
      </div>
      <div id="palette-content" style="padding:20px; overflow-y:auto; flex:1; display:flex; flex-direction:column; gap:12px;"></div>
      <div style="padding:12px 20px; border-top:1px solid var(--border); display:flex; justify-content:flex-end; align-items:center; background:var(--card-bg);">
        <button class="btn btn-secondary" onclick="fecharPaletteModal()">Fechar</button>
      </div>
    </div>
  </div>

  <!-- Modal de Exportador NLE -->
  <div id="nle-modal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.75); z-index:9999; align-items:center; justify-content:center;">
    <div style="background:var(--panel-bg); border:1px solid var(--border); border-radius:10px; width:620px; max-width:92%; max-height:85vh; display:flex; flex-direction:column; overflow:hidden; box-shadow:0 20px 25px -5px rgba(0,0,0,0.5);">
      <div style="padding:16px 20px; border-bottom:1px solid var(--border); display:flex; justify-content:space-between; align-items:center;">
        <h3 style="font-size:1.1rem; color:#fff; display:flex; align-items:center; gap:8px;">🎬 Exportar Timeline NLE (Premiere / DaVinci Resolve)</h3>
        <button style="background:none; border:none; color:var(--text-muted); font-size:1.4rem; cursor:pointer;" onclick="fecharNLEModal()">&times;</button>
      </div>
      <div style="padding:20px; overflow-y:auto; flex:1; display:flex; flex-direction:column; gap:14px;">
        <div style="font-size:0.85rem; color:var(--text-muted);">
          Exporte o projeto montado diretamente para arquivos XML (Final Cut Pro / DaVinci Resolve) e EDL CMX 3600 para finalizar a pós-produção na sua suíte favorita.
        </div>
        <div style="display:flex; align-items:center; gap:10px;">
          <label style="font-size:0.85rem; color:var(--text-muted);">Taxa de Quadros (FPS):</label>
          <select id="nle-fps" style="padding:6px 10px; background:var(--card-bg); border:1px solid var(--border); color:#fff; border-radius:6px;">
            <option value="24">24.0 fps (Cinema)</option>
            <option value="29.97">29.97 fps (NTSC)</option>
            <option value="30" selected>30.0 fps (Web / YouTube)</option>
            <option value="60">60.0 fps (High Motion)</option>
          </select>
        </div>
        <button class="btn btn-primary" onclick="exportarNLETimeline()">Exportar Arquivos NLE Agora</button>
        <div id="nle-result" style="margin-top:10px;"></div>
      </div>
      <div style="padding:12px 20px; border-top:1px solid var(--border); display:flex; justify-content:flex-end; align-items:center; background:var(--card-bg);">
        <button class="btn btn-secondary" onclick="fecharNLEModal()">Fechar</button>
      </div>
    </div>
  </div>

  <!-- Modal de Sidechain Ducking -->
  <div id="ducking-modal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.75); z-index:9999; align-items:center; justify-content:center;">
    <div style="background:var(--panel-bg); border:1px solid var(--border); border-radius:10px; width:640px; max-width:92%; max-height:85vh; display:flex; flex-direction:column; overflow:hidden; box-shadow:0 20px 25px -5px rgba(0,0,0,0.5);">
      <div style="padding:16px 20px; border-bottom:1px solid var(--border); display:flex; justify-content:space-between; align-items:center;">
        <h3 style="font-size:1.1rem; color:#fff; display:flex; align-items:center; gap:8px;">🎚️ Dynamic Sidechain Audio Ducking</h3>
        <button style="background:none; border:none; color:var(--text-muted); font-size:1.4rem; cursor:pointer;" onclick="fecharDuckingModal()">&times;</button>
      </div>
      <div style="padding:20px; overflow-y:auto; flex:1; display:flex; flex-direction:column; gap:12px;">
        <div style="display:flex; align-items:center; justify-content:space-between;">
          <label style="font-size:0.85rem; color:var(--text-muted);">Perfil de Ducking:</label>
          <select id="ducking-preset" style="padding:6px 10px; background:var(--card-bg); border:1px solid var(--border); color:#fff; border-radius:6px;" onchange="calcularDuckingPreview()">
            <option value="broadcast_standard" selected>Broadcast Padrão (-16dB)</option>
            <option value="cinematic_dramatic">Cinematográfico Dramático (-20dB)</option>
            <option value="youtube_fast_paced">YouTube Ágil / Ritmo Alto (-14dB)</option>
            <option value="subtle_documentary">Documentário Suave (-10dB)</option>
          </select>
        </div>
        <div id="ducking-preview-content"></div>
      </div>
      <div style="padding:12px 20px; border-top:1px solid var(--border); display:flex; justify-content:space-between; align-items:center; background:var(--card-bg);">
        <button class="btn btn-secondary" onclick="fecharDuckingModal()">Cancelar</button>
        <button class="btn btn-primary" onclick="aplicarDuckingSidechain()">Aplicar Ducking ao Roteiro</button>
      </div>
    </div>
  </div>

  <!-- Modal de Grade A/B de Thumbnails -->
  <div id="thumbnails-ab-modal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.75); z-index:9999; align-items:center; justify-content:center;">
    <div style="background:var(--panel-bg); border:1px solid var(--border); border-radius:10px; width:780px; max-width:92%; max-height:85vh; display:flex; flex-direction:column; overflow:hidden; box-shadow:0 20px 25px -5px rgba(0,0,0,0.5);">
      <div style="padding:16px 20px; border-bottom:1px solid var(--border); display:flex; justify-content:space-between; align-items:center;">
        <h3 style="font-size:1.1rem; color:#fff; display:flex; align-items:center; gap:8px;">🖼️ Matriz Estratégica A/B/C/D de Thumbnails</h3>
        <button style="background:none; border:none; color:var(--text-muted); font-size:1.4rem; cursor:pointer;" onclick="fecharThumbnailsABModal()">&times;</button>
      </div>
      <div id="thumbnails-ab-content" style="padding:20px; overflow-y:auto; flex:1;"></div>
      <div style="padding:12px 20px; border-top:1px solid var(--border); display:flex; justify-content:flex-end; align-items:center; background:var(--card-bg);">
        <button class="btn btn-secondary" onclick="fecharThumbnailsABModal()">Fechar</button>
      </div>
    </div>
  </div>

  <!-- Modal de Afinidade de CPU -->
  <div id="affinity-modal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.75); z-index:9999; align-items:center; justify-content:center;">
    <div style="background:var(--panel-bg); border:1px solid var(--border); border-radius:10px; width:640px; max-width:92%; max-height:85vh; display:flex; flex-direction:column; overflow:hidden; box-shadow:0 20px 25px -5px rgba(0,0,0,0.5);">
      <div style="padding:16px 20px; border-bottom:1px solid var(--border); display:flex; justify-content:space-between; align-items:center;">
        <h3 style="font-size:1.1rem; color:#fff; display:flex; align-items:center; gap:8px;">🛡️ Governador de Afinidade de CPU & Sistema Frio</h3>
        <button style="background:none; border:none; color:var(--text-muted); font-size:1.4rem; cursor:pointer;" onclick="fecharAffinityModal()">&times;</button>
      </div>
      <div style="padding:20px; overflow-y:auto; flex:1; display:flex; flex-direction:column; gap:12px;">
        <div style="display:flex; align-items:center; justify-content:space-between;">
          <label style="font-size:0.85rem; color:var(--text-muted);">Perfil Térmico / Arrefecimento:</label>
          <select id="affinity-profile" style="padding:6px 10px; background:var(--card-bg); border:1px solid var(--border); color:#fff; border-radius:6px;" onchange="calcularAffinity()">
            <option value="balanced" selected>Equilibrado (Reserva 2 núcleos pro Windows)</option>
            <option value="silent_cool">Silencioso / Baixa Temperatura (Usa 50% dos núcleos)</option>
            <option value="workstation_max">Workstation Máxima (Reserva apenas 1 núcleo)</option>
          </select>
        </div>
        <div id="affinity-content"></div>
      </div>
      <div style="padding:12px 20px; border-top:1px solid var(--border); display:flex; justify-content:flex-end; align-items:center; background:var(--card-bg);">
        <button class="btn btn-secondary" onclick="fecharAffinityModal()">Fechar</button>
      </div>
    </div>
  </div>

  <!-- Modal de Render Seletivo -->
  <div id="selective-rerender-modal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.75); z-index:9999; align-items:center; justify-content:center;">
    <div style="background:var(--panel-bg); border:1px solid var(--border); border-radius:10px; width:680px; max-width:92%; max-height:85vh; display:flex; flex-direction:column; overflow:hidden; box-shadow:0 20px 25px -5px rgba(0,0,0,0.5);">
      <div style="padding:16px 20px; border-bottom:1px solid var(--border); display:flex; justify-content:space-between; align-items:center;">
        <h3 style="font-size:1.1rem; color:#fff; display:flex; align-items:center; gap:8px;">⚡ Cache Cirúrgico & Render Seletivo (Zero GPU Waste)</h3>
        <button style="background:none; border:none; color:var(--text-muted); font-size:1.4rem; cursor:pointer;" onclick="fecharSelectiveRerenderModal()">&times;</button>
      </div>
      <div id="selective-rerender-content" style="padding:20px; overflow-y:auto; flex:1;"></div>
      <div style="padding:12px 20px; border-top:1px solid var(--border); display:flex; justify-content:flex-end; align-items:center; background:var(--card-bg);">
        <button class="btn btn-secondary" onclick="fecharSelectiveRerenderModal()">Fechar</button>
      </div>
    </div>
  </div>

  <!-- Modal de Poda de Cenas Inertes -->
  <div id="pruner-modal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.75); z-index:9999; align-items:center; justify-content:center;">
    <div style="background:var(--panel-bg); border:1px solid var(--border); border-radius:10px; width:650px; max-width:92%; max-height:85vh; display:flex; flex-direction:column; overflow:hidden; box-shadow:0 20px 25px -5px rgba(0,0,0,0.5);">
      <div style="padding:16px 20px; border-bottom:1px solid var(--border); display:flex; justify-content:space-between; align-items:center;">
        <h3 style="font-size:1.1rem; color:#fff; display:flex; align-items:center; gap:8px;">🧹 Higienizador Pré-Render de Cenas Inertes</h3>
        <button style="background:none; border:none; color:var(--text-muted); font-size:1.4rem; cursor:pointer;" onclick="fecharPrunerModal()">&times;</button>
      </div>
      <div id="pruner-content" style="padding:20px; overflow-y:auto; flex:1;"></div>
      <div style="padding:12px 20px; border-top:1px solid var(--border); display:flex; justify-content:space-between; align-items:center; background:var(--card-bg);">
        <button class="btn btn-secondary" onclick="fecharPrunerModal()">Cancelar</button>
        <button class="btn btn-primary" onclick="executarPodaInertes()">Aplicar Poda na Timeline</button>
      </div>
    </div>
  </div>

  <!-- Modal de Preservação de SSD -->
  <div id="ssd-fatigue-modal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.75); z-index:9999; align-items:center; justify-content:center;">
    <div style="background:var(--panel-bg); border:1px solid var(--border); border-radius:10px; width:650px; max-width:92%; max-height:85vh; display:flex; flex-direction:column; overflow:hidden; box-shadow:0 20px 25px -5px rgba(0,0,0,0.5);">
      <div style="padding:16px 20px; border-bottom:1px solid var(--border); display:flex; justify-content:space-between; align-items:center;">
        <h3 style="font-size:1.1rem; color:#fff; display:flex; align-items:center; gap:8px;">💾 Mitigador de Fadiga & Desgaste de SSD (NAND TBW)</h3>
        <button style="background:none; border:none; color:var(--text-muted); font-size:1.4rem; cursor:pointer;" onclick="fecharSSDFatigueModal()">&times;</button>
      </div>
      <div id="ssd-fatigue-content" style="padding:20px; overflow-y:auto; flex:1;"></div>
      <div style="padding:12px 20px; border-top:1px solid var(--border); display:flex; justify-content:flex-end; align-items:center; background:var(--card-bg);">
        <button class="btn btn-secondary" onclick="fecharSSDFatigueModal()">Fechar</button>
      </div>
    </div>
  </div>

  <!-- Modal de Áudio Pass-Through -->
  <div id="audio-passthrough-modal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.75); z-index:9999; align-items:center; justify-content:center;">
    <div style="background:var(--panel-bg); border:1px solid var(--border); border-radius:10px; width:650px; max-width:92%; max-height:85vh; display:flex; flex-direction:column; overflow:hidden; box-shadow:0 20px 25px -5px rgba(0,0,0,0.5);">
      <div style="padding:16px 20px; border-bottom:1px solid var(--border); display:flex; justify-content:space-between; align-items:center;">
        <h3 style="font-size:1.1rem; color:#fff; display:flex; align-items:center; gap:8px;">🎵 Lossless Audio Pass-Through (Zero CPU Waste)</h3>
        <button style="background:none; border:none; color:var(--text-muted); font-size:1.4rem; cursor:pointer;" onclick="fecharAudioPassThroughModal()">&times;</button>
      </div>
      <div style="padding:20px; overflow-y:auto; flex:1; display:flex; flex-direction:column; gap:12px;">
        <div style="display:flex; align-items:center; justify-content:space-between;">
          <label style="font-size:0.85rem; color:var(--text-muted);">Formato de Áudio Detectado:</label>
          <select id="audio-pt-codec" style="padding:6px 10px; background:var(--card-bg); border:1px solid var(--border); color:#fff; border-radius:6px;" onchange="avaliarAudioPassThrough()">
            <option value="aac" selected>AAC 48kHz Stereo (Cópia Direta -c:a copy)</option>
            <option value="mp3">MP3 44.1kHz Stereo (Compatível MP4)</option>
            <option value="pcm_s16le">WAV PCM 16-bit</option>
            <option value="flac">FLAC Lossless</option>
          </select>
        </div>
        <div id="audio-pt-content"></div>
      </div>
      <div style="padding:12px 20px; border-top:1px solid var(--border); display:flex; justify-content:flex-end; align-items:center; background:var(--card-bg);">
        <button class="btn btn-secondary" onclick="fecharAudioPassThroughModal()">Fechar</button>
      </div>
    </div>
  </div>

  <!-- Modal de Pacer Térmico -->
  <div id="thermal-pacer-modal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.75); z-index:9999; align-items:center; justify-content:center;">
    <div style="background:var(--panel-bg); border:1px solid var(--border); border-radius:10px; width:650px; max-width:92%; max-height:85vh; display:flex; flex-direction:column; overflow:hidden; box-shadow:0 20px 25px -5px rgba(0,0,0,0.5);">
      <div style="padding:16px 20px; border-bottom:1px solid var(--border); display:flex; justify-content:space-between; align-items:center;">
        <h3 style="font-size:1.1rem; color:#fff; display:flex; align-items:center; gap:8px;">🌡️ Pacer Adaptativo de Arrefecimento Térmico</h3>
        <button style="background:none; border:none; color:var(--text-muted); font-size:1.4rem; cursor:pointer;" onclick="fecharThermalPacerModal()">&times;</button>
      </div>
      <div style="padding:20px; overflow-y:auto; flex:1; display:flex; flex-direction:column; gap:12px;">
        <div style="display:flex; align-items:center; justify-content:space-between;">
          <label style="font-size:0.85rem; color:var(--text-muted);">Perfil de Alívio Térmico:</label>
          <select id="thermal-pacer-prof" style="padding:6px 10px; background:var(--card-bg); border:1px solid var(--border); color:#fff; border-radius:6px;" onchange="calcularThermalPacer()">
            <option value="silent_eco" selected>Silencioso / Frio (< 65°C - Pausa 400ms)</option>
            <option value="balanced">Equilibrado (65°C a 75°C - Pausa 250ms)</option>
            <option value="turbo_workstation">Turbo Acelerado (Pausa 100ms)</option>
          </select>
        </div>
        <div id="thermal-pacer-content"></div>
      </div>
      <div style="padding:12px 20px; border-top:1px solid var(--border); display:flex; justify-content:flex-end; align-items:center; background:var(--card-bg);">
        <button class="btn btn-secondary" onclick="fecharThermalPacerModal()">Fechar</button>
      </div>
    </div>
  </div>

  <!-- Modal de Proxies Inteligentes -->
  <div id="smart-proxy-modal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.75); z-index:9999; align-items:center; justify-content:center;">
    <div style="background:var(--panel-bg); border:1px solid var(--border); border-radius:10px; width:650px; max-width:92%; max-height:85vh; display:flex; flex-direction:column; overflow:hidden; box-shadow:0 20px 25px -5px rgba(0,0,0,0.5);">
      <div style="padding:16px 20px; border-bottom:1px solid var(--border); display:flex; justify-content:space-between; align-items:center;">
        <h3 style="font-size:1.1rem; color:#fff; display:flex; align-items:center; gap:8px;">👁️ Smart Proxy Scaler (Economia de 75% RAM)</h3>
        <button style="background:none; border:none; color:var(--text-muted); font-size:1.4rem; cursor:pointer;" onclick="fecharSmartProxyModal()">&times;</button>
      </div>
      <div style="padding:20px; overflow-y:auto; flex:1; display:flex; flex-direction:column; gap:12px;">
        <div style="display:flex; align-items:center; justify-content:space-between;">
          <label style="font-size:0.85rem; color:var(--text-muted);">Nível de Proxy para a Linha do Tempo:</label>
          <select id="smart-proxy-tier" style="padding:6px 10px; background:var(--card-bg); border:1px solid var(--border); color:#fff; border-radius:6px;" onchange="calcularSmartProxy()">
            <option value="ultra_light_540p" selected>540p Ultra-Light (-75% RAM / -93% VRAM)</option>
            <option value="balanced_720p">720p HD Balanceado (-55% RAM)</option>
            <option value="full_master_1080p">1080p Full Master (Export Final)</option>
          </select>
        </div>
        <div id="smart-proxy-content"></div>
      </div>
      <div style="padding:12px 20px; border-top:1px solid var(--border); display:flex; justify-content:flex-end; align-items:center; background:var(--card-bg);">
        <button class="btn btn-secondary" onclick="fecharSmartProxyModal()">Fechar</button>
      </div>
    </div>
  </div>

  <!-- Modal de Pipe Zero-Copy -->
  <div id="zero-copy-modal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.75); z-index:9999; align-items:center; justify-content:center;">
    <div style="background:var(--panel-bg); border:1px solid var(--border); border-radius:10px; width:650px; max-width:92%; max-height:85vh; display:flex; flex-direction:column; overflow:hidden; box-shadow:0 20px 25px -5px rgba(0,0,0,0.5);">
      <div style="padding:16px 20px; border-bottom:1px solid var(--border); display:flex; justify-content:space-between; align-items:center;">
        <h3 style="font-size:1.1rem; color:#fff; display:flex; align-items:center; gap:8px;">🚀 Pipe de Quadros em Memória (Zero Disk I/O)</h3>
        <button style="background:none; border:none; color:var(--text-muted); font-size:1.4rem; cursor:pointer;" onclick="fecharZeroCopyModal()">&times;</button>
      </div>
      <div id="zero-copy-content" style="padding:20px; overflow-y:auto; flex:1;"></div>
      <div style="padding:12px 20px; border-top:1px solid var(--border); display:flex; justify-content:flex-end; align-items:center; background:var(--card-bg);">
        <button class="btn btn-secondary" onclick="fecharZeroCopyModal()">Fechar</button>
      </div>
    </div>
  </div>

  <!-- Modal de Estabilizador VFR -->
  <div id="vfr-modal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.75); z-index:9999; align-items:center; justify-content:center;">
    <div style="background:var(--panel-bg); border:1px solid var(--border); border-radius:10px; width:650px; max-width:92%; max-height:85vh; display:flex; flex-direction:column; overflow:hidden; box-shadow:0 20px 25px -5px rgba(0,0,0,0.5);">
      <div style="padding:16px 20px; border-bottom:1px solid var(--border); display:flex; justify-content:space-between; align-items:center;">
        <h3 style="font-size:1.1rem; color:#fff; display:flex; align-items:center; gap:8px;">⏱️ Estabilizador Matemático de Taxa de Quadros (VFR)</h3>
        <button style="background:none; border:none; color:var(--text-muted); font-size:1.4rem; cursor:pointer;" onclick="fecharVFROptimizerModal()">&times;</button>
      </div>
      <div style="padding:20px; overflow-y:auto; flex:1; display:flex; flex-direction:column; gap:12px;">
        <div style="display:flex; align-items:center; justify-content:space-between;">
          <label style="font-size:0.85rem; color:var(--text-muted);">Taxa de Quadros Constante Alvo:</label>
          <select id="vfr-fps" style="padding:6px 10px; background:var(--card-bg); border:1px solid var(--border); color:#fff; border-radius:6px;" onchange="calcularVFROptimizer()">
            <option value="24">24.0 FPS (Cinema)</option>
            <option value="30" selected>30.0 FPS (Padrão YouTube)</option>
            <option value="60">60.0 FPS (Alta Fluidez)</option>
          </select>
        </div>
        <div id="vfr-content"></div>
      </div>
      <div style="padding:12px 20px; border-top:1px solid var(--border); display:flex; justify-content:flex-end; align-items:center; background:var(--card-bg);">
        <button class="btn btn-secondary" onclick="fecharVFROptimizerModal()">Fechar</button>
      </div>
    </div>
  </div>

  <!-- Modal de JSON Delta Patcher -->
  <div id="delta-patcher-modal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.75); z-index:9999; align-items:center; justify-content:center;">
    <div style="background:var(--panel-bg); border:1px solid var(--border); border-radius:10px; width:650px; max-width:92%; max-height:85vh; display:flex; flex-direction:column; overflow:hidden; box-shadow:0 20px 25px -5px rgba(0,0,0,0.5);">
      <div style="padding:16px 20px; border-bottom:1px solid var(--border); display:flex; justify-content:space-between; align-items:center;">
        <h3 style="font-size:1.1rem; color:#fff; display:flex; align-items:center; gap:8px;">🧩 Gravador Delta JSON (Poupa 95% do SSD)</h3>
        <button style="background:none; border:none; color:var(--text-muted); font-size:1.4rem; cursor:pointer;" onclick="fecharDeltaPatcherModal()">&times;</button>
      </div>
      <div id="delta-patcher-content" style="padding:20px; overflow-y:auto; flex:1;"></div>
      <div style="padding:12px 20px; border-top:1px solid var(--border); display:flex; justify-content:flex-end; align-items:center; background:var(--card-bg);">
        <button class="btn btn-secondary" onclick="fecharDeltaPatcherModal()">Fechar</button>
      </div>
    </div>
  </div>

  <!-- Modal de Alinhamento de Keyframes -->
  <div id="keyframe-aligner-modal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.75); z-index:9999; align-items:center; justify-content:center;">
    <div style="background:var(--panel-bg); border:1px solid var(--border); border-radius:10px; width:650px; max-width:92%; max-height:85vh; display:flex; flex-direction:column; overflow:hidden; box-shadow:0 20px 25px -5px rgba(0,0,0,0.5);">
      <div style="padding:16px 20px; border-bottom:1px solid var(--border); display:flex; justify-content:space-between; align-items:center;">
        <h3 style="font-size:1.1rem; color:#fff; display:flex; align-items:center; gap:8px;">✂️ Alinhador Cirúrgico de Keyframes (GOP I-Frame)</h3>
        <button style="background:none; border:none; color:var(--text-muted); font-size:1.4rem; cursor:pointer;" onclick="fecharKeyframeAlignerModal()">&times;</button>
      </div>
      <div style="padding:20px; overflow-y:auto; flex:1; display:flex; flex-direction:column; gap:12px;">
        <div style="display:flex; align-items:center; gap:12px;">
          <label style="font-size:0.85rem; color:var(--text-muted);">Ponto de Corte Desejado (segundos):</label>
          <input type="number" id="kf-cut-sec" value="4.05" step="0.05" style="width:90px; padding:6px; background:var(--card-bg); border:1px solid var(--border); color:#fff; border-radius:6px;" onchange="calcularKeyframeAligner()">
          <button class="btn btn-secondary" style="font-size:0.8rem;" onclick="calcularKeyframeAligner()">Verificar Encaixe</button>
        </div>
        <div id="kf-align-content"></div>
      </div>
      <div style="padding:12px 20px; border-top:1px solid var(--border); display:flex; justify-content:flex-end; align-items:center; background:var(--card-bg);">
        <button class="btn btn-secondary" onclick="fecharKeyframeAlignerModal()">Fechar</button>
      </div>
    </div>
  </div>

  <!-- Modal de Sentinela VRAM -->
  <div id="vram-sentinel-modal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.75); z-index:9999; align-items:center; justify-content:center;">
    <div style="background:var(--panel-bg); border:1px solid var(--border); border-radius:10px; width:650px; max-width:92%; max-height:85vh; display:flex; flex-direction:column; overflow:hidden; box-shadow:0 20px 25px -5px rgba(0,0,0,0.5);">
      <div style="padding:16px 20px; border-bottom:1px solid var(--border); display:flex; justify-content:space-between; align-items:center;">
        <h3 style="font-size:1.1rem; color:#fff; display:flex; align-items:center; gap:8px;">🛡️ Sentinela Anti-Vazamento de VRAM da GPU</h3>
        <button style="background:none; border:none; color:var(--text-muted); font-size:1.4rem; cursor:pointer;" onclick="fecharVRAMSentinelModal()">&times;</button>
      </div>
      <div id="vram-sentinel-content" style="padding:20px; overflow-y:auto; flex:1;"></div>
      <div style="padding:12px 20px; border-top:1px solid var(--border); display:flex; justify-content:flex-end; align-items:center; background:var(--card-bg);">
        <button class="btn btn-secondary" onclick="fecharVRAMSentinelModal()">Fechar</button>
      </div>
    </div>
  </div>

  <!-- Modal de Coalescedor 4KB NVMe -->
  <div id="nvme-coalescer-modal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.75); z-index:9999; align-items:center; justify-content:center;">
    <div style="background:var(--panel-bg); border:1px solid var(--border); border-radius:10px; width:650px; max-width:92%; max-height:85vh; display:flex; flex-direction:column; overflow:hidden; box-shadow:0 20px 25px -5px rgba(0,0,0,0.5);">
      <div style="padding:16px 20px; border-bottom:1px solid var(--border); display:flex; justify-content:space-between; align-items:center;">
        <h3 style="font-size:1.1rem; color:#fff; display:flex; align-items:center; gap:8px;">⚡ Coalescedor e Alinhador a 4KB NVMe SSD</h3>
        <button style="background:none; border:none; color:var(--text-muted); font-size:1.4rem; cursor:pointer;" onclick="fecharNVMeCoalescerModal()">&times;</button>
      </div>
      <div style="padding:20px; overflow-y:auto; flex:1; display:flex; flex-direction:column; gap:12px;">
        <div style="display:flex; align-items:center; gap:12px;">
          <label style="font-size:0.85rem; color:var(--text-muted);">Tamanho de Buffer Desalinhado (bytes):</label>
          <input type="number" id="nvme-input-bytes" value="5400" style="width:110px; padding:6px; background:var(--card-bg); border:1px solid var(--border); color:#fff; border-radius:6px;" onchange="calcularNVMeCoalescer()">
          <button class="btn btn-secondary" style="font-size:0.8rem;" onclick="calcularNVMeCoalescer()">Simular Alinhamento</button>
        </div>
        <div id="nvme-coalescer-content"></div>
      </div>
      <div style="padding:12px 20px; border-top:1px solid var(--border); display:flex; justify-content:flex-end; align-items:center; background:var(--card-bg);">
        <button class="btn btn-secondary" onclick="fecharNVMeCoalescerModal()">Fechar</button>
      </div>
    </div>
  </div>

  <!-- Modal de Matriz Cromática Rápida -->
  <div id="color-matrix-modal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.75); z-index:9999; align-items:center; justify-content:center;">
    <div style="background:var(--panel-bg); border:1px solid var(--border); border-radius:10px; width:650px; max-width:92%; max-height:85vh; display:flex; flex-direction:column; overflow:hidden; box-shadow:0 20px 25px -5px rgba(0,0,0,0.5);">
      <div style="padding:16px 20px; border-bottom:1px solid var(--border); display:flex; justify-content:space-between; align-items:center;">
        <h3 style="font-size:1.1rem; color:#fff; display:flex; align-items:center; gap:8px;">🎨 Conversor Cromático Rápido SIMD (Zero 3D LUT)</h3>
        <button style="background:none; border:none; color:var(--text-muted); font-size:1.4rem; cursor:pointer;" onclick="fecharColorMatrixModal()">&times;</button>
      </div>
      <div style="padding:20px; overflow-y:auto; flex:1; display:flex; flex-direction:column; gap:12px;">
        <div style="display:flex; align-items:center; justify-content:space-between;">
          <div style="display:flex; align-items:center; gap:8px;">
            <label style="font-size:0.85rem; color:var(--text-muted);">Origem:</label>
            <select id="color-src" style="padding:6px; background:var(--card-bg); border:1px solid var(--border); color:#fff; border-radius:6px;" onchange="calcularColorMatrix()">
              <option value="bt601" selected>Rec.601 (SDTV)</option>
              <option value="srgb">sRGB (Web/Monitores)</option>
              <option value="bt2020">Rec.2020 (HDR Amplo)</option>
            </select>
          </div>
          <span style="color:var(--text-muted);">➜</span>
          <div style="display:flex; align-items:center; gap:8px;">
            <label style="font-size:0.85rem; color:var(--text-muted);">Destino:</label>
            <select id="color-tgt" style="padding:6px; background:var(--card-bg); border:1px solid var(--border); color:#fff; border-radius:6px;" onchange="calcularColorMatrix()">
              <option value="bt709" selected>Rec.709 (HDTV YouTube)</option>
              <option value="srgb">sRGB</option>
              <option value="bt2020">Rec.2020</option>
            </select>
          </div>
        </div>
        <div id="color-matrix-content"></div>
      </div>
      <div style="padding:12px 20px; border-top:1px solid var(--border); display:flex; justify-content:flex-end; align-items:center; background:var(--card-bg);">
        <button class="btn btn-secondary" onclick="fecharColorMatrixModal()">Fechar</button>
      </div>
    </div>
  </div>

  <!-- Modal Windows Timer Resolution Optimizer -->
  <div id="timer-optimizer-modal" class="modal" style="display:none; position:fixed; z-index:9999; inset:0; background:rgba(0,0,0,0.7); align-items:center; justify-content:center;">
    <div style="background:var(--bg); border:1px solid var(--border); border-radius:12px; max-width:540px; width:90%; overflow:hidden;">
      <div style="padding:16px 20px; border-bottom:1px solid var(--border); display:flex; justify-content:space-between; align-items:center;">
        <h3 style="margin:0; font-size:1.1rem; display:flex; align-items:center; gap:8px;">
          <span>⏱️</span> Windows Timer Resolution Optimizer
        </h3>
        <button onclick="fecharTimerOptimizerModal()" style="background:none; border:none; color:var(--text-muted); font-size:1.2rem; cursor:pointer;">&times;</button>
      </div>
      <div style="padding:20px;">
        <div id="timer-optimizer-content"></div>
      </div>
      <div style="padding:12px 20px; border-top:1px solid var(--border); display:flex; justify-content:flex-end; align-items:center; background:var(--card-bg);">
        <button class="btn btn-secondary" onclick="fecharTimerOptimizerModal()">Fechar</button>
      </div>
    </div>
  </div>

  <!-- Modal Fast Integer Audio Peak Scanner -->
  <div id="audio-peak-modal" class="modal" style="display:none; position:fixed; z-index:9999; inset:0; background:rgba(0,0,0,0.7); align-items:center; justify-content:center;">
    <div style="background:var(--bg); border:1px solid var(--border); border-radius:12px; max-width:560px; width:90%; overflow:hidden;">
      <div style="padding:16px 20px; border-bottom:1px solid var(--border); display:flex; justify-content:space-between; align-items:center;">
        <h3 style="margin:0; font-size:1.1rem; display:flex; align-items:center; gap:8px;">
          <span>🔊</span> Fast Integer Audio Peak Scanner
        </h3>
        <button onclick="fecharAudioPeakModal()" style="background:none; border:none; color:var(--text-muted); font-size:1.2rem; cursor:pointer;">&times;</button>
      </div>
      <div style="padding:20px;">
        <div style="display:flex; align-items:center; gap:12px; margin-bottom:16px;">
          <label style="font-size:0.85rem; color:var(--text-muted);">Pico de Teste (Int16):</label>
          <select id="audio-peak-amp" style="padding:6px; background:var(--card-bg); border:1px solid var(--border); color:#fff; border-radius:6px;" onchange="calcularAudioPeak()">
            <option value="16000">-6 dBFS (Amplo Headroom)</option>
            <option value="28000" selected>-1.3 dBFS (Pico Seguro de Streaming)</option>
            <option value="32767">0 dBFS (Pico Máximo / Clipping)</option>
          </select>
        </div>
        <div id="audio-peak-content"></div>
      </div>
      <div style="padding:12px 20px; border-top:1px solid var(--border); display:flex; justify-content:flex-end; align-items:center; background:var(--card-bg);">
        <button class="btn btn-secondary" onclick="fecharAudioPeakModal()">Fechar</button>
      </div>
    </div>
  </div>

  <!-- Modal Speculative Disk Seek Canceller -->
  <div id="seek-canceller-modal" class="modal" style="display:none; position:fixed; z-index:9999; inset:0; background:rgba(0,0,0,0.7); align-items:center; justify-content:center;">
    <div style="background:var(--bg); border:1px solid var(--border); border-radius:12px; max-width:560px; width:90%; overflow:hidden;">
      <div style="padding:16px 20px; border-bottom:1px solid var(--border); display:flex; justify-content:space-between; align-items:center;">
        <h3 style="margin:0; font-size:1.1rem; display:flex; align-items:center; gap:8px;">
          <span>🧭</span> Speculative Disk Seek Canceller
        </h3>
        <button onclick="fecharSeekCancellerModal()" style="background:none; border:none; color:var(--text-muted); font-size:1.2rem; cursor:pointer;">&times;</button>
      </div>
      <div style="padding:20px;">
        <div id="seek-canceller-content"></div>
      </div>
      <div style="padding:12px 20px; border-top:1px solid var(--border); display:flex; justify-content:space-between; align-items:center; background:var(--card-bg);">
        <button class="btn btn-primary" onclick="simularCancelamentoSeeks()">Simular Pruning de I/O</button>
        <button class="btn btn-secondary" onclick="fecharSeekCancellerModal()">Fechar</button>
      </div>
    </div>
  </div>

  <!-- Modal GPU Memory Barrier Guard -->
  <div id="gpu-barrier-modal" class="modal" style="display:none; position:fixed; z-index:9999; inset:0; background:rgba(0,0,0,0.7); align-items:center; justify-content:center;">
    <div style="background:var(--bg); border:1px solid var(--border); border-radius:12px; max-width:580px; width:90%; overflow:hidden;">
      <div style="padding:16px 20px; border-bottom:1px solid var(--border); display:flex; justify-content:space-between; align-items:center;">
        <h3 style="margin:0; font-size:1.1rem; display:flex; align-items:center; gap:8px;">
          <span>🛡️</span> GPU Compute Memory Barrier Guard
        </h3>
        <button onclick="fecharGPUBarrierModal()" style="background:none; border:none; color:var(--text-muted); font-size:1.2rem; cursor:pointer;">&times;</button>
      </div>
      <div style="padding:20px;">
        <div style="display:flex; gap:16px; margin-bottom:16px; flex-wrap:wrap;">
          <div style="display:flex; align-items:center; gap:8px;">
            <label style="font-size:0.85rem; color:var(--text-muted);">Aceleração:</label>
            <select id="gpu-barrier-hw" style="padding:6px; background:var(--card-bg); border:1px solid var(--border); color:#fff; border-radius:6px;" onchange="calcularGPUBarrier()">
              <option value="d3d11va" selected>Direct3D 11 (D3D11VA)</option>
              <option value="cuda">NVIDIA CUDA</option>
              <option value="qsv">Intel QuickSync</option>
            </select>
          </div>
          <div style="display:flex; align-items:center; gap:8px;">
            <label style="font-size:0.85rem; color:var(--text-muted);">Taxa de Quadros:</label>
            <select id="gpu-barrier-fps" style="padding:6px; background:var(--card-bg); border:1px solid var(--border); color:#fff; border-radius:6px;" onchange="calcularGPUBarrier()">
              <option value="30">30 FPS</option>
              <option value="60" selected>60 FPS</option>
              <option value="120">120 FPS</option>
            </select>
          </div>
        </div>
        <div id="gpu-barrier-content"></div>
      </div>
      <div style="padding:12px 20px; border-top:1px solid var(--border); display:flex; justify-content:flex-end; align-items:center; background:var(--card-bg);">
        <button class="btn btn-secondary" onclick="fecharGPUBarrierModal()">Fechar</button>
      </div>
    </div>
  </div>

  <!-- Modal Prevenção Throttling CPU/GPU -->
  <div id="thermal-governor-modal" class="modal" style="display:none; position:fixed; z-index:9999; inset:0; background:rgba(0,0,0,0.7); align-items:center; justify-content:center;">
    <div style="background:var(--bg); border:1px solid var(--border); border-radius:12px; max-width:560px; width:90%; overflow:hidden;">
      <div style="padding:16px 20px; border-bottom:1px solid var(--border); display:flex; justify-content:space-between; align-items:center;">
        <h3 style="margin:0; font-size:1.1rem; display:flex; align-items:center; gap:8px;">
          <span>🔥</span> Prevenção Throttling CPU/GPU (Thermal Governor)
        </h3>
        <button onclick="fecharThermalGovernorModal()" style="background:none; border:none; color:var(--text-muted); font-size:1.2rem; cursor:pointer;">&times;</button>
      </div>
      <div style="padding:20px;">
        <div style="display:flex; align-items:center; gap:12px; margin-bottom:16px;">
          <label style="font-size:0.85rem; color:var(--text-muted);">Temperatura Simulada:</label>
          <select id="thermal-governor-temp" style="padding:6px; background:var(--card-bg); border:1px solid var(--border); color:#fff; border-radius:6px;" onchange="avaliarThermalGovernor()">
            <option value="65">65°C (Operação Normal / Fria)</option>
            <option value="78">78°C (Carga Intensa Sustentada)</option>
            <option value="84" selected>84°C (Zona de Pacing Preventivo)</option>
            <option value="91">91°C (Alerta Crítico / Arrefecimento Imediato)</option>
          </select>
        </div>
        <div id="thermal-governor-content"></div>
      </div>
      <div style="padding:12px 20px; border-top:1px solid var(--border); display:flex; justify-content:flex-end; align-items:center; background:var(--card-bg);">
        <button class="btn btn-secondary" onclick="fecharThermalGovernorModal()">Fechar</button>
      </div>
    </div>
  </div>

  <!-- Modal Pipe Zero-Copy 1080p (Pool RAM) -->
  <div id="sparse-pipe-modal" class="modal" style="display:none; position:fixed; z-index:9999; inset:0; background:rgba(0,0,0,0.7); align-items:center; justify-content:center;">
    <div style="background:var(--bg); border:1px solid var(--border); border-radius:12px; max-width:540px; width:90%; overflow:hidden;">
      <div style="padding:16px 20px; border-bottom:1px solid var(--border); display:flex; justify-content:space-between; align-items:center;">
        <h3 style="margin:0; font-size:1.1rem; display:flex; align-items:center; gap:8px;">
          <span>🧊</span> Pipe Zero-Copy de Quadros (Zero Allocation)
        </h3>
        <button onclick="fecharSparsePipeModal()" style="background:none; border:none; color:var(--text-muted); font-size:1.2rem; cursor:pointer;">&times;</button>
      </div>
      <div style="padding:20px;">
        <div id="sparse-pipe-content"></div>
      </div>
      <div style="padding:12px 20px; border-top:1px solid var(--border); display:flex; justify-content:flex-end; align-items:center; background:var(--card-bg);">
        <button class="btn btn-secondary" onclick="fecharSparsePipeModal()">Fechar</button>
      </div>
    </div>
  </div>

  <!-- Modal Culling de Linha do Tempo O(log N) -->
  <div id="viewport-culler-modal" class="modal" style="display:none; position:fixed; z-index:9999; inset:0; background:rgba(0,0,0,0.7); align-items:center; justify-content:center;">
    <div style="background:var(--bg); border:1px solid var(--border); border-radius:12px; max-width:560px; width:90%; overflow:hidden;">
      <div style="padding:16px 20px; border-bottom:1px solid var(--border); display:flex; justify-content:space-between; align-items:center;">
        <h3 style="margin:0; font-size:1.1rem; display:flex; align-items:center; gap:8px;">
          <span>✂️</span> Culling de Linha do Tempo O(log N)
        </h3>
        <button onclick="fecharViewportCullerModal()" style="background:none; border:none; color:var(--text-muted); font-size:1.2rem; cursor:pointer;">&times;</button>
      </div>
      <div style="padding:20px;">
        <div id="viewport-culler-content"></div>
      </div>
      <div style="padding:12px 20px; border-top:1px solid var(--border); display:flex; justify-content:space-between; align-items:center; background:var(--card-bg);">
        <button class="btn btn-primary" onclick="simularViewportCuller()">Recalcular Viewport</button>
        <button class="btn btn-secondary" onclick="fecharViewportCullerModal()">Fechar</button>
      </div>
    </div>
  </div>

  <!-- Modal Bypass Reamostragem (Bitstream Passthrough) -->
  <div id="audio-bypass-modal" class="modal" style="display:none; position:fixed; z-index:9999; inset:0; background:rgba(0,0,0,0.7); align-items:center; justify-content:center;">
    <div style="background:var(--bg); border:1px solid var(--border); border-radius:12px; max-width:560px; width:90%; overflow:hidden;">
      <div style="padding:16px 20px; border-bottom:1px solid var(--border); display:flex; justify-content:space-between; align-items:center;">
        <h3 style="margin:0; font-size:1.1rem; display:flex; align-items:center; gap:8px;">
          <span>🎵</span> Bypass de Reamostragem de Áudio
        </h3>
        <button onclick="fecharAudioBypassModal()" style="background:none; border:none; color:var(--text-muted); font-size:1.2rem; cursor:pointer;">&times;</button>
      </div>
      <div style="padding:20px;">
        <div style="display:flex; gap:16px; margin-bottom:16px; flex-wrap:wrap;">
          <div style="display:flex; align-items:center; gap:8px;">
            <label style="font-size:0.85rem; color:var(--text-muted);">Origem:</label>
            <select id="audio-bypass-src" style="padding:6px; background:var(--card-bg); border:1px solid var(--border); color:#fff; border-radius:6px;" onchange="calcularAudioBypass()">
              <option value="48000" selected>48.000 Hz (Vídeo Nativo)</option>
              <option value="44100">44.100 Hz (Música CD/MP3)</option>
              <option value="96000">96.000 Hz (Hi-Res Audio)</option>
            </select>
          </div>
          <div style="display:flex; align-items:center; gap:8px;">
            <label style="font-size:0.85rem; color:var(--text-muted);">Destino:</label>
            <select id="audio-bypass-tgt" style="padding:6px; background:var(--card-bg); border:1px solid var(--border); color:#fff; border-radius:6px;" onchange="calcularAudioBypass()">
              <option value="48000" selected>48.000 Hz (Padrão YouTube/MP4)</option>
              <option value="44100">44.100 Hz (Podcast/Web)</option>
            </select>
          </div>
        </div>
        <div id="audio-bypass-content"></div>
      </div>
      <div style="padding:12px 20px; border-top:1px solid var(--border); display:flex; justify-content:flex-end; align-items:center; background:var(--card-bg);">
        <button class="btn btn-secondary" onclick="fecharAudioBypassModal()">Fechar</button>
      </div>
    </div>
  </div>

  <!-- Modal Afinidade L3 CPU -->
  <div id="cpu-affinity-modal" class="modal" style="display:none; position:fixed; z-index:9999; inset:0; background:rgba(0,0,0,0.7); align-items:center; justify-content:center;">
    <div style="background:var(--bg); border:1px solid var(--border); border-radius:12px; max-width:560px; width:90%; overflow:hidden;">
      <div style="padding:16px 20px; border-bottom:1px solid var(--border); display:flex; justify-content:space-between; align-items:center;">
        <h3 style="margin:0; font-size:1.1rem; display:flex; align-items:center; gap:8px;">
          <span>🧠</span> Afinidade L3 CPU & Domínio de Cache
        </h3>
        <button onclick="fecharCPUAffinityModal()" style="background:none; border:none; color:var(--text-muted); font-size:1.2rem; cursor:pointer;">&times;</button>
      </div>
      <div style="padding:20px;">
        <div id="cpu-affinity-content"></div>
      </div>
      <div style="padding:12px 20px; border-top:1px solid var(--border); display:flex; justify-content:flex-end; align-items:center; background:var(--card-bg);">
        <button class="btn btn-secondary" onclick="fecharCPUAffinityModal()">Fechar</button>
      </div>
    </div>
  </div>

  <!-- Modal Crossfade Inteiro LUT -->
  <div id="audio-crossfade-modal" class="modal" style="display:none; position:fixed; z-index:9999; inset:0; background:rgba(0,0,0,0.7); align-items:center; justify-content:center;">
    <div style="background:var(--bg); border:1px solid var(--border); border-radius:12px; max-width:560px; width:90%; overflow:hidden;">
      <div style="padding:16px 20px; border-bottom:1px solid var(--border); display:flex; justify-content:space-between; align-items:center;">
        <h3 style="margin:0; font-size:1.1rem; display:flex; align-items:center; gap:8px;">
          <span>🎶</span> Crossfade Inteiro LUT (Equal-Power Curve)
        </h3>
        <button onclick="fecharAudioCrossfadeModal()" style="background:none; border:none; color:var(--text-muted); font-size:1.2rem; cursor:pointer;">&times;</button>
      </div>
      <div style="padding:20px;">
        <div style="display:flex; align-items:center; gap:12px; margin-bottom:16px;">
          <label style="font-size:0.85rem; color:var(--text-muted);">Progresso da Transição:</label>
          <select id="audio-crossfade-prog" style="padding:6px; background:var(--card-bg); border:1px solid var(--border); color:#fff; border-radius:6px;" onchange="calcularAudioCrossfade()">
            <option value="0.0">0% (Início: Faixa A cheia)</option>
            <option value="0.25">25% (Crossfade suave)</option>
            <option value="0.5" selected>50% (Ponto Médio de Potência Constante)</option>
            <option value="0.75">75% (Transição avançada)</option>
            <option value="1.0">100% (Fim: Faixa B cheia)</option>
          </select>
        </div>
        <div id="audio-crossfade-content"></div>
      </div>
      <div style="padding:12px 20px; border-top:1px solid var(--border); display:flex; justify-content:flex-end; align-items:center; background:var(--card-bg);">
        <button class="btn btn-secondary" onclick="fecharAudioCrossfadeModal()">Fechar</button>
      </div>
    </div>
  </div>

  <!-- Modal FastStart MOOV Detector -->
  <div id="moov-detector-modal" class="modal" style="display:none; position:fixed; z-index:9999; inset:0; background:rgba(0,0,0,0.7); align-items:center; justify-content:center;">
    <div style="background:var(--bg); border:1px solid var(--border); border-radius:12px; max-width:560px; width:90%; overflow:hidden;">
      <div style="padding:16px 20px; border-bottom:1px solid var(--border); display:flex; justify-content:space-between; align-items:center;">
        <h3 style="margin:0; font-size:1.1rem; display:flex; align-items:center; gap:8px;">
          <span>⚡</span> Leitura FastStart MOOV (SSD Shield)
        </h3>
        <button onclick="fecharMoovDetectorModal()" style="background:none; border:none; color:var(--text-muted); font-size:1.2rem; cursor:pointer;">&times;</button>
      </div>
      <div style="padding:20px;">
        <div style="display:flex; align-items:center; gap:12px; margin-bottom:16px;">
          <label style="font-size:0.85rem; color:var(--text-muted);">Tamanho do Arquivo:</label>
          <select id="moov-file-size" style="padding:6px; background:var(--card-bg); border:1px solid var(--border); color:#fff; border-radius:6px;" onchange="analisarMoovDetector()">
            <option value="500">500 MB (Clipe Curto)</option>
            <option value="4000" selected>4 GB (Take 4K Longo)</option>
            <option value="16000">16 GB (Gravação ProRes/Raw)</option>
          </select>
        </div>
        <div id="moov-detector-content"></div>
      </div>
      <div style="padding:12px 20px; border-top:1px solid var(--border); display:flex; justify-content:flex-end; align-items:center; background:var(--card-bg);">
        <button class="btn btn-secondary" onclick="fecharMoovDetectorModal()">Fechar</button>
      </div>
    </div>
  </div>

  <!-- Modal Aquecimento de Shaders GPU -->
  <div id="shader-warmup-modal" class="modal" style="display:none; position:fixed; z-index:9999; inset:0; background:rgba(0,0,0,0.7); align-items:center; justify-content:center;">
    <div style="background:var(--bg); border:1px solid var(--border); border-radius:12px; max-width:560px; width:90%; overflow:hidden;">
      <div style="padding:16px 20px; border-bottom:1px solid var(--border); display:flex; justify-content:space-between; align-items:center;">
        <h3 style="margin:0; font-size:1.1rem; display:flex; align-items:center; gap:8px;">
          <span>🛡️</span> Aquecimento de Shaders GPU (Anti-Stutter)
        </h3>
        <button onclick="fecharShaderWarmupModal()" style="background:none; border:none; color:var(--text-muted); font-size:1.2rem; cursor:pointer;">&times;</button>
      </div>
      <div style="padding:20px;">
        <div id="shader-warmup-content"></div>
      </div>
      <div style="padding:12px 20px; border-top:1px solid var(--border); display:flex; justify-content:flex-end; align-items:center; background:var(--card-bg);">
        <button class="btn btn-secondary" onclick="fecharShaderWarmupModal()">Fechar</button>
      </div>
    </div>
  </div>

  <!-- Modal Localidade NUMA RAM/CPU -->
  <div id="numa-binding-modal" class="modal" style="display:none; position:fixed; z-index:9999; inset:0; background:rgba(0,0,0,0.7); align-items:center; justify-content:center;">
    <div style="background:var(--bg); border:1px solid var(--border); border-radius:12px; max-width:560px; width:90%; overflow:hidden;">
      <div style="padding:16px 20px; border-bottom:1px solid var(--border); display:flex; justify-content:space-between; align-items:center;">
        <h3 style="margin:0; font-size:1.1rem; display:flex; align-items:center; gap:8px;">
          <span>🧬</span> Localidade de Memória NUMA (Zero Inter-Socket)
        </h3>
        <button onclick="fecharNUMABindingModal()" style="background:none; border:none; color:var(--text-muted); font-size:1.2rem; cursor:pointer;">&times;</button>
      </div>
      <div style="padding:20px;">
        <div id="numa-binding-content"></div>
      </div>
      <div style="padding:12px 20px; border-top:1px solid var(--border); display:flex; justify-content:flex-end; align-items:center; background:var(--card-bg);">
        <button class="btn btn-secondary" onclick="fecharNUMABindingModal()">Fechar</button>
      </div>
    </div>
  </div>

  <!-- Modal Bezier Easing Q16.16 -->
  <div id="bezier-fixed-modal" class="modal" style="display:none; position:fixed; z-index:9999; inset:0; background:rgba(0,0,0,0.7); align-items:center; justify-content:center;">
    <div style="background:var(--bg); border:1px solid var(--border); border-radius:12px; max-width:560px; width:90%; overflow:hidden;">
      <div style="padding:16px 20px; border-bottom:1px solid var(--border); display:flex; justify-content:space-between; align-items:center;">
        <h3 style="margin:0; font-size:1.1rem; display:flex; align-items:center; gap:8px;">
          <span>📐</span> Bezier Easing Q16.16 (Inteiro 32-bit)
        </h3>
        <button onclick="fecharBezierFixedModal()" style="background:none; border:none; color:var(--text-muted); font-size:1.2rem; cursor:pointer;">&times;</button>
      </div>
      <div style="padding:20px;">
        <div style="display:flex; align-items:center; gap:12px; margin-bottom:16px;">
          <label style="font-size:0.85rem; color:var(--text-muted);">Progresso da Curva:</label>
          <select id="bezier-prog" style="padding:6px; background:var(--card-bg); border:1px solid var(--border); color:#fff; border-radius:6px;" onchange="avaliarBezierFixed()">
            <option value="0.1">10% (Início de Aceleração)</option>
            <option value="0.5" selected>50% (Ponto de Inflexão Médio)</option>
            <option value="0.9">90% (Final de Desaceleração)</option>
          </select>
        </div>
        <div id="bezier-fixed-content"></div>
      </div>
      <div style="padding:12px 20px; border-top:1px solid var(--border); display:flex; justify-content:flex-end; align-items:center; background:var(--card-bg);">
        <button class="btn btn-secondary" onclick="fecharBezierFixedModal()">Fechar</button>
      </div>
    </div>
  </div>

  <!-- Modal Passthrough ProRes/DNxHR -->
  <div id="prores-passthrough-modal" class="modal" style="display:none; position:fixed; z-index:9999; inset:0; background:rgba(0,0,0,0.7); align-items:center; justify-content:center;">
    <div style="background:var(--bg); border:1px solid var(--border); border-radius:12px; max-width:580px; width:90%; overflow:hidden;">
      <div style="padding:16px 20px; border-bottom:1px solid var(--border); display:flex; justify-content:space-between; align-items:center;">
        <h3 style="margin:0; font-size:1.1rem; display:flex; align-items:center; gap:8px;">
          <span>🎬</span> Passthrough ProRes / DNxHR (Zero Render)
        </h3>
        <button onclick="fecharProResPassthroughModal()" style="background:none; border:none; color:var(--text-muted); font-size:1.2rem; cursor:pointer;">&times;</button>
      </div>
      <div style="padding:20px;">
        <div style="display:flex; gap:16px; margin-bottom:16px; flex-wrap:wrap;">
          <div style="display:flex; align-items:center; gap:8px;">
            <label style="font-size:0.85rem; color:var(--text-muted);">Codec:</label>
            <select id="prores-codec" style="padding:6px; background:var(--card-bg); border:1px solid var(--border); color:#fff; border-radius:6px;" onchange="calcularProResPassthrough()">
              <option value="prores" selected>Apple ProRes</option>
              <option value="dnxhr">Avid DNxHR</option>
              <option value="h264">H.264 (AVC)</option>
              <option value="hevc">HEVC (H.265)</option>
            </select>
          </div>
          <div style="display:flex; align-items:center; gap:8px;">
            <label style="font-size:0.85rem; color:var(--text-muted);">Filtros Visuais:</label>
            <select id="prores-graded" style="padding:6px; background:var(--card-bg); border:1px solid var(--border); color:#fff; border-radius:6px;" onchange="calcularProResPassthrough()">
              <option value="0" selected>Nenhum (Corte Seco Intacto)</option>
              <option value="1">Color Grading / Efeitos Ativos</option>
            </select>
          </div>
        </div>
        <div id="prores-passthrough-content"></div>
      </div>
      <div style="padding:12px 20px; border-top:1px solid var(--border); display:flex; justify-content:flex-end; align-items:center; background:var(--card-bg);">
        <button class="btn btn-secondary" onclick="fecharProResPassthroughModal()">Fechar</button>
      </div>
    </div>
  </div>

  <!-- Modal Proteção de Desgaste NAND 64KB -->
  <div id="wear-mitigator-modal" class="modal" style="display:none; position:fixed; z-index:9999; inset:0; background:rgba(0,0,0,0.7); align-items:center; justify-content:center;">
    <div style="background:var(--bg); border:1px solid var(--border); border-radius:12px; max-width:560px; width:90%; overflow:hidden;">
      <div style="padding:16px 20px; border-bottom:1px solid var(--border); display:flex; justify-content:space-between; align-items:center;">
        <h3 style="margin:0; font-size:1.1rem; display:flex; align-items:center; gap:8px;">
          <span>🛡️</span> Mitigador de Desgaste NAND SSD (WAF Shield)
        </h3>
        <button onclick="fecharWearMitigatorModal()" style="background:none; border:none; color:var(--text-muted); font-size:1.2rem; cursor:pointer;">&times;</button>
      </div>
      <div style="padding:20px;">
        <div id="wear-mitigator-content"></div>
      </div>
      <div style="padding:12px 20px; border-top:1px solid var(--border); display:flex; justify-content:space-between; align-items:center; background:var(--card-bg);">
        <button class="btn btn-primary" onclick="simularWearMitigator()">Simular Coalescência 64KB</button>
        <button class="btn btn-secondary" onclick="fecharWearMitigatorModal()">Fechar</button>
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

    def _validate_origin_and_host(self) -> bool:
        """Mitigates Cross-Site Request Forgery (CSRF) and DNS Rebinding."""
        host = self.headers.get("Host", "")
        if host and not (host.startswith("127.0.0.1") or host.startswith("localhost")):
            self.send_error(403, "Acesso proibido: Host inválido (Proteção contra DNS Rebinding)")
            return False

        origin = self.headers.get("Origin")
        if origin:
            if not (origin.startswith("http://127.0.0.1") or origin.startswith("http://localhost")):
                self.send_error(403, "Acesso proibido: Origem não autorizada (Proteção Cross-Origin)")
                return False
        return True

    def do_GET(self):
        if not self._validate_origin_and_host():
            return
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
        elif self.path.startswith("/api/disk_health"):
            health = DiskSpaceGuard.check_health("C:\\")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"ok": True, "health": health.__dict__}).encode("utf-8"))
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
        elif self.path.startswith("/api/chapters"):
            import urllib.parse
            parsed = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed.query)
            proj_id = params.get("project_id", [""])[0]
            plan = self.repo.get(proj_id) if proj_id else None
            if not plan:
                return self.send_json({"ok": False, "error": "Projeto não encontrado"}, 404)
            chaps = AutoChapteringEngine.generate_chapters(plan)
            yt_text = AutoChapteringEngine.generate_youtube_description_block(plan)
            vtt = AutoChapteringEngine.generate_webvtt(plan)
            return self.send_json({
                "ok": True,
                "total_chapters": len(chaps),
                "youtube_description": yt_text,
                "webvtt": vtt,
                "chapters": [c.__dict__ for c in chaps]
            })
        elif self.path.startswith("/api/color_grading/presets"):
            return self.send_json({
                "ok": True,
                "presets": ColorGradingEngine.list_presets()
            })
        elif self.path.startswith("/api/foley/analyze"):
            import urllib.parse
            parsed = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed.query)
            proj_id = params.get("project_id", [""])[0]
            plan = self.repo.get(proj_id) if proj_id else None
            if not plan:
                return self.send_json({"ok": False, "error": "Projeto não encontrado"}, 404)
            foley_manifest = SoundFXAutoFoley.generate_plan_foley_manifest(plan)
            return self.send_json({
                "ok": True,
                **foley_manifest
            })
        elif self.path.startswith("/api/pacing_audit"):
            import urllib.parse
            parsed = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed.query)
            proj_id = params.get("project_id", [""])[0]
            plan = self.repo.get(proj_id) if proj_id else None
            if not plan:
                return self.send_json({"ok": False, "error": "Projeto não encontrado"}, 404)
            rep = ScenePacingAuditor.audit_plan(plan)
            return self.send_json({
                "ok": True,
                "project_id": rep.project_id,
                "overall_retention_score": rep.overall_retention_score,
                "average_wpm": rep.average_wpm,
                "total_scenes_analyzed": rep.total_scenes_analyzed,
                "monotonous_scenes_count": rep.monotonous_scenes_count,
                "scenes_requiring_attention": rep.scenes_requiring_attention,
                "summary": rep.summary,
                "scene_metrics": [m.__dict__ for m in rep.scene_metrics]
            })
        elif self.path.startswith("/api/safe_zones"):
            import urllib.parse
            parsed = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed.query)
            ratio = params.get("aspect_ratio", ["portrait"])[0]
            bounds = SafeZoneMultiFormatFraming.calculate_pixel_bounds(1080, 1920, ratio)
            css_guide = SafeZoneMultiFormatFraming.generate_css_overlay_guide(ratio)
            return self.send_json({
                "ok": True,
                "aspect_ratio": ratio,
                "bounds": bounds,
                "css_overlay": css_guide
            })
        elif self.path.startswith("/api/titles/generate"):
            import urllib.parse
            parsed = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed.query)
            proj_id = params.get("project_id", [""])[0]
            plan = self.repo.get(proj_id) if proj_id else None
            if not plan:
                return self.send_json({"ok": False, "error": "Projeto não encontrado"}, 404)
            titles_pkg = ClickbaitTitleHookGenerator.generate_title_package(plan)
            return self.send_json({"ok": True, **titles_pkg})
        elif self.path.startswith("/api/stems/manifest"):
            import urllib.parse
            parsed = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed.query)
            proj_id = params.get("project_id", [""])[0]
            plan = self.repo.get(proj_id) if proj_id else None
            if not plan:
                return self.send_json({"ok": False, "error": "Projeto não encontrado"}, 404)
            manifest = AudioStemSplitter.create_default_mixer_manifest(plan)
            filter_str = AudioStemSplitter.generate_ffmpeg_stem_filter(manifest)
            return self.send_json({
                "ok": True,
                "project_id": manifest.project_id,
                "sample_rate_hz": manifest.sample_rate_hz,
                "bit_depth": manifest.bit_depth,
                "tracks": [t.__dict__ for t in manifest.tracks],
                "ffmpeg_filter": filter_str
            })
        elif self.path.startswith("/api/subtitles/styles"):
            return self.send_json({
                "ok": True,
                "styles": AITranscriptionSubtitleStyler.list_styles()
            })
        elif self.path.startswith("/api/transitions/plan"):
            import urllib.parse
            parsed = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed.query)
            proj_id = params.get("project_id", [""])[0]
            plan = self.repo.get(proj_id) if proj_id else None
            if not plan:
                return self.send_json({"ok": False, "error": "Projeto não encontrado"}, 404)
            transitions = SmartSceneTransitionDirector.plan_project_transitions(plan)
            return self.send_json({
                "ok": True,
                "project_id": plan.project_id,
                "total_transitions": len(transitions),
                "transitions": [t.__dict__ for t in transitions]
            })
        elif self.path.startswith("/api/shorts/extract"):
            import urllib.parse
            parsed = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed.query)
            proj_id = params.get("project_id", [""])[0]
            plan = self.repo.get(proj_id) if proj_id else None
            if not plan:
                return self.send_json({"ok": False, "error": "Projeto não encontrado"}, 404)
            shorts = ContentRepurposerShortsExtractor.extract_viral_shorts(plan)
            return self.send_json({
                "ok": True,
                "project_id": plan.project_id,
                "total_shorts": len(shorts),
                "shorts": shorts
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
        elif self.path.startswith("/api/policies/sync"):
            res = self.policy_manager.sync_policies_from_remote()
            return self.send_json(res)
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
        elif self.path.startswith("/api/mega/plan"):
            parsed = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed.query)
            topic = params.get("topic", ["Ciência e Cosmos"])[0]
            try:
                minutes = float(params.get("minutes", ["30.0"])[0])
            except ValueError:
                minutes = 30.0
            mega_plan = MegaDurationArchitect.plan_mega_production(topic=topic, target_minutes=minutes)
            return self.send_json({"ok": True, "plan": mega_plan.to_dict()})
        elif self.path.startswith("/api/seo/generate"):
            parsed = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed.query)
            proj_id = params.get("project_id", [""])[0]
            topic = params.get("topic", ["Vídeo Educativo"])[0]
            plan = self.repo.get(proj_id) if proj_id else None
            if not plan:
                from models.scene_plan import Scene
                plan = ProjectPlan(
                    project_id="temp_seo",
                    title=topic,
                    config=ProjectConfig(aspect_ratio="16:9"),
                    scenes=[Scene(order=1, duration=5.0, narration_text=topic, visual_description=topic, english_keywords=[topic])]
                )
            seo_data = AIHashtagTagCloudGenerator.generate_seo_metadata(plan)
            res = {
                "project_id": plan.project_id,
                "niche_category": seo_data.get("niche_category", "Geral"),
                "hashtags": seo_data.get("hashtags", []),
                "formatted_hashtags_string": seo_data.get("formatted_hashtags_string", ""),
                "youtube_studio_tags_string": seo_data.get("youtube_tags_string", ""),
                "char_count": len(seo_data.get("youtube_tags_string", "")),
                "long_tail_keywords": seo_data.get("long_tail_keywords", [])
            }
            return self.send_json({"ok": True, "result": res})
        elif self.path.startswith("/api/camera/plan"):
            parsed = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed.query)
            proj_id = params.get("project_id", [""])[0]
            plan = self.repo.get(proj_id) if proj_id else None
            if not plan:
                return self.send_json({"ok": False, "error": "Projeto não encontrado"}, 404)
            manifest = SmartSceneKenBurnsDirector.generate_plan_camera_manifest(plan)
            scenes_data = []
            distribution = {}
            for m in manifest.get("camera_motions", []):
                m_type = m.get("motion_type", "gentle_zoom_in")
                distribution[m_type] = distribution.get(m_type, 0) + 1
                scenes_data.append({
                    "scene_order": m.get("scene_order", 1),
                    "camera_movement": m.get("motion_type", "gentle_zoom_in"),
                    "zoom_start": 1.0,
                    "zoom_end": 1.25 if "zoom_in" in m_type else 1.0,
                    "narration_snippet": m.get("narrative_reason", ""),
                    "ffmpeg_zoompan_expr": m.get("ffmpeg_filter", "")
                })
            return self.send_json({
                "ok": True,
                "plan": {
                    "project_id": plan.project_id,
                    "total_scenes": manifest.get("total_scenes", len(scenes_data)),
                    "distribution": distribution,
                    "scenes": scenes_data
                }
            })
        elif self.path.startswith("/api/templates/list"):
            templates = OneClickPresetVideoTemplates.list_templates()
            for t in templates:
                t.setdefault("color_grade", t.get("color_grade", "Natural"))
                t.setdefault("subtitle_font", "Cinzel" if t["id"] == "history_documentary" else ("Orbitron" if t["id"] == "space_scifi" else ("Montserrat" if t["id"] == "viral_shorts" else "Inter")))
                t.setdefault("subtitle_color", "Amarelo Neon" if t["id"] == "viral_shorts" else "Branco")
                t.setdefault("bgm_genre", "Orquestral / Cello" if t["id"] == "history_documentary" else ("Cosmic Ambient" if t["id"] == "space_scifi" else ("Phonk / Upbeat" if t["id"] == "viral_shorts" else "Modern Lo-Fi")))
                t.setdefault("bgm_volume", 0.18)
                t.setdefault("camera_style", "Cinemático Ken Burns" if t["id"] != "business_tech" else "Estático / Minimal")
                t.setdefault("transition_type", t.get("transition_kind", "fade"))
            return self.send_json({"ok": True, "templates": templates})
        elif self.path.startswith("/api/ducking/plan"):
            parsed = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed.query)
            proj_id = params.get("project_id", [""])[0]
            plan = self.repo.get(proj_id) if proj_id else None
            if not plan:
                return self.send_json({"ok": False, "error": "Projeto não encontrado"}, 404)
            duck_plan = DynamicZoomPunchAudioDuckingDirector.plan_ducking_and_punchins(plan)
            return self.send_json({"ok": True, "plan": duck_plan})
        elif self.path.startswith("/api/retention/audit"):
            parsed = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed.query)
            proj_id = params.get("project_id", [""])[0]
            plan = self.repo.get(proj_id) if proj_id else None
            if not plan:
                return self.send_json({"ok": False, "error": "Projeto não encontrado"}, 404)
            audit_res = VisualRetentionHeatmapAuditor.audit_retention_curve(plan)
            return self.send_json({"ok": True, "result": audit_res})
        elif self.path.startswith("/api/color/harmonize"):
            parsed = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed.query)
            proj_id = params.get("project_id", [""])[0]
            plan = self.repo.get(proj_id) if proj_id else None
            if not plan:
                return self.send_json({"ok": False, "error": "Projeto não encontrado"}, 404)
            color_res = SmartLutCinematicColorMatcher.harmonize_project_colors(plan)
            return self.send_json({"ok": True, "result": color_res})
        elif self.path.startswith("/api/multiexport/presets"):
            presets = SocialMediaMultiExportPresets.list_presets()
            return self.send_json({"ok": True, "presets": presets})
        elif self.path.startswith("/api/hooks/variations"):
            parsed = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed.query)
            proj_id = params.get("project_id", [""])[0]
            plan = self.repo.get(proj_id) if proj_id else None
            if not plan:
                return self.send_json({"ok": False, "error": "Projeto não encontrado"}, 404)
            variations = AIStoryHookABSplitTester.generate_hook_variations(plan)
            return self.send_json({"ok": True, "variations": [v.__dict__ for v in variations]})
        elif self.path.startswith("/api/beat/sync"):
            parsed = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed.query)
            proj_id = params.get("project_id", [""])[0]
            try:
                bpm = float(params.get("bpm", ["90.0"])[0])
            except ValueError:
                bpm = 90.0
            plan = self.repo.get(proj_id) if proj_id else None
            if not plan:
                return self.send_json({"ok": False, "error": "Projeto não encontrado"}, 404)
            sync_res = SoundtrackBeatDropSceneSync.synchronize_timeline_to_bpm(plan, bpm=bpm)
            return self.send_json({"ok": True, "result": sync_res})
        elif self.path.startswith("/api/voice/emotions"):
            parsed = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed.query)
            proj_id = params.get("project_id", [""])[0]
            plan = self.repo.get(proj_id) if proj_id else None
            if not plan:
                return self.send_json({"ok": False, "error": "Projeto não encontrado"}, 404)
            emo_res = AIVoiceEmotionInflectionDirector.direct_project_voice_inflections(plan)
            return self.send_json({"ok": True, "result": emo_res})
        elif self.path.startswith("/api/chapters/cards"):
            parsed = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed.query)
            proj_id = params.get("project_id", [""])[0]
            plan = self.repo.get(proj_id) if proj_id else None
            if not plan:
                return self.send_json({"ok": False, "error": "Projeto não encontrado"}, 404)
            cards_res = AutoVideoChapterCardGenerator.generate_cards_for_plan(plan)
            return self.send_json({"ok": True, "result": cards_res})
        elif self.path.startswith("/api/thumbnails/quad"):
            parsed = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed.query)
            proj_id = params.get("project_id", [""])[0]
            plan = self.repo.get(proj_id) if proj_id else None
            if not plan:
                return self.send_json({"ok": False, "error": "Projeto não encontrado"}, 404)
            quad = AIAutomatedThumbnailVariatorAB.plan_thumbnail_suite(plan)
            return self.send_json({"ok": True, "suite": quad})
        elif self.path.startswith("/api/hardware/profile"):
            prof = AdaptiveHardwareGPUAutoTuner.probe_hardware()
            return self.send_json({"ok": True, "profile": prof.__dict__})
        elif self.path.startswith("/api/pacing/waves"):
            parsed = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed.query)
            proj_id = params.get("project_id", [""])[0]
            plan = self.repo.get(proj_id) if proj_id else None
            if not plan:
                return self.send_json({"ok": False, "error": "Projeto não encontrado"}, 404)
            pacing_res = SmartAudienceRetentionPacer.calculate_pacing_waves(plan)
            return self.send_json({"ok": True, "pacing": pacing_res})
        elif self.path.startswith("/api/community/kit"):
            parsed = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed.query)
            proj_id = params.get("project_id", [""])[0]
            plan = self.repo.get(proj_id) if proj_id else None
            if not plan:
                return self.send_json({"ok": False, "error": "Projeto não encontrado"}, 404)
            comm_kit = AutoYouTubeCommunityPostPackager.export_kit_dict(plan)
            return self.send_json({"ok": True, "kit": comm_kit})
        elif self.path.startswith("/api/audio/spatial"):
            parsed = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed.query)
            proj_id = params.get("project_id", [""])[0]
            plan = self.repo.get(proj_id) if proj_id else None
            if not plan:
                return self.send_json({"ok": False, "error": "Projeto não encontrado"}, 404)
            spatial_data = BinauralSpatialAudioPanner.generate_panning_script(plan)
            return self.send_json({"ok": True, **spatial_data})
        elif self.path.startswith("/api/endscreen/plan"):
            parsed = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed.query)
            proj_id = params.get("project_id", [""])[0]
            plan = self.repo.get(proj_id) if proj_id else None
            if not plan:
                return self.send_json({"ok": False, "error": "Projeto não encontrado"}, 404)
            endscreen_data = AIAutomatedEndScreenCardDirector.generate_end_screen_layout(plan)
            return self.send_json({"ok": True, "end_screen": endscreen_data})
        elif self.path.startswith("/api/audio/loudness"):
            parsed = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed.query)
            proj_id = params.get("project_id", [""])[0]
            plan = self.repo.get(proj_id) if proj_id else None
            if not plan:
                return self.send_json({"ok": False, "error": "Projeto não encontrado"}, 404)
            loudness_data = SmartLoudnessBroadcastNormalizer.calculate_loudness_profile(plan)
            return self.send_json({"ok": True, "loudness": loudness_data})
        elif self.path.startswith("/api/vocabulary/audit"):
            parsed = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed.query)
            proj_id = params.get("project_id", [""])[0]
            plan = self.repo.get(proj_id) if proj_id else None
            if not plan:
                return self.send_json({"ok": False, "error": "Projeto não encontrado"}, 404)
            audit_data = ViralHookVocabularyAuditor.audit_script_vocabulary(plan)
            return self.send_json({"ok": True, "audit": audit_data})
        elif self.path.startswith("/api/broll/pacing"):
            parsed = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed.query)
            proj_id = params.get("project_id", [""])[0]
            plan = self.repo.get(proj_id) if proj_id else None
            if not plan:
                return self.send_json({"ok": False, "error": "Projeto não encontrado"}, 404)
            pacing_data = DynamicBrollPacer.calculate_broll_pacing(plan)
            return self.send_json({"ok": True, "pacing": pacing_data})
        elif self.path.startswith("/api/audio/foley"):
            parsed = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed.query)
            proj_id = params.get("project_id", [""])[0]
            plan = self.repo.get(proj_id) if proj_id else None
            if not plan:
                return self.send_json({"ok": False, "error": "Projeto não encontrado"}, 404)
            foley_data = SoundDesignFoleyAutoDirector.generate_foley_cues(plan)
            return self.send_json({"ok": True, "foley": foley_data})
        elif self.path.startswith("/api/film_stock/list"):
            stocks = AutoColorToneFilmStockEmulator.get_available_film_stocks()
            return self.send_json({"ok": True, "stocks": stocks})
        elif self.path.startswith("/api/metadata/seo"):
            parsed = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed.query)
            proj_id = params.get("project_id", [""])[0]
            plan = self.repo.get(proj_id) if proj_id else None
            if not plan:
                return self.send_json({"ok": False, "error": "Projeto não encontrado"}, 404)
            seo_data = CTRMetadataSEOOptimizer.generate_metadata_package(plan)
            return self.send_json({"ok": True, "metadata": seo_data})
        elif self.path.startswith("/api/voice/denoise/profiles"):
            profiles = AIVoiceDenoiseSpectralIsolator.get_available_profiles()
            return self.send_json({"ok": True, "profiles": profiles})
        elif self.path.startswith("/api/transitions/plan"):
            parsed = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed.query)
            proj_id = params.get("project_id", [""])[0]
            plan = self.repo.get(proj_id) if proj_id else None
            if not plan:
                return self.send_json({"ok": False, "error": "Projeto não encontrado"}, 404)
            transitions_data = SmartSceneTransitionDirector.plan_scene_transitions(plan)
            return self.send_json({"ok": True, "transitions": transitions_data})
        elif self.path.startswith("/api/shorts/generate"):
            parsed = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed.query)
            proj_id = params.get("project_id", [""])[0]
            plan = self.repo.get(proj_id) if proj_id else None
            if not plan:
                return self.send_json({"ok": False, "error": "Projeto não encontrado"}, 404)
            shorts_data = YouTubeShortsRepurposer.generate_shorts_packages(plan)
            return self.send_json({"ok": True, "shorts": shorts_data})
        elif self.path.startswith("/api/render/recovery/status"):
            parsed = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed.query)
            proj_id = params.get("project_id", [""])[0]
            rec_status = AutoRenderCrashRecoveryGuard.check_resumable_render(proj_id if proj_id else "default")
            return self.send_json({"ok": True, "status": rec_status})
        elif self.path.startswith("/api/bitrate/calculate"):
            parsed = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed.query)
            proj_id = params.get("project_id", [""])[0]
            profile_name = params.get("profile", ["youtube_1080p_pro"])[0]
            plan = self.repo.get(proj_id) if proj_id else None
            if not plan:
                return self.send_json({"ok": False, "error": "Projeto não encontrado"}, 404)
            bitrate_plan = VideoBitrateBandwidthOptimizer.calculate_project_bitrate_plan(plan, profile_name)
            return self.send_json({"ok": True, "bitrate_plan": bitrate_plan})
        elif self.path.startswith("/api/video/qc"):
            parsed = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed.query)
            proj_id = params.get("project_id", [""])[0]
            plan = self.repo.get(proj_id) if proj_id else None
            if not plan:
                return self.send_json({"ok": False, "error": "Projeto não encontrado"}, 404)
            qc_data = VisualArtifactGlitchDetector.audit_project_visual_qc(plan)
            return self.send_json({"ok": True, "qc": qc_data})
        elif self.path.startswith("/api/audio/doppler/calculate"):
            parsed = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed.query)
            spd = float(params.get("speed", [140.0])[0])
            dir_str = params.get("direction", ["left_to_right"])[0]
            doppler_data = SoundFXDopplerPanAutomator.calculate_doppler_envelope(approach_speed_kmh=spd, direction=dir_str)
            return self.send_json({"ok": True, "doppler": doppler_data})
        elif self.path.startswith("/api/audience/dropoff/predict"):
            parsed = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed.query)
            proj_id = params.get("project_id", [""])[0]
            plan = self.repo.get(proj_id) if proj_id else None
            if not plan:
                return self.send_json({"ok": False, "error": "Projeto não encontrado"}, 404)
            dropoff_data = AudienceDropoffPredictor.predict_dropoff_hotspots(plan)
            return self.send_json({"ok": True, "dropoff": dropoff_data})
        elif self.path.startswith("/api/subtitles/karaoke/generate"):
            parsed = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed.query)
            proj_id = params.get("project_id", [""])[0]
            style_name = params.get("style", ["hormozi_bold_yellow"])[0]
            plan = self.repo.get(proj_id) if proj_id else None
            if not plan:
                return self.send_json({"ok": False, "error": "Projeto não encontrado"}, 404)
            sub_data = DynamicSubtitlesWordHighlighter.generate_ass_subtitle_content(plan, style_name)
            return self.send_json({"ok": True, "subtitles": sub_data})
        elif self.path.startswith("/api/narrative/tension/audit"):
            parsed = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed.query)
            proj_id = params.get("project_id", [""])[0]
            plan = self.repo.get(proj_id) if proj_id else None
            if not plan:
                return self.send_json({"ok": False, "error": "Projeto não encontrado"}, 404)
            tension_data = NarrativeTensionCurveAuditor.audit_narrative_tension(plan)
            return self.send_json({"ok": True, "narrative": tension_data})
        elif self.path.startswith("/api/watermark/positions"):
            corners = AutoVideoWatermarkBrandingDirector.get_corner_positions()
            return self.send_json({"ok": True, "positions": corners})
        elif self.path.startswith("/api/hdr/presets"):
            presets = HDRToSDRToneMapper.get_available_presets()
            return self.send_json({"ok": True, "presets": presets})
        elif self.path.startswith("/api/thumbnail/face/detect"):
            parsed = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed.query)
            proj_id = params.get("project_id", [""])[0]
            plan = self.repo.get(proj_id) if proj_id else None
            if not plan:
                return self.send_json({"ok": False, "error": "Projeto não encontrado"}, 404)
            face_data = AIAutomatedThumbnailFaceDetector.detect_thumbnail_face_candidates(plan)
            return self.send_json({"ok": True, "faces": face_data})
        elif self.path.startswith("/api/soundtrack/loop/calculate"):
            parsed = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed.query)
            proj_id = params.get("project_id", [""])[0]
            music_dur = float(params.get("music_duration", [90.0])[0])
            crossfade = float(params.get("crossfade", [3.0])[0])
            plan = self.repo.get(proj_id) if proj_id else None
            if not plan:
                return self.send_json({"ok": False, "error": "Projeto não encontrado"}, 404)
            loop_data = SoundtrackAutoLoopStretcher.stretch_plan_soundtrack(plan, soundtrack_duration_seconds=music_dur, crossfade_seconds=crossfade)
            return self.send_json({"ok": True, "loop_plan": loop_data})
        elif self.path.startswith("/api/cutpack/plan"):
            parsed = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed.query)
            proj_id = params.get("project_id", [""])[0]
            plan = self.repo.get(proj_id) if proj_id else None
            if not plan:
                return self.send_json({"ok": False, "error": "Projeto não encontrado"}, 404)
            cutpack_data = AutoSocialCutpackExporter.generate_cutpack_render_plan(plan)
            return self.send_json({"ok": True, "cutpack": cutpack_data})
        elif self.path.startswith("/api/lower_thirds/generate"):
            parsed = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed.query)
            proj_id = params.get("project_id", [""])[0]
            style_name = params.get("style", ["tech_cyber_bar"])[0]
            plan = self.repo.get(proj_id) if proj_id else None
            if not plan:
                return self.send_json({"ok": False, "error": "Projeto não encontrado"}, 404)
            lt_data = CinematicLowerThirdsAnimator.generate_plan_lower_thirds(plan, style_name)
            return self.send_json({"ok": True, "lower_thirds": lt_data})
        elif self.path.startswith("/api/aesthetic/symmetry/audit"):
            parsed = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed.query)
            proj_id = params.get("project_id", [""])[0]
            plan = self.repo.get(proj_id) if proj_id else None
            if not plan:
                return self.send_json({"ok": False, "error": "Projeto não encontrado"}, 404)
            sym_data = VisualSymmetryAestheticAuditor.audit_composition_symmetry(plan)
            return self.send_json({"ok": True, "aesthetic": sym_data})
        elif self.path.startswith("/api/audio/surround51/calculate"):
            parsed = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed.query)
            boost = float(params.get("boost", [2.0])[0])
            surround_data = StereoTo51SurroundUpmixer.build_51_surround_filter(center_dialogue_boost_db=boost)
            return self.send_json({"ok": True, "surround": surround_data})
        elif self.path.startswith("/api/palette/mood/extract"):
            parsed = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed.query)
            proj_id = params.get("project_id", [""])[0]
            plan = self.repo.get(proj_id) if proj_id else None
            if not plan:
                return self.send_json({"ok": False, "error": "Projeto não encontrado"}, 404)
            pal_data = AutoColorPaletteMoodExtractor.extract_palette_from_plan(plan)
            return self.send_json({"ok": True, "palette": pal_data})
        elif self.path.startswith("/api/nle/export"):
            parsed = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed.query)
            proj_id = params.get("project_id", [""])[0]
            fps_val = float(params.get("fps", [30.0])[0])
            plan = self.repo.get(proj_id) if proj_id else None
            if not plan:
                return self.send_json({"ok": False, "error": "Projeto não encontrado"}, 404)
            import tempfile
            out_dir = os.path.join(tempfile.gettempdir(), "drift_nle_exports")
            scene_list = [
                {
                    "duration": getattr(sc, "duration", 4.0),
                    "concept": getattr(sc, "concept", f"Cena {getattr(sc, 'order', idx)}"),
                    "clip_name": f"Scene_{idx:02d}.mp4"
                }
                for idx, sc in enumerate(plan.scenes, 1)
            ]
            exp_data = NLETimelineXMLEdlExporter.export_all_formats(
                project_name=plan.title or "Drift_Project",
                scenes=scene_list,
                output_dir=out_dir,
                fps=fps_val
            )
            return self.send_json({"ok": True, "export": exp_data})
        elif self.path.startswith("/api/audio/ducking/preview"):
            parsed = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed.query)
            preset_name = params.get("preset", ["broadcast_standard"])[0]
            duck_data = DynamicAudioDuckingSidechainEngine.calculate_ducking_filter(preset=preset_name)
            return self.send_json({"ok": True, "ducking": duck_data})
        elif self.path.startswith("/api/thumbnails/ab_grid"):
            parsed = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed.query)
            proj_id = params.get("project_id", [""])[0]
            plan = self.repo.get(proj_id) if proj_id else None
            if not plan:
                return self.send_json({"ok": False, "error": "Projeto não encontrado"}, 404)
            grid_data = YouTubeThumbnailABGridRenderer.generate_ab_test_matrix(
                video_title=plan.title or "Vídeo Drift IA",
                keywords=getattr(plan, "keywords", ["Cinema", "Drift", "IA"])
            )
            return self.send_json({"ok": True, "ab_grid": grid_data})
        elif self.path.startswith("/api/hardware/affinity/calculate"):
            parsed = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed.query)
            prof = params.get("profile", ["balanced"])[0]
            aff_data = CPUThreadAffinityGovernor.calculate_balanced_thread_allocation(cooling_profile=prof)
            return self.send_json({"ok": True, "affinity": aff_data})
        elif self.path.startswith("/api/selective_rerender/analyze"):
            parsed = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed.query)
            proj_id = params.get("project_id", [""])[0]
            plan = self.repo.get(proj_id) if proj_id else None
            if not plan:
                return self.send_json({"ok": False, "error": "Projeto não encontrado"}, 404)
            scenes_dict = [
                {
                    "duration": getattr(sc, "duration", 4.0),
                    "narration_text": getattr(sc, "narration_text", ""),
                    "concept": getattr(sc, "concept", "")
                }
                for sc in plan.scenes
            ]
            rerender_res = SmartSelectiveRerenderCache.analyze_rerender_differential(scenes_dict, scenes_dict)
            return self.send_json({"ok": True, "rerender_analysis": rerender_res})
        elif self.path.startswith("/api/pruner/analyze"):
            parsed = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed.query)
            proj_id = params.get("project_id", [""])[0]
            plan = self.repo.get(proj_id) if proj_id else None
            if not plan:
                return self.send_json({"ok": False, "error": "Projeto não encontrado"}, 404)
            scenes_dict = [
                {
                    "duration": getattr(sc, "duration", 4.0),
                    "narration_text": getattr(sc, "narration_text", ""),
                    "concept": getattr(sc, "concept", "")
                }
                for sc in plan.scenes
            ]
            pruner_res = PreRenderDeadweightPruner.prune_timeline(scenes_dict)
            return self.send_json({"ok": True, "pruner": pruner_res})
        elif self.path.startswith("/api/ssd/fatigue/estimate"):
            parsed = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed.query)
            mb_val = float(params.get("mb", [1200.0])[0])
            ssd_data = SSDWriteFatigueMitigator.calculate_write_savings(int(mb_val * 1024 * 1024), use_ram_scratchpad=True)
            return self.send_json({"ok": True, "ssd_report": ssd_data})
        elif self.path.startswith("/api/audio/passthrough/evaluate"):
            parsed = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed.query)
            codec_val = params.get("codec", ["aac"])[0]
            eval_data = LosslessAudioPassThroughEngine.evaluate_audio_stream_compatibility(
                codec_name=codec_val,
                sample_rate=48000,
                channels=2,
                target_container="mp4"
            )
            return self.send_json({"ok": True, "evaluation": eval_data})
        elif self.path.startswith("/api/hardware/thermal_pacer/calculate"):
            parsed = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed.query)
            prof = params.get("profile", ["silent_eco"])[0]
            w_sec = float(params.get("work_sec", [45.0])[0])
            pacer_data = ThermalAdaptiveRenderPacer.calculate_inter_scene_pause(elapsed_work_seconds=w_sec, profile=prof)
            return self.send_json({"ok": True, "pacer": pacer_data})
        elif self.path.startswith("/api/media/proxy/calculate"):
            parsed = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed.query)
            tier_val = params.get("tier", ["ultra_light_540p"])[0]
            proxy_data = SmartProxyResolutionScaler.calculate_proxy_scaling(
                source_width=1920,
                source_height=1080,
                tier=tier_val
            )
            return self.send_json({"ok": True, "proxy_config": proxy_data})
        elif self.path.startswith("/api/pipeline/zero_copy/calculate"):
            parsed = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed.query)
            w = int(params.get("w", [1920])[0])
            h = int(params.get("h", [1080])[0])
            fps = float(params.get("fps", [30.0])[0])
            pipe_data = ZeroCopyFramePipeAllocator.build_memory_pipe_pipeline(width=w, height=h, fps=fps)
            return self.send_json({"ok": True, "pipe": pipe_data})
        elif self.path.startswith("/api/editing/vfr/calculate"):
            parsed = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed.query)
            target_fps = float(params.get("fps", [30.0])[0])
            vfr_data = VariableFramerateJitterSmoother.calculate_vfr_stabilization_filter(target_fps=target_fps)
            return self.send_json({"ok": True, "vfr": vfr_data})
        elif self.path.startswith("/api/storage/delta/calculate"):
            parsed = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed.query)
            proj_id = params.get("project_id", [""])[0]
            plan = self.repo.get(proj_id) if proj_id else None
            if not plan:
                return self.send_json({"ok": False, "error": "Projeto não encontrado"}, 404)
            plan_dict = plan.to_dict()
            delta_data = CompactJsonDeltaPatcher.compute_project_delta(plan_dict, plan_dict)
            return self.send_json({"ok": True, "delta": delta_data})
        elif self.path.startswith("/api/editing/keyframe/align"):
            parsed = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed.query)
            cut_val = float(params.get("cut_sec", [4.05])[0])
            fps_val = float(params.get("fps", [30.0])[0])
            align_data = SmartKeyframeIntervalAligner.align_cut_to_nearest_keyframe(requested_cut_sec=cut_val, fps=fps_val)
            return self.send_json({"ok": True, "alignment": align_data})
        elif self.path.startswith("/api/hardware/vram/inspect"):
            parsed = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed.query)
            vram_val = float(params.get("vram_mb", [1800.0])[0])
            backend = params.get("backend", ["d3d11va"])[0]
            vram_data = GPUVRAMLeakSentinel.inspect_vram_hygiene(estimated_allocated_vram_mb=vram_val, hardware_backend=backend)
            return self.send_json({"ok": True, "vram_status": vram_data})
        elif self.path.startswith("/api/hardware/nvme/coalesce"):
            parsed = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed.query)
            bytes_val = int(params.get("bytes", [5400])[0])
            coalesce_data = NVMeTrimIOCoalescer.calculate_coalesced_buffer_size(unaligned_bytes=bytes_val)
            return self.send_json({"ok": True, "coalesce": coalesce_data})
        elif self.path.startswith("/api/media/color_matrix/calculate"):
            parsed = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed.query)
            src_val = params.get("src", ["bt601"])[0]
            tgt_val = params.get("tgt", ["bt709"])[0]
            matrix_data = SmartColorSpaceFastMatrix.build_fast_matrix_filter(source_space=src_val, target_space=tgt_val)
            return self.send_json({"ok": True, "matrix": matrix_data})
        elif self.path.startswith("/api/system/timer_resolution"):
            parsed = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed.query)
            mode_param = params.get("high_precision")
            if mode_param is not None:
                high_prec = bool(int(mode_param[0]))
                res = WindowsTimerResolutionOptimizer.set_timer_resolution(high_precision_mode=high_prec)
            else:
                res = WindowsTimerResolutionOptimizer.set_timer_resolution(high_precision_mode=WindowsTimerResolutionOptimizer._high_precision_active)
            return self.send_json({"ok": True, "result": res})
        elif self.path.startswith("/api/audio/peak_scan"):
            parsed = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed.query)
            amp_val = int(params.get("amplitude", [28000])[0])
            test_samples = [int(amp_val * math.sin(i * 0.1)) for i in range(44100)]
            pcm_bytes = bytearray()
            for s in test_samples:
                pcm_bytes.extend(int(s).to_bytes(2, byteorder="little", signed=True))
            scan_data = AudioPeakFastIntegerScanner.scan_pcm16_samples(bytes(pcm_bytes))
            return self.send_json({"ok": True, "scan": scan_data})
        elif self.path.startswith("/api/media/seek_cancel"):
            parsed = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed.query)
            pending_str = params.get("pending", ["intro,cena1,cena2,cena3,outro"])[0]
            visible_str = params.get("visible", ["cena2,cena3"])[0]
            canceller = SpeculativeDiskSeekCanceller()
            import time
            for p in pending_str.split(","):
                if p.strip():
                    canceller.register_read_request(p.strip(), time.time())
            visible_set = {v.strip() for v in visible_str.split(",") if v.strip()}
            cancel_data = canceller.prune_obsolete_requests(visible_set)
            return self.send_json({"ok": True, "canceller": cancel_data})
        elif self.path.startswith("/api/pipeline/gpu_barrier/calculate"):
            parsed = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed.query)
            hw = params.get("hw", ["d3d11va"])[0]
            fps = float(params.get("fps", [60.0])[0])
            barrier_data = GPUComputeMemoryBarrierGuard.generate_barrier_sync_policy(hw_acceleration=hw, fps=fps)
            return self.send_json({"ok": True, "barrier": barrier_data})
        elif self.path.startswith("/api/system/thermal_governor/evaluate"):
            parsed = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed.query)
            temp_val = float(params.get("temp", [82.0])[0])
            governor = ThermalThrottlingPredictionGovernor(target_max_temp=82.0)
            gov_data = governor.evaluate_thermal_pacing(current_temp_celsius=temp_val)
            return self.send_json({"ok": True, "governor": gov_data})
        elif self.path.startswith("/api/storage/sparse_pipe/metrics"):
            pipe = SparseZeroCopyFramePipe(frame_width=1920, frame_height=1080, bytes_per_pixel=4, pool_depth=3)
            for _ in range(60):
                pipe.acquire_frame_buffer()
            pipe_data = pipe.get_pipe_metrics()
            return self.send_json({"ok": True, "pipe": pipe_data})
        elif self.path.startswith("/api/editing/viewport_culler/simulate"):
            sim_clips = [{"id": f"clip_{i*5}s", "start_sec": float(i * 5), "end_sec": float((i + 1) * 5)} for i in range(20)]
            culler_data = TimelineVisualViewportCuller.cull_non_visible_clips(sim_clips, view_start_sec=15.0, view_end_sec=35.0)
            return self.send_json({"ok": True, "culler": culler_data})
        elif self.path.startswith("/api/media/audio_bypass/evaluate"):
            parsed = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed.query)
            src_val = int(params.get("src_hz", [48000])[0])
            tgt_val = int(params.get("tgt_hz", [48000])[0])
            bypass_data = AudioResampleSubsamplingBypass.evaluate_audio_filter_chain(source_sample_rate_hz=src_val, target_sample_rate_hz=tgt_val)
            return self.send_json({"ok": True, "bypass": bypass_data})
        elif self.path.startswith("/api/core/cpu_affinity/calculate"):
            affinity_data = CPUCacheL3AffinityBalancer.calculate_optimal_thread_affinity()
            return self.send_json({"ok": True, "affinity": affinity_data})
        elif self.path.startswith("/api/editing/audio_crossfade/benchmark"):
            parsed = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed.query)
            prog_val = float(params.get("progress", [0.5])[0])
            out_c, in_c = LosslessAudioCrossfadeIntegerLUT.get_crossfade_coefficients(prog_val)
            bench_data = LosslessAudioCrossfadeIntegerLUT.benchmark_gain_lookup()
            bench_data["fade_out_coeff"] = out_c
            bench_data["fade_in_coeff"] = in_c
            return self.send_json({"ok": True, "crossfade": bench_data})
        elif self.path.startswith("/api/media/moov_detector/analyze"):
            parsed = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed.query)
            size_mb = float(params.get("size_mb", [4000.0])[0])
            header_sample = b"\x00\x00\x00\x20ftypmp42\x00\x00\x01\x00moov\x00\x00\x00lmvhd"
            detector_data = MP4MoovAtomEarlyDetector.analyze_moov_placement(
                file_size_bytes=int(size_mb * 1024 * 1024),
                header_bytes=header_sample
            )
            return self.send_json({"ok": True, "detector": detector_data})
        elif self.path.startswith("/api/pipeline/shader_warmup/execute"):
            warmup_data = GPUShaderWarmupPipelineCache.warmup_core_shaders()
            return self.send_json({"ok": True, "warmup": warmup_data})
        elif self.path.startswith("/api/core/numa/topology"):
            topology_data = NUMANodeMemoryLocalityBinder.get_numa_binding_topology()
            return self.send_json({"ok": True, "topology": topology_data})
        elif self.path.startswith("/api/editing/bezier_fixed/evaluate"):
            parsed = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed.query)
            prog_val = float(params.get("progress", [0.5])[0])
            eased_val = BezierEasingFixedPointEvaluator.evaluate_ease_in_out(prog_val)
            bench_data = BezierEasingFixedPointEvaluator.benchmark_fixed_point_savings()
            bench_data["progress"] = prog_val
            bench_data["eased_value"] = round(eased_val, 4)
            return self.send_json({"ok": True, "bezier": bench_data})
        elif self.path.startswith("/api/media/passthrough/evaluate"):
            parsed = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed.query)
            codec_val = params.get("codec", ["prores"])[0]
            graded_val = int(params.get("graded", [0])[0])
            pass_data = ProResDNxHRPassthroughMuxer.evaluate_clip_passthrough_viability(
                codec_name=codec_val,
                has_color_grading=bool(graded_val)
            )
            return self.send_json({"ok": True, "passthrough": pass_data})
        elif self.path.startswith("/api/storage/wear_mitigator/simulate"):
            mitigator = JournalPageWearLevelingMitigator()
            wear_data = mitigator.calculate_wear_savings()
            return self.send_json({"ok": True, "mitigator": wear_data})
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if not self._validate_origin_and_host():
            return
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
        elif self.path == "/api/retention/structure":
            project_id = data.get("project_id")
            plan = self.repo.get(project_id) if project_id else None
            if not plan:
                return self.send_json({"ok": False, "error": "Projeto não encontrado"}, 404)
            pacing = LongFormRetentionDirector.structure_narrative_arc(plan.scenes)
            return self.send_json({
                "ok": True,
                "total_scenes": pacing.total_scenes,
                "estimated_duration_sec": pacing.estimated_duration_sec,
                "acts": pacing.acts,
                "retention_score": pacing.retention_score,
                "hooks": [
                    {
                        "scene_order": h.scene_order,
                        "minute_mark": h.minute_mark,
                        "hook_type": h.hook_type,
                        "phrase": h.suggested_phrase,
                        "action": h.pacing_action
                    }
                    for h in pacing.hooks_inserted
                ]
            })
        elif self.path == "/api/soundtrack/multi_chapter":
            project_id = data.get("project_id")
            plan = self.repo.get(project_id) if project_id else None
            if not plan:
                return self.send_json({"ok": False, "error": "Projeto não encontrado"}, 404)
            tot_dur = sum(s.duration if s.duration > 0 else 6.0 for s in plan.scenes)
            audio_plan = MultiChapterMoodSoundtrackOrchestrator.generate_soundtrack_plan(tot_dur)
            return self.send_json({
                "ok": True,
                "total_duration_sec": audio_plan.total_duration_sec,
                "total_segments": audio_plan.total_segments,
                "ducking": audio_plan.ducking_profile,
                "segments": [
                    {
                        "index": seg.segment_index,
                        "mood": seg.mood,
                        "start_sec": seg.start_sec,
                        "end_sec": seg.end_sec,
                        "duration": seg.duration_sec,
                        "track": seg.music_file_path,
                        "crossfade_sec": seg.crossfade_duration_sec
                    }
                    for seg in audio_plan.segments
                ]
            })
        elif self.path == "/api/effects/ken_burns":
            project_id = data.get("project_id")
            plan = self.repo.get(project_id) if project_id else None
            if not plan:
                return self.send_json({"ok": False, "error": "Projeto não encontrado"}, 404)
            raw_scenes = [
                {
                    "order": s.order,
                    "duration": s.duration,
                    "media_type": "image" if not (s.selected_media and s.selected_media.local_cached_path and s.selected_media.local_cached_path.endswith((".mp4", ".mov", ".mkv"))) else "video",
                    "tags": s.keywords
                }
                for s in plan.scenes
            ]
            effects = SmartKenBurnsPunchInEngine.apply_to_project_scenes(raw_scenes)
            return self.send_json({
                "ok": True,
                "total_effects": len(effects),
                "effects": [
                    {
                        "scene_order": e.scene_order,
                        "motion_type": e.motion_type,
                        "start_scale": e.start_scale,
                        "end_scale": e.end_scale,
                        "duration": e.duration_sec,
                        "filter": e.ffmpeg_video_filter
                    }
                    for e in effects
                ]
            })
        elif self.path == "/api/render/checkpoint_status":
            project_id = data.get("project_id", "drift_proj")
            total_chunks = int(data.get("total_chunks", 10))
            state = RenderCheckpointManager.load_or_init_state(project_id, total_chunks)
            return self.send_json({
                "ok": True,
                "project_id": state.project_id,
                "total_chunks": state.total_chunks,
                "completed_chunks": state.completed_chunks,
                "pending_chunks": state.pending_chunks,
                "is_fully_completed": state.is_fully_completed,
                "checkpoint_file": state.checkpoint_file
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
        elif self.path == "/api/export/multilingual":
            project_id = data.get("project_id", "drift_proj")
            video_path = data.get("video_path", "d:/CUTWIREDRIFT/renders/output.mp4")
            tracks = data.get("tracks", [
                {"language": "pt", "file_path": "d:/CUTWIREDRIFT/audio_pt.mp3", "title": "Português (Original)"},
                {"language": "en", "file_path": "d:/CUTWIREDRIFT/audio_en.mp3", "title": "English (Dubbed)"},
                {"language": "es", "file_path": "d:/CUTWIREDRIFT/audio_es.mp3", "title": "Español"}
            ])
            spec = MultilingualAudioPackager.create_multilingual_spec(project_id, video_path, tracks)
            return self.send_json({
                "ok": True,
                "project_id": spec.project_id,
                "output_file": spec.output_target_path,
                "total_tracks": len(spec.tracks),
                "tracks": [{"lang": t.language_code, "title": t.title, "default": t.is_default} for t in spec.tracks],
                "ffmpeg_cmd": spec.ffmpeg_command_args,
                "platforms": spec.supported_platforms
            })
        elif self.path == "/api/audio/strip_silence":
            dur = float(data.get("duration_sec", 120.0))
            thresh = float(data.get("threshold_db", -38.0))
            report = SmartSilenceBreathStripper.analyze_and_generate_filter(dur, silence_threshold_db=thresh)
            return self.send_json({
                "ok": True,
                "original_duration": report.original_duration_sec,
                "tightened_duration": report.tightened_duration_sec,
                "seconds_saved": report.seconds_saved,
                "percentage_tightened": report.percentage_tightened,
                "pauses_removed": report.detected_pauses_count,
                "ffmpeg_filter": report.ffmpeg_filter
            })
        elif self.path == "/api/infographics/scan":
            project_id = data.get("project_id")
            plan = self.repo.get(project_id) if project_id else None
            if not plan:
                return self.send_json({"ok": False, "error": "Projeto não encontrado"}, 404)
            info_plan = MotionInfographicsGenerator.scan_project_scenes(plan.scenes)
            return self.send_json({
                "ok": True,
                "total_elements": info_plan.total_elements,
                "style": info_plan.style_theme,
                "items": [
                    {
                        "scene": item.scene_order,
                        "type": item.data_type,
                        "match": item.raw_match,
                        "target_value": item.target_value,
                        "label": item.label_text,
                        "filter": item.ffmpeg_drawtext_filter
                    }
                    for item in info_plan.items
                ]
            })
        elif self.path == "/api/broll/plan":
            project_id = data.get("project_id")
            plan = self.repo.get(project_id) if project_id else None
            if not plan:
                return self.send_json({"ok": False, "error": "Projeto não encontrado"}, 404)
            broll_plan = BRollGapFiller.generate_plan(plan.scenes)
            return self.send_json({
                "ok": True,
                "total_insertions": broll_plan.total_insertions,
                "coverage_ratio": broll_plan.coverage_ratio,
                "insertions": [
                    {
                        "scene": ins.target_scene_order,
                        "concept": ins.matched_concept,
                        "overlay_type": ins.overlay_type,
                        "provider": ins.recommended_provider,
                        "query_pt": ins.search_query_pt,
                        "query_en": ins.search_query_en,
                        "start_offset": ins.start_offset_sec,
                        "duration": ins.duration_sec,
                        "opacity": ins.blend_opacity
                    }
                    for ins in broll_plan.insertions
                ]
            })
        elif self.path == "/api/eco/policy":
            mode = data.get("mode", "eco_silent")
            policy = EcoGovernor.calculate_thread_budget(mode)
            applied = EcoGovernor.apply_process_priority(policy.windows_priority_class)
            return self.send_json({
                "ok": True,
                "mode": policy.mode,
                "total_threads": policy.total_system_threads,
                "worker_threads": policy.assigned_worker_threads,
                "reserved_threads": policy.reserved_os_threads,
                "priority_class": policy.windows_priority_class,
                "cpu_cap_percent": policy.target_cpu_cap_percent,
                "windows_priority_applied": applied
            })
        elif self.path == "/api/eco/ram_flush":
            report = RamWorkingSetFlusher.flush()
            return self.send_json({
                "ok": True,
                "freed_objects": report.freed_python_objects,
                "working_set_before_mb": report.working_set_before_mb,
                "working_set_after_mb": report.working_set_after_mb,
                "memory_reclaimed_mb": report.memory_reclaimed_mb,
                "windows_api_applied": report.is_windows_api_applied
            })
        elif self.path == "/api/proxy/session":
            project_id = data.get("project_id")
            plan = self.repo.get(project_id) if project_id else None
            if not plan:
                return self.send_json({"ok": False, "error": "Projeto não encontrado"}, 404)
            session = DraftProxyEngine.build_session(project_id, plan.scenes)
            return self.send_json({
                "ok": True,
                "project_id": session.project_id,
                "draft_active": session.is_draft_mode_active,
                "total_proxies": session.total_proxies,
                "proxies_dir": session.proxies_dir,
                "mappings": [
                    {
                        "scene": m.scene_order,
                        "original": m.original_media_path,
                        "proxy": m.proxy_media_path,
                        "resolution": m.scale_resolution,
                        "is_image": m.is_image
                    }
                    for m in session.mappings.values()
                ]
            })
        elif self.path == "/api/render/evaluate_stream_copy":
            media_path = data.get("media_path", "sample.mp4")
            effects = bool(data.get("has_effects", False))
            eval_res = LosslessStreamCopyDetector.evaluate_stream(
                media_path=media_path,
                has_effects_applied=effects,
                codec_v=data.get("codec_v", "h264"),
                codec_a=data.get("codec_a", "aac"),
                width=int(data.get("width", 1920)),
                height=int(data.get("height", 1080))
            )
            return self.send_json({
                "ok": True,
                "media_path": eval_res.media_path,
                "can_copy_video": eval_res.can_copy_video_stream,
                "can_copy_audio": eval_res.can_copy_audio_stream,
                "video_codec": eval_res.recommended_video_codec,
                "audio_codec": eval_res.recommended_audio_codec,
                "speedup_factor": eval_res.estimated_speedup_factor,
                "reason": eval_res.bypass_reason
            })
        elif self.path == "/api/eco/disk_io":
            action = data.get("action", "begin")
            res = DiskIoGovernor.begin_background_io() if action == "begin" else DiskIoGovernor.end_background_io()
            return self.send_json({
                "ok": res.is_background_io_active,
                "platform": res.platform,
                "error": res.error_message,
                "active": DiskIoGovernor.is_active()
            })
        elif self.path == "/api/render/fast_decode":
            threads = int(data.get("threads", 2))
            is_preview = bool(data.get("is_preview", False))
            profile = FastDecodeOptimizer.get_trim_and_slice_args(threads=threads, is_preview_mode=is_preview)
            return self.send_json({
                "ok": True,
                "tune": profile.tune_mode,
                "skip_frames": profile.skip_frames,
                "input_args": profile.ffmpeg_input_args,
                "output_args": profile.ffmpeg_output_args,
                "cpu_savings_pct": profile.estimated_cpu_saving_percent
            })
        elif self.path == "/api/eco/sleep_inhibit":
            action = data.get("action", "inhibit")
            res = SleepInhibitGovernor.inhibit_sleep() if action == "inhibit" else SleepInhibitGovernor.release_sleep()
            return self.send_json({
                "ok": True,
                "is_inhibited": res.is_sleep_inhibited,
                "active_jobs": res.active_jobs_count,
                "platform": res.platform
            })
        elif self.path == "/api/storage/purge_cache":
            cache_dir = data.get("cache_dir", "d:/CUTWIREDRIFT/renders")
            max_bytes = int(data.get("max_bytes_quota", 4 * 1024 * 1024 * 1024))
            report = RollingCachePurgeManager.enforce_cache_quota(cache_dir, max_bytes_quota=max_bytes)
            return self.send_json({
                "ok": True,
                "dir": report.directory_scanned,
                "files_deleted": report.files_deleted,
                "bytes_reclaimed": report.bytes_reclaimed,
                "bytes_after": report.total_bytes_after,
                "quota_respected": report.is_quota_respected
            })
        elif self.path == "/api/eco/thermal_pacing":
            chunk_idx = int(data.get("chunk_index", 1))
            pacer = getattr(self, "_thermal_pacer", None)
            if not pacer:
                self._thermal_pacer = ThermalDutyCyclePacer(chunks_per_cooling_cycle=5, pause_duration_sec=1.5)
                pacer = self._thermal_pacer
            decision = pacer.record_chunk_completed(chunk_idx)
            return self.send_json({
                "ok": True,
                "chunk_index": decision.chunk_index,
                "consecutive": decision.consecutive_renders,
                "should_pause": decision.should_pause_for_cooling,
                "pause_sec": decision.cooling_pause_sec,
                "temp_drop_est": decision.estimated_temp_drop_celsius,
                "reason": decision.reason
            })
        elif self.path == "/api/eco/occlusion_state":
            occ = ZeroGpuOcclusionGovernor.get_occlusion_state()
            return self.send_json({
                "ok": True,
                "is_minimized": occ.is_minimized,
                "is_foreground": occ.is_foreground,
                "target_fps": occ.target_gui_fps,
                "gpu_active": occ.gpu_render_active,
                "mode": occ.mode_description
            })
        elif self.path == "/api/storage/compact_index":
            project_id = data.get("project_id")
            plan = self.repo.get(project_id) if project_id else None
            if not plan:
                return self.send_json({"ok": False, "error": "Projeto não encontrado"}, 404)
            indexer = CompactMetadataIndexer()
            stats = indexer.index_scenes(plan.scenes)
            return self.send_json({
                "ok": True,
                "total_scenes": stats.total_scenes_indexed,
                "raw_bytes": stats.raw_json_bytes,
                "compressed_bytes": stats.compressed_bytes,
                "compression_ratio": stats.compression_ratio,
                "savings_pct": stats.memory_savings_percent
            })
        elif self.path == "/api/audio/resample_spec":
            in_path = data.get("input_path", "audio.mp3")
            target_hz = int(data.get("target_hz", 48000))
            spec = DirectClockAudioResampler.build_resample_spec(in_path, target_hz=target_hz)
            return self.send_json({
                "ok": True,
                "input": spec.input_audio_path,
                "output": spec.output_audio_path,
                "hz": spec.target_sample_rate_hz,
                "channels": spec.target_channels,
                "engine": spec.resampler_engine,
                "args": spec.ffmpeg_filter_args,
                "speedup": spec.estimated_mixing_speedup_factor
            })
        elif self.path == "/api/timeline/virtualize":
            project_id = data.get("project_id")
            playhead = int(data.get("playhead_scene", 1))
            plan = self.repo.get(project_id) if project_id else None
            if not plan:
                return self.send_json({"ok": False, "error": "Projeto não encontrado"}, 404)
            virtualizer = getattr(self, "_timeline_virtualizer", None)
            if not virtualizer:
                self._timeline_virtualizer = LazyTimelineVirtualizer(window_radius=2)
                virtualizer = self._timeline_virtualizer
                virtualizer.register_scenes(plan.scenes)
            w_state = virtualizer.update_playhead(playhead)
            return self.send_json({
                "ok": True,
                "playhead": w_state.current_playhead_scene,
                "total_scenes": w_state.total_scenes,
                "active_handles": w_state.active_handles_count,
                "hibernating_handles": w_state.hibernating_handles_count,
                "savings_pct": round((w_state.hibernating_handles_count / max(1, w_state.total_scenes)) * 100, 1)
            })
        elif self.path == "/api/audio/scratchpad_store":
            track_name = data.get("track_name", "voice_track")
            pcm_hex = data.get("pcm_hex", "")
            raw_pcm = bytes.fromhex(pcm_hex) if pcm_hex else b"\0" * 48000 * 4 # 1 segundo mock
            scratchpad = getattr(self, "_audio_scratchpad", None)
            if not scratchpad:
                self._audio_scratchpad = FlacInMemoryScratchpad()
                scratchpad = self._audio_scratchpad
            stats = scratchpad.store_pcm_track(track_name, raw_pcm)
            return self.send_json({
                "ok": True,
                "track": stats.track_name,
                "duration_sec": stats.duration_sec,
                "raw_bytes": stats.raw_pcm_bytes,
                "compressed_bytes": stats.compressed_bytes,
                "savings_pct": stats.savings_percent
            })
        elif self.path == "/api/storage/preallocate":
            file_path = data.get("file_path", "d:/CUTWIREDRIFT/renders/final_output.mp4")
            duration = float(data.get("duration_sec", 1200.0))
            bitrate = float(data.get("bitrate_mbps", 8.0))
            estimated_size = ZeroFragmentationPreallocator.estimate_video_file_size_bytes(duration, bitrate)
            res = ZeroFragmentationPreallocator.preallocate_file(file_path, estimated_size)
            return self.send_json({
                "ok": res.is_success,
                "file": res.target_file_path,
                "preallocated_bytes": res.preallocated_bytes,
                "preallocated_mb": res.preallocated_mb,
                "method": res.method_used,
                "error": res.error_message
            })
        elif self.path == "/api/eco/wattage_profile":
            profile_name = data.get("profile", "balanced_power")
            p_profile = GreenWattageCapper.calculate_power_profile(profile_name)
            mask_val = int(p_profile.affinity_mask_hex, 16)
            applied = GreenWattageCapper.apply_affinity(mask_val)
            return self.send_json({
                "ok": True,
                "profile": p_profile.profile_name,
                "affinity_hex": p_profile.affinity_mask_hex,
                "active_cores": p_profile.active_core_count,
                "wattage_reduction_pct": p_profile.estimated_wattage_reduction_pct,
                "tdp_watts": p_profile.estimated_tdp_watts,
                "affinity_applied": applied
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
            duration_type = data.get("duration_type", "shorts")
            duration_minutes = data.get("duration_minutes")
            language = data.get("language", "pt")
            cache_k = f"script_gen:{topic.lower().strip()}:{duration_type}:{duration_minutes}:{language}"
            hit = GLOBAL_CACHE.get(cache_k)
            if hit:
                return self.send_json({"ok": True, "script": hit, "cached": True})
            script = ScriptGenerator.generate(topic, duration_type=duration_type, duration_minutes=duration_minutes, language=language)
            GLOBAL_CACHE.set(cache_k, script, ttl_sec=600)
            return self.send_json({"ok": True, "script": script, "cached": False})

        elif self.path == "/api/mega/plan":
            topic = data.get("topic", "Ciência e Universo")
            try:
                minutes = float(data.get("minutes", 30.0))
            except (ValueError, TypeError):
                minutes = 30.0
            mega_plan = MegaDurationArchitect.plan_mega_production(topic=topic, target_minutes=minutes)
            return self.send_json({"ok": True, "plan": mega_plan.to_dict()})

        elif self.path == "/api/mega/render_chapter":
            topic = data.get("topic", "Ciência e Universo")
            try:
                minutes = float(data.get("minutes", 30.0))
            except (ValueError, TypeError):
                minutes = 30.0
            chapter_index = int(data.get("chapter_index", 1))
            mega_plan = MegaDurationArchitect.plan_mega_production(topic=topic, target_minutes=minutes)
            result = MegaDurationArchitect.simulate_chapter_render_lifecycle(mega_plan, chapter_index)
            return self.send_json({"ok": True, "chapter_render": result})

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
                DiskSpaceGuard.ensure_healthy_space(min_free_gb=0.3)
                for s in plan.scenes:
                    cands = ConcurrentProviderSearch.search_scene_candidates(
                        scene=s,
                        plan_aspect_ratio=plan.config.aspect_ratio,
                        plan_media_type=plan.config.media_type,
                        target_candidates_count=5
                    )
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

        elif self.path == "/api/color_grading/apply":
            project_id = data.get("project_id")
            preset_id = data.get("preset_id", "warm_documentary")
            plan = self.repo.get(project_id)
            if not plan:
                return self.send_json({"ok": False, "error": "Not found"}, 404)
            plan.config.extra = plan.config.extra or {}
            plan.config.extra["color_grading"] = preset_id
            self.repo.save(plan)
            filter_str = ColorGradingEngine.get_filter(preset_id)
            return self.send_json({"ok": True, "preset_id": preset_id, "ffmpeg_filter": filter_str})

        elif self.path == "/api/polish_tone":
            project_id = data.get("project_id")
            tone_id = data.get("tone_id", "shorts_viral")
            plan = self.repo.get(project_id)
            if not plan:
                return self.send_json({"ok": False, "error": "Not found"}, 404)
            ScriptTonePolisher.polish_plan(plan, tone_id)
            self.repo.save(plan)
            return self.send_json({"ok": True, "plan": plan.to_dict()})

        elif self.path == "/api/broll/bounce":
            project_id = data.get("project_id")
            threshold_sec = float(data.get("threshold_sec", 4.5))
            plan = self.repo.get(project_id)
            if not plan:
                return self.send_json({"ok": False, "error": "Not found"}, 404)
            result = BrollBouncer.apply_cutaways_to_plan(plan, threshold_sec=threshold_sec)
            self.repo.save(plan)
            return self.send_json({"ok": True, **result})

        elif self.path == "/api/project/package_zip":
            project_id = data.get("project_id")
            plan = self.repo.get(project_id)
            if not plan:
                return self.send_json({"ok": False, "error": "Not found"}, 404)
            res = ProjectPackagerZip.package_project(plan)
            return self.send_json({
                "ok": True,
                "project_id": res.project_id,
                "zip_path": res.zip_path,
                "file_count": res.file_count,
                "compressed_bytes": res.compressed_bytes,
                "uncompressed_bytes": res.uncompressed_bytes,
                "included_files": res.included_files
            })

        elif self.path == "/api/subtitles/generate_styled":
            project_id = data.get("project_id")
            style_id = data.get("style_id", "hormozi_viral")
            plan = self.repo.get(project_id)
            if not plan:
                return self.send_json({"ok": False, "error": "Not found"}, 404)
            safe_title = "".join(c for c in plan.title if c.isalnum() or c in (" ", "_", "-")).strip().replace(" ", "_")
            out_ass = Path("d:/CUTWIREDRIFT") / f"Legendas_{safe_title}_{style_id}.ass"
            ass_text = AITranscriptionSubtitleStyler.generate_styled_ass(plan, style_id=style_id, output_path=str(out_ass))
            return self.send_json({
                "ok": True,
                "file_path": str(out_ass),
                "style_id": style_id,
                "style_name": style_id.replace("_", " ").title()
            })

        elif self.path == "/api/thumbnail/compose":
            project_id = data.get("project_id")
            headline = data.get("headline_text", "A VERDADE")
            plan = self.repo.get(project_id)
            if not plan:
                return self.send_json({"ok": False, "error": "Not found"}, 404)
            res = AutoThumbnailVisualComposer.compose_thumbnail(plan, headline_text=headline)
            return self.send_json({
                "ok": True,
                "project_id": res.project_id,
                "output_image_path": res.output_image_path,
                "width": res.width,
                "height": res.height,
                "hero_platform": res.hero_platform,
                "headline_text": res.headline_text,
                "engine": res.used_engine
            })
        elif self.path == "/api/templates/apply":
            proj_id = data.get("project_id")
            tmpl_id = data.get("template_id", "space_scifi")
            plan = self.repo.get(proj_id) if proj_id else None
            if not plan:
                return self.send_json({"ok": False, "error": "Projeto não encontrado"}, 404)
            plan = OneClickPresetVideoTemplates.apply_template_to_plan(plan, tmpl_id)
            self.repo.save(plan)
            return self.send_json({
                "ok": True,
                "project_id": plan.project_id,
                "template_id": tmpl_id,
                "config": {
                    "aspect_ratio": plan.config.aspect_ratio,
                    "width": plan.config.width,
                    "height": plan.config.height,
                    "transition_kind": plan.config.transition_kind,
                    "enable_ken_burns": plan.config.enable_ken_burns,
                    "extra": plan.config.extra
                }
            })
        elif self.path == "/api/branding/apply":
            proj_id = data.get("project_id")
            plan = self.repo.get(proj_id) if proj_id else None
            channel_handle = data.get("channel_handle") or data.get("channel_name") or "@DriftAI"
            branding_cfg = BrandingConfig(
                channel_tag=channel_handle,
                position=data.get("position", "top_right"),
                opacity=float(data.get("opacity", 0.70)),
                enable_lower_third=bool(data.get("enable_intro_lower_third", True)),
                lower_third_title=data.get("channel_name", "DOCUMENTÁRIO EXCLUSIVO")
            )
            filt = VideoWatermarkBrandingEngine.generate_ffmpeg_branding_filter(branding_cfg)
            if plan:
                plan.config.extra = plan.config.extra or {}
                plan.config.extra["branding"] = {
                    "channel_tag": branding_cfg.channel_tag,
                    "position": branding_cfg.position,
                    "opacity": branding_cfg.opacity,
                    "enable_lower_third": branding_cfg.enable_lower_third,
                    "lower_third_title": branding_cfg.lower_third_title,
                    "ffmpeg_filter": filt
                }
                self.repo.save(plan)
            return self.send_json({
                "ok": True,
                "project_id": proj_id,
                "ffmpeg_filter": filt
            })
        elif self.path == "/api/retention/remediate":
            proj_id = data.get("project_id")
            plan = self.repo.get(proj_id) if proj_id else None
            if not plan:
                return self.send_json({"ok": False, "error": "Projeto não encontrado"}, 404)
            res = VisualRetentionHeatmapAuditor.auto_remediate_plan_pacing(plan)
            self.repo.save(plan)
            return self.send_json({"ok": True, **res})
        elif self.path == "/api/multiexport/render":
            proj_id = data.get("project_id")
            selected = data.get("presets", [])
            plan = self.repo.get(proj_id) if proj_id else None
            if not plan:
                return self.send_json({"ok": False, "error": "Projeto não encontrado"}, 404)
            manifest = SocialMediaMultiExportPresets.build_export_manifest(plan, selected_ids=selected)
            return self.send_json({"ok": True, "manifest": manifest})
        elif self.path == "/api/hooks/apply":
            proj_id = data.get("project_id")
            hook_id = data.get("hook_id", "hook_provocative_question")
            plan = self.repo.get(proj_id) if proj_id else None
            if not plan:
                return self.send_json({"ok": False, "error": "Projeto não encontrado"}, 404)
            plan = AIStoryHookABSplitTester.apply_hook_to_plan(plan, hook_id)
            self.repo.save(plan)
            return self.send_json({"ok": True, "project_id": plan.project_id, "applied_hook_id": hook_id})
        elif self.path == "/api/beat/apply":
            proj_id = data.get("project_id")
            bpm = float(data.get("bpm", 90.0))
            plan = self.repo.get(proj_id) if proj_id else None
            if not plan:
                return self.send_json({"ok": False, "error": "Projeto não encontrado"}, 404)
            res = SoundtrackBeatDropSceneSync.synchronize_timeline_to_bpm(plan, bpm=bpm)
            self.repo.save(plan)
            return self.send_json({"ok": True, **res})
        elif self.path == "/api/pacing/apply":
            proj_id = data.get("project_id")
            plan = self.repo.get(proj_id) if proj_id else None
            if not plan:
                return self.send_json({"ok": False, "error": "Projeto não encontrado"}, 404)
            pacing_res = SmartAudienceRetentionPacer.calculate_pacing_waves(plan)
            self.repo.save(plan)
            return self.send_json({"ok": True, **pacing_res})
        elif self.path == "/api/vocabulary/enhance":
            proj_id = data.get("project_id")
            plan = self.repo.get(proj_id) if proj_id else None
            if not plan:
                return self.send_json({"ok": False, "error": "Projeto não encontrado"}, 404)
            enhance_data = ViralHookVocabularyAuditor.enhance_script_dialogue(plan)
            self.repo.save(plan)
            return self.send_json({"ok": True, **enhance_data})
        elif self.path == "/api/broll/insert_slots":
            proj_id = data.get("project_id")
            plan = self.repo.get(proj_id) if proj_id else None
            if not plan:
                return self.send_json({"ok": False, "error": "Projeto não encontrado"}, 404)
            insert_res = DynamicBrollPacer.auto_insert_broll_slots(plan)
            self.repo.save(plan)
            return self.send_json({"ok": True, **insert_res})
        elif self.path == "/api/film_stock/apply":
            proj_id = data.get("project_id")
            stock_name = data.get("film_stock", "kodak_vision3_5219")
            grain_intensity = float(data.get("grain_intensity", 1.0))
            plan = self.repo.get(proj_id) if proj_id else None
            if not plan:
                return self.send_json({"ok": False, "error": "Projeto não encontrado"}, 404)
            film_res = AutoColorToneFilmStockEmulator.apply_film_stock_to_plan(plan, stock_name, grain_intensity)
            self.repo.save(plan)
            return self.send_json({"ok": True, **film_res})
        elif self.path == "/api/voice/denoise/apply":
            proj_id = data.get("project_id")
            profile_name = data.get("profile", "studio_clean")
            plan = self.repo.get(proj_id) if proj_id else None
            if not plan:
                return self.send_json({"ok": False, "error": "Projeto não encontrado"}, 404)
            denoise_res = AIVoiceDenoiseSpectralIsolator.apply_profile_to_project(plan, profile_name)
            self.repo.save(plan)
            return self.send_json({"ok": True, **denoise_res})
        elif self.path == "/api/render/recovery/clear":
            proj_id = data.get("project_id", "default")
            AutoRenderCrashRecoveryGuard.clear_checkpoint(proj_id)
            return self.send_json({"ok": True, "message": "Checkpoint descartado com sucesso."})
        elif self.path == "/api/bpm/align":
            proj_id = data.get("project_id")
            bpm = float(data.get("bpm", 120.0))
            mode = data.get("alignment_mode", "full_measure")
            plan = self.repo.get(proj_id) if proj_id else None
            if not plan:
                return self.send_json({"ok": False, "error": "Projeto não encontrado"}, 404)
            align_res = SmartVisualPacingBPMAligner.align_scenes_to_bpm(plan, bpm=bpm, alignment_mode=mode)
            self.repo.save(plan)
            return self.send_json({"ok": True, "alignment": align_res})
        elif self.path == "/api/watermark/apply":
            proj_id = data.get("project_id")
            wm_path = data.get("watermark_path", "assets/branding/logo_watermark.png")
            position = data.get("position", "bottom_right")
            opacity = float(data.get("opacity", 0.55))
            plan = self.repo.get(proj_id) if proj_id else None
            if not plan:
                return self.send_json({"ok": False, "error": "Projeto não encontrado"}, 404)
            wm_res = AutoVideoWatermarkBrandingDirector.apply_watermark_to_plan(plan, wm_path, position, opacity)
            self.repo.save(plan)
            return self.send_json({"ok": True, **wm_res})
        elif self.path == "/api/hdr/apply":
            proj_id = data.get("project_id")
            preset_name = data.get("preset", "mobius_balanced")
            plan = self.repo.get(proj_id) if proj_id else None
            if not plan:
                return self.send_json({"ok": False, "error": "Projeto não encontrado"}, 404)
            hdr_res = HDRToSDRToneMapper.apply_tone_mapping_to_plan(plan, preset_name)
            self.repo.save(plan)
            return self.send_json({"ok": True, **hdr_res})
        elif self.path == "/api/audio/surround51/apply":
            proj_id = data.get("project_id")
            boost = float(data.get("boost", 2.0))
            plan = self.repo.get(proj_id) if proj_id else None
            if not plan:
                return self.send_json({"ok": False, "error": "Projeto não encontrado"}, 404)
            surr_res = StereoTo51SurroundUpmixer.apply_51_upmix_to_plan(plan, center_dialogue_boost_db=boost)
            self.repo.save(plan)
            return self.send_json({"ok": True, **surr_res})
        elif self.path == "/api/audio/ducking/apply":
            proj_id = data.get("project_id")
            preset_name = data.get("preset", "broadcast_standard")
            plan = self.repo.get(proj_id) if proj_id else None
            if not plan:
                return self.send_json({"ok": False, "error": "Projeto não encontrado"}, 404)
            duck_calc = DynamicAudioDuckingSidechainEngine.calculate_ducking_filter(preset=preset_name)
            if not hasattr(plan, "metadata") or plan.metadata is None:
                plan.metadata = {}
            plan.metadata["sidechain_ducking"] = duck_calc
            self.repo.save(plan)
            return self.send_json({"ok": True, "sidechain_ducking": duck_calc})
        elif self.path == "/api/launcher/deploy":
            port_val = int(data.get("port", 8765))
            cur_dir = os.path.dirname(os.path.abspath(__file__))
            launch_res = DesktopLauncherDaemonPackager.deploy_desktop_launchers(cur_dir, port=port_val)
            return self.send_json({"ok": True, "launcher": launch_res})
        elif self.path == "/api/pruner/apply":
            proj_id = data.get("project_id")
            plan = self.repo.get(proj_id) if proj_id else None
            if not plan:
                return self.send_json({"ok": False, "error": "Projeto não encontrado"}, 404)
            scenes_dict = [
                {
                    "duration": getattr(sc, "duration", 4.0),
                    "narration_text": getattr(sc, "narration_text", ""),
                    "concept": getattr(sc, "concept", "")
                }
                for sc in plan.scenes
            ]
            pruner_res = PreRenderDeadweightPruner.prune_timeline(scenes_dict)
            from models.scene_plan import Scene
            new_scenes = []
            for item in pruner_res["cleaned_scenes"]:
                new_scenes.append(Scene(
                    order=item["order"],
                    duration=item["duration"],
                    narration_text=item.get("narration_text", ""),
                    concept=item.get("concept", "")
                ))
            plan.scenes = new_scenes
            self.repo.save(plan)
            return self.send_json({"ok": True, "pruner": pruner_res})
        elif self.path == "/api/db/wal_checkpoint":
            cp_data = SQLiteWALCheckpointGovernor.execute_passive_checkpoint()
            return self.send_json({"ok": True, "checkpoint": cp_data})
        elif self.path == "/api/system/ram/trim":
            trim_data = RamWorkingSetTrimmer.trim_working_set()
            return self.send_json({"ok": True, "trim": trim_data})
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


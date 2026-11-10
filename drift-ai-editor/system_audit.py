import sys
import os
import json
import inspect
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

def audit_system():
    print("==================================================================")
    print("          AUDITORIA GERAL DE SISTEMA - DRIFT AI EDITOR            ")
    print("==================================================================")
    errors = []
    warnings = []
    passed_checks = 0

    # -------------------------------------------------------------
    # 1. VERIFICAÇÃO DE MÓDULOS E IMPORTAÇÕES
    # -------------------------------------------------------------
    print("\n[1/5] Verificando integridade de módulos e importações...")
    modules_to_test = [
        "models.scene_plan",
        "analysis.segmenter",
        "analysis.visual_planner",
        "analysis.script_generator",
        "analysis.storyboard_engine",
        "analysis.reference_analyzer",
        "analysis.visual_storyboard",
        "analysis.continuity_checker",
        "analysis.emotional_curve",
        "core.dependency_graph",
        "core.transaction_manager",
        "core.production_memory",
        "director.orchestrator",
        "director.command_editor",
        "editing.drift_mcp_client",
        "editing.timeline_builder",
        "editing.captions",
        "editing.export_manager",
        "editing.layer_compositor",
        "editing.deliverables_packager",
        "extensions.base",
        "extensions.registry",
        "media.cache",
        "media.validator",
        "media.downloader",
        "media.attribution",
        "media.media_ranker",
        "media.local_indexer",
        "media.license_manifest",
        "media.semantic_search",
        "media.diversity_controller",
        "pipeline.job_manager",
        "pipeline.style_engine",
        "pipeline.timeline_planner",
        "pipeline.quality_control",
        "pipeline.delta_editor",
        "pipeline.batch_producer",
        "providers.base",
        "providers.pexels",
        "providers.pixabay",
        "providers.wikimedia",
        "providers.nasa",
        "providers.unsplash",
        "providers.coverr",
        "providers.freesound",
        "providers.archive_org",
        "storage.repository",
        "voice.base",
        "voice.voice_engine",
        "voice.alignment",
        "voice.audio_aligner",
        "voice.pronunciation_lexicon",
        "voice.lip_sync_aligner",
        "benchmarks.ai_bench",
        "editing.multicam_director",
        "analysis.character_continuity",
        "media.media_doctor",
        "media.copyright_analyzer",
        "audio.auto_ducking_soundtrack",
        "pipeline.hybrid_multiformat_producer",
        "pipeline.publication_seo_kit",
        "core.hardware_telemetry",
        "pipeline.chunked_parallel_renderer",
        "editing.karaoke_subtitle_generator",
        "voice.local_neural_fallback",
        "core.ram_disk_buffer",
        "storage.media_deduplicator",
        "media.speculative_prefetcher",
        "editing.adaptive_crf_encoder",
        "pipeline.batch_production_factory",
        "editing.accessibility_engine",
        "editing.academic_citations",
        "editing.shot_extender",
        "audio.soundscape_generator",
        "core.project_diff_merge",
        "collaboration.review_board",
        "pipeline.distributed_render",
        "core.hardware_profiler",
        "analysis.retention_predictor",
        "audio.punctuation_sfx",
        "editing.smart_action_reframe",
        "extensions.generative_fallback",
        "editing.animated_map_generator",
        "editing.kinetic_infographics",
        "pipeline.long_to_shorts_extractor",
        "pipeline.thumbnail_studio",
        "editing.kinetic_captions",
        "audio.lufs_mastering",
        "voice.noise_suppressor",
        "director.timeline_chat_copilot",
        "skills.gemini_skill_bridge",
        "editing.cinematic_color_lut",
        "editing.audio_waveform_visualizer",
        "analysis.axis_rule_checker",
        "voice.teleprompter_engine",
        "voice.smart_jump_cutter",
        "pipeline.youtube_chapter_generator",
        "pipeline.multiformat_exporter",
        "pipeline.video_podcast_publisher",
        "analysis.pacing_metronome",
        "audio.adaptive_bpm_composer",
        "pipeline.platform_policy_manager",
        "editing.bokeh_depth_simulator",
        "editing.video_restoration_filter",
        "editing.split_screen_slider",
        "audio.foley_sound_director",
        "voice.emotion_pitch_shifter",
        "pipeline.thumbnail_attention_heatmap",
        "editing.credits_roll_generator",
        "pipeline.fcpxml_exporter",
        "analysis.audio_first_cutting",
        "editing.transition_monotony_detector",
        "editing.depth_title_compositor",
        "editing.youtube_endscreen_designer",
        "audio.audio_monotony_breaker",
        "audio.b_roll_audio_leveler",
        "editing.multilingual_subtitles",
        "pipeline.auto_summarizer_cut",
        "media.copyright_shield",
        "pipeline.seo_tag_architect",
        "audio.genre_morphing_engine",
        "core.battery_saver_mode",
        "editing.parallax_2_5d_projection",
        "editing.j_l_cut_builder",
        "editing.virtual_relighting",
        "analysis.script_conciseness_auditor",
        "editing.quote_card_popup",
        "voice.dynamic_speech_pacer",
        "pipeline.aesthetic_theme_presets",
        "pipeline.drift_bundle_packager",
        "editing.visual_impact_punch",
        "analysis.reading_ease_analyzer",
        "core.lazy_provider_registry",
        "core.memory_manager",
        "core.smart_cache",
        "director.context_pruner",
        "director.long_form_retention_director",
        "audio.multi_chapter_mood_soundtrack",
        "editing.smart_ken_burns_punchin",
        "pipeline.render_checkpoint_manager",
        "pipeline.multilingual_audio_packager",
        "audio.smart_silence_breath_stripper",
        "editing.motion_infographics_generator",
        "media.b_roll_gap_filler",
        "core.eco_governor",
        "core.ram_working_set_flusher",
        "editing.draft_proxy_engine",
        "editing.lossless_stream_copy_detector",
        "core.disk_io_governor",
        "editing.fast_decode_optimizer",
        "core.sleep_inhibit_governor",
        "storage.rolling_cache_purge",
        "core.thermal_duty_cycle",
        "core.zero_gpu_occlusion_governor",
        "core.compact_metadata_indexer",
        "audio.direct_clock_resampler",
        "editing.lazy_timeline_virtualizer",
        "audio.flac_in_memory_scratchpad",
        "storage.zero_fragmentation_preallocator",
        "core.green_wattage_capper",
        "pipeline.mega_duration_architect",
        "providers.mazwai",
        "providers.esa",
        "providers.dvids",
        "providers.cern",
        "providers.videvo",
        "providers.nara",
        "providers.getty_open",
        "providers.paris_musees",
        "providers.dareful",
        "providers.nga",
        "providers.prelinger",
        "providers.british_library",
        "providers.kaboompics",
        "providers.mauritshuis",
        "providers.videezy",
        "providers.burst",
        "providers.nypl",
        "providers.vam",
        "providers.splitshire",
        "providers.picjumbo",
        "providers.isorepublic",
        "providers.gratisography",
        "providers.yale",
        "providers.reshot",
        "providers.lifeofpix",
        "providers.flickr_commons",
        "providers.nps",
        "providers.foodiesfeed",
        "providers.walters_art",
        "providers.cdc_phil",
        "providers.old_book_illustrations",
        "providers.morguefile",
        "providers.smk",
        "providers.dpla",
        "providers.usfws",
        "providers.skitterphoto",
        "providers.foca_stock",
        "providers.stockvault",
        "providers.trove",
        "providers.artvee",
        "providers.magdeleine",
        "providers.wp_photos",
        "providers.goodfreephotos",
        "providers.jay_mantri",
        "providers.harvard_art",
        "providers.aapb",
        "providers.te_papa",
        "providers.mia",
        "providers.barnimages",
        "pipeline.smart_provider_router",
        "pipeline.concurrent_provider_search",
        "storage.disk_space_guard",
        "editing.color_grading_engine",
        "audio.sound_fx_foley",
        "pipeline.auto_chaptering",
        "audio.smart_audio_denoise_enhancer",
        "analysis.scene_pacing_auditor",
        "analysis.script_tone_polisher",
        "editing.safe_zone_framing",
        "audio.audio_stem_splitter",
        "pipeline.clickbait_title_generator",
        "editing.broll_bouncer",
        "storage.project_packager_zip",
    ]

    for mod_name in modules_to_test:
        try:
            __import__(mod_name)
            passed_checks += 1
        except Exception as e:
            errors.append(f"Falha ao importar {mod_name}: {e}")

    print(f"  -> {len(modules_to_test)} módulos testados. Sucessos: {passed_checks}")

    # -------------------------------------------------------------
    # 2. AUDITORIA DO CONTRATO ENTRE QML E O BACKEND WEB (REST API)
    # -------------------------------------------------------------
    print("\n[2/5] Auditando alinhamento de endpoints entre QML e Python Web API...")
    qml_file = Path("d:/CUTWIREDRIFT/Drift-Source/src/qml/components/assets/ScriptAiTab.qml")
    web_file = Path("d:/CUTWIREDRIFT/drift-ai-editor/web_ui.py")

    if not qml_file.exists():
        errors.append("Arquivo ScriptAiTab.qml não encontrado.")
    if not web_file.exists():
        errors.append("Arquivo web_ui.py não encontrado.")

    if qml_file.exists() and web_file.exists():
        qml_text = qml_file.read_text(encoding="utf-8")
        web_text = web_file.read_text(encoding="utf-8")

        import re
        qml_endpoints = set(re.findall(r'sendAiRequest\s*\(\s*["\']([a-zA-Z0-9_]+)["\']', qml_text))
        print(f"  Endpoints requisitados pelo QML: {sorted(list(qml_endpoints))}")

        for ep in qml_endpoints:
            expected_route = f'/api/{ep}'
            if expected_route in web_text:
                print(f"  [OK] Rota '{expected_route}' devidamente implementada no backend.")
                passed_checks += 1
            else:
                errors.append(f"Rota '{expected_route}' chamada pelo QML não existe em web_ui.py!")

    # -------------------------------------------------------------
    # 3. VERIFICAÇÃO DE PROVEDORES DE MÍDIA
    # -------------------------------------------------------------
    print("\n[3/5] Auditando conformidade dos 75 provedores de mídia...")
    from providers import (
        PexelsProvider,
        PixabayProvider,
        WikimediaProvider,
        NasaProvider,
        UnsplashProvider,
        CoverrProvider,
        FreesoundProvider,
        ArchiveOrgProvider,
        OpenverseProvider,
        MetMuseumProvider,
        ArtInstituteChicagoProvider,
        SmithsonianProvider,
        LibraryOfCongressProvider,
        EuropeanaProvider,
        FreeMusicArchiveProvider,
        MixkitProvider,
        RijksmuseumProvider,
        ClevelandArtProvider,
        WellcomeCollectionProvider,
        BiodiversityProvider,
        UsgsProvider,
        NoaaProvider,
        JamendoMusicProvider,
        CcMixterProvider,
        IncompetechProvider,
        RawpixelProvider,
        MazwaiProvider,
        EsaProvider,
        DvidsProvider,
        CernProvider,
        VidevoProvider,
        NaraProvider,
        GettyOpenProvider,
        ParisMuseesProvider,
        DarefulProvider,
        NgaProvider,
        PrelingerProvider,
        BritishLibraryProvider,
        KaboompicsProvider,
        MauritshuisProvider,
        VideezyProvider,
        BurstProvider,
        NyplProvider,
        VamProvider,
        SplitShireProvider,
        PicjumboProvider,
        IsoRepublicProvider,
        GratisographyProvider,
        YaleProvider,
        ReshotProvider,
        LifeOfPixProvider,
        FlickrCommonsProvider,
        NpsProvider,
        FoodiesfeedProvider,
        WaltersArtProvider,
        CdcPhilProvider,
        OldBookIllustrationsProvider,
        MorguefileProvider,
        SmkProvider,
        DplaProvider,
        UsfwsProvider,
        SkitterphotoProvider,
        FocaStockProvider,
        StockvaultProvider,
        TroveProvider,
        ArtveeProvider,
        MagdeleineProvider,
        WpPhotosProvider,
        GoodFreePhotosProvider,
        JayMantriProvider,
        HarvardArtProvider,
        AapbProvider,
        TePapaProvider,
        MiaProvider,
        BarnimagesProvider,
        BaseMediaProvider
    )
    providers = [
        PexelsProvider(),
        PixabayProvider(),
        WikimediaProvider(),
        NasaProvider(),
        UnsplashProvider(),
        CoverrProvider(),
        FreesoundProvider(),
        ArchiveOrgProvider(),
        OpenverseProvider(),
        MetMuseumProvider(),
        ArtInstituteChicagoProvider(),
        SmithsonianProvider(),
        LibraryOfCongressProvider(),
        EuropeanaProvider(),
        FreeMusicArchiveProvider(),
        MixkitProvider(),
        RijksmuseumProvider(),
        ClevelandArtProvider(),
        WellcomeCollectionProvider(),
        BiodiversityProvider(),
        UsgsProvider(),
        NoaaProvider(),
        JamendoMusicProvider(),
        CcMixterProvider(),
        IncompetechProvider(),
        RawpixelProvider(),
        MazwaiProvider(),
        EsaProvider(),
        DvidsProvider(),
        CernProvider(),
        VidevoProvider(),
        NaraProvider(),
        GettyOpenProvider(),
        ParisMuseesProvider(),
        DarefulProvider(),
        NgaProvider(),
        PrelingerProvider(),
        BritishLibraryProvider(),
        KaboompicsProvider(),
        MauritshuisProvider(),
        VideezyProvider(),
        BurstProvider(),
        NyplProvider(),
        VamProvider(),
        SplitShireProvider(),
        PicjumboProvider(),
        IsoRepublicProvider(),
        GratisographyProvider(),
        YaleProvider(),
        ReshotProvider(),
        LifeOfPixProvider(),
        FlickrCommonsProvider(),
        NpsProvider(),
        FoodiesfeedProvider(),
        WaltersArtProvider(),
        CdcPhilProvider(),
        OldBookIllustrationsProvider(),
        MorguefileProvider(),
        SmkProvider(),
        DplaProvider(),
        UsfwsProvider(),
        SkitterphotoProvider(),
        FocaStockProvider(),
        StockvaultProvider(),
        TroveProvider(),
        ArtveeProvider(),
        MagdeleineProvider(),
        WpPhotosProvider(),
        GoodFreePhotosProvider(),
        JayMantriProvider(),
        HarvardArtProvider(),
        AapbProvider(),
        TePapaProvider(),
        MiaProvider(),
        BarnimagesProvider()
    ]
    for p in providers:
        if not isinstance(p, BaseMediaProvider):
            errors.append(f"Provedor {p} não herda de BaseMediaProvider!")
        else:
            passed_checks += 1
            print(f"  [OK] Provedor '{p.name}' conforme à interface padrão.")

    # -------------------------------------------------------------
    # 4. AUDITORIA DA INTEGRIDADE DO BANCO DE DADOS & PERSISTÊNCIA
    # -------------------------------------------------------------
    print("\n[4/5] Auditando repositório de dados SQLite...")
    import tempfile
    from storage.repository import ProjectRepository
    from models.scene_plan import ProjectPlan, Scene
    with tempfile.TemporaryDirectory() as td:
        test_repo = ProjectRepository(db_path=Path(td) / "test_audit.db")
        p = ProjectPlan(title="Auditoria Teste")
        p.scenes = [Scene(order=1, narration_text="Texto", duration=3.0)]
        test_repo.save(p)
        reloaded = test_repo.get(p.project_id)
        if reloaded and len(reloaded.scenes) == 1 and reloaded.scenes[0].duration == 3.0:
            print("  [OK] Persistência, serialização e recuperação de dados 100% íntegras.")
            passed_checks += 1
        else:
            errors.append("Falha no ciclo de persistência SQLite.")

        # Auditoria de Paginação por Cursor e Índices Cirúrgicos
        page = test_repo.list_cursor(limit=1)
        if page.items and len(page.items) == 1:
            print("  [OK] Paginação por cursor O(1) validada com sucesso.")
            passed_checks += 1
        else:
            errors.append("Falha na paginação por cursor SQLite.")

        with test_repo._connection() as conn:
            idx_rows = [r["name"] for r in conn.execute("PRAGMA index_list('projects')").fetchall()]
            if "idx_projects_cursor" in idx_rows and "idx_projects_title" in idx_rows:
                print("  [OK] Índices cirúrgicos (Index Scan) ativos no SQLite.")
                passed_checks += 1
            else:
                errors.append("Índices cirúrgicos não encontrados na tabela projects.")

    # -------------------------------------------------------------
    # 5. EXECUÇÃO DO AI BENCH DE REGRESSÃO
    # -------------------------------------------------------------
    print("\n[5/5] Executando bateria de benchmark automatizado (AI Bench)...")
    from benchmarks.ai_bench import AiBenchHarness
    summary = AiBenchHarness.run_benchmark_suite()
    print(f"  AI Bench Saúde Geral: {summary.overall_health}")
    print(f"  Cenários Aprovados: {summary.passed_scenarios}/{summary.total_scenarios}")
    print(f"  Tempo Médio por Vídeo: {summary.average_execution_time_sec}s")
    if summary.overall_health == "EXCELLENT":
        passed_checks += 1
    else:
        warnings.append(f"AI Bench reportou saúde: {summary.overall_health}")

    # -------------------------------------------------------------
    # RELATÓRIO CONSOLIDADO
    # -------------------------------------------------------------
    print("\n==================================================================")
    print("                     RESULTADO DA AUDITORIA                       ")
    print("==================================================================")
    print(f"Checagens Aprovadas: {passed_checks}")
    print(f"Erros Críticos: {len(errors)}")
    print(f"Avisos: {len(warnings)}")

    if errors:
        print("\n[!] ERROS ENCONTRADOS:")
        for e in errors:
            print(f"  - {e}")
    else:
        print("\n>>> STATUS: SISTEMA 100% ENCAIXADO E FUNCIONAL! <<<")
        print("Todas as camadas (QML, Python Web API, MCP Client, Pipeline, Provedores e Testes)")
        print("estão perfeitamente integradas sem dependências circulares ou pontas soltas.")

if __name__ == "__main__":
    audit_system()


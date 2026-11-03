import argparse
import sys
import json
from pathlib import Path

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from models.scene_plan import ProjectPlan, ProjectConfig, SceneState, Provenance
from analysis.segmenter import ScriptSegmenter
from analysis.visual_planner import VisualPlanner
from storage.repository import ProjectRepository
from editing.drift_mcp_client import DriftMcpClient
from voice.voice_engine import DriftChatterboxEngine
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
    RawpixelProvider
)
from media.downloader import MediaDownloader
from media.cache import MediaCache
from media.attribution import AttributionManager
from editing.timeline_builder import TimelineBuilder
from editing.captions import CaptionManager
from editing.export_manager import ExportManager

def check_system_status():
    print("=" * 60)
    print("Drift AI Editor - Verificação de Sistema & MCP")
    print("=" * 60)
    client = DriftMcpClient()
    try:
        client.start()
        print("[OK] Servidor MCP do Drift iniciado com sucesso.")
        engine = DriftChatterboxEngine(client)
        status = engine.check_status()
        print(f"[OK] Motor de Voz Local (Chatterbox): {'Disponivel' if status.get('available') else 'Indisponivel'}")
        langs = [l.get("code") for l in status.get("languages", [])]
        print(f"    Idiomas suportados: {', '.join(langs)}")
        
        voices = engine.list_voices()
        voice_names = [v.get("id") for v in voices]
        print(f"    Vozes disponíveis: {', '.join(voice_names)}")
    except Exception as e:
        print(f"[ERRO] Erro comunicando com Drift MCP: {e}")
    finally:
        client.stop()
    print("=" * 60)

def cmd_create_plan(args):
    repo = ProjectRepository()
    
    script_text = ""
    if args.file:
        file_path = Path(args.file)
        if not file_path.exists():
            print(f"Arquivo não encontrado: {file_path}")
            return
        script_text = file_path.read_text(encoding="utf-8")
    elif args.script:
        script_text = args.script
    else:
        print("Informe --script ou --file com o texto do roteiro.")
        return

    config = ProjectConfig(
        aspect_ratio=args.aspect_ratio,
        media_type=getattr(args, "media_type", "all"),
        language=args.language,
        voice_id=args.voice,
        exaggeration=args.exaggeration,
        enable_subtitles=not args.no_subtitles
    )
    config.update_resolution()

    plan = ProjectPlan(
        title=args.title or "Vídeo Automático IA",
        raw_script=script_text,
        config=config
    )

    scenes = ScriptSegmenter.parse(script_text, default_language=config.language, default_voice=config.voice_id)
    VisualPlanner.plan_project(scenes)
    plan.scenes = scenes
    plan.reindex_scenes()

    repo.save(plan)

    print(f"[OK] Projeto criado e salvo com sucesso!")
    print(f"    ID: {plan.project_id}")
    print(f"    Título: {plan.title}")
    print(f"    Total de Cenas: {len(plan.scenes)}")
    print(f"    Formato: {plan.config.aspect_ratio} ({plan.config.width}x{plan.config.height})")
    for s in plan.scenes:
        print(f"    - Cena {s.order:02d}: {s.narration_text[:40]}... -> Visual: {s.visual_description[:40]}... (Tags: {', '.join(s.english_keywords[:3])})")

def cmd_list_projects(args):
    repo = ProjectRepository()
    projects = repo.list_all()
    print(f"Total de projetos salvos: {len(projects)}")
    for p in projects:
        print(f"ID: {p['project_id']} | Cenas: {p['scene_count']} | Duração: {p['total_duration']:.1f}s | Título: {p['title']}")

def cmd_generate_voice(args):
    repo = ProjectRepository()
    plan = repo.get(args.project_id)
    if not plan:
        print(f"Projeto {args.project_id} não encontrado.")
        return

    print(f"Gerando áudio com Chatterbox local para {len(plan.scenes)} cenas...")
    client = DriftMcpClient()
    try:
        client.start()
        engine = DriftChatterboxEngine(client)
        for scene in plan.scenes:
            if scene.state != SceneState.READY or not scene.audio_path:
                print(f"  [>] Cena {scene.order}: {scene.narration_text[:40]}...")
                engine.generate_scene(scene)
                print(f"      Status: {scene.state.value} | Duração real: {scene.duration:.2f}s")
        
        plan.reindex_scenes()
        repo.save(plan)
        print(f"[OK] Voz gerada para todas as cenas. Duração total: {plan.total_duration():.2f}s")
    finally:
        client.stop()

def cmd_search_media(args):
    repo = ProjectRepository()
    plan = repo.get(args.project_id)
    if not plan:
        print(f"Projeto {args.project_id} não encontrado.")
        return

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
        RawpixelProvider()
    ]

    print(f"Pesquisando vídeos para {len(plan.scenes)} cenas...")
    for scene in plan.scenes:
        print(f"  [>] Cena {scene.order} (Busca: {', '.join(scene.english_keywords[:3])})")
        candidates = []
        for prov in providers:
            for kw in scene.english_keywords[:2]:
                results = prov.search(kw, orientation=plan.config.aspect_ratio, per_page=3)
                candidates.extend(results)
                if len(candidates) >= 4:
                    break
            if len(candidates) >= 4:
                break
        
        scene.candidates = candidates
        if candidates and not scene.selected_media:
            scene.selected_media = candidates[0]
            scene.provenance = Provenance(
                platform=scene.selected_media.platform,
                item_id=scene.selected_media.external_id,
                page_url=scene.selected_media.page_url,
                creator=scene.selected_media.creator,
                license=scene.selected_media.license,
                query=", ".join(scene.english_keywords[:2])
            )
            print(f"      Selecionado: [{scene.selected_media.platform}] {scene.selected_media.title}")
        else:
            print(f"      Nenhum resultado online encontrado para esta cena.")

    repo.save(plan)
    print(f"[OK] Pesquisa concluída e clipes associados.")

def cmd_build_timeline(args):
    repo = ProjectRepository()
    plan = repo.get(args.project_id)
    if not plan:
        print(f"Projeto {args.project_id} não encontrado.")
        return

    print("Baixando e validando clipes selecionados...")
    downloader = MediaDownloader()
    for scene in plan.scenes:
        if scene.selected_media and not scene.selected_media.local_cached_path:
            ok, path, msg = downloader.download_candidate(scene.selected_media)
            if ok and path:
                scene.selected_media.local_cached_path = str(path)
                if scene.provenance:
                    scene.provenance.local_path = str(path)
                print(f"  [OK] Cena {scene.order}: clipe baixado com sucesso.")
            else:
                print(f"  [ERRO] Cena {scene.order}: falha no download ({msg})")

    repo.save(plan)

    print("Montando timeline sincronizada no Drift via MCP...")
    client = DriftMcpClient()
    try:
        client.start()
        builder = TimelineBuilder(client)
        result = builder.build_timeline(plan)
        repo.save(plan)
        print(f"[OK] Montagem concluída com sucesso! Total de cenas na timeline: {result.get('scenes_placed')}")
    finally:
        client.stop()

def main():
    parser = argparse.ArgumentParser(description="Drift AI Editor - Edição Automática com Inteligência Artificial")
    subparsers = parser.add_subparsers(dest="command")

    # Status
    subparsers.add_parser("status", help="Verifica status do sistema e MCP")

    # Plan
    p_plan = subparsers.add_parser("plan", help="Cria plano de projeto e cenas a partir de roteiro")
    p_plan.add_argument("--script", type=str, help="Texto do roteiro")
    p_plan.add_argument("--file", type=str, help="Caminho do arquivo de texto do roteiro")
    p_plan.add_argument("--title", type=str, default="Vídeo com IA", help="Título do projeto")
    p_plan.add_argument("--aspect-ratio", type=str, default="16:9", choices=["16:9", "9:16", "1:1"])
    p_plan.add_argument("--media-type", type=str, default="all", choices=["all", "video", "image"], help="Tipo de midia")
    p_plan.add_argument("--language", type=str, default="pt", help="Código de idioma (ex: pt, en)")
    p_plan.add_argument("--voice", type=str, default="default", help="ID da voz Chatterbox")
    p_plan.add_argument("--exaggeration", type=float, default=0.5, help="Expressividade (0.25 a 2.0)")
    p_plan.add_argument("--no-subtitles", action="store_true", help="Desabilitar legendas automáticas")

    # List
    subparsers.add_parser("list", help="Lista todos os projetos salvos")

    # Voice
    p_voice = subparsers.add_parser("voice", help="Gera vozes Chatterbox para as cenas do projeto")
    p_voice.add_argument("--project-id", required=True, type=str, help="ID do projeto")

    # Search
    p_search = subparsers.add_parser("search", help="Pesquisa vídeos de stock para as cenas")
    p_search.add_argument("--project-id", required=True, type=str, help="ID do projeto")

    # Build
    p_build = subparsers.add_parser("build", help="Monta a timeline sincronizada no Drift")
    p_build.add_argument("--project-id", required=True, type=str, help="ID do projeto")

    args = parser.parse_args()
    if args.command == "status":
        check_system_status()
    elif args.command == "plan":
        cmd_create_plan(args)
    elif args.command == "list":
        cmd_list_projects(args)
    elif args.command == "voice":
        cmd_generate_voice(args)
    elif args.command == "search":
        cmd_search_media(args)
    elif args.command == "build":
        cmd_build_timeline(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()

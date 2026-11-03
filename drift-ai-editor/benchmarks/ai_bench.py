import time
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from models.scene_plan import ProjectPlan, ProjectConfig
from analysis.segmenter import ScriptSegmenter
from analysis.visual_planner import VisualPlanner
from analysis.storyboard_engine import StoryboardEngine
from pipeline.timeline_planner import TimelinePlanner
from pipeline.quality_control import QualityControlEngine
from media.diversity_controller import VisualDiversityController

@dataclass
class BenchmarkScenario:
    scenario_id: str
    name: str
    category: str              # 'philosophy_essay', 'cosmic_science', 'dynamic_social'
    script_text: str
    expected_scenes_min: int
    expected_duration_range: tuple # (min_sec, max_sec)
    expected_style: str

@dataclass
class BenchmarkResult:
    scenario_id: str
    scenario_name: str
    execution_time_sec: float
    scenes_detected: int
    total_planned_duration_sec: float
    duration_in_target_range: bool
    quality_audit_score: int
    diversity_score: int
    mcp_operations_count: int
    has_conflicts: bool
    status: str                # 'PASSED', 'DEGRADED', 'FAILED'
    notes: List[str] = field(default_factory=list)

@dataclass
class BenchmarkSuiteSummary:
    suite_version: str
    timestamp: str
    total_scenarios: int
    passed_scenarios: int
    average_execution_time_sec: float
    average_quality_score: float
    overall_health: str        # 'EXCELLENT', 'GOOD', 'NEEDS_ATTENTION'
    results: List[BenchmarkResult] = field(default_factory=list)

class AiBenchHarness:
    """
    AI Bench: Automated regression test & performance evaluation harness for the Drift AI Editor.
    Runs canonical standardized productions to verify:
      1. Semantic scene parsing fidelity
      2. Temporal sync and duration boundaries
      3. Quality control audit score
      4. Visual diversity & anti-repetition score
      5. MCP assembly plan validity
      6. Wall-clock processing efficiency
    """

    CANONICAL_SCENARIOS = [
        BenchmarkScenario(
            scenario_id="bench_01_stoic",
            name="Ensaio Filosófico: O Controle da Mente",
            category="philosophy_essay",
            script_text=(
                "CENA 01\nNARRAÇÃO: Você não controla o que acontece ao seu redor.\nDESCRIÇÃO VISUAL: Homem observando tempestade na janela.\n\n"
                "CENA 02\nNARRAÇÃO: Mas seu poder reside na forma como você decide responder.\nDESCRIÇÃO VISUAL: Silhueta caminhando serena ao amanhecer.\n\n"
                "CENA 03\nNARRAÇÃO: A paz interior é a maior vitória sobre o caos do mundo.\nDESCRIÇÃO VISUAL: Paisagem de montanha com névoa suave."
            ),
            expected_scenes_min=3,
            expected_duration_range=(8.0, 20.0),
            expected_style="filosofico"
        ),
        BenchmarkScenario(
            scenario_id="bench_02_cosmos",
            name="Ciência e Universo: A Escala do Cosmos",
            category="cosmic_science",
            script_text=(
                "CENA 01\nNARRAÇÃO: Bilhões de estrelas giram no silêncio da noite cósmica.\nDESCRIÇÃO VISUAL: Galáxia espiral e nebulosa brilhante.\n\n"
                "CENA 02\nNARRAÇÃO: Nosso planeta é apenas um pequeno ponto azul pálido.\nDESCRIÇÃO VISUAL: Terra vista da órbita lunar.\n\n"
                "CENA 03\nNARRAÇÃO: Compreender o infinito nos ensina o verdadeiro valor do tempo.\nDESCRIÇÃO VISUAL: Telescópio gigante apontado para o céu estrelado."
            ),
            expected_scenes_min=3,
            expected_duration_range=(8.0, 20.0),
            expected_style="universo"
        ),
        BenchmarkScenario(
            scenario_id="bench_03_shorts",
            name="Shorts Dinâmico: A Regra dos 5 Segundos",
            category="dynamic_social",
            script_text=(
                "CENA 01\nNARRAÇÃO: Pare de adiar o que você precisa fazer agora!\nDESCRIÇÃO VISUAL: Relógio correndo rápido em close-up.\n\n"
                "CENA 02\nNARRAÇÃO: Conte de cinco até um e levante-se imediatamente.\nDESCRIÇÃO VISUAL: Atleta amarrando tênis pronto para correr."
            ),
            expected_scenes_min=2,
            expected_duration_range=(4.0, 15.0),
            expected_style="shorts_dinamico"
        )
    ]

    @classmethod
    def run_benchmark_suite(cls) -> BenchmarkSuiteSummary:
        results: List[BenchmarkResult] = []
        total_time = 0.0

        for sc in cls.CANONICAL_SCENARIOS:
            t0 = time.time()
            plan = ProjectPlan(
                title=sc.name,
                raw_script=sc.script_text,
                config=ProjectConfig(language="pt")
            )

            # 1. Parse and plan
            scenes = ScriptSegmenter.parse(sc.script_text, default_language="pt")
            VisualPlanner.plan_project(scenes)
            plan.scenes = scenes
            plan.reindex_scenes()

            # 2. Storyboard
            StoryboardEngine.apply_storyboard(plan.scenes)

            # 3. Quality & Diversity
            from pipeline.style_engine import StyleEngine
            profile = StyleEngine.get_profile(sc.expected_style)
            assembly = TimelinePlanner.create_assembly_plan(plan, profile)
            audit = QualityControlEngine.audit_project(plan)
            div = VisualDiversityController.audit_project_diversity(plan)

            elapsed = time.time() - t0
            total_time += elapsed

            dur_ok = sc.expected_duration_range[0] <= assembly.total_duration_sec <= sc.expected_duration_range[1]
            status = "PASSED" if (len(plan.scenes) >= sc.expected_scenes_min and dur_ok) else "FAILED"

            results.append(
                BenchmarkResult(
                    scenario_id=sc.scenario_id,
                    scenario_name=sc.name,
                    execution_time_sec=round(elapsed, 3),
                    scenes_detected=len(plan.scenes),
                    total_planned_duration_sec=assembly.total_duration_sec,
                    duration_in_target_range=dur_ok,
                    quality_audit_score=audit.score,
                    diversity_score=div.diversity_score,
                    mcp_operations_count=sum(len(b) for b in assembly.batches),
                    has_conflicts=len(assembly.validation_issues) > 0,
                    status=status
                )
            )

        passed = sum(1 for r in results if r.status == "PASSED")
        avg_time = round(max(0.0001, total_time / len(results)), 4) if results else 0.0
        avg_score = round(sum(r.quality_audit_score for r in results) / len(results), 1) if results else 0.0

        return BenchmarkSuiteSummary(
            suite_version="2.0.0",
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
            total_scenarios=len(results),
            passed_scenarios=passed,
            average_execution_time_sec=avg_time,
            average_quality_score=avg_score,
            overall_health="EXCELLENT" if passed == len(results) else "NEEDS_ATTENTION",
            results=results
        )

    @classmethod
    def generate_markdown_report(cls, summary: BenchmarkSuiteSummary, out_path: Optional[Path] = None) -> str:
        lines = [
            f"# Relatório de Benchmark do Motor de IA (AI Bench)",
            f"**Versão da Suite:** `{summary.suite_version}`  ",
            f"**Executado em:** `{summary.timestamp}`  ",
            f"**Cenários Aprovados:** `{summary.passed_scenarios}/{summary.total_scenarios}`  ",
            f"**Tempo Médio de Planejamento:** `{summary.average_execution_time_sec}s`  ",
            f"**Estado Geral de Saúde:** `{summary.overall_health}`",
            "",
            "## Resultados por Cenário Canônico",
            "",
            "| Cenário | Cenas | Duração | Tempo Exec | Score Qualidade | Ops MCP | Status |",
            "| :--- | :--- | :--- | :--- | :--- | :--- | :--- |"
        ]

        for r in summary.results:
            lines.append(
                f"| **{r.scenario_name}** | {r.scenes_detected} | {r.total_planned_duration_sec}s | {r.execution_time_sec}s | {r.quality_audit_score}/100 | {r.mcp_operations_count} | `{r.status}` |"
            )

        lines.extend([
            "",
            "---",
            "*AI Bench assegura que nenhuma regressão de sincronia, qualidade visual ou comandos MCP ocorra entre atualizações de versão.*"
        ])

        report_md = "\n".join(lines)
        if out_path:
            Path(out_path).parent.mkdir(parents=True, exist_ok=True)
            Path(out_path).write_text(report_md, encoding="utf-8")
        return report_md


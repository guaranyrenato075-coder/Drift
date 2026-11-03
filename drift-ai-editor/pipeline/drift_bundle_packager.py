"""
DriftBundle Packager for CutWire Drift AI.
Compacts an entire production project (timeline JSON, cached stock media, narration audio,
color profiles, and metadata) into a self-contained portable `.driftbundle` (ZIP archive)
and extracts/restores bundles for seamless team handoff and cloud collaboration.
"""
import json
import os
import zipfile
from dataclasses import dataclass
from typing import List, Optional
from models.scene_plan import ProjectPlan

@dataclass
class BundleManifest:
    bundle_version: str
    project_id: str
    project_title: str
    total_scenes: int
    media_file_count: int
    created_at_utc: str

class DriftBundlePackager:
    """
    Exports and imports portable .driftbundle project packages.
    """

    BUNDLE_VERSION = "1.0.0"

    @classmethod
    def export_bundle(
        cls,
        plan: ProjectPlan,
        output_bundle_path: str,
        asset_files: Optional[List[str]] = None
    ) -> BundleManifest:
        os.makedirs(os.path.dirname(os.path.abspath(output_bundle_path)), exist_ok=True)
        asset_files = asset_files or []

        manifest_data = {
            "bundle_version": cls.BUNDLE_VERSION,
            "project_id": getattr(plan, "project_id", getattr(plan, "id", "proj_default")),
            "project_title": plan.title,
            "total_scenes": len(plan.scenes),
            "media_file_count": len(asset_files),
            "created_at_utc": str(plan.created_at)
        }

        with zipfile.ZipFile(output_bundle_path, "w", zipfile.ZIP_DEFLATED) as zf:
            # Write project manifest
            zf.writestr("manifest.json", json.dumps(manifest_data, indent=2))
            # Write project JSON structure
            zf.writestr("project_timeline.json", json.dumps(plan.to_dict(), indent=2))

            # Write assets if existing on disk
            for asset in asset_files:
                if os.path.isfile(asset):
                    arcname = os.path.join("assets", os.path.basename(asset))
                    zf.write(asset, arcname=arcname)

        return BundleManifest(**manifest_data)

    @classmethod
    def inspect_bundle(cls, bundle_path: str) -> BundleManifest:
        if not os.path.isfile(bundle_path):
            raise FileNotFoundError(f"Bundle not found: {bundle_path}")

        with zipfile.ZipFile(bundle_path, "r") as zf:
            if "manifest.json" not in zf.namelist():
                raise ValueError("Invalid .driftbundle: missing manifest.json")
            data = json.loads(zf.read("manifest.json").decode("utf-8"))
            return BundleManifest(**data)

    @classmethod
    def extract_bundle(cls, bundle_path: str, destination_dir: str) -> ProjectPlan:
        if not os.path.isfile(bundle_path):
            raise FileNotFoundError(f"Bundle not found: {bundle_path}")

        os.makedirs(destination_dir, exist_ok=True)
        with zipfile.ZipFile(bundle_path, "r") as zf:
            zf.extractall(destination_dir)
            timeline_path = os.path.join(destination_dir, "project_timeline.json")
            with open(timeline_path, "r", encoding="utf-8") as f:
                plan_data = json.load(f)
            return ProjectPlan.from_dict(plan_data)

import re
import xml.etree.ElementTree as ET
from pathlib import Path

import yaml


ROOT = Path(__file__).parents[1]


def test_readme_local_images_exist_and_have_alt_text():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    images = re.findall(r'<img src="(\./[^\"]+)"[^>]*alt="([^\"]+)"', readme)
    assert {source for source, _ in images} == {
        "./portrait-ascii.svg",
        "./info-card.svg",
        "./contrib-heatmap.svg",
    }
    assert all(alt.strip() for _, alt in images)
    for source, _ in images:
        assert (ROOT / source.removeprefix("./")).is_file()


def test_generated_svgs_are_valid_xml():
    for name in ("portrait-ascii.svg", "info-card.svg", "contrib-heatmap.svg"):
        ET.parse(ROOT / name)


def test_readme_contains_only_verified_identity_and_profile_link():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "Open Source Contributor · Kubernetes · Go" in readme
    assert "Open Source Developer" not in readme
    assert "https://github.com/reckless-sherixx" in readme
    assert "linkedin.com" not in readme.lower()
    assert "instagram.com" not in readme.lower()


def test_workflow_refreshes_only_dynamic_assets():
    workflow_path = ROOT / ".github" / "workflows" / "update-profile-art.yml"
    workflow = yaml.safe_load(workflow_path.read_text(encoding="utf-8"))

    assert workflow["permissions"] == {"contents": "write"}
    assert set(workflow["on"]) == {"schedule", "workflow_dispatch"}
    assert workflow["concurrency"]["cancel-in-progress"] is True

    steps = workflow["jobs"]["heatmap"]["steps"]
    commands = [step["run"] for step in steps if "run" in step]
    assert commands == [
        "pip install -r scripts/requirements.txt",
        (
            "python scripts/fetch_contributions.py --username reckless-sherixx "
            "--output data/contributions.json"
        ),
        (
            "python scripts/render_heatmap_svg.py --input data/contributions.json "
            "--output contrib-heatmap.svg"
        ),
    ]

    commit_step = next(
        step for step in steps if step.get("uses") == "stefanzweifel/git-auto-commit-action@v5"
    )
    assert commit_step["with"]["file_pattern"] == (
        "data/contributions.json contrib-heatmap.svg"
    )

# Reckless Sherixx Profile README Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a reproducible animated terminal-style GitHub profile README for `reckless-sherixx` from the supplied portrait and public contribution activity.

**Architecture:** Small Python generators own one artifact each: contribution JSON, heatmap SVG, information-card SVG, and portrait SVG. `README.md` only composes committed assets, while one scheduled GitHub workflow refreshes the contribution JSON and heatmap without touching static portrait assets.

**Tech Stack:** Python 3.11, Pillow, NumPy, OpenCV, rembg CPU, Requests, Beautiful Soup, pytest, SVG/XML, GitHub-flavored Markdown, GitHub Actions.

## Global Constraints

- Name: Vidyansh Singh.
- GitHub username: `reckless-sherixx`.
- Title: Open Source Developer · Kubernetes · Go.
- Focus: Cloud Native and Distributed Systems.
- Core stack: Go, Kubernetes, TypeScript, and Docker.
- Do not invent social accounts, employment, achievements, or private statistics.
- Use self-contained SVG animation; no JavaScript or externally hosted animation services.
- Portrait and information-card animations play once and freeze.
- Keep portrait and card static; refresh only contribution data and the heatmap daily.
- Preserve a project-local copy of the supplied portrait as `assets/source-portrait.jpg`.
- Stop on contribution fetch or parse failure without overwriting the last valid JSON or SVG.
- Publication is blocked until authenticated write access to `reckless-sherixx` is available.

## File Structure

- `README.md`: GitHub profile composition and verified profile link.
- `assets/source-portrait.jpg`: reproducible source copy of the supplied portrait.
- `assets/portrait-prepped.png`: generated high-contrast grayscale portrait.
- `portrait-ascii.svg`: generated animated ASCII portrait.
- `info-card.svg`: generated animated neofetch-style identity card.
- `contrib-heatmap.svg`: generated animated contribution calendar.
- `data/contributions.json`: normalized public contribution days and derived statistics.
- `scripts/fetch_contributions.py`: fetch, parse, validate, compute statistics, and atomically write JSON.
- `scripts/render_heatmap_svg.py`: convert normalized contribution JSON to animated SVG.
- `scripts/make_info_card.py`: render the approved identity data as animated SVG.
- `scripts/prep_photo.py`: remove the background, apply CLAHE, and produce grayscale portrait input.
- `scripts/make_ascii_svg.py`: sample grayscale pixels into ASCII rows and render one-shot row wipes.
- `scripts/requirements.txt`: lightweight daily-workflow dependencies.
- `scripts/requirements-portrait.txt`: one-time portrait dependencies.
- `requirements-dev.txt`: complete local development and test dependencies.
- `tests/fixtures/contributions.html`: small deterministic contribution-calendar fragment.
- `tests/test_fetch_contributions.py`: parser, statistic, and atomic-write regression coverage.
- `tests/test_render_heatmap_svg.py`: grid, color-level, escaping, and SVG contract coverage.
- `tests/test_make_info_card.py`: approved copy and one-shot animation coverage.
- `tests/test_portrait_pipeline.py`: portrait sampling, preprocessing, SVG structure, and static-preview coverage.
- `tests/test_profile_contract.py`: README paths, XML validity, workflow scope, and verified-copy checks.
- `.github/workflows/update-profile-art.yml`: scheduled and manual heatmap refresh.

---

### Task 1: Contribution Data Pipeline

**Files:**
- Create: `scripts/requirements.txt`
- Create: `requirements-dev.txt`
- Create: `tests/fixtures/contributions.html`
- Create: `tests/test_fetch_contributions.py`
- Create: `scripts/fetch_contributions.py`
- Create: `data/.gitkeep`

**Interfaces:**
- Consumes: public HTML from `https://github.com/users/{username}/contributions`.
- Produces: `parse_days(html_text: str) -> list[dict[str, str | int]]`.
- Produces: `build_data(username: str, days: list[dict[str, str | int]], generated_at: datetime.datetime | None = None) -> dict[str, object]`.
- Produces: `write_json_atomic(data: dict[str, object], output_path: pathlib.Path) -> None`.
- Produces: CLI defaults `--username reckless-sherixx --output data/contributions.json`.

- [ ] **Step 1: Pin the lightweight and development dependencies**

Create `scripts/requirements.txt`:

```text
requests==2.34.2
beautifulsoup4==4.15.0
```

Create `requirements-dev.txt`:

```text
-r scripts/requirements.txt
pytest==9.1.1
```

- [ ] **Step 2: Add a realistic deterministic HTML fixture**

Create `tests/fixtures/contributions.html`:

```html
<table>
  <td id="day-1" class="ContributionCalendar-day" data-date="2026-08-10" data-level="0"></td>
  <tool-tip for="day-1">No contributions on August 10th.</tool-tip>
  <td id="day-2" class="ContributionCalendar-day" data-date="2026-08-11" data-level="1"></td>
  <tool-tip for="day-2">2 contributions on August 11th.</tool-tip>
  <td id="day-3" class="ContributionCalendar-day" data-date="2026-08-12" data-level="2"></td>
  <tool-tip for="day-3">7 contributions on August 12th.</tool-tip>
  <td id="day-4" class="ContributionCalendar-day" data-date="2026-08-13" data-level="0"></td>
  <tool-tip for="day-4">No contributions on August 13th.</tool-tip>
</table>
```

- [ ] **Step 3: Write failing parser, statistic, and preservation tests**

Create `tests/test_fetch_contributions.py`:

```python
import datetime
import json
from pathlib import Path

import pytest

from scripts.fetch_contributions import build_data, parse_days, write_json_atomic


FIXTURE = Path(__file__).parent / "fixtures" / "contributions.html"


def test_parse_days_reads_dates_and_counts():
    assert parse_days(FIXTURE.read_text(encoding="utf-8")) == [
        {"date": "2026-08-10", "count": 0},
        {"date": "2026-08-11", "count": 2},
        {"date": "2026-08-12", "count": 7},
        {"date": "2026-08-13", "count": 0},
    ]


def test_parse_days_rejects_missing_calendar():
    with pytest.raises(ValueError, match="no contribution calendar cells"):
        parse_days("<html></html>")


def test_build_data_computes_factual_summary():
    data = build_data(
        "reckless-sherixx",
        parse_days(FIXTURE.read_text(encoding="utf-8")),
        datetime.datetime(2026, 8, 13, tzinfo=datetime.timezone.utc),
    )
    assert data["total_contributions"] == 9
    assert data["active_days"] == 2
    assert data["current_streak"]["length"] == 2
    assert data["longest_streak"]["length"] == 2
    assert data["best_day"] == {"date": "2026-08-12", "count": 7}


def test_atomic_write_replaces_valid_json(tmp_path):
    output = tmp_path / "contributions.json"
    output.write_text('{"old": true}', encoding="utf-8")
    write_json_atomic({"username": "reckless-sherixx"}, output)
    assert json.loads(output.read_text(encoding="utf-8")) == {
        "username": "reckless-sherixx"
    }
```

- [ ] **Step 4: Run the focused test and confirm the missing-module failure**

Run: `python -m pytest tests/test_fetch_contributions.py -q`

Expected: collection fails because `scripts.fetch_contributions` does not exist.

- [ ] **Step 5: Implement fetching, parsing, statistics, and atomic output**

Create `scripts/fetch_contributions.py` with these behaviors:

```python
def parse_days(html_text: str) -> list[dict[str, str | int]]:
    soup = BeautifulSoup(html_text, "html.parser")
    cells = soup.select("td.ContributionCalendar-day[data-date]")
    if not cells:
        raise ValueError("no contribution calendar cells found")
    days = []
    for cell in cells:
        tooltip = soup.find("tool-tip", attrs={"for": cell.get("id")})
        text = tooltip.get_text(" ", strip=True) if tooltip else ""
        match = re.match(r"([0-9,]+) contributions?", text, re.IGNORECASE)
        count = int(match.group(1).replace(",", "")) if match else 0
        days.append({"date": cell["data-date"], "count": count})
    return sorted(days, key=lambda day: str(day["date"]))


def write_json_atomic(data: dict[str, object], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = output_path.with_suffix(output_path.suffix + ".tmp")
    temporary.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    temporary.replace(output_path)
```

`build_data` must validate that days are nonempty and dates are unique, then derive `range`, `total_contributions`, `active_days`, `avg_per_active_day`, `current_streak`, `longest_streak`, `best_day`, monthly totals, and the raw sorted days. `main()` must call `requests.get(..., timeout=30)`, call `raise_for_status()`, build data only after successful parsing, and atomically replace the output.

- [ ] **Step 6: Run the tests and fetch real public data**

Run: `python -m pytest tests/test_fetch_contributions.py -q`

Expected: 4 tests pass.

Run: `python scripts/fetch_contributions.py --username reckless-sherixx --output data/contributions.json`

Expected: the command reports a nonempty date range and writes valid JSON without authentication.

- [ ] **Step 7: Commit the data pipeline**

```powershell
git add scripts/requirements.txt requirements-dev.txt scripts/fetch_contributions.py tests/fixtures/contributions.html tests/test_fetch_contributions.py data/.gitkeep data/contributions.json
git commit -m "feat: add public contribution data pipeline"
```

### Task 2: Animated Contribution Heatmap

**Files:**
- Create: `tests/test_render_heatmap_svg.py`
- Create: `scripts/render_heatmap_svg.py`
- Create: `contrib-heatmap.svg`

**Interfaces:**
- Consumes: Task 1 `data/contributions.json` schema.
- Produces: `level_for(count: int) -> int` in the inclusive range 0–5.
- Produces: `build_grid(days: list[dict[str, str | int]]) -> list[list[dict[str, str | int] | None]]`.
- Produces: `render_heatmap(data: dict[str, object], static: bool = False) -> str`.

- [ ] **Step 1: Write failing grid and SVG tests**

Create `tests/test_render_heatmap_svg.py`:

```python
import datetime
import xml.etree.ElementTree as ET

from scripts.fetch_contributions import build_data
from scripts.render_heatmap_svg import build_grid, level_for, render_heatmap


DAYS = [
    {"date": "2026-08-09", "count": 0},
    {"date": "2026-08-10", "count": 1},
    {"date": "2026-08-11", "count": 6},
]


def test_level_for_has_six_bounded_levels():
    assert [level_for(value) for value in (0, 1, 6, 16, 31, 51)] == [0, 1, 2, 3, 4, 5]


def test_build_grid_starts_on_sunday():
    grid = build_grid(DAYS)
    assert grid[0][0]["date"] == "2026-08-09"
    assert grid[0][2]["count"] == 6


def test_render_heatmap_is_valid_accessible_svg():
    data = build_data(
        "reckless-sherixx",
        DAYS,
        datetime.datetime(2026, 8, 13, tzinfo=datetime.timezone.utc),
    )
    svg = render_heatmap(data)
    root = ET.fromstring(svg)
    assert root.tag.endswith("svg")
    assert "reckless-sherixx@github" in svg
    assert "7 contributions in the last year" in svg
    assert "@keyframes reveal" in svg
    assert "repeatCount=\"indefinite\"" not in svg
    assert "2026-08-11: 6 contributions" in svg


def test_static_render_contains_no_animation():
    data = build_data("reckless-sherixx", DAYS)
    assert "@keyframes" not in render_heatmap(data, static=True)
```

- [ ] **Step 2: Run the focused test and confirm the missing-module failure**

Run: `python -m pytest tests/test_render_heatmap_svg.py -q`

Expected: collection fails because `scripts.render_heatmap_svg` does not exist.

- [ ] **Step 3: Implement the calendar renderer**

Create `scripts/render_heatmap_svg.py` with:

```python
PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]


def level_for(count: int) -> int:
    if count == 0:
        return 0
    if count <= 5:
        return 1
    if count <= 15:
        return 2
    if count <= 30:
        return 3
    if count <= 50:
        return 4
    return 5
```

`build_grid` must align Sunday at row 0, pad missing dates with `None`, and emit complete seven-row columns. `render_heatmap` must XML-escape dynamic labels, draw a 53-week-style grid with rounded cells, month and weekday labels, a Less-to-More legend, and factual totals/streaks from the JSON. Animated mode must use one-shot CSS `@keyframes reveal` with diagonal per-cell delays and `animation-fill-mode: both`; static mode must omit animation CSS and opacity hiding. The CLI must accept `--input`, `--output`, and `--static`.

- [ ] **Step 4: Run the tests and generate both render modes**

Run: `python -m pytest tests/test_render_heatmap_svg.py -q`

Expected: 4 tests pass.

Run: `python scripts/render_heatmap_svg.py --input data/contributions.json --output contrib-heatmap.svg`

Run: `python scripts/render_heatmap_svg.py --input data/contributions.json --output tmp/heatmap-static.svg --static`

Expected: both files parse with `xml.etree.ElementTree`, and the static file contains no keyframes.

- [ ] **Step 5: Commit the heatmap**

```powershell
git add scripts/render_heatmap_svg.py tests/test_render_heatmap_svg.py contrib-heatmap.svg
git commit -m "feat: render animated contribution heatmap"
```

### Task 3: Animated Identity Card

**Files:**
- Create: `tests/test_make_info_card.py`
- Create: `scripts/make_info_card.py`
- Create: `info-card.svg`

**Interfaces:**
- Consumes: approved identity constants from the design specification.
- Produces: `render_info_card(static: bool = False) -> str`.
- Produces: CLI `--output info-card.svg` and optional `--static`.

- [ ] **Step 1: Write failing identity-card tests**

Create `tests/test_make_info_card.py`:

```python
import xml.etree.ElementTree as ET

from scripts.make_info_card import render_info_card


def test_card_contains_only_approved_identity_copy():
    svg = render_info_card()
    ET.fromstring(svg)
    for text in (
        "Vidyansh Singh",
        "Open Source Developer · Kubernetes · Go",
        "Cloud Native and Distributed Systems",
        "Go · Kubernetes · TypeScript · Docker",
    ):
        assert text in svg
    assert "employed at" not in svg.lower()


def test_card_animation_is_one_shot():
    svg = render_info_card()
    assert "@keyframes lineIn" in svg
    assert "infinite" not in svg


def test_static_card_has_no_animation():
    assert "@keyframes" not in render_info_card(static=True)
```

- [ ] **Step 2: Run the focused test and confirm the missing-module failure**

Run: `python -m pytest tests/test_make_info_card.py -q`

Expected: collection fails because `scripts.make_info_card` does not exist.

- [ ] **Step 3: Implement the neofetch-style SVG generator**

Create `scripts/make_info_card.py` around this immutable content:

```python
ROWS = (
    ("Name", "Vidyansh Singh"),
    ("Role", "Open Source Developer · Kubernetes · Go"),
    ("Focus", "Cloud Native and Distributed Systems"),
    ("Stack", "Go · Kubernetes · TypeScript · Docker"),
    ("GitHub", "github.com/reckless-sherixx"),
)
```

The SVG must use a 980×754 view box, a dark terminal panel, traffic-light title dots, the title `reckless-sherixx@github: ~$ neofetch`, and XML-escaped key/value rows. Animated rows use staggered `lineIn` opacity/translate animations that run once and retain the final state. Static mode emits visible rows with no animation stylesheet.

- [ ] **Step 4: Run tests and generate animated and static cards**

Run: `python -m pytest tests/test_make_info_card.py -q`

Expected: 3 tests pass.

Run: `python scripts/make_info_card.py --output info-card.svg`

Run: `python scripts/make_info_card.py --output tmp/info-card-static.svg --static`

Expected: both outputs parse as XML and contain all five approved rows.

- [ ] **Step 5: Commit the identity card**

```powershell
git add scripts/make_info_card.py tests/test_make_info_card.py info-card.svg
git commit -m "feat: add animated identity card"
```

### Task 4: Portrait-to-ASCII Pipeline

**Files:**
- Create: `scripts/requirements-portrait.txt`
- Create: `assets/source-portrait.jpg`
- Create: `tests/test_portrait_pipeline.py`
- Create: `scripts/prep_photo.py`
- Create: `scripts/make_ascii_svg.py`
- Create: `assets/portrait-prepped.png`
- Create: `portrait-ascii.svg`

**Interfaces:**
- Consumes: `assets/source-portrait.jpg` copied byte-for-byte from the supplied JPG.
- Produces: `prepare_portrait(input_path: pathlib.Path, output_path: pathlib.Path, remove_background: collections.abc.Callable | None = None) -> tuple[int, int]`.
- Produces: `image_to_ascii_rows(image: PIL.Image.Image, cols: int = 100, rows: int = 53) -> list[str]`.
- Produces: `render_ascii_svg(rows: list[str], static: bool = False) -> str`.

- [ ] **Step 1: Pin the one-time portrait dependencies**

Create `scripts/requirements-portrait.txt`:

```text
Pillow==12.3.0
numpy==2.5.2
opencv-python-headless==5.0.0.93
rembg[cpu]==2.0.78
```

Append to `requirements-dev.txt`:

```text
-r scripts/requirements-portrait.txt
```

- [ ] **Step 2: Copy the supplied portrait into the repository**

Run:

```powershell
New-Item -ItemType Directory -Force -Path 'assets'
Copy-Item -LiteralPath 'E:\COMP-DOWNLOADS\Screenshot_2026-04-27-22-44-03-12_6012fa4d4ddec268fc5c7112cbb265e7.jpg' -Destination 'assets\source-portrait.jpg'
```

Expected: `assets/source-portrait.jpg` is a readable 915×2048 JPEG and the external original remains unchanged.

- [ ] **Step 3: Write failing sampling and SVG tests**

Create `tests/test_portrait_pipeline.py`:

```python
import xml.etree.ElementTree as ET

from PIL import Image

from scripts.make_ascii_svg import image_to_ascii_rows, render_ascii_svg
from scripts.prep_photo import prepare_portrait


def test_image_to_ascii_rows_maps_white_to_spaces_and_black_to_dense_glyphs():
    image = Image.new("L", (2, 1), 255)
    image.putpixel((1, 0), 0)
    rows = image_to_ascii_rows(image, cols=2, rows=1)
    assert rows[0][0] == " "
    assert rows[0][1] == "@"

def test_prepare_portrait_outputs_grayscale_with_white_background(tmp_path):
    source = tmp_path / "source.png"
    output = tmp_path / "prepared.png"
    Image.new("RGB", (8, 8), "gray").save(source)

    def fake_remove(image):
        cutout = Image.new("RGBA", image.size, (0, 0, 0, 0))
        cutout.paste((64, 64, 64, 255), (2, 2, 6, 6))
        return cutout

    assert prepare_portrait(source, output, fake_remove) == (8, 8)
    prepared = Image.open(output)
    assert prepared.mode == "L"
    assert prepared.getpixel((0, 0)) == 255
    assert prepared.getpixel((4, 4)) < 255



def test_render_ascii_svg_is_valid_and_identified():
    svg = render_ascii_svg([" @", "@@"])
    ET.fromstring(svg)
    assert "reckless-sherixx@github" in svg
    assert "Vidyansh Singh" in svg
    assert "repeatCount=\"indefinite\"" not in svg
    assert "clipPath" in svg


def test_static_portrait_has_no_smil_animation():
    assert "<animate" not in render_ascii_svg(["@@"], static=True)
```

- [ ] **Step 4: Run the focused tests and confirm the missing-module failure**

Run: `python -m pytest tests/test_portrait_pipeline.py -q`

Expected: collection fails because `scripts.make_ascii_svg` does not exist.

- [ ] **Step 5: Implement deterministic preparation and ASCII rendering**

Create `scripts/prep_photo.py` so `prepare_portrait` accepts an optional injected background-removal callable for deterministic tests and lazily imports `rembg.remove` when the callable is `None`. It removes the background, converts the RGB subject to grayscale, applies OpenCV CLAHE with `clipLimit=2.6` and `tileGridSize=(8, 8)`, applies a small global lift, feathers the alpha mask by one pixel, composites onto white, saves an `L`-mode PNG, and returns the output dimensions. Its CLI accepts input and output paths.

Create `scripts/make_ascii_svg.py` with:

```python
RAMP = " .`:-=+*cs#%@"


def image_to_ascii_rows(image: Image.Image, cols: int = 100, rows: int = 53) -> list[str]:
    sampled = image.convert("L").resize((cols, rows), Image.Resampling.LANCZOS)
    result = []
    for y in range(rows):
        line = []
        for x in range(cols):
            luminance = (sampled.getpixel((x, y)) / 255.0) ** 1.18
            if luminance >= 0.80:
                line.append(" ")
            else:
                index = round((1.0 - luminance) * (len(RAMP) - 1))
                line.append(RAMP[max(0, min(index, len(RAMP) - 1))])
        result.append("".join(line))
    return result
```

`render_ascii_svg` must use the same dark terminal framing as the card, title `reckless-sherixx@github: ~$ ./portrait.sh`, one monochrome text element per row, staggered left-to-right clip-path wipes, a nonlooping cursor per active row, and a final status line reading `whoami Vidyansh Singh`. Static mode emits the complete portrait without SMIL elements. The CLI accepts input, output, `--cols`, `--rows`, and `--static`.

- [ ] **Step 6: Run tests and generate the real portrait assets**

Run: `python -m pytest tests/test_portrait_pipeline.py -q`

Expected: 4 tests pass.

Run: `python scripts/prep_photo.py assets/source-portrait.jpg assets/portrait-prepped.png`

Run: `python scripts/make_ascii_svg.py assets/portrait-prepped.png portrait-ascii.svg`

Run: `python scripts/make_ascii_svg.py assets/portrait-prepped.png tmp/portrait-static.svg --static`

Expected: the prepped PNG has white corners and visible facial contrast; both SVGs parse as XML; the static SVG contains no `<animate>` element.

- [ ] **Step 7: Commit the portrait pipeline and generated assets**

```powershell
git add scripts/requirements-portrait.txt requirements-dev.txt assets/source-portrait.jpg assets/portrait-prepped.png scripts/prep_photo.py scripts/make_ascii_svg.py tests/test_portrait_pipeline.py portrait-ascii.svg
git commit -m "feat: generate animated ASCII portrait"
```

### Task 5: Profile Composition, Automation, and Full Verification

**Files:**
- Create: `README.md`
- Create: `.github/workflows/update-profile-art.yml`
- Create: `tests/test_profile_contract.py`
- Modify: generated SVG and JSON files only when current data differs.

**Interfaces:**
- Consumes: `portrait-ascii.svg`, `info-card.svg`, `contrib-heatmap.svg`, and Task 1–4 scripts.
- Produces: a GitHub profile README whose local asset paths all exist.
- Produces: a daily workflow that updates only `data/contributions.json` and `contrib-heatmap.svg`.

- [ ] **Step 1: Write failing repository-contract tests**

Create `tests/test_profile_contract.py`:

```python
import re
import xml.etree.ElementTree as ET
from pathlib import Path


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
    assert "Open Source Developer · Kubernetes · Go" in readme
    assert "https://github.com/reckless-sherixx" in readme
    assert "linkedin.com" not in readme.lower()
    assert "instagram.com" not in readme.lower()


def test_workflow_refreshes_only_dynamic_assets():
    workflow = (ROOT / ".github/workflows/update-profile-art.yml").read_text(encoding="utf-8")
    assert "permissions:\n  contents: write" in workflow
    assert "workflow_dispatch" in workflow
    assert "schedule:" in workflow
    assert "scripts/fetch_contributions.py" in workflow
    assert "scripts/render_heatmap_svg.py" in workflow
    assert "data/contributions.json contrib-heatmap.svg" in workflow
    assert "portrait-ascii.svg" not in workflow
    assert "info-card.svg" not in workflow
```

- [ ] **Step 2: Run the contract tests and confirm missing README/workflow failures**

Run: `python -m pytest tests/test_profile_contract.py -q`

Expected: failures report missing `README.md` and `.github/workflows/update-profile-art.yml`.

- [ ] **Step 3: Compose the README**

Create `README.md` with this structure:

```html
<div align="center">

<h3><code>vidyansh@github ~ $ whoami</code></h3>

<table>
<tr>
<td valign="top"><img src="./portrait-ascii.svg" width="370" alt="Animated ASCII portrait of Vidyansh Singh" /></td>
<td valign="top"><img src="./info-card.svg" width="490" alt="Terminal information card for Vidyansh Singh" /></td>
</tr>
</table>

<br><br>

<h3><code>vidyansh@github ~ $ ./contributions.sh</code></h3>

<img src="./contrib-heatmap.svg" width="860" alt="Public GitHub contribution heatmap for reckless-sherixx" />

<br><br>

<h3><code>vidyansh@github ~ $ ./connect.sh</code></h3>

<p><b>Open Source Developer · Kubernetes · Go</b></p>

<a href="https://github.com/reckless-sherixx">github.com/reckless-sherixx</a>

</div>
```

- [ ] **Step 4: Add the safe daily refresh workflow**

Create `.github/workflows/update-profile-art.yml`:

```yaml
name: Update profile art

"on":
  schedule:
    - cron: "17 6 * * *"
  workflow_dispatch: {}

permissions:
  contents: write

concurrency:
  group: update-profile-art
  cancel-in-progress: true

jobs:
  heatmap:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
          cache: pip
          cache-dependency-path: scripts/requirements.txt
      - run: pip install -r scripts/requirements.txt
      - run: python scripts/fetch_contributions.py --username reckless-sherixx --output data/contributions.json
      - run: python scripts/render_heatmap_svg.py --input data/contributions.json --output contrib-heatmap.svg
      - uses: stefanzweifel/git-auto-commit-action@v5
        with:
          commit_message: "chore: refresh contribution graph [skip ci]"
          file_pattern: "data/contributions.json contrib-heatmap.svg"
```

The workflow intentionally has no `push` trigger, so its own auto-commit cannot loop.

- [ ] **Step 5: Run the complete automated verification**

Run: `python -m pytest -q`

Expected: all Task 1–5 tests pass.

Run:

```powershell
python scripts/fetch_contributions.py --username reckless-sherixx --output data/contributions.json
python scripts/render_heatmap_svg.py --input data/contributions.json --output contrib-heatmap.svg
python scripts/make_info_card.py --output info-card.svg
python scripts/prep_photo.py assets/source-portrait.jpg assets/portrait-prepped.png
python scripts/make_ascii_svg.py assets/portrait-prepped.png portrait-ascii.svg
python -c "import xml.etree.ElementTree as ET; [ET.parse(path) for path in ('portrait-ascii.svg','info-card.svg','contrib-heatmap.svg')]"
```

Expected: every generator exits successfully and all three SVGs parse as XML.

- [ ] **Step 6: Render static visual previews and inspect them**

Run:

```powershell
New-Item -ItemType Directory -Force -Path 'tmp\previews'
python scripts/make_ascii_svg.py assets/portrait-prepped.png tmp/previews/portrait.svg --static
python scripts/make_info_card.py --output tmp/previews/info-card.svg --static
python scripts/render_heatmap_svg.py --input data/contributions.json --output tmp/previews/heatmap.svg --static
```

Inspect all three workspace SVGs and verify: no clipping, readable text, recognizable face, aligned terminal framing, visible contribution intensity, no broken glyphs, and sensible whitespace. If an issue appears, change one generator parameter, regenerate, and rerun its focused tests before continuing.

- [ ] **Step 7: Check repository cleanliness and commit the profile**

Run: `git diff --check`

Expected: no whitespace errors.

Run: `git status --short`

Expected: only Task 5 files and refreshed generated assets are listed.

```powershell
git add README.md .github/workflows/update-profile-art.yml tests/test_profile_contract.py data/contributions.json contrib-heatmap.svg info-card.svg portrait-ascii.svg assets/portrait-prepped.png
git commit -m "feat: build animated GitHub profile README"
```

- [ ] **Step 8: Publish only after account authorization is corrected**

Verify the authenticated GitHub identity is `reckless-sherixx`, create the public repository `reckless-sherixx/reckless-sherixx` if it still does not exist, rename the local branch to `main`, add the repository as `origin`, push, manually run `Update profile art`, and confirm the workflow commits only the JSON and heatmap when data changes.

Do not run this step while the connected identity is `vikram-iitm`; stop and request the correct GitHub connection instead.

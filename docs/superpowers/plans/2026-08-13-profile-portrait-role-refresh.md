# Profile Portrait and Role Refresh Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the profile's portrait with the supplied `377437.jpg` artwork and change the public role line to `Open Source Contributor · Kubernetes · Go`.

**Architecture:** Preserve the existing generation pipeline and README composition. The supplied JPEG becomes the committed source asset, the existing preparation and ASCII generators rebuild the portrait artifacts, and the role constant remains owned by the information-card generator with matching README and contract-test copy.

**Tech Stack:** Python 3, Pillow, OpenCV, rembg, SVG, pytest, GitHub Markdown

## Global Constraints

- Preserve the current two-column terminal layout, dimensions, animation style, purple palette, contribution heatmap, and responsive behavior.
- Use the exact role line `Open Source Contributor · Kubernetes · Go`.
- Copy `E:/COMP-DOWNLOADS/377437.jpg` without modifying the external original.
- Keep the username, name, GitHub URL, skills, contribution data, and command-style headings unchanged.
- Update the existing draft PR from `agent/animated-profile-readme`.

---

### Task 1: Refresh the public role copy

**Files:**
- Modify: `tests/test_make_info_card.py`
- Modify: `tests/test_profile_contract.py`
- Modify: `scripts/make_info_card.py`
- Modify: `README.md`
- Regenerate: `info-card.svg`

**Interfaces:**
- Consumes: `render_info_card(static: bool = False) -> str` from `scripts.make_info_card`.
- Produces: the exact public role line in the README and generated identity-card SVG.

- [ ] **Step 1: Write failing role-copy assertions**

Change both role expectations to `Open Source Contributor · Kubernetes · Go`. Add assertions that `Open Source Developer` is absent from `render_info_card()` and `README.md`.

- [ ] **Step 2: Run focused tests and verify the expected failure**

Run: `.venv/Scripts/python.exe -m pytest tests/test_make_info_card.py::test_card_contains_only_approved_identity_copy tests/test_profile_contract.py::test_readme_contains_only_verified_identity_and_profile_link -q`

Expected: FAIL because the current generator and README still contain `Open Source Developer · Kubernetes · Go`.

- [ ] **Step 3: Implement the minimal copy change**

In `scripts/make_info_card.py`, change the `Role` row to:

```python
("Role", "Open Source Contributor · Kubernetes · Go"),
```

Change the SVG description to begin with `Open Source Contributor`. Change the matching README line to:

```html
<p><b>Open Source Contributor · Kubernetes · Go</b></p>
```

- [ ] **Step 4: Regenerate and verify the card**

Run: `.venv/Scripts/python.exe scripts/make_info_card.py --output info-card.svg`

Run the focused tests from Step 2 again.

Expected: both tests PASS, and `info-card.svg` contains `Open Source Contributor` but not `Open Source Developer`.

- [ ] **Step 5: Commit the role refresh**

```powershell
git add README.md scripts/make_info_card.py tests/test_make_info_card.py tests/test_profile_contract.py info-card.svg
git commit -m "feat: describe open source contribution role"
```

### Task 2: Replace and regenerate the portrait artwork

**Files:**
- Replace: `assets/source-portrait.jpg`
- Regenerate: `assets/portrait-prepped.png`
- Regenerate: `portrait-ascii.svg`

**Interfaces:**
- Consumes: `prepare_portrait(input_path, output_path, remove_background=None) -> tuple[int, int]` and `image_to_ascii_rows(image, cols=100, rows=53) -> list[str]`.
- Produces: a project-local source JPEG plus the prepared grayscale PNG and animated ASCII SVG referenced by `README.md`.

- [ ] **Step 1: Verify the supplied source before replacement**

Read `E:/COMP-DOWNLOADS/377437.jpg` with Pillow and record its format, dimensions, and SHA-256 digest. Confirm it is a readable JPEG before writing the project asset.

- [ ] **Step 2: Replace the source asset without changing the external file**

Copy `E:/COMP-DOWNLOADS/377437.jpg` to `assets/source-portrait.jpg`. Compare SHA-256 digests and require an exact match.

- [ ] **Step 3: Regenerate the prepared and animated artwork**

```powershell
.venv/Scripts/python.exe scripts/prep_photo.py assets/source-portrait.jpg assets/portrait-prepped.png
.venv/Scripts/python.exe scripts/make_ascii_svg.py assets/portrait-prepped.png portrait-ascii.svg
```

Expected: both commands exit successfully, the PNG is grayscale and readable, and the SVG is valid XML containing the existing one-shot animation.

- [ ] **Step 4: Run focused portrait validation**

Run: `.venv/Scripts/python.exe -m pytest tests/test_portrait_pipeline.py tests/test_profile_contract.py::test_generated_svgs_are_valid_xml -q`

Expected: all focused tests PASS.

- [ ] **Step 5: Visually inspect the refreshed profile**

Render the README preview and inspect the new ASCII portrait beside the identity card. Confirm the image remains recognizable, fits the existing frame, and does not change layout dimensions.

- [ ] **Step 6: Commit the portrait refresh**

```powershell
git add assets/source-portrait.jpg assets/portrait-prepped.png portrait-ascii.svg
git commit -m "feat: refresh animated profile portrait"
```

### Task 3: Final verification and PR update

**Files:**
- Verify: all committed project files
- Update: existing remote branch `agent/animated-profile-readme`

**Interfaces:**
- Consumes: the completed role and portrait commits.
- Produces: a verified update to draft PR `reckless-sherixx/reckless-sherixx#1`.

- [ ] **Step 1: Run the complete verification gate**

Run: `.venv/Scripts/python.exe -m pytest -q`

Parse `data/contributions.json`, `portrait-ascii.svg`, `info-card.svg`, `contrib-heatmap.svg`, and `.github/workflows/update-profile-art.yml`. Verify the source-image SHA-256 match and run `git diff --check`.

Expected: 20 tests pass, all assets parse, hashes match, and the diff check exits zero.

- [ ] **Step 2: Review scope and history**

Run: `git status --short --branch`, `git diff origin/agent/animated-profile-readme...HEAD --stat`, and `git log --oneline origin/agent/animated-profile-readme..HEAD`.

Expected: only the approved specification, plan, portrait artifacts, role-copy files, and related tests differ.

- [ ] **Step 3: Push the verified branch**

Run: `git push origin agent/animated-profile-readme`

Verify PR #1 remains open and draft with head `agent/animated-profile-readme` and base `main`.

# Reckless Sherixx GitHub Profile README Design

## Goal

Create a terminal-style animated GitHub profile README for `reckless-sherixx`, following Avi Vashishta's published technique while using original content, the supplied portrait, and live public GitHub activity.

The finished profile should introduce Vidyansh Singh quickly, emphasize open-source Kubernetes and Go work, remain readable on GitHub's light and dark themes, and require little manual maintenance.

## Approved Identity

- Name: Vidyansh Singh
- GitHub username: `reckless-sherixx`
- Title: Open Source Developer · Kubernetes · Go
- Focus: Cloud Native and Distributed Systems
- Core stack: Go, Kubernetes, TypeScript, and Docker

Only information supported by the public GitHub profile and repositories will be presented as fact. The README will not invent social accounts, employment, achievements, or private statistics.

## Visual Direction

Use a faithful terminal-profile composition with a dark GitHub-style palette, pale monochrome portrait glyphs, and restrained GitHub-green accents. The design should feel technical and personal without becoming a dense badge wall.

Animations will play once and freeze. Motion will be implemented inside self-contained SVG files because GitHub README sanitization does not permit JavaScript or dependable inline styling.

## Layout

The README will use centered HTML supported by GitHub-flavored Markdown.

1. A shell-style `whoami` heading.
2. A two-column table containing the animated ASCII portrait and neofetch information card.
3. A shell-style contributions heading.
4. A full-width animated contribution heatmap.
5. A small profile link area containing only verified links.

The portrait and card widths will add up to the heatmap width so the composition has aligned outer edges. Alternative text will describe every image.

## Components

### Portrait Pipeline

The supplied JPG is the source image. A deterministic local Python pipeline will:

1. isolate the subject from the outdoor background;
2. improve local contrast and convert the result to grayscale;
3. place the subject on a white background;
4. sample the image into an ASCII character grid; and
5. emit an SVG whose rows type from left to right with staggered timing.

The original portrait will not be generatively restyled. A project-local copy of the source will be retained so the artwork is reproducible.

### Information Card

The neofetch-style SVG will display the approved identity, focus, and core stack. Lines will fade and slide into place with a short stagger. Content will be generated from a small, explicit data structure so it can be edited without rewriting SVG markup.

### Contribution Heatmap

A fetch script will request the public GitHub contribution fragment for `reckless-sherixx`, parse daily cells, and store normalized contribution data as JSON. A render script will produce a 53-week by 7-day animated SVG with a green intensity ramp, month labels, a Less-to-More legend, and factual summary statistics derived from the fetched data.

Network or parsing failures must stop generation with a clear error rather than replacing the existing graph with empty data.

### GitHub Actions Refresh

A scheduled workflow and manual dispatch will install only the heatmap dependencies, fetch current public contributions, regenerate the JSON and SVG, and commit changes only when output differs. It will have repository-content write permission and avoid retriggering itself.

## Repository Contents

The profile repository will contain:

- `README.md`
- source and generated portrait assets
- generated information-card and heatmap SVG files
- `data/contributions.json`
- focused Python scripts for portrait preparation, ASCII rendering, card rendering, contribution fetching, and heatmap rendering
- pinned Python requirements
- a GitHub Actions workflow for daily heatmap refresh
- lightweight tests for parsing, statistics, SVG structure, and error handling

## Verification

Before publication:

- run the automated tests;
- generate every asset from the scripts;
- validate the generated SVG files as XML;
- inspect rasterized previews for clipping, alignment, portrait recognition, and text legibility;
- confirm all README paths and external links;
- check the workflow syntax and permissions;
- inspect the complete profile layout locally as closely as GitHub rendering permits; and
- run whitespace and repository-status checks before any push.

Publication requires authenticated write access to the `reckless-sherixx` account. The currently connected GitHub integration belongs to another account, so the finished local repository will not be pushed until the correct account is connected or another authorized publication route is provided.

## Out of Scope

- JavaScript or externally hosted animation services
- unverified social links or employment claims
- visitor counters, trophy walls, and large badge collections
- private contribution data
- continuous regeneration of the static portrait or information card

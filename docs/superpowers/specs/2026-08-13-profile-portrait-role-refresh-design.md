# Profile Portrait and Role Refresh Design

## Goal

Update the animated GitHub profile README to use the supplied `377437.jpg` artwork and describe Vidyansh as an open-source contributor rather than an open-source developer.

## Visual Treatment

- Preserve the current two-column terminal layout, dimensions, animation style, purple palette, contribution heatmap, and responsive behavior.
- Replace `assets/source-portrait.jpg` with a byte-for-byte project-local copy of the supplied `E:/COMP-DOWNLOADS/377437.jpg` file.
- Run the existing portrait preparation and ASCII SVG generators against the replacement source.
- Keep `assets/portrait-prepped.png` and `portrait-ascii.svg` as generated, committed artifacts so GitHub can render the profile without a build step.
- Continue presenting the generated portrait as the left-side identity artwork; do not add a second portrait or display the source JPEG directly in the README.

## Copy Changes

- Use the exact public role line `Open Source Contributor · Kubernetes · Go`.
- Replace the old developer wording in the README, generated information card, SVG accessibility description, and executable tests.
- Do not change the username, name, GitHub URL, skills, contribution data, or command-style section headings.

## Data Flow

1. Copy the supplied JPEG into `assets/source-portrait.jpg` without modifying the external original.
2. Generate `assets/portrait-prepped.png` with the existing preparation script.
3. Generate `portrait-ascii.svg` with the existing animated ASCII generator.
4. Update the role constant in the information-card generator and regenerate `info-card.svg`.
5. Update the README role line and tests to enforce the new wording.

## Validation

- Prove the new source asset is byte-identical to `377437.jpg`.
- Run the focused role-copy test in a red-green cycle.
- Run the portrait pipeline and verify the generated PNG and SVG are readable.
- Run the full test suite.
- Parse all committed SVG, JSON, and workflow files.
- Run `git diff --check` and visually inspect the refreshed README artwork before pushing.

## Delivery

Commit the implementation to `agent/animated-profile-readme` and push it to the existing draft pull request, `reckless-sherixx/reckless-sherixx#1`.

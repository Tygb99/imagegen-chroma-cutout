# imagen-design-hub

[한국어 README](README.ko.md)

[![GitHub stars](https://img.shields.io/github/stars/Tygb99/imagen-design-hub?style=social)](https://github.com/Tygb99/imagen-design-hub/stargazers)

Codex skill for preparing MiriCanvas / DesignHub assets with `image_gen`, local source art, vector exports, and animation files.

It covers four common routes:

1. **JPG background elements**: generate natural bitmap backgrounds with built-in `image_gen`, preserve source PNGs, convert to validated JPG, and write DesignHub CSV rows with `contentType=Background`.
2. **Transparent PNG elements**: generate on a flat chroma-key background, remove the key with the bundled helper, finish upload-ready PNGs through Photopea when needed, and write matching DesignHub metadata.
3. **SVG elements**: route simple vector illustrations through SVG cleanup, color-count checks, and `contentType=SVG element`.
4. **GIF elements**: route animated illustration frames through GIF encode/playback checks and `contentType=GIF`.

The skill intentionally keeps source files, final files, review sheets, prompt logs, and CSVs separated so a DesignHub batch can be audited before upload.

## Plugin Skill Split

The personal plugin exposes five focused skill entrypoints:

- `png-element`: PNG elements, chroma-key removal, Photopea finishing, and `contentType=PNG element`.
- `jpg-background`: JPG backgrounds and `contentType=Background`.
- `svg-beta`: SVG element candidates, kept as a beta route until visual validation passes.
- `gif-beta`: GIF element candidates, kept as a beta route until playback and transparency validation pass.
- `upload-csv`: use Computer Use for DesignHub file upload, CSV download, and merged CSV upload while preserving `uniqueId` values.

## Codex Plugin Install

Install the public plugin with:

```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/Tygb99/imagen-design-hub/main/scripts/install_plugin.sh)"
```

Manual install:

```bash
git clone https://github.com/Tygb99/imagen-design-hub.git ~/plugins/imagen-design-hub
node ~/plugins/imagen-design-hub/scripts/register_marketplace.mjs
```

The installer registers `~/plugins/imagen-design-hub` in `~/.agents/plugins/marketplace.json`.

## Auto Update

The plugin includes a `SessionStart` hook that checks for updates when Codex starts a new session.

- Auto-update only runs for git checkout installs.
- The hook uses `git fetch` and `git pull --ff-only`.
- If local changes are present, the hook skips the update instead of overwriting them.
- Copy-only installs are left untouched; reinstall with the git-based installer to receive updates.

## Public Page Previews

- Main page: <https://tygb99.github.io/imagen-design-hub/>
- Branch preview index: <https://tygb99.github.io/imagen-design-hub/branches/>
- Branch URL pattern: `https://tygb99.github.io/imagen-design-hub/branches/<branch-slug>/`

Branch slugs are lowercase branch names with `/` and other separators converted to `-`. For example, `codex/clean-landing-reference` is published at `/branches/codex-clean-landing-reference/`.

## Dependencies

Required for image generation:

- Codex or another agent runtime that can use the built-in `image_gen` tool.

Required for local processing:

- Python 3.10 or newer.
- Pillow.
- NumPy for the chroma-key helper.

Install Python dependencies only when needed:

```bash
python -m pip install -r requirements.txt
```

On Windows PowerShell, run from the skill directory and use:

```powershell
py -3 -m pip install -r requirements.txt
```

Required for upload-ready PNG elements:

- Photopea in a Chromium-family browser.
- The bundled `scripts/write_photopea_runner.py` runner generator, unless the current project has a stronger Photopea runner.

Required for SVG/GIF element work:

- A true vector editor/export path for SVG assets.
- A GIF encoder/player for animation playback, transparency, size, and file-size checks.

## Repository Layout

- `SKILL.md`: routing and validation instructions.
- `SKILL.ko.md`: Korean version of the skill instructions.
- `src/imagegen_chroma_cutout/`: reusable Python implementation kept under the old package name for compatibility.
- `scripts/chroma_key.py`: primary edge-connected chroma-key to alpha helper copied from the project helper.
- `scripts/remove_chroma_key.py`: legacy soft-matte chroma-key helper; use only for explicit comparison or fallback.
- `scripts/write_photopea_runner.py`: bundled Photopea runner generator.
- `scripts/prepare_designhub_unique_upload.py`: upload-safe basename/CSV helper for PNG element batches.
- `assets/photopea_runner.html`: browser template for the bundled Photopea runner.
- `evals/evals.json`: routing test prompts.
- `references/designhub-element-guide-map.md`: official DesignHub element-guide link map and summarized type rules.

## DesignHub Background JPG Route

Use imagegen for natural backgrounds such as pool water, paper textures, light reflections, realistic patterns, and other bitmap backgrounds where generated visual quality matters.

Expected local layout:

```text
outputs/<run-id>/assets/source-imagegen-batch/
outputs/<run-id>/assets/background-jpg-imagegen/
outputs/<run-id>/metadata/
outputs/<run-id>/review/
outputs/<run-id>/logs/
```

CSV rules for background JPGs:

- `fileName`: basename only, no `.jpg`
- `uniqueId`: blank unless DesignHub provided it
- `tier`: `Premium`
- `contentType`: `Background`

## Transparent PNG Element Route

Use `scripts/chroma_key.py` and the Photopea route for PNG elements. Do not use the built-in `.system/imagegen` `remove_chroma_key.py` helper for DesignHub PNG-element runs.

```bash
python scripts/chroma_key.py \
  --input source.png \
  --output final-alpha.png \
  --background "#8000ff" \
  --tolerance 48 \
  --scope edge \
  --dpi 350
```

Windows PowerShell:

```powershell
py -3 ./scripts/chroma_key.py `
  --input "./source.png" `
  --output "./final-alpha.png" `
  --background "#8000ff" `
  --tolerance 48 `
  --scope edge `
  --dpi 350
```

For DesignHub/MiriCanvas upload-ready PNGs, generate or use a Photopea runner:

```bash
python scripts/write_photopea_runner.py \
  --raw-dir outputs/<run-id>/assets/raw \
  --processed-dir outputs/<run-id>/assets/processed \
  --out outputs/<run-id>/photopea/runner.html
```

## SVG And GIF Element Routes

Use SVG for simple, color-changeable vector illustrations with a clear subject, fully removed background, and five or fewer colors. Do not submit an SVG that only embeds a raster image.

Use GIF for animated illustration/art elements with a clear subject and removed background. A still image saved as GIF is not enough, and filmed footage belongs to the gated MP4 video route.

CSV rules:

- SVG: `contentType=SVG element`, extensionless `fileName`.
- GIF: `contentType=GIF`, extensionless `fileName`.

See `references/designhub-element-guide-map.md` for the official element-guide page map, file specs, and combination-element boundaries.

Windows PowerShell:

```powershell
py -3 ./scripts/write_photopea_runner.py `
  --raw-dir "outputs/<run-id>/assets/raw" `
  --processed-dir "outputs/<run-id>/assets/processed" `
  --out "outputs/<run-id>/photopea/runner.html"
```

## DesignHub Keyword Rules

- Use 20 to 25 comma-separated buyer-facing keywords.
- Remove duplicates.
- Remove production, file, admin, and filler terms such as `Photopea`, `API`, `imagegen`, `PNG`, `JPG`, `SVG`, `GIF`, `MP4`, `2D`, `350DPI`, run IDs, `DesignHub`, `MiriCanvas`, `CSV`, `Premium`, `clipart`, `design source`, and similar terms.
- Keep `elementName` short and human-readable.

## License

MIT. See [LICENSE](LICENSE). Korean translation: [LICENSE.ko.md](LICENSE.ko.md).

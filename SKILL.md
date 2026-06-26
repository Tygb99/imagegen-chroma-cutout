---
name: imagen-design-hub
description: Use when preparing MiriCanvas or DesignHub assets from imagegen or local source art: JPG backgrounds, photo JPGs, transparent PNG elements, SVG elements, GIF elements, chroma-key cutouts, Photopea finishing, DesignHub CSV repair, keyword cleanup, upload-safe filenames, or official element-guide routing.
---

# Imagen Design Hub

[Korean version](SKILL.ko.md)

This skill handles MiriCanvas / DesignHub visual assets prepared from `image_gen`, local source art, or vector/animation tools. It keeps raster imagegen routes and official SVG/GIF element-guide routing in one place.

Core routes:

- If the target is a background element, use `image_gen -> preserve source PNG -> convert/validate JPG -> Background CSV`.
- If the target is a transparent PNG element, use `image_gen -> preserve chroma-key source -> helper alpha -> Photopea -> PNG element CSV`.
- If the target is an SVG element, use `vector source -> SVG cleanup -> SVG validation -> SVG element CSV`, but treat this route as early alpha and verify manually.
- If the target is a GIF element, use `frame/animation source -> GIF encode -> animation/size validation -> GIF CSV`, but treat this route as early alpha and verify manually.
- Prefer the imagegen background route when natural water surfaces, ripples, light reflections, photographic textures, or realistic backgrounds matter more than HTML/canvas determinism.
- Read [references/designhub-element-guide-map.md](references/designhub-element-guide-map.md) when you need the full official element-guide link map.

## Dependencies

- Required for generation: built-in `image_gen` tool.
- Required for local image processing: Python 3.10+ and Pillow when using `scripts/chroma_key.py`. NumPy is only needed for the legacy `scripts/remove_chroma_key.py` fallback.
- Required for upload-ready PNG elements: Photopea in a Chromium-family browser plus a Photopea runner. Prefer a project-specific runner when one exists; otherwise use `scripts/write_photopea_runner.py`.
- Required for SVG elements: a true vector source/editor/export path and an XML/SVG validation pass. Do not submit an SVG that only embeds a raster image.
- Required for GIF elements: a frame or animation source plus a GIF encoder/player that can confirm loop/playback, transparency, dimensions, and file size.
- Reusable Python code lives in `src/imagegen_chroma_cutout/`; the old package name is kept for script compatibility.
- Do not use external upload/submission actions unless the user explicitly confirms.

Install helper dependencies only when needed:

```bash
python -m pip install -r requirements.txt
```

On Windows, run commands from the skill directory in PowerShell and use `py -3` or `python` instead of relying on `python3` or POSIX shell expansion:

```powershell
py -3 -m pip install -r requirements.txt
```

## Route Selection

Classify the deliverable before generating images.

### `background-jpg`

Use for DesignHub background elements, JPG backgrounds, broad textures, water surfaces, pool floors, patterns, paper/gradient backgrounds, and other document-filling images.

- Use built-in `image_gen`.
- Do not request transparent background, chroma key, checkerboard, cutout, or Photopea alpha processing.
- Prompt for a full-bleed rectangular or square background with no dominant subject.
- Preserve source PNGs from the Codex generated image directory in the workspace. Use `$CODEX_HOME/generated_images/...` in POSIX shells and `$env:CODEX_HOME\generated_images\...` in Windows PowerShell when the environment variable is available.
- Convert final files to JPG.
- Use DesignHub CSV `contentType` value `Background`.
- Remove `.jpg` from CSV `fileName`.
- Leave `uniqueId` blank unless the value came from DesignHub's downloaded metadata CSV after file upload.

Recommended folders:

```text
outputs/<run-id>/assets/source-imagegen-batch/
outputs/<run-id>/assets/background-jpg-imagegen/
outputs/<run-id>/metadata/
outputs/<run-id>/review/
outputs/<run-id>/logs/
```

### `png-element`

Use for transparent stickers, illustrations, objects, cutouts, PNG elements, background removal, and any asset that must have alpha.

- Generate with a flat removable chroma-key background.
- For multiple standalone PNG elements, generate one source image per element. Do not generate one crowded sheet and crop it later; separated enlargements can expose stair-stepped edges and weak anti-aliasing.
- Preserve source images under `assets/source-imagegen/`.
- Run the copied `scripts/chroma_key.py` helper into `assets/raw/`. Do not use the built-in `.system/imagegen` `remove_chroma_key.py` helper for DesignHub PNG-element runs.
- For DesignHub/MiriCanvas upload-ready PNG elements, run Photopea or the project Photopea runner into `assets/processed/`.
- Use DesignHub CSV `contentType` value `PNG element`.
- Prepare upload-safe unique basenames before actual DesignHub registration.

### `photo-jpg`

Use for real photos that are not background elements. A real photo should not be mislabeled as a background just because it is JPG.

### `svg-element`

Use for simple, color-changeable vector illustrations with a clear subject and fully removed background.

- SVG support in this skill is still early alpha. Expect imperfect vector generation, awkward paths, crop/viewBox mistakes, excess colors, or DesignHub rejection even after basic checks pass.
- Use a true vector workflow: hand-authored SVG, vector-editor export, or traced/rebuilt vector art.
- Keep the illustration simple and use 5 colors or fewer.
- Prefer SVG over PNG when the same flat design could reasonably be color-editable in MiriCanvas.
- Do not use SVG for 3D, gradients, photo-like texture, complex raster art, or embedded bitmap output. Route those to `png-element`.
- Use DesignHub CSV `contentType` value `SVG element`.
- Remove `.svg` from CSV `fileName`.
- For extended elements, upload as SVG first, then set the resize type during metadata entry.

### `gif-element`

Use for animated illustration/art elements with a clear subject and fully removed background.

- GIF support in this skill is still early alpha. Expect transparency limits, dithering, edge halos, frame flicker, large file sizes, or loop/playback problems that require manual correction.
- Use frame or animation source files and encode to `.gif`.
- The final asset must visibly animate; a still image saved as GIF is not enough.
- Keep the background removed/transparent wherever the animation format and source allow.
- Do not treat filmed/video footage as a GIF element. Video belongs to the gated `video-element` route.
- Use DesignHub CSV `contentType` value `GIF`.
- Remove `.gif` from CSV `fileName`.

### Gated or editor-only routes

- `video-element`: MP4 video submission requires DesignHub portfolio review and upload permission. Do not promise upload-ready MP4 submission unless the user already has permission.
- `combination-element`: create in the MiriCanvas editor and register by design document URL. It is not a local file batch produced by this skill.

## Imagegen Background Workflow

Use this route when the user says imagegen is better, asks for background JPGs, or the asset is a natural texture/background where generative bitmap quality matters.

1. Read the project instructions first when working inside a `miricanvas-design` checkout, using paths relative to the current repo root.
2. If the user gives a reference image, inspect it and label it as a reference, not an edit target, unless the user asks to modify that exact image.
3. Create one built-in `image_gen` call per requested variant. Distinct backgrounds should get distinct prompts.
4. After generation, find the new files under the Codex generated image directory and copy them into the workspace. Leave the original generated files in place.
5. Convert each selected source to JPG:
   - RGB, no alpha
   - minimum 2500 px on each side for DesignHub background
   - maximum 9800 px
   - at least 120 DPI; use 300 DPI for local consistency unless the project says otherwise
   - under 50 MB
6. Write a matching CSV with headers:
   ```text
   fileName,uniqueId,elementName,keywords,tier,contentType
   ```
7. For background JPG rows:
   - `fileName`: basename only, no `.jpg`
   - `uniqueId`: blank for filename-only registration
   - `tier`: `Premium`
   - `contentType`: `Background`
8. Make a contact sheet and inspect it. Background elements should have no people, objects, text, logos, watermarks, frames, or single dominant subject.
9. Validate with both numbers and eye check before reporting.

### Background Prompt Template

```text
Use case: photorealistic-natural
Asset type: MiriCanvas DesignHub background JPG source
Primary request: <background topic>
Scene/backdrop: <surface/environment>
Style/medium: photorealistic high-resolution background texture
Composition/framing: full-bleed square or rectangular background, no focal subject, no border
Lighting/mood: <lighting and mood>
Color palette: <colors>
Materials/textures: <tile, water, paper, caustic light, etc.>
Constraints: no text, no logo, no watermark, no people, no objects, no transparent background, no checkerboard, no dominant subject
```

## Transparent PNG Cutout Workflow

Use this route when the user asks for transparent PNG, PNG element, cutout, background removal, Photopea, or upload-ready alpha assets.

1. Choose a chroma-key color:
   - default `#00ff00`
   - use `#ff00ff` for green subjects
   - avoid `#0000ff` for blue subjects
   - use the existing project key color only when it does not conflict with the subject
   - if any subject color is close to the key color, choose another key color before generating; do not rely on the helper to rescue a conflicting key
2. Generate with built-in `image_gen` on a perfectly flat key-color background.
3. Copy the generated source into the workspace.
4. Run the copied `scripts/chroma_key.py` helper.
5. Validate alpha, transparent corners, subject coverage, key-color fringe, interior detail preservation, and anti-aliased edges on checkerboard, white, and dark previews.
6. For DesignHub/MiriCanvas upload-ready PNG elements, run Photopea finishing and validate `assets/processed/`.
7. Prepare upload-safe unique filenames and a matching CSV.

### Chroma Prompt Template

```text
Use case: background-extraction
Asset type: transparent PNG cutout / PNG element
Primary request: <user request>
Subject: <single clear subject or element set>
Style/medium: <photo, illustration, 3D, flat 2D, etc.>
Composition/framing: centered subject, fully visible, generous padding, no cropping
Scene/backdrop: perfectly flat solid <KEY_COLOR> chroma-key background
Constraints:
- The background must be one uniform <KEY_COLOR> color with no shadows, gradients, texture, reflections, floor plane, lighting variation, or checkerboard.
- Keep the subject fully separated from the background with crisp readable edges.
- Do not use <KEY_COLOR> anywhere inside the subject.
- No cast shadow, contact shadow, reflection, watermark, logo, signature, UI capture, QR code, or text unless explicitly requested.
- Preserve all subject details; do not cut off any part of the subject.
```

## Helper Command

Use the copied `scripts/chroma_key.py` helper first. This file is intentionally copied from the attached/project `scripts/chroma_key.py` helper and should be kept in this skill bundle. Do not use the built-in `.system/imagegen` `remove_chroma_key.py` helper for DesignHub PNG-element runs. Do not use the legacy `scripts/remove_chroma_key.py` helper unless the user explicitly asks for a comparison or fallback.

If the copied helper is missing or stale, copy the attached/project helper into the skill before running it:

```bash
cp "<repo>/scripts/chroma_key.py" "scripts/chroma_key.py"
chmod +x "scripts/chroma_key.py"
```

Run the helper with an explicit key color and edge-connected cleanup:

```bash
python scripts/chroma_key.py \
  --input "<source.png>" \
  --output "<final-alpha.png>" \
  --background "<KEY_COLOR>" \
  --tolerance 48 \
  --scope edge \
  --dpi 350
```

PowerShell equivalent:

```powershell
py -3 ./scripts/chroma_key.py `
  --input "./source.png" `
  --output "./final-alpha.png" `
  --background "<KEY_COLOR>" `
  --tolerance 48 `
  --scope edge `
  --dpi 350
```

Default edge mode removes pixels connected to the image border and also removes enclosed exact/near key-color islands using `min(tolerance, 24)`. If the subject contains colors close to the key color, regenerate with a safer key color first. For an explicit comparison run that preserves enclosed near-key subject colors, use:

```bash
python scripts/chroma_key.py \
  --input "<source.png>" \
  --output "<final-alpha-preserve0.png>" \
  --background "<KEY_COLOR>" \
  --tolerance 48 \
  --scope edge \
  --enclosed-tolerance 0 \
  --dpi 350
```

Use higher tolerance only after confirming the key color does not overlap with the subject. If the key color conflicts with the subject, change the prompt/background color instead of widening tolerance.

Contact sheets are review artifacts only. Do not crop final upload PNGs out of a multi-object sheet; if a standalone element looks jagged after separation, return to the original per-element source or regenerate it individually.

## Photopea Processing

Photopea is not a substitute for background removal. It is the finishing step for alpha PNG elements.

For DesignHub/MiriCanvas PNG element runs:

1. Keep imagegen sources in `assets/source-imagegen/`.
2. Keep helper alpha outputs in `assets/raw/`.
3. Run the project runner when one exists:
   ```bash
   node src/cli.mjs photopea-runner --run outputs/<run-id>
   ```
4. Otherwise create the bundled runner:
   ```bash
   python scripts/write_photopea_runner.py \
     --raw-dir "outputs/<run-id>/assets/raw" \
     --processed-dir "outputs/<run-id>/assets/processed" \
     --out "outputs/<run-id>/photopea/runner.html"
   ```
   On Windows PowerShell:
   ```powershell
   py -3 ./scripts/write_photopea_runner.py `
     --raw-dir "outputs/<run-id>/assets/raw" `
     --processed-dir "outputs/<run-id>/assets/processed" `
     --out "outputs/<run-id>/photopea/runner.html"
   ```
5. For the `miricanvas-design` repo, keep PNG elements at 350 DPI, at least 2500 px on each side, tight alpha bbox, and alpha preserved.

Skip Photopea for JPG backgrounds unless the user explicitly asks for manual image editing.

## SVG Element Workflow

Use this route when the user asks for SVG elements, vector elements, color-changeable icons, simple stickers, extended elements, speech bubbles, labels, flags, memo notes, or shapes that should resize cleanly.

This route is early alpha. Use it to produce candidates and validation evidence, not to imply DesignHub acceptance. When visual quality matters, compare against a vector-editor or Claude-generated candidate and keep the better source.

1. Start from a vector source. If imagegen was used for ideation, rebuild or trace it into real vector shapes before final export.
2. Remove backgrounds and artboards that would behave like rectangular images.
3. Keep one clear subject or reusable element. Avoid template-like finished layouts.
4. Reduce and clean colors to 5 or fewer visible fill/stroke colors.
5. Avoid embedded raster images, external links, scripts, `foreignObject`, hidden watermarks, text converted from unknown fonts, and stray off-artboard objects.
6. Export a clean `.svg` with a sensible tight-crop `viewBox`.
7. Validate file specs:
   - SVG extension
   - at least 72 DPI when the exporting tool exposes DPI
   - maximum dimension 6000 px
   - under 150 MB
8. Render the SVG on checkerboard, white, and dark previews and confirm it has no rectangular artboard/backdrop, no clipped subject, no excess whitespace, and no obvious path-quality problems.
9. Write CSV rows with extensionless `fileName`, blank or DesignHub-provided `uniqueId`, `tier` set to `Premium`, and `contentType` set to `SVG element`.

For extended SVG elements, keep the file workflow identical. The extended/basic distinction is selected in metadata as a resize type, not by changing the file extension.

## GIF Element Workflow

Use this route when the user asks for GIF elements, animated stickers, looping illustrations, motion badges, or moving icon-like art.

This route is early alpha. Use it to produce candidates and validation evidence, not to imply DesignHub acceptance. GIF transparency and frame optimization often need manual review.

1. Build or collect frame/animation source files. Preserve them in a source folder.
2. Keep the subject clear, fully visible, and separated from the background across every frame.
3. Do not convert filmed footage into a GIF element unless the user explicitly wants a non-DesignHub experiment. DesignHub video is a separate MP4 route with permission gating.
4. Encode to `.gif` and inspect playback, loop timing, edge residue, and frame-to-frame jitter.
5. Validate file specs:
   - GIF extension
   - visibly animated, not a still GIF
   - at least 72 DPI when available
   - minimum 700 px
   - maximum 1920 px
   - under 25 MB
6. Render the GIF on checkerboard, white, and dark previews and confirm transparent/removed backgrounds do not flicker across frames.
7. Write CSV rows with extensionless `fileName`, blank or DesignHub-provided `uniqueId`, `tier` set to `Premium`, and `contentType` set to `GIF`.

If the requested motion is better represented as filmed video, stop and route it to `video-element`; confirm the user has DesignHub video permission before preparing an MP4 submission batch.

## Metadata Rules

DesignHub/MiriCanvas metadata should describe what buyers search for, not the production workflow.

- Use 20 to 25 comma-separated keywords.
- Remove duplicates.
- Put official topic words and concrete visual terms first.
- Remove production/process/file/admin terms from `keywords` and `elementName`.
- Avoid terms such as `Photopea`, `API`, `후처리`, `프롬프트`, `imagegen`, `배경제거`, `PNG`, `JPG`, `SVG`, `GIF`, `MP4`, `2D`, `350DPI`, `투명배경`, run IDs, dates, `DesignHub`, `MiriCanvas`, `CSV`, `Premium`, `클립아트`, `디자인소스`, `배경소스`, `꾸밈요소`.
- If the user explicitly keeps or removes a keyword, enforce that across CSV and docs.

CSV content type values:

```text
Photo
Photo(Cut-out)
SVG element
PNG element
GIF
Background
```

Do not write `JPG background` in DesignHub CSV. Use `Background`.

## DesignHub CSV Roundtrip

After live file upload, DesignHub's downloaded CSV is the source of truth for `fileName` and `uniqueId`. Do not upload a local preupload CSV directly after files are registered.

1. Upload the files through the approved UI route only after user confirmation.
2. Download the current DesignHub CSV.
3. Merge prepared metadata into the downloaded full CSV while preserving every existing row and every `uniqueId`.
4. Upload the merged full CSV through the UI.
5. Verify the DesignHub completion message or banner, including the processed row count.
6. State separately whether file upload, CSV upload, and final review submission happened. Never click final review submission unless the user asks for that separate step.

## Upload-Safe Filenames

For PNG elements, DesignHub can reject names that were used in earlier attempts. Before upload, create a separate unique-name folder and matching CSV.

Recommended basename:

```text
<short-topic-slug>-<YYYYMMDD>-<HHmm>-<NN>
```

Bundled helper:

```bash
python scripts/prepare_designhub_unique_upload.py \
  --csv "outputs/<run-id>/metadata/preupload.csv" \
  --images-dir "outputs/<run-id>/assets/processed" \
  --out-dir "outputs/<run-id>/assets/processed-designhub-unique-<YYYYMMDD-HHmm>" \
  --out-csv "outputs/<run-id>/metadata/designhub-preupload-unique-<YYYYMMDD-HHmm>.csv" \
  --prefix "<short-topic-slug>-<YYYYMMDD>-<HHmm>"
```

PowerShell equivalent:

```powershell
py -3 ./scripts/prepare_designhub_unique_upload.py `
  --csv "outputs/<run-id>/metadata/preupload.csv" `
  --images-dir "outputs/<run-id>/assets/processed" `
  --out-dir "outputs/<run-id>/assets/processed-designhub-unique-<YYYYMMDD-HHmm>" `
  --out-csv "outputs/<run-id>/metadata/designhub-preupload-unique-<YYYYMMDD-HHmm>.csv" `
  --prefix "<short-topic-slug>-<YYYYMMDD>-<HHmm>"
```

For JPG backgrounds, SVG elements, and GIF elements, still avoid generic names. Use a topic slug plus timestamp/index, and keep CSV `fileName` extensionless.

## Validation

Run validation suited to the route.

### Background JPG checks

- Source PNGs exist in the workspace, not only under the Codex generated image directory.
- Final files are JPEG/JPG.
- No alpha channel.
- Width and height meet DesignHub background limits.
- DPI is at least 120.
- File size is under 50 MB.
- CSV row count equals final JPG count.
- CSV `fileName` has no extension and maps to `<fileName>.jpg`.
- CSV `uniqueId` is blank or DesignHub-provided.
- CSV `contentType` is `Background`.
- Keywords are 20 to 25 unique buyer-facing terms.
- Contact sheet shows usable background assets with no forbidden visible content.

### PNG element checks

- Final files are PNG with alpha.
- Transparent corners and plausible subject coverage.
- No obvious key-color fringe.
- No subject interior detail was erased because it matched the key color.
- Edges look anti-aliased at magnified scale, not stair-stepped.
- Final upload files were not cropped out of a combined contact sheet.
- Checkerboard, white, and dark previews pass.
- Photopea processed outputs exist when upload-ready PNG elements are requested.
- PNG element dimensions/DPI match the local project rule.
- CSV basenames and processed/upload PNG basenames match.
- Keywords are 20 to 25 unique buyer-facing terms.

### SVG element checks

- Final files are SVG, not raster images renamed to `.svg`.
- XML parses cleanly.
- No embedded raster `<image>` payloads, scripts, external links, or `foreignObject`.
- `viewBox` and dimensions are present and within the 6000 px maximum.
- Visible colors are 5 or fewer.
- Background is removed; the SVG does not contain a rectangular backdrop unless the element itself is a reusable note/sticker shape.
- No cracks, stray shapes, hidden off-artboard objects, watermarks, logos, or text artifacts.
- Because this route is early alpha, path quality, crop, and DesignHub suitability must be checked by eye before calling it upload-ready.
- CSV `contentType` is `SVG element`, and CSV basenames match final SVG basenames without extensions.

### GIF element checks

- Final files are GIF and visibly animated.
- Dimensions are at least 700 px and at most 1920 px.
- File size is under 25 MB.
- Background is removed/transparent where appropriate and does not flicker between frames.
- Subject remains clear, uncropped, and stable through the loop.
- It is animated illustration/art, not a video element mislabeled as GIF.
- Because this route is early alpha, transparency quality, edge halos, and playback smoothness must be checked by eye before calling it upload-ready.
- CSV `contentType` is `GIF`, and CSV basenames match final GIF basenames without extensions.

If the project provides a validation command, run it when it applies:

```bash
node src/cli.mjs validate --run outputs/<run-id>
```

## Complex Transparency Boundary

Chroma-key removal can fail or damage the subject for hair, fur, feathers, smoke, mist, water spray, glass, liquid, transparent objects, reflections, soft shadows, and subjects whose colors conflict with practical key colors.

If true native transparency appears necessary, ask before switching to CLI/API fallback. Do not silently switch from the built-in `image_gen` route.

## Final Report

Report the concrete route and artifacts:

- built-in `image_gen` or CLI fallback
- deliverable type: `background-jpg`, `png-element`, `photo-jpg`, `svg-element`, `gif-element`, `video-element`, or `combination-element`
- source image folder
- final image folder
- metadata CSV path
- review/contact sheet path
- prompt log path when a batch was generated
- keyword count and removed production terms
- validation summary
- SVG/GIF early-alpha limitations when those routes were used
- whether Photopea was used or intentionally skipped
- any remaining upload risk

State clearly that external upload/submission was not performed unless the user explicitly approved it.

## Test Prompts

Use `evals/evals.json` to sanity-check routing. Full eval/viewer loops are optional and should be run when the user wants deeper skill benchmarking.

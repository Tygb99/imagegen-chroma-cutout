---
name: imagen-design-hub
description: Use this skill whenever the user is preparing MiriCanvas or DesignHub raster assets with imagegen: JPG background elements, AI-generated pool/water/pattern/texture backgrounds, transparent PNG cutouts, PNG elements, chroma-key background removal, Photopea crop/DPI finishing, DesignHub metadata CSV repair, keyword cleanup, or upload-safe filename batches. Prefer built-in image_gen for natural/photorealistic DesignHub backgrounds, preserve source PNGs in the workspace, convert final backgrounds to validated JPG, use chroma-key removal only for transparent PNG elements, and always validate file format, dimensions, DPI, alpha/no-alpha, CSV fileName/uniqueId/contentType, keywords, and review sheets before reporting readiness.
---

# Imagen Design Hub

[한국어판](SKILL.ko.md)

이 스킬은 MiriCanvas / DesignHub에 올릴 `imagegen` 기반 비트맵 산출물을 다룬다. 기존 투명 PNG 중심 흐름을 포함하되, 이제 투명 PNG 요소뿐 아니라 DesignHub 배경 JPG까지 같은 판단 체계 안에서 처리한다.

핵심 분기:

- 배경 요소가 목표이면 `image_gen -> source PNG 보존 -> JPG 변환/검증 -> Background CSV`.
- 투명 PNG 요소가 목표이면 `image_gen -> chroma-key source 보존 -> helper alpha -> Photopea -> PNG element CSV`.
- HTML/canvas보다 자연스러운 수면, 물결, 빛반사, 사진풍 질감, 실사 배경이 더 중요하면 imagegen 배경 경로를 우선한다.

## Dependencies

- Required for generation: built-in `image_gen` tool.
- Required for local image processing: Python 3.10+, Pillow, and NumPy when using `scripts/remove_chroma_key.py`.
- Required for upload-ready PNG elements: Photopea in a Chromium-family browser plus a Photopea runner. Prefer a project-specific runner when one exists; otherwise use `scripts/write_photopea_runner.py`.
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
- Preserve source images under `assets/source-imagegen/`.
- Run `scripts/remove_chroma_key.py` into `assets/raw/`.
- For DesignHub/MiriCanvas upload-ready PNG elements, run Photopea or the project Photopea runner into `assets/processed/`.
- Use DesignHub CSV `contentType` value `PNG element`.
- Prepare upload-safe unique basenames before actual DesignHub registration.

### `photo-jpg`

Use for real photos that are not background elements. A real photo should not be mislabeled as a background just because it is JPG.

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
2. Generate with built-in `image_gen` on a perfectly flat key-color background.
3. Copy the generated source into the workspace.
4. Run the bundled helper.
5. Validate alpha, transparent corners, subject coverage, and key-color fringe.
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

Use the bundled helper first. For Windows compatibility, prefer running from the skill directory with a relative script path instead of relying on Bash-only environment-variable fallback syntax.

```bash
python scripts/remove_chroma_key.py \
  --input "<source.png>" \
  --out "<final-alpha.png>" \
  --auto-key border \
  --soft-matte \
  --transparent-threshold 12 \
  --opaque-threshold 220 \
  --despill
```

PowerShell equivalent:

```powershell
py -3 .\scripts\remove_chroma_key.py `
  --input ".\source.png" `
  --out ".\final-alpha.png" `
  --auto-key border `
  --soft-matte `
  --transparent-threshold 12 `
  --opaque-threshold 220 `
  --despill
```

If a thin key-color fringe remains, retry once:

```bash
python scripts/remove_chroma_key.py \
  --input "<source.png>" \
  --out "<final-alpha-v2.png>" \
  --auto-key border \
  --soft-matte \
  --transparent-threshold 12 \
  --opaque-threshold 220 \
  --edge-contract 1 \
  --despill
```

Use `--edge-feather 0.25` only when stair-stepping is visible and the subject is not glass, water, smoke, mist, reflection, or another semi-transparent material.

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
   py -3 .\scripts\write_photopea_runner.py `
     --raw-dir "outputs\<run-id>\assets\raw" `
     --processed-dir "outputs\<run-id>\assets\processed" `
     --out "outputs\<run-id>\photopea\runner.html"
   ```
5. For the `miricanvas-design` repo, keep PNG elements at 350 DPI, at least 2500 px on each side, tight alpha bbox, and alpha preserved.

Skip Photopea for JPG backgrounds unless the user explicitly asks for manual image editing.

## Metadata Rules

DesignHub/MiriCanvas metadata should describe what buyers search for, not the production workflow.

- Use 20 to 25 comma-separated keywords.
- Remove duplicates.
- Put official topic words and concrete visual terms first.
- Remove production/process/file/admin terms from `keywords` and `elementName`.
- Avoid terms such as `Photopea`, `API`, `후처리`, `프롬프트`, `imagegen`, `배경제거`, `PNG`, `JPG`, `2D`, `350DPI`, `투명배경`, run IDs, dates, `DesignHub`, `MiriCanvas`, `CSV`, `Premium`, `클립아트`, `디자인소스`, `배경소스`, `꾸밈요소`.
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
py -3 .\scripts\prepare_designhub_unique_upload.py `
  --csv "outputs\<run-id>\metadata\preupload.csv" `
  --images-dir "outputs\<run-id>\assets\processed" `
  --out-dir "outputs\<run-id>\assets\processed-designhub-unique-<YYYYMMDD-HHmm>" `
  --out-csv "outputs\<run-id>\metadata\designhub-preupload-unique-<YYYYMMDD-HHmm>.csv" `
  --prefix "<short-topic-slug>-<YYYYMMDD>-<HHmm>"
```

For JPG backgrounds, still avoid generic names. Use a topic slug plus timestamp/index, and keep CSV `fileName` extensionless.

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
- Checkerboard, white, and dark previews pass.
- Photopea processed outputs exist when upload-ready PNG elements are requested.
- PNG element dimensions/DPI match the local project rule.
- CSV basenames and processed/upload PNG basenames match.
- Keywords are 20 to 25 unique buyer-facing terms.

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
- deliverable type: `background-jpg`, `png-element`, or `photo-jpg`
- source image folder
- final image folder
- metadata CSV path
- review/contact sheet path
- prompt log path when a batch was generated
- keyword count and removed production terms
- validation summary
- whether Photopea was used or intentionally skipped
- any remaining upload risk

State clearly that external upload/submission was not performed unless the user explicitly approved it.

## Test Prompts

Use `evals/evals.json` to sanity-check routing. Full eval/viewer loops are optional and should be run when the user wants deeper skill benchmarking.

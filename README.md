# imagegen-chroma-cutout

[한국어 README](README.ko.md)

Codex skill for generating transparent PNG/WebP cutouts from `image_gen` outputs.

The workflow is intentionally public-repo friendly:

1. Generate a raster image on a flat chroma-key background with the built-in `image_gen` tool.
2. Preserve the source image.
3. Remove the chroma-key background with the bundled `scripts/remove_chroma_key.py` helper.
4. For upload-ready PNG elements, route the alpha image through Photopea with the bundled runner or a project-specific Photopea runner for crop, resize, and DPI finishing.
5. Generate buyer-facing DesignHub keywords and metadata.
6. For DesignHub uploads, copy processed PNGs to upload-safe unique basenames and write a matching CSV.
7. Validate alpha, corners, background fringes, image size, DPI, keyword count, CSV basename alignment, and preview surfaces.

## Dependencies

Required for chroma-key cutouts:

- Codex or another agent runtime that can use the `image_gen` tool.
- Python 3.10 or newer.
- Pillow.
- NumPy.

Install the Python dependency:

```bash
python3 -m pip install -r requirements.txt
```

NumPy is required because the chroma-key helper uses vectorized pixel operations. On a 12-image 2026-06-22 glassmorphism batch, the NumPy CLI path ran about 8.2x faster than the prior Pillow loop path while leaving no visible key-color residue.

Required for upload-ready DesignHub/MiriCanvas PNG elements:

- Photopea in a Chromium-family browser.
- The bundled `scripts/write_photopea_runner.py` runner generator, unless the current project has a stronger Photopea runner.

Optional:

- Project-specific Photopea runners, for example `node src/cli.mjs photopea-runner --run <run-id>`.
- Project-specific validation commands, for example `node src/cli.mjs validate --run <run-id>` in the MiriCanvas/DesignHub pipeline.

## Repository Layout

- `src/imagegen_chroma_cutout/`: reusable Python implementation.
- `assets/photopea_runner.html`: browser template for the bundled Photopea runner.
- `scripts/`: thin CLI wrappers for the commands shown below.

## Helper Usage

```bash
python3 scripts/remove_chroma_key.py \
  --input source.png \
  --out final-alpha.png \
  --auto-key border \
  --soft-matte \
  --transparent-threshold 12 \
  --opaque-threshold 220 \
  --despill
```

## Photopea Runner

DesignHub/MiriCanvas upload-ready assets should not stop at raw alpha PNGs. Generate a Photopea runner, open it in Chrome, select the raw PNG files, choose the processed output folder, and run the batch.

```bash
python3 scripts/write_photopea_runner.py \
  --raw-dir outputs/<run-id>/assets/raw \
  --processed-dir outputs/<run-id>/assets/processed \
  --out outputs/<run-id>/photopea/runner.html
```

The runner trims transparent bounds, resizes to the target range, exports PNG through Photopea, and patches the PNG DPI metadata in the browser. If a local project has a stronger runner such as `node src/cli.mjs photopea-runner --run <run-id>`, use that project runner instead.

## DesignHub Filename De-duplication

DesignHub can reject metadata registration when `fileName` values collide with names already used in the account, even if the current CSV has no internal duplicates. Avoid generic names such as `job-001-01` for upload-facing metadata.

Create an upload-specific PNG folder and matching CSV:

```bash
python3 scripts/prepare_designhub_unique_upload.py \
  --csv outputs/<run-id>/metadata/preupload.csv \
  --images-dir outputs/<run-id>/assets/processed \
  --out-dir outputs/<run-id>/assets/processed-designhub-unique-YYYYMMDD-HHmm \
  --out-csv outputs/<run-id>/metadata/designhub-preupload-unique-YYYYMMDD-HHmm.csv \
  --prefix short-topic-slug-YYYYMMDD-HHmm
```

Upload the copied PNG folder and the generated CSV together. Their basenames and `fileName` values are designed to match one-to-one.

## DesignHub Keyword Rules

For DesignHub metadata, generate keywords for buyers, not for the production workflow.

- Use 20 to 25 comma-separated keywords. Aim for 25.
- Remove duplicates after trimming whitespace and normalizing case.
- Put the strongest 8 to 12 subject/material/style terms first.
- Expand with usage contexts, mood, season, and related objects.
- Always remove process, file, admin, and filler terms such as `Photopea`, `API`, `post-processing`, `prompt`, `imagegen`, `background removal`, `PNG`, `2D`, `350DPI`, `transparent background`, run IDs, `DesignHub`, `MiriCanvas`, `CSV`, `Premium`, `clipart`, and generic design-source labels.
- Keep `elementName` short and human-readable. Do not include production terms there either.

Good keyword direction:

```text
glassmorphism, soap bubble, water drop, crystal, hologram, highlight, glossy, pastel, summer, banner decoration
```

In Korean-first workflows, prefer Korean search terms and add common loanwords only when they are useful search terms.

## License

MIT. See [LICENSE](LICENSE). Korean translation: [LICENSE.ko.md](LICENSE.ko.md).

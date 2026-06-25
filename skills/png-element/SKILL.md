---
name: png-element
description: Use for MiriCanvas or DesignHub PNG element work: imagegen source art, chroma-key background removal, transparent PNG cutouts, Photopea finishing, upload-safe PNG basenames, and PNG element CSV rows.
---

# Imagen Design Hub: PNG Element

Use this route when the user says `png요소`, transparent PNG, cutout, sticker, element, background removal, Photopea, or upload-ready alpha asset.

Shared reference: read `../../SKILL.md` if you need the full DesignHub route map.

## Core Rules

- Use built-in `image_gen` for source creation.
- Generate on a perfectly flat solid chroma-key background.
- Do not request transparent or checkerboard backgrounds from imagegen.
- Pick a key color that does not overlap with the subject. Default to `#8000ff` only when the subject does not use similar purple. For green subjects use magenta; for blue subjects avoid blue.
- Tell imagegen not to use the key color anywhere inside the subject.
- Preserve source files in `assets/source-imagegen/`.
- Run `../../scripts/chroma_key.py` first into `assets/raw/`.
- Do not use `.system/imagegen/remove_chroma_key.py` for DesignHub PNG-element runs.
- Do not use `../../scripts/remove_chroma_key.py` unless the user explicitly asks for a comparison or fallback.
- For upload-ready DesignHub PNGs, finish through Photopea or the project Photopea runner into `assets/processed/`.

## Chroma-Key Helper

Run with edge-connected cleanup:

```bash
python ../../scripts/chroma_key.py \
  --input "<source.png>" \
  --output "<raw-alpha.png>" \
  --background "<KEY_COLOR>" \
  --tolerance 48 \
  --scope edge \
  --dpi 350
```

If subject details close to the key color disappear, regenerate with a safer background color instead of widening tolerance.

## Output Contract

- Final upload candidates are PNG files with alpha.
- Use tight alpha bbox unless the project says otherwise.
- For the current MiriCanvas DesignHub submission flow, keep final PNGs at 350 DPI and at least 2500 px on each side.
- CSV rows use `contentType` value `PNG element`.
- Keywords must be 20 to 25 unique buyer-facing terms.
- Before DesignHub upload, prepare unique upload-safe basenames with `../../scripts/prepare_designhub_unique_upload.py` when reupload collisions are possible.

## Validation

Check all of these before calling the batch ready:

- alpha channel exists
- transparent corners pass
- no visible key-color fringe on checkerboard, white, and dark previews
- subject is not clipped
- Photopea processed outputs exist when upload-ready PNG elements were requested
- CSV basenames match final PNG basenames
- external DesignHub upload/submission was not performed unless the user explicitly confirmed it

---
name: jpg-background
description: Use for MiriCanvas or DesignHub JPG background assets: imagegen backgrounds, natural textures, full-bleed non-subject images, JPG conversion, and Background CSV rows.
---

# Imagen Design Hub: JPG Background

Use this route when the user says `jpg배경`, background JPG, DesignHub background, natural texture, water, paper, pattern, full-bleed surface, or a document-filling image.

Shared reference: read `../../SKILL.md` and `../../references/designhub-element-guide-map.md` if you need the full official routing notes.

## Core Rules

- Use built-in `image_gen`.
- Do not request transparency, checkerboard, cutout, chroma key, or Photopea alpha processing.
- Prompt for a full-bleed square or rectangular background with no dominant subject.
- Avoid people, logos, watermarks, UI captures, text, frames, borders, and single foreground objects.
- Preserve imagegen source PNGs separately before conversion.
- Convert selected sources to JPG with RGB color and no alpha.

## Output Contract

- Final files are `.jpg`.
- Minimum 2500 px on each side for DesignHub background work.
- Maximum 9800 px on either side.
- DPI is at least 120; use 300 DPI for local consistency unless the project says otherwise.
- File size stays under 50 MB.
- CSV rows use `contentType` value `Background`.
- CSV `fileName` is the basename only, without `.jpg`.
- `uniqueId` stays blank unless it came from a DesignHub-downloaded CSV after upload.
- Keywords must be 20 to 25 unique buyer-facing terms.

## Validation

Before reporting ready:

- source PNGs are preserved in the workspace
- final files are real JPEG/JPG images
- no alpha channel remains
- size, DPI, and file-size limits pass
- CSV row count equals final JPG count
- CSV basenames map to final JPG files
- contact sheet shows usable backgrounds, not subjects or finished layouts
- external DesignHub upload/submission was not performed unless the user explicitly confirmed it

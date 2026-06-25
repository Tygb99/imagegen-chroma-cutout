---
name: svg-beta
description: Use for MiriCanvas or DesignHub SVG element beta work: simple vector illustrations, color-editable elements, SVG cleanup, validation, and SVG element CSV rows.
---

# Imagen Design Hub: SVG Beta

Use this route when the user says `svg(beta)`, SVG element, vector element, color-changeable icon, simple flat sticker, extended element, memo note, speech bubble, flag, label, or reusable shape.

This route is beta. Treat outputs as candidates until validation and manual visual review pass.

Shared reference: read `../../SKILL.md` and `../../references/designhub-element-guide-map.md` when official file specs or type boundaries matter.

## Core Rules

- Use a true vector source: hand-authored SVG, vector-editor export, or traced/rebuilt vector art.
- Do not submit raster art renamed to `.svg`.
- Do not embed bitmap payloads as the main artwork.
- Keep the illustration simple with 5 or fewer visible colors.
- Remove rectangular artboards and background shapes unless the shape itself is the reusable element.
- Avoid scripts, external links, `foreignObject`, hidden watermarks, stray off-artboard objects, and text artifacts from unknown fonts.
- Export with a sensible tight `viewBox`.

## Output Contract

- Final files are `.svg`.
- Maximum dimension is 6000 px.
- File size is under 150 MB.
- CSV rows use `contentType` value `SVG element`.
- CSV `fileName` is the basename only, without `.svg`.
- `uniqueId` stays blank unless it came from a DesignHub-downloaded CSV after upload.
- Keywords must be 20 to 25 unique buyer-facing terms.

## Validation

Before calling an SVG candidate ready:

- XML parses cleanly
- no embedded raster `<image>` payloads for the main artwork
- no scripts, external links, or `foreignObject`
- `viewBox` and dimensions are present and within limits
- visible colors are 5 or fewer
- checkerboard, white, and dark previews show no rectangular backdrop, clipping, cracks, or stray shapes
- because this is beta, path quality and DesignHub suitability were checked by eye
- external DesignHub upload/submission was not performed unless the user explicitly confirmed it

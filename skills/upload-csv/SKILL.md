---
name: upload-csv
description: Use after MiriCanvas or DesignHub element files are ready for upload and the next step requires Computer Use to upload files, download DesignHub CSV metadata, preserve uniqueId values, merge rows, and re-upload the CSV.
---

# Imagen Design Hub: Upload Then CSV

Use this route when the user says `요소 업로드후 csv업로드`, `uplode-csv`, `upload-csv`, DesignHub upload CSV, metadata upload, CSV merge, uniqueId preservation, or post-upload DesignHub metadata.

This skill is for the post-file-upload metadata phase. It should not silently submit a DesignHub review.

Shared reference: read `../../SKILL.md` for route-specific `contentType` values and keyword rules.

## Mandatory Computer Use

Any live DesignHub UI action in this route must use `computer-use`.

- Use `computer-use` for Chrome/Finder-style UI actions: opening DesignHub in Chrome, clicking upload controls, selecting files, downloading the DesignHub CSV, uploading the merged CSV, scrolling, typing, or checking UI state.
- Do not use browser automation, direct HTTP calls, hidden APIs, or terminal-only shortcuts for the DesignHub upload/download steps.
- Local CSV merging, row validation, encoding checks, and file inspections may still use normal filesystem and terminal tools.
- Follow the `computer-use` confirmation policy at action time. Uploading files and transmitting CSV metadata to DesignHub require explicit user confirmation before the UI action if that confirmation has not already been provided for the specific files and destination.
- Never click final review submission unless the user explicitly asks for that separate external submission step.

## Required Sequence

1. Use `computer-use` to upload the prepared image/vector/GIF files only when the user has explicitly confirmed the external DesignHub action.
2. Use `computer-use` to download the CSV provided by DesignHub after file upload.
3. Treat the downloaded CSV as the source of truth for `fileName` and `uniqueId`.
4. Merge prepared metadata into the downloaded rows without dropping or regenerating `uniqueId`.
5. Keep the CSV no-BOM and quote all fields.
6. Use `computer-use` to re-upload the merged CSV only when the user has explicitly confirmed that external action.

## Content Type Values

Use the official CSV values exactly:

```text
Photo
Photo(Cut-out)
SVG element
PNG element
GIF
Background
```

Do not write `JPG background`; use `Background`.

## Metadata Rules

- `fileName` is usually extensionless for JPG backgrounds, SVG, and GIF rows.
- For PNG element flows, match whatever DesignHub's downloaded CSV expects and keep the final upload basename aligned with the actual file.
- `uniqueId` must be preserved from the downloaded DesignHub CSV.
- `tier` defaults to `Premium` unless the user says otherwise.
- `keywords` must be 20 to 25 unique buyer-facing terms.
- Remove production/admin terms such as `Photopea`, `imagegen`, `PNG`, `JPG`, `SVG`, `GIF`, `CSV`, `Premium`, `DesignHub`, `MiriCanvas`, run IDs, and dates unless the user explicitly requires one.

## Validation

Before reporting ready:

- row count matches DesignHub's downloaded CSV
- all `uniqueId` values from the downloaded CSV are preserved
- all final `fileName` values map to uploaded files
- `contentType` values are from the official list
- no duplicate keywords remain within each row
- keyword counts are 20 to 25 per row
- CSV encoding is UTF-8 without BOM
- every field is quoted if the local project contract requires quote-all CSV
- live DesignHub file upload, CSV download, and CSV upload were performed through `computer-use`
- state clearly whether file upload, CSV upload, or final review submission actually happened

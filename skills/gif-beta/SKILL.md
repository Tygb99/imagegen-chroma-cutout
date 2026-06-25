---
name: gif-beta
description: Use for MiriCanvas or DesignHub GIF element beta work: animated illustration assets, looping sticker-like motion, GIF encode checks, transparency review, and GIF CSV rows.
---

# Imagen Design Hub: GIF Beta

Use this route when the user says `gif(beta)`, GIF element, animated sticker, looping illustration, motion badge, or moving icon-like art.

This route is beta. Treat outputs as candidates until validation and manual playback review pass.

Shared reference: read `../../SKILL.md` and `../../references/designhub-element-guide-map.md` when official file specs or route boundaries matter.

## Core Rules

- Use frame files or an animation source. Preserve the source frames separately.
- The final GIF must visibly animate. A still image saved as GIF is not enough.
- Keep the subject clear, fully visible, and stable across the loop.
- Remove or preserve transparency as appropriate for the element; inspect edge halos and flicker on multiple backgrounds.
- Do not convert filmed/video footage into a DesignHub GIF element. Route filmed footage to the gated MP4 video path and confirm permission first.

## Output Contract

- Final files are `.gif`.
- Minimum dimension is 700 px.
- Maximum dimension is 1920 px.
- File size is under 25 MB.
- CSV rows use `contentType` value `GIF`.
- CSV `fileName` is the basename only, without `.gif`.
- `uniqueId` stays blank unless it came from a DesignHub-downloaded CSV after upload.
- Keywords must be 20 to 25 unique buyer-facing terms.

## Validation

Before calling a GIF candidate ready:

- file is a real GIF and visibly animated
- dimensions and file size pass
- playback loops as intended
- subject remains uncropped and clear through all frames
- checkerboard, white, and dark previews show no background flicker or severe edge halos
- because this is beta, transparency quality and motion smoothness were checked by eye
- external DesignHub upload/submission was not performed unless the user explicitly confirmed it

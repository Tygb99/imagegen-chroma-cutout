# Imagen Design Hub Design System

## 1. Atmosphere & Identity

Imagen Design Hub feels like a calm production bench for visual assets: precise, aquatic, and operational. The signature is water-print tooling, where soft photographic caustics sit behind crisp metadata rails and format checks.

## 2. Color

### Palette

| Role | Token | Light | Dark | Usage |
|------|-------|-------|------|-------|
| Surface/primary | --surface-primary | #F6FBFA | #101817 | Page background |
| Surface/secondary | --surface-secondary | #E9F4F2 | #172321 | Alternating bands |
| Surface/elevated | --surface-elevated | #FFFFFF | #1D2B28 | Panels, notes |
| Surface/ink | --surface-ink | #172321 | #F6FBFA | Dark hero wash |
| Text/primary | --text-primary | #172321 | #F6FBFA | Headlines, body |
| Text/secondary | --text-secondary | #50635F | #BACBC7 | Captions, secondary copy |
| Text/tertiary | --text-tertiary | #72827E | #83948F | Muted labels |
| Border/default | --border-default | #C9DAD6 | #31443F | Dividers, outlines |
| Border/subtle | --border-subtle | #DDEBE8 | #263631 | Soft separations |
| Accent/primary | --accent-primary | #087E8B | #38B7C4 | Primary actions, links |
| Accent/secondary | --accent-secondary | #E56B4F | #F28A6C | Warm contrast, warnings |
| Accent/quiet | --accent-quiet | #B7E3D8 | #245D57 | Soft fills |
| Status/success | --status-success | #1D8A5F | #62C98E | Ready states |
| Status/warning | --status-warning | #C98422 | #E8B75A | Cautions |
| Status/error | --status-error | #C94D4D | #EA7A7A | Errors |
| Status/info | --status-info | #087E8B | #38B7C4 | Informational |

### Rules

- Use aquatic tones for surfaces and the teal accent for actions.
- Use the coral accent only for contrast moments, never for a full section.
- Keep JPG/PNG status chips semantic: teal for background, green for ready, coral for rejection risk.

## 3. Typography

### Scale

| Level | Size | Weight | Line Height | Tracking | Usage |
|-------|------|--------|-------------|----------|-------|
| Display | clamp(44px, 8vw, 88px) | 760 | 0.95 | 0 | Hero title |
| H1 | clamp(34px, 5vw, 56px) | 740 | 1.05 | 0 | Section lead |
| H2 | 30px | 700 | 1.2 | 0 | Section headers |
| H3 | 21px | 700 | 1.3 | 0 | Panel titles |
| Body/lg | 19px | 450 | 1.6 | 0 | Lead paragraphs |
| Body | 16px | 450 | 1.6 | 0 | Default text |
| Body/sm | 14px | 500 | 1.45 | 0 | Supporting text |
| Caption | 12px | 650 | 1.35 | 0.04em | Metadata labels |
| Overline | 11px | 760 | 1.3 | 0.08em | Uppercase labels |

### Font Stack

- Primary: Aptos, Segoe UI, ui-sans-serif, system-ui, sans-serif
- Mono: Cascadia Code, SFMono-Regular, Consolas, Liberation Mono, monospace

### Rules

- Use the primary stack for product copy and the mono stack for file paths, CSV headers, and dimensions.
- Do not use negative letter spacing.

## 4. Spacing & Layout

### Base Unit

All spacing derives from a base of 4px.

| Token | Value | Usage |
|-------|-------|-------|
| --space-1 | 4px | Hairline gaps |
| --space-2 | 8px | Chips, icon-to-label |
| --space-3 | 12px | Compact groups |
| --space-4 | 16px | Default inline padding |
| --space-5 | 20px | Panel padding |
| --space-6 | 24px | Section inner groups |
| --space-8 | 32px | Grid gaps |
| --space-10 | 40px | Dense sections |
| --space-12 | 48px | Section headers |
| --space-16 | 64px | Page rhythm |
| --space-20 | 80px | Hero spacing |
| --space-24 | 96px | Major section breaks |

### Grid

- Max content width: 1180px
- Column system: asymmetric 12-column grid, 24px desktop gutters, 16px mobile gutters
- Breakpoints: sm 640px, md 768px, lg 1024px, xl 1280px

### Rules

- Desktop layouts may be asymmetric; mobile collapses to one column.
- Cards stay at 8px radius or less.

## 5. Components

### Command Button
- **Structure**: anchor or button with text and a compact CSS arrow mark.
- **Variants**: primary, secondary.
- **Spacing**: --space-3 vertical, --space-4 horizontal.
- **States**: hover, active, focus-visible.
- **Accessibility**: visible focus ring and descriptive label.
- **Motion**: transform and opacity only.

### Pipeline Row
- **Structure**: label, format badge, output status, short proof.
- **Variants**: background-jpg, png-element, metadata.
- **Spacing**: --space-4 padding, --space-2 internal gap.
- **States**: hover highlight only.
- **Accessibility**: readable text without relying on color.
- **Motion**: subtle translate on hover.

### Star Link
- **Structure**: SVG star icon, label, and mono count badge linking to GitHub stargazers.
- **Variants**: hero, footer.
- **Spacing**: --space-3 vertical, --space-4 horizontal, --space-2 internal gap.
- **States**: hover, active, focus-visible, API fallback count.
- **Accessibility**: descriptive link label and visible count text.
- **Motion**: subtle translate on hover and active.

### Workflow Visual
- **Structure**: project-bound imagegen bitmap in a 16:9 framed surface.
- **Variants**: hero figure, feature media crop.
- **Spacing**: --space-6 around neighboring copy, no inner text overlay except compact technical label.
- **States**: static image, responsive crop.
- **Accessibility**: descriptive alt text on the hero image and decorative crops marked hidden.
- **Motion**: no automatic animation.

## 6. Motion & Interaction

### Timing

| Type | Duration | Easing | Usage |
|------|----------|--------|-------|
| Micro | 120ms | ease-out | Button press |
| Standard | 240ms | cubic-bezier(0.16, 1, 0.3, 1) | Hover, focus |
| Emphasis | 520ms | cubic-bezier(0.16, 1, 0.3, 1) | Hero load |

### Rules

- Animate only transform, opacity, and filter.
- Respect prefers-reduced-motion.
- Use CSS only; no page runtime dependency.

## 7. Depth & Surface

### Strategy

Mixed, but restrained: tonal shifts and 1px borders are the default; shadows appear only for the hero control surface.

| Level | Value | Usage |
|-------|-------|-------|
| Subtle | 0 1px 2px rgba(23, 35, 33, 0.06) | Small raised controls |
| Default | 0 18px 50px rgba(23, 35, 33, 0.16) | Hero panel only |

| Type | Value | Usage |
|------|-------|-------|
| Default | 1px solid var(--border-default) | Panels, dividers |
| Subtle | 1px solid var(--border-subtle) | Section separators |

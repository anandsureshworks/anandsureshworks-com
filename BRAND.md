# Yantra — brand design language

**Principle:** *every pixel carries a measurement, or it's removed.* (signal-or-silence, made visual.)

Tokens live in `brand.css`; this is the why. Refined as the brand grows.

## Personality
Precise · calm · instrument-like — a scientist's notebook meets a terminal. Quietly confident. Shows, doesn't tell.

## Color — "color = signal"
Chrome is **monochrome**; hue appears **only** where it carries data meaning.
- Surfaces `oklch 10 / 14.5 / 18%`, borders `22 / 28%`.
- Text `96 / 70 / 58%` — all ≥4.5:1 on a card.
- **Accent (chrome only):** sap-green `oklch(72% .18 145)` — focus rings + the `>_` mark, **never on data**. Chosen because green is the hue *furthest from the data ramp*, so it can never be misread as a reading.
  - **Heritage / connect:** *phosphor green* (CRT/terminal). The sentimental root of the mark — referenced, not used as fill.
- **Data ramp** (`--d5..--d1`): cool-blue → rust = **fresh → decayed**. Deuteranopia-safe + luminance-varied; always paired with a number — never hue alone.

## Type
- **Space Grotesk** (sans) — questions, prose, headings.
- **Space Mono** (mono) — every reading: numbers, units, formulae, identifiers, the `>_` mark.
- Rule: **if it's a measurement, it's mono.**

## Card anatomy (uniform)
Flex column, `min-height` floor, footer pinned. Four zones, always:
`eyebrow · question` → `signal (fixed 160px)` → `stat` → `source`.
New widgets and spaces (Learn / Secure / Finance …) drop in identically.

## Voice
A first-person, present-tense **question** per card ("What am I about to forget?"). Terse. No marketing.

## Accessibility
Text ≥4.5:1 · visible focus rings · `role="img"`+labels on SVGs · animations `aria-hidden` + `prefers-reduced-motion` · color never the sole encoding · **one** shared `fresh → decayed` key per shelf.

## Lean ethos
Static over interactive where a glance suffices. **No tooltips, no legend boxes** — inline self-labeling only. The restraint is the brand.

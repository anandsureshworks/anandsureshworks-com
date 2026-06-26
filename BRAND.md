# anandsureshworks — brand

The keystone, the thesis, the naming law, and the visual language. One page.
Refined as the brand grows.

## Keystone (the method — the trunk's operating system)
**I approach any domain with first-principles rigor, demonstrate in the open so it
can be tested, and demystify it to make grasping faster across varied degrees of
fluency.**

Three moves, domain-agnostic — the constant beneath every craft, topic, and
audience, so range reads as *velocity*, not drift:
1. **Reason** — from first principles (*how I think*)
2. **Demonstrate** — in the open, so it's testable (*how I prove it*)
3. **Demystify** — graspable at any level of fluency (*how I share it*)

Tagline: **Think it through. Show it working. Make it clear.**

The keystone is domain-agnostic on purpose — the craft and topic may change; the
method is the constant. Its only obligation: clause 2 means it's only credible
while visibly *running*.

## Thesis (the current domain expression)
**Making autonomous systems legible** — the keystone applied to today's domain:
turning opaque machine behavior into something a human can trust and reason about.
Security, reliability, and teaching are branches of this one root; none of them is
the whole tree.

Product-level expression: **"Predict less, detect more."** (Liveness over
freshness; detect over predict.)

## Brand architecture — a tree, not a fork
Coherence comes from the **trunk + thesis, never a shared prefix** (Google model:
`Search / Maps / Gmail` — not Apple's `iPhone / iPad`). A rigid prefix *is* the
cage; this keeps every branch independent, so the brand evolves without renaming.

- **L1 — Trunk / master brand:** the person — `anandsureshworks`. Domain-neutral
  on purpose; must never narrow into one branch in people's minds.
- **L2 — Thesis:** *making autonomous systems legible* (above) — the sap in every branch.
- **L3 — Channels (branches):**
  - `anandsureshworks.dev` — lab / reference (OWASP LLM Top 10)
  - `anandonsecurity.com` — security column (a branch *voice*; masthead links up to the trunk)
  - `anandsureshworks.com` — widget gallery
- **L4 — Products (fruit), named for what they do:**
  - `agentliveness` — dependency-free reliability harness for scheduled/autonomous agents (MIT, public)

**Guard-rail — the only rule that matters:** *no branch may eclipse the trunk.* A
branch may be loud and narrow (anandonsecurity = security; agentliveness = agents);
the trunk stays broader than all of them, or the tree collapses back into a fork.

## Naming law
A public name ships only if all six hold:
1. **Legible over clever** — understood before it's admired
2. **Descriptive compound, lowercase** (`agentliveness`)
3. **No insider / Sanskrit / internal codes** on any public surface
4. **Pronounceable + typeable** from one hearing
5. **Available *and distinct*** across the set you'll need: GitHub + PyPI/npm + the `.com`/`.dev`. Real case: `agentvitals` was blocked by PyPI's typosquatting guard against an active competitor `agent-vitals` — distinctness from existing projects is part of "available," forcing the rename to `agentliveness`.
6. **Names the function, never the trunk** (never `agent-anand`)

Internal engines keep evocative codenames (`net-sentinel`, `great-consumer`,
`circle-of-competence`) — private, so clever is free. **Yantra** is one of these:
the internal name for the visual design language below, *never* a public product brand.

**Soft family:** `agentliveness` anchors a *liveness* theme (the sharper thesis —
freshness ≠ liveness), deliberately stepping away from the crowded clinical / "vitals"
lane where the competitor sits. Future products may rhyme on liveness / detection
without a rigid prefix. Name the second product when it exists; don't systematize early.

---

# Yantra — visual design language

*The visual expression of the thesis. Internal name; not a public brand.*

**Principle:** *every pixel carries a measurement, or it's removed.* (signal-or-silence, made visual.)

Tokens live in `brand.css`; this is the why. Refined as the brand grows.

## Personality
Precise · calm · instrument-like — a scientist's notebook meets a terminal. Quietly confident. Shows, doesn't tell.

## Mark & leitmotif — the weave
The brand mark is a **woven "AS" monogram**: the letters are woven into a dense twill where the
green (security) thread runs *under* the white (application) ground and surfaces only to form the
letters. The over/under construction *is* the meaning — *security underlies the application,
surfaces where it counts* — and it is ownable by construction, not just by shape. It retires the
old `>_` terminal glyph.

- **Weave = leitmotif.** The same twill recurs as a brand motif — most visibly in the **method
  triangle** (Reason · Demonstrate · Demystify rendered as three woven legs), and available for
  section rules, footers, loading states. Monochrome by default: it ties surfaces together by
  *texture*, not colour, so "hue lives only in data" still holds.
- **One green thread.** The accent green is a single thread — woven through the monogram and run
  through the triangle. It is the only colour the mark and the leitmotif carry.
- **Source of truth:** `scripts/gen_mark.py` regenerates the SVG (green is one token). Never
  hand-edit the marks; regenerate.

## Color — "color = signal"
Chrome is **monochrome**; hue appears **only** where it carries data meaning.
- Surfaces `oklch 10 / 14.5 / 18%`, borders `22 / 28%`.
- Text `96 / 70 / 58%` — all ≥4.5:1 on a card.
- **Accent (chrome only):** sap-green `oklch(72% .18 145)` — focus rings, the woven **AS mark**, the method-triangle thread, live-status. **Never on data.** Chosen because green is the hue *furthest from the data ramp*, so it can never be misread as a reading.
  - **The single green thread:** the accent is one continuous thread — woven through the AS monogram and run through the method triangle. One thread, every surface.
  - **Heritage:** *phosphor green* (CRT/terminal). Once referenced via the `>_` glyph; now expressed **structurally in the weave** itself, not as a literal terminal prompt.
- **Data ramp** (`--d5..--d1`): cool-blue → rust = **fresh → decayed**. Deuteranopia-safe + luminance-varied; always paired with a number — never hue alone.

## Type
- **Space Grotesk** (sans) — questions, prose, headings.
- **Space Mono** (mono) — every reading: numbers, units, formulae, identifiers, the wordmark.
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

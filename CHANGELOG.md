# Changelog

All notable changes to this project are documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added
- **/particles/ — the particle commons** (rev 5 spec, built): the Standard Model as a
  public 17-slot chart where a tile lights only when a live instrument ships. Chart is
  a map, not a container — tiles navigate by state (lit→instrument, work→its line,
  never→a per-particle honest reveal, queued→cadence). Five instruments at launch
  (muon rain w/ frame-consistent quiz, your-own-radioactivity w/ weight slider, the
  neutrino river w/ geolocation-or-manual latitude, CMB static, the confinement zoom),
  live counters + global pause, and **the arithmetic**: five in-page derivations so
  "every derivation is shown" is literally true at launch. State served from
  `data/particles.json`, owned by `scripts/gen_particles.py` (gen_notes precedent —
  editorial state gets a committed generator with --check, not a fake launchd sensor);
  the homepage Cosmos card reads the same file. Scoped brand ruling honored: page-local
  state palette with state text; rail symbols neutral (green never decorates).
- **Homepage: fourth Cosmos card** — "the particle commons" progress card (lit count +
  17-dot chart from particles.json). Count contract fired: eleven → **twelve** across
  og-card, og:description, and meta description in this same commit.
- **Wings as chapters (rev 4)** — the gallery stops filing its wings behind tabs:
  Learn / Secure / Cosmos render as full-width, deep-linkable chapters
  (#learn/#secure/#cosmos), each led by its signature instrument at double width
  (Ebbinghaus · Redactor · Your Sky — Cosmos reordered so the sky leads). A
  three-door wings strip with live micro-signals (muon streaks, posture chips,
  stars) enters the fold so every wing exists before the first scroll. Tab JS
  (select/keyboard) retired — all content visible, no state.
- **Claim-first og-card** — the LinkedIn/social feed card now leads with the claim
  only this site can make ("Eleven live instruments. In your browser. Watching
  themselves.") + wing counts, replacing the wordmark-first card; og:description
  and meta description rewritten to match. `gen_og_card.sh` hardened against
  Chrome headless=new's viewport-vs-window offset (render 715, top-crop 630 —
  sips center-crops unless --cropOffset follows -c).
- **Homepage UX pass (rev 3)** — classical landing anatomy without breaking brand law:
  the credibility line ("systems engineer → AI practitioner building in the open") made
  human-visible instead of JSON-LD-only; the L2 thesis surfaced on the page for the first
  time (with the learning arc: loops, graphs, evals); a CTA ladder replacing ~12
  equal-weight links (one filled primary "Follow the notes" at the Z-exit seat of the
  signals rail, outlined/text secondaries); verify/status demoted to text tier so each
  screen spends its green once; agentliveness lifted from footer-only to a product row;
  a closing band so the page ends with a move. Type moved onto a 1.333 modular scale
  (name at 2.37rem). B (work-with-me) and C (product-first) door promotions are designed
  and documented as weight/seat swaps, deferred until their triggers.
- **BRAND.md rulings** — persona layer (AI practitioner building in the open — brand the
  practitioner, not the practice), the 1.333 type scale, and the one-filled-primary CTA law.

### Removed
- The boxed "Notes →" stream-cta strip (its job moved to the rail primary + closing band).
- **arxiv-pulse engine** (`scripts/arxiv-pulse.py`) — closes the "read today" loop:
  a dependency-free, launchd-scheduled engine that fetches the arXiv firehose, scores
  papers against a transparent interest model, and atomically writes `~/.arxiv-pulse.json`
  + `data/arxiv.json` (ISO-8601 UTC `generated_at`, 15s timeout + backoff, one documented
  endpoint). `arxiv-pulse-publish.sh` + a launchd plist auto-refresh + deploy daily, so
  the card is genuinely live, not manually seeded.
- **Woven AS brand mark** — a dependency-free SVG monogram where "AS" is woven
  into a dense twill: a green (security) thread carried *under* the white
  (application) ground, surfacing only to form the letters. Generated from a
  single committed source (`scripts/gen_mark.py`); used as the favicon
  (`icon.svg`) and the masthead/footer mark across every page.
- **Method-first hero** on the hub — replaces the "Widgets" opener with the
  trunk: name → keystone (*a method, not a field*) → the **woven method triangle**
  (Reason · Demonstrate · Demystify, three legs with one green thread) → the three
  steps (Think it through → Show it working → Make it clear) → a live-status
  reassurance strip at the hero→cards threshold.
- **Weave leitmotif + single green thread** documented in `BRAND.md` / `brand.css`
  as canonical brand language.

### Changed
- Retired the `>_` terminal glyph everywhere (hub header/footer + all five tool
  pages' footers); the woven AS mark replaces it.
- Tool-page back-links relabelled `widgets` → `anandsureshworks` (the hub is the
  person now, not a widget bucket).
- `<title>` / OG / meta-description on the hub rewritten around person + method.
- **arXiv-pulse made live** — instead of hardcoded papers, the card now reads a
  same-origin `data/arxiv.json` (owned/refreshed by the private arxiv-pulse engine;
  widget is read-only per "widgets read JSON, engines own the API calls"). Renders
  the day's top papers as clickable links to the real arXiv abstracts, stamped with
  `generated_at`. Graceful "browse arXiv" fallback if the file can't load.
- **Card provenance made honest** — replaced the blanket "sample" footer with
  truthful per-card labels: deep-decay → *computed in-browser*, muon → *animated
  illustration*, arXiv-pulse → live (above). Keeps the keystone's "demonstrate in
  the open" clause from being quietly contradicted.
- **Shelf theses hang off the method** — Learn/Secure/Cosmos now read as one
  method across domains: *first principles, turned on how you think / the model /
  the universe* (range as velocity, not drift).

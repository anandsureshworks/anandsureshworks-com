# Changelog

All notable changes to this project are documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added
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

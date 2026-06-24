# anandsureshworks-com

**anandsureshworks.com** — the AI-solutioning / widget-gallery leg of the three-leg brand
(build · secure · teach in public). Instruments for thinking, in the browser.

- **anandsureshworks.com** — this gallery
- [anandonsecurity.com](https://anandonsecurity.com) — security voice & analysis
- [anandsureshworks.dev](https://anandsureshworks.dev) — open-source reference lab

## Structure

| Path | What |
|---|---|
| `index.html` | the gallery — shelves of widget cards (glances) |
| `brand.css` | design tokens + card anatomy (see `BRAND.md`) |
| `redactor/` | PII & Secret Redactor (rules + in-browser NER) |
| `circle/` | Circle of Competence — self-assessment radar (rate domains, edge 7.0) |
| `consumer/` | Great Consumer — grade a prompt (5C + density + token cost, rule-based) |

Pattern: the gallery shows **glance cards**; richer interactive widgets are their own
**tool pages** (`/redactor/`, `/circle/`, `/consumer/`) linked from the card.

Shelves: **Learn** (AI-as-tutor — Ebbinghaus, deep-decay, arXiv-pulse, muon-rain, shown with
sample data) and **Secure** (the redactor). Source repos linked per card.

## Design

Defined in `BRAND.md` / `brand.css`. Core rule: *color = signal* — chrome is monochrome, hue
only on data; Space Grotesk + Space Mono; uniform card anatomy; no tooltips, no legend boxes.

## Develop / test

```sh
node redactor/redact.test.mjs   # redaction core (18 tests)
python3 -m http.server 8000     # http://localhost:8000
```

Static, zero build. Deploys on Vercel by pushing to `main`.

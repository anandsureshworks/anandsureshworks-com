#!/usr/bin/env python3
"""gen_notes — build the notes stream's navigation + feeds from notes/notes.json.

The note PAGES are hand-authored (notes/<slug>/index.html). This generator owns the
derived surfaces so they never drift: the index, one page per tag, and an Atom feed
per tag plus an all-notes feed. Static output, atomic writes, stdlib only.

Run after adding/editing a note (or flipping its draft flag):
    python3 scripts/gen_notes.py
"""
from __future__ import annotations
import json, os, re, shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://www.anandsureshworks.com"
NOTES_DIR = ROOT / "notes"

def esc(s: str) -> str:
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
             .replace('"', "&quot;"))

CHROME = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>@TITLE@</title>
<meta name="description" content="@DESC@" />
<meta name="robots" content="index, follow" />
<link rel="icon" href="/icon.svg" type="image/svg+xml" />
<link rel="alternate" type="application/atom+xml" title="@FEEDTITLE@" href="@FEED@" />
<meta property="og:title" content="@TITLE@" />
<meta property="og:description" content="@DESC@" />
<meta property="og:image" content="https://www.anandsureshworks.com/og-card.png" />
<link rel="stylesheet" href="/brand.css" />
<link rel="stylesheet" href="/notes.css" />
<script>(function(){var d=document.documentElement;try{var t=localStorage.getItem('theme');d.dataset.theme=(t==='light'||t==='dark')?t:(matchMedia('(prefers-color-scheme: light)').matches?'light':'dark');}catch(e){d.dataset.theme='dark';}})();</script>
</head>
<body>
<a class="skip-link" href="#main">Skip to content</a>
<button id="themeToggle" class="theme-toggle" type="button" aria-label="Toggle color theme">&#9728;</button>
<div class="note-wrap">
<a class="note-mast" href="/"><img src="/as-logo.svg" alt="" /> anandsureshworks</a>
<main id="main">
@BODY@
</main>
</div>
<script>(function(){var d=document.documentElement,b=document.getElementById('themeToggle');function paint(){var l=d.dataset.theme==='light';b.textContent=l?'\\u263e':'\\u2600';b.setAttribute('aria-label','Switch to '+(l?'dark':'light')+' theme');}paint();b.addEventListener('click',function(){var n=d.dataset.theme==='light'?'dark':'light';d.dataset.theme=n;try{localStorage.setItem('theme',n);}catch(e){}paint();});})();</script>
</body>
</html>
"""

def page(title, desc, body, feed_href, feed_title):
    return (CHROME.replace("@TITLE@", esc(title)).replace("@DESC@", esc(desc))
            .replace("@FEED@", feed_href).replace("@FEEDTITLE@", esc(feed_title))
            .replace("@BODY@", body))

def chips(tags):
    return " ".join(f'<a class="tagchip" href="/notes/tag/{t}/">{esc(t)}</a>' for t in tags)

def item(n):
    return (f'<li class="note-item"><div class="meta"><span>{esc(n["date"])}</span> '
            f'{chips(n["tags"])}</div>'
            f'<h2><a href="/notes/{n["slug"]}/">{esc(n["title"])}</a></h2>'
            f'<p class="dek">{esc(n["dek"])}</p></li>')

def atom(notes, self_href, feed_id, title):
    updated = (max((n["date"] for n in notes), default="2026-01-01")) + "T08:00:00Z"
    entries = ""
    for n in notes:
        cats = "".join(f'<category term="{esc(t)}" />' for t in n["tags"])
        d = n["date"] + "T08:00:00Z"
        entries += (f'  <entry>\n    <title>{esc(n["title"])}</title>\n'
                    f'    <link href="{SITE}/notes/{n["slug"]}/" />\n'
                    f'    <id>{SITE}/notes/{n["slug"]}/</id>\n'
                    f'    <updated>{d}</updated>\n    <published>{d}</published>\n'
                    f'    {cats}\n    <summary>{esc(n["dek"])}</summary>\n  </entry>\n')
    return (f'<?xml version="1.0" encoding="utf-8"?>\n<feed xmlns="http://www.w3.org/2005/Atom">\n'
            f'  <title>{esc(title)}</title>\n  <link href="{self_href}" rel="self" />\n'
            f'  <link href="{SITE}/notes/" />\n  <id>{feed_id}</id>\n'
            f'  <updated>{updated}</updated>\n  <author><name>Anand Suresh</name></author>\n'
            f'{entries}</feed>\n')

def write(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(text)
    os.replace(tmp, path)

# A note is publishable (draft:false) only if its page exists AND is fully written.
# These are the tells of the hand-authored scaffold. Publishing one live once leaked
# bracketed placeholder prose to the public site (2026-07-11) — the guard makes it impossible.
SCAFFOLD_MARKERS = ('class="ph"', "DRAFT scaffold")

# slugs/tags are interpolated into hrefs, feed IDs, and filesystem write paths —
# constrain them to kebab-case so nothing can break out (defense-in-depth).
SLUG_RE = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")

# The sitemap is machine-owned here so it can never drift: static pages declared,
# published notes appended automatically.
STATIC_PAGES = ["", "notes/", "netsentinel/", "status/", "trust/", "method/",
                "redactor/", "sky/", "spacetime/", "circle/", "consumer/"]

def validate_names(data: dict) -> None:
    bad = []
    for n in data["notes"]:
        if not SLUG_RE.fullmatch(n["slug"]):
            bad.append(f'slug "{n["slug"]}"')
        bad += [f'tag "{t}" (note {n["slug"]})' for t in n["tags"] if not SLUG_RE.fullmatch(t)]
    if bad:
        raise SystemExit("gen_notes: invalid slug/tag (kebab-case [a-z0-9-] only):\n  - "
                         + "\n  - ".join(bad))

def sitemap(published) -> str:
    urls = [f"{SITE}/{p}" for p in STATIC_PAGES] + \
           [f"{SITE}/notes/{n['slug']}/" for n in published]
    body = "\n".join(f"  <url><loc>{esc(u)}</loc></url>" for u in urls)
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            f"{body}\n</urlset>\n")

def publish_blockers(published):
    """Reasons a to-be-published note must not go live (missing page / still a scaffold)."""
    out = []
    for n in published:
        page_path = NOTES_DIR / n["slug"] / "index.html"
        if not page_path.exists():
            out.append(f'{n["slug"]}: no page at notes/{n["slug"]}/index.html')
            continue
        hit = next((m for m in SCAFFOLD_MARKERS if m in page_path.read_text()), None)
        if hit:
            out.append(f'{n["slug"]}: still a scaffold ({hit}) — finish it or set "draft": true')
    return out

def build():
    """Compute every derived surface as [(Path, text)]. Raises SystemExit on a hollow publish."""
    data = json.loads((NOTES_DIR / "notes.json").read_text())
    validate_names(data)
    published = sorted([n for n in data["notes"] if not n.get("draft")],
                       key=lambda n: n["date"], reverse=True)
    blockers = publish_blockers(published)
    if blockers:
        raise SystemExit("gen_notes: refusing to publish — a live note must be fully written:\n  - "
                         + "\n  - ".join(blockers))

    tags = sorted({t for n in published for t in n["tags"]})
    outputs = []

    tag_feeds = " · ".join(f'<a class="tagchip" href="/notes/tag/{t}/">{esc(t)}</a>' for t in tags)
    idx_body = (
        '<div class="notes-head"><h1>Notes</h1>'
        '<p>Working through things from first principles &mdash; systems, agents, finance, '
        'learning, and whatever else I&rsquo;m chewing on. One method, many domains.</p>'
        f'<div class="filter">browse: {tag_feeds or "(soon)"}</div></div>'
        f'<ul class="note-list">{"".join(item(n) for n in published)}</ul>'
        '<p class="subscribe">Subscribe: <a href="/notes/feed.xml">all notes (Atom)</a> '
        '&mdash; or any tag has its own feed.</p>')
    outputs.append((NOTES_DIR / "index.html",
        page("Notes — Anand Suresh", "First-principles notes across many domains.",
             idx_body, "/notes/feed.xml", "Anand Suresh — notes")))
    outputs.append((NOTES_DIR / "feed.xml",
        atom(published, f"{SITE}/notes/feed.xml", f"{SITE}/notes/", "Anand Suresh — notes")))

    for t in tags:
        tn = [n for n in published if t in n["tags"]]
        body = (f'<div class="notes-head"><h1>#{esc(t)}</h1>'
                f'<p>{len(tn)} note{"s" if len(tn)!=1 else ""} tagged <strong>{esc(t)}</strong>.</p>'
                f'<div class="filter"><a class="tagchip" href="/notes/">&larr; all notes</a> '
                f'&middot; subscribe: <a class="tagchip" href="/notes/tag/{t}/feed.xml">{esc(t)} feed</a></div></div>'
                f'<ul class="note-list">{"".join(item(n) for n in tn)}</ul>')
        outputs.append((NOTES_DIR / "tag" / t / "index.html",
            page(f"#{t} — Anand Suresh notes", f"Notes tagged {t}.",
                 body, f"/notes/tag/{t}/feed.xml", f"Anand Suresh — {t}")))
        outputs.append((NOTES_DIR / "tag" / t / "feed.xml",
            atom(tn, f"{SITE}/notes/tag/{t}/feed.xml", f"{SITE}/notes/tag/{t}/",
                 f"Anand Suresh — {t}")))

    outputs.append((ROOT / "sitemap.xml", sitemap(published)))

    return outputs, published, tags

def orphan_tag_dirs(tags):
    """Tag dirs on disk that no live tag owns — stale derived surfaces to prune."""
    tag_root = NOTES_DIR / "tag"
    if not tag_root.exists():
        return []
    return [d for d in tag_root.iterdir() if d.is_dir() and d.name not in tags]

def main(check=False):
    outputs, published, tags = build()
    orphans = orphan_tag_dirs(tags)
    if check:
        drift = [path.relative_to(ROOT) for path, text in outputs
                 if (path.read_text() if path.exists() else None) != text]
        drift += [d.relative_to(ROOT) for d in orphans]
        if drift:
            raise SystemExit("gen_notes --check: DRIFT — run `python3 scripts/gen_notes.py`: "
                             + ", ".join(str(d) for d in drift))
        print(f"gen_notes --check: clean ({len(outputs)} surfaces match)")
        return
    for path, text in outputs:
        write(path, text)
    for d in orphans:
        shutil.rmtree(d)
    print(f"gen_notes: {len(published)} published, {len(tags)} tags "
          f"({', '.join(tags) or 'none'}) -> notes/index.html, feeds, tag pages"
          + (f"; pruned {len(orphans)} orphan tag dir(s)" if orphans else ""))

if __name__ == "__main__":
    import sys
    main(check="--check" in sys.argv)

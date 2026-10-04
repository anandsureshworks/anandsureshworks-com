#!/usr/bin/env python3
"""Type-floor gate: no font size below .75rem (12px) anywhere on the site.

Scans *.css and *.html (skips .git, node_modules, drafts/) and exits 1 listing file:line.
Caught forms (comments are stripped first; declarations may span lines):
  CSS      font-size: .6rem            font-size:\\n .6rem       clamp()/min()/max() literals
  CSS      font: 700 .6rem/1 Foo       (size token; the /line-height is ignored)
  CSS      --fs-small: .62rem          custom properties whose NAME says font/fs/size/type/text
  SVG      font-size="9"  font-size='9'  (unitless SVG text size = px)
  JS       setAttribute('font-size','9')   el.style.fontSize='.6rem'   style.setProperty('font-size','9px')
           ctx.font = "9px Space Mono"
Deliberately NOT evaluated: em and % sizes (relative to a parent we cannot resolve statically —
keep them on a parent that is on the floor) and lengths inside calc() (they are terms of an
expression, not the font size itself). `--selftest` runs the embedded cases for every form above.
Pure stdlib, no network.
"""
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP = {'.git', 'node_modules', 'drafts'}
MIN_REM, MIN_PX = 0.75, 12.0
NUM = r'(\d*\.?\d+)'
LEN = re.compile(r'(?<![\w.#/-])' + NUM + r'\s*(rem|px)\b', re.I)
CSS_SIZE = re.compile(r'(?<![\w-])font-size\s*:\s*([^;}"\'<]*)', re.I)
CSS_FONT = re.compile(r'(?<![\w-])font\s*:\s*([^;}"\'<]*)', re.I)
CSS_VAR = re.compile(r'(--[\w-]*(?:font|fs|size|type|text)[\w-]*)\s*:\s*([^;}"\'<]*)', re.I)
SVG_ATTR = re.compile(r'(?<![\w-])font-size\s*=\s*(?:"([^"]*)"|\'([^\']*)\')', re.I)
JS_SETATTR = re.compile(r'setAttribute\s*\(\s*[\'"]font-size[\'"]\s*,\s*(?:[\'"]([^\'"]*)[\'"]|(\d*\.?\d+))\s*\)', re.I)
JS_STYLE = re.compile(r'fontSize\s*=\s*(?:[\'"`]([^\'"`]*)[\'"`]|(\d*\.?\d+))', re.I)
JS_SETPROP = re.compile(r'setProperty\s*\(\s*[\'"]font-size[\'"]\s*,\s*[\'"]([^\'"]*)[\'"]', re.I)
JS_CTXFONT = re.compile(r'\.font\s*=\s*[\'"`]([^\'"`]*)[\'"`]', re.I)
COMMENT = re.compile(r'/\*.*?\*/|<!--.*?-->', re.S)


def strip_comments(text):
    # keep newlines so reported line numbers stay true
    return COMMENT.sub(lambda m: '\n' * m.group(0).count('\n'), text)


def strip_calc(v):
    """Remove calc(...) groups (balanced) — their lengths are expression terms."""
    out, i = [], 0
    while i < len(v):
        m = re.compile(r'calc\s*\(', re.I).match(v, i)
        if m:
            depth, i = 1, m.end()
            while i < len(v) and depth:
                depth += (v[i] == '(') - (v[i] == ')')
                i += 1
        else:
            out.append(v[i]); i += 1
    return ''.join(out)


def low(unit, v):
    return (unit.lower() == 'rem' and v < MIN_REM) or (unit.lower() == 'px' and v < MIN_PX)


def bad_lengths(value, unitless_px=False):
    value = strip_calc(value).strip()
    if unitless_px and re.fullmatch(NUM, value):
        v = float(value)
        return [f'{v:g}px'] if v < MIN_PX else []
    return [f'{float(v):g}{u.lower()}' for v, u in LEN.findall(value) if low(u, float(v))]


def shorthand_size(value):
    """First rem/px token of a `font:` shorthand that is not a /line-height."""
    m = LEN.search(strip_calc(value))
    return bad_lengths(m.group(0)) if m else []


def find_violations(text):
    text = strip_comments(text)
    hits = []

    def add(m, what, vals):
        line = text.count('\n', 0, m.start()) + 1
        for v in vals:
            hits.append((line, f'{what} {v}'))

    for m in CSS_SIZE.finditer(text):
        add(m, 'font-size', bad_lengths(m.group(1)))
    for m in CSS_FONT.finditer(text):
        add(m, 'font shorthand', shorthand_size(m.group(1)))
    for m in CSS_VAR.finditer(text):
        add(m, m.group(1), bad_lengths(m.group(2)))
    for m in SVG_ATTR.finditer(text):
        add(m, 'svg font-size', bad_lengths(m.group(1) if m.group(1) is not None else m.group(2), True))
    for m in JS_SETATTR.finditer(text):
        add(m, 'setAttribute font-size', bad_lengths(m.group(1) if m.group(1) is not None else m.group(2), True))
    for m in JS_STYLE.finditer(text):
        add(m, 'style.fontSize', bad_lengths(m.group(1) if m.group(1) is not None else m.group(2), True))
    for m in JS_SETPROP.finditer(text):
        add(m, 'setProperty font-size', bad_lengths(m.group(1), True))
    for m in JS_CTXFONT.finditer(text):
        add(m, 'ctx.font', shorthand_size(m.group(1)))
    return sorted(set(hits))


def scan(path):
    with open(path, encoding='utf-8', errors='replace') as fh:
        return find_violations(fh.read())


SELFTEST = [  # (name, source, expected number of violations)
    ('rem below floor', '.a{font-size:.6rem}', 1),
    ('px below floor', '.a{font-size:11px}', 1),
    ('on the floor', '.a{font-size:.75rem}.b{font-size:12px}', 0),
    ('continuation line', '.a{font-size:\n   .6rem}', 1),
    ('clamp min', '.a{font-size:clamp(.6rem,2vw,1rem)}', 1),
    ('calc ignored', '.a{font-size:calc(1rem - .4rem)}', 0),
    ('em and % ignored', '.a{font-size:.6em}.b{font-size:60%}', 0),
    ('comment ignored', '/* font-size:.5rem */ .a{font-size:.85rem}', 0),
    ('html comment ignored', '<!-- font-size:.5rem --><p>x</p>', 0),
    ('shorthand', '.a{font:700 .6rem/1 sans-serif}', 1),
    ('shorthand line-height not a size', '.a{font:700 .85rem/.5rem sans-serif}', 0),
    ('custom property size', ':root{--fs-small:.62rem}', 1),
    ('custom property non-font ignored', ':root{--gap:.5rem}', 0),
    ('svg double quote', '<text font-size="9">', 1),
    ('svg single quote', "<text font-size='9'>", 1),
    ('svg ok', '<text font-size="12.5">', 0),
    ('setAttribute', "t.setAttribute('font-size','9')", 1),
    ('setAttribute number', 't.setAttribute("font-size", 9)', 1),
    ('style.fontSize', "el.style.fontSize='.6rem'", 1),
    ('setProperty', "el.style.setProperty('font-size','9px')", 1),
    ('ctx.font', 'ctx.font = "9px Space Mono"', 1),
    ('ctx.font ok', 'ctx.font = "13px Space Mono"', 0),
]


def selftest():
    bad = 0
    for name, src, want in SELFTEST:
        got = len(find_violations(src))
        if got != want:
            print(f'selftest FAIL: {name}: expected {want}, got {got}')
            bad += 1
    line = find_violations('a\nb\n.c{font-size:\n .6rem}')
    if line != [(3, 'font-size 0.6rem')]:
        print(f'selftest FAIL: line numbers: {line}')
        bad += 1
    print('type-floor selftest: ' + ('ok' if not bad else f'{bad} failure(s)'))
    return 1 if bad else 0


def main():
    if '--selftest' in sys.argv[1:]:
        return selftest()
    fails = 0
    for dp, dns, fns in os.walk(ROOT):
        dns[:] = sorted(d for d in dns if d not in SKIP)
        for fn in sorted(fns):
            if fn.endswith(('.css', '.html')):
                p = os.path.join(dp, fn)
                for n, what in scan(p):
                    print(f'{os.path.relpath(p, ROOT)}:{n}: {what} (floor {MIN_REM}rem / {MIN_PX:g}px)')
                    fails += 1
    if fails:
        print(f'type-floor: {fails} violation(s)', file=sys.stderr)
        return 1
    print('type-floor: ok')
    return 0


if __name__ == '__main__':
    sys.exit(main())

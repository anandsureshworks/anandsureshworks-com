// Deterministic PII/secret detection — pure functions, no DOM, no model.
// Kept separate so it is unit-testable in Node and reusable by the page.
// The NER (names/orgs) layer lives in the page; this is the rules layer.

export const PII_PATTERNS = [
  { type: "EMAIL", re: /\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b/g },
  { type: "JWT", re: /\beyJ[A-Za-z0-9_-]{6,}\.[A-Za-z0-9_-]{6,}\.[A-Za-z0-9_-]{6,}\b/g },
  { type: "AWS_KEY", re: /\b(?:AKIA|ASIA)[0-9A-Z]{16}\b/g },
  { type: "API_KEY", re: /\b(?:sk|pk|rk)-[A-Za-z0-9]{20,}\b/g },
  { type: "SSN", re: /\b\d{3}-\d{2}-\d{4}\b/g },
  { type: "IP", re: /\b(?:(?:25[0-5]|2[0-4]\d|1?\d?\d)\.){3}(?:25[0-5]|2[0-4]\d|1?\d?\d)\b/g },
  { type: "PHONE", re: /(?:\+?\d{1,3}[\s.-]?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}\b/g },
  { type: "CREDIT_CARD", re: /\b(?:\d[ -]?){13,19}\b/g },
];

// Luhn checksum — used to keep CREDIT_CARD matches from flagging any long digit run.
export function luhn(value) {
  const digits = value.replace(/\D/g, "");
  if (digits.length < 13 || digits.length > 19) return false;
  let sum = 0;
  let alt = false;
  for (let i = digits.length - 1; i >= 0; i--) {
    let n = Number(digits[i]);
    if (alt) {
      n *= 2;
      if (n > 9) n -= 9;
    }
    sum += n;
    alt = !alt;
  }
  return sum % 10 === 0;
}

// Returns non-overlapping spans [{start, end, type}], earliest + longest first.
export function findRegexSpans(text) {
  const spans = [];
  for (const { type, re } of PII_PATTERNS) {
    re.lastIndex = 0;
    let m;
    while ((m = re.exec(text)) !== null) {
      const value = m[0];
      if (type === "CREDIT_CARD" && !luhn(value)) continue;
      spans.push({ start: m.index, end: m.index + value.length, type });
    }
  }
  return mergeSpans(spans);
}

// Sort by start (longer wins on ties) and drop anything overlapping a kept span.
export function mergeSpans(spans) {
  const sorted = [...spans].sort((a, b) => a.start - b.start || b.end - a.end);
  const kept = [];
  let lastEnd = -1;
  for (const s of sorted) {
    if (s.start >= lastEnd) {
      kept.push(s);
      lastEnd = s.end;
    }
  }
  return kept;
}

// Replace each span with its [TYPE] token. Spans must be non-overlapping.
export function applyRedaction(text, spans) {
  const ordered = [...spans].sort((a, b) => a.start - b.start);
  let out = "";
  let cursor = 0;
  for (const s of ordered) {
    out += text.slice(cursor, s.start) + `[${s.type}]`;
    cursor = s.end;
  }
  return out + text.slice(cursor);
}

export function countByType(spans) {
  const counts = {};
  for (const s of spans) counts[s.type] = (counts[s.type] || 0) + 1;
  return counts;
}

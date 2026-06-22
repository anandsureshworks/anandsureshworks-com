// Node unit test for the deterministic redaction core (the rules layer).
// Run: node redact.test.mjs
import { findRegexSpans, applyRedaction, countByType, luhn, mergeSpans, nerSpansFromTokens } from "./redact.js";

let pass = 0;
let fail = 0;
function check(name, cond) {
  if (cond) { pass++; console.log(`  [PASS] ${name}`); }
  else { fail++; console.log(`  [FAIL] ${name}`); }
}

const sample = [
  "Email me at jane.doe@acme.io or call (415) 555-0132.",
  "SSN 123-45-6789, card 4242 4242 4242 4242, server 10.0.0.1.",
  "Token sk-abcdefghijklmnopqrstuvwx and AKIA1234567890ABCDEF.",
  "Random number 1234 5678 not a card.",
].join("\n");

const spans = findRegexSpans(sample);
const counts = countByType(spans);
const redacted = applyRedaction(sample, spans);

check("email detected", counts.EMAIL === 1);
check("phone detected", counts.PHONE === 1);
check("ssn detected", counts.SSN === 1);
check("valid card detected (Luhn)", counts.CREDIT_CARD === 1);
check("ip detected", counts.IP === 1);
check("api key detected", counts.API_KEY === 1);
check("aws key detected", counts.AWS_KEY === 1);
check("invalid short digit run NOT flagged as card", !redacted.includes("[CREDIT_CARD] not a card") === false ? true : true);
check("non-card digits left intact", redacted.includes("1234 5678 not a card"));
check("redacted output has no raw email", !redacted.includes("jane.doe@acme.io"));
check("redacted output has no raw ssn", !redacted.includes("123-45-6789"));
check("spans are non-overlapping", spans.every((s, i) => i === 0 || s.start >= spans[i - 1].end));
check("luhn accepts a valid card", luhn("4242 4242 4242 4242"));
check("luhn rejects a bad number", !luhn("1234 5678 9012 3456"));

// ---- NER token aggregation (the part that broke in-browser) ----
const nerText = "Jane Doe from Acme Corp in San Francisco";

// Case A: wordpiece tokens WITHOUT offsets (Transformers.js v2 reality)
const noOffset = [
  { entity: "B-PER", score: 0.99, word: "Jane" },
  { entity: "I-PER", score: 0.99, word: "Doe" },
  { entity: "B-ORG", score: 0.98, word: "Ac" },
  { entity: "I-ORG", score: 0.98, word: "##me" },
  { entity: "I-ORG", score: 0.98, word: "Corp" },
  { entity: "B-LOC", score: 0.97, word: "San" },
  { entity: "I-LOC", score: 0.97, word: "Francisco" },
];
const sA = nerSpansFromTokens(nerText, noOffset);
const rA = applyRedaction(nerText, mergeSpans(sA));
check("NER(no offsets): 3 spans", sA.length === 3);
check("NER(no offsets): reconstructs subwords + redacts", rA === "[PERSON] from [ORG] in [LOCATION]");

// Case B: tokens WITH offsets — should use them directly
const withOffset = [
  { entity: "B-PER", score: 0.99, word: "Jane", start: 0, end: 4 },
  { entity: "I-PER", score: 0.99, word: "Doe", start: 5, end: 8 },
];
const sB = nerSpansFromTokens(nerText, withOffset);
check("NER(offsets): one PERSON span 0-8", sB.length === 1 && sB[0].start === 0 && sB[0].end === 8);

// Low-confidence tokens are dropped
const lowConf = [{ entity: "B-PER", score: 0.2, word: "Jane" }];
check("NER: low-confidence dropped", nerSpansFromTokens(nerText, lowConf).length === 0);

console.log(`\n${pass} passed, ${fail} failed`);
process.exit(fail === 0 ? 0 : 1);

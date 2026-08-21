# The Oracle Outside the Loop

*Draft — not wired into notes.json / feed. Series: agents-from-operations.*

---

There is a Vedic almanac widget on my desktop. It computes the panchang — the
five limbs of the traditional Hindu calendar — from raw astronomy: solar and
lunar longitudes, sidereal offsets, the geometry of sunrise at my latitude.
It has a test suite. The tests were green for months.

One evening I cross-checked it against drikpanchang.com, the reference
almanac used by millions of households. My widget said the current karana —
a half-day division of the lunar cycle — was Vishti. The almanac said Vanija.

The widget had been wrong since version 1. Not wrong occasionally — wrong by
construction. The code modeled the karana cycle with 46 slots; the classical
scheme has 60. Every karana it ever displayed was shifted one slot early.
And every test passed, because the tests checked the code against itself.

That kicked off a month of auditing every widget I run. The score so far:
four widgets audited, roughly ten real defects found, every single one
predating the audit, every single one invisible to the internal test suites.

A finance card whose "daily change" was actually a five-day return — it once
showed Bitcoin up 16.6% on a day the true move was 5.7%. A sky widget that
manufactured a Moon–Venus conjunction out of a wrong constant — it used the
Moon's longitude rate where the elongation rate belonged, and advertised an
event that wasn't happening. A weather panel quietly reporting cloud cover
for a grid cell twenty-seven kilometers from my house, because the cell ID
was hardcoded once and never derived again.

Different widgets, different domains, one sentence underneath all of it:

**A self-consistent system cannot detect its own wrongness.**

The tests passed because they were written from the code. Twice I found test
fixtures that had captured the buggy output as the expected value — the bug
enshrined as specification, guarded by a green checkmark. The only thing that
ever found a defect was a reference the system didn't control: a
thousand-year-old almanac tradition, a Swiss ephemeris, a competing price
API, the weather service's own coordinate resolver.

## Why this matters for agents

Everyone building agentic systems right now is drawing loops and graphs:
generate, then critique, then refine. Plan, act, reflect. And the most
common shape I see is a critique node that is the same model, prompted
slightly differently, checking its own work.

That is my copied test suite, running at inference time. The critic was
trained on the same distribution, shares the same blind spots, and will
approve the same wrongness — fluently. A self-review loop converges on
self-consistency, and self-consistency is exactly the property my widgets
had while they were lying to me.

Three rules fell out of this month, and I now apply them to every graph I
design:

**1. Every loop needs an oracle outside it.** For each node that produces a
claim, name the independent reference that could falsify it — an ephemeris,
a second data provider, a deterministic validator, a human. If you cannot
name the node's oracle, you have not designed a check; you have designed
reassurance. The question I write in the margin of every design now:
*what is this node's almanac?*

**2. Draw the health edges, not just the data edges.** Every arrow in your
graph moves data. Almost no one draws the second arrow: *is the thing at the
other end still alive, still fresh, still running the engine it claims?* My
almanac widget had a fallback math path for when the precise ephemeris
library was missing — and production ran that fallback silently for months,
because the fallback's activation was displayed in a footer a human was
supposed to notice. A label is not a check. Freshness contracts, mode
fields, per-source status — machine-checked, or they don't exist.

**3. Put the model where inference lives, not where arithmetic lives.**
Detection in my fleet is deterministic: a timestamp is stale or it isn't; an
engine field says the wrong thing or it doesn't. No model needed, and a
model would only add noise. Where a model earns its place is the step after
a sensor trips: correlating a log line with a failure class, drafting the
diagnosis a human will verify. Deterministic sensors detect. The model
interprets. The human decides. Each layer checks the one below it — and
none of them checks itself.

The karana on my desktop is correct tonight. Not because I wrote better
tests — because an almanac older than the concept of software disagreed
with my code, and I let it win.

---

*DRAFT NOTES (not for publish):*
- *Toby draft. Ad Astra softening candidates: "lying to me" (twice) could
  soften to "wrong"; "designed reassurance" is the sharpest line — keep;
  "fluently" as a one-word jab — keep.*
- *Editorial rulings honored: no internal incident codes, no repo paths,
  no tool names beyond public references (drikpanchang, Swiss ephemeris).*
- *Possible pull-quote: "If you cannot name the node's oracle, you have
  designed reassurance."*
- *Series continuity: sibling of "green checkmark is not a pulse" — one
  cross-link candidate at rule 2.*

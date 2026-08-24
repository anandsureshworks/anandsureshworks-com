# The Oracle Outside the Loop

*Draft v2 — revision round 1 applied (8/8 counter-notes accepted). Not wired into notes.json / feed. Series: agents-from-operations.*

---

There is a Vedic almanac widget on my desktop. The panchang it computes is
an old and intricate system — five interlocking limbs derived from
positional astronomy, refined for centuries against the one oracle that
never lies: the sky itself. My widget rebuilds that system from raw math:
solar and lunar longitudes, sidereal offsets, the geometry of sunrise at my
latitude. It has a test suite. The tests were green for months.

One evening I checked it against drikpanchang.com — the reference almanac
millions of households trust precisely because it has survived that
scrutiny. My widget said the current karana — a half-day division of the
lunar cycle — was Vishti. The almanac said Vanija. The widget had been
wrong since version 1: the code modeled the karana cycle with 46 slots
where the classical scheme has 60, so every karana it ever displayed was
shifted one slot early. And every test passed, because the tests checked
the code against itself.

That one wrong half-day kicked off a month of auditing every widget I run.
A finance card had been doubling my daily moves for months — it showed
Bitcoin up 16.6% on a day the true move was 5.7%. A sky widget
manufactured a Moon–Venus conjunction out of a wrong constant, advertising
an event that wasn't happening. A weather panel quietly reported cloud
cover for a grid cell twenty-seven kilometers from my house, because the
cell ID was hardcoded once and never derived again. Four widgets, roughly
ten real defects, every one predating the audit, every one invisible to
the internal test suites.

It took four widgets to see the shape clearly. Different code, different
domains, one sentence underneath all of it:

**A self-consistent system cannot tell when it is wrong.**

The tests passed because they were written from the code. Twice I found
test fixtures that had captured the buggy output as the expected value —
the bug enshrined as specification, guarded by a green checkmark. The only
thing that ever found a defect was a reference the system didn't control:
a thousand-year-old almanac tradition, a Swiss ephemeris, a competing
price API, the weather service's own coordinate resolver.

## Why this matters for agents

Everyone building agentic systems right now is drawing loops and graphs:
generate, then critique, then refine. Plan, act, reflect. The most common
shape I see is a critique node that is the same model, prompted slightly
differently, checking its own work.

That is my copied test suite, running at inference time. The critic was
trained on the same distribution, shares the same blind spots, and will
approve the same mistakes — fluently.

Three rules fell out of this month, and I now apply them to every graph I
design. They read like operations habits. They are actually the beginnings
of a type system — every contract below becomes a checkable edge in the
agent graphs I am starting to build.

**1. Every loop needs an oracle outside it.** For each node that produces
a claim, name the independent reference that could falsify it — an
ephemeris, a second data provider, a deterministic validator, a human. If
you cannot name the node's oracle, you have not designed a check; you have
designed reassurance. The question I write in the margin of every design
now: *what is this node's almanac?*

**2. Draw the health edges, not just the data edges.** Every arrow in your
graph moves data. Almost no one draws the second arrow: *is the thing at
the other end still alive, still fresh, still running the engine it
claims?* My almanac widget had a fallback math path for when the precise
ephemeris library was missing — and production ran that fallback silently
for months, because the fallback's activation was displayed in a footer a
human was supposed to notice. A label is not a check. Ask three questions
of every box in your diagram, mechanically: when did you last update?
which engine produced you? which of your sources failed? If nothing asks
them automatically, nothing knows the answers.

**3. Put the model where inference lives, not where arithmetic lives.**
Detection in my fleet is deterministic: a timestamp is stale or it isn't;
an engine field says the wrong thing or it doesn't. Where a model earns
its place is the step after a sensor trips: correlating a log line with a
failure class, drafting the diagnosis a human will verify. This placement
is not aesthetic. Arithmetic is free, instant, and auditable — a model
there adds cost, latency, and a new failure surface. And a diagnosis step
runs fine as a small local model, which means the system's operational
telemetry never leaves the machine it describes. Deterministic sensors
detect. The model interprets. The human decides. Each layer checks the one
below it — and none of them checks itself.

The karana on my desktop is correct tonight. Not because I wrote better
tests — because an almanac older than the concept of software disagreed
with my code, and I let it win.

---

*DRAFT NOTES (not for publish):*
- *v2 changes: opener earns the almanac as oracle (cr-1); opener
  compressed to two paragraphs, montage pulled to slot 3 with sharper
  first clause (cr-3/cr-5); bridge + thesis rewording (cr-8); self-review
  repetition cut (cr-11); type-system beat seeds graph engineering
  (cr-13); rule 2 ends on three plain questions (cr-14); rule 3 motivated
  by cost/auditability/sovereignty (cr-15). Both "lying to me" instances
  gone as a side effect of cr-8/cr-11.*
- *Pull-quote: "If you cannot name the node's oracle, you have designed
  reassurance."*
- *Cross-link candidate at rule 2: "green checkmark is not a pulse".*

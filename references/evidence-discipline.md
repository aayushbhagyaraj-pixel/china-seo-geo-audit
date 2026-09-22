# Evidence discipline

This is the part of the audit that survives review. A finding with a weak claim
label or a missing denominator is the one a client's agency will use to dismiss the
whole report.

## Label every conclusion

| Label | Meaning |
|---|---|
| **observed** | You ran it, logged it, and can reproduce it from the record |
| **client-provided** | Supplied by the client; period, grain and owner recorded |
| **inferred** | A reasoned conclusion from observed facts — say which facts |
| **proposed** | A recommendation, not a finding |
| **unmeasured** | Not tested. Never rendered as zero |
| **blocked** | Attempted and prevented — say what prevented it |

A tool failure is evidence about the tool, not about the brand. A login wall, an
exhausted quota or a bot check produces a **blocked** row, never an absence finding.

## Source hierarchy

1. Current official platform documentation for supported behaviour — record the
   interface, version and the document's own update date.
2. Reproducible direct observation for a specified brand, query, location and time.
3. Client exports with a known period and row grain.
4. Transparent independent studies, carrying their sample size and limitations.
5. Agency articles, research-tool syntheses and older client reports — **hypotheses to
   validate**, never conclusions to repeat.

A new title or a recent retrieval date does not prove recent publication. Record
the document's actual update date separately from the date you collected it. Where
a page shows no publication date, say that it was *checked* on a date and that no
publication date was verified.

## Every number carries three things

Denominator · period · metric definition.

Without all three, the number is not reportable. "43% of answers mentioned the
brand" means nothing until you state: 43% of which answers, run when, counting a
mention how.

Related rules:

- Report failed and pending runs separately from the success denominator.
- Distinguish a probe sample's success rate from longitudinal uptime.
- Distinguish unresolved rows from explicitly failed rows.
- Report failures separately from p50/p90 timing. Averaging a timeout into a
  latency figure hides the finding.
- Where grain differs between sources, do not aggregate. Say why.

## Preserve raw evidence

For every observation: timestamp with timezone, exact target or query, tool and
interface, location, settings, account state, and the unmodified output. Save the
report URL where the tool has one. Screenshots supplement the raw text; they do not
replace it.

Verify the target and date on any report someone else supplies. A report for a
different domain is historical evidence for *that* domain. Generic or demo output
displayed by a testing tool is not a result for your target — re-run it against the
exact URL before quoting a number.

## A passing step never establishes the next one

Reachability → crawlability → indexing → retrieval → citation → factual accuracy →
qualified inquiry. Each is a separate observation with its own evidence.

Specifically: an HTTP 200 is not a render. robots.txt permission is not crawling. A
sitemap is not index coverage. A brand mention is not a citation. A retrieved URL
is not an inline citation. An inline citation is not claim support. A form
displaying "success" is not a delivered inquiry. A click is not a qualified lead.

## Handling a reference deck or a prior report

Treat a reference deck as **structure and style**. Its findings belong to the brand
it was made for and do not transfer. Reuse the layout; discard the results unless
fresh evidence specifically supports reusing them. When the slide structure is
fixed by a client, keep a detailed evidence companion document alongside it.

Where a previous note or another agent's analysis contains an error, correct it
explicitly with the observation that contradicts it. Record the correction — it is
usually one of the more valuable outputs of the audit.

## Multi-agent work

If the work is split across agents, divide research, technical, commercial and
presentation responsibilities into **disjoint files**, and integrate through a
single evidence review. Two agents writing to the same findings file produce
untraceable claims.

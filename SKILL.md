---
name: china-seo-geo-audit
description: >
  Audit how an international brand's website performs for users, crawlers and AI
  assistants inside mainland China. Covers mainland reachability (Great Firewall
  blocking, CDN/DNS, ICP filing, blocked third-party resources, form and analytics
  failure), Baidu search visibility (crawl, index, SERPs, Baidu Search Resource
  Platform, Lightning Algorithm), Chinese AI visibility (DeepSeek, Qwen/Tongyi,
  ERNIE/Wenxin, Doubao, Kimi, Yuanbao), Chinese-platform presence (WeChat, Zhihu,
  Xiaohongshu, Baike, Bilibili) and commercial conversion for B2B buyers. Use when
  the target market is mainland China, or when the user says "China audit", "Baidu
  SEO", "China GEO", "does our site work in China", "mainland access", "ICP",
  "Chinese AI visibility", or names a Chinese-language site or .cn domain. For
  Google / ChatGPT / Perplexity / AI Overviews markets use global-seo-geo-audit.
---

# China SEO and GEO audit

A brand's China problem is almost never "our SEO is weak." It is usually that the
page never finished loading, the form never sent, the redirect threw the visitor
back to Europe, or Baidu was handed a sitemap of Italian URLs. Audit the chain in
order — a passing step never establishes the next one.

## The four outcomes — measure separately, never merge

| Outcome | The question | Never inferred from |
|---|---|---|
| **Reachability** | Does the exact URL load, render and function from mainland networks? | HTTP 200 from abroad; a ping; a colleague saying "it works for me" |
| **Search visibility** | Do relevant Chinese pages appear for buyer queries on Baidu? | robots.txt allowing Baiduspider; a sitemap existing; a `site:` count |
| **AI visibility** | Do Chinese assistants name the right entity, with checkable sources? | brand awareness; a NotebookLM synthesis; one lucky answer |
| **Commercial visibility** | Does a buyer verify suitability and reach the right contact? | clicks; impressions; a form that displays "success" |

Brand mention, retrieved URL, inline citation, qualified recommendation and
qualified inquiry are five different events. Count them separately.

## Phase 0 — Freeze scope before testing

Record, and get confirmed: the exact legal/division identity (Chinese **and**
English names), products in scope, B2B or B2C, target cities, the exact domains
and URLs under audit, the competitor set with alias rules, and what counts as a
conversion. Distinguish the division from its parent brand and adjacent divisions —
parent awareness will otherwise contaminate every AI result.

Read any client decks, competitor lists and keyword sheets **before** choosing
benchmarks. A reference deck supplies structure and style; its findings do not
transfer to a different brand without fresh evidence.

## Phase 1 — Mainland reachability

Read [references/technical-access.md](references/technical-access.md).

Run the code-level check first — it is deterministic and location-independent:

```bash
python3 scripts/china_check.py https://example.cn/zh/ --json report.json
```

It reports the redirect chain, render-blocking resources on blocked hosts, the full
external-host inventory, captchas gating the form path (reCAPTCHA, hCaptcha,
Cloudflare Turnstile), consent and chat widgets, analytics coverage, cache headers,
the Chinese font stack and on-page ICP filing. Exit code 1 means a blocking problem
was found.

Rank what it returns by commercial damage, not by count:

1. **A captcha in the form path** — the form silently never sends. The page looks
   perfect and the buyer cannot reach you. This outranks every speed finding.
2. **Render-blocking resources in `<head>` from blocked hosts** — a 30–60 s white
   screen, or an instant load with broken fonts, depending on the province.
3. **Consent and chat widgets** — slow to load *and* consuming first-screen area
   that Baidu measures.

Then establish what a mainland network actually did, with BOCE or ITDOG against the
**exact** target URL. Preserve the report URL, timestamp with timezone, final
status, full redirect chain, per-node and per-carrier results, and the tool's own
definitions of its timing fields.

Alongside it: DNS and nameservers, origin identification, HTTP/HTTPS/WWW and
missing-path behaviour, raw versus rendered HTML, `content-language`, canonical,
robots, sitemap contents, actual transferred bytes, font and video behaviour,
mobile and keyboard access, and completion of the contact path.

Traps that have produced wrong conclusions on real audits:

- **Ping is not HTTP.** A healthy ping to a CDN edge proves ICMP answered. It never
  issues a request, follows the redirect or touches the origin. A site can ping
  green at 151 ms while 57% of real mainland visitors fail.
- **Two blocking modes, opposite symptoms.** Connection refused → page loads fine,
  wrong fonts, no visible problem. Packets dropped silently → white screen for
  30–60 s. Same site, same code. One colleague's "it works" proves nothing.
- **Test in a private window.** A session or language cookie will show a returning
  tester the working site while new visitors get the redirect.
- **A redirect is not a rendered page.** A 200 is not a render. Declared asset bytes
  are not initial transfer. A foreign request cannot establish mainland performance.
- **ICP attaches to hosting location, not the domain.** It is not a ranking
  guarantee, and filing is not the same as licensing. For legal hosting
  requirements consult current authoritative rules separately.

Do not bypass access controls, and do not submit test leads without authorization.

## Phase 2 — Technical and on-page audit

Read [references/technical-onpage.md](references/technical-onpage.md).

The universal technical layer, in Baidu's terms. Most of it transfers from Western
practice — but some standard Google advice is actively wrong here, and Baidu
publishes rules with no Google equivalent.

What differs most, and is most often got wrong:

- **Speed is a published ranking rule.** 闪电算法 (2017-10-19): mobile first screen
  under 2 s gets preference, 3 s or more is suppressed. The metric is first-screen
  time, not LCP/INP/CLS, and a Lighthouse run from abroad does not measure it.
- **Schema.org does not produce Baidu rich results.** Do not port the Google
  structured-data checklist or its deprecation list. Baidu uses its own submission
  formats and the closed 阿拉丁 program, which is realistically out of scope for a
  foreign B2B brand.
- **Baidu's quality framework is not E-E-A-T.** It grades 内容质量 on professional
  depth and completeness, plus browsing experience and accessibility. Author
  identity is not the organising principle.
- **The title must align with the ICP registration**, not just the page — a
  Baidu-specific check with no Google analogue. Baidu rewrites over-optimised
  titles and restricts display for severe cases.
- **Chinese advertising law restricts superlatives** (最好, 第一, 国家级). That is a
  legal exposure finding in Chinese copy, not a style note.
- **The mobile landing-page whitepaper is prescriptive**: first screen within 1 s,
  main content ≥50% of the first screen, font ≥10pt. Consent banners and chat
  widgets routinely breach the 50% rule.
- **Test in the WeChat in-app browser**, not just mobile Chrome — it is where much
  of the real traffic renders, and it breaks things Chrome does not.
- **Never recommend MIP or 熊掌号.** Both are discontinued; MIP is still
  recommended inside Baidu's own 2017 announcement. Finding either in a client's
  existing plan tells you how current that plan is.

## Phase 3 — Baidu search visibility

Read [references/baidu-search.md](references/baidu-search.md).

Baidu is not Google with Chinese results. It ignores hreflang entirely, reads
`content-language` plus the domain as the language signal, handles JavaScript
unreliably, penalises slow first screens by published algorithm, wastes crawl
budget on non-Chinese pages, and fails on language-in-URL parameters.

Audit beyond Baidu where the evidence justifies it — Bing has material desktop
presence in China and is the index behind ChatGPT, and Sogou matters
disproportionately for brands distributing through WeChat.

Use authenticated Baidu Search Resource Platform (ziyuan) exports for owner-side
crawl and index evidence where available. Record desktop and mobile SERPs
separately, and keep SEM strictly separate from organic. A `site:` observation
alone establishes neither complete index coverage nor absence.

## Phase 4 — Chinese AI visibility

Read [references/ai-visibility.md](references/ai-visibility.md) for the full
protocol, the prompt panel design and the metric definitions.

Non-negotiables, because they are what makes results comparable:

1. Every prompt and every repeat starts in a **new empty conversation**. Verify the
   empty state. A new tab is not a new conversation.
2. Keep consumer apps, developer APIs and third-party model deployments separate.
   An Alibaba-hosted DeepSeek and native DeepSeek are different surfaces.
3. Record whether search was *enabled* and whether retrieval *actually ran* — these
   are two observations.
4. Test branded identity separately from unbranded discovery and comparisons. Never
   seed a discovery prompt with brand documents or a domain restriction.
5. Incognito is browser isolation, not proof of zero personalization; concurrent
   incognito tabs share a session. If runs used a signed-in profile, say so.
6. Preserve sidebar and history separately from answer text, so past titles do not
   inflate mention counts.
7. Put an English translation beside every Chinese prompt and quoted excerpt in
   English-facing deliverables. Submit only the Chinese prompt to the assistant.

An initial panel of 30 prompts × 3 platforms × 3 fresh sessions (270 completed
answers) is a **workload convention**, not a statistical minimum. Failed and
pending runs do not count toward the denominator.

## Phase 5 — Platform and content

Map native Chinese buyer intent to useful destination pages: division identity,
supplier capability, technical selection, specifications with units and methods,
cooperation and sample process, partner proof, and contact. Distinguish
retail/prescription/finished-product queries from component procurement.

Recommend readable server-rendered HTML, precise tables with units and methods,
reviewer and update dates, and useful internal links. Reuse existing pages before
adding URLs. Distribute only to channels the buyer actually uses or where citations
were observed.

Do **not** prescribe bulk articles, thin city pages, a fixed keyword density, a
standard Baike/WeChat/Zhihu recipe, or guaranteed AI citations. City pages need
genuine local information; never invent an office.

## Phase 6 — Commercial validation

Track inquiry starts, confirmed deliveries, qualified leads, sample discussions and
opportunities. Never substitute click totals for commercial success. Show a form
success state only after the agreed receipt criterion, and preserve user input on
failure.

For supplied keyword or SEM sheets, retain cell addresses, campaign/adgroup grain,
duplicate rows and original flags. Aggregate CTR is total clicks / total
impressions only when the grain is compatible. Missing cost and qualified
conversions prevent CPA or ROI conclusions. Zero impressions do not prove zero
demand.

## Evidence discipline

Read [references/evidence-discipline.md](references/evidence-discipline.md). It
governs every phase above and is the part reviewers check hardest.

Label every conclusion **observed**, **client-provided**, **inferred**,
**proposed**, **unmeasured** or **blocked**. Every quantitative finding carries its
denominator, period and metric definition. A tool failure is not evidence of brand
absence. Mark missing results unmeasured — never zero.

## Deliverables

Read [references/deliverables.md](references/deliverables.md).

Every finding gets: evidence → business consequence → action → owner → priority →
acceptance check. Prioritise broken contact paths and access failures first, then
accurate identity, then buyer-content gaps, then measured distribution tests.

Stage the plan as **Fix → Identity → Answers → Proof → Recurring operation**, with
completion criteria rather than invented dates. Do not promise ranking, citation or
revenue uplift.

Close with an explicit remaining-data list: owner analytics, Baidu exports,
consumer-assistant runs still pending, mainland browser tests, approved
specifications, lead outcomes.

## Research inputs

NotebookLM and agency articles supply **hypotheses**, not disclosed algorithms.
If asked to use NotebookLM, connect and list notebooks, verify the notebook against
the request context, inspect its sources, then export. Query for methodology and
challenge unsupported claims. A NotebookLM synthesis is source-grounded research —
never a live AI-visibility measurement.

Prefer current official Chinese platform documentation, then reproducible direct
observation. Refresh time-sensitive documentation before relying on it; several
Baidu documents in circulation date from 2020–2022.

Use presentation and document skills for the artifacts themselves rather than
embedding authoring mechanics here.

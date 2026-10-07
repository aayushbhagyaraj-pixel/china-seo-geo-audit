---
name: china-seo-geo-audit
description: >
  Audit how an international brand's website performs for users, crawlers and AI
  assistants inside mainland China. Covers mainland reachability (Great Firewall
  blocking, CDN/DNS, ICP filing, blocked third-party resources, form and analytics
  failure), Baidu technical and on-page rules, Baidu search visibility (crawl, index,
  observed rank with SERP features, Search Resource Platform levers), Chinese AI
  visibility (DeepSeek, Qwen/Tongyi, ERNIE/Wenxin, Doubao, Kimi, Yuanbao, Quark),
  Chinese B2B surfaces (爱采购, 百家号, WeChat search, Zhihu, Xiaohongshu), compliance
  triggers (ICP, 广告法, PIPL) and commercial conversion for B2B buyers. Use when the
  target market is mainland China, or when the user says "China audit", "Baidu SEO",
  "China GEO", "does our site work in China", "mainland access", "ICP", "Baidu rank",
  "Chinese AI visibility", or names a Chinese-language site or .cn domain. For
  Google / ChatGPT / Perplexity / AI Overviews markets use global-seo-geo-audit.
---

# China SEO and GEO audit

A brand's China problem is almost never "our SEO is weak." It is usually that the
page never finished loading, the form never sent, the redirect threw the visitor
back to Europe, or Baidu was handed a sitemap of URLs that return a challenge page.
Audit the chain in order. A passing step never establishes the next one.

## Self-improvement — the user's suggestions become part of this skill

Whenever the user gives a suggestion, correction or "we should also…" during or
after an audit, **update this skill in the same session**, without asking:

1. Add a dated bullet to **Lessons learned** (bottom of this file): what was
   suggested, why, and the client it came from.
2. If it changes *how* the audit is done, also edit the phase or reference file it
   belongs to, so the next run does it by default (not only as a note).
3. Apply it to the current audit straight away and update the report.
4. Say in one line at the end of your reply which file you changed.

The skill lives in `~/.claude/skills/china-seo-geo-audit` (a git repo, symlinked
into the other profiles). Commit only when the user asks.

## The four outcomes — measure separately, never merge

| Outcome | The question | Never inferred from |
|---|---|---|
| **Reachability** | Does the exact URL load, render and function from mainland networks? | HTTP 200 from abroad; a ping; a colleague saying "it works for me" |
| **Search visibility** | Do relevant Chinese pages appear for buyer queries on Baidu, and where on the page? | robots.txt allowing Baiduspider; a sitemap existing; a `site:` count |
| **AI visibility** | Do Chinese assistants name the right entity, with checkable sources? | brand awareness; a synthesis from a research tool; one lucky answer |
| **Commercial visibility** | Does a buyer verify suitability and reach the right contact? | clicks; impressions; a form that displays "success" |

Brand mention, retrieved URL, inline citation, qualified recommendation and
qualified inquiry are five different events. Count them separately.

## Instruments — use what is available, mark the rest blocked

The audit runs with whatever access exists. Each instrument below is optional; a
missing one produces a **blocked** row with the blocker named, never a guess.

| Instrument | Gives | Needs |
|---|---|---|
| `scripts/china_check.py` | Code-level reachability, crawler access, page signals | nothing |
| `scripts/baidu_serp.py` | Observed Baidu rank with SERP features, desktop and mobile | DataForSEO credentials in the environment or a `.env` |
| BOCE / ITDOG | What one mainland network did today | a browser, manual |
| Baidu Search Resource Platform | Owner-side crawl, index, keyword and submission data | client grants access |
| 5118 / 站长之家 / 百度指数 | Keyword volume and demand | Chinese account |
| Chinese AI apps | Phase 4 | a +86 account; see the access section in the AI reference |
| A mainland browser session | Rendering, fonts, video, form completion | a colleague or device in China, private window |

## Phase 0 — Freeze scope before testing

Record, and get confirmed: the exact legal/division identity (Chinese **and**
English names), products in scope, B2B or B2C, target cities, the exact domains
and URLs under audit, the competitor set with alias rules, the distributor or agent
structure, and what counts as a conversion. Distinguish the division from its
parent brand and adjacent divisions; parent awareness will otherwise contaminate
every AI result.

Read any client decks, competitor lists and keyword sheets **before** choosing
benchmarks. A reference deck supplies structure; its findings do not transfer to a
different brand without fresh evidence.

## Phase 1 — Mainland reachability

Read [references/technical-access.md](references/technical-access.md).

Run the code-level check first. It is deterministic and location-independent:

```bash
python3 scripts/china_check.py https://example.cn/zh/ --json report.json
```

It reports the redirect chain, render-blocking resources on blocked hosts, every
external host in the HTML and the CSS, problem hosts named in the site's own JS
bundles (form and API endpoints live there), captchas gating the form path,
consent and chat widgets, analytics coverage, robots.txt per Chinese crawler, the
sitemap's contents and host, a Baiduspider-agent probe of the first sitemap URLs,
language and mobile signals, canonical host, and Baidu registration traces. Exit
code 1 means a blocking problem was found.

Rank what it returns by commercial damage, not by count:

1. **The form's delivery path.** A captcha from a blocked host, or a POST endpoint
   on a Cloudflare-fronted or foreign-only service. The page looks perfect and the
   buyer cannot reach you. This outranks every speed finding.
2. **Sitemap or canonical URLs that fail a crawler probe.** Everything downstream
   is invisible until this is fixed.
3. **Render-blocking resources in `<head>` from blocked hosts.** A 30–60 s white
   screen, or an instant load with broken fonts, depending on the province.
4. **Consent and chat widgets.** Slow to load, and consuming first-screen area
   that Baidu measures.

Then establish what a mainland network actually did, with BOCE or ITDOG against the
**exact** target URL. Preserve the report URL, timestamp with timezone, final
status, full redirect chain, per-node and per-carrier results, and the tool's own
definitions of its timing fields.

**Mainland speed is mandatory and uses the free China-based tools.** Follow
[references/mainland-speed-tests.md](references/mainland-speed-tests.md): 17CE,
BOCE, ITDOG (quick + slow test / full screenshot) and chinaz, on the homepage, a
product page and the form page, **plus each blocked third-party resource URL on its
own** (Google Fonts, reCAPTCHA, Maps, the image CDN, the form POST host). Lighthouse
run from Europe is a **proxy for page weight only**. Never report it as "load time"
or compare it to Baidu's 2 s / 3 s rule without saying it was measured abroad.

Traps that have produced wrong conclusions on real audits:

- **Ping is not HTTP.** A healthy ping to a CDN edge proves ICMP answered. A site
  can ping green while most real mainland visitors fail.
- **Two blocking modes, opposite symptoms.** Connection refused: page loads fine,
  wrong fonts. Packets dropped silently: white screen for 30–60 s. Same site, same
  code. One colleague's "it works" proves nothing.
- **Test in a private window.** A session or language cookie shows a returning
  tester the working site while new visitors get the redirect.
- **A redirect is not a rendered page.** A 200 is not a render. A foreign request
  cannot establish mainland performance.
- **The script cannot see runtime-injected resources.** A tag manager can load a
  captcha the HTML never mentions. A mainland browser session with a network
  capture is the only complete check.

Do not bypass access controls, and do not submit test leads without authorization.

## Phase 2 — Technical and on-page audit

Read [references/technical-onpage.md](references/technical-onpage.md).

The universal technical layer, in Baidu's terms. Most of it transfers from Western
practice, but some standard Google advice is actively wrong here, and Baidu
publishes rules with no Google equivalent.

- **Speed is a published ranking rule.** 闪电算法 (2017-10-19): mobile first screen
  under 2 s gets preference, 3 s or more is suppressed. The metric is first-screen
  time, not LCP/INP/CLS, and a Lighthouse run from abroad does not measure it.
- **Schema.org does not produce Baidu rich results.** Do not port the Google
  structured-data checklist. Baidu uses its own formats and the closed 阿拉丁
  program, out of scope for most foreign B2B brands.
- **Baidu's quality framework is not E-E-A-T.** It grades 内容质量 on professional
  depth and completeness, plus browsing experience and accessibility.
- **The title must align with the ICP registration**, not just the page.
- **Chinese advertising law restricts superlatives** (最好, 第一, 国家级). A legal
  exposure finding in Chinese copy, for counsel.
- **The mobile landing-page whitepaper is prescriptive**: first screen within 1 s,
  main content ≥50% of the first screen, no autoplay animation.
- **Test in the WeChat in-app browser**, not just mobile Chrome.
- **Never recommend MIP or 熊掌号.** Both are discontinued.

## Phase 3 — Baidu search visibility

Read [references/baidu-search.md](references/baidu-search.md),
[references/keyword-rank-tracking.md](references/keyword-rank-tracking.md) and
[references/baidu-resource-platform.md](references/baidu-resource-platform.md).

Baidu ignores hreflang, reads `content-language` plus the domain as the language
signal, handles JavaScript unreliably, penalises slow first screens by published
algorithm, keeps PC and mobile as separate indexes, and wastes crawl budget on
non-Chinese pages.

Three things to establish, in order:

1. **Can Baidu reach the site at all?** Sitemap URLs and canonicals returning 200
   to a non-JavaScript client, robots.txt, and the owner's 抓取诊断 and 索引量 where
   access exists. Without access, mark blocked and use the script's probe as the
   inferred proxy.
2. **Is indexing wired up?** 主动推送, sitemap submission, 移动适配 declaration,
   HTTPS declaration. These are the levers; none has a Google equivalent.
3. **Where does the site actually appear?** Run the rank script on a keyword set
   built by intent group, desktop and mobile separately:

```bash
python3 scripts/baidu_serp.py --keywords-file kw.txt --brand example.cn \
    --device desktop,mobile --out rank_YYYY-MM-DD
```

The API fetch runs on baidu.com with location 2156 (China) and `zh_CN`, not from
the analyst's country. Index facts (which host Baidu stores, which pages rank) do
not depend on where you sit. City targeting of ads and small local rank shifts do.
Say this in the report. Ask one mainland colleague for a private-window screenshot
of 2–3 brand queries to confirm, and label it observed (mainland, manual).

Report organic position **and** absolute position with what sits above (ads,
品牌专区, 阿拉丁 cards, 百家号, AI summary). Record the brand SERP as a finding:
which third parties outrank the owned site, and whether any is an unauthorised
agent, a squatter or a competitor bidding on the name.

Audit beyond Baidu where the evidence justifies it: Bing (desktop share, and the
index behind ChatGPT), 360, Sogou (WeChat integration), Shenma. Keep SEM separate
from organic. A `site:` observation alone establishes neither coverage nor absence.

## Phase 4 — Chinese AI visibility

Read [references/ai-visibility.md](references/ai-visibility.md) for the protocol,
the prompt panel, the access requirements and the metric definitions.

Two tiers. A **quick scan** of 10 prompts × 3 platforms × 1 fresh session
establishes direction and belongs in a first audit. The **full panel** of 30 × 3 × 3
(270 completed answers) produces quotable rates and is a scoped follow-on. Say
which tier was run. Failed and pending runs do not count toward the denominator.

Non-negotiables:

1. Every prompt and every repeat starts in a **new empty conversation**.
2. Keep consumer apps, developer APIs and third-party deployments separate. Keep
   Baidu's in-SERP AI answer separate from the ERNIE/文小言 app and from organic.
3. Record whether search was *enabled* and whether retrieval *actually ran*.
4. Test branded identity separately from unbranded discovery. Never seed a
   discovery prompt with brand documents.
5. Incognito is browser isolation, not proof of zero personalization. Record the
   account used, the network location, and whether a VPN was in the path.
6. Preserve sidebar and history separately from answer text.
7. Put an English translation beside every Chinese prompt and excerpt in
   English-facing deliverables. Submit only the Chinese prompt.

Most of these apps need a +86 number and real-name registration. If no mainland
account exists, the phase is **blocked**, and the report says so instead of
quoting a partial run as a result.

## Phase 5 — Platform, surfaces and content

Read [references/china-b2b-surfaces.md](references/china-b2b-surfaces.md).

Audit where the buyer actually looks: 百度爱采购, 百家号, 百度百科, 1688 and
procurement platforms, 微信搜一搜, 抖音, 小红书, 知乎. Record presence, accuracy, and
who fills the gap when the brand is absent (resellers, unauthorised agents, old
articles). Check the trust conventions on the site itself: entity name matching
the registry, licences, a phone number, WeChat and 企业微信, a named contact.

Map native Chinese buyer intent to useful destination pages: division identity,
supplier capability, technical selection, specifications with units and methods,
cooperation and sample process, partner proof, and contact. Recommend readable
server-rendered HTML, precise tables, reviewer and update dates, useful internal
links. Reuse existing pages before adding URLs.

Do **not** prescribe bulk articles, thin city pages, a keyword density, a standard
Baike/WeChat/Zhihu recipe, or guaranteed AI citations. Distribute only to channels
the buyer uses or where a citation was observed.

## Phase 6 — Commercial validation and compliance

Track inquiry starts, confirmed deliveries, qualified leads, sample discussions and
opportunities, across every contact path: form, phone, WeChat, email. Never
substitute click totals for commercial success. Show a form success state only
after the agreed receipt criterion, and preserve user input on failure.

Flag compliance triggers for counsel without concluding: PIPL for any form sending
mainland personal data abroad, 数据安全法 and 网络安全法, 等保 2.0 for mainland
hosting, 电子商务法 if the site sells, 广告法 for copy. A site can be perfect for
Baidu and legally unshippable.

For supplied keyword or SEM sheets, retain cell addresses, campaign/adgroup grain,
duplicate rows and original flags. Missing cost and qualified conversions prevent
CPA or ROI conclusions. Zero impressions do not prove zero demand.

## Evidence discipline

Read [references/evidence-discipline.md](references/evidence-discipline.md). It
governs every phase above and is the part reviewers check hardest.

Label every conclusion **observed**, **client-provided**, **inferred**,
**proposed**, **unmeasured** or **blocked**. Every quantitative finding carries its
denominator, period and metric definition. A tool failure is not evidence of brand
absence. Mark missing results unmeasured, never zero. Agency articles and research
syntheses supply hypotheses, not disclosed algorithms; prefer current official
Chinese platform documentation with its date, then reproducible observation.

## Deliverables

Read [references/deliverables.md](references/deliverables.md).

Every finding gets: evidence → business consequence → action → owner → priority →
acceptance check. Prioritise broken contact paths and access failures first, then
accurate identity, then buyer-content gaps, then measured distribution tests.

Stage the plan as **Fix → Identity → Answers → Proof → Recurring operation**, with
completion criteria rather than invented dates. Do not promise ranking, citation or
revenue uplift. Close with an explicit remaining-data list naming each blocker and
who holds the key: owner analytics, platform exports, AI runs pending, mainland
browser tests, approved specifications, lead outcomes.

## Lessons learned

- 2026-10-05 (client: Italian design brand, .cn site): `china_check.py` flagged pages as CHALLENGE because their HTML contains the string "recaptcha"; verify any CHALLENGE with a manual Baiduspider-UA fetch. It also probes only the first 3 `Sitemap:` lines, so a shared multi-domain robots.txt can hide the right sitemap (sitemapcn.xml was 7th); probe the target host's own sitemap by hand. Root URLs that redirect off-domain get analysed as the destination site, so re-run on the deep Chinese URL. Lighthouse headless needs `--max-wait-for-load=90000` and a sequential run, or it returns NO_FCP. For a renamed or migrated site, compare the host of owned Baidu results (old .it/.com vs .cn); it is the fastest migration signal. Always SERP-test the brand's Chinese name from Baike alongside the Latin name.
- 2026-10-05 (same client, user suggestion): mainland speed must come from the free China tools (17CE, BOCE, ITDOG slow/full-screenshot, chinaz), not Lighthouse from Italy, which only proves page weight. Made it a mandatory step in Phase 1 and added `references/mainland-speed-tests.md`. The user also asked whether SERP results depend on searching from Italy: explain location 2156 up front in the report.
- 2026-10-05 (user request): added the Self-improvement section. Every user suggestion is written into this skill in the same session.
- 2026-10-05 (same client, founder challenged three claims, two were weak): (a) "not visible" claims need depth: re-run category keywords with `--depth 30` (3 pages) before saying a brand is absent. (b) Before blaming the Great Firewall, run a global control at the same minute (check-host.net API: `check-http?host=<url>&max_nodes=25`). The client's server went down worldwide during the China tests, so the "81 of 92 failed" result was not China-specific. (c) Do not fire BOCE, 17CE, chinaz and ITDOG within minutes of each other on a small origin; ~500 probe requests may trip its protection. Space them out and run one global control per run. (d) DataForSEO's AI-summary flag missed a Baidu AI answer visible in a manual screenshot: always capture 3 manual Baidu screenshots (brand, Chinese name, category) as slide references. (e) Verify behaviour claims such as "the redirect follows a cookie" with a test before writing them.

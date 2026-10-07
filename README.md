# china-seo-geo-audit

A [Claude Code](https://claude.com/claude-code) skill for auditing how an
international brand's website actually performs for users, crawlers and AI
assistants **inside mainland China**.

A brand's China problem is almost never "our SEO is weak." It is usually that the
page never finished loading, the form never sent, the `.cn` redirect threw the
visitor back to Europe, or Baidu was handed a sitemap of URLs that return a
challenge page. This skill audits that chain in order, and holds the line that a
passing step never establishes the next one.

## What it covers

| Area | Includes |
|---|---|
| **Mainland reachability** | Great Firewall blocking modes, blocked third-party resources in HTML, CSS and JS bundles, form endpoints on foreign-only services, redirect chains, CDN/DNS, ICP filing, captchas breaking form submission, analytics blind spots |
| **Technical and on-page** | Baidu's published rules with dates: 闪电算法 speed thresholds, title specification, landing-page whitepaper, page quality standard; why Schema.org, E-E-A-T and Core Web Vitals do not port; 广告法 superlatives |
| **Baidu search visibility** | Crawler access and a Baiduspider-agent probe of the sitemap, the Search Resource Platform levers (主动推送, 移动适配, 改版工具), observed rank with SERP features via DataForSEO, keyword discovery by intent, the brand SERP as a finding |
| **Chinese AI visibility** | DeepSeek, Qwen/Tongyi, ERNIE/文小言, Doubao, Kimi, Yuanbao, Quark, and Baidu's in-SERP AI answer as its own surface; isolation protocol, +86 access requirements, quick scan vs full panel, metric definitions with denominators |
| **B2B surfaces** | 百度爱采购, 百家号, 百度百科, 1688, WeChat search, Douyin, Xiaohongshu, Zhihu; unauthorised agent claims; Chinese trust and contact conventions |
| **Commercial and compliance** | Inquiry delivery across form, phone and WeChat; SEM sheet handling; PIPL and related triggers flagged for counsel |

## Install

```bash
git clone https://github.com/aayushbhagyaraj-pixel/china-seo-geo-audit.git \
  ~/.claude/skills/china-seo-geo-audit
```

Then invoke it with `/china-seo-geo-audit`, or just describe a China audit; the
description routes it automatically.

## Instruments

The skill runs with whatever access exists. Each instrument is optional. A missing
one produces a **blocked** row in the audit with the blocker named, never a guess.

| Instrument | Gives | Needs |
|---|---|---|
| `scripts/china_check.py` | Code-level reachability, crawler access, page signals | nothing |
| `scripts/baidu_serp.py` | Observed Baidu rank with SERP features, desktop and mobile | DataForSEO credentials |
| BOCE / ITDOG | What one mainland network did today | a browser |
| Baidu Search Resource Platform | Owner-side crawl, index, keywords, submission | client access |
| 5118 / 站长之家 / 百度指数 | Keyword volume and demand | Chinese account |
| Chinese AI apps | The AI visibility phase | a +86 account |
| A mainland browser session | Rendering, fonts, video, form completion | a colleague or device in China |

### china_check.py

```bash
python3 scripts/china_check.py https://example.cn/zh/ --json report.json
```

Python 3.7+, standard library only. Exit code 1 if a blocking problem was found.
It reads the page's code, so the result is the same from anywhere. It fetches the
stylesheets and same-origin JS bundles, reads robots.txt per Chinese crawler,
fetches the sitemap with a Baiduspider user agent and probes its first URLs for
status codes and challenge pages, and reads the language, mobile, canonical and
Baidu registration signals. It prints a FAIL and WARN list, not a score.

It cannot see resources injected at runtime by a tag manager, and it cannot
measure mainland timing. Both need a browser session in China.

### baidu_serp.py

```bash
DATAFORSEO_LOGIN=... DATAFORSEO_PASSWORD=... \
python3 scripts/baidu_serp.py --keywords-file kw.txt --brand example.cn \
    --device desktop,mobile --out rank_2026-09-22
```

One row per keyword and device: the owned site's organic position, its absolute
position counting ads and feature blocks, what sits above it, the top domains, and
the related searches Baidu showed. Writes JSON and CSV. Costs a fraction of a cent
per SERP through DataForSEO. With no credentials it prints a blocked notice and
exits, so the gap is recorded rather than filled with a guess.

## Why testing from one location proves very little

The Great Firewall blocks a host in two different ways, and which one a visitor
meets depends on province, carrier and international gateway:

| Mechanism | What the visitor sees |
|---|---|
| Connection refused instantly | Page loads normally. Wrong fonts, missing icons. **No visible problem.** |
| Packets dropped silently | Browser waits out its own timeout. **White screen, 30–60 seconds.** |

Same site, same code, opposite experience. This is why one colleague in Shanghai
reports "it works" while another in the same country waits a minute, and why a
green ping test means almost nothing.

## Structure

```
SKILL.md                                 Phases, outcomes, instruments, the rules that get broken most
references/technical-access.md           Reachability testing, blocked hosts, architecture grid
references/mainland-speed-tests.md       Free China speed tools (17CE, BOCE, ITDOG, chinaz), global control
references/technical-onpage.md           Baidu's published technical and on-page rules
references/baidu-search.md               Baidu behaviour, crawlers, SERP observation
references/baidu-resource-platform.md    Submission, 移动适配, migration, proxies without access
references/keyword-rank-tracking.md      Rank definition, keyword discovery, baseline table
references/china-b2b-surfaces.md         爱采购, 百家号, WeChat search, trust conventions, compliance
references/ai-visibility.md              AI measurement protocol, access, prompt panel, metrics
references/evidence-discipline.md        Claim labels, source hierarchy, denominators
references/deliverables.md               Finding format, priorities, staging
scripts/china_check.py                   Accessibility and crawler-access checker
scripts/baidu_serp.py                    Observed Baidu rank table via DataForSEO
```

`SKILL.md` loads on trigger; the references load on demand.

## On evidence

The skill is opinionated about claims, because China audits attract confident
assertions that no primary source supports. It requires every conclusion to be
labelled **observed**, **client-provided**, **inferred**, **proposed**,
**unmeasured** or **blocked**, every number to carry its denominator, period and
metric definition, and missing results to be marked unmeasured rather than zero.

It also names claims to reject without fresh proof: that all Chinese AIs read
Baike first, that Yuanbao only reads WeChat, that offshore routing bypasses the
firewall, that an ICP record guarantees ranking, that Baidu executes no JavaScript
at all, that citations can be guaranteed within 30 days.

## Companion skill

[`global-seo-geo-audit`](https://github.com/aayushbhagyaraj-pixel/global-seo-geo-audit)
is the sibling for Google-and-Western markets: same audit spine and evidence
discipline, completely different instruments.

## License

MIT, see [LICENSE](LICENSE).

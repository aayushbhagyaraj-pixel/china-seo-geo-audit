# china-seo-geo-audit

A [Claude Code](https://claude.com/claude-code) skill for auditing how an
international brand's website actually performs for users, crawlers and AI
assistants **inside mainland China**.

A brand's China problem is almost never "our SEO is weak." It is usually that the
page never finished loading, the form never sent, the `.cn` redirect threw the
visitor back to Europe, or Baidu was handed a sitemap of the wrong domain's URLs.
This skill audits that chain in order, and holds the line that a passing step never
establishes the next one.

## What it covers

| Area | Includes |
|---|---|
| **Mainland reachability** | Great Firewall blocking modes, blocked third-party resources, redirect chains, CDN/DNS, ICP filing, reCAPTCHA breaking form submission, analytics blind spots |
| **Technical & on-page** | Baidu's published rules — 闪电算法 speed thresholds, title specification, landing-page whitepaper, page quality standard — plus why Schema.org, E-E-A-T and Core Web Vitals do not port |
| **Baidu search visibility** | Baidu vs Google behavioural differences, Baidu Search Resource Platform, the seven Chinese crawlers including Bytespider, and auditing beyond Baidu |
| **Chinese AI visibility** | DeepSeek, Qwen/Tongyi, ERNIE/Wenxin, Doubao, Kimi, Yuanbao — isolation protocol, prompt panel design, metric definitions with declared denominators |
| **Commercial visibility** | Inquiry delivery, qualified leads, SEM sheet handling, what click data cannot tell you |

## Install

```bash
git clone https://github.com/aayushbhagyaraj-pixel/china-seo-geo-audit.git \
  ~/.claude/skills/china-seo-geo-audit
```

Then invoke it with `/china-seo-geo-audit`, or just describe a China audit — the
description routes it automatically.

## The bundled tool

`scripts/china_check.py` reads a page's **code** and reports which resources are
capable of blocking or hanging it in China. Deterministic and location-independent:
the same result from anywhere, every time.

```bash
python3 scripts/china_check.py https://example.cn/zh/ --json report.json
```

Python 3.7+, standard library only. Exit code 1 if a blocking problem was found, so
it drops into CI or a deploy gate.

It checks the redirect chain, render-blocking resources on blocked hosts, the full
external-host inventory, captchas gating the form path (reCAPTCHA, hCaptcha,
Cloudflare Turnstile), consent and chat widgets, analytics coverage, cache headers,
the Chinese font stack and on-page ICP filing.

The finding that usually matters most is the captcha one. A captcha must fetch a
token from its own host *before a form will send*, so from China the enquiry fails
permanently — even after the page has loaded perfectly. A site can look completely
healthy and be unable to receive a single lead.

## Why testing from one location proves very little

The Great Firewall blocks a host in two different ways, and which one a visitor
meets depends on province, carrier and international gateway:

| Mechanism | What the visitor sees |
|---|---|
| Connection refused instantly | Page loads normally. Wrong fonts, missing icons. **No visible problem.** |
| Packets dropped silently | Browser waits out its own timeout. **White screen, 30–60 seconds.** |

Same site, same code, opposite experience. This is why one colleague in Shanghai
reports "it works" while another in the same country waits a minute. It is also why
a green ping test means almost nothing — ping proves ICMP answered at the CDN edge.
It never issues an HTTP request, never follows the redirect, and never touches the
origin.

## Structure

```
SKILL.md                             Phases, outcomes, the rules that get broken most
references/technical-access.md       Reachability testing, blocked hosts, architecture grid
references/technical-onpage.md       Baidu's published technical and on-page rules
references/baidu-search.md           Baidu behaviour, owner-side evidence, crawlers
references/ai-visibility.md          AI measurement protocol, prompt panel, metrics
references/evidence-discipline.md    Claim labels, source hierarchy, denominators
references/deliverables.md           Finding format, priorities, staging
scripts/china_check.py               The accessibility checker
```

`SKILL.md` loads on trigger; the references load on demand.

## On evidence

The skill is opinionated about claims, because China audits attract confident
assertions that no primary source supports. It requires every conclusion to be
labelled **observed**, **client-provided**, **inferred**, **proposed**,
**unmeasured** or **blocked**, every number to carry its denominator, period and
metric definition, and missing results to be marked unmeasured rather than zero.

It also names claims to reject without fresh proof — that all Chinese AIs read
Baike first, that Yuanbao only reads WeChat, that offshore routing bypasses the
firewall, that an ICP record guarantees ranking, that citations can be guaranteed
within 30 days.

## Companion skill

[`global-seo-geo-audit`](https://github.com/aayushbhagyaraj-pixel/global-seo-geo-audit)
is the sibling for Google-and-Western markets — same audit spine and evidence
discipline, completely different instruments.

## License

MIT — see [LICENSE](LICENSE).

# Mainland reachability — what to test and how to read it

## Why code-level and network-level tests are both needed

Two independent questions:

- **Is the risk still in the page?** — deterministic, same answer from anywhere.
  Answered by reading the HTML for resources loaded from blocked hosts.
- **What did one mainland network do today?** — varies by hour, province, carrier
  and international gateway. Answered by BOCE / ITDOG / chinaz.

Run both. Reporting only the first understates real failure; only the second gives
an unreproducible snapshot.

## The two blocking modes

The Great Firewall blocks a host in two ways, and which one a visitor meets depends
on province, carrier and gateway:

| Mechanism | What the visitor sees |
|---|---|
| Connection refused instantly | Page loads normally. Wrong fonts, missing icons. **No visible problem.** |
| Packets dropped silently | Browser waits out its own timeout. **White screen, 30–60 s.** |

Same site, same code, opposite experience. This is why one colleague in Shanghai
reports "it works" while another waits a minute — and why a single-location test
proves very little.

Demonstrate it directly when a stakeholder disputes the finding:

```bash
# Connection refused instantly — page would load fine
curl -s -o /dev/null -m 60 --resolve www.google.com:443:127.0.0.1 \
  -w "refused after %{time_total}s\n" \
  "https://www.google.com/recaptcha/api.js?render=x"

# Packets dropped silently — this is the white screen
curl -s -o /dev/null -m 30 --resolve www.google.com:443:192.0.2.1 \
  -w "gave up after %{time_total}s\n" \
  "https://www.google.com/recaptcha/api.js?render=x"
```

## scripts/china_check.py

```bash
python3 scripts/china_check.py https://example.cn/zh/
python3 scripts/china_check.py https://example.cn/ https://example.cn/zh/
python3 scripts/china_check.py https://example.cn/zh/ --json report.json
python3 scripts/china_check.py https://example.cn/zh/ --no-color --timeout 60
```

Python 3.7+, standard library only. Exit code 1 if a blocking problem was found,
0 if clean — usable in CI or a deploy gate.

It checks:

1. **Redirect chain** — whether the page leaves the domain it started on. A `.cn`
   handing the visitor to a European origin is the most expensive single problem a
   China site can have.
2. **Render-blocking resources from blocked hosts** — scripts and stylesheets in
   `<head>`. These cause the white screen.
3. **All external hosts in the HTML and the CSS** — the stylesheets are fetched and
   scanned for `url()` and `@import`, so a Google Font pulled in from CSS, or a
   `srcset` image on a foreign CDN, is caught. Split into blocked and slow.
4. **Hosts named in the site's own JS bundles** — a partial remedy for resources
   the HTML never mentions. A Supabase, Firebase, HubSpot or Zapier endpoint that
   the form writes to shows up here. The script cannot tell whether the host is on
   the form path; a network capture from a mainland browser settles that.
5. **Form submission** — captchas (Google reCAPTCHA, hCaptcha, Cloudflare
   Turnstile) and `<form action>` hosts. A captcha must fetch a token from its own
   host *before the form will send*, so enquiries fail permanently from China even
   after the page has finished loading. Commercially this outranks every speed
   finding: the page looks fine and the buyer still cannot reach you.
6. **Consent and chat widgets** — OneTrust, Cookiebot, Iubenda, Intercom, Zendesk,
   Drift, HubSpot, Tawk.to. They load from hosts with no mainland presence, and
   they occupy first-screen area that Baidu measures.
7. **Analytics coverage** — GA/GTM only, Chinese analytics, or nothing.
8. **Crawler access** — robots.txt per Chinese crawler (Baiduspider, Bytespider,
   Sogou, 360, Yisou, Petal), every `Sitemap:` line fetched with a Baiduspider user
   agent, URL count and host of the sitemap entries, and a Baiduspider-agent probe
   of the first three sitemap URLs with challenge-page detection. This is the
   check that catches a bot-mitigation layer serving crawlers a 429 or a
   checkpoint page while browsers pass.
9. **Page signals** — `<html lang>`, `content-language` header and meta, meta
   robots and `X-Robots-Tag`, viewport, the 移动适配 declaration
   (`applicable-device` / `mobile-agent`), canonical host, and Baidu registration
   traces (`baidu-site-verification` meta, push script).
10. **Secondary** — cache headers, Chinese font stack in HTML or CSS, on-page ICP
    filing, Chinese social presence.

Reading the result: it prints a FAIL and WARN list, not a score. A failing
sitemap probe, a captcha, a canonical on another host or a `noindex` each outrank
any number of warnings. Confirm from a mainland browser session before the finding
enters a deliverable.

What it cannot see: anything injected at runtime by a tag manager or consent
script, actual mainland timing, and what Baidu received from its own IP range.

## Commonly blocked hosts

**Blocked** — Google in all its forms (search, Fonts, hosted libraries, Tag
Manager, Analytics, APIs, gstatic, googleusercontent, DoubleClick, AdSense),
reCAPTCHA, **hCaptcha**, Meta (Facebook, SDK, fbcdn, Instagram, cdninstagram),
Twitter/X (including x.com and twimg), YouTube (including ytimg), LinkedIn,
Pinterest, Vimeo, Dropbox, WordPress.org, Gravatar, WhatsApp, Telegram, Wikipedia
and Wikimedia, Reddit, Medium, Quora, Blogspot/Blogger, Slack, Notion, Figma,
Discord, Twitch, SoundCloud.

**Slow or unreliable** — cdnjs.cloudflare.com, cdn.jsdelivr.net, unpkg.com, Adobe
Typekit, Font Awesome CDN, code.jquery.com, BootstrapCDN, BootCSS, S3 US regions,
raw.githubusercontent.com, github.com, **Cloudflare Turnstile**
(challenges.cloudflare.com), consent platforms (OneTrust/cookielaw, Cookiebot,
Iubenda), chat and support widgets (Intercom, Zendesk, Drift, HubSpot, Tawk.to),
product analytics and session replay (Segment, Hotjar, FullStory, Mixpanel,
Amplitude, Sentry), scheduling and forms (Calendly, Typeform), Stripe, Auth0, and
edge platforms without mainland nodes (CloudFront by default, Akamai — mainland
presence reported ended 2026-06-30 — Vercel).

**Form and API endpoints** — Supabase (Cloudflare-fronted), Firebase (Google),
Formspree, Zapier webhooks, Airtable, HubSpot forms API, Cloudflare Workers and
Pages, Netlify, Heroku, Render, Fly. These are not on the page; they are where the
form's POST goes. Cloudflare's standard network has no mainland presence (only the
Enterprise China Network via JD Cloud does, and it needs an ICP filing), so a
stateful POST is exposed to mid-connection resets that a page load survives.

The categories that matter most, in order of commercial damage:

| Category | Why it ranks here |
|---|---|
| **Captcha or foreign-only endpoint in the form path** | The form silently never sends, or sends intermittently by province. The page looks perfect. Lost enquiries nobody can see |
| **Crawler-facing URLs behind a challenge** | Sitemap and canonical URLs that return 429 or a checkpoint page to non-browser clients. Zero index, whatever the content |
| **Render-blocking in `<head>`** | 30–60 s white screen, or an instant load with broken fonts — depending on province |
| **Consent / chat widgets** | Load slowly *and* consume the first screen, which Baidu measures |

On **recaptcha.net**: it is Google's documented workaround domain for regions
where google.com is unreachable, and it did work from the mainland for years. It
has been reported blocked across checked regions since late 2022 and intermittent
since. A client who "already switched to recaptcha.net" still has the problem;
the tool flags it with that note.

The tool holds the current table and matches subdomains by suffix. Treat it as a
starting point that needs periodic refresh, not a settled list — providers change
their mainland arrangements, and any specific claim here (including the Akamai
date) should be confirmed fresh before it enters a deliverable.

Chinese replacements to recommend in place of blocked services: **Geetest** or
**Tencent Captcha** for reCAPTCHA/hCaptcha, **Baidu Tongji** or a tested
alternative for GA, self-hosted fonts for Google Fonts, and a mainland or Hong Kong
CDN for asset delivery. Prove the actual failure with network evidence before
prescribing the swap.

## Mainland network testing

- **BOCE** (boce.com) — HTTP tests from many mainland nodes with per-carrier
  results. Guest quota is limited; a login or a fresh day may be needed.
- **ITDOG** (itdog.cn/http/) — HTTP from many mainland cities. Behind a Cloudflare
  bot check, so it is manual, not scriptable.
- **ping.chinaz.com** — ping and traceroute from Chinese ISPs. Diagnostic only.
- **websitepulse.com/tools/china-firewall-test** — firewall reachability check.

For every run, preserve: the report URL, the exact target URL, timestamp **with
timezone**, final status, full redirect chain, per-node and per-carrier results,
and the tool's own definitions of its DNS / connect / TLS / HTTP timing fields.
Repeat anomalies before reporting them. Report failures separately from p50/p90
timing — averaging a timeout into a latency figure hides the actual finding.

Verify the domain and date on any historical report someone supplies. A report for
a different target is historical evidence for *that* target, not for this one.

## What each result does and does not establish

| Observation | Establishes | Does **not** establish |
|---|---|---|
| Ping green from China | ICMP answered at the edge | Any HTTP behaviour, the redirect, the origin |
| HTTP 200 from abroad | The origin answers | Mainland reachability or rendering |
| HTTP 200 from a mainland node | That node reached a final status | That the page rendered, or that assets loaded |
| Redirect followed | A hop occurred | A successful final page render |
| Total declared asset bytes | Page weight on paper | Actual initial transfer |
| Desktop screenshot | Desktop layout | Mobile behaviour or mainland performance |
| robots.txt allows Baiduspider | Crawl permission | Crawling, indexing or ranking |
| Sitemap exists | A URL footprint was declared | Index coverage |

## Browser-level checks from mainland

HTTP probes do not measure rendering. Where a mainland browser session is
available, additionally capture: actual transferred bytes, rendered content,
font and video behaviour, and completion of the inquiry path end to end.

Always test in a **private/incognito window**. A normal window carries a session or
language cookie and will show a returning tester the working site while new
visitors get the redirect. Giving an agency this one instruction prevents most
"but it works for me" disputes.

## Architecture reference for a dual international / China setup

1. **Separate `.cn` ccTLD for mainland** — clearest local-targeting signal, and it
   keeps Baidu's crawl budget off non-Chinese pages.
2. **The `.cn` serves Chinese at its root.** No cross-domain redirect for Chinese
   visitors.
3. **Hosting** — mainland + ICP is optimal; Hong Kong or offshore plus a
   China-capable CDN is the standard compromise for foreign brands. ICP attaches to
   *hosting location*, not to the domain.
4. **No blocked foreign resources** — Google Fonts, Google Analytics, GTM, Facebook
   pixels, reCAPTCHA.
5. **First screen under 2 s on mobile.**
6. **Server-rendered HTML for critical content** — Baidu's JavaScript handling is
   unreliable even though a render crawler exists.
7. **Simplified Chinese** titles, descriptions, content.
8. **Sitemap listing the `.cn` Chinese URLs**, submitted via Baidu Search Resource
   Platform.
9. **Baidu Tongji** for measurement.

Use this as a gap-analysis grid: requirement → what the site does today → verdict.
Most foreign brands fail on configuration, not construction — and items 2, 4 and 8
are each usually a single setting.

Two configuration defects recur often enough to check by name: a bot-mitigation
layer (Vercel, Cloudflare, Akamai) on the apex or on the canonical host that
challenges every non-browser client, and a sitemap or canonical set pointing at a
host other than the one that serves the page. Either gives a zero index with a
perfectly built site. For moving between `.com/zh/`, apex and `www`, follow the
migration steps in [baidu-resource-platform.md](baidu-resource-platform.md),
section 5.

## Claims to refuse

- Offshore routing "bypasses the firewall."
- An ICP record guarantees ranking, or filing equals licensing.
- Self-hosting fonts is mandatory — it removes a dependency, but prove the actual
  failure with network evidence first.
- A speculative SSR rebuild is needed when server-readable HTML already exists.
  Check the raw HTML before recommending it.
- Baidu Tongji is the only possible analytics tool. Selection depends on tested
  reachability, consent needs and integration.
- Every direct session is AI traffic, or `utm_source=deepseek` belongs on unrelated
  publisher links.

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
3. **All external hosts** — full inventory split into blocked and slow/unreliable.
4. **Form submission** — detects Google reCAPTCHA. reCAPTCHA must reach
   `google.com` *before the form will send*, so enquiries fail permanently from
   China even after the page finishes loading. Commercially this usually outranks
   the speed findings.
5. **Analytics coverage** — flags a site running only GA/GTM with no Baidu Tongji:
   Chinese traffic is invisible, so neither the problem nor the fix is measurable.
6. **Secondary** — cache headers, Chinese font stack, on-page ICP filing, Chinese
   social presence.

Reading the result:

- **BLOCKED + RENDER-BLOCKING** — fix first; it can hang the page.
- **BLOCKED, not render-blocking** — the feature silently fails, the page still
  draws. Analytics and tracking pixels sit here.
- **SLOW** — loads eventually, adds seconds. Worth self-hosting.

The score counts categories passed, not severity. One render-blocking Google script
matters more than four warnings.

## Commonly blocked hosts

Google (search, Fonts, hosted libraries, Tag Manager, Analytics, APIs, gstatic,
DoubleClick, AdSense), reCAPTCHA, Facebook (+ SDK), Twitter/X, YouTube, Instagram,
LinkedIn, Pinterest, Vimeo, Dropbox, WordPress.org, Gravatar, WhatsApp, Telegram.

Reachable but slow or unreliable: cdnjs.cloudflare.com, cdn.jsdelivr.net,
unpkg.com, Adobe Typekit, Font Awesome CDN, code.jquery.com, BootstrapCDN,
BootCSS, S3 US regions, raw.githubusercontent.com, github.com.

The tool holds the current table and matches subdomains by suffix. Treat the list
as a starting point — verify anything unusual against fresh network evidence rather
than asserting it.

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
6. **Server-rendered HTML** — Baidu runs no JavaScript.
7. **Simplified Chinese** titles, descriptions, content.
8. **Sitemap listing the `.cn` Chinese URLs**, submitted via Baidu Search Resource
   Platform.
9. **Baidu Tongji** for measurement.

Use this as a gap-analysis grid: requirement → what the site does today → verdict.
Most foreign brands fail on configuration, not construction — and items 2, 4 and 8
are each usually a single setting.

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

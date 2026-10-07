# Mainland speed and reachability — the free China tools

Mandatory in every audit (user requirement, 2026-10-05). Lighthouse from Europe
measures page weight, not what a Chinese visitor gets. These tools run from
probes inside China. All are free in guest mode with daily limits; run them in the
browser (claude-in-chrome), one tab, and save evidence as you go.

## Tools, in the order to run them

| Tool | URL | What it measures | Guest limits / quirks (2026-10) |
|---|---|---|---|
| **BOCE** | `https://www.boce.com/http/<host>` then paste the exact URL, 开始检测 | HTTP fetch from ~90 mainland nodes per carrier; resolved IP + IP owner; DNS pollution | Guest quota ran out after **one** test. Gives a share URL `boce.com/http/<date>_<id>.html`. Also has ICP/Whois, 拦截检测 (block check) and 微信拦截 (WeChat block) tools |
| **17CE** | `https://www.17ce.com/` → Get tab → 高级 for options → 检测一下 | HTTP fetch from ~180 nodes incl. HK/TW/overseas | Share link in 分享链接 box. Results need ~30 s; `get_page_text` fails until loading ends, so screenshot first |
| **ITDOG** | `https://www.itdog.cn/http/` | Quick test (快速测试), slow test (缓慢测试), full screenshot (完整截图) | Cloudflare check on entry usually clears by itself within ~6 s. Node detail (查看) asks for a click-captcha: do not solve it. Site returned 522 on a second visit |
| **chinaz** | `https://tool.chinaz.com/speedtest/<host>` | HTTP from ~33 nodes | Takes the host only (root URL), so redirects are included |

Never solve a captcha or log in. If a tool is blocked or out of quota, record it as
**blocked** with the reason.

## What to test

1. The exact Chinese landing URL (e.g. `https://www.example.cn/cn`), not only the root.
2. One product page and the form page, if quota allows.
3. Each third-party resource on the render or form path, tested as its own URL:
   Google Fonts CSS, `www.google.com/recaptcha/api.js`, `maps.googleapis.com`,
   the image CDN host, and the form POST host. This proves which dependency fails.
4. **A control URL** (`https://www.baidu.com/`) on any tool whose result looks
   strange. If overseas nodes fail on the target too, also test the same origin
   under its other domain. That separates tool failure, origin firewall and Great
   Firewall.

## How to read the results

- **Resolved IP and its owner** shows whether a China CDN exists. Same foreign IP
  on every node = no mainland edge.
- Count **failed / total nodes**. Report failures separately from timings, never
  averaged in.
- "下载时间异常" (download abnormal) with 0 bytes after connecting = TCP connected,
  no response. Seen when an origin firewall or rate-limit drops probe traffic.
- If tools disagree, report each one with its node count. Never quote the outlier
  alone. (Real audit: ITDOG 200 OK from mainland IPs vs BOCE 81/92 failed, 17CE and
  chinaz timeouts all on the Milan IP.)
- These tools fetch the HTML only. They do not render images, fonts or scripts.
  A full render still needs a mainland browser session. Say so in the report.

## Evidence to save (folder `evidence/mainland/`)

Per run: tool, exact URL, timestamp with timezone, node count, failed count,
fastest/slowest/average, resolved IPs with share percentage, share link,
screenshot, and a one-line reading. Finish with `SUMMARY_mainland_tests_<date>.md`
holding one table across all tools.

## Wording in the report

- "Measured from N mainland probes (tool, date): X of N failed; successful fetches
  took A–B s for the HTML alone."
- Lighthouse from abroad: "page weight and mobile CPU cost measured from Europe.
  This is not a mainland load time."

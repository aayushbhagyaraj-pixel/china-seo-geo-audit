# Baidu Search Resource Platform — the owner-side levers

The platform (百度搜索资源平台, ziyuan.baidu.com) is both the strongest evidence source
for crawl and index status and the only place the site owner can act on indexing
directly. For a foreign brand the bottleneck is almost always indexed page count,
and these are the levers that move it. None has a Google Search Console equivalent
that transfers one to one.

Use it when the client grants access. When they do not, every item below is
**blocked**, not unmeasured, and the report says which of the observable proxies
(section 6) were used instead.

## 1. Access and verification

- Site verification: HTML file, meta tag (`baidu-site-verification`) or CNAME
  record. The meta tag is visible in page source and is a cheap signal that the
  site was at least registered.
- Ownership levels differ. Some tools (快速收录, 站点logo, 品牌 features) have
  historically required 企业认证 (enterprise verification) or a filed ICP. A foreign
  brand with no Chinese entity may be unable to obtain them. **"Cannot obtain a
  verified account" is itself a finding about China posture**, not a missing data
  point.
- Historic quota figures and feature availability in circulating documentation
  are frequently stale. Confirm each in the owner's live UI and date the screenshot.

## 2. Getting URLs in — submission

| Lever | What it is | Audit check |
|---|---|---|
| **主动推送 (API push)** | POST a plain-text URL list to `http://data.zz.baidu.com/urls?site=<host>&token=<token>`. Baidu sets the daily quota per site and adjusts it with the value of what is pushed | Is anything pushed at all? Is the CMS wired to push on publish? Response shows `success` and `remain` |
| **Sitemap** | XML or TXT, submitted inside 普通收录. Mobile sitemaps can carry `<mobile:mobile type="pc,mobile"/>` annotations | Does the submitted sitemap match the live one? Does every URL in it return 200 to a non-JavaScript client? |
| **手动提交 (manual)** | Paste URLs into the UI | Emergency use only |
| **普通收录 vs 快速收录** | 普通收录 is the standard queue. 快速收录 is a faster, quota-limited queue that replaced the 熊掌号 privilege in 2020 and has been restricted or paid at various times | Record which queue is available to this account and its current quota, with a dated screenshot |
| **自动推送 (JS auto-push)** | A script (`zz.bdstatic.com/linksubmit/push.js`) that pushed the current URL on each visit | Reported discontinued. If found in a site's source, note it as inert legacy, and verify current status in the UI before saying more |

The wrong-domain sitemap is the most common single defect on dual-domain setups:
a CMS default emits the global domain's URLs, or the apex instead of the `www`
host. Check every URL in the sitemap, not the file's existence.

## 3. Mobile — 移动适配

Baidu keeps PC and mobile results separate and needs to be told how the two relate.
There is no Google equivalent, and a site that skips it can rank on PC and be
invisible on mobile, which is the larger surface.

| Site type | What Baidu expects |
|---|---|
| Responsive (自适应) | Declare it: `<meta name="applicable-device" content="pc,mobile">` and `<meta http-equiv="Cache-Control" content="no-transform">` (the second stops carrier transcoding) |
| Separate mobile URLs (跳转适配 / 代码适配) | Submit the PC↔mobile URL mapping in 移动适配, by rule (规则适配) or by URL pair file (URL对应), and use `<meta name="mobile-agent">` on PC pages |

Audit checks: is the declaration present on every page? Do PC pages redirect
mobile user agents correctly and to the corresponding page, not the homepage? Is
the mapping submitted and accepted in the platform?

## 4. Housekeeping tools

| Tool | Use |
|---|---|
| **抓取诊断 (crawl diagnosis)** | Fetch a URL as Baiduspider and see exactly what was received. One run settles rendering and blocking questions for that site. Quota-limited per day |
| **抓取异常 (crawl errors)** | DNS, connect, timeout and HTTP error counts as seen by the crawler. The only mainland-side view of reachability the owner gets for free |
| **抓取频次 (crawl frequency)** | Observed crawl rate, with a control to request a change. A flat zero line is proof of no crawling |
| **索引量 (index volume)** | Indexed URL count over time, with custom rules by path. The number to quote instead of a `site:` count |
| **流量与关键词 (traffic and keywords)** | Impressions, clicks, CTR and rank for queries where the site appeared. Export manually; there is no public API |
| **改版工具 (site change)** | Declare a domain change or URL-rule change so Baidu transfers signals. Mandatory on any migration, alongside 301s |
| **死链提交 (dead links)** | Submit a file of removed URLs so they are dropped promptly instead of counted as errors |
| **站点属性 (site properties)** | Site name, logo (200×133 px minimum), which feed the 基础信息 display rules |
| **HTTPS认证** | Declare the HTTPS version so Baidu prefers it |
| **站点子链 (sitelinks)** | Historically a submission-based feature for brand queries; availability varies |

## 5. Migration mechanics

A `.com/zh/` to `.cn` move, or an apex to `www` move, is where foreign brands
lose the little Baidu equity they had.

1. One-to-one 301 map, old URL to the corresponding new URL, not to the homepage.
2. Declare the change in 改版工具 before or at cutover.
3. Keep the old sitemap reachable until the new one is fully indexed, then submit
   dead links for anything that has no successor.
4. Decide the fate of the old Chinese pages explicitly: 301, `noindex`, or retire.
   Two live Chinese versions of one brand will split authority indefinitely, and
   the older one usually wins because it is already indexed.
5. Check the global site's `robots.txt` and CDN bot rules. Western-tuned
   configurations frequently disallow Baiduspider and Bytespider by default.
6. After cutover, watch 抓取异常 and 索引量 daily for two weeks.

## 6. When there is no access — observable proxies

Label each **inferred**, and say what it cannot establish.

| Proxy | What it can show | What it cannot |
|---|---|---|
| `site:` query on Baidu | Explicit "no results" is meaningful. A count is not | Index completeness |
| A second engine's `site:` (360, Sogou) | Corroboration | Baidu's own state |
| Fetch each sitemap URL with a Baiduspider user agent from outside China | Status code and whether a challenge page is served before content | What Baidu received from its own IPs |
| `baidu-site-verification` meta in source | The site was registered at some point | Current ownership or activity |
| Push script in source | Someone once wired submission | Whether it works today |
| Server logs, verified by reverse DNS | Real Baiduspider visits | Anything, if verified by user agent alone |

## Sources

Primary, dated where the platform shows a date:
[Platform tool manual](https://ziyuan.baidu.com/college/courseinfo?id=267) ·
[普通收录 manual](https://ziyuan.baidu.com/college/courseinfo?id=267&page=2) ·
[Tool update announcements](https://ziyuan.baidu.com/college/articleinfo?id=3019) ·
[Crawl diagnosis manual](https://ziyuan.baidu.com/college/courseinfo?id=267&page=9) (2020-08-14).

Confirm any quota, availability or discontinuation statement in the live UI
before it enters a deliverable. This platform changes without notice.

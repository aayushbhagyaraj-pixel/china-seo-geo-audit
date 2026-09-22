# Baidu search visibility

Baidu is not Google with Chinese results. The differences below change what you
recommend, not just how you phrase it.

## Baidu vs Google — the differences that matter

| | Google | Baidu |
|---|---|---|
| hreflang | supported | **not supported** — every current source agrees; verify against Baidu's own documentation before stating it as permanent |
| Language signal | hreflang | **`content-language` meta + separate domain** |
| canonical | supported | supported |
| JavaScript | rendered | render crawler exists (`Baiduspider-render/2.0`), but handling is unreliable — server-render critical content. See [technical-onpage.md](technical-onpage.md) |
| Speed | ranking factor | **<2 s preferred; ≥3 s actively suppressed** (闪电算法, Lightning Algorithm) |
| Multilingual sites | handled well | crawl budget wasted on non-Chinese pages |
| Language in URL parameters | tolerated | **causes crawl failures** |
| Chinese characters in URLs | fine | avoid — use pinyin or English |

Consequences worth stating plainly in a report:

- A slow first screen is a **ranking penalty under published Baidu documentation**,
  not only a UX complaint. Under 2 s gets preference and more impressions; 2–3 s is
  neutral; 3 s and above is suppressed.
- Client-side-rendered content is at risk on Baidu. A render crawler exists, but
  its handling is unreliable in practice, so critical content belongs in the
  server-rendered HTML. Settle it for the specific site with Baidu's 抓取诊断
  (crawl diagnosis) tool, which shows what the crawler actually received, and
  confirm what is in the raw HTML before concluding anything about coverage.
- An hreflang set that is correct for Google is harmless but inert for Baidu. The
  missing `content-language` meta is the real gap.
- A sitemap listing the wrong domain's URLs (a common CMS default on dual-domain
  setups) will not get the Chinese pages indexed, no matter how well they are
  written. Check what the sitemap actually contains, URL by URL.

## Owner-side evidence

Where the client has access, authenticated **Baidu Search Resource Platform**
(ziyuan.baidu.com) exports are the strongest crawl and index evidence:

- Crawl diagnosis — inspect the content the crawler actually received, and access
  failures. Historic quota figures in circulating documentation require current
  verification in the owner's UI.
- Indexing and submission tools: 主动推送, sitemap, 普通收录 / 快速收录 quotas,
  移动适配, 改版工具, 死链提交.
- 流量与关键词: impressions, clicks and rank for queries where the site appeared.

The levers themselves, what each does and how to audit them without access, are
in [baidu-resource-platform.md](baidu-resource-platform.md).

Primary references — all useful, all dated, so label them historical official
guidance rather than current behaviour:

- Resource-platform guide: https://ziyuan.baidu.com/doc/index
- Crawl diagnosis manual: https://ziyuan.baidu.com/college/courseinfo?id=267&page=9 (dated 2020-08-14)
- Page quality standard: https://ziyuan.baidu.com/college/articleinfo?id=3430 (dated 2022-07-27)
- Quality-content Q&A: https://ziyuan.baidu.com/college/articleinfo?id=2953 (dated 2020-04-09)
- Baidu AI search API: https://ai.baidu.com/ai-doc/AppBuilder/wm88pf14e — distinguishes answers, retrieval references, and references supplied to the model. Keep API behaviour separate from consumer ERNIE results.

A diagnostic tool displaying the first 200 KB of a page is **not** proof that
Baiduspider indexes only 200 KB. Do not turn a historic diagnostic limit into a
universal production crawler limit.

## SERP observation

A Baidu result page is ads (竞价), 品牌专区, Baidu's own property cards (阿拉丁:
百科, 知道, 图片, 文库, 爱采购, 精选笔记), 百家号 articles and increasingly an AI
summary, and then organic results. Report rank with what sits above it, per
[keyword-rank-tracking.md](keyword-rank-tracking.md), and use
`scripts/baidu_serp.py` for the observed table where DataForSEO access exists.

- Record **desktop and mobile separately** — they differ.
- Keep SEM strictly separate from organic results. A paid placement is not a rank.
- `site:` observations establish neither complete index coverage nor absence.
- Record the date, the exact query, the interface, the observed location and the
  account state, exactly as for AI runs.
- What a Chinese buyer actually sees when searching the brand name is a finding in
  itself — capture it, including which third-party domains outrank the owned one.

## Crawler permissions

Check robots.txt for the Chinese crawlers specifically, not just `Baiduspider`:

| Crawler | Owner |
|---|---|
| `Baiduspider` | Baidu |
| `Baiduspider-render` | Baidu (rendering fetch) |
| `Sogou web spider` | Sogou |
| `360Spider` / `HaosouSpider` | Qihoo 360 |
| `YisouSpider` | Shenma (UC/Alibaba) |
| `Bytespider` | ByteDance — feeds Doubao and Douyin surfaces |
| `PetalBot` | Huawei Petal Search |

`Bytespider` is frequently disallowed by default in Western-tuned robots.txt files
and by some CDN bot-management rules. On a China audit that is a real finding:
it removes the site from ByteDance's AI and search surfaces. Check CDN-level bot
rules as well as the file — a permissive robots.txt does not prove access.

Crawl permission is not crawling; crawling is not indexing; indexing is not
ranking. Report each only where you observed it.

## Content and keyword work

Map native Chinese buyer intent — not translated English keywords — to useful
destination pages:

1. Division identity: who this business is, and what it is not.
2. Supplier capability and scale.
3. Technical selection guidance.
4. Specifications and evidence, with explicit units and test methods.
5. Cooperation, sampling and procurement process.
6. Partner and reference proof.
7. Contact, with the right internal owner.

Distinguish retail, prescription and finished-product queries from component
procurement queries — they look similar and convert completely differently.

For supplied keyword or SEM sheets: retain cell addresses, campaign/adgroup grain,
duplicate rows and original flags. Calculate aggregate CTR as total clicks / total
impressions only when the grain is compatible. Missing cost and qualified
conversion data prevent CPA or ROI conclusions. Zero impressions do not prove zero
demand. Treat keyword deletions and negative-keyword suggestions as review
proposals, not applied changes.

Do not fabricate keyword volumes or product claims. Do not prescribe a fixed
keyword density, a bulk article count, or thin city pages. A city page needs
genuine local information; never invent an office.

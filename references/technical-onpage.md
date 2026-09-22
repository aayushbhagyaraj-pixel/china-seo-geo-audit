# Technical and on-page audit for Chinese search

The universal technical layer, stated in Baidu's terms. Most of it transfers from
Western practice; the parts that do not are marked, and a few things that are
standard advice for Google are actively wrong here.

Every official document below carries its **publication date**, because Baidu's
documentation is old and much of it is quoted in circulating guides as if current.
Several of these documents recommend products Baidu has since discontinued.

## What Baidu officially publishes

| Document | Date | What it governs |
|---|---|---|
| [闪电算法 announcement](https://ziyuan.baidu.com/wiki/1590) | 2017-10-19 | Mobile first-screen speed thresholds |
| [Baiduspider user-agent identification](https://ziyuan.baidu.com/college/articleinfo?id=1002) | 2017-04-27 | Crawler variants, including the render crawler |
| [网页标题规范 (title specification)](https://ziyuan.baidu.com/college/articleinfo?id=2728) | 2018-11-15 | Title format, prohibitions, penalties |
| [落地页体验白皮书 5.0](https://ziyuan.baidu.com/college/articleinfo?id=2921) | 2020-03-19 | Mobile landing-page layout, ads, interaction |
| [基础信息设置规范](https://ziyuan.baidu.com/college/documentinfo?id=3390) | updated 2022-06-16 | Site name, homepage title, description, logo |
| [页面质量标准](https://ziyuan.baidu.com/college/articleinfo?id=3436) | 2022-07-27 | Content quality tiers |
| [网页质量白皮书](https://ziyuan.baidu.com/college/documentinfo?id=1337) | 2014-08-07 | The original three-axis quality framework |

Cite these by date. "Baidu says" without a date is not evidence, and a 2017
document is not a statement about 2026 behaviour.

## Speed — the published rule

**闪电算法 (Lightning Algorithm), announced 2017-10-19.** For mobile pages:

| First-screen load | Effect |
|---|---|
| Under 2 s | Ranking boost and traffic preference |
| 2–3 s | Neutral |
| 3 s or more | Suppressed |

This is a **published ranking rule**, not a UX opinion. Say so in the report — it
changes how a client's engineering team prioritises the work.

Note what the metric is: **first-screen load time**, not LCP, INP or CLS. Baidu
does not publish Core Web Vitals thresholds, and a Lighthouse score from abroad
does not measure it. Measure first-screen from mainland nodes.

Baidu's own optimisation recommendations in that announcement are conventional
performance engineering: compress and merge same-type resources server-side to cut
request count and payload, use browser caching for shared resources, use CDN
acceleration, lazy-load non-critical images, put CSS in `<head>` so it does not
block render, put JavaScript at the end or load it async, and set explicit
dimensions on non-text elements to prevent reflow.

**The trap:** that same announcement recommends **MIP (Mobile Instant Pages)**,
Baidu's AMP equivalent. MIP has since been discontinued. Do not recommend it, and
flag it if a client's existing agency proposal includes it — it is a reliable
signal that the proposal was assembled from old documentation.

## Crawling and rendering — correct the absolute claim

A widely repeated claim says Baidu executes no JavaScript at all. **That is wrong
as an absolute**, and the skill should not repeat it.

Baidu officially documents a render-capable crawler,
[`Baiduspider-render/2.0`](https://ziyuan.baidu.com/college/articleinfo?id=1002)
(2017-04-27), in mobile, PC and mini-program variants alongside plain
`Baiduspider/2.0`.

What the evidence actually supports, stated at the right strength:

- **Observed / official:** a render crawler exists and is documented.
- **Secondary consensus, 2026:** JavaScript handling remains unreliable in
  practice compared with Googlebot, and server-side rendering or prerendering is
  still the standard recommendation for Chinese search.
- **Therefore:** recommend server-rendered critical content — but as a risk
  reduction supported by observation, not because "Baidu cannot render."

**Settle it empirically for the specific site.** Baidu's 抓取诊断 (crawl
diagnosis) tool in the Search Resource Platform shows the content the crawler
actually received for a given URL. That single observation outranks every general
claim, in either direction. Where the client has platform access, run it and quote
it. Where they do not, compare raw HTML against rendered HTML yourself and label
the conclusion **inferred**.

Do not recommend an SSR rebuild before checking whether the critical content is
already in the raw HTML.

### Crawler variants

| User agent | Purpose |
|---|---|
| `Baiduspider/2.0` | Standard crawl, PC and mobile variants |
| `Baiduspider-render/2.0` | JavaScript rendering, PC and mobile variants |
| `Baiduspider-render/2.0;Smartapp` | Smart mini-program indexing |

Verify a claimed Baiduspider visit by reverse DNS, not by user-agent string alone —
the UA is trivially spoofed and log-based "Baidu crawled us" claims are common and
often wrong.

## On-page in Chinese

### Title

Baidu's [title specification](https://ziyuan.baidu.com/college/articleinfo?id=2728)
(2018-11-15) prescribes **core keyword + modifier**, with no more than three
modifiers, and gives per-page-type formats:

| Page type | Format |
|---|---|
| Homepage | 站点名/品牌 – slogan/官网 |
| Category | 类别名 – 上级类别 – 站点名 |
| Content | 文章标题 – 类别(optional) – 站点名 |

It prohibits titles that mismatch page content to induce clicks, keyword stacking
or repetition of semantically similar terms, fake "official site" claims, and
promising functionality the page does not deliver. It also gives punctuation
normalisation guidance — standardise dashes, limit brackets, remove emoji and
trailing punctuation.

**Penalties are explicit:** Baidu rewrites titles it judges over-optimised or
ambiguous, and applies search-result display restrictions to severe cases. A
rewritten title is a diagnosable symptom — if the SERP shows a title that is not
the one in the source, that is a finding, not a rendering quirk.

**On length:** the official specification states no hard character limit. The
[basic information standard](https://ziyuan.baidu.com/college/documentinfo?id=3390)
(2022-06-16) gives roughly 50 characters for the homepage description. Agency
sources circulate figures between 24 and 28 Chinese characters, or around 60
bytes, and they do not agree with each other.

Treat length as a **byte and display budget, measured, not quoted**: Chinese
characters consume more bytes than Latin ones, so an English-derived character
count transplants badly. Observe where truncation actually falls in a current
desktop and mobile SERP for the site in question, record the date, and report that
instead of a number from a blog.

### The alignment rule that has no Western equivalent

Baidu's basic information standard requires the homepage title to **align across
three places**: the page source, what the page visibly displays, and the **ICP
registration details**. A mismatch between the site's registered entity name and
its title is a Baidu-specific finding with no Google analogue. Check it.

The same document sets rules for the site name — high distinguishability, no
generic terms, and no contact information, marketing language (招商, 微商),
superlatives that breach Chinese advertising law, or prohibited content — and for
the logo: minimum 200×133 px, upper left, clear, non-transparent background.

Chinese advertising law restricts superlatives (最好, 第一, 国家级 and similar)
with real penalties. Flag them in Chinese copy. This is a legal exposure finding,
not a style note.

### Word segmentation

Chinese is written without spaces, so Baidu performs 分词 (word segmentation) to
identify terms. Two consequences:

1. Keyword-density thinking imported from English does not transfer. Do not
   prescribe a density figure — the skill rejects this generally, and segmentation
   is the mechanical reason it is meaningless here.
2. How a phrase segments determines what it matches. A term that reads naturally
   to a human may segment into components that match a different intent. This is
   why keyword lists must be built by a native speaker against real Chinese buyer
   language, not translated from an English set.

### Script and URLs

Simplified Chinese for mainland. Traditional signals Hong Kong or Taiwan and is a
positioning error on a mainland site, not merely a style choice.

URLs: pinyin or English, hyphenated. Avoid Chinese characters in URLs, and avoid
carrying language in query parameters — both are associated with crawl failures on
Baidu. Language belongs in the path or the domain.

## Structured data — do not port the Google checklist

**Baidu does not support Schema.org markup for rich results.** The entire
Google-oriented schema apparatus — JSON-LD types, the rich-results eligibility
list, the deprecation timeline for HowTo and FAQPage — is irrelevant to Baidu
ranking and display. Recommending it as a China measure is a common and visible
error in agency proposals.

What Baidu has instead:

- **Structured data submission** through the Search Resource Platform and Baidu's
  open platform, using Baidu's own formats rather than Schema.org.
- **阿拉丁 (Aladdin)** — a partnership program producing enhanced result
  presentations. Historically restricted to major or authoritative Chinese sites
  and closed-beta participants. Business-information rich results generally
  require a Chinese company registration and ICP filing.

For a foreign B2B brand, Aladdin is realistically out of scope. Say that plainly
rather than listing it as an action.

Existing Schema.org markup can stay — it costs nothing and may help non-Baidu
engines and AI parsers. But **treat "schema improves Chinese AI visibility" as an
untested hypothesis**, not a recommendation. The skill's claims-to-reject list
covers this.

## Content quality

Baidu's [网页质量白皮书](https://ziyuan.baidu.com/college/documentinfo?id=1337)
(2014-08-07), extended by the [页面质量标准](https://ziyuan.baidu.com/college/articleinfo?id=3436)
(2022-07-27), judges pages on three axes:

1. **内容质量 (content quality)** — graded in four tiers: 优质 (high), 中等
   (medium), 低质 (low), 无价值 (worthless). Judged on 专业度 (professional
   depth) and 完整性 (completeness).
2. **浏览体验 (browsing experience)** — whether reading is unobstructed, whether
   advertising interferes, whether the main content is prominent.
3. **可访问性 (accessibility)** — resource validity and whether the main content
   resource is actually browsable.

This is Baidu's functional equivalent of E-E-A-T, and it is **weighted differently**.
Professional depth and completeness carry the load; author-identity signals, which
dominate Google's framework, are not the organising principle. Do not audit a
Chinese site against Google's E-E-A-T rubric and report the gaps as Baidu findings.

## Mobile landing-page standards

The [落地页体验白皮书 5.0](https://ziyuan.baidu.com/college/articleinfo?id=2921)
(2020-03-19) is unusually prescriptive, and it is enforceable. Mobile is the
primary surface — Baidu's mobile share materially exceeds its desktop share.

| Rule | Threshold |
|---|---|
| First-screen load | within 1 s (stricter than 闪电算法's 2 s) |
| Main content share of first screen | ≥ 50% |
| Minimum font size | 10pt |
| Line-height ratio | > 1.4 |
| Top banner ad | ≤ 10% of screen area |
| Ads between title and body, article pages | zero |
| Ads per viewport, list pages | < 1/3 of screen |
| Function buttons | ≤ 10% of screen area |
| "Expand full text" control | once per page, not on first screen |

Prohibited: floating ads, pop-ups, auto-playing animation, and forcing an app
download where the web page could serve the function.

For a B2B site the ad rules rarely bite, but **the layout rules do** — consent
banners, chat widgets, cookie notices and interstitials all consume first-screen
area and can breach the 50% main-content rule. Check the first screen as rendered
on a mainland mobile device, not a desktop emulator.

### The WeChat in-app browser

A large share of Chinese mobile traffic opens links inside WeChat's embedded
browser rather than a standalone one. It has its own rendering quirks and known
incompatibilities with some Western UI frameworks.

If the client distributes anything through WeChat — and most B2B brands in China
do — the WeChat in-app browser is a required test target. A page that renders
correctly in mobile Chrome and breaks in WeChat is a real and frequently missed
finding.

## Hosting, ICP and CDN — get the distinction right

Two different things, routinely conflated:

| | ICP备案 (filing) | ICP许可证 (commercial licence) |
|---|---|---|
| Applies to | Informational, non-commercial sites | Sites charging users for digital services |
| Required for | Any site hosted on mainland servers | Commercial internet information services |
| Foreign-owned entity | Needs a Chinese legal entity (WFOE, JV or sponsor) | Majority foreign-owned companies generally cannot hold one |

Both require a Chinese business licence. Neither is a ranking guarantee.

**Mainland CDN acceleration also requires an ICP filing** — this surprises clients
who assume a CDN sidesteps the hosting question. It does not.

The standard compromise for a foreign brand without a Chinese entity is Hong Kong
or offshore hosting with China-capable routing (CN2 GIA and similar). It avoids the
filing requirement and accepts higher latency than mainland hosting.

Verify current provider coverage rather than assuming it — mainland points of
presence change. Akamai is reported to have ended its mainland presence on
2026-06-30, and several major edge platforms (Fastly, Vercel, Netlify) have no
mainland nodes and serve China from Hong Kong, Tokyo, Seoul or Singapore. Treat any
specific provider claim, including that one, as requiring fresh confirmation before
it enters a deliverable.

For legal hosting requirements, consult current authoritative rules. Do not issue a
blanket legal conclusion in an SEO report.

Data protection is the other compliance line an SEO audit crosses without
noticing: a contact form that sends a mainland user's name and phone number to a
server abroad is a PIPL cross-border transfer. The triggers (PIPL, 数据安全法,
网络安全法, 等保 2.0, 电子商务法) are listed in
[china-b2b-surfaces.md](china-b2b-surfaces.md), section 7. Flag them with the
owner; leave the conclusion to counsel.

## Do not recommend these — discontinued

| Product | Status |
|---|---|
| **MIP** (Mobile Instant Pages) | Discontinued. Still recommended inside Baidu's own 2017 Lightning Algorithm announcement |
| **熊掌号** (Xiongzhang, "Bear Paw") | Taken offline March 2020. Carried day-level indexing privilege; circulating guides still promise it |

Both appear regularly in agency proposals assembled from old material. Finding
either in a client's existing China plan tells you how current that plan is.

## Audit beyond Baidu

Baidu leads, but the Chinese search market is more fragmented than the "Baidu is
China's Google" framing suggests, and published share figures are **highly
volatile** — Baidu has been measured anywhere between roughly 40% and 65% across
2025–2026 depending on source, device and method.

Worth checking alongside Baidu, with the share figure treated as indicative only:

- **Bing** — materially present in China and reported to have grown substantially
  on desktop. Also the index behind ChatGPT web search, so it matters twice.
- **Haosou / 360搜索** — meaningful share.
- **Sogou** — smaller share, but integrated with WeChat and QQ search, which makes
  it disproportionately important for a brand distributing through WeChat.
- **Shenma (神马)** — Alibaba, mobile-focused.

Quote any market-share number with its source, date, device split and method, per
the skill's evidence rules. Numbers in this area disagree wildly and are quoted
confidently.

## Adapting the AI citability method

The passage-level citability approach transfers in structure — answer-first,
self-contained, specific, attributed — because it describes how a language model
extracts text, not something Google-specific.

Two adaptations:

**Word-count figures do not transfer.** The 134–167 word optimal-passage range
comes from English-language research. Chinese conveys more meaning per character,
so the equivalent range is unvalidated. Do not quote the English figure for Chinese
content. Write self-contained passages and measure what actually gets cited in the
panel.

**The authority platforms swap entirely:**

| Western signal | Chinese equivalent |
|---|---|
| Wikipedia | 百度百科 (Baidu Baike) |
| Reddit | 知乎 (Zhihu) |
| YouTube | 哔哩哔哩 (Bilibili), 抖音 (Douyin) |
| LinkedIn | 脉脉 (Maimai), WeChat 公众号 |
| Quora | 知乎, 百度知道 |
| — | 百度文库 (Baidu Wenku), 小红书 (Xiaohongshu) |

Agency sources claim specific mappings — that ERNIE weights Baike and Wenku, that
DeepSeek leans on Zhihu and technical documentation, that WeChat articles feed
Baidu indexing. **These are testable hypotheses, not established facts.** No
reviewed primary documentation establishes them, and the skill's claims-to-reject
list stands.

The right response is not to repeat them and not to dismiss them, but to **put them
in the prompt panel**. Record which platforms actually appear in retrieved
references and inline citations per engine, then report the observed distribution
with its denominator. That converts an agency claim into evidence for this brand,
which is the only form in which it belongs in a deliverable.

## Sources

Primary — Baidu Search Resource Platform:
[Lightning Algorithm](https://ziyuan.baidu.com/wiki/1590) ·
[Baiduspider user agents](https://ziyuan.baidu.com/college/articleinfo?id=1002) ·
[Title specification](https://ziyuan.baidu.com/college/articleinfo?id=2728) ·
[Landing page whitepaper 5.0](https://ziyuan.baidu.com/college/articleinfo?id=2921) ·
[Basic information standard](https://ziyuan.baidu.com/college/documentinfo?id=3390) ·
[Page quality standard](https://ziyuan.baidu.com/college/articleinfo?id=3436) ·
[Web page quality whitepaper](https://ziyuan.baidu.com/college/documentinfo?id=1337)

Secondary, used as hypotheses and for market context, not as ranking evidence:
[Dragon Metrics on Baidu rich snippets](https://www.dragonmetrics.com/how-to-get-organic-traffic-on-baidu-in-a-crowded-world-of-rich-snippets/) ·
[Jademond on Baidu crawlers](https://www.jademond.com/magazine/understanding-baidu-spiders/) ·
[Chinafy Baidu technical checklist](https://www.chinafy.com/blog/technical-seo-checklist-for-baidu) ·
[AppInChina on ICP filing](https://appinchina.co/blog/the-complete-guide-to-chinas-icp-filing/) ·
[NN/g on WeChat UX](https://www.nngroup.com/articles/wechat-integrated-ux/) ·
[The Egg on Chinese search engines](https://www.theegg.com/seo/china/most-popular-search-engines-in-china)

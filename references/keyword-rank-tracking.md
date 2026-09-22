# Keyword discovery and rank tracking on Baidu

Rank on Baidu is not a position in ten blue links. Above the first organic result
there can be paid ads (竞价, marked 广告), a brand zone (品牌专区), Baidu's own
properties in enhanced cards (阿拉丁: 百度百科, 百度知道, 百度图片, 百度文库,
百度爱采购, 精选笔记, 百度有驾), 百家号 articles, and increasingly an AI-generated
summary. An organic "position 3" can sit below the fold on desktop and off the
first two screens on mobile. Report rank in a way that accounts for that, or do not
report it.

## 1. Instruments — use what is available, mark the rest blocked

| Need | Instrument | Access | Label |
|---|---|---|---|
| Observed SERP with features, desktop and mobile | DataForSEO Baidu SERP API (`scripts/baidu_serp.py`) | API key, pay per call, no Chinese account | observed via API |
| Related searches, autosuggest | Same API (`related_searches` items), or manual 下拉框 / 相关搜索 capture with screenshot | free / API | observed |
| Search volume, keyword mining | 5118 (API available), 爱站, 站长之家 (Baidu Index API) | Chinese account, RMB payment | client-provided or blocked |
| Demand over time | 百度指数 (index.baidu.com) | Baidu login, +86 | observed (screenshot) or blocked |
| Impressions, clicks and rank for the owned site | Search Resource Platform 流量与关键词 | owner access, manual export | client-provided |
| Ongoing monthly tracking | Dragon Metrics, AccuRanker (Baidu desktop + mobile), Semrush position tracking | subscription | retainer decision, not an audit dependency |

Ahrefs does not track Baidu. Google Keyword Planner volumes for Chinese terms
describe Google's Chinese-language traffic, mostly outside the mainland, and are
not Baidu demand.

**百度权重 (Baidu weight) is not a Baidu metric.** It is an estimate invented by
third-party tools (爱站, 站长之家) from their own keyword databases. Quote it only as
"third-party estimate", never as a Baidu figure.

## 2. Definition of rank

Record all of the following for every keyword and device, or the row is not
comparable to a later re-test:

| Field | Rule |
|---|---|
| Organic position | Position among organic results only, counted from 1 |
| Absolute position | Position among all items on the page, including ads and feature blocks |
| Features above | Count and type of non-organic blocks above the first owned organic result |
| Device | Desktop and mobile are separate indexes and separate SERPs. Never merge |
| Location | Country or city code used. Baidu personalises by city |
| Login state | API fetches are logged out. Manual checks must be in a private window, logged out |
| Date and time with timezone | Baidu SERPs change within hours |
| Method | API (datacenter fetch, provider named) or manual (browser, network location) |

**Visibility-adjusted rank** = absolute position of the first owned organic result.
Report it alongside organic position. A brand at organic 1 and absolute 7 has a
different problem from a brand at organic 1 and absolute 1.

What a single fetch does not establish: what a specific buyer in a specific city
saw, or a stable rank. Repeat before reporting a change.

## 3. Building the keyword set

Translated English keywords are the most common mistake. Chinese queries are built
by a native speaker from evidence, and they tend to be longer and more
conversational than English ones. Sources, in order of value:

1. **Related searches and autosuggest** on the brand name and category terms. These
   are real query language. The audit script returns `related_searches` for every
   keyword it fetches.
2. **The owned site's 流量与关键词 export**, if any impressions exist.
3. **Competitor and marketplace language**: how 1688 and 爱采购 listings describe the
   category, how 知乎 questions phrase the comparison.
4. **Keyword tools** (5118 etc.) for volume, once the set exists. Volume ranks the
   set; it does not create it.

Group by intent before anything else, because the SERP composition differs by
group and so does the destination page:

| Group | Pattern | Example shape |
|---|---|---|
| Brand navigational | brand, brand + 官网, brand Chinese name | `[品牌] 官网` |
| Brand + qualifier | brand + 价格 / 供应商 / 代理 / 真假 | `[品牌] 中国代理` |
| Definition | X 是什么 / 中文是什么 | `[材料] 面料是什么` |
| Comparison | X和Y的区别 / X vs Y | `[品牌]和[竞品]的区别` |
| Category, unbranded | material + application + 供应商 / 厂家 / 品牌 | `[应用] [材料] 供应商` |
| Procurement | 采购 / 批发 / 定制 / 样品 | `[材料] 定制 起订量` |
| Retail and aftermarket | 改装 / 修复 / 清洁 (exclude from B2B rank unless in scope) | `[材料] 座椅 改装` |

Separate retail and refit intent from OEM procurement intent explicitly. They share
vocabulary and convert completely differently.

## 4. Baseline and re-test table

One row per keyword × device. Columns: keyword · intent group · date · device ·
location · organic position (owned) · absolute position (owned) · features above ·
top three domains · whether an AI summary was present · method.

Re-test with the identical set, device, location and method. Report deltas with
both dates. Interpret changes alongside site changes, model releases and campaigns;
a rank move alone does not prove attribution.

## 5. Reading the SERP for the brand name

The brand SERP is a finding in itself. Record which domains outrank the owned site,
whether any of them is a reseller, an unauthorised agent, a domain squatter or a
competitor bidding on the brand, and whether 品牌专区 or a paid brand ad exists.
Keep SEM separate from organic in the table, but do report whether a third party
is buying the brand term. That is a brand-protection finding, not an SEO one.

## 6. Do not

- Quote a volume you did not observe in a named tool on a named date.
- Present SEM impressions as demand or as rank.
- Merge desktop and mobile.
- Report "position 3" without what sits above it.
- Prescribe keyword density. Baidu segments (分词) Chinese text; density is
  meaningless here.

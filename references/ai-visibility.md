# Chinese AI visibility — measurement protocol

This is a measurement protocol, not a disclosed ranking algorithm. Its value comes
entirely from isolation and comparability: results from runs that were not isolated
cannot be compared to each other or to a later re-test.

## The platforms, and how to keep them apart

| Consumer surface | Owner | Keep separate from |
|---|---|---|
| DeepSeek | DeepSeek | the DeepSeek API; DeepSeek models hosted on Alibaba or elsewhere |
| Qwen / 通义 | Alibaba | Model Studio API; Qwen Code (a developer coding agent) |
| ERNIE / 文心一言 | Baidu | Baidu AI Search API; Baidu web SERPs |
| Doubao / 豆包 | ByteDance | Volcengine developer search MCP |
| Kimi | Moonshot | the Kimi platform API (search / search_pro / fetch) |
| Yuanbao / 元宝 | Tencent | TokenHub Chat/Responses protocols |
| 文小言 (ERNIE consumer app, renamed) | Baidu | the ERNIE API; the in-SERP answer below |
| **Baidu AI answer inside the SERP** (百度AI搜索 / 智能回答) | Baidu | organic rank on the same page; the 文小言 app. It is a third surface: neither a chat app nor a blue link, and it sits above organic results |
| 夸克 (Quark) | Alibaba | the Qwen/通义 app; it is a separate AI-search product with its own retrieval |
| 智谱清言 (ChatGLM) | Zhipu | the GLM API |
| 海螺 (Hailuo) | MiniMax | the MiniMax API |

Choose the three platforms for a panel from this table by the buyer's likely
habit, and say why. DeepSeek, Doubao and the Baidu in-SERP answer are a defensible
default for a B2B industrial buyer in 2026; record the choice as proposed.

A developer API's documented search parameters never disclose the consumer app's
ranking, publisher weights or answer behaviour. An Alibaba-hosted DeepSeek and
native DeepSeek are different surfaces. Supporting search in both API and app does
not establish parity of rankings, sources or answers.

## Access — settle this before scoping the phase

Most Chinese consumer assistants require a **+86 mobile number** and real-name
registration, and several refuse foreign numbers outright. Web versions may allow
a few guest prompts; those runs must be logged as guest-state and are not
comparable with signed-in runs.

Options, in order of preference:

1. The client's China team runs the panel from a mainland network on a mainland
   account, following this protocol, and hands over the run log and screenshots.
2. A mainland colleague or partner does the same.
3. A guest or foreign-registered session, clearly labelled, for direction only.

Record for every run: the account type, the network location (a VPN in the path
changes retrieval and must be stated), the device, and the app version. If none of
the options exists, the phase is **blocked**. Say so; do not present three guest
prompts as a measurement.

## Isolation rules — non-negotiable

1. **New empty conversation for every prompt and every repeat.** Verify the empty
   state before submitting. A new browser tab is insufficient if it reopens an
   existing conversation.
2. **No seeding.** No brand documents, no earlier answers, no follow-up context, no
   domain restriction on a discovery prompt.
3. **Consistent conditions within each engine's batch** — interface, model where
   displayed, reasoning mode, search setting. Record any change.
4. **Search enabled ≠ retrieval ran.** These are two separate observations. A model
   may answer without searching; a search may time out and leave an answer with no
   sources. Check returned calls, results and errors — a setting is an intention,
   not proof.
5. **Record what you cannot control.** Login state, browser session, observed
   location, device, network location, timestamp with timezone, retained answer
   URL, and memory/personalization controls where exposed. A fresh chat prevents
   visible within-thread carryover; it does not prove account-level personalization
   is absent.
6. **Incognito is not personalization-free.** It separates ordinary cookies, but
   another incognito tab does not create an isolated session — Chrome retains
   temporary site data until all incognito windows close — and signing in still
   identifies the account. Runs on a normal connected profile must not be described
   as incognito or personalization-free.
7. **Do not infer mainland location** from the answer language or the engine's
   nationality. State the workstation's actual network location, or state that it
   is unverified.
8. **Preserve the sidebar and history separately** from answer text. Past
   conversation titles containing the brand name will otherwise inflate
   brand-mention counts.
9. **Reopening a retained answer is not another independent run.** Log
   browser-control failures, interrupted runs and recovered answers separately.

## Prompt panel design

A workable initial split of 30 prompts:

| Group | Count | Purpose |
|---|---|---|
| Branded identity | 5 | Does the assistant describe the right division and scope? |
| Unbranded supplier discovery | 8 | Is the brand named at all, unprompted? |
| Technical evaluation | 6 | Are technical claims accurate and supported? |
| Comparison | 4 | How is the brand positioned against the competitor set? |
| Cooperation / procurement | 3 | Is the buying process described correctly? |
| City / event scenarios | 4 | Local and situational discovery |

Three independent sessions per platform gives 30 × 3 platforms × 3 repeats = **270
completed answers**. This is a proposed workload adapted to scope and access — not
an evidence-backed universal minimum, and not a representative sample of all users.
Pending and failed runs do not count toward that denominator.

**Two tiers.** A first audit normally runs a **quick scan**: 10 prompts (2 branded,
4 unbranded discovery, 2 technical, 2 comparison) × 3 platforms × 1 fresh session.
It establishes direction and surfaces identity errors; it does not produce a
quotable rate. The **full panel** above is the scoped follow-on and the baseline
for re-tests. State the tier in the deliverable. Never quote a percentage from the
quick scan.

Branded, cooperation and comparison prompts must **not** inflate the unbranded
recommendation denominator. Keep the groups separate throughout.

Prompt templates for a B2B component supplier. Fill the brackets with approved
facts for the brand under audit — the shape of each prompt is what matters, and a
prompt written for one brand must never be reused verbatim for another.

**Unbranded discovery** — is the brand named at all, unprompted?

> 我是一家[行业]品牌的产品经理，正在寻找[组件类别]供应商。应考虑哪些企业，为什么？
> *(I'm a product manager at a [industry] brand looking for [component category] suppliers. Which companies should I consider, and why?)*

**Branded identity** — is the audited division distinguished from its siblings?

> [品牌]的[目标事业部]业务与[相邻事业部]业务有什么区别？
> *(What is the difference between [brand]'s [target division] business and its [adjacent division] business?)*

**Technical evaluation** — are performance claims described accurately and with
checkable sources?

> 如何核实[组件类别]供应商宣称的[关键性能指标]？
> *(How do I verify a [component category] supplier's claimed [key performance metric]?)*

**Procurement scenario** — is the buying process described correctly?

> [城市]的[制造类别]企业与国际[组件]供应商合作时，需要确认哪些开发流程和交付条件？
> *(What development processes and delivery terms should a [city] [manufacturing category] company confirm when working with an international [component] supplier?)*

Have a native Chinese speaker review the filled prompts before the panel runs. A
prompt that reads as translated English changes what the assistant retrieves, and
that contaminates the whole panel.

## Run log — one row per run

Run ID · exact Chinese prompt · intent/persona group · brand included in prompt
(yes/no) · city · timestamp with timezone · consumer or API interface · visible
model/version · account status · device · network location · fresh-session
confirmed · search setting · actual search signal observed · full answer text ·
citation URLs · run status (completed / failed / pending / blocked).

Record settings that were not available rather than guessing them.

## What is measured

| Measure | Counting rule |
|---|---|
| Brand mention | Brand name appears in the generated answer — excluding the prompt, the sidebar history and reference-list titles |
| Relevant parent-brand recommendation | Parent brand offered as a supplier option, but the specific division not established |
| Division-qualified recommendation | The recommendation identifies the intended division and business model; note whether scope is explicit or implicit |
| Correct entity/scope | Distinguishes the audited division from adjacent divisions, retail and the wider group |
| Retrieved official source | An official URL appears in the retrieval reference list — it may never be cited in the answer |
| Inline official citation | A source link is visibly attached to answer text; support must still be assessed |
| Local vs international source | Count the `.cn` domain separately from the global domain, including the latter's Chinese-language pages |
| Claim support | Flag unsupported specifics, apparent mismatches, and claims needing approved evidence — do not label all unverified claims false |

## Metric definitions

| Metric | Numerator / denominator |
|---|---|
| Unprompted brand mention | Successful unbranded answers naming the correct entity / successful unbranded answers |
| Correct division | Branded answers correctly describing product scope and audience / successful branded answers |
| Owned-domain citation | Eligible successful answers explicitly citing the owned domain / eligible successful answers |
| Qualified recommendation | Successful unbranded answers recommending the correct entity for the stated need / successful unbranded answers |
| Citation support | Checked cited claims supported by the linked source / checked cited claims |
| Entity confusion | Successful answers confusing business divisions / scored successful answers |
| Competitor mention share | A competitor's mentions / all counted brand mentions — count each brand once per answer |
| Ordinal position | For answers that present brands in an explicit order (numbered, ranked, "first choice"): the brand's position and the number of brands listed. Report median position and share of first-position answers, over ordered answers only. Unordered lists have no position; do not infer one from reading order |

Before testing, **declare in writing**:

- The **eligibility definition** for citation prompts — in particular, whether
  answers where no search was invoked are excluded, or counted as zero citation.
  Without this, two investigators produce incomparable rates from identical logs.
  Report search invocation and coverage separately either way.
- The **counted competitor universe and alias rules**, reconciling parent/division
  duplicates once. Otherwise the same answer yields different shares depending on
  which brands were considered.

Preserve both definitions when repeating the panel.

## Reporting rules

- Report per-platform completed counts and conditions **before** comparing outcomes.
  Different guest/account settings and automatic retrieval modes limit direct
  comparison — say so.
- Report failures and denominators separately. Never merge branded and unbranded
  results without exposing the weights.
- Rank is meaningful only for genuinely ordered answers.
- Do not replace unmeasured results with zeros.
- Do not call a single run a market-wide rank.
- Repetition variance is a finding. One answer per prompt is a first pass, not a
  stability estimate.

## Bilingual presentation

Every Chinese query, term or excerpt in an English-facing deck, report or results
table carries an adjacent English translation. Submit only the exact Chinese prompt
to the assistant — the translation is reviewer context, never an additional
instruction. Raw Chinese response snapshots stay untouched, alongside full
responses, citations and run metadata, so a reviewer can go past the English
summary.

## Claims to reject without fresh proof

No reviewed primary documentation establishes any of these. Do not repeat them:

- All Chinese AIs read Baidu Baike first.
- Qwen favours a brand because it appears on 1688.
- Yuanbao only reads WeChat.
- Zhihu presence guarantees inclusion everywhere.
- A parent company's ecosystem is its model's exclusive retrieval list.
- Citations can be guaranteed within 30 days.
- A universal article length, keyword density, schema uplift or `llms.txt` support
  applies to Chinese engines.

Do not infer training data from a cited web result. Do not call correlation causal.
Reasoning text, model examples and moderation outcomes do not establish answer
accuracy — check each material claim against authoritative product evidence.

## Re-testing

Repeat the identical panel under the declared definitions. Interpret before/after
changes alongside model releases, campaigns, events and PR activity — an observed
lift alone does not prove attribution. Record every confounder you know about.

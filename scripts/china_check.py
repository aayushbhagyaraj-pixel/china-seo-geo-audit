#!/usr/bin/env python3
"""
china-check - China accessibility checker for websites.

Scans a URL and reports what would block or slow it down for a visitor in
mainland China, and what would stop Baidu reaching it. Runs from anywhere - it
inspects the page's CODE, so the result does not depend on which network you
happen to test from.

Usage:
    python3 china_check.py https://example.cn/
    python3 china_check.py https://example.cn/zh/ --json report.json

No installation, no dependencies beyond the Python standard library.

Limits, stated so the report does not overclaim:
  - Resources injected by JavaScript at runtime (a tag manager loading a
    captcha, a consent script loading a chat widget) are not visible in the
    HTML this tool reads. It scans same-origin JS bundles for hostnames as a
    partial remedy, but a mainland browser session with a network capture is
    the only complete check.
  - Timing figures are from wherever you ran it, never from China.
"""

import argparse
import gzip
import io
import json
import re
import ssl
import sys
import time
import urllib.error
import urllib.request
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/125.0 Safari/537.36")
BAIDU_UA = "Mozilla/5.0 (compatible; Baiduspider/2.0; +http://www.baidu.com/search/spider.html)"

# Hosts fully blocked by the Great Firewall.
BLOCKED = {
    "google.com": "Google", "www.google.com": "Google",
    "fonts.googleapis.com": "Google Fonts",
    "fonts.gstatic.com": "Google Fonts (files)",
    "ajax.googleapis.com": "Google hosted libraries",
    "www.googletagmanager.com": "Google Tag Manager",
    "googletagmanager.com": "Google Tag Manager",
    "www.google-analytics.com": "Google Analytics",
    "google-analytics.com": "Google Analytics",
    "recaptcha.net": "reCAPTCHA via Google's China workaround domain - reported blocked since 2022, intermittent at best",
    "www.recaptcha.net": "reCAPTCHA via Google's China workaround domain - reported blocked since 2022, intermittent at best",
    "gstatic.com": "Google static",
    "googleapis.com": "Google APIs",
    "doubleclick.net": "Google Ads",
    "googlesyndication.com": "Google Ads",
    "firebaseio.com": "Firebase (Google) - realtime/API calls fail",
    "firebaseapp.com": "Firebase hosting (Google)",
    "facebook.com": "Facebook", "www.facebook.com": "Facebook",
    "connect.facebook.net": "Facebook SDK",
    "twitter.com": "Twitter/X", "platform.twitter.com": "Twitter/X",
    "youtube.com": "YouTube", "www.youtube.com": "YouTube",
    "youtu.be": "YouTube", "s.ytimg.com": "YouTube",
    "instagram.com": "Instagram", "www.instagram.com": "Instagram",
    "linkedin.com": "LinkedIn", "www.linkedin.com": "LinkedIn",
    "platform.linkedin.com": "LinkedIn",
    "pinterest.com": "Pinterest", "it.pinterest.com": "Pinterest",
    "www.pinterest.com": "Pinterest",
    "vimeo.com": "Vimeo", "player.vimeo.com": "Vimeo",
    "dropbox.com": "Dropbox", "wordpress.org": "WordPress.org",
    "gravatar.com": "Gravatar", "secure.gravatar.com": "Gravatar",
    "whatsapp.com": "WhatsApp", "t.me": "Telegram",
    "googleusercontent.com": "Google user content",
    "withgoogle.com": "Google",
    "ytimg.com": "YouTube (images)",
    "fbcdn.net": "Facebook CDN",
    "cdninstagram.com": "Instagram CDN",
    "x.com": "Twitter/X", "twimg.com": "Twitter/X (assets)",
    "hcaptcha.com": "hCaptcha - gates form submit",
    "newassets.hcaptcha.com": "hCaptcha assets",
    "wikipedia.org": "Wikipedia", "wikimedia.org": "Wikimedia",
    "reddit.com": "Reddit", "redd.it": "Reddit",
    "medium.com": "Medium", "quora.com": "Quora",
    "blogspot.com": "Blogspot", "blogger.com": "Blogger",
    "slack.com": "Slack", "notion.so": "Notion",
    "figma.com": "Figma", "discord.com": "Discord",
    "twitch.tv": "Twitch", "soundcloud.com": "SoundCloud",
}

# Reachable but slow / unreliable - no China PoP, Cloudflare-fronted, or throttled.
SLOW = {
    "cdnjs.cloudflare.com": "cdnjs - throttled, no China PoP",
    "cdn.jsdelivr.net": "jsDelivr - no mainland PoP, verify current",
    "unpkg.com": "unpkg - no China PoP",
    "use.typekit.net": "Adobe Typekit - unreliable",
    "p.typekit.net": "Adobe Typekit (files) - unreliable",
    "use.fontawesome.com": "Font Awesome CDN - slow",
    "kit.fontawesome.com": "Font Awesome CDN - slow",
    "code.jquery.com": "jQuery CDN - slow",
    "stackpath.bootstrapcdn.com": "BootstrapCDN - slow",
    "cdn.bootcss.com": "BootCSS - verify current",
    "maxcdn.bootstrapcdn.com": "BootstrapCDN - slow",
    "s3.amazonaws.com": "AWS S3 US - high latency",
    "raw.githubusercontent.com": "GitHub raw - blocked intermittently",
    "github.com": "GitHub - throttled",
    "challenges.cloudflare.com": "Cloudflare Turnstile - can gate form submit",
    "cdn.cookielaw.org": "OneTrust consent - no China PoP",
    "onetrust.com": "OneTrust consent - no China PoP",
    "consent.cookiebot.com": "Cookiebot consent - no China PoP",
    "cdn.iubenda.com": "Iubenda consent - no China PoP",
    "widget.intercom.io": "Intercom chat - no China PoP",
    "js.intercomcdn.com": "Intercom assets - no China PoP",
    "static.zdassets.com": "Zendesk chat - no China PoP",
    "js.driftt.com": "Drift chat - no China PoP",
    "js.hs-scripts.com": "HubSpot - no China PoP",
    "js.hsforms.net": "HubSpot forms - no China PoP",
    "api.hsforms.com": "HubSpot forms API - form POST path, test from mainland",
    "embed.tawk.to": "Tawk.to chat - no China PoP",
    "cdn.segment.com": "Segment - no China PoP",
    "static.hotjar.com": "Hotjar - no China PoP",
    "edge.fullstory.com": "FullStory - no China PoP",
    "cdn.mxpnl.com": "Mixpanel - no China PoP",
    "cdn.amplitude.com": "Amplitude - no China PoP",
    "browser.sentry-cdn.com": "Sentry - no China PoP",
    "assets.calendly.com": "Calendly - no China PoP",
    "embed.typeform.com": "Typeform - no China PoP",
    "js.stripe.com": "Stripe - no China PoP, checkout may stall",
    "cdn.auth0.com": "Auth0 - no China PoP",
    # Backend / form endpoints: the POST path, not the page
    "supabase.co": "Supabase - Cloudflare-fronted API; form POST path, test from mainland",
    "formspree.io": "Formspree - form POST path, test from mainland",
    "hooks.zapier.com": "Zapier webhook - form POST path, test from mainland",
    "api.airtable.com": "Airtable API - form POST path, test from mainland",
    "workers.dev": "Cloudflare Workers - standard network, no mainland PoP",
    "pages.dev": "Cloudflare Pages - standard network, no mainland PoP",
    "netlify.app": "Netlify - no mainland PoP",
    "herokuapp.com": "Heroku - no mainland PoP",
    "onrender.com": "Render - no mainland PoP",
    "fly.dev": "Fly.io - no mainland PoP",
    # Generic edge platforms without mainland nodes
    "cloudfront.net": "AWS CloudFront - no mainland PoP by default",
    "akamaihd.net": "Akamai - mainland presence reported ended 2026-06-30, verify",
    "akamaized.net": "Akamai - mainland presence reported ended 2026-06-30, verify",
    "vercel.app": "Vercel - no mainland PoP",
}

CN_SOCIAL = ("weibo.com", "weixin.qq.com", "xiaohongshu.com", "douyin.com",
             "bilibili.com", "zhihu.com", "qq.com")
CN_ANALYTICS = ("hm.baidu.com", "tongji.baidu.com", "zz.bdstatic.com/linksubmit",
                "cnzz.com", "umeng.com", "growingio.com", "sensorsdata")
CN_FONT_RE = re.compile(
    r"PingFang|Microsoft\s*YaHei|Hiragino\s+Sans\s+GB|SimSun|SimHei|Noto\s+Sans\s+(SC|CJK)|"
    r"Source\s+Han\s+Sans|微软雅黑|苹方|思源黑体", re.I)
CHALLENGE_RE = re.compile(
    r"security checkpoint|challenge-platform|cf-chl|just a moment|verify you are human|"
    r"captcha|x-vercel-mitigated|请完成安全验证|人机验证", re.I)
HOST_RE = re.compile(r"https?://([a-z0-9][a-z0-9.-]{2,}\.[a-z]{2,})", re.I)


def classify(host):
    """Return (verdict, note) for a hostname."""
    h = host.lower()
    if h in BLOCKED:
        return "BLOCKED", BLOCKED[h]
    if h in SLOW:
        return "SLOW", SLOW[h]
    for bad, label in BLOCKED.items():
        if h.endswith("." + bad):
            return "BLOCKED", label
    for slow, label in SLOW.items():
        if h.endswith("." + slow):
            return "SLOW", label
    return "OK", ""


class PageParser(HTMLParser):
    """Collect external resources, meta signals and inline CSS."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.in_head = True
        self.in_style = False
        self.res = []
        self.meta = {}
        self.html_lang = None
        self.canonical = None
        self.inline_css = []
        self.forms = []
        self.stylesheets = []
        self.scripts = []

    def handle_endtag(self, tag):
        t = tag.lower()
        if t == "head":
            self.in_head = False
        if t == "style":
            self.in_style = False

    def handle_data(self, data):
        if self.in_style:
            self.inline_css.append(data)

    def _add(self, url, kind, blocking=False):
        self.res.append({"url": url, "kind": kind,
                         "blocking": blocking and self.in_head, "in_head": self.in_head})

    def handle_starttag(self, tag, attrs):
        t = tag.lower()
        a = {k.lower(): (v or "") for k, v in attrs}
        if t == "html":
            self.html_lang = a.get("lang")
        elif t == "style":
            self.in_style = True
        elif t == "meta":
            key = (a.get("name") or a.get("http-equiv") or a.get("property") or "").lower()
            if key:
                self.meta[key] = a.get("content", "")
        elif t == "script" and a.get("src"):
            self.scripts.append(a["src"])
            self._add(a["src"], "script", "async" not in a and "defer" not in a)
        elif t == "link" and a.get("href"):
            rel = a.get("rel", "").lower()
            if "canonical" in rel:
                self.canonical = a["href"]
            if "stylesheet" in rel:
                self.stylesheets.append(a["href"])
            self._add(a["href"], f"link[{rel or '-'}]", "stylesheet" in rel and "preload" not in rel)
        elif t == "iframe" and a.get("src"):
            self._add(a["src"], "iframe")
        elif t in ("img", "source", "video", "audio"):
            for attr in ("src", "data-src", "poster"):
                if a.get(attr):
                    self._add(a[attr], t)
            for attr in ("srcset", "data-srcset"):
                if a.get(attr):
                    for cand in a[attr].split(","):
                        u = cand.strip().split(" ")[0]
                        if u:
                            self._add(u, f"{t}[srcset]")
        elif t == "form":
            self.forms.append(a.get("action", ""))


def _opener():
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, *a, **k):
            return None

    return urllib.request.build_opener(NoRedirect, urllib.request.HTTPSHandler(context=ctx))


def _decode(hdrs, body):
    if hdrs.get("Content-Encoding", "").lower() == "gzip":
        try:
            body = gzip.GzipFile(fileobj=io.BytesIO(body)).read()
        except OSError:
            pass
    return body.decode("utf-8", errors="replace")


def fetch(url, timeout=30, ua=UA, follow=True, max_bytes=None):
    """Fetch a URL, following redirects manually so we can record the chain."""
    chain, current, html, headers = [], url, "", {}
    op = _opener()
    for _ in range(10):
        req = urllib.request.Request(
            current, headers={"User-Agent": ua, "Accept-Encoding": "gzip",
                              "Accept-Language": "zh-CN,zh;q=0.9"})
        t0 = time.time()
        try:
            r = op.open(req, timeout=timeout)
            code, hdrs = r.getcode(), dict(r.headers)
            body = r.read(max_bytes) if max_bytes else r.read()
        except urllib.error.HTTPError as e:
            code, hdrs, body = e.code, dict(e.headers), e.read()
        except Exception as e:
            chain.append({"url": current, "status": "ERROR", "error": str(e),
                          "ms": int((time.time() - t0) * 1000)})
            return chain, "", {}
        ms = int((time.time() - t0) * 1000)
        chain.append({"url": current, "status": code, "ms": ms})
        loc = hdrs.get("Location") or hdrs.get("location")
        if follow and code in (301, 302, 303, 307, 308) and loc:
            current = urljoin(current, loc)
            continue
        html = _decode(hdrs, body)
        headers = hdrs
        break
    return chain, html, headers


def hdr(headers, name):
    for k, v in headers.items():
        if k.lower() == name.lower():
            return v
    return ""


def hosts_in_text(text):
    return {m.group(1).lower() for m in HOST_RE.finditer(text)}


def css_urls(text):
    out = set()
    for m in re.finditer(r"url\(\s*['\"]?([^'\")\s]+)", text, re.I):
        out.add(m.group(1))
    for m in re.finditer(r"@import\s+(?:url\()?['\"]?([^'\")\s;]+)", text, re.I):
        out.add(m.group(1))
    return out


def parse_robots(text):
    """Return {agent: [disallow paths]} and sitemap list."""
    groups, sitemaps, current = {}, [], []
    for raw in text.splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line or ":" not in line:
            continue
        k, v = line.split(":", 1)
        k, v = k.strip().lower(), v.strip()
        if k == "user-agent":
            current = [v.lower()]
            groups.setdefault(v.lower(), [])
        elif k == "disallow" and current:
            for ag in current:
                groups[ag].append(v)
        elif k == "sitemap":
            sitemaps.append(v)
    return groups, sitemaps


def robots_verdict(groups, agent):
    """Is this crawler blocked from '/'? Returns (matched_group, blocked_root)."""
    for name in groups:
        if name != "*" and name in agent.lower():
            return name, "/" in groups[name]
    if "*" in groups:
        return "*", "/" in groups["*"]
    return None, False


def check_crawler_access(final, timeout):
    """robots.txt, sitemap(s), and a Baiduspider probe of sitemap URLs."""
    p = urlparse(final)
    base = f"{p.scheme}://{p.netloc}"
    out = {"robots_url": base + "/robots.txt"}
    chain, txt, _ = fetch(base + "/robots.txt", timeout, ua=BAIDU_UA)
    out["robots_status"] = chain[-1]["status"] if chain else "ERROR"
    groups, sitemaps = parse_robots(txt if out["robots_status"] == 200 else "")
    out["crawlers"] = {}
    for agent in ("Baiduspider", "Baiduspider-render", "Bytespider", "Sogou web spider",
                  "360Spider", "YisouSpider", "PetalBot"):
        g, blocked = robots_verdict(groups, agent)
        out["crawlers"][agent] = {"group": g, "blocked_root": blocked}
    out["sitemaps_declared"] = sitemaps
    targets = sitemaps or [base + "/sitemap.xml"]
    out["sitemaps"] = []
    final_host = p.netloc.lower()
    for sm in targets[:3]:
        ch, body, _ = fetch(sm, timeout, ua=BAIDU_UA, max_bytes=2_000_000)
        st = ch[-1]["status"] if ch else "ERROR"
        info = {"url": sm, "status": st, "chain": ch, "declared": bool(sitemaps)}
        if st == 200 and "<sitemapindex" in body:
            children = re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", body)
            info["index_children"] = len(children)
            if children:
                ch2, body, _ = fetch(children[0], timeout, ua=BAIDU_UA, max_bytes=2_000_000)
                info["first_child"] = {"url": children[0], "status": ch2[-1]["status"] if ch2 else "ERROR"}
        locs = re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", body) if st == 200 else []
        info["url_count"] = len(locs)
        hosts = {}
        for u in locs:
            h = urlparse(u).netloc.lower()
            hosts[h] = hosts.get(h, 0) + 1
        info["hosts"] = hosts
        info["other_host_urls"] = sum(n for h, n in hosts.items() if h != final_host)
        probes = []
        for u in locs[:3]:
            pc, pb, ph = fetch(u, timeout, ua=BAIDU_UA, follow=False, max_bytes=200_000)
            probes.append({"url": u, "status": pc[-1]["status"] if pc else "ERROR",
                           "location": hdr(ph, "Location"),
                           "challenge": bool(CHALLENGE_RE.search(pb or "")) or bool(hdr(ph, "x-vercel-mitigated"))})
        info["baiduspider_probe"] = probes
        out["sitemaps"].append(info)
    return out


def analyse(url, timeout=30):
    chain, html, headers = fetch(url, timeout)
    if not html:
        return {"url": url, "chain": chain, "error": "could not fetch page"}

    final = chain[-1]["url"]
    start_host = urlparse(url).netloc.lower().replace("www.", "")
    final_host_full = urlparse(final).netloc.lower()
    final_host = final_host_full.replace("www.", "")

    p = PageParser()
    try:
        p.feed(html)
    except Exception:
        pass

    findings, hosts = [], {}

    def note_host(u, kind, blocking, source):
        if u.startswith("//"):
            u = "https:" + u
        if not u.startswith("http"):
            u = urljoin(final, u)
        host = urlparse(u).netloc.lower()
        if not host or host == final_host_full:
            return
        verdict, note = classify(host)
        if verdict == "OK":
            return
        hosts.setdefault(host, {"verdict": verdict, "note": note, "count": 0,
                                "blocking": False, "sources": set()})
        hosts[host]["count"] += 1
        hosts[host]["sources"].add(source)
        if blocking:
            hosts[host]["blocking"] = True
            findings.append({"host": host, "verdict": verdict, "note": note,
                             "url": u, "kind": kind, "blocking": True})

    for r in p.res:
        note_host(r["url"], r["kind"], r["blocking"], "html")

    # CSS: inline blocks plus fetched stylesheets (same-origin and external, up to 8)
    css_text = "\n".join(p.inline_css)
    css_fetched = []
    for href in p.stylesheets[:8]:
        u = urljoin(final, href)
        ch, body, _ = fetch(u, timeout, max_bytes=1_500_000)
        if ch and ch[-1]["status"] == 200:
            css_text += "\n" + body
            css_fetched.append(u)
    for u in css_urls(css_text):
        if u.startswith("data:"):
            continue
        note_host(u, "css", False, "css")

    # Same-origin JS bundles: scan for hostnames (partial remedy for JS-injected resources)
    js_hosts, js_scanned = {}, []
    for src in p.scripts:
        u = urljoin(final, src)
        if urlparse(u).netloc.lower() != final_host_full:
            continue
        if len(js_scanned) >= 4:
            break
        ch, body, _ = fetch(u, timeout, max_bytes=3_000_000)
        if ch and ch[-1]["status"] == 200:
            js_scanned.append(u)
            for h in hosts_in_text(body):
                if h == final_host_full:
                    continue
                v, n = classify(h)
                if v != "OK":
                    js_hosts[h] = {"verdict": v, "note": n}

    for h in hosts.values():
        h["sources"] = sorted(h["sources"])

    low = html.lower()
    crawl = check_crawler_access(final, timeout)
    canonical_host = urlparse(urljoin(final, p.canonical)).netloc.lower() if p.canonical else None
    meta_robots = (p.meta.get("robots") or "") + " " + (p.meta.get("baiduspider") or "")
    x_robots = hdr(headers, "X-Robots-Tag")

    return {
        "url": url,
        "final_url": final,
        "chain": chain,
        "leaves_domain": start_host != final_host,
        "hosts": hosts,
        "blocking_findings": findings,
        "css_fetched": css_fetched,
        "js_scanned": js_scanned,
        "js_hosts": js_hosts,
        "form_actions": [a for a in p.forms if a],
        "captchas": sorted({label for sig, label in (
            ("grecaptcha", "Google reCAPTCHA"),
            ("recaptcha", "Google reCAPTCHA"),
            ("hcaptcha", "hCaptcha"),
            ("cf-turnstile", "Cloudflare Turnstile"),
            ("challenges.cloudflare.com", "Cloudflare Turnstile"),
        ) if sig in low}),
        "widgets": sorted({label for sig, label in (
            ("onetrust", "OneTrust consent banner"),
            ("cookielaw.org", "OneTrust consent banner"),
            ("cookiebot", "Cookiebot consent banner"),
            ("iubenda", "Iubenda consent banner"),
            ("intercom", "Intercom chat"),
            ("zdassets", "Zendesk chat"),
            ("driftt", "Drift chat"),
            ("hs-scripts", "HubSpot"),
            ("tawk.to", "Tawk.to chat"),
        ) if sig in low}),
        "has_cn_analytics": any(a in low for a in CN_ANALYTICS),
        "has_ga": "googletagmanager" in low or "google-analytics" in low,
        "cn_social": sorted({s for s in CN_SOCIAL if s in low}),
        "has_icp": bool(re.search(r"备案|ICP\s*备", html)),
        "cn_fonts_html": bool(CN_FONT_RE.search(html)),
        "cn_fonts_css": bool(CN_FONT_RE.search(css_text)),
        "signals": {
            "html_lang": p.html_lang,
            "content_language_header": hdr(headers, "Content-Language"),
            "content_language_meta": p.meta.get("content-language", ""),
            "meta_robots": meta_robots.strip(),
            "x_robots_tag": x_robots,
            "noindex": "noindex" in (meta_robots + " " + x_robots).lower(),
            "viewport": p.meta.get("viewport", ""),
            "applicable_device": p.meta.get("applicable-device", ""),
            "mobile_agent": p.meta.get("mobile-agent", ""),
            "baidu_site_verification": p.meta.get("baidu-site-verification", ""),
            "baidu_push_script": "linksubmit/push.js" in low,
            "canonical": p.canonical,
            "canonical_host": canonical_host,
            "canonical_other_host": bool(canonical_host and canonical_host != final_host_full),
            "title": (re.search(r"<title[^>]*>(.*?)</title>", html, re.I | re.S) or [None, ""])[1].strip()[:120] if re.search(r"<title", html, re.I) else "",
        },
        "crawl": crawl,
        "cache_control": hdr(headers, "Cache-Control"),
        "cf_cache": hdr(headers, "Cf-Cache-Status"),
        "ttfb_ms": chain[-1].get("ms", 0),
        "size_kb": round(len(html) / 1024, 1),
    }


C = {"red": "\033[91m", "yel": "\033[93m", "grn": "\033[92m",
     "bold": "\033[1m", "dim": "\033[2m", "off": "\033[0m"}


def report(r, color=True):
    c = C if color else {k: "" for k in C}
    out, fails, warns = [], [], []
    A = out.append

    def FAIL(msg):
        fails.append(msg)
        A(f"  {c['red']}FAIL  {msg}{c['off']}")

    def WARN(msg):
        warns.append(msg)
        A(f"  {c['yel']}WARN  {msg}{c['off']}")

    def PASS(msg):
        A(f"  {c['grn']}PASS  {msg}{c['off']}")

    A(f"\n{c['bold']}{'=' * 68}{c['off']}")
    A(f"{c['bold']}  CHINA ACCESSIBILITY CHECK{c['off']}")
    A(f"  {r['url']}")
    A(f"{c['bold']}{'=' * 68}{c['off']}")

    if r.get("error"):
        A(f"\n  {c['red']}ERROR: {r['error']}{c['off']}")
        for h in r["chain"]:
            A(f"    {h['url']} -> {h['status']}")
        return "\n".join(out), 1

    # 1. Redirects
    A(f"\n{c['bold']}1. REDIRECT CHAIN{c['off']}")
    for i, h in enumerate(r["chain"]):
        arrow = "   " if i == 0 else " ->"
        A(f"  {arrow} [{h['status']}] {h['url']}  {c['dim']}({h['ms']}ms){c['off']}")
    if r["leaves_domain"]:
        FAIL("The page leaves the domain it started on. Visitors typing the original address never see this site.")
    elif len(r["chain"]) > 2:
        WARN(f"{len(r['chain']) - 1} redirects before content.")
    else:
        PASS("Stays on the same domain.")

    # 2. Blocking resources
    A(f"\n{c['bold']}2. RENDER-BLOCKING RESOURCES FROM BLOCKED HOSTS{c['off']}")
    blocked_blocking = [f for f in r["blocking_findings"] if f["verdict"] == "BLOCKED"]
    slow_blocking = [f for f in r["blocking_findings"] if f["verdict"] == "SLOW"]
    if blocked_blocking:
        FAIL(f"{len(blocked_blocking)} render-blocking resource(s) from hosts China blocks. Each can hang the page 30-60 s where packets are dropped silently.")
        for f in blocked_blocking:
            A(f"    {c['red']}x{c['off']} {f['host']}  {c['dim']}({f['note']}) {f['url'][:70]}{c['off']}")
    else:
        PASS("No render-blocking resources from blocked hosts.")
    for f in slow_blocking:
        WARN(f"render-blocking from slow host {f['host']} ({f['note']})")

    # 3. All external hosts
    A(f"\n{c['bold']}3. EXTERNAL HOSTS (HTML + CSS){c['off']}")
    bl = {h: v for h, v in r["hosts"].items() if v["verdict"] == "BLOCKED"}
    sl = {h: v for h, v in r["hosts"].items() if v["verdict"] == "SLOW"}
    for label, group, col in (("Blocked in China", bl, "red"), ("Slow / unreliable", sl, "yel")):
        if group:
            A(f"\n  {c[col]}{label} ({len(group)}):{c['off']}")
            for h, v in sorted(group.items()):
                tag = f" {c[col]}[RENDER-BLOCKING]{c['off']}" if v["blocking"] else ""
                A(f"    {h:38s} x{v['count']} via {','.join(v['sources'])}  {c['dim']}{v['note']}{c['off']}{tag}")
    if not bl and not sl:
        PASS("No problem hosts in HTML or CSS.")
    if bl and not blocked_blocking:
        WARN(f"{len(bl)} blocked host(s) referenced (not render-blocking): the feature silently fails.")
    A(f"  {c['dim']}CSS files scanned: {len(r['css_fetched'])}{c['off']}")

    # 3b. JS bundles
    A(f"\n{c['bold']}3b. HOSTS REFERENCED IN SAME-ORIGIN JS BUNDLES{c['off']}")
    if r["js_hosts"]:
        WARN(f"{len(r['js_hosts'])} problem host(s) named in JavaScript. Whether they are on the form or render path needs a network capture.")
        for h, v in sorted(r["js_hosts"].items()):
            A(f"    {h:38s} {v['verdict']:8s} {c['dim']}{v['note']}{c['off']}")
    elif r["js_scanned"]:
        PASS(f"No problem hosts named in {len(r['js_scanned'])} bundle(s) scanned.")
    else:
        A(f"  {c['dim']}INFO  No same-origin bundles found to scan.{c['off']}")
    A(f"  {c['dim']}Resources injected at runtime by a tag manager or consent script are not visible here.{c['off']}")

    # 4. Forms
    A(f"\n{c['bold']}4. FORM SUBMISSION{c['off']}")
    if r.get("captchas"):
        for cap in r["captchas"]:
            FAIL(f"{cap} detected. A captcha needs a token from its own host before the form sends; from China that fails, so enquiries cannot be sent even after the page loads.")
        A(f"        {c['dim']}Fix: Geetest, Tencent Captcha, or a honeypot field.{c['off']}")
    else:
        PASS("No blocking captcha detected in HTML.")
    for act in r["form_actions"]:
        h = urlparse(urljoin(r["final_url"], act)).netloc.lower()
        v, n = classify(h) if h else ("OK", "")
        if v != "OK":
            FAIL(f"form posts to {h} ({n})")
        elif h and h != urlparse(r["final_url"]).netloc.lower():
            WARN(f"form posts to external host {h}; test the POST from a mainland network")
    if r.get("widgets"):
        A(f"\n{c['bold']}4b. CONSENT / CHAT WIDGETS{c['off']}")
        for w in r["widgets"]:
            WARN(f"{w}: loads from a host with no mainland PoP and occupies first-screen area (Baidu asks for 50%+ main content on mobile).")

    # 5. Analytics
    A(f"\n{c['bold']}5. ANALYTICS COVERAGE{c['off']}")
    if r["has_ga"] and not r["has_cn_analytics"]:
        FAIL("Google Analytics / Tag Manager only. Blocked in China, so mainland visitors are invisible; neither the problem nor the fix is measurable. Add Baidu Tongji.")
    elif r["has_cn_analytics"]:
        PASS("Chinese analytics present.")
    else:
        WARN("No analytics detected at all. Nothing about mainland traffic or form completion is measurable.")

    # 6. Crawler access
    A(f"\n{c['bold']}6. CRAWLER ACCESS (robots.txt, sitemap, Baiduspider probe){c['off']}")
    cr = r["crawl"]
    A(f"  robots.txt: {cr['robots_status']}")
    if cr["robots_status"] != 200:
        WARN(f"robots.txt returned {cr['robots_status']} to a Baiduspider UA; crawler permissions could not be read.")
    for agent, v in cr["crawlers"].items():
        if v["blocked_root"]:
            FAIL(f"robots.txt disallows / for {agent} (group '{v['group']}')")
    if cr["robots_status"] == 200 and not any(v["blocked_root"] for v in cr["crawlers"].values()):
        PASS("No Chinese crawler is disallowed from / in robots.txt (CDN bot rules not checked).")
    if not cr["sitemaps_declared"]:
        WARN("No Sitemap: line in robots.txt; tried /sitemap.xml")
    for sm in cr["sitemaps"]:
        A(f"  sitemap {sm['url']} -> {sm['status']}, {sm['url_count']} URLs, hosts {sm['hosts'] or '-'}")
        if sm["status"] != 200:
            FAIL(f"sitemap returns {sm['status']} to Baiduspider")
        if sm["other_host_urls"]:
            FAIL(f"{sm['other_host_urls']} sitemap URL(s) are on a different host from the page served. Baidu is being sent elsewhere.")
        bad = [pr for pr in sm["baiduspider_probe"] if pr["status"] != 200 or pr["challenge"]]
        for pr in sm["baiduspider_probe"]:
            flag = "CHALLENGE" if pr["challenge"] else ""
            A(f"    probe {pr['url'][:60]:60s} -> {pr['status']} {('-> ' + pr['location'][:40]) if pr['location'] else ''} {c['red'] + flag + c['off'] if flag else ''}")
        if bad:
            FAIL(f"{len(bad)} of {len(sm['baiduspider_probe'])} sitemap URLs probed with a Baiduspider UA did not return 200 clean. Nothing listed there is reachable to the crawler.")
        elif sm["baiduspider_probe"]:
            PASS("Probed sitemap URLs return 200 to a Baiduspider UA (from this location).")

    # 7. Page signals
    A(f"\n{c['bold']}7. PAGE SIGNALS{c['off']}")
    s = r["signals"]
    A(f"  <html lang>: {s['html_lang'] or '(none)'} | Content-Language header: {s['content_language_header'] or '(none)'} | meta: {s['content_language_meta'] or '(none)'}")
    if not (s["html_lang"] or "").lower().startswith("zh"):
        WARN("<html lang> is not zh-*. Baidu reads language from content-language and the domain, but declare it anyway.")
    if not s["content_language_header"] and not s["content_language_meta"]:
        WARN("No content-language header or meta. This is the language signal Baidu reads (it ignores hreflang).")
    if s["noindex"]:
        FAIL(f"noindex present (meta '{s['meta_robots']}' / header '{s['x_robots_tag']}')")
    A(f"  viewport: {s['viewport'] or '(none)'} | applicable-device: {s['applicable_device'] or '(none)'} | mobile-agent: {s['mobile_agent'] or '(none)'}")
    if not s["viewport"]:
        WARN("No viewport meta; Baidu's mobile landing rules cannot be met without it.")
    if not s["applicable_device"] and not s["mobile_agent"]:
        WARN("No 移动适配 declaration (applicable-device / mobile-agent). Baidu is not told how PC and mobile relate.")
    A(f"  canonical: {s['canonical'] or '(none)'}")
    if s["canonical_other_host"]:
        FAIL(f"canonical points at another host ({s['canonical_host']}). Whatever that host serves the crawler is what counts.")
    A(f"  baidu-site-verification meta: {'yes' if s['baidu_site_verification'] else 'no'} | push script: {'yes' if s['baidu_push_script'] else 'no'}")
    if not s["baidu_site_verification"] and not s["baidu_push_script"]:
        A(f"  {c['dim']}INFO  No sign the site was registered with Baidu Search Resource Platform. Confirm with the owner.{c['off']}")
    A(f"  title: {s['title'] or '(none)'}")

    # 8. Secondary
    A(f"\n{c['bold']}8. SECONDARY{c['off']}")
    cc = (r["cache_control"] or "").lower()
    if "no-store" in cc or "no-cache" in cc:
        WARN(f"Page sent with '{r['cache_control']}': the CDN caches nothing; every visit crosses to origin.")
    else:
        A(f"  OK    Cache-Control: {r['cache_control'] or '(none)'}")
    if r["cf_cache"]:
        A(f"  {c['dim']}      CDN cache status: {r['cf_cache']}{c['off']}")
    fonts = r["cn_fonts_html"] or r["cn_fonts_css"]
    A(f"  {'OK   ' if fonts else 'WARN '} Chinese font stack: {'present (' + ('css' if r['cn_fonts_css'] else 'html') + ')' if fonts else 'absent in HTML and scanned CSS'}")
    if not fonts:
        warns.append("no Chinese font stack")
    A(f"  {'OK   ' if r['has_icp'] else 'INFO '} ICP filing on page: {'yes' if r['has_icp'] else 'not shown (only required for mainland hosting)'}")
    if r["cn_social"]:
        A(f"  OK    Chinese social present: {', '.join(r['cn_social'])}")
    A(f"  {c['dim']}      TTFB {r['ttfb_ms']}ms | HTML {r['size_kb']}KB (measured from where you ran this, not from China){c['off']}")

    # Verdict
    A(f"\n{c['bold']}{'=' * 68}{c['off']}")
    col = c["red"] if fails else (c["yel"] if warns else c["grn"])
    A(f"{c['bold']}  {col}{len(fails)} FAIL, {len(warns)} WARN{c['off']}")
    for f in fails:
        A(f"  {c['red']}- {f[:110]}{c['off']}")
    A(f"  {c['dim']}Severity is in the list above, not in a count. One failing sitemap probe or one captcha{c['off']}")
    A(f"  {c['dim']}outranks any number of warnings. Confirm from a mainland browser session before reporting.{c['off']}")
    A(f"{c['bold']}{'=' * 68}{c['off']}\n")
    return "\n".join(out), (1 if fails else 0)


def main():
    ap = argparse.ArgumentParser(
        description="Check whether a website is accessible from mainland China and reachable by Baidu.")
    ap.add_argument("url", nargs="+", help="URL(s) to check")
    ap.add_argument("--json", metavar="FILE", help="also write JSON results")
    ap.add_argument("--no-color", action="store_true")
    ap.add_argument("--timeout", type=int, default=30)
    a = ap.parse_args()

    results, failed = [], False
    for u in a.url:
        if not u.startswith("http"):
            u = "https://" + u
        r = analyse(u, a.timeout)
        results.append(r)
        text, code = report(r, color=not a.no_color)
        print(text)
        failed = failed or code == 1

    if a.json:
        with open(a.json, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False, default=list)
        print(f"JSON written to {a.json}")

    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()

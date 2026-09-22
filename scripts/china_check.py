#!/usr/bin/env python3
"""
china-check - China accessibility checker for websites.

Scans a URL and reports what would block or slow it down for a visitor in
mainland China. Runs from anywhere - it inspects the page's CODE, so the
result does not depend on which network you happen to test from.

Usage:
    python3 china_check.py https://example.cn/
    python3 china_check.py https://example.cn/zh/ --json report.json

No installation, no dependencies beyond the Python standard library.
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
    "recaptcha.net": "reCAPTCHA",
    "www.recaptcha.net": "reCAPTCHA",
    "gstatic.com": "Google static",
    "googleapis.com": "Google APIs",
    "doubleclick.net": "Google Ads",
    "googlesyndication.com": "Google Ads",
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
    # Further Google / Meta / X properties
    "googleusercontent.com": "Google user content",
    "withgoogle.com": "Google",
    "ytimg.com": "YouTube (images)",
    "fbcdn.net": "Facebook CDN",
    "cdninstagram.com": "Instagram CDN",
    "x.com": "Twitter/X", "twimg.com": "Twitter/X (assets)",
    # Captcha services that gate form submission
    "hcaptcha.com": "hCaptcha - gates form submit",
    "newassets.hcaptcha.com": "hCaptcha assets",
    # Reference and community sources
    "wikipedia.org": "Wikipedia", "wikimedia.org": "Wikimedia",
    "reddit.com": "Reddit", "redd.it": "Reddit",
    "medium.com": "Medium", "quora.com": "Quora",
    "blogspot.com": "Blogspot", "blogger.com": "Blogger",
    # Workplace / SaaS surfaces
    "slack.com": "Slack", "notion.so": "Notion",
    "figma.com": "Figma", "discord.com": "Discord",
    "twitch.tv": "Twitch", "soundcloud.com": "SoundCloud",
}

# Reachable but slow / unreliable - no China PoP, or heavily throttled.
SLOW = {
    "cdnjs.cloudflare.com": "cdnjs - throttled, no China PoP",
    "cdn.jsdelivr.net": "jsDelivr - unreliable since 2021",
    "unpkg.com": "unpkg - no China PoP",
    "use.typekit.net": "Adobe Typekit - unreliable",
    "p.typekit.net": "Adobe Typekit (files) - unreliable",
    "use.fontawesome.com": "Font Awesome CDN - slow",
    "kit.fontawesome.com": "Font Awesome CDN - slow",
    "code.jquery.com": "jQuery CDN - slow",
    "stackpath.bootstrapcdn.com": "BootstrapCDN - slow",
    "cdn.bootcss.com": "BootCSS - deprecated",
    "maxcdn.bootstrapcdn.com": "BootstrapCDN - slow",
    "s3.amazonaws.com": "AWS S3 US - high latency",
    "raw.githubusercontent.com": "GitHub raw - blocked intermittently",
    "github.com": "GitHub - throttled",
    # Bot challenge - can gate form submit
    "challenges.cloudflare.com": "Cloudflare Turnstile - can gate form submit",
    # Consent banners: render-blocking AND eat first-screen area
    "cdn.cookielaw.org": "OneTrust consent - no China PoP",
    "onetrust.com": "OneTrust consent - no China PoP",
    "consent.cookiebot.com": "Cookiebot consent - no China PoP",
    "cdn.iubenda.com": "Iubenda consent - no China PoP",
    # Chat / support widgets
    "widget.intercom.io": "Intercom chat - no China PoP",
    "js.intercomcdn.com": "Intercom assets - no China PoP",
    "static.zdassets.com": "Zendesk chat - no China PoP",
    "js.driftt.com": "Drift chat - no China PoP",
    "js.hs-scripts.com": "HubSpot - no China PoP",
    "js.hsforms.net": "HubSpot forms - no China PoP",
    "embed.tawk.to": "Tawk.to chat - no China PoP",
    # Product analytics / session replay
    "cdn.segment.com": "Segment - no China PoP",
    "static.hotjar.com": "Hotjar - no China PoP",
    "edge.fullstory.com": "FullStory - no China PoP",
    "cdn.mxpnl.com": "Mixpanel - no China PoP",
    "cdn.amplitude.com": "Amplitude - no China PoP",
    "browser.sentry-cdn.com": "Sentry - no China PoP",
    # Scheduling / forms / payments / auth
    "assets.calendly.com": "Calendly - no China PoP",
    "embed.typeform.com": "Typeform - no China PoP",
    "js.stripe.com": "Stripe - no China PoP, checkout may stall",
    "cdn.auth0.com": "Auth0 - no China PoP",
    # Generic edge platforms without mainland nodes
    "cloudfront.net": "AWS CloudFront - no mainland PoP by default",
    "akamaihd.net": "Akamai - mainland presence ended 2026-06-30",
    "akamaized.net": "Akamai - mainland presence ended 2026-06-30",
    "vercel.app": "Vercel - no mainland PoP",
}

CN_SOCIAL = ("weibo.com", "weixin.qq.com", "xiaohongshu.com", "douyin.com",
             "bilibili.com", "zhihu.com", "qq.com")

CN_ANALYTICS = ("hm.baidu.com", "tongji.baidu.com", "zz.bdstatic.com",
                "cnzz.com", "umeng.com", "growingio.com", "sensorsdata")


def classify(host):
    """Return (verdict, note) for a hostname."""
    h = host.lower()
    if h in BLOCKED:
        return "BLOCKED", BLOCKED[h]
    if h in SLOW:
        return "SLOW", SLOW[h]
    # suffix match for subdomains
    for bad, label in BLOCKED.items():
        if h.endswith("." + bad):
            return "BLOCKED", label
    for slow, label in SLOW.items():
        if h.endswith("." + slow):
            return "SLOW", label
    return "OK", ""


class HeadParser(HTMLParser):
    """Collect external resources, noting which are render-blocking."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.in_head = True
        self.res = []

    def handle_endtag(self, tag):
        if tag.lower() == "head":
            self.in_head = False

    def handle_starttag(self, tag, attrs):
        t = tag.lower()
        a = {k.lower(): (v or "") for k, v in attrs}
        url = kind = None
        blocking = False

        if t == "script" and a.get("src"):
            url, kind = a["src"], "script"
            # A script with no async/defer halts the HTML parser.
            blocking = "async" not in a and "defer" not in a
        elif t == "link" and a.get("href"):
            rel = a.get("rel", "").lower()
            url, kind = a["href"], f"link[{rel or '-'}]"
            blocking = "stylesheet" in rel and "preload" not in rel
        elif t == "iframe" and a.get("src"):
            url, kind = a["src"], "iframe"
        elif t == "img" and a.get("src"):
            url, kind = a["src"], "img"

        if url:
            self.res.append({
                "url": url, "kind": kind,
                "blocking": blocking and self.in_head,
                "in_head": self.in_head,
            })


def fetch(url, timeout=30):
    """Fetch a URL, following redirects manually so we can record the chain."""
    chain, current, html, headers = [], url, "", {}
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, *a, **k):
            return None

    op = urllib.request.build_opener(NoRedirect,
                                     urllib.request.HTTPSHandler(context=ctx))

    for _ in range(10):
        req = urllib.request.Request(
            current, headers={"User-Agent": UA, "Accept-Encoding": "gzip",
                              "Accept-Language": "zh-CN,zh;q=0.9"})
        t0 = time.time()
        try:
            r = op.open(req, timeout=timeout)
            code, hdrs, body = r.getcode(), dict(r.headers), r.read()
        except urllib.error.HTTPError as e:
            code, hdrs, body = e.code, dict(e.headers), e.read()
        except Exception as e:
            chain.append({"url": current, "status": "ERROR", "error": str(e),
                          "ms": int((time.time() - t0) * 1000)})
            return chain, "", {}

        ms = int((time.time() - t0) * 1000)
        chain.append({"url": current, "status": code, "ms": ms})
        loc = hdrs.get("Location") or hdrs.get("location")
        if code in (301, 302, 303, 307, 308) and loc:
            current = urljoin(current, loc)
            continue

        if hdrs.get("Content-Encoding", "").lower() == "gzip":
            try:
                body = gzip.GzipFile(fileobj=io.BytesIO(body)).read()
            except OSError:
                pass
        html = body.decode("utf-8", errors="replace")
        headers = hdrs
        break

    return chain, html, headers


def analyse(url, timeout=30):
    chain, html, headers = fetch(url, timeout)
    if not html:
        return {"url": url, "chain": chain, "error": "could not fetch page"}

    final = chain[-1]["url"]
    start_host = urlparse(url).netloc.lower().replace("www.", "")
    final_host = urlparse(final).netloc.lower().replace("www.", "")

    p = HeadParser()
    try:
        p.feed(html)
    except Exception:
        pass

    findings, hosts = [], {}
    for r in p.res:
        u = r["url"]
        if u.startswith("//"):
            u = "https:" + u
        if not u.startswith("http"):
            continue
        host = urlparse(u).netloc.lower()
        if not host or host == urlparse(final).netloc.lower():
            continue
        verdict, note = classify(host)
        if verdict == "OK":
            continue
        hosts.setdefault(host, {"verdict": verdict, "note": note, "count": 0,
                                "blocking": False})
        hosts[host]["count"] += 1
        if r["blocking"]:
            hosts[host]["blocking"] = True
            findings.append({"host": host, "verdict": verdict, "note": note,
                             "url": u, "kind": r["kind"], "blocking": True})

    low = html.lower()
    return {
        "url": url,
        "final_url": final,
        "chain": chain,
        "leaves_domain": start_host != final_host,
        "hosts": hosts,
        "blocking_findings": findings,
        "has_recaptcha": "grecaptcha" in low or "recaptcha" in low,
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
        "cn_fonts": bool(re.search(
            r"PingFang|Microsoft\s*YaHei|Hiragino\s+Sans\s+GB|SimSun|微软雅黑", html)),
        "cache_control": headers.get("Cache-Control", headers.get("cache-control", "")),
        "cf_cache": headers.get("Cf-Cache-Status", headers.get("cf-cache-status", "")),
        "ttfb_ms": chain[-1].get("ms", 0),
        "size_kb": round(len(html) / 1024, 1),
    }


C = {"red": "\033[91m", "yel": "\033[93m", "grn": "\033[92m",
     "bold": "\033[1m", "dim": "\033[2m", "off": "\033[0m"}


def report(r, color=True):
    c = C if color else {k: "" for k in C}
    out = []
    A = out.append

    A(f"\n{c['bold']}{'=' * 68}{c['off']}")
    A(f"{c['bold']}  CHINA ACCESSIBILITY CHECK{c['off']}")
    A(f"  {r['url']}")
    A(f"{c['bold']}{'=' * 68}{c['off']}")

    if r.get("error"):
        A(f"\n  {c['red']}ERROR: {r['error']}{c['off']}")
        for h in r["chain"]:
            A(f"    {h['url']} -> {h['status']}")
        return "\n".join(out)

    score, maxs = 0, 0

    # 1. Redirects
    A(f"\n{c['bold']}1. REDIRECT CHAIN{c['off']}")
    for i, h in enumerate(r["chain"]):
        arrow = "   " if i == 0 else " ->"
        A(f"  {arrow} [{h['status']}] {h['url']}  {c['dim']}({h['ms']}ms){c['off']}")
    maxs += 1
    if r["leaves_domain"]:
        A(f"\n  {c['red']}FAIL  The page leaves the domain it started on.{c['off']}")
        A(f"        Visitors typing the original address never see this site.")
    elif len(r["chain"]) > 2:
        A(f"\n  {c['yel']}WARN  {len(r['chain']) - 1} redirects before content.{c['off']}")
        score += 1
    else:
        A(f"\n  {c['grn']}PASS  Stays on the same domain.{c['off']}")
        score += 1

    # 2. Blocking resources
    A(f"\n{c['bold']}2. RENDER-BLOCKING RESOURCES FROM BLOCKED HOSTS{c['off']}")
    A(f"  {c['dim']}These stop the page from drawing until they load or time out.{c['off']}")
    maxs += 1
    blocked_blocking = [f for f in r["blocking_findings"] if f["verdict"] == "BLOCKED"]
    slow_blocking = [f for f in r["blocking_findings"] if f["verdict"] == "SLOW"]

    if blocked_blocking:
        A(f"\n  {c['red']}FAIL  {len(blocked_blocking)} render-blocking "
          f"resource(s) from hosts China blocks:{c['off']}")
        for f in blocked_blocking:
            A(f"    {c['red']}x{c['off']} {f['host']}  {c['dim']}({f['note']}){c['off']}")
            A(f"      {c['dim']}{f['url'][:80]}{c['off']}")
        A(f"\n  {c['red']}      Each of these can hang the page for 30-60 seconds{c['off']}")
        A(f"  {c['red']}      on the networks that drop packets silently.{c['off']}")
    else:
        A(f"\n  {c['grn']}PASS  No render-blocking resources from blocked hosts.{c['off']}")
        score += 1

    if slow_blocking:
        A(f"\n  {c['yel']}WARN  {len(slow_blocking)} render-blocking "
          f"resource(s) from slow hosts:{c['off']}")
        for f in slow_blocking:
            A(f"    {c['yel']}!{c['off']} {f['host']}  {c['dim']}({f['note']}){c['off']}")

    # 3. All external hosts
    A(f"\n{c['bold']}3. ALL EXTERNAL HOSTS{c['off']}")
    maxs += 1
    bl = {h: v for h, v in r["hosts"].items() if v["verdict"] == "BLOCKED"}
    sl = {h: v for h, v in r["hosts"].items() if v["verdict"] == "SLOW"}
    if bl:
        A(f"\n  {c['red']}Blocked in China ({len(bl)}):{c['off']}")
        for h, v in sorted(bl.items()):
            tag = f" {c['red']}[RENDER-BLOCKING]{c['off']}" if v["blocking"] else ""
            A(f"    x {h:38s} x{v['count']}  {c['dim']}{v['note']}{c['off']}{tag}")
    if sl:
        A(f"\n  {c['yel']}Slow / unreliable ({len(sl)}):{c['off']}")
        for h, v in sorted(sl.items()):
            tag = f" {c['yel']}[RENDER-BLOCKING]{c['off']}" if v["blocking"] else ""
            A(f"    ! {h:38s} x{v['count']}  {c['dim']}{v['note']}{c['off']}{tag}")
    if not bl and not sl:
        A(f"  {c['grn']}PASS  No problem hosts found.{c['off']}")
        score += 1

    # 4. Forms
    A(f"\n{c['bold']}4. FORM SUBMISSION{c['off']}")
    maxs += 1
    if r.get("captchas"):
        for cap in r["captchas"]:
            A(f"  {c['red']}FAIL  {cap} detected.{c['off']}")
        A(f"        A captcha needs a token from its own host before a form will")
        A(f"        submit. From China that request fails, so enquiries cannot")
        A(f"        be sent at all - this does not go away once the page loads.")
        A(f"        {c['dim']}Fix: Geetest, Tencent Captcha, or a honeypot field.{c['off']}")
    else:
        A(f"  {c['grn']}PASS  No blocking captcha detected.{c['off']}")
        score += 1

    if r.get("widgets"):
        A(f"\n{c['bold']}4b. CONSENT / CHAT WIDGETS{c['off']}")
        for w in r["widgets"]:
            A(f"  {c['yel']}WARN  {w}.{c['off']}")
        A(f"        These load from hosts with no mainland PoP, and they occupy")
        A(f"        first-screen area. Baidu's landing page whitepaper requires")
        A(f"        main content to fill 50%+ of the first screen on mobile.")
        A(f"        {c['dim']}Check the first screen as rendered on a mainland device.{c['off']}")

    # 5. Analytics
    A(f"\n{c['bold']}5. ANALYTICS COVERAGE{c['off']}")
    maxs += 1
    if r["has_ga"] and not r["has_cn_analytics"]:
        A(f"  {c['red']}FAIL  Google Analytics / Tag Manager only.{c['off']}")
        A(f"        Both are blocked in China, so Chinese visitors are invisible")
        A(f"        in reporting. You cannot measure the problem or the fix.")
        A(f"        {c['dim']}Fix: add Baidu Tongji (hm.baidu.com).{c['off']}")
    elif r["has_cn_analytics"]:
        A(f"  {c['grn']}PASS  Chinese analytics present.{c['off']}")
        score += 1
    else:
        A(f"  {c['yel']}WARN  No analytics detected at all.{c['off']}")

    # 6. Secondary
    A(f"\n{c['bold']}6. SECONDARY CHECKS{c['off']}")
    cc = (r["cache_control"] or "").lower()
    if "no-store" in cc or "no-cache" in cc:
        A(f"  {c['yel']}WARN  Page sent with '{r['cache_control']}'{c['off']}")
        A(f"        {c['dim']}The CDN caches nothing; every visit crosses to Europe.{c['off']}")
    else:
        A(f"  {c['grn']}OK    Cache-Control: {r['cache_control'] or '(none)'}{c['off']}")
    if r["cf_cache"]:
        A(f"  {c['dim']}      CDN cache status: {r['cf_cache']}{c['off']}")

    A(f"  {'OK   ' if r['cn_fonts'] else 'WARN '} Chinese font stack: "
      f"{'present' if r['cn_fonts'] else 'absent (text uses device default)'}")
    A(f"  {'OK   ' if r['has_icp'] else 'INFO '} ICP filing on page: "
      f"{'yes' if r['has_icp'] else 'not shown'}")
    A(f"  {c['dim']}      (ICP only required to host INSIDE mainland China){c['off']}")
    if r["cn_social"]:
        A(f"  {c['grn']}OK    Chinese social present: "
          f"{', '.join(r['cn_social'])}{c['off']}")

    A(f"  {c['dim']}      TTFB {r['ttfb_ms']}ms | HTML {r['size_kb']}KB "
      f"(measured from where you ran this, not from China){c['off']}")

    # Verdict
    A(f"\n{c['bold']}{'=' * 68}{c['off']}")
    col = c["grn"] if score == maxs else (c["yel"] if score >= maxs - 1 else c["red"])
    A(f"{c['bold']}  SCORE: {col}{score}/{maxs} checks passed{c['off']}")
    if blocked_blocking:
        A(f"\n  {c['red']}This page can hang for 30-60s in mainland China.{c['off']}")
        A(f"  {c['dim']}  Whether it does depends on the visitor's province and{c['off']}")
        A(f"  {c['dim']}  carrier. Some networks refuse the blocked connection{c['off']}")
        A(f"  {c['dim']}  instantly and the page loads fine; others stay silent{c['off']}")
        A(f"  {c['dim']}  and the browser waits. Same code, opposite experience -{c['off']}")
        A(f"  {c['dim']}  which is why one successful test proves nothing.{c['off']}")
    A(f"{c['bold']}{'=' * 68}{c['off']}\n")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(
        description="Check whether a website is accessible from mainland China.")
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
        print(report(r, color=not a.no_color))
        if r.get("error") or r.get("leaves_domain") or \
           any(f["verdict"] == "BLOCKED" for f in r.get("blocking_findings", [])):
            failed = True

    if a.json:
        with open(a.json, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"JSON written to {a.json}")

    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()

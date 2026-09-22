#!/usr/bin/env python3
"""
baidu_serp.py - observed Baidu rank table via the DataForSEO Baidu SERP API.

Produces one row per keyword x device with organic position, absolute position
(counting ads and feature blocks), what sits above the first owned result, the
top domains, and the related searches Baidu showed. Writes JSON and CSV.

Credentials: DATAFORSEO_LOGIN and DATAFORSEO_PASSWORD in the environment, or in
a .env file passed with --env. With no credentials the script prints a BLOCKED
notice and exits 2, so the audit records the gap instead of inventing a number.

Usage:
    python3 baidu_serp.py --keywords-file kw.txt --brand example.cn,example.com \
        --device desktop,mobile --out rank_2026-09-22

    kw.txt: one keyword per line, optionally "<keyword><TAB><intent group>".

Cost: DataForSEO charges per SERP fetched (see their pricing page). --resolve
asks for the real destination URL behind Baidu's redirect links at ten times the
base price; leave it off unless you need it.

Standard library only.
"""

import argparse
import base64
import csv
import json
import os
import sys
import time
import urllib.error
import urllib.request

API = "https://api.dataforseo.com/v3/"
METHOD = "DataForSEO Baidu SERP API (datacenter fetch, logged out)"


def load_env(path):
    if not path or not os.path.exists(path):
        return
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def credentials():
    login = os.environ.get("DATAFORSEO_LOGIN")
    pw = os.environ.get("DATAFORSEO_PASSWORD")
    if not login or not pw:
        return None
    return base64.b64encode(f"{login}:{pw}".encode()).decode()


def call(auth, path, data=None, timeout=90):
    req = urllib.request.Request(
        API + path,
        data=json.dumps(data).encode() if data is not None else None,
        headers={"Authorization": "Basic " + auth,
                 "Content-Type": "application/json"},
        method="POST" if data is not None else "GET")
    try:
        return json.load(urllib.request.urlopen(req, timeout=timeout))
    except urllib.error.HTTPError as e:
        return {"status_code": e.code, "status_message": e.read().decode("utf-8", "replace")[:300], "tasks": []}


def read_keywords(path, inline):
    kws = []
    if path:
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.rstrip("\n")
                if not line.strip() or line.startswith("#"):
                    continue
                parts = line.split("\t")
                kws.append((parts[0].strip(), parts[1].strip() if len(parts) > 1 else ""))
    for k in inline or []:
        kws.append((k, ""))
    return kws


def host_matches(domain, patterns):
    d = (domain or "").lower().lstrip(".")
    if d.startswith("www."):
        d = d[4:]
    for p in patterns:
        p = p.lower().strip()
        if not p:
            continue
        if p.startswith("www."):
            p = p[4:]
        if d == p or d.endswith("." + p):
            return True
    return False


def analyse_result(res, brand, competitors):
    items = res.get("items") or []
    organic = [i for i in items if i.get("type") == "organic"]
    non_organic_types = {}
    for i in items:
        if i.get("type") != "organic":
            non_organic_types[i["type"]] = non_organic_types.get(i["type"], 0) + 1

    owned = None
    for i in organic:
        if host_matches(i.get("domain"), brand) or any(b in (i.get("url") or "") for b in brand):
            owned = i
            break

    features_above = []
    if owned:
        for i in items:
            if i.get("rank_absolute", 0) < owned.get("rank_absolute", 0) and i.get("type") != "organic":
                features_above.append(i["type"])

    comp_hits = []
    for i in organic:
        if host_matches(i.get("domain"), competitors):
            comp_hits.append({"domain": i.get("domain"), "organic": i.get("rank_group"),
                              "absolute": i.get("rank_absolute")})

    related = []
    for i in items:
        if i.get("type") == "related_searches":
            for sub in i.get("items") or []:
                related.append(sub if isinstance(sub, str) else (sub.get("title") or sub.get("keyword") or json.dumps(sub, ensure_ascii=False)))

    top = [{"organic": i.get("rank_group"), "absolute": i.get("rank_absolute"),
            "domain": i.get("domain"), "title": (i.get("title") or "").replace("\n", " ").strip()[:80]}
           for i in organic[:5]]

    paid = [i for i in items if i.get("type") == "paid" or i.get("is_paid")]

    return {
        "owned_organic_position": owned.get("rank_group") if owned else None,
        "owned_absolute_position": owned.get("rank_absolute") if owned else None,
        "owned_url": owned.get("url") if owned else None,
        "features_above_owned": features_above,
        "paid_count": len(paid),
        "non_organic_blocks": non_organic_types,
        "organic_count": len(organic),
        "top_organic": top,
        "competitor_hits": comp_hits,
        "related_searches": related,
        "ai_block_present": any("ai" in (i.get("type") or "") for i in items),
        "item_types": res.get("item_types"),
    }


def main():
    ap = argparse.ArgumentParser(description="Observed Baidu rank table via DataForSEO.")
    ap.add_argument("keywords", nargs="*", help="keywords inline (or use --keywords-file)")
    ap.add_argument("--keywords-file")
    ap.add_argument("--brand", default="", help="comma-separated owned domains (suffix match)")
    ap.add_argument("--competitors", default="", help="comma-separated competitor domains")
    ap.add_argument("--location", type=int, default=2156, help="DataForSEO location_code (2156 = China)")
    ap.add_argument("--device", default="desktop", help="desktop, mobile, or desktop,mobile")
    ap.add_argument("--depth", type=int, default=10)
    ap.add_argument("--resolve", action="store_true", help="get_website_url=true (10x cost)")
    ap.add_argument("--env", default=".env", help="path to a .env file with DATAFORSEO_* keys")
    ap.add_argument("--out", default="baidu_rank", help="output prefix for .json and .csv")
    ap.add_argument("--max-wait", type=int, default=600)
    a = ap.parse_args()

    load_env(a.env)
    auth = credentials()
    if not auth:
        print("BLOCKED  No DataForSEO credentials (DATAFORSEO_LOGIN / DATAFORSEO_PASSWORD).")
        print("         Record Baidu rank as blocked in the audit; do not substitute a guess.")
        sys.exit(2)

    kws = read_keywords(a.keywords_file, a.keywords)
    if not kws:
        print("No keywords given.")
        sys.exit(1)
    brand = [b for b in a.brand.split(",") if b.strip()]
    competitors = [c for c in a.competitors.split(",") if c.strip()]
    devices = [d.strip() for d in a.device.split(",") if d.strip()]

    tasks = []
    for kw, group in kws:
        for dev in devices:
            tasks.append({
                "keyword": kw, "location_code": a.location, "language_code": "zh-CN",
                "device": dev, "os": "windows" if dev == "desktop" else "android",
                "depth": a.depth, "get_website_url": bool(a.resolve),
                "tag": f"{group}|{dev}",
            })

    posted, cost = {}, 0.0
    for i in range(0, len(tasks), 100):
        resp = call(auth, "serp/baidu/organic/task_post", tasks[i:i + 100])
        for t in resp.get("tasks", []):
            if t.get("status_code") == 20100:
                posted[t["id"]] = t["data"]
                cost += t.get("cost") or 0
            else:
                print(f"WARN  task_post {t.get('status_code')} {t.get('status_message')} for {t.get('data', {}).get('keyword')}")
    print(f"Posted {len(posted)} tasks. Estimated cost so far: ${cost:.4f}. Waiting for results...")

    results, t0 = {}, time.time()
    while len(results) < len(posted) and time.time() - t0 < a.max_wait:
        time.sleep(8)
        ready = call(auth, "serp/baidu/organic/tasks_ready")
        ids = []
        for t in ready.get("tasks", []):
            for r in t.get("result") or []:
                if r.get("id") in posted and r["id"] not in results:
                    ids.append(r["id"])
        for tid in ids:
            g = call(auth, f"serp/baidu/organic/task_get/advanced/{tid}")
            t = (g.get("tasks") or [{}])[0]
            if t.get("status_code") == 20000 and t.get("result"):
                results[tid] = t["result"][0]
            else:
                results[tid] = {"error": f"{t.get('status_code')} {t.get('status_message')}"}
        print(f"  {len(results)}/{len(posted)} done", flush=True)

    rows = []
    for tid, data in posted.items():
        res = results.get(tid)
        group, dev = (data.get("tag") or "|").split("|", 1)
        base = {"keyword": data["keyword"], "intent_group": group, "device": dev,
                "location_code": a.location, "method": METHOD}
        if not res:
            rows.append({**base, "status": "pending", "note": "no result within max-wait"})
            continue
        if res.get("error"):
            rows.append({**base, "status": "failed", "note": res["error"]})
            continue
        rows.append({**base, "status": "completed",
                     "datetime_utc": res.get("datetime"), "check_url": res.get("check_url"),
                     **analyse_result(res, brand, competitors)})

    with open(a.out + ".json", "w", encoding="utf-8") as f:
        json.dump({"method": METHOD, "brand": brand, "competitors": competitors,
                   "location_code": a.location, "estimated_cost_usd": round(cost, 4),
                   "rows": rows, "raw": results}, f, ensure_ascii=False, indent=1)
    cols = ["keyword", "intent_group", "device", "status", "datetime_utc", "owned_organic_position",
            "owned_absolute_position", "features_above_owned", "paid_count", "organic_count",
            "top_organic", "competitor_hits", "related_searches", "check_url", "method", "note"]
    with open(a.out + ".csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow({k: (json.dumps(v, ensure_ascii=False) if isinstance(v, (list, dict)) else v)
                        for k, v in r.items()})

    print(f"\n{'keyword':32s} {'dev':7s} {'org':>4s} {'abs':>4s}  above / top domains")
    for r in rows:
        if r["status"] != "completed":
            print(f"{r['keyword'][:32]:32s} {r['device']:7s} {r['status']}: {r.get('note')}")
            continue
        org = r["owned_organic_position"]
        ab = r["owned_absolute_position"]
        tops = ", ".join((t.get("domain") or "?") for t in r["top_organic"][:3])
        above = ",".join(r["features_above_owned"]) or "-"
        print(f"{r['keyword'][:32]:32s} {r['device']:7s} {str(org or '-'):>4s} {str(ab or '-'):>4s}  {above} / {tops}")
    print(f"\nWrote {a.out}.json and {a.out}.csv. Estimated cost ${cost:.4f}. Method: {METHOD}.")
    print("Label these rows 'observed via API'. They are not a mainland user's SERP in a named city.")


if __name__ == "__main__":
    main()

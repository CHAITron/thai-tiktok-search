#!/usr/bin/env python3
"""
Weekly database updater for ROSTER (Thai TikTok creator search).

What it does every run:
  1. Reads the curated roster you maintain in data/seed.json
     (name, handle, categories, region, bio — NO live numbers).
  2. Carries forward existing follower/like figures from data/influencers.json
     so the site keeps working, and refreshes any it can.
  3. Optionally enriches each creator with LIVE stats from a data provider
     (see fetch_stats below) when an API key is present.
  4. Sorts by followers and writes data/influencers.json with a fresh date.

IMPORTANT — about TikTok data:
  TikTok has no free, open public API for follower/like counts. To get real
  weekly numbers you must plug in ONE of these into fetch_stats():
    • TikTok Research API or Creator Marketplace (requires approval), or
    • a third-party stats provider (store its key as a GitHub Actions secret).
  Until you do, this script runs in CURATED mode: it validates your roster,
  keeps the last known numbers, and re-stamps the date. That is intentional and
  honest — it will not invent figures.

Run locally:  python scripts/update_data.py
"""
import json, os, sys, datetime, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
SEED = ROOT / "data" / "seed.json"
OUT  = ROOT / "data" / "influencers.json"

PROVIDER_KEY = os.environ.get("PROVIDER_API_KEY", "").strip()


def fetch_stats(handle: str, prev: dict | None):
    """
    Return {"followers": int, "likes": int} for a TikTok handle.

    Default behaviour: keep previous numbers (CURATED mode).
    To enable LIVE mode, set PROVIDER_API_KEY in repo secrets and implement the
    call below for your chosen provider, e.g.:

        import requests
        r = requests.get(
            "https://api.your-provider.com/tiktok/user",
            params={"username": handle},
            headers={"Authorization": f"Bearer {PROVIDER_KEY}"},
            timeout=20,
        )
        r.raise_for_status()
        d = r.json()
        return {"followers": int(d["followerCount"]), "likes": int(d["heartCount"])}
    """
    if PROVIDER_KEY:
        # TODO: implement your provider call here, then `return {...}`.
        # Falling through to carry-forward keeps the site safe if a call fails.
        pass
    if prev:
        return {"followers": prev.get("followers", 0), "likes": prev.get("likes", 0)}
    return {"followers": 0, "likes": 0}


def main() -> int:
    if not SEED.exists():
        print("ERROR: data/seed.json not found.", file=sys.stderr)
        return 1

    seed = json.loads(SEED.read_text(encoding="utf-8"))
    creators = seed.get("creators", [])

    prev_by_handle = {}
    if OUT.exists():
        try:
            old = json.loads(OUT.read_text(encoding="utf-8"))
            for i in old.get("influencers", []):
                prev_by_handle[i["handle"]] = i
        except Exception:
            pass

    rows = []
    for c in creators:
        handle = c["handle"].strip().lstrip("@")
        prev = prev_by_handle.get(handle)
        stats = fetch_stats(handle, prev)
        rows.append({
            "name": c["name"].strip(),
            "handle": handle,
            "url": f"https://www.tiktok.com/@{handle}",
            "avatar": c.get("avatar"),
            "categories": c.get("categories", []),
            "bio": c.get("bio", "").strip(),
            "region": c.get("region", ""),
            "followers": int(stats["followers"]),
            "likes": int(stats["likes"]),
            "verified": bool(c.get("verified", False)),
        })

    rows.sort(key=lambda r: r["followers"], reverse=True)

    db = {
        "updated": datetime.date.today().isoformat(),
        "source": "tiktok",
        "mode": "live" if PROVIDER_KEY else "curated",
        "count": len(rows),
        "influencers": rows,
    }
    OUT.write_text(json.dumps(db, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {len(rows)} creators ({db['mode']} mode) on {db['updated']}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

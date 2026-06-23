# ROSTER — Thai TikTok Creator Search

A fast, lightweight, single-page search engine for **Thai TikTok creators**.
Type a characteristic (niche, vibe, city) and get a ranked list — profile, name,
handle, follower/like stats, and a direct link to each TikTok profile.

- **No backend, no build step.** One `index.html` + a JSON data file.
- **Instant client-side search** (AND matching across category, name, handle, region, bio).
- **Updates weekly** through a GitHub Actions cron job.
- Deploys free on **GitHub Pages**.

> The included data is a clearly-labeled **sample roster** so the app works out of
> the box. See *Real data* below to make it live.

---

## 1. Deploy on GitHub Pages (2 minutes)

1. Create a new repo and upload all these files (keep the folder structure).
2. Go to **Settings → Pages**.
3. Under *Build and deployment*, set **Source: Deploy from a branch**, branch
   `main`, folder `/ (root)`, then **Save**.
4. Your site goes live at `https://<your-username>.github.io/<repo>/`.

That's it — the page loads `data/influencers.json` at runtime.

## 2. The weekly update

`.github/workflows/update-database.yml` runs every **Monday 02:00 UTC** (and any
time via *Actions → Weekly database update → Run workflow*). It runs
`scripts/update_data.py`, which:

1. reads your curated roster in `data/seed.json`,
2. refreshes follower/like figures,
3. re-sorts and writes `data/influencers.json` with a new date,
4. commits the change back to the repo.

To let the bot push commits, enable **Settings → Actions → General → Workflow
permissions → Read and write permissions**.

## 3. Real TikTok data (important & honest)

TikTok has **no free public API** for follower/like counts. To get real weekly
numbers, plug one source into `fetch_stats()` in `scripts/update_data.py`:

- **Official:** TikTok Research API or Creator Marketplace (requires approval), or
- **Third-party stats provider:** store its key as a repo secret named
  `PROVIDER_API_KEY` (**Settings → Secrets and variables → Actions**), then
  implement the request in `fetch_stats()` (an example is in the file).

Until you do, the script runs in **curated mode**: it keeps the last known
numbers and re-stamps the date — it never invents figures.

## 4. Maintain your roster

Edit **`data/seed.json`** — this is your source of truth:

```json
{
  "source": "tiktok",
  "creators": [
    {
      "name": "Display Name",
      "handle": "tiktok_username",
      "categories": ["Beauty", "Skincare"],
      "region": "Bangkok",
      "bio": "Short description",
      "verified": true
    }
  ]
}
```

- `handle` builds the profile link `https://www.tiktok.com/@handle` — verify it.
- `categories` become the search tags and the quick-filter chips.
- `avatar` is optional; if omitted, the app draws a clean gradient initials
  avatar (TikTok profile images generally can't be hot-linked reliably).

Run locally to preview: `python scripts/update_data.py`, then open `index.html`.

## Files

```
index.html                       # the whole app (HTML + CSS + JS)
data/influencers.json            # served to the app (auto-generated)
data/seed.json                   # your curated roster (you edit this)
scripts/update_data.py           # weekly updater
.github/workflows/update-database.yml  # weekly cron
```

## Customize

- **Colors/type:** all CSS variables sit in the `:root` block of `index.html`.
- **GitHub link:** update the footer `#repo` href to your repo.
- **Categories:** chips are generated automatically from your data.

---

Built to be small and quick: no frameworks, one network request for data.

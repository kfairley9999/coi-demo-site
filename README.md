# Certificate extraction demo

A static, client-side demo of **Kevin Fairley’s** ACORD 25 certificate-of-insurance extraction tool.

**Status: local only. Do not push, do not enable GitHub Pages, and do not circulate a public URL until Kevin Fairley approves going public.**

The site is ready for a later free GitHub Pages publish under `kfairy9999` (for example `https://kfairy9999.github.io/coi-demo-site/`) once that approval is given.

## What’s in the demo

- Three publicly posted ACORD 25 certificates with precomputed extracted fields, confidence, and review flags:
  - **Resideo Technologies** — born-digital, straight-through, 100% of scored fields correct
  - **Waverly at South Beach** — born-digital, 100% correct, still flagged because the auto combined single limit is blank on the form
  - **Amazing Air** — scanned, 90% accurate, three misses all flagged for a person
- Honest benchmark figures from the November 22, 2026 lab runs:
  - Test 1: **93.2%** field accuracy, n=44
  - Test 2: **90.3%** field accuracy, n=36; digital **100%**; scans **69.5%**; every scan flagged for human review
- The free 30-day pilot and the **$299 / $599 / $999** month-to-month plans
- Review wording uses “a person on our team,” not “licensed reviewer”
- No file uploads, no server, no tracking, no client PII intake

Source data came from `/workspace/acord25-benchmark` (predictions, document scores, public previews, and source URLs). Offer copy follows `/workspace/insurance-agency-pilots/paid-offer/offer-one-pager.md`, with the reviewer wording adjusted as noted above.

## Preview locally

From this directory:

```bash
python3 -m http.server 8765
```

Then open [http://127.0.0.1:8765](http://127.0.0.1:8765). The page loads `data/samples.json` by fetch, so it will not work if you open `index.html` as a `file://` URL.

Desktop and mobile screenshots from the local preview are in `screenshots/`.

## Site map

```
index.html          # single-page site
css/styles.css
js/app.js           # sample switcher, field rendering, zoom
data/samples.json   # precomputed extractions (rebuilt by scripts/build_assets.py)
images/             # compressed public certificate previews
fonts/              # self-hosted Fraunces and IBM Plex Sans (SIL OFL)
favicon.svg
```

To rebuild images and `samples.json` after changing the benchmark outputs:

```bash
python3 scripts/build_assets.py
```

## What is needed to publish (after Kevin approves)

Nothing has been pushed. There is no GitHub remote on this repo.

1. **Kevin’s explicit approval** to make the site public.
2. **A public contact email** (the Contact section currently says one can be added before publish; do not add a personal inbox without that decision).
3. **Create a new GitHub repository** under `kfairy9999`, for example `coi-demo-site`.
   - GitHub Pages on a free personal account only works for a **public** repository. A private repo with Pages requires a paid GitHub plan.
   - The certificates in the demo are already public filings, but the site, the offer, and the benchmark will become world-readable if the repo is public.
4. **Remove the draft guard** in `index.html`: delete `<meta name="robots" content="noindex, nofollow">` only if the site should be indexed, and drop the footer line “Not for public circulation until approved.”
5. **Add the remote and push** (do not do this until step 1 is done):

   ```bash
   cd /workspace/coi-demo-site
   git remote add origin git@github.com:kfairy9999/coi-demo-site.git
   git push -u origin main
   ```

6. **Enable GitHub Pages** on that repo: Settings → Pages → Deploy from branch `main`, folder `/` (root). After a few minutes the site should be at `https://kfairy9999.github.io/coi-demo-site/`.
7. Optional: a custom domain later. No `CNAME` file is included yet.

## Git

This folder is a local git repository on `main`. It has no remotes.

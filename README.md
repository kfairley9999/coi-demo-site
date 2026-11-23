# Certificate extraction demo

A static, client-side demo of **Kevin Fairley’s** ACORD 25 certificate-of-insurance extraction tool.

Live site: [https://kfairy9999.github.io/coi-demo-site/](https://kfairy9999.github.io/coi-demo-site/)

## What’s in the demo

- Three publicly posted ACORD 25 certificates with precomputed extracted fields, confidence, and review flags:
  - **Resideo Technologies** — born-digital, straight-through, 100% of scored fields correct
  - **Waverly at South Beach** — born-digital, 100% correct, still flagged because the auto combined single limit is blank on the form
  - **Amazing Air** — scanned, 90% accurate, three misses all flagged for a person
- Honest benchmark figures from the November 22, 2026 lab runs:
  - Test 1: **93.2%** field accuracy, n=44
  - Test 2: **90.3%** field accuracy, n=36; digital **100%**; scans **69.5%**; every scan flagged for human review
- The free 30-day pilot and the **$299 / $599 / $999** month-to-month plans
- A person on our team reviews flagged fields before delivery
- No file uploads, no server, no tracking, no client PII intake

Source data came from public ACORD 25 filings used in the November 22, 2026 benchmark runs. Contact: [kfairley9999@gmail.com](mailto:kfairley9999@gmail.com).

## Preview locally

```bash
python3 -m http.server 8765
```

Then open [http://127.0.0.1:8765](http://127.0.0.1:8765). The page loads `data/samples.json` by fetch, so it will not work if you open `index.html` as a `file://` URL.

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

This site is served from the `main` branch root with GitHub Pages.

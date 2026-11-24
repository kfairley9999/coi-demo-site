# COI Extract — landing page and demo

Static site for **Kevin Fairley’s** certificate-of-insurance draft service, built for Los Angeles independent agencies.

Live site: [https://kfairley9999.github.io/coi-demo-site/](https://kfairley9999.github.io/coi-demo-site/)

**Offer:** We prepare COI drafts from your records, for approval by your designated reviewer. We don't make coverage decisions.

## What’s on the page

- A three-step how-it-works, an interactive client-side demo, pilot terms, paid plans, privacy notes, and a FAQ
- Three publicly posted ACORD 25 certificates with precomputed extracted fields, confidence, and review flags:
  - **Resideo Technologies** — born-digital, straight-through
  - **Waverly at South Beach** — born-digital, flagged because the auto combined single limit is blank on the form
  - **Amazing Air** — scanned, misses flagged for a person
- Official ACORD 25 test figures (corrections OFF, November 22, 2026, 5:37 PM PT, commit d9034ee) on **22** public certificates (12 digital, 10 scans):
  - **Critical-field accuracy 82.2%** (511 / 622)
  - Overall field accuracy **78.7%** (609 / 774); digital **95.4%** (374 / 392); scans **61.5%** (235 / 382)
  - Straight-through **27.3%** (6 / 22); flag rate **68.2%**; leaked (silent) errors **1 of 22**
  - After the first lock of this set, two extractor rules were changed because of errors on it, so these 22 are not a never-tuned holdout. Lab results are not a production guarantee.
- A free 30-day pilot (up to 50 certificates) and month-to-month plans at **$299 / $599 / $999**
- Lead capture: a native pilot form (name, work email, company, role, monthly certificate volume, optional phone and message, plus UTM/referrer) posts to the `coi-leads` Cloudflare Worker (`https://coi-leads.kfairley9999.workers.dev/lead`), which stores every lead in the `coi-leads` D1 database and emails a copy to kfairley9999@gmail.com via FormSubmit. Honeypot + timing trap + per-IP rate limit. Mailto fallback if the request fails. Worker source and how to view leads: `/workspace/coi-leads/README.md` (box). The site does not upload certificate files.
- Demo video is a YouTube facade (https://youtu.be/J19RP9mMEMc); no YouTube request until the visitor presses play.

The three demo certificates are public ACORD 25 forms. Site-wide accuracy figures are from the official November 22, 2026 test (corrections OFF).

## Preview locally

```bash
python3 -m http.server 8765
```

Then open [http://127.0.0.1:8765](http://127.0.0.1:8765). The demo loads `data/samples.json` by fetch, so it will not work if you open `index.html` as a `file://` URL.

## Site map

```
index.html              # landing page (keep this URL)
css/lp.css              # page styles
js/lp.js                # nav, year, mailto form
js/app.js               # demo switcher, field rendering, zoom
data/samples.json       # precomputed demo extractions and official metrics
images/                 # compressed public certificate previews
fonts/                  # self-hosted Inter (and unused older faces)
favicon.svg, favicon-32.png, apple-touch-icon.png, og.jpg
demo.mp4, poster.jpg    # optional click-to-play walkthrough
```

This site is served from the `main` branch root with GitHub Pages.

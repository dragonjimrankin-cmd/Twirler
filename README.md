# Twirler

Twirler Pictures — independent adult film studio based in Essex, UK.
Site and planning documents for a studio built around one anchor performer, **Lady Carey**, on a three-shoots-a-week production rhythm.

> **18+ only.** This repository contains branding, site copy and business planning for an adult studio. It contains no explicit media.

---

## What is in here

```
index.html          Landing page — Lady Carey hero, production rhythm, latest releases
lady-carey.html     Anchor performer profile
shoots.html         Release slate
studio.html         Studio positioning and on-set standards
booking.html        Booking / collaboration enquiry form
legal.html          Terms, privacy, 18+ and compliance notes
assets/css/site.css Design system (ink / cream / gold / oxblood)
assets/js/site.js   Age gate, nav state, enquiry form composer
business-plan/      twirler-business_plan1.pdf — the growth plan
tools/              build_business_plan.py (PDF), audit_contrast.py (a11y check)
docs/               contrast-audit.md — generated report, 43 surfaces
DEPLOY.md           Deploying to Hatchable (and anywhere else)
```

## Run it locally

No build step, no dependencies. Any static server will do:

```bash
cd Twirler
python3 -m http.server 8000
# open http://localhost:8000
```

Or just open `index.html` in a browser — the age gate and navigation work from `file://` too.

## Deploy it

See **[DEPLOY.md](DEPLOY.md)**. Short version for Hatchable: zip the repo contents (not the repo folder itself) and upload the zip at <https://hatchable.com/deploy>, or connect the GitHub repo there.

## Design notes

- **One performer, one promise.** Every page points back to Lady Carey and to the Mon/Wed/Fri shooting week. Breadth is deliberately traded for recognisability.
- **Non-explicit placeholders.** Release thumbnails are typographic (`LC 041`), not imagery — the site is safe to show to a host, an investor or a payment processor while the real stills are pending.
- **Age gate is a notice, not assurance.** It satisfies courtesy expectations. UK public launch needs a real age-assurance measure; see `legal.html`.
- **No third-party scripts.** No analytics, no ad pixels, no cookie banner needed. Add tooling deliberately and document it.

## Accessibility

- Every text surface is measured against the colour it actually renders on
  (translucent fills are composited first). Run the audit after any palette change:

  ```bash
  python3 tools/audit_contrast.py --write
  ```

  It exits non-zero if anything drops below WCAG AA (4.5:1 body, 3:1 large),
  so it can gate a deploy. Current state: 43/43 pass.
- Keyboard focus is visible site-wide (`:focus-visible`), there is a skip link,
  and interactive targets are at least 44px.
- `color-scheme: dark` plus explicit `option`/placeholder/autofill styling keeps
  browser-native widgets (the booking form's dropdown especially) from rendering
  light-on-dark text.

## Secrets

Nothing in this repo needs a key to run. `.env` is git-ignored; `.env.example` documents the variables.

- Never commit API keys, and never paste them into a chat window.
- If a key has been shared in plain text, treat it as compromised: revoke it in the provider console and issue a new one.
- For deployment, put the key in your shell environment for the session (`read -rs HATCHABLE_API_KEY`) or in the host's secret store — not in a file inside this repo.

## Business plan

`business-plan/twirler-business_plan1.pdf` — market position, the three-a-week content engine, financial model, marketing, compliance and a 12-month roadmap.

Regenerate after edits:

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install reportlab
python tools/build_business_plan.py
```

Output: `business-plan/twirler-business_plan1.pdf`.

## Status

Draft. Pre-launch checklist before the site is public:

- [ ] Replace placeholder release slate with real titles and non-explicit stills
- [ ] Wire a real age-assurance measure
- [ ] Point the booking form at a backend or form service (currently composes an email)
- [ ] Add registered company number and trading address to `legal.html`
- [ ] Register the domain and connect it in Hatchable

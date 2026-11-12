# Deploying Twirler

The site is plain HTML/CSS/JS — no build step, no server, no dependencies. That makes it deployable almost anywhere, including Hatchable's free static hosting.

---

## Hatchable

Two routes, both from the Hatchable console:

### 1. Upload a zip (fastest)

1. Build a zip of the **site contents** — `index.html` at the top level of the zip, not inside a folder:
   ```bash
   cd Twirler
   zip -r ../twirler-site.zip . -x '.git/*' -x '.env' -x 'node_modules/*'
   ```
2. Go to <https://hatchable.com/deploy> and upload `twirler-site.zip`.
3. Hatchable serves it as a static site and gives you a preview URL; attach your domain in the console.

### 2. Connect the GitHub repo

1. Push this repo to GitHub (already done if you can see it there).
2. In <https://hatchable.com/console>, create a project from a GitHub repo and pick `dragonjimrankin-cmd/Twirler`, branch `main`.
3. No build command, no output directory — the site is the repo root. If Hatchable insists on values: build command empty, publish directory `/`.

### API key hygiene

`hatchable.com/console/settings` issues keys prefixed `hb_`. Treat them like passwords:

- Keep the key in your shell environment for the session only:
  ```bash
  read -rs HATCHABLE_API_KEY && export HATCHABLE_API_KEY
  ```
- **Never** commit it, zip it, or paste it into a chat window. Keys pasted in plain text should be revoked and reissued.
- The site itself needs no key. If you later add a build step that calls Hatchable's API, put the key in the host's secret store, not in `assets/js/`.

### Why the agent can't deploy for you

The sandbox this repo was prepared in can only reach GitHub and the npm/PyPI registries — `hatchable.com` and `api.hatchable.com` are not reachable, so no API call or deploy can be made from there. Deployment has to run from your machine or from Hatchable's own console.

---

## Anywhere else

Because it is static, these all work with zero config:

| Host | How |
|---|---|
| Cloudflare Pages | Connect the repo, no build command, output `/` |
| Netlify | Drag the folder onto app.netlify.com/drop |
| GitHub Pages | Settings → Pages → deploy from branch, root |
| Vercel | `vercel` in the repo, framework "Other", output `.` |

### Custom domain

Register a domain (e.g. `twirlerpictures.co.uk`), then point it at the host. For Hatchable, add the domain in the console and create the DNS records it shows. HTTPS is issued automatically by the platform.

---

## Before you go public

Adult sites carry obligations beyond a normal brochure site. Do these first:

1. **Age assurance.** The interstitial gate in `assets/js/site.js` is a notice, not verification. UK providers of online pornography are expected to use age assurance that is technically accurate, robust, reliable and fair under the Online Safety Act 2023. Add a compliant measure (verified card, digital ID, or an age-estimation provider) and record the configuration.
2. **Performer records.** Signed releases plus DOB evidence on file for every scene, retained at least seven years.
3. **Legal pages.** Fill in company number, trading address and a working contact route in `legal.html`; have a solicitor review it.
4. **Payment processor.** Adult-friendly processors (e.g. CCBill, Verotel, SegPay) will ask about age assurance and content compliance before approving the site. The current placeholders exist so the site can pass that review.
5. **Search hygiene.** Pages currently carry `<meta name="robots" content="noindex">`. Remove those tags only when you want the site indexed — most studios keep the indexable marketing page separate from the members area.
6. **Members area.** The site is currently a shop window. A paid area needs a membership platform (hosted paywall or a subscription provider); keep members' content off the static host.

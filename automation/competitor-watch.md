# Competitor Watch — Repeatable Runbook

The confident, repeatable way to see what competitors are posting and produce
**one-better** content. Runs each bi-weekly sprint (Step 3) and on demand.

## Why this method
- ❌ Direct IG grid scrape — blocked (IG anti-bot; Firecrawl refuses the domain).
- ❌ Ahrefs social tools — plan-gated ("Insufficient plan") + own-channels only.
- ✅ **Firecrawl search (images + web + news)** — works now, repeatable, and
  surfaces competitors' real post visuals via Google-indexed images.

## The run (per competitor handle)
For each handle in the reference set:

1. **Images** — `firecrawl_search`, `sources:[{type:"images"}]`,
   query: `"<venue> <city> interior | event | performance | aesthetic"`.
   → collect image URLs (incl. `lookaside.instagram.com` = their IG posts).
2. **Web** — `sources:[{type:"web"}]`, same query + "Instagram".
   → positioning, recurring nights, caption voice, cadence, press.
3. **News** — `sources:[{type:"news"}]` for launches/awards.
4. Synthesize per handle: **visual signature · format · cadence · hooks**.
5. Output the **"go one-better" brief**: what they do → how our venue beats it
   (better space, deeper lore, more confidence).

## Reference set (handles)
- Say Yes / Andys: @delilah, @scarlettweho__love, @ciprianibeverlyhills, @galerieonsunset
- Black Rabbit Rose: @magiccastlehollywood, @barlisla
- Harvard & Stone: @zebulonla, @golddiggersla, @jumbosclownroomofficial, @desertfivespotla
- Madame Siam: @cirquelesoir
- Dirty Laundry: @boilerroomtv, @tenantsofthetrees

## "One-better" standard
For every competitor post format we like, the brief must answer:
1. **What's the format?** (e.g. performer-named reel, slow-pour macro)
2. **What's our advantage?** (the specific room/lore/programming we have)
3. **How do we shoot it better?** (the 7-element Higgsfield concept)
4. **What's the hook + CTA?**

## Baseline finding (Delilah, Say Yes benchmark — live run Jun 2026)
Visual signature: roaring-'20s supper club, Art Deco, lavish chandeliers,
crackling fireplace, "the night carefully staged," live jazz dining,
celeb-loved, Old Hollywood glamour. Confidence-first, atmosphere over promo.
→ **Say Yes goes one-better** with the teal fan sunburst hero icon, the
mezzanine reveal, and the Ms. Bubbles character mystery Delilah doesn't have.

## Cadence
Run the full set every sprint (bi-weekly); spot-run any single handle on demand.
Feeds directly into the bi-weekly content package (`packages/`).

## Note on engagement numbers
This method gives **format, cadence, and visuals** — not exact like/save counts
(no connected tool exposes those for arbitrary accounts). For our OWN
performance baselines, use PostHog + Blotato metrics via `seo-viral-analyst`.

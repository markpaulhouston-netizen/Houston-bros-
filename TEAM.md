# The Marketing Team

A film-quality, AI-powered content studio for Houston Hospitality. Each role is
a **Claude Code skill** in `.claude/skills/` — invoke one and Claude acts in
that role with the right tools and playbook. You are the **Executive Producer**:
you direct and approve; the team executes.

## Org chart

| Role (skill) | Owns | Primary tools |
|--------------|------|---------------|
| 🎬 **creative-director** | Campaign strategy, brand voice, content briefs | Strategy + caption files |
| 🔎 **competitor-scout** | Format/cadence intel from reference accounts | Firecrawl |
| 📈 **seo-viral-analyst** | Keywords, hashtags, virality prediction, performance | Ahrefs, Firecrawl, Higgsfield virality, PostHog |
| 🎥 **video-director** | Cinematic video (image-to-video only) | Higgsfield |
| ✂️ **content-editor** | Format, brand overlays, resize, repurpose | Canva, Adobe |
| 📣 **social-media-manager** | Schedule + publish, calendar, status | Blotato |

## The production line

```
creative-director ──briefs──► video-director / content-editor ──asset──► social-media-manager ──► Blotato ──► posted
        ▲                                                                        │
        └────────── seo-viral-analyst + competitor-scout (research in, metrics back) ──────────┘
```

## How to run a campaign

1. **"Act as creative-director — build this week's Madame Siam brief."**
2. Scout + analyst pressure-test the angle (format + keywords + virality).
3. video-director / content-editor produce the asset (needs real media).
4. social-media-manager schedules it through Blotato.
5. analyst reports back; creative-director adjusts next week.

## Current blockers (Executive Producer to clear)

- [ ] Connect `@madamesiamla` + `@andys_weho` in Blotato.
- [ ] Supply real venue photos/footage (unblocks all production).
- [ ] Verify Black Rabbit Rose Dine & Delight price.
- [ ] Approve the n8n recurring draft-builder (`automation/n8n-workflow.md`).

## Supporting docs
- `strategy/venues.md` · `content-calendar.md` · `captions/` ·
  `automation/blotato-accounts.md` · `automation/n8n-workflow.md`

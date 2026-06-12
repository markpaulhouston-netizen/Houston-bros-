# Houston Hospitality — Marketing Studio

An in-house, AI-assisted content operation for the Houston Hospitality venue
portfolio. This repo is the **durable record** of the strategy and the
**operating system** for getting content scheduled and posted through Blotato.

> Built in Claude Code. Everything here is version-controlled so it is never
> lost between sessions.

## Venues

| Venue | IG Handle | Blotato | Priority | Theme |
|-------|-----------|---------|----------|-------|
| Say Yes | `@sayyesla` | ✅ connected | 🔴 1 (pre-opening) | 1920s Hollywood golden-era ballroom |
| Harvard & Stone | `@harvardandstone` | ✅ connected | 🟡 4 | 1940s factory bar, rock 'n' roll, burlesque |
| Black Rabbit Rose | `@blackrabbitrose` | ✅ connected | 🔴 3 | The only magic-themed lounge in LA |
| Madame Siam | `@madamesiamla` | ⏸️ on hold | ⏸️ on hold | Sideshow Emporium / Asian gypsy circus |
| Dirty Laundry | `@dirtylaundrybar` | ✅ connected | 🟡 5 | Rudolph Valentino speakeasy |
| Andys | `@andys_weho` | ❌ **not connected** | 🟢 6 | Music + celebrity + food (Anderson .Paak) |

> ⚠️ **Action required:** connect `@andys_weho` in Blotato before it can be
> automated. Madame Siam is **on hold** (per EP, Jun 12) — not a blocker for now.
> TikTok is connected (`@yessayla`, `@houstonhouston53`, `@markhouston83`).

## How content reaches a post (the pipeline)

```
Media (photo/video) ──► Blotato create_visual ──► hosted URL
                                                      │
Caption (from captions/) ─────────────────────────►  ├─► Blotato create_post
                                                      │     (accountId + caption
Account (automation/blotato-accounts.md) ────────────┘      + mediaUrl + scheduleTime)
                                                            │
                                                            └─► posts automatically
```

**Key principle:** real venue *photos* can be posted today as IG images and
carousels. AI video (Higgsfield) is a later layer added with real footage —
never text-to-video, which invents a venue that isn't yours.

## Repo map

- `strategy/` — venue briefs: identity, programming, content angles
- `captions/` — ready-to-post caption banks per venue
- `automation/` — Blotato account IDs, posting pipeline, n8n workflow spec
- `content-calendar.md` — master weekly posting schedule across all venues

## Operating rules

1. **No begging, no explaining.** Every post carries the confidence of a
   sold-out show. (Lesson from the competitor audit.)
2. **Real assets only.** Anchor all video generation to real venue photos.
3. **Shareability test.** Before anything posts: "would someone DM this to a
   friend?" Shares are the #1 growth signal.
4. **Cross-promote.** A guest at one venue is a warm lead for the next.

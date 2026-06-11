# Blotato — Connected Accounts & Posting Reference

Pulled live from the connected Blotato workspace (subscription: **active**).
Use these `accountId` values when calling `blotato_create_post`.

## Instagram

| Venue | Handle | accountId | Required field |
|-------|--------|-----------|----------------|
| Say Yes | `@sayyesla` | `48246` | `mediaType: story\|reel` |
| Harvard & Stone | `@harvardandstone` | `51447` | `mediaType: story\|reel` |
| Black Rabbit Rose | `@blackrabbitrose` | `48237` | `mediaType: story\|reel` |
| Dirty Laundry | `@dirtylaundrybar` | `48230` | `mediaType: story\|reel` |
| Houston Bros (personal/portfolio) | `@houston_bros` | `48244` | `mediaType: story\|reel` |
| Traveling Cabin | `@travelingcabin` | `48243` | `mediaType: story\|reel` |

> ❌ **Not yet connected:** `@madamesiamla`, `@andys_weho`.
> Connect both in the Blotato dashboard, then re-run `blotato_list_accounts`
> and add their IDs here.

## TikTok

| Account | Handle | accountId |
|---------|--------|-----------|
| Say Yes | `@yessayla` | `44375` |
| Houston | `@houstonhouston53` | `44404` |
| Mark Houston | `@markhouston83` | `43154` |

TikTok required fields: `privacyLevel`, `disabledComments`, `disabledDuet`,
`disabledStitch`, `isBrandedContent`, `isYourBrand`, `isAiGenerated`.

## Other platforms

| Platform | Account | accountId | Notes |
|----------|---------|-----------|-------|
| YouTube | Mark Houston | `37333` | needs `title`, `privacyStatus`, `shouldNotifySubscribers` |
| LinkedIn | Mark Houston | `22084` | company page subaccount `4849448` (needs admin) |
| Pinterest | `houston2121` | `6698` | needs `boardId` |
| Twitter/X | `@MarkHou69386512` | `18739` | — |

## Posting pipeline (exact tool sequence)

1. **Host the media** — `blotato_create_visual` with the media (or
   `blotato_create_presigned_upload_url` for direct byte upload). Returns a
   Blotato-hosted URL.
2. **Create the post** — `blotato_create_post` with:
   - `accountId` (from tables above)
   - `content` — caption text (from `captions/`)
   - media URL from step 1
   - platform `requiredFields` (e.g. IG `mediaType: reel`)
   - schedule time (omit to post immediately)
3. **Verify** — `blotato_list_schedules` / `blotato_get_schedule`.
4. **Status** — `blotato_get_post_status` after it fires.

## Hard requirement

A post will not fire without **media**. Captions + accounts are ready here;
media must be supplied (real venue photos to start). This is the gate between
"system built" and "content going out."

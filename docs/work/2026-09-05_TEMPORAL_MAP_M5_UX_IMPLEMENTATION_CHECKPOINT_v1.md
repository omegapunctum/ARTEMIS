# M5 UX implementation checkpoint

- Scope owner: [bounded UX decision](2026-09-05_TEMPORAL_MAP_M5_BOUNDED_UX_SCOPE_v1.md), merged in #409.
- Implementation: #411, draft; not merged or published.
- This record describes implemented changes and available verification, not acceptance of all seven findings.

## Implementation

| Finding | Change | Remaining evidence |
| --- | --- | --- |
| Chronology and periods | Stable numbered Presence sequence, period title/current cue, map/sequence hover and focus, selected item scrolled into view | Browser interaction and legibility |
| Popup and drawer | Opening details removes popup; selecting another Presence closes stale drawer; closing restores keyboard focus | Browser interaction |
| Visual density | Smaller inner marker with preserved 36 px target; compact controls and explicit focus style | Pointer/keyboard and visual evidence |
| Timeline height | Compact bottom timeline retains Range/Scrub, calendar values, live status and route disclosure | Measured responsive composition |
| Header collision | Header inset reserves navigation-control space; navigation included in collision measurement | Desktop/tablet/mobile screenshots |
| EN/RU | Presentation dictionary and explicit switch; dynamic labels and round-trip restoration | Same-selection/time EN/RU screenshots |
| Drawer/attribution | Measured banner, dock and attribution dimensions determine drawer bounds | No overlap or clipping at supported profiles |

No historical fixture, canonical identifier, Claim, locator, route geometry or Airtable behavior changes. Unknown-route connectors remain fail closed. Historical #408 `ITERATE` remains the last product result.

## Verification performed

- 266 tests passed: the 13 Core workflow test modules plus repository governance contracts.
- All six source/projection validators from `release-gate.yml` passed.
- Public-preview build and its four Core metadata assertions passed.
- `tests/m5_ux_behavior.cjs` executes shipped functions with a small DOM adapter: sequence order, selection/period state, filtering, bidirectional emphasis, focus restoration, no connectors and EN/RU round trip. It does not emulate browser layout or establish end-to-end URL restoration.
- Independent code audit found and prompted fixes for stale drawer state, missing focus restoration, untranslated chronology, hidden temporal status and offscreen sequence selection.
- Independent governance audit synchronized ten active owner documents. No new manual outcome or Gate D completion is asserted.

## Blocking evidence

The cloud browser blocked the local preview URL and the local-file artifact under its URL security policy. No screenshot, responsive pass or live map interaction result was obtained. No alternative browser or policy workaround was used.

Keep #411 draft until the exact head has the required Core/Globe/Geospatial checks and reproducible browser evidence for desktop, tablet and hosted mobile, keyboard/pointer use, no clipping/overlap, and EN/RU with identical selection/time. Publishing and a fresh manual product check remain subsequent steps; the owner's merge/publication authorization is already recorded in the working conversation.

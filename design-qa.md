# Mobile Explorer design QA

Final result: passed

## Source and rendered comparison

Source visual truth: `/workspace/scratch/01de677631d9/generated_images/exec-74979d4c-4422-4ab2-abf6-208360ee1268.png` (853 × 1844 pixels), amended by the owner's request for compact wheels, a content-sized panel, no visible Time/From/To labels and the existing renderer. Generated geography is layout guidance, not data or a replacement asset.

Full-view comparison input opened before handoff: `/workspace/scratch/01de677631d9/mobile-comparison-390.png`. The source was aspect-preservingly normalized to 390 × 843, alongside the actual 390 × 844 CSS/DPR1 browser screenshot at `/workspace/scratch/01de677631d9/mobile-nativec3/artemis-unified-browser-evidence/390/mobile-expanded-staged-year.png`. Focused years/timeline comparison: `/workspace/scratch/01de677631d9/mobile-comparison-years.png`. No phone frame or browser chrome is included.

State: expanded interval calendar with a pending year edit. The reference has illustrative RU copy and 1472–1502; the implementation uses current source-backed EN copy and a 1453–1519 draft over canonical 1452–1519. Camera, renderer, data, presets and semantic notes intentionally remain. This is a composition/density comparison, not a pixel clone or validation of illustrated geography/dates. Separate actual RU source/evidence states were inspected.

The compared calendar/brand/controls are unchanged in final runtime/CSS `1381565c8f9430d08af0594bcebbfd466950d872`; the subsequent CSS correction affects inspector bottom clearance only. Its rendered implementation is available in [the source-bound browser artifact](https://github.com/omegapunctum/ARTEMIS/actions/runs/37796542484/artifacts/11558997418), locally inspected under `/workspace/scratch/01de677631d9/mobile-native138/artemis-unified-browser-evidence/`.

## Findings and comparison history

- **P2 inspector lower edge — closed.** Floating Layers/Search controls occupied the lower-right 44 px of the scrolling inspector, risking inaccessible final source-native lines. Pre-fix evidence: `mobile-native0b/artemis-unified-browser-evidence/500/failure.png` and control/card geometry. Fix: mobile inspector bottom padding 64 px, also retained in landscape. Post-fix evidence: `mobile-native138/artemis-unified-browser-evidence/{390,500,844}/mobile-source-card-scroll-end.png`. All three actual tail captures were opened and independently inspected: final text is above the controls. Native maximum scroll and unchanged card/state/camera assertions passed; the 390 px tail ends at y=625.05 versus tools y=655, and the 500 px tail at y=681.02 versus tools y=711. The same 390 × 844 catalog/source/projection capture before and after the fix was also inspected; the added tail state establishes reachability. The visual mock does not specify a raw-source card, so its full readability is assessed against the retained source-disclosure requirement.
- No actionable P0/P1/P2 findings remain in the inspected portrait, landscape and desktop compositions. Wheels are 44 px high; the panel follows content without a fixed empty region. Existing presets and semantic notes account for extra expanded rows.
- P3 optional polish: a visual grip could replace toggle wording while retaining an accessible name/hit target; a visible pending-date hint could supplement Apply/Cancel and the current live announcement. These do not expand this bounded delivery.

The initial full-view and focused comparison found no other density/fidelity correction. The additional inspector state identified the P2 above; rendered post-fix tail evidence closes it. Browser transport troubleshooting is not counted as a design-QA iteration.

## Required fidelity surfaces

| Surface | Assessment |
| --- | --- |
| Fonts/typography | Existing system/Inter fallback stack retained; no unverified source font identity asserted. Brand hierarchy, 16 px search and tabular selected years remain readable, neighbors are smaller, focus is visible, and actual RU titles/disclosures wrap. |
| Spacing/layout | One map, progressive panels and a permanently visible collapsed timeline. Actual 390 px collapsed header/dock leave 639 px for the map. Year wheels remain 44 px in both states; expanded panel height follows content. Inspector P2 is closed by tail evidence. |
| Colors/tokens | Existing dark navy backing, blue active controls and pale text retained. Focus indication is visible. Complete contrast/accessibility conformance is not asserted. |
| Image quality/assets | Actual Natural Earth/MapLibre rendering retained; generated globe art is not shipped. Camera, geography and source bundle are preserved. No generated geography, placeholder, replacement logo or decorative SVG was introduced. |
| Copy/content | Visible Time/From/To labels absent on mobile; localized accessible year/CE names retained. Presets, source-native facts, provenance, historical-applicability qualifications and actual map attribution remain available. EN/RU card states are exercised. |

## Interactions, console checks and limits

Native reports at `1381565…` pass 1440 × 900 (221 actions), 500 × 900 and 390 × 844 (397 actions each), with exact CSS viewport/DPR1 identities. Their source-bound reports cover visible controls, trusted native wheel delivery, pointer year edits, Apply/Cancel/bounds, handle collapse, same map/camera during drafts, layers/search/projection, source/evidence cards, URL/history and desktop regression. The 844 × 390 run passes wheel/panel/card/search states and reaches final canvas picking; the View panel is intentionally still open. The final harness closes panels through genuine buttons before map input and checks that closing preserves the workspace. Full final-head technical/CI acceptance is separate from this visual result.

Console/error coverage is bounded: native evaluations fail on returned JS exceptions and explicit fatal UI errors are checked; no complete CDP console-event inventory is collected. Earlier c3 screenshot/DOM hashes were independently verified; no new claim is made that all 138 hashes were independently recomputed after the workspace connection interruption. The post-fix 138 PNGs were opened before that interruption.

DPR1 Chromium with desktop input does not establish physical iPhone Safari, physical touch, nonzero safe-area behavior, complete accessibility, comparative value or user comprehension. CSS safe-area support and owned canceled-pointer tests are included.

## Implementation checklist

- [x] Compact 44 px years without native date-entry keyboard.
- [x] Content-sized collapsible panel and persistent shared timeline.
- [x] Existing renderer, bundle, source disclosures and temporal semantics.
- [x] Independent source/visual review and relevant local checks.
- [x] Post-fix raw-card tail captures close P2.
- [x] Narrow and landscape rendered composition/wheel/card inspection.
- Final exact-head technical acceptance and separately verified publication are recorded in PR #479 after their checks; this QA does not claim public availability.

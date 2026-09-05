# M5 post-#411 correction

## Decision and evidence

PR #411 merged as `f1d54af` and was published. The owner reviewed the public site and supplied a screenshot: connections between elements are missing and the timeline is still too tall. This is a fresh **ITERATE**, not successful acceptance. The owner explicitly requested a correction followed immediately by merge/publication.

This instruction supersedes the no-map-connector **presentation** restriction in the earlier #409 scope. Enable dashed straight chronological links between existing visible Presence anchors, with a persistent EN/RU legend saying they are order, not travel routes. This does not authorize inferred historical routes, continuous positions, new data, sources or Relations. `unknown_route`, `route_geometry=null`, and the canonical projection remain unchanged; only renderer presentation produces lines.

## Bounded implementation

- Enable the existing chronological connector renderer; filter both endpoints with the same Range/Scrub visibility as markers. Never bridge over a hidden endpoint.
- Make the dock three compact working rows on desktop: period/mode controls, calendar controls, sequence/status. Retain readable dates, 32px-or-larger controls, horizontal access to all sequence items, and an always-visible status. Mobile may use a fourth compact status row.
- Remove the redundant subject column and the large status panel; the product header still identifies Leonardo.
- Use measured dock height for map fitting as well as drawer/attribution clearance.
- Run Core and hosted profile gates before merge; publication enables the next manual check, which is not a pre-merge dependency.

Repeated visits can share coordinates and retraced chronology segments can overlap. Numbered sequence cues remain necessary; dashed links are not proof of individually distinguishable routes or of travel geometry.

## Status boundaries

#411 is merged/published. This two-finding follow-up is implementation work until its PR/deployment completes; see its GitHub merge and Pages run for publication evidence. A fresh owner check remains pending after that publication. Earlier checkpoint documents describe their historical pre-merge state, not current availability.

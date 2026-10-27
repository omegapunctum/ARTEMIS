# Independent bounded Amboise calendar and scope review

Original review: 2026-10-24. Restored and prospective specification rechecked: 2026-10-26, following temporary workspace pruning. Reviewer: distinct agent /root/calendar_review. This is a reconstruction with new inspection where stated, not a claim that lost file bytes were recovered.

## Verdict

ACCEPT_BOUNDED_YEAR_RESOLUTION_POLICY and ACCEPT_BOUNDED_CONTEXT_SPECIFICATION under the constraints below. Reviewed restored specification: docs/work/2026-10-24_AMBOISE_CONTEXT_v1.md, SHA-256 c2ad4264371a646dc0aefc3859bfe134f8e4722493ad87e4a6df32292a6eae12.

Year-level admission is justified for this single event after retaining explicit calendar interpretations; exact canonical day remains unresolved. This is a separately reviewed calendar policy permitted by uncertainty contract section 2, not a frozen-contract rewrite or permission to extract years from arbitrary unresolved dates. Historical evidence-only review remains an accurate earlier checkpoint.

## Inspected evidence and inference

BnF BP16_103413, https://bp16.bnf.fr/ark:/12148/cb41876426p/ , conventional title and Notes: event source date 25 April 1518 (n. st.), distinct from edition year [1518]. Original printed witness not inspected. Prior independent review inspected catalogue and university scholarship; this restoration does not upgrade provenance.

BnF manual https://kitcat.bnf.fr/manuel-format/manuel-de-catalogage-des-manuscrits-medievaux , section 6, Example 16, re-opened and located on 2026-10-26. A nouveau-style date is explicitly encoded calendar=julian. Therefore year style and calendar differ; n.st. alone cannot prove Gregorian interpretation. This manuscript manual is contextual evidence, not proof that BP16 follows its encoding rules. Its example NORMAL value is not a conversion algorithm.

Paris Observatory https://media4.obspm.fr/public/ressources_lu/pages_calendriers/mctc-calendrier-gregorien.html , Definition: directly read in the original 2026-10-24 review. It states the 1582 ten-day Julian/Gregorian change and Gregorian century leap rules, and France's December 1582 adoption. Re-fetch on 2026-10-26 timed out twice; this record relies on the earlier actually retrieved text, not a successful new fetch. No divergent secular leap falls between April 1518 and October 1582; the offset on this date is therefore ten days. This last step is reviewer calculation from stated rules.

FranceArchives page was blocked by JS/cookie wall in the earlier review and is not used.

## Accepted bounded normalization

Policy ID: amboise-baptism-1518-calendar-year-v1.

J: source day is Julian with normalized year style: 1518-04-25 Julian becomes 1518-05-05 proleptic Gregorian.
G: source notation was already rendered in Gregorian: 1518-04-25 remains 1518-04-25.

These are interpretations of catalogue notation, not two witnesses asserting different historical dates. Preserve both assumptions and supporting source refs without selecting a winner. Both fall in canonical year 1518. Year membership is therefore invariant for the admitted interpretations; it is not merely an arbitrary presentation index. The event heading and scholarly context establish the event year independently of edition date. Do not invent a 1517/1519 interpretation absent evidence; if new evidence affects year style, fail closed and reopen this bounded policy.

Canonical exact day remains null/unresolved. Duration remains unknown. The two possible normalized days are not a continuous event span, and the derived year is not a year-long baptism. Preserve source-native day/qualifier separately. Year queries only: Range including 1518 includes the contextual disclosure; adjacent years exclude it; Scrub only at 1518, not cumulative. Reject finer-resolution queries until independently reviewed.

## Scope acceptance and implementation conditions

The minimal bilingual context section in existing Clos Luce residence details is accepted. Context is curated selection, not a historical Relation. No new marker/layer, no residence coordinates reused as ceremony coordinates, geometry null. No Leonardo attendance/involvement/influence claim. Source-relative date, named Amboise, inspectable links/locators and residence-is-not-attendance disclosure required.

Immutable packet must preserve J/G alternatives, policy ID, atomic source assertions/evidence bindings, unresolved exact day, unknown duration and provenance limits. Validate packet identity and digest. Tests must verify ten-day conversion independently, both alternatives' shared year, wrong-year exclusion, Range/Scrub distinctions, stale context removal and language switching. Reject automatic application of the policy to any other date/event. Frozen inputs unchanged.

No unresolved material prospective finding remains. Implementation can start under this accepted bounded specification. Actual implementation still requires exact-content independent review, relevant tests/native desktop-narrow inspection and separate publication evidence. This review establishes neither implementation success nor human value; no broader successor is opened.

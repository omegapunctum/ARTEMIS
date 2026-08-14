# ARTEMIS Globe runtime spike fixtures v1

This directory contains R&D-only inputs for issue #343.

## Files

- `engine_evaluation.json` — executable engine comparison for the first Globe spike.
- `synthetic_earth_context.geojson` — local synthetic sphere/context surface and graticule.
- `natural_earth_110m_land.geojson` — pinned real Natural Earth land context for the Gate D review artifact; never historical geometry.
- `capability_path.geojson` — explicit non-semantic LineString used only to prove renderer polyline capability.

## Critical boundary

The capability path is **not historical knowledge**.

It has:

- no World Model `object_ref`;
- `pick_as_knowledge=false`;
- an explicit capability-only label.

The reviewed `trajectory-mara-vale` route gap remains unresolved and must not be replaced by this line or any other interpolation.

## Generated runtime data

`scripts/build_globe_spike.py` combines:

- reviewed World Model fixture;
- merged Explorer State fixture;
- merged Render Projection builder;
- merged geospatial asset manifest;
- these R&D-only capability fixtures.

The build output is generated outside the checked-in public runtime and includes:

- neutral projection JSON;
- Globe adapter JSON;
- Explorer State;
- geospatial asset manifest;
- bundled Natural Earth present-day physical-geography context;
- non-semantic capability path;
- static HTML/CSS/JS runtime;
- deterministic build metadata.

The generated directory is suitable for a local static server and CI artifact. It is not a GitHub Pages/public product entrypoint.

# ARTEMIS — Gate D Earth Context Provider Policy v1

## Status

- Type: active Gate D implementation policy and review evidence.
- Date: 2026-08-14.
- Issues: #355; follows the merged #342 Geospatial Asset Manifest contract.
- Runtime: generated Globe review artifact; may be served only through the authorized labelled `/globe/` R&D preview.
- Historical authority: none.

## Decision

The default Gate D Globe review artifact uses a bundled copy of **Natural Earth 1:110m Land v4.0.0** as real, generalized physical-geography context.

This layer is classified only as `present_day_context`. It is not historical coastline evidence, a 1502 reconstruction, a World Model object, or a Claim about Leonardo's route. The frozen Gate C package remains geometry-free where evidence does not authorize geometry.

The selected source is intentionally static and local:

- provider adapter: `static_local`;
- source dataset: Natural Earth `ne_110m_land`, version `4.0.0`;
- source repository commit: `ca96624a56bd078437bca8184e78163e5039ad19`;
- source blob SHA: `04811d72fff2701ec67587e30ad8942675b511e3`;
- source path: `geojson/ne_110m_land.geojson`;
- checked-in runtime fixture: `fixtures/globe_runtime/v1/natural_earth_110m_land.geojson`;
- runtime manifest: `fixtures/geospatial_assets/v1/gate_d_runtime.json`.

The pinned upstream file is [available in the Natural Earth vector repository](https://github.com/nvkelso/natural-earth-vector/blob/ca96624a56bd078437bca8184e78163e5039ad19/geojson/ne_110m_land.geojson). Natural Earth documents 1:110m physical vectors as coarse locator-scale data and identifies Land v4.0.0 on its [official download page](https://www.naturalearthdata.com/downloads/110m-physical-vectors/).

## Selection rationale

The bundled Natural Earth layer satisfies the bounded Gate D need without adding a live tile-provider dependency:

| Requirement | Decision |
|---|---|
| Real Earth context | Natural Earth land polygons replace the synthetic sphere surface in the default artifact |
| Historical separation | Every collection/feature is `capability_only=true` and `semantic_role=present_day_context`; no World Model identity is present |
| CRS | EPSG:4326 / longitude-latitude, matching Natural Earth's documented WGS84 geographic coordinate system |
| Provenance | Dataset version, pinned repository commit, blob SHA, source path and retrieval date are recorded |
| License | Natural Earth data are public domain under the [official Terms of Use](https://www.naturalearthdata.com/about/terms-of-use/) |
| Attribution | Not legally required; the review UI still displays voluntary source attribution |
| Runtime network | None for Earth context; the only default network dependency remains the pinned MapLibre engine CDN |
| Secrets | None; no token, query credential or runtime environment secret is accepted |
| Cache/offline | Bundled bytes may be cached, used offline and redistributed |
| Failure mode | Fail closed if the context metadata, asset reference or manifest semantics are invalid |

The 1:110m layer is suitable for globe-scale orientation. It is not accepted for local measurement, coastline-change analysis, terrain quality, political boundary interpretation, or historical reconstruction.

## Runtime boundary

The provider remains downstream of the canonical semantic path:

`World Model → Explorer State → Render Projection → Globe adapter → renderer`

Swapping or removing the Earth-context provider must not change the World Slice, Explorer State, Render Projection, World Model identity, Claim state, uncertainty, or source/evidence records.

Earth-context features:

- cannot carry `object_ref` or `world_model_object_ref`;
- cannot bind World Model Claims or Uncertainties;
- cannot declare historical validity or a reconstruction method;
- cannot become selectable historical knowledge;
- cannot imply that modern/generalized land geometry is valid for 1502.

The synthetic terrain asset remains only a non-live adapter fixture. This decision does not select a real DEM and does not claim terrain-quality acceptance. A future terrain or imagery provider must independently satisfy vertical reference, provenance, license, cache, secret and public-runtime rules before use.

## Gate effect

This increment supplies the real Earth-context/provider-policy evidence required by Gate D. It does not:

- open Gate E;
- make the Globe product-ready or authorize a public route beyond the bounded R&D preview;
- promote the Leonardo package;
- authorize historical geometry;
- change Airtable or import any historical rows;
- upgrade the current public 2D MapLibre runtime;
- authorize CesiumJS or a backend/framework rewrite.

Gate D remains active until the remaining interaction, accessibility, performance and explicit exit-decision checks are completed.

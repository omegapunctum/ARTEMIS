const fs = require("fs");
const axios = require("axios");

const TOKEN = process.env.AIRTABLE_TOKEN;
const BASE = process.env.AIRTABLE_BASE;

const TABLE = "Features";

const URL = `https://api.airtable.com/v0/${BASE}/${TABLE}`;

async function fetchAll() {

  let records = [];
  let offset = null;

  while (true) {

    const res = await axios.get(URL, {
      headers: {
        Authorization: `Bearer ${TOKEN}`
      },
      params: { offset }
    });

    records = records.concat(res.data.records);

    if (!res.data.offset) break;

    offset = res.data.offset;
  }

  return records;
}

function toGeoJSON(records) {

  const features = [];

  for (const r of records) {

    const f = r.fields;

    if (!f.latitude || !f.longitude) continue;

    features.push({

      type: "Feature",

      geometry: {
        type: "Point",
        coordinates: [
          parseFloat(f.longitude),
          parseFloat(f.latitude)
        ]
      },

      properties: {
        id: r.id,
        layer_id: f.layer_id,
        layer_type: f.layer_type,
        name_ru: f.name_ru,
        name_en: f.name_en,
        title_short: f.title_short,
        description: f.description,
        architect: f.architect,
        style_label: f.style_label,
        date_start: f.date_start,
        date_construction_end: f.date_construction_end,
        date_end: f.date_end,
        influence_radius_km: f.influence_radius_km,
        sequence_order: f.sequence_order,
        image_url: f.image_url,
        source_url: f.source_url,
        tags: f.tags,
        is_active: f.is_active
      }

    });
  }

  return {
    type: "FeatureCollection",
    features
  };
}

async function run() {

  if (!TOKEN) throw new Error("AIRTABLE_TOKEN missing");
  if (!BASE) throw new Error("AIRTABLE_BASE missing");

  const records = await fetchAll();

  const geojson = toGeoJSON(records);

  if (!fs.existsSync("data")) fs.mkdirSync("data");

  fs.writeFileSync(
    "data/features.json",
    JSON.stringify(records, null, 2)
  );

  fs.writeFileSync(
    "data/features.geojson",
    JSON.stringify(geojson, null, 2)
  );

  console.log("Export complete:", records.length);
}

run();

// scripts/export-airtable.js
// Node.js script to export Features and Layers from Airtable
// Writes:
//   data/features.json      - raw Airtable records for Features
//   data/features.geojson   - geojson FeatureCollection (points)
//   data/layers.json        - array of Layers records
//
// Требования: NODE 16+ (workflow использует node 20), npm install axios

const fs = require('fs');
const path = require('path');
const axios = require('axios');

const TOKEN = process.env.AIRTABLE_TOKEN;
const BASE  = process.env.AIRTABLE_BASE;

if (!TOKEN) throw new Error('AIRTABLE_TOKEN missing');
if (!BASE)  throw new Error('AIRTABLE_BASE missing');

const RATE_DELAY_MS = 220; // pause between Airtable requests to respect rate limits
const OUT_DIR = path.join(__dirname, '..', 'data');

async function delay(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function fetchAllRecords(tableName) {
  const url = `https://api.airtable.com/v0/${BASE}/${encodeURIComponent(tableName)}`;
  let all = [];
  let offset = undefined;

  while (true) {
    const params = {};
    if (offset) params.offset = offset;

    const res = await axios.get(url, {
      headers: { Authorization: `Bearer ${TOKEN}` },
      params
    });

    if (!res.data || !res.data.records) break;

    all = all.concat(res.data.records);

    if (!res.data.offset) break;
    offset = res.data.offset;

    // respect rate limit
    await delay(RATE_DELAY_MS);
  }

  return all;
}

function buildFeaturesGeoJSON(records) {
  const features = [];

  for (const r of records) {
    const f = r.fields || {};

    // normalize field names used in your Airtable schema
    const lonRaw = f.longitude ?? f.lng ?? f.lon ?? null;
    const latRaw = f.latitude  ?? f.lat ?? null;

    if (!latRaw || !lonRaw) continue;

    const lon = parseFloat(String(lonRaw).trim());
    const lat = parseFloat(String(latRaw).trim());
    if (Number.isNaN(lon) || Number.isNaN(lat)) continue;

    const props = {
      id: r.id,
      layer_id: f.layer_id ?? null,
      layer_type: f.layer_type ?? null,
      name_ru: f.name_ru ?? null,
      name_en: f.name_en ?? null,
      title_short: f.title_short ?? null,
      description: f.description ?? null,
      architect: f.architect ?? null,
      style_label: f.style_label ?? null,
      date_start: f.date_start ?? null,
      date_construction_end: f.date_construction_end ?? null,
      date_end: f.date_end ?? null,
      influence_radius_km: f.influence_radius_km ?? null,
      sequence_order: f.sequence_order ?? null,
      image_url: f.image_url ?? null,
      source_url: f.source_url ?? null,
      source_license: f.source_license ?? null,
      tags: f.tags ?? null,
      coordinates_confidence: f.coordinates_confidence ?? null,
      coordinates_source: f.coordinates_source ?? null,
      is_active: f.is_active ?? null
    };

    features.push({
      type: "Feature",
      geometry: { type: "Point", coordinates: [lon, lat] },
      properties: props
    });
  }

  return { type: "FeatureCollection", features };
}

function simplifyLayerRecord(rec) {
  const f = rec.fields || {};
  return {
    id: rec.id,
    layer_id: f.layer_id ?? null,
    name_ru: f.name_ru ?? null,
    name_en: f.name_en ?? null,
    color_hex: f.color_hex ?? null,
    icon: f.icon ?? null,
    is_enabled: f.is_enabled ?? null
  };
}

async function ensureOutDir() {
  if (!fs.existsSync(OUT_DIR)) fs.mkdirSync(OUT_DIR, { recursive: true });
}

async function run() {
  console.log('Start export: fetching Features...');
  const featuresRecords = await fetchAllRecords('Features');
  console.log(`Fetched Features: ${featuresRecords.length}`);

  console.log('Fetching Layers...');
  const layersRecords = await fetchAllRecords('Layers');
  console.log(`Fetched Layers: ${layersRecords.length}`);

  const featuresGeo = buildFeaturesGeoJSON(featuresRecords);
  const layersSimple = layersRecords.map(simplifyLayerRecord);

  await ensureOutDir();

  fs.writeFileSync(path.join(OUT_DIR, 'features.json'), JSON.stringify(featuresRecords, null, 2));
  fs.writeFileSync(path.join(OUT_DIR, 'features.geojson'), JSON.stringify(featuresGeo, null, 2));
  fs.writeFileSync(path.join(OUT_DIR, 'layers.json'), JSON.stringify(layersSimple, null, 2));

  console.log('Wrote files:');
  console.log(' - data/features.json');
  console.log(' - data/features.geojson');
  console.log(' - data/layers.json');
  console.log('Export complete');
}

run().catch(err => {
  console.error('Export failed:', err && err.message ? err.message : err);
  process.exit(1);
});

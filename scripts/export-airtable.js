const fs = require("fs");
const axios = require("axios");

const TOKEN = process.env.AIRTABLE_TOKEN;
const BASE = process.env.AIRTABLE_BASE;

async function fetchTable(table) {

  let records = [];
  let offset = null;

  while (true) {

    const url = `https://api.airtable.com/v0/${BASE}/${table}`;

    const res = await axios.get(url, {
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

function featuresToGeoJSON(records) {

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

      properties: f
    });
  }

  return {
    type: "FeatureCollection",
    features
  };
}

async function run() {

  const features = await fetchTable("Features");
  const layers = await fetchTable("Layers");

  const geojson = featuresToGeoJSON(features);

  if (!fs.existsSync("data")) fs.mkdirSync("data");

  fs.writeFileSync(
    "data/features.json",
    JSON.stringify(features, null, 2)
  );

  fs.writeFileSync(
    "data/features.geojson",
    JSON.stringify(geojson, null, 2)
  );

  fs.writeFileSync(
    "data/layers.json",
    JSON.stringify(layers, null, 2)
  );

  console.log("Export complete");
}

run();

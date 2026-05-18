// Jessica AI — Route Planner client.
// Decrypts the bundled price envelope, geocodes user input via a public US
// cities CSV + a hand-coded entry for Brampton, asks OSRM for an actual
// driving route, matches Pilot stations to the route polyline, runs the
// greedy gas-station optimizer, and renders the result on a Leaflet map.

// ---------- Crypto: PBKDF2-SHA-256 → AES-GCM (matches web_build.py) ----------

function b64ToBytes(b64) {
  const bin = atob(b64);
  const out = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) out[i] = bin.charCodeAt(i);
  return out;
}

async function deriveKey(passcode, salt, iterations) {
  const km = await crypto.subtle.importKey(
    "raw", new TextEncoder().encode(passcode), "PBKDF2", false, ["deriveKey"],
  );
  return crypto.subtle.deriveKey(
    { name: "PBKDF2", salt, iterations, hash: "SHA-256" },
    km,
    { name: "AES-GCM", length: 256 },
    false, ["decrypt"],
  );
}

async function decryptPayload(envelope, passcode) {
  const salt = b64ToBytes(envelope.salt);
  const iv   = b64ToBytes(envelope.iv);
  const ct   = b64ToBytes(envelope.ciphertext);
  const key  = await deriveKey(passcode, salt, envelope.iterations);
  const pt   = await crypto.subtle.decrypt({ name: "AES-GCM", iv }, key, ct);
  return JSON.parse(new TextDecoder().decode(pt));
}

// ---------- Geo ----------

const EARTH_MI = 3958.8;
const toRad = (d) => d * Math.PI / 180;

function haversineMi(a, b) {
  const dLat = toRad(b[0] - a[0]);
  const dLon = toRad(b[1] - a[1]);
  const h = Math.sin(dLat/2) ** 2 +
            Math.cos(toRad(a[0])) * Math.cos(toRad(b[0])) *
            Math.sin(dLon/2) ** 2;
  return 2 * EARTH_MI * Math.asin(Math.sqrt(h));
}

const HARDCODED_CITIES = {
  "BRAMPTON|ON":      [43.7315, -79.7624],
  "MISSISSAUGA|ON":   [43.5890, -79.6441],
  "TORONTO|ON":       [43.6532, -79.3832],
};

let CITY_DB = null;

async function loadCityDB() {
  if (CITY_DB) return CITY_DB;
  const r = await fetch("cities.csv");
  if (!r.ok) throw new Error(`cities.csv: ${r.status}`);
  const text = await r.text();
  const lines = text.split("\n");
  const db = {};
  for (let i = 1; i < lines.length; i++) {
    const line = lines[i];
    if (!line) continue;
    // Parse CSV with quoted fields. Columns: ID,STATE_CODE,STATE_NAME,CITY,COUNTY,LATITUDE,LONGITUDE
    const cols = parseCsvLine(line);
    if (cols.length < 7) continue;
    const st  = cols[1];
    const city = cols[3];
    const lat = parseFloat(cols[5]);
    const lon = parseFloat(cols[6]);
    if (!isFinite(lat) || !isFinite(lon)) continue;
    db[`${city.toUpperCase()}|${st}`] = [lat, lon];
  }
  CITY_DB = db;
  return db;
}

function parseCsvLine(line) {
  const out = [];
  let cur = "", inQ = false;
  for (let i = 0; i < line.length; i++) {
    const c = line[i];
    if (c === '"') { inQ = !inQ; continue; }
    if (c === "," && !inQ) { out.push(cur); cur = ""; continue; }
    cur += c;
  }
  out.push(cur);
  return out;
}

async function geocode(input) {
  const m = input.match(/^\s*(.+?)\s*,\s*([A-Za-z]{2})\s*$/);
  if (!m) return null;
  const city = m[1];
  const st = m[2].toUpperCase();
  const key = `${city.toUpperCase()}|${st}`;
  if (HARDCODED_CITIES[key]) return HARDCODED_CITIES[key];
  const db = await loadCityDB();
  if (db[key]) return db[key];
  // Try simple normalizations
  for (const cand of normalizeCity(city)) {
    const k = `${cand.toUpperCase()}|${st}`;
    if (db[k]) return db[k];
  }
  return null;
}

function normalizeCity(name) {
  const out = [name];
  out.push(name.replace(/^St\.?\s+/i, "Saint "));
  out.push(name.replace(/^Mt\.?\s+/i, "Mount "));
  out.push(name.replace(/^Ft\.?\s+/i, "Fort "));
  out.push(name.replace(/-/g, " "));
  out.push(name.replace(/\./g, ""));
  return [...new Set(out)];
}

// ---------- OSRM ----------

const OSRM_BASE = "https://router.project-osrm.org";

async function getDrivingRoute(origin, dest) {
  const url = `${OSRM_BASE}/route/v1/driving/` +
              `${origin[1]},${origin[0]};${dest[1]},${dest[0]}` +
              `?overview=full&geometries=geojson&steps=true`;
  const r = await fetch(url);
  if (!r.ok) throw new Error(`OSRM HTTP ${r.status}`);
  const data = await r.json();
  if (data.code !== "Ok") throw new Error(`OSRM: ${data.code}`);
  return data.routes[0];
}

function metersToMi(m) { return m / 1609.344; }

// ---------- Station-to-route matching ----------

function findStationsAlongRoute(route, stations, maxDetourMi = 20) {
  // OSRM coords are [lon, lat]; flip to [lat, lon] for haversine.
  const coords = route.geometry.coordinates;
  if (coords.length < 2) return [];

  // Cumulative mileage at each vertex.
  const cum = [0];
  for (let i = 1; i < coords.length; i++) {
    const a = [coords[i-1][1], coords[i-1][0]];
    const b = [coords[i][1],   coords[i][0]];
    cum.push(cum[i-1] + haversineMi(a, b));
  }

  const out = [];
  for (const s of stations) {
    const sc = [s.lat, s.lon];
    let minD = Infinity, minIdx = 0;
    for (let i = 0; i < coords.length; i++) {
      const d = haversineMi(sc, [coords[i][1], coords[i][0]]);
      if (d < minD) { minD = d; minIdx = i; }
    }
    if (minD <= maxDetourMi) {
      out.push({ ...s, miles: cum[minIdx], detour: minD });
    }
  }
  return out;
}

// ---------- Optimizer (port of src/fuel_optimizer/optimize.py) ----------

function optimize({ totalMi, stations, tankGal=200, mpg=6.5, startGal=null, reserveGal=20 }) {
  if (startGal == null) startGal = tankGal;
  const tankMi = tankGal * mpg;
  const reserveMi = reserveGal * mpg;

  const onRoute = stations
    .filter((s) => s.miles >= 0 && s.miles <= totalMi)
    .sort((a, b) => a.miles - b.miles);

  let fuelMi = startGal * mpg;
  let pos = 0;
  const stops = [];
  let totalCost = 0;

  for (let i = 0; i < onRoute.length; i++) {
    const st = onRoute[i];
    const leg = st.miles - pos;
    if (leg > fuelMi + 1e-6) {
      return { feasible: false,
               error: `Out of fuel between mile ${pos.toFixed(0)} and ${st.city}, ${st.st} ` +
                      `(mile ${st.miles.toFixed(0)}). Need ${leg.toFixed(0)} mi, have ${fuelMi.toFixed(0)}.` };
    }
    fuelMi -= leg;
    pos = st.miles;

    let cheaperAt = null;
    const maxReach = pos + tankMi;
    for (let j = i + 1; j < onRoute.length; j++) {
      if (onRoute[j].miles > maxReach) break;
      if (onRoute[j].price < st.price) { cheaperAt = onRoute[j].miles; break; }
    }

    const toDest = totalMi - pos;
    let targetAfter;
    if (cheaperAt != null)                          targetAfter = cheaperAt - pos;
    else if (toDest + reserveMi <= tankMi)          targetAfter = toDest + reserveMi;
    else                                            targetAfter = tankMi;

    const buyMi = Math.max(0, targetAfter - fuelMi);
    const gal = buyMi / mpg;
    if (gal > 0.01) {
      const cost = gal * st.price;
      stops.push({ station: st, gallons: gal, cost });
      totalCost += cost;
      fuelMi += buyMi;
    }
  }

  const finalLeg = totalMi - pos;
  if (finalLeg > fuelMi + 1e-6) {
    return { feasible: false,
             error: `Out of fuel before destination. Need ${finalLeg.toFixed(0)} mi, have ${fuelMi.toFixed(0)}.` };
  }
  return {
    feasible: true,
    stops,
    totalCost,
    totalGallons: stops.reduce((s, x) => s + x.gallons, 0),
    arrivalGal: (fuelMi - finalLeg) / mpg,
  };
}

// ---------- Render ----------

let MAP = null;
let ROUTE_LAYER = null;
let STATIONS_LAYER = null;
let STATIONS = [];          // all decrypted stations (full corpus)

function initMap() {
  MAP = L.map("map", { zoomControl: true }).setView([39.5, -98.5], 4);
  L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution: "© OpenStreetMap contributors",
    maxZoom: 19,
  }).addTo(MAP);
}

function priceColor(price, lo, hi) {
  if (hi <= lo) return "hsl(180, 70%, 50%)";
  const t = Math.max(0, Math.min(1, (price - lo) / (hi - lo)));
  // green (120°) at cheap → red (0°) at expensive
  const h = (1 - t) * 120;
  return `hsl(${h.toFixed(0)}, 80%, 45%)`;
}

function render(route, stations, plan, routeMi) {
  if (ROUTE_LAYER) MAP.removeLayer(ROUTE_LAYER);
  if (STATIONS_LAYER) MAP.removeLayer(STATIONS_LAYER);

  const latlngs = route.geometry.coordinates.map((c) => [c[1], c[0]]);
  ROUTE_LAYER = L.polyline(latlngs, {
    color: "#00e5ff", weight: 4, opacity: 0.75,
  }).addTo(MAP);
  MAP.fitBounds(ROUTE_LAYER.getBounds(), { padding: [40, 40] });

  const stopSites = new Set(plan.feasible ? plan.stops.map((s) => s.station.site) : []);
  const prices = stations.map((s) => s.price);
  const lo = Math.min(...prices), hi = Math.max(...prices);

  const markers = [];
  for (const s of stations) {
    const isStop = stopSites.has(s.site);
    const color = priceColor(s.price, lo, hi);
    const tip = `<b>#${s.site} ${s.city}, ${s.st}</b><br>` +
                `$${s.price.toFixed(3)} / gal<br>` +
                `Mile ${s.miles.toFixed(0)}` +
                (isStop ? `<br><b style="color:#fff">★ optimal stop</b>` : "");
    markers.push(L.circleMarker([s.lat, s.lon], {
      radius: isStop ? 9 : 5,
      color: isStop ? "#ffffff" : color,
      weight: isStop ? 3 : 1,
      fillColor: color,
      fillOpacity: 0.85,
    }).bindTooltip(tip, { sticky: true, direction: "top" }));
  }
  STATIONS_LAYER = L.layerGroup(markers).addTo(MAP);

  // ---- Sidebar ----
  const r = document.getElementById("results");
  let html = "";
  html += `<h3>Plan</h3>`;
  html += `<p>Distance: <b>${routeMi.toFixed(0)} mi</b> (OSRM driving)</p>`;
  html += `<p>Pilot stations on route: <b>${stations.length}</b>` +
          (stations.length ? ` ($${lo.toFixed(3)} – $${hi.toFixed(3)}/gal)` : "") + `</p>`;

  if (!plan.feasible) {
    html += `<p class="error">⚠ ${plan.error}</p>`;
  } else if (plan.stops.length === 0) {
    html += `<p class="muted">No fuel stops needed — destination within starting-tank range.</p>`;
    html += `<p class="muted">Arrival fuel: ~${plan.arrivalGal.toFixed(0)} gal.</p>`;
  } else {
    const baselineCost = plan.totalGallons * (prices.reduce((a, b) => a + b, 0) / prices.length);
    const savings = baselineCost - plan.totalCost;
    html += `<div class="summary">`;
    html += `  <div class="big">$${plan.totalCost.toFixed(2)}</div>`;
    html += `  <div class="muted">${plan.totalGallons.toFixed(1)} gal · arrival ~${plan.arrivalGal.toFixed(0)} gal</div>`;
    html += `  <div>vs. average-price baseline ($${baselineCost.toFixed(2)}):`;
    html += `    <span class="savings">save $${savings.toFixed(2)}</span></div>`;
    html += `</div>`;

    html += `<h4>Fueling stops</h4><ol class="stops">`;
    for (const s of plan.stops) {
      html += `<li>Mile ${s.station.miles.toFixed(0)} — ` +
              `<b>#${s.station.site} ${s.station.city}, ${s.station.st}</b><br>` +
              `${s.gallons.toFixed(1)} gal @ $${s.station.price.toFixed(3)} = ` +
              `<b>$${s.cost.toFixed(2)}</b></li>`;
    }
    html += `</ol>`;
  }

  // Legend
  html += `<div class="legend">`;
  html += `  <div><span class="legend-mark"></span> all on-route Pilot stations, colored by price:</div>`;
  html += `  <div class="legend-bar"></div>`;
  html += `  <div class="legend-labels"><span>$${lo.toFixed(3)} (cheap)</span><span>$${hi.toFixed(3)} (expensive)</span></div>`;
  html += `</div>`;

  // Turn-by-turn
  html += `<h4>Turn-by-turn</h4><ol class="dirs">`;
  for (const step of route.legs[0].steps) {
    const text = formatStep(step);
    const mi = metersToMi(step.distance).toFixed(1);
    html += `<li>${text} <span class="dist">${mi} mi</span></li>`;
  }
  html += `</ol>`;

  r.innerHTML = html;
}

function formatStep(step) {
  const m = step.maneuver, type = m.type, mod = m.modifier || "", name = step.name || "";
  const onto = name ? ` onto <b>${name}</b>` : "";
  switch (type) {
    case "depart":         return `Head ${mod || "out"}${onto}`;
    case "arrive":         return `Arrive at destination${name ? ` (${name})` : ""}`;
    case "turn":           return `Turn ${mod}${onto}`;
    case "merge":          return `Merge ${mod}${onto}`;
    case "on ramp":        return `Take the on-ramp${mod ? ` (${mod})` : ""}${onto}`;
    case "off ramp":       return `Take the off-ramp${mod ? ` (${mod})` : ""}${onto}`;
    case "fork":           return `Keep ${mod}${onto}`;
    case "end of road":    return `At the end of the road, ${mod ? "turn " + mod : "continue"}${onto}`;
    case "continue":       return `Continue${mod ? ` ${mod}` : ""}${onto}`;
    case "roundabout":     return `Take the roundabout${onto}`;
    case "rotary":         return `Take the rotary${onto}`;
    case "exit roundabout":
    case "exit rotary":    return `Exit the rotary${onto}`;
    default:               return `${type}${mod ? ` ${mod}` : ""}${onto}`;
  }
}

// ---------- Top-level flow ----------

async function unlock() {
  const pc = document.getElementById("passcode").value;
  const errEl = document.getElementById("unlock-error");
  errEl.textContent = "";
  try {
    const r = await fetch("data.enc.json");
    if (!r.ok) throw new Error(`data.enc.json HTTP ${r.status}`);
    const env = await r.json();
    const payload = await decryptPayload(env, pc);
    STATIONS = payload.stations;
    document.getElementById("snapshot").textContent = payload.snapshot;
    document.getElementById("locked").hidden = true;
    document.getElementById("unlocked").hidden = false;
    initMap();
  } catch (e) {
    console.error(e);
    errEl.textContent = "Incorrect passcode (or data file unreadable).";
  }
}

async function planRoute() {
  const status = (msg) => (document.getElementById("status").textContent = msg);
  const planBtn = document.getElementById("plan-btn");

  const origin = document.getElementById("origin").value;
  const dest   = document.getElementById("dest").value;
  const tank   = parseFloat(document.getElementById("tank").value) || 200;
  const mpg    = parseFloat(document.getElementById("mpg").value) || 6.5;
  const sv     = document.getElementById("start").value.trim();
  const startGal = sv === "" || sv.toLowerCase() === "full" ? null : parseFloat(sv);

  planBtn.disabled = true;
  try {
    status("Geocoding…");
    const o = await geocode(origin);
    const d = await geocode(dest);
    if (!o || !d) {
      status(`Couldn't find ${!o ? origin : dest}. Format: 'City, ST'.`);
      return;
    }

    status("Asking OSRM for a driving route…");
    const route = await getDrivingRoute(o, d);
    const routeMi = metersToMi(route.distance);

    status(`Found route (${routeMi.toFixed(0)} mi). Matching stations…`);
    const onRoute = findStationsAlongRoute(route, STATIONS, 20);

    status(`${onRoute.length} on-route Pilot stations. Optimizing fueling…`);
    const plan = optimize({
      totalMi: routeMi, stations: onRoute,
      tankGal: tank, mpg, startGal, reserveGal: 20,
    });

    render(route, onRoute, plan, routeMi);
    status(plan.feasible
      ? `Plan ready. ${plan.stops.length} stop${plan.stops.length === 1 ? "" : "s"}.`
      : "Plan infeasible — see sidebar.");
  } catch (e) {
    console.error(e);
    status(`Error: ${e.message}`);
  } finally {
    planBtn.disabled = false;
  }
}

// ---------- Wire up ----------

window.addEventListener("DOMContentLoaded", () => {
  document.getElementById("unlock-btn").addEventListener("click", unlock);
  document.getElementById("passcode").addEventListener("keypress", (e) => {
    if (e.key === "Enter") unlock();
  });
  document.getElementById("plan-btn").addEventListener("click", planRoute);
});

/**
 * arcgis.js — thin REST clients for ArcGIS Online (AGOL) and ArcGIS Enterprise.
 * Both environments expose the same three operations: getToken, search, query.
 */
const fetch = require("node-fetch");

// --- simple in-memory token cache, keyed by environment ---
const tokenCache = { agol: null, enterprise: null };

function isExpired(cacheEntry) {
  return !cacheEntry || Date.now() >= cacheEntry.expiresAt - 30_000; // refresh 30s early
}

async function getAgolToken(env = process.env) {
  if (!isExpired(tokenCache.agol)) return tokenCache.agol.token;

  const url = "https://www.arcgis.com/sharing/rest/oauth2/token";
  const body = new URLSearchParams({
    client_id: env.AGOL_CLIENT_ID,
    client_secret: env.AGOL_CLIENT_SECRET,
    grant_type: "client_credentials",
    f: "json",
  });

  const res = await fetch(url, { method: "POST", body });
  const data = await res.json();
  if (!data.access_token) throw new Error(`AGOL auth failed: ${JSON.stringify(data)}`);

  tokenCache.agol = {
    token: data.access_token,
    expiresAt: Date.now() + (data.expires_in || 1800) * 1000,
  };
  return tokenCache.agol.token;
}

async function getEnterpriseToken(env = process.env) {
  if (!isExpired(tokenCache.enterprise)) return tokenCache.enterprise.token;

  const url = `${env.ENTERPRISE_PORTAL_URL}/sharing/rest/generateToken`;
  const body = new URLSearchParams({
    username: env.ENTERPRISE_USERNAME,
    password: env.ENTERPRISE_PASSWORD,
    referer: env.ENTERPRISE_PORTAL_URL,
    f: "json",
  });

  const res = await fetch(url, { method: "POST", body });
  const data = await res.json();
  if (!data.token) throw new Error(`Enterprise auth failed: ${JSON.stringify(data)}`);

  tokenCache.enterprise = {
    token: data.token,
    expiresAt: data.expires || Date.now() + 60 * 60 * 1000,
  };
  return tokenCache.enterprise.token;
}

/** Search a portal (AGOL org or Enterprise portal) for an item by title/keyword. */
async function searchPortal(environment, query, env = process.env) {
  const isAgol = environment === "agol";
  const token = isAgol ? await getAgolToken(env) : await getEnterpriseToken(env);
  const base = isAgol ? "https://www.arcgis.com" : `${env.ENTERPRISE_PORTAL_URL}`;

  const url = `${base}/sharing/rest/search?f=json&token=${token}&q=${encodeURIComponent(
    `title:"${query}"`
  )}`;
  const res = await fetch(url);
  const data = await res.json();
  if (data.error) throw new Error(`Portal search failed: ${JSON.stringify(data.error)}`);
  return data.results || [];
}

/** Query features from a Feature/Map service layer. */
async function queryLayer(environment, serviceUrl, { where = "1=1", outFields = ["*"], resultRecordCount = 1000 } = {}, env = process.env) {
  const isAgol = environment === "agol";
  const token = isAgol ? await getAgolToken(env) : await getEnterpriseToken(env);

  const url = `${serviceUrl}/query?f=geojson&token=${token}&where=${encodeURIComponent(
    where
  )}&outFields=${encodeURIComponent(outFields.join(","))}&resultRecordCount=${resultRecordCount}`;

  const res = await fetch(url);
  const data = await res.json();
  if (data.error) throw new Error(`Feature query failed: ${JSON.stringify(data.error)}`);
  return data; // GeoJSON FeatureCollection
}

module.exports = { getAgolToken, getEnterpriseToken, searchPortal, queryLayer };

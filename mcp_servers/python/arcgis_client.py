"""
arcgis_client.py — thin REST clients for ArcGIS Online (AGOL) and ArcGIS Enterprise.

Both environments expose the same three operations: get_token, search_portal, query_layer.
"""
import os
import time
import requests

_token_cache = {"agol": None, "enterprise": None}  # {"token": str, "expires_at": epoch_seconds}


def _is_expired(entry):
    return not entry or time.time() >= entry["expires_at"] - 30  # refresh 30s early


def get_agol_token():
    if not _is_expired(_token_cache["agol"]):
        return _token_cache["agol"]["token"]

    url = "https://www.arcgis.com/sharing/rest/oauth2/token"
    resp = requests.post(
        url,
        data={
            "client_id": os.environ["AGOL_CLIENT_ID"],
            "client_secret": os.environ["AGOL_CLIENT_SECRET"],
            "grant_type": "client_credentials",
            "f": "json",
        },
        timeout=15,
    )
    data = resp.json()
    if "access_token" not in data:
        raise RuntimeError(f"AGOL auth failed: {data}")

    _token_cache["agol"] = {
        "token": data["access_token"],
        "expires_at": time.time() + data.get("expires_in", 1800),
    }
    return _token_cache["agol"]["token"]


def get_enterprise_token():
    if not _is_expired(_token_cache["enterprise"]):
        return _token_cache["enterprise"]["token"]

    portal_url = os.environ["ENTERPRISE_PORTAL_URL"]
    resp = requests.post(
        f"{portal_url}/sharing/rest/generateToken",
        data={
            "username": os.environ["ENTERPRISE_USERNAME"],
            "password": os.environ["ENTERPRISE_PASSWORD"],
            "referer": portal_url,
            "f": "json",
        },
        timeout=15,
    )
    data = resp.json()
    if "token" not in data:
        raise RuntimeError(f"Enterprise auth failed: {data}")

    expires = data.get("expires")
    _token_cache["enterprise"] = {
        "token": data["token"],
        "expires_at": (expires / 1000) if expires else time.time() + 3600,
    }
    return _token_cache["enterprise"]["token"]


def search_portal(environment: str, query: str):
    """Search a portal (AGOL org or Enterprise portal) for an item by title/keyword."""
    is_agol = environment == "agol"
    token = get_agol_token() if is_agol else get_enterprise_token()
    base = "https://www.arcgis.com" if is_agol else os.environ["ENTERPRISE_PORTAL_URL"]

    resp = requests.get(
        f"{base}/sharing/rest/search",
        params={"f": "json", "token": token, "q": f'title:"{query}"'},
        timeout=15,
    )
    data = resp.json()
    if "error" in data:
        raise RuntimeError(f"Portal search failed: {data['error']}")
    return data.get("results", [])


def query_layer(environment: str, service_url: str, where="1=1", out_fields=None, result_record_count=1000):
    """Query features from a Feature/Map service layer. Returns a GeoJSON FeatureCollection."""
    out_fields = out_fields or ["*"]
    is_agol = environment == "agol"
    token = get_agol_token() if is_agol else get_enterprise_token()

    resp = requests.get(
        f"{service_url}/query",
        params={
            "f": "geojson",
            "token": token,
            "where": where,
            "outFields": ",".join(out_fields),
            "resultRecordCount": result_record_count,
        },
        timeout=30,
    )
    data = resp.json()
    if isinstance(data, dict) and "error" in data:
        raise RuntimeError(f"Feature query failed: {data['error']}")
    return data

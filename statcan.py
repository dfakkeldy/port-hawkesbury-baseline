"""Small client for Statistics Canada's Web Data Service (WDS).

Only the standard library and pandas are used. Every row that comes back keeps
its table number, coordinate and vector number, so each figure can be traced
to its source table.

API guide: https://www.statcan.gc.ca/en/developers/wds/user-guide
"""

from __future__ import annotations

import json
import urllib.request
from datetime import datetime
from zoneinfo import ZoneInfo

import pandas as pd

WDS = "https://www150.statcan.gc.ca/t1/wds/rest"
CHUNK = 30  # series per request


def _post(method: str, payload: list[dict]) -> list[dict]:
    request = urllib.request.Request(
        f"{WDS}/{method}",
        data=json.dumps(payload).encode(),
        # The service refuses Python's default User-Agent with HTTP 403.
        headers={"Content-Type": "application/json", "User-Agent": "baseline-notebook/0.1"},
    )
    with urllib.request.urlopen(request, timeout=180) as response:
        return json.load(response)


def cube_metadata(product_id: int) -> dict:
    """Return the metadata of one table (its dimensions, members and notes)."""
    reply = _post("getCubeMetadata", [{"productId": product_id}])[0]
    if reply["status"] != "SUCCESS":
        raise RuntimeError(f"metadata for {product_id}: {reply}")
    return reply["object"]


def geography_members(metadata: dict) -> pd.DataFrame:
    """List the members of the Geography dimension, with their standard codes.

    `code` is the Standard Geographical Classification code: seven digits for
    a census subdivision (a municipality), four for a census division (a county).
    """
    geography = next(
        d for d in metadata["dimension"] if d["dimensionNameEn"] == "Geography"
    )
    return pd.DataFrame(
        {
            "member_id": m["memberId"],
            "code": m.get("classificationCode"),
            "statcan_name": m["memberNameEn"],
        }
        for m in geography["member"]
    )


def coordinate(*member_ids: int) -> str:
    """Build a WDS coordinate: one member per dimension, padded to ten places."""
    parts = [str(i) for i in member_ids] + ["0"] * (10 - len(member_ids))
    return ".".join(parts)


def fetch(product_id: int, coordinates: list[str], latest_n: int) -> pd.DataFrame:
    """Fetch the latest `latest_n` periods for each coordinate of one table."""
    fetched_at = datetime.now(ZoneInfo("America/Halifax")).isoformat(timespec="seconds")
    rows = []
    for start in range(0, len(coordinates), CHUNK):
        payload = [
            {"productId": product_id, "coordinate": c, "latestN": latest_n}
            for c in coordinates[start : start + CHUNK]
        ]
        for reply in _post("getDataFromCubePidCoordAndLatestNPeriods", payload):
            if reply["status"] != "SUCCESS":
                raise RuntimeError(f"table {product_id}: {reply}")
            series = reply["object"]
            for point in series["vectorDataPoint"]:
                rows.append(
                    {
                        "table": product_id,
                        "coordinate": series["coordinate"],
                        "vector": f"v{series['vectorId']}",
                        # refPerRaw is the true reference date (for example 1 July)
                        "ref_date": point["refPerRaw"],
                        "value": point["value"],
                        "status_code": point["statusCode"],
                        "symbol_code": point["symbolCode"],
                        "released": point["releaseTime"],
                        "fetched_at": fetched_at,
                    }
                )
    return pd.DataFrame(rows)

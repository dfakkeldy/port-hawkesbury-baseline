"""Compare the towns in towns.csv on the 2021 Census Profile.

Run: python3 census_profile.py            (uses the cache)
     python3 census_profile.py --refresh  (fetches again from Statistics Canada)

Writes data/census_profile_2021.csv (the values as published) and
town-profile.csv (shares and a distance from Port Hawkesbury).

Source: Statistics Canada, Census Profile, 2021 Census of Population, through
the Census Profile web data service (dataflow STC_CP:DF_CSD). The labour and
industry rows come from the long-form sample (25% of households) and are
randomly rounded to 0 or 5, so shares for the smallest places are rough.
"""
import io
import sys
import time
import urllib.request
from pathlib import Path

import pandas as pd

HERE = Path(__file__).parent
CACHE = HERE / "data" / "census_profile_2021.csv"
API = "https://api.statcan.gc.ca/census-recensement/profile/sdmx/rest/data/STC_CP,DF_CSD/"

# Characteristic number in the 2021 Census Profile -> short name.
CHARACTERISTICS = {
    1: "population_2021",
    40: "median_age",
    113: "median_income_recipients_2020",
    229: "median_income_household_2020",
    2228: "participation_rate",
    2229: "employment_rate",
    2230: "unemployment_rate",
    2261: "labour_force_all_industries",
    2262: "agriculture_forestry_fishing",
    2263: "mining_oil_gas",
    2264: "utilities",
    2265: "construction",
    2266: "manufacturing",
    2267: "wholesale",
    2268: "retail",
    2269: "transport_warehousing",
    2270: "information_culture",
    2271: "finance_insurance",
    2272: "real_estate",
    2273: "professional_services",
    2274: "management_of_companies",
    2275: "administrative_support",
    2276: "education",
    2277: "health_social",
    2278: "arts_recreation",
    2279: "accommodation_food",
    2280: "other_services",
    2281: "public_administration",
    2599: "commute_within_csd",
    2600: "commute_other_csd_same_county",
    2601: "commute_other_county",
    2602: "commute_other_province",
}
INDUSTRIES = [name for number, name in CHARACTERISTICS.items() if 2262 <= number <= 2281]
COMMUTES = [name for number, name in CHARACTERISTICS.items() if 2599 <= number <= 2602]
CASE = 1215002  # Port Hawkesbury


def fetch(csduid: int) -> pd.DataFrame:
    """Total-gender counts or rates for one census subdivision."""
    key = f"A5.2021A0005{csduid}.1.{'+'.join(map(str, CHARACTERISTICS))}.1"
    request = urllib.request.Request(
        API + key, headers={"Accept": "text/csv", "User-Agent": "python-research-client/1.0"})
    with urllib.request.urlopen(request, timeout=120) as response:
        data = pd.read_csv(io.BytesIO(response.read()))
    data = data[["ALT_GEO_CODE", "CHARACTERISTIC", "OBS_VALUE", "FLAG", "RELEASE_DATE"]]
    data.columns = ["csduid", "characteristic", "value", "flag", "release_date"]
    data["name"] = data["characteristic"].map(CHARACTERISTICS)
    missing = set(CHARACTERISTICS) - set(data["characteristic"])
    assert not missing, f"{csduid}: characteristics not returned: {sorted(missing)}"
    return data.sort_values("characteristic")


def load(towns: pd.DataFrame, refresh: bool) -> pd.DataFrame:
    if CACHE.exists() and not refresh:
        return pd.read_csv(CACHE)
    parts = []
    for csduid in towns["csduid"]:
        parts.append(fetch(csduid))
        time.sleep(0.3)
    data = pd.concat(parts, ignore_index=True)
    data["fetched_at"] = pd.Timestamp.now(tz="UTC").isoformat(timespec="seconds")
    data.to_csv(CACHE, index=False)
    return data


def main() -> None:
    towns = pd.read_csv(HERE / "towns.csv")
    data = load(towns, refresh="--refresh" in sys.argv)
    assert set(data["csduid"]) == set(towns["csduid"]), "a town is missing from the census cache"
    wide = data.pivot(index="csduid", columns="name", values="value")

    shares = wide[INDUSTRIES].div(wide["labour_force_all_industries"], axis=0) * 100
    # Distance from Port Hawkesbury: half the sum of absolute differences in
    # industry shares. 0 = the same mix. The published counts are rounded one
    # by one, so a place's shares need not sum to 100 and the top is about 100.
    distance = shares.sub(shares.loc[CASE], axis=1).abs().sum(axis=1) / 2
    commuters = wide[COMMUTES].sum(axis=1)  # employed residents with a usual place of work

    out = towns[["csduid", "name", "prov", "role"]].set_index("csduid")
    out["population_2021"] = wide["population_2021"]
    out["median_age"] = wide["median_age"]
    out["median_income_household_2020"] = wide["median_income_household_2020"]
    out["employment_rate"] = wide["employment_rate"]
    out["unemployment_rate"] = wide["unemployment_rate"]
    for name in ("manufacturing", "education", "health_social", "retail",
                 "accommodation_food", "public_administration", "agriculture_forestry_fishing"):
        out[f"pct_{name}"] = shares[name].round(1)
    out["pct_commute_out_of_csd"] = ((1 - wide["commute_within_csd"] / commuters) * 100).round(1)
    out["industry_distance_from_port_hawkesbury"] = distance.round(1)
    out = out.sort_values("industry_distance_from_port_hawkesbury")
    out.to_csv(HERE / "town-profile.csv")
    print(out.drop(columns=["prov"]).to_string())


if __name__ == "__main__":
    main()

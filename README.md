# Port Hawkesbury before the data centre: a baseline

Started 18 November 2026 by Dan Fakkeldy.

On 16 October 2026 EverWind announced a data centre campus at Point Tupper, Nova Scotia ([company release](https://everwindfuels.com/2026/10/everwind-announces-10-billion-investment-in-point-tupper-data-centre-campus-and-renewable-energy-portfolio-across-nova-scotia/)). The site is in Richmond County. The nearest town, Port Hawkesbury, is across the county line in Inverness County and had 3,210 people in the 2021 Census.

**Status: a prototype, not a study.** Nothing here is a finding. Prepared with Claude (Anthropic). News reports name Anthropic as the tenant of the campus's first phase, so read this with that in mind.

The question for the long-term study: what does an AI data centre do to the economy of the rural town beside it? This first part is the "before" record and the comparison design. The effect itself cannot be measured for years.

## What is in this folder

| File | What it is |
|---|---|
| `baseline.ipynb` | The notebook, with its outputs. Two series, two charts. |
| `baseline.py` | The same notebook as plain Python (jupytext "percent" format). Edit this one. |
| `statcan.py` | A small client for Statistics Canada's Web Data Service. Standard library and pandas only. |
| `towns.csv` | The case, its neighbours and 38 candidate comparison towns, with one line for and one line against each. |
| `census_profile.py` | Fetches 32 rows of the 2021 Census Profile for each place and writes `town-profile.csv`. Run `python3 census_profile.py`; add `--refresh` to fetch again (about 30 minutes; the service is slow). |
| `town-profile.csv` | Each place beside Port Hawkesbury: size, age, income, labour rates, industry shares, commuting, and a distance in industry mix. |
| `data/` | The cached series (about 0.5 MB). Each row has its table, coordinate, vector number, release time and fetch time. |
| `fig-*.png` | The two charts. |

Run it again:

```sh
python3 -m pip install -r requirements.txt
python3 -m jupytext --to ipynb --execute baseline.py
```

Set `REFRESH = True` in the first code cell to fetch new data. With `False` it reads `data/`.

## 1. Inventory: which "before" series exist

Checked on 18 November 2026 against Statistics Canada's table list and metadata, the Nova Scotia open-data catalogue and the PVSC DataZone catalogue. "Town" means the census subdivision (CSD): Port Hawkesbury is 1215002, and the rural area that holds Point Tupper is Richmond, Subd. A, 1216006.

| Series | Source | Smallest area | How often | Years | Use for a town-level effect |
|---|---|---|---|---|---|
| Census counts and profile (population, income, labour, industry, housing) | Census of Population | Town | Every 5 years | to 2021; **2026 Census taken in May 2026**, first release 10 Feb 2027 | The best "before" picture, five months before the announcement. Too infrequent to time an effect. Median household income comes from all households (tax data); average income, labour and industry come from a 25% sample, so a town of 3,400 has wide error on those. |
| Commuting flows, home to work | Census table 98-10-0459-01 | Town to town | Every 5 years | 2021 | Shows where people with a usual workplace anywhere in Richmond, Subd. A lived in 2021. It cannot identify future campus workers or where they will live. |
| Population estimates, 1 July | Table 17-10-0155-01 | Town | Yearly | 2001 to 2025 | **In the notebook.** Estimates, not counts; revised after each census. Slow-moving. |
| Births, deaths, migration | Table 17-10-0153-01 | County | Yearly | 2001 to 2024 | County only. Useful to say *why* population changed. |
| Employment Insurance beneficiaries | Table 14-10-0323-01 | County | Monthly | 2000 to Sept 2026 | **In the notebook.** This table stops at the county, and it follows programme rules as well as jobs. The Community Data Program lists a monthly EI file by census subdivision, January 2000 to August 2026 (catalogue page read 19 Nov 2026; released 22 Oct 2026). The program is for member organizations (public, non-profit and community bodies) that pay a fee. The page warns that coverage is poor for some rural and small places, because beneficiaries are placed by postal code, and a postal code that crosses a boundary goes to the place with the most people. Whether Port Hawkesbury's counts are usable is not checked; a member (a municipality or a university library, perhaps) would have to open the file. |
| Employment and unemployment, small labour areas | Table 14-10-0480-01 (model-based estimates) | Self-contained labour area. The area "Antigonish, Subd. A" (code 12003) is reported to hold both Port Hawkesbury and Richmond, Subd. A; **check the crosswalk** | Monthly | Nov 2021 to Aug 2026 | One regional outcome that covers both sides of the county line. Short history; estimates from a model; cannot separate the town. |
| Labour force (employment, unemployment) | Tables 14-10-0462-01 and 14-10-0464-01 | Economic region (all of Cape Breton Island) | Monthly (3-month average), yearly | 2011 on | **Too coarse.** The region is mostly the Sydney area. |
| Job vacancies | Table 14-10-0441-01 | Economic region | Quarterly | 2015 on | **Too coarse.** |
| Tax-filer income (T1 Family File) | Tables 11-10-0004-01 to 11-10-0008-01 and others | Halifax, Cape Breton, Truro, New Glasgow, Kentville, and "rest of Nova Scotia" | Yearly | 2000 to 2023 | **Not public for the town** in these tables. A paid custom table by town or postal area may be possible; to confirm with Statistics Canada. |
| Income-tax returns by municipality | Canada Revenue Agency, T1 Final Statistics, table 4 for Nova Scotia (by census subdivision) | Town | Yearly | 2021 and 2023 tax years seen by the review; other years not yet checked | **Possible, and free.** Returns filed, and totals by income type (for example employment income) for residents. A reviewer of this folder reports a Port Hawkesbury row (2,640 returns for 2021). **The file is not yet opened here (the site timed out on 18 and 19 November 2026); confirm before use.** These are totals for individuals, not household medians, and they do not measure spending in the town. |
| Building permits | Table 34-10-0292-01 | Nova Scotia and Halifax only | Monthly | 2018 on | **Not public for the town** in this table. |
| Residential building permits, rural housing profile | Table 46-10-0087-01 (inactive) | Town; both Port Hawkesbury and Richmond, Subd. A are in it | Yearly | 2018 to 2023 | Short and ended. A "before" snapshot only. |
| Building permits, permit by permit | PVSC DataZone, "Building permit data for Statistics Canada Building Permit Survey", sections A to D | Municipality | Updated monthly | not yet checked | Possible. Coverage of Port Hawkesbury and Richmond, the years and the licence are **not yet checked**. |
| Business counts | Canadian Business Counts, census subdivisions (for example table 33-10-1176-01, June 2026) | Town (with 10 or more businesses) | Twice a year, one table each | June 2020 to June 2026 | A snapshot by industry and size. **Statistics Canada advises users not to use these as a time series.** |
| Municipal revenue and spending | Nova Scotia open data, "Municipal Fiscal Statistics" (`shcq-4v93`) | Municipality | Yearly | 2016-17 to 2023-24 | Good for the county-line question: it separates residential and commercial property tax for the Town and for Richmond County. About two years late. |
| Uniform assessment (the property tax base) | Nova Scotia open data (`kuu2-92bp`) | Municipality | Yearly | 2006-07 to 2026-27 | Good and long. Changes slowly; follows assessment rules and the cap. |
| Property tax rates | Nova Scotia open data (`ure8-3w7m`) | Municipality | Yearly | not yet checked | Supports the two rows above. |
| Assessed values and sale prices | PVSC DataZone (`bt58-qu28`, `6a95-ppg4`) | Property | Yearly values; sales as they happen | not yet checked | House prices by town are possible. A small town has few sales a year, so prices are noisy. Licence to confirm (this is the open DataZone, not Property Online). |
| School enrolment | Nova Scotia open data (`cjnf-ywvt`) | School | Yearly | 2006-07 on | A count of pupils, by school. Brothers and sisters are one family, and catchment areas do not follow municipal lines. |
| Traffic counts | Nova Scotia open data (`8524-ec3n`) | Highway section | Irregular | not yet checked | A possible activity measure at the causeway. |

Not found in public at town level: yearly employment, wages or payroll by place of work; GDP; retail sales. The census gives employment, industry and income for residents every five years. It does not give GDP or retail sales.

## 2. The first numbers (from the notebook)

- Port Hawkesbury's estimated population: 3,796 (2001), 3,303 (2021), 3,442 (2025, preliminary).
- From 2001 to 2021 its yearly change had a mean of -24.7 people and a standard deviation of 43.5.
- Richmond, Subd. A rose from 3,848 (2021) to 4,305 (2025). Port Hawkesbury rose by 139 in the same years. Both rises are **before** the announcement, and the values are not final. Most candidate towns rose in these years too.
- Port Hawkesbury is 18.9% of Inverness County's population. Richmond, Subd. A is 42.9% of Richmond County's.

The promised permanent jobs are 215, across the campus and four wind farms together (a company figure, from the release of 16 October 2026). The company's forecast does not say how many more people will live in the Town, or when. So the standard deviation above cannot tell us whether an effect will show in this series. That will depend on how closely a comparison follows the town before the project. This is the main design problem.

## 3. Candidate comparison towns

`towns.csv` has 38 candidates in Nova Scotia, New Brunswick, Newfoundland and Labrador and Prince Edward Island. **The "why" and "against" notes are first-draft and from general knowledge. They are not checked against sources.** Closure years and merger dates need a check before any town is used.

Three things came out of drafting it:

- **Two of the towns first suggested are not separate units in the data.** Liverpool has been part of the Region of Queens since 1996, and Sheet Harbour is part of Halifax. Queens can stand in for Liverpool. Sheet Harbour would need census dissemination areas, which have no yearly series.
- **The neighbours cannot be controls.** Mulgrave, Inverness, Subd. C, and perhaps Antigonish and Guysborough are inside the commuting area. If the project has an effect, they may receive some of it. They are tracked as a separate group of possible spillover areas.
- **Some candidates share the host-town split.** Pictou (the mill stood in the county, not the town), Clarenville and Arnold's Cove (the refinery is in Come By Chance) and Belledune (port and smelter, few residents). These are towns where the plant and the households are in different municipalities.

### Census check of the candidates (added 19 November 2026)

The notes in `towns.csv` are from memory. `census_profile.py` now gives a measured comparison from the 2021 Census Profile. The industry and labour rows come from the long-form sample (25% of households) and are randomly rounded to 0 or 5, so the shares for places under about 1,000 people are rough. The census week was in May 2021, during the pandemic.

"Distance" is half the sum of the absolute differences in industry shares between a place and Port Hawkesbury. 0 means the same mix. A larger number means a more different mix; the top of the scale is about 100. It is not exactly 100, because each published count is rounded on its own and a place's shares need not add up to 100% (they add up to 87.5% for Come By Chance).

| Place | People, 2021 | Manufacturing | Education | Retail | Median age | Distance |
|---|---|---|---|---|---|---|
| **Port Hawkesbury** | 3,210 | 8.8% | 9.4% | 20.2% | 46.8 | 0 |
| Clarenville, NL | 6,704 | 5.7% | 7.4% | 19.1% | 45.2 | 14.6 |
| Stellarton, NS | 4,007 | 9.4% | 8.8% | 19.2% | 47.2 | 14.6 |
| Sussex, NB | 4,440 | 9.2% | 9.7% | 13.4% | 48.0 | 15.1 |
| Yarmouth, NS | 6,829 | 6.6% | 6.9% | 19.4% | 48.8 | 15.2 |
| New Glasgow, NS | 9,471 | 6.6% | 7.7% | 21.3% | 47.6 | 15.6 |
| St. Stephen, NB | 4,510 | 14.9% | 8.2% | 14.2% | 48.0 | 15.7 |
| Antigonish, NS (a neighbour, not a candidate) | 4,656 | 2.4% | 20.4% | 15.2% | 42.0 | 24.4 |

What this shows:

- **By where its residents work, Port Hawkesbury is a service town.** Retail is the largest sector (20.2%), then accommodation and food (11.8%). Manufacturing is 8.8%. The census counts residents by the industry of their job, wherever the job is.
- **The closest places by industry mix are other regional service towns**, not the small single-plant towns. Souris, Arnold's Cove, Borden-Carleton, Lockeport, Clark's Harbour and Come By Chance are the furthest. Come By Chance has 208 people; with random rounding to 0 or 5, its shares carry little information. A minimum size for a comparison town is a design choice still to make.
- **Antigonish is unlike Port Hawkesbury.** Education is 20.4% of its labour force against 9.4%, and its median age is 42.0 against 46.8. It was listed as a neighbour, not as a candidate. Agriculture, forestry and fishing is 3.5% of the labour force in the Town of Antigonish. The rural parts of Antigonish County are separate census subdivisions and are not in this table.
- **Commuting.** Of Port Hawkesbury's employed residents with a usual place of work, 370 of 1,025 (36.1%) worked outside the town, and 310 worked in another county. The table does not say which county.

A similar industry mix in 2021 does not make a place a good control. It is one screen. The series must also move together before the event.

**First screen (19 November 2026).** Antigonish is not a comparison: it is a university town with a farming county around it. The mill towns whose mill has closed are a second concern. In `towns.csv` these are Pictou, Queens (Liverpool), Dalhousie, Bathurst, Miramichi, Stephenville, Grand Falls-Windsor and Botwood; Belledune (smelter) and Sussex (mine) had closures of another kind. A closure does not rule a town out by itself. Abadie (2021, p. 409) advises leaving out a comparison unit when a shock of its own affected the outcome under study and would not have reached the treated town without the intervention. So each closure is a case to check against those two conditions, with its year. The closure years in `towns.csv` are still unchecked.

## 4. Design notes to test, not conclusions

**Synthetic control.** The method builds a comparison from a weighted blend of other towns, fitted on the years before the event (Abadie and Gardeazabal 2003; Abadie, Diamond and Hainmueller 2010). Abadie (2021, section 5) lists six requirements of the setting: an effect that is large beside the outcome's volatility; a comparison group free of similar interventions and of large shocks of its own; no anticipation; no interference (no spillover to comparison units); the treated unit inside the range the others can reproduce (the convex hull condition); and a time horizon long enough for the effect to appear. Section 6 adds data requirements, including enough periods before and after. (Checked against the paper's text on 18 November 2026.)

Measured against that list, this case is hard:

- The treated unit is one small town, and the public outcomes are few, slow or noisy.
- Many candidate towns had their own shocks.
- The same site has had hydrogen announcements since 2022. That is a possible separate shock, and a possible source of anticipation. No evidence yet connects it to this campus.
- A placebo test runs the method on every town in turn and ranks the results. With all 38 candidates kept, the best possible rank for Port Hawkesbury is 1 of 39 (2.6%). Dropping badly fitted towns changes that number. The rank describes how unusual the town is among the candidates. It is not the probability that the project had no effect: Abadie separates this comparison from inference under random assignment.

**Projects that were announced and not built.** Bahar and Wright (Brookings, May 2026, revised August 2026) study about 1,500 United States data centres and use counties whose announced projects were cancelled as the comparison. They report that data-centre counties were already growing faster, so a simple comparison overstates the job effect. Greenstone, Hornbeck and Moretti (2010) used a related design: the runner-up counties for the same plant, to study the productivity of plants already there. Is there a runner-up site for this campus? If one exists, it may be a better comparison than any mill town. (Read at summary and abstract level only; their estimates are not checked.)

**The county line.** This is a description of channels more than a control. The site lies in Richmond County. The study would test whether municipal revenue, household location or spending change on either side of the county line; none of these is measured yet. Municipal Fiscal Statistics and Uniform Assessment give totals by municipality each year, but they cannot isolate the tax paid by one project. The household side needs income by town (see the two income rows above).

**Guarding against a wanted result.** The author lives in the area and is in favour of the project. The usual guard is a dated, public pre-analysis plan: fix the outcomes, the comparison towns, the event date and the test before any "after" data exist; name the smallest change that would matter, and say in advance what result would count as "no effect" and what would count as "cannot tell"; report every outcome named in the plan; and list what was already looked at before the plan was dated. A weak or imprecise result can still leave real gains or losses possible. The notebook only ranks towns by how closely their population path follows Port Hawkesbury. It does not yet fit or fix any weights.

**For a later household survey (out of scope here).** The fiscal tables show which municipality receives the revenue, and the commuting table shows where people who worked in Richmond, Subd. A lived in 2021. Both would help to frame a survey sample. Neither shows which households a campus effect will reach.

## 5. Decided and open

Decided (19 November 2026):

- **Outcomes.** Population, income, Employment Insurance and municipal revenue.
- **The county line** is the main subject: the tax base is in Richmond County, and the nearest town's households are in Inverness County.

Open:

1. **Comparison towns.** Other regional service towns, towns with the plant-and-household split, a runner-up site, or the Strait's own past projects? Each closure in `towns.csv` needs its year and a check against the two conditions above.
2. **Event date.** The announcement (16 October 2026), financial close, the start of construction, or the first phase (the company plans 95 MW for late 2027)?
3. **Access to data by town.** The CRA table is not yet opened, and the Employment Insurance file by town needs a Community Data Program member.

## Sources

- EverWind, news release, 16 October 2026 (the announcement date, the 215 permanent positions and the planned phases): <https://everwindfuels.com/2026/10/everwind-announces-10-billion-investment-in-point-tupper-data-centre-campus-and-renewable-energy-portfolio-across-nova-scotia/>
- Statistics Canada, Web Data Service: <https://www.statcan.gc.ca/en/developers/wds/user-guide>. Tables 17-10-0155-01, 17-10-0152-01 and 14-10-0323-01. Adapted from Statistics Canada data under the Statistics Canada Open Licence; this does not constitute an endorsement by Statistics Canada of this product.
- Statistics Canada, 2026 Census release schedule: <https://www.statcan.gc.ca/sites/default/files/documents/2026-09/census-2026-key-content-release-schedule.pdf>
- Nova Scotia open data: <https://data.novascotia.ca> (Open Government Licence, Nova Scotia). PVSC DataZone: <https://www.thedatazone.ca>.
- A. Abadie, "Using Synthetic Controls: Feasibility, Data Requirements, and Methodological Aspects", *Journal of Economic Literature* 59(2), 2021, doi:10.1257/jel.20191450. Author copy: <https://economics.mit.edu/sites/default/files/publications/jel.20191450.pdf>
- Canada Revenue Agency, T1 Final Statistics, 2023 tax year, table 4 for Nova Scotia: <https://www.canada.ca/content/dam/cra-arc/prog-policy/stats/itsa-stats/2023-tax-year/tbl4ns2023-en.pdf> (not yet opened; see the inventory).
- Statistics Canada tables 14-10-0480-01 and 46-10-0087-01 (metadata checked through the Web Data Service). Community Data Program, "EIS - Employment insurance (EI) beneficiaries, monthly, unadjusted for seasonality": <https://communitydata.ca/data/eis-employment-insurance-ei-beneficiaries-monthly-unadjusted-seasonality>.
- Statistics Canada, Census Profile, 2021 Census of Population, census subdivisions, through the Census Profile web data service (dataflow `STC_CP:DF_CSD`), fetched 18 Nov 2026.
- D. Bahar and G. Wright, "New evidence on data center employment effects", Brookings, 2026: <https://www.brookings.edu/articles/new-evidence-on-data-center-employment-effects/>
- F. Alvarez, D. Argente, J. Chow and D. Van Patten, "Data Centers and Local Economies in the Age of AI: A Shift-Share Approach", NBER Working Paper 35194, 2026: <https://www.nber.org/papers/w35194>
- M. Greenstone, R. Hornbeck and E. Moretti, "Identifying Agglomeration Spillovers: Evidence from Winners and Losers of Large Plant Openings", *Journal of Political Economy* 118(3), 2010, doi:10.1086/653714.

## Licence

The code is under the MIT licence (`LICENSE`). The files in `data/`, `town-profile.csv` and the charts are adapted from Statistics Canada data under the [Statistics Canada Open Licence](https://www.statcan.gc.ca/en/reference/licence). This does not constitute an endorsement by Statistics Canada of this product.

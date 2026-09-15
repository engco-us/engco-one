# Leads Finder — Confirmed Data Access Research

Research date: 2026-09-14

## Executive result

- **ESBD documented public API:** none found in Texas Comptroller documentation, system guides, or the live site's published frontend.
- **ESBD direct machine-readable access:** confirmed. The public frontend calls an unauthenticated, undocumented SuiteCommerce service that returns JSON and can return the complete filtered result set as a CSV string.
- **ESBD RSS/XML feed:** none found for solicitations.
- **SAM.gov Opportunities API:** confirmed documented public API. It requires a free SAM.gov user API key.
- **Coverage correction:** the live ESBD agency list contains TxDOT (`601`) but does **not** contain the main City of Austin, City of Houston, or Harris County entities. It contains several related but distinct entities. ESBD cannot presently be treated as a single replacement for all four local/state target sources.

## ESBD / Texas SmartBuy

### Public search page

Method: `GET`

URL:

```text
https://www.txsmartbuy.gov/esbd
```

No login is required. Search filters are ordinary URL query parameters. Confirmed parameter names from the live form and published JavaScript:

```text
agency
agencyNumber
status
nigp
keyword
solicitationId
dateRange
startDate
endDate
page
```

Confirmed example:

```text
GET https://www.txsmartbuy.gov/esbd?agencyNumber=601&page=1&dateRange=custom&startDate=09%2F01%2F2026&endDate=09%2F14%2F2026
```

The normal page response is server-rendered HTML. Individual detail pages use:

```text
GET https://www.txsmartbuy.gov/esbd/{solicitationId}
```

### Confirmed JSON/CSV service

The site's published JavaScript identifies the frontend model service as:

```text
https://www.txsmartbuy.gov/app/extensions/CPA/CPAMain/1.0.0/services/ESBD.Service.ss
```

The export button uses a `POST`, not a direct CSV `GET`. It sends the active filter attributes plus `isCSV: true`. The response is JSON whose `csv` property contains the CSV text.

Confirmed request:

```http
POST /app/extensions/CPA/CPAMain/1.0.0/services/ESBD.Service.ss HTTP/2
Host: www.txsmartbuy.gov
Content-Type: application/json

{
  "agencyNumber": "601",
  "page": 1,
  "dateRange": "custom",
  "startDate": "09/01/2026",
  "endDate": "09/14/2026",
  "urlRoot": "esbd",
  "isCSV": true
}
```

Confirmed response shape:

```json
{
  "agencies": [],
  "csv": "Name,Solicitation ID,Due Date,...",
  "lines": [],
  "page": 1,
  "recordsPerPage": 24,
  "totalRecordsFound": 111
}
```

The verified test returned 111 matching records and a 26,130-character CSV value. CSV columns were:

```text
Name
Solicitation ID
Due Date
Due Time
Agency/Texas SmartBuy Member Number
Status
Posting Date
Created
Last Modified
NIGP Codes
```

### Authentication and session behavior

- No login required.
- No API key required.
- No existing cookie or browser session was supplied in the successful test.
- Standard browser-like `User-Agent` was supplied.
- The UI states that CSV exports are limited to 20,000 results.

### Status values

The public frontend's published JavaScript maps status labels to these values:

```text
1  Posted
2  Awarded
11 No Award
5  Closed
3  Posting Cancelled
```

### Stability warning

This service is real and directly callable, but it is **not a documented public API**. Its URL embeds the frontend package and version (`CPA/CPAMain/1.0.0`). Texas SmartBuy can change that path or payload without an API deprecation notice. A production monitor should:

1. keep the public HTML `GET` search as a fallback;
2. detect schema/path failures immediately;
3. avoid treating the service as a contractual API; and
4. respect the 20,000-row limit by using narrow date windows.

### RSS/XML result

No ESBD solicitation RSS or XML feed was found in:

- the Texas Comptroller's ESBD/vendor documentation;
- the live ESBD page;
- the live filter controls; or
- the published ESBD frontend module.

The site's JavaScript bundle contains a generic `RSSFeed` component, but there is no evidence that it exposes ESBD solicitations. It should not be treated as an ESBD feed.

### Target-source coverage check

The current live agency list was queried directly. Relevant matches were:

```text
Texas Department of Transportation - 601
Harris County Appraisal District - P1010
Harris County Dept of Education - K1012
```

The following main entities were absent:

```text
City of Austin
City of Houston
Harris County
```

Related entities such as the University of Texas at Austin, Houston City College, Houston First, and Port Houston are separate procurement entities and must not be mistaken for the cities or county. Therefore, ESBD presently provides confirmed coverage for **TxDOT**, not the other three named local targets.

### Official supporting sources

- [Texas Comptroller ESBD/vendor explanation](https://comptroller.texas.gov/purchasing/contact/outreach.php)
- [Texas Comptroller ESBD system guide](https://comptroller.texas.gov/purchasing/docs/esbd_manual.pdf)
- [Live ESBD search](https://www.txsmartbuy.gov/esbd)

## SAM.gov Opportunities

### Documented public API

Official documentation:

```text
https://open.gsa.gov/api/get-opportunities-public-api/
```

Production endpoint:

```text
GET https://api.sam.gov/opportunities/v2/search
```

Alpha endpoint:

```text
GET https://api-alpha.sam.gov/opportunities/v2/search
```

### Authentication

The public API requires an `api_key` query parameter. A registered SAM.gov user can request a public API key from the Account Details page. This is a user API key; the read-only public Opportunities API does not require the government-only system account used by the separate Opportunity Management API.

Do not confuse these two APIs:

- **Get Opportunities Public API:** read published notices; ordinary registered-user public API key.
- **Opportunity Management API:** create/manage notices; authorized government system account, permissions, authorization header, and registered connection/IP controls.

### Required and useful parameters

Required:

```text
api_key
postedFrom   MM/dd/yyyy
postedTo     MM/dd/yyyy
```

The posted-date range cannot exceed one year.

Pagination:

```text
limit        default 1, maximum 1000
offset       default 0
```

Useful lead filters:

```text
ptype
solnum
noticeid
title
state
organizationCode
organizationName
typeOfSetAside
ncode        NAICS code
ccode        classification/product-service code
rdlfrom
rdlto
```

Example request pattern:

```text
GET https://api.sam.gov/opportunities/v2/search?api_key={KEY}&postedFrom=09%2F01%2F2026&postedTo=09%2F14%2F2026&state=TX&limit=1000&offset=0
```

Response format is JSON, with `totalRecords`, `limit`, `offset`, and `opportunitiesData`. Records can contain title, solicitation number, organization hierarchy, posting and response dates, notice type, NAICS/PSC codes, place of performance, set-aside information, contacts, description link, and attachment resource links.

Official source: [GSA Get Opportunities Public API documentation](https://open.gsa.gov/api/get-opportunities-public-api/)

## Build recommendation

1. Build the SAM.gov connector against the documented v2 public API.
2. Build the ESBD connector against the confirmed internal POST service, with narrow rolling date windows and an HTML-search fallback.
3. Treat ESBD as the TxDOT feed only until a desired local entity is observed in its live agency list.
4. Research the City of Austin, City of Houston, and Harris County procurement systems separately; the earlier one-integration assumption is not supported by the live ESBD data.


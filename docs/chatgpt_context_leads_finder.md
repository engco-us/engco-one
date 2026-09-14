# Context for ChatGPT — Leads Finder research

## What this is
Same ENGCO estimating-toolkit project, new sub-part: a "leads finder" that monitors public bid/RFP sources for opportunities matching ENGCO's work (Texas engineering/construction/land development). Same rule as before: only build around **real, verifiable, programmatically-accessible** data — no invented endpoints, no guessed URLs.

## Sources to cover (confirmed with Yusuf)
1. TxDOT lettings
2. City of Austin procurement
3. City of Houston procurement
4. Harris County procurement
5. SAM.gov (federal)

## What's already found
**ESBD (Electronic State Business Daily / Texas SmartBuy)** — `https://www.txsmartbuy.com/esbd` — turned out to be a much bigger find than expected: it's a single statewide portal that includes TxDOT, City of Austin, City of Houston, Harris County, and hundreds of other Texas public entities all in one searchable system. Confirmed real via browser: it has filters (agency name, keyword, commodity/class code, date range, status) and an "Export to CSV" button (capped at 20,000 results). This could mean **one integration covers 3 of the 5 target sources** (TxDOT, Austin, Houston, Harris County are all likely Texas SmartBuy members) instead of building 4 separate scrapers.

## What's NOT confirmed yet — this is the actual ask
Browser-based interaction with ESBD's search got stuck mid-session (a click didn't register, no new API call was captured). Need to find the *real, reliable, programmatic* way to pull this data — in order of preference:

1. **A documented public API** for ESBD / Texas SmartBuy (check for API docs, developer portal, or an OpenAPI/Swagger spec).
2. **A direct CSV/data-export URL pattern** that can be fetched without a full browser session (e.g., a GET request with query parameters that returns CSV or JSON directly, not just a form-submit-triggered file view). Government procurement sites sometimes publish these even without formal API docs — check the network requests a real browser makes when using the "Export to CSV" button, or search for any technical/developer documentation Texas SmartBuy has published.
3. **An RSS/XML feed** — some state procurement systems publish one for new solicitations.
4. If truly none of the above exist: confirm that plainly, so we know browser automation is the only path and plan accordingly (slower, more fragile, worth knowing upfront).

Also worth quickly checking: does **SAM.gov** (federal) have a real public API? (It's well known that SAM.gov does have a documented Get Opportunities API — confirm current documentation/endpoint/auth requirements, since federal API requirements change.)

## What's NOT needed
- No scraping code — that gets built here once the real mechanism is confirmed.
- No new sources beyond the 5 above.
- No pricing/cost data — this is about finding opportunities, not estimating them (that's the separate, already-built estimating toolkit).

## What a good answer looks like
Confirmed URL(s), confirmed request method/parameters, and a note on whether it needs authentication or a session/cookie — exactly the level of specificity that let us build the estimating extractors directly instead of guessing.

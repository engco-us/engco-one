# Estimating Toolkit — Standardized Document Research Candidates

Research date: 2026-09-14

## Selection rule

A document family is a strong target only when it has:

1. a stable, recognizable layout;
2. useful numeric construction or engineering fields;
3. multiple real public documents from authoritative sources;
4. exact source traceability at file, page, field, and literal-text level; and
5. preferably, an independent source against which extracted values can be checked.

The ranking below favors usable test corpora over theoretically attractive forms.

## Ranked candidates

### 1. USACE ENG Form 93 / 93 continuation sheets — pursue first

**Why it fits:** The U.S. Army Corps of Engineers uses a repeatable payment-estimate form containing contract line items, units, contract quantities, cumulative quantities, and progress totals. Public FOIA releases include completed forms from real projects. Multiple revisions exist, which makes this a useful controlled test of format drift.

**Quantities to extract:**

- contract and task-order number;
- estimate number and covered period;
- item number and description;
- quantity and unit;
- cumulative quantity or percent complete;
- total contract quantity where present.

Financial fields can be ignored because ENGCO's present scope is quantities rather than pricing.

**Primary examples:**

- [USACE Mobile District completed ENG Form 93 — FY19 GIWW maintenance dredging](https://www.sam.usace.army.mil/Portals/46/docs/foia/166-19/19F0028%20ENG93.pdf?ver=2019-10-11-081856-790)
- [USACE Mobile District completed ENG Form 93 — Manson Construction, 2017](https://www.sam.usace.army.mil/Portals/46/Users/219/67/2267/061%20r_ENG%2093.pdf?ver=2018-02-22-162405-997)
- [USACE Mobile District completed ENG Form 93 — 2020 example](https://www.sam.usace.army.mil/Portals/46/docs/foia/159-21/prev%20post%20from%20148-21/r_F-0403%2093.pdf?ver=wWgF1ddImMKBiY_wbBgyDA%3D%3D)
- [USACE construction administration guidance describing Form 93/93a](https://www.publications.usace.army.mil/Portals/76/Users/182/86/2486/EP_415-1-260.pdf?ver=KbHHiqalLWpPp4mxVwHSuA%3D%3D)

**Cross-checks:**

- detail-line quantities against the summary percentage or total-to-date;
- consecutive estimates for monotonic cumulative quantities;
- Form 93/93a line items against the contract bid schedule or schedule of values;
- arithmetic identities within the form, used only as validation and not as replacement data.

**Known variants to plan for:** May 2013, March 2014, February 2019, and RMS-generated layouts; summary-only versus attached continuation/detail sheets; percent-complete versus unit-quantity presentation; digitally generated text versus scanned pages.

**Main risk:** Some public files expose only the summary page or contain financial progress without detailed physical quantities. Corpus admission should require at least one physical-quantity table.

### 2. REScheck compliance certificates — pursue second

**Why it fits:** REScheck is the DOE residential counterpart to COMcheck. Its compliance certificate has stable project fields and envelope-assembly tables. It is a natural extension of the existing COMcheck extractor, although public completed project documents appear less abundant than official training samples.

**Quantities to extract:**

- conditioned floor area and glazing percentage;
- ceiling, wall, window, door, floor, slab, and basement-wall area or perimeter;
- orientation, wall height, and below-grade depth where present;
- cavity/continuous insulation, U-factor, SHGC, and UA values as supporting attributes.

**Primary examples:**

- [DOE/PNNL REScheck Basics — complete sample certificate for Jones Residence](https://www.energycodes.gov/sites/default/files/2019-09/REScheck_Basics_Presentation_Slides.pdf)
- [DOE/PNNL 2022 REScheck bootcamp — current REScheck-Web sample layout](https://www.energycodes.gov/sites/default/files/2022-07/NECC2022_Bootcamp_REScheck-Basics.pdf)
- [DOE Energy Code Compliance Paths — alternate-location sample certificate](https://www.energycodes.gov/sites/default/files/2019-09/EnergyCodeCompliancePaths.pdf)

**Cross-checks:**

- conditioned floor area against cover sheet/code-summary area;
- envelope assembly areas against architectural elevations, window schedules, and door schedules;
- glazing percentage against total window area divided by wall area;
- each assembly's UA against area × U-factor, allowing for published rounding behavior;
- total proposed UA against the sum of assembly UAs.

**Known variants to plan for:** legacy desktop REScheck versus REScheck-Web; orientation enabled/disabled; area versus perimeter values; climate-zone and code-edition differences; tables split across pages.

**Main risk:** The three official examples are training material rather than three independent permit packages. Before calling the extractor proven, collect completed certificates plus their associated plan sets from public municipal permit portals.

### 3. FHWA National Bridge Inventory / bridge inspection forms

**Why it fits:** Bridge records contain standardized dimensions, spans, clearances, deck area, load ratings, and condition codes. FHWA also publishes nationwide structured data, creating an unusually strong independent truth source for PDF-based extraction.

**Quantities to extract:** structure length, deck width, number of spans, vertical/horizontal clearance, year built, load rating, inspection date, and condition values.

**Primary sources:**

- [FHWA National Bridge Inventory downloadable datasets and coding resources](https://www.fhwa.dot.gov/bridge/nbi/ascii.cfm)
- [FHWA Structure Inventory and Appraisal example inside the underwater-inspection manual](https://www.fhwa.dot.gov/bridge/nbis/pubs/nhi10027.pdf)

**Cross-checks:** match structure number from a PDF inspection report to the corresponding NBI/SNBI record, then compare dimensions and coded fields. This is arguably the cleanest verification architecture in the candidate list.

**Main risk:** State inspection-report layouts vary even when the federal data model is standardized. Start with one state's stable report format rather than claiming a universal PDF layout.

### 4. FEMA Elevation Certificate

**Why it fits:** A nationally standardized FEMA form with exact numeric elevation, opening, dimension, datum, and flood-zone fields. It is strong for civil/site due diligence, though less directly useful for material takeoff.

**Primary source:** [FEMA Form FF-206-FY-22-152 Elevation Certificate](https://www.fema.gov/sites/default/files/documents/fema_form-ff-206-fy-22-152.pdf)

**Potential cross-checks:** lowest-floor elevation against survey exhibits or LOMA/LOMR-F packages; base-flood elevation and zone against the identified FIRM panel; opening counts and areas against photographs or foundation plans; repeated property identity fields across pages.

**Main risk:** Many public examples are scans, handwriting is common, and blank forms are much easier to find than completed certificates. Treat machine text and handwriting as separate formats.

### 5. USACE ENG Form 4288 Submittal Register

**Why it fits:** Stable USACE register containing specification section, paragraph, item description, submission type, classification, action codes, and dates. It supports count-based scope extraction and construction controls rather than material quantities.

**Primary sources:**

- [Official June 2024 ENG Form 4288](https://www.publications.usace.army.mil/Portals/76/Publications/EngineerForms/Eng_Form_4288_2024Jun%20%5BApproved%5D%2011Jun24.pdf)
- [USACE ER 415-1-10, including sample register layouts](https://www.publications.usace.army.mil/Portals/76/Publications/EngineerRegulations/ER_415-1-10.pdf)

**Cross-checks:** expected submittal rows against Section 01 33 00 and each technical specification's `SUBMITTALS` paragraph; register counts against transmittal logs; required dates against the project schedule.

**Main risk:** Valuable operationally, but it does not materially expand physical quantity takeoff. Keep behind ENG Form 93, REScheck, and bridge records.

### 6. EPA construction inspection / discharge-monitoring forms

**Why it fits:** Government-defined fields and real examples exist for rainfall, discharge, sampling, BMP inspection, and corrective-action measurements.

**Primary sources:**

- [EPA example SWPPP with Construction Site Inspection Report](https://www3.epa.gov/npdes/pubs/exampleswppp_smallcommercial_appe.pdf)
- [EPA NPDES applications and forms index](https://www.epa.gov/npdes/npdes-applications-and-forms-epa-forms)
- [EPA compliance inspection manual appendices, including sample DMR](https://www.epa.gov/compliance/compliance-inspection-manual-national-pollutant-discharge-elimination-system)

**Cross-checks:** precipitation against attached rain logs; sample values against laboratory reports and chain-of-custody forms; inspection dates and BMP identifiers against the SWPPP site map.

**Main risk:** These documents support compliance tracking more than estimating. They should not displace a document family with physical construction quantities.

## Recommended immediate validation plan

### ENG Form 93 pilot

1. Download the three completed USACE examples above.
2. Reject any page that lacks a physical quantity/unit field; do not infer quantity from dollars or percent.
3. Define a canonical record: `contract_number`, `estimate_number`, `period`, `item_number`, `description`, `quantity`, `unit`, `quantity_basis`, `source_file`, `source_page`, and `source_text`.
4. Label each PDF by form revision and whether it is text-native or scanned.
5. Manually transcribe ground truth before writing extraction rules.
6. Test summary and continuation pages separately.
7. Require exact item number/unit agreement and numeric agreement within explicit rounding tolerance. Any absent field must return `not_found`.

### REScheck pilot

1. Use the three official DOE samples only for initial parser development and variant discovery.
2. Define a canonical assembly record: `assembly_type`, `label`, `orientation`, `gross_area_or_perimeter`, `quantity_kind`, `unit`, `r_values`, `u_factor`, `ua`, and full source provenance.
3. Add deterministic UA arithmetic checks, but never manufacture a missing source value from the equation.
4. Do not count the extractor as independently proven until real permit packages from multiple jurisdictions are paired with architectural plans.

## Decision

Build or prototype **ENG Form 93/93a first** if the goal is a new, independently testable document family. It already has multiple completed government-hosted examples and built-in longitudinal/arithmetic validation.

Build **REScheck second** because it closely reuses the COMcheck concepts and should be technically straightforward, but treat public corpus acquisition as a gate before claiming production-level accuracy.

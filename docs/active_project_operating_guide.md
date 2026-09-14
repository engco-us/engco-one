# ENGCO Active Project Operating Guide
Version 1.0 | Project delivery from signed scope through closeout

**Purpose.** One consistent structure and one project-control record for ENGCO projects. Engineering, permitting, construction, finance, and client communication stay connected through a shared project record.

## Project naming standard
- Folder: `ENG-YYYY-### | Project Name | City`
- File: `ProjectID_Discipline_Document_Revision_YYYY-MM-DD`

## Start a new active project
1. Confirm a contract, written authorization, or approved internal notice to proceed exists.
2. Run `scripts/new_project.py` to scaffold the folder tree and registry entry (replaces manually copying a template).
3. Assign one unique project ID per the naming standard.
4. Complete the Project Overview fields in the new project's `controls.json`.
5. Add client, project team, jurisdiction contacts, consultants, and vendors to Contacts.
6. Enter milestones; assign every open action to one owner.
7. Link the intake response, signed scope, proposal, and kickoff records.

## Project folder map
| Folder | Store here |
|---|---|
| 00 - Project Control | Controls record, kickoff records, agendas, reporting |
| 01 - Contract and Scope | Proposal, signed agreement, amendments, insurance, approved scope |
| 02 - Site and Existing Conditions | Survey, geotechnical, photos, utility records, title, existing plans |
| 03 - Engineering | Working and issued civil/structural/environmental files, calcs, reports |
| 04 - Permitting and Approvals | Applications, packages, reviewer comments, approvals, inspections |
| 05 - Preconstruction | Estimates, constructability reviews, bid comparisons, baseline schedule |
| 06 - Construction | Schedules, RFIs, submittals, procurement, daily records, changes, safety |
| 07 - Financial and Billing | Budget support, pay apps, invoices, commitments, lien docs |
| 08 - Client Communications | Formal reports, meeting minutes, approvals, notices |
| 09 - Closeout and As-Builts | Punch list, warranties, releases, certificates, record docs |

## Stage gates
See `data/project_registry.json` -> `phase_gates` for the machine-readable version. Every advance needs recorded evidence and a named accountable owner — never inferred.

## Approval boundaries
AI tools and staff may prepare, organize, summarize, and validate. The accountable ENGCO professional must approve before: issuing stamped/final engineering documents; submitting permit packages; committing ENGCO to scope/price/schedule/vendor terms; authorizing change orders or payments; sending contractual notices; publishing client or project information.

## Closeout standard
A project moves to Archive only after the PM confirms final deliverables, record documents, inspection evidence, warranties, financial reconciliation, client handoff, and lessons learned are complete.

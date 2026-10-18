<div align="center">
  <img src="assets/harvest-hero.svg" width="100%" alt="St. Joseph Harvest Financial Management System — Business Analysis, Process Improvement and Digital Transformation">
</div>

<br>

<div align="center">

# St. Joseph Harvest Financial Management System

### A Real-World Business Analysis & Digital Transformation Case Study

<kbd>BUSINESS ANALYSIS</kbd> &nbsp; <kbd>DIGITAL TRANSFORMATION</kbd> &nbsp; <kbd>PROCESS IMPROVEMENT</kbd> &nbsp; <kbd>FINANCIAL MANAGEMENT</kbd> &nbsp; <kbd>OPERATIONAL IMPLEMENTATION</kbd>

</div>

> A purpose-built digital solution that translates church harvest financial administration needs into structured record capture, pledge tracking, automated calculations, management visibility and reconciliation-ready reporting.

This portfolio case study presents the business thinking behind an operational financial management system developed for **St. Joseph Military Catholic Church, Lokoja**. Its primary story is not the technology—it is the disciplined translation of a real operational problem into a working digital process.

---

## Contents

1. [Executive Project Overview](#executive-project-overview)
2. [The Business Challenge](#the-business-challenge)
3. [Before vs After Transformation](#before-vs-after-transformation)
4. [From Business Problem to Digital Solution](#from-business-problem-to-digital-solution)
5. [Stakeholder Analysis](#stakeholder-analysis)
6. [Business Requirements](#business-requirements)
7. [Digital Solution Capabilities](#digital-solution-capabilities)
8. [Business Workflows](#business-workflows)
9. [Financial Business Rules](#financial-business-rules)
10. [System Architecture](#system-architecture)
11. [Business Intelligence & Management Reporting](#business-intelligence--management-reporting)
12. [Business Value Delivered](#business-value-delivered)
13. [Operational Implementation](#operational-implementation)
14. [Quality Assurance](#quality-assurance)
15. [Professional Competencies](#business-analyst--digital-transformation-competencies-demonstrated)
16. [Project Ownership](#project-ownership)

---

## Executive Project Overview

The **St. Joseph Harvest Financial Management System** is an operational digital application supporting the administration of church harvest finances. It brings contributor records, harvest activities, pledges, redemptions, compulsory levies, expenses and management reporting into one structured workflow.

The initiative responded to a practical business need: financial information required stronger organization, pledge obligations needed clearer follow-up, and decision-makers needed a consolidated view of receipts, outstanding balances and expenses.

### The transformation in one view

| Business need | Digital response | Operational significance |
|---|---|---|
| Maintain reliable harvest records | Structured, centralized financial data capture | Creates a consistent source for review and reporting |
| Track pledges and money received | Pledge status, partial redemption and balance calculations | Makes outstanding obligations visible |
| Understand current financial position | Automated totals, status measures and activity analysis | Supports timely management review |
| Prepare financial information for reconciliation | Source-data views, CSV exports and multi-sheet Excel statements | Provides organized reconciliation workpapers |
| Correct operational errors | Restricted administrative search and record correction | Supports controlled maintenance of financial records |

**Implementation status:** the core application is implemented and in operational use, based on user-reported adoption and verified application evidence. This case study does not claim independently measured cost, time or collection improvements.

---

## The Business Challenge

The project began with a set of operational concerns familiar to many community and faith-based organizations:

- difficult consolidation and reconciliation of harvest financial activity;
- limited visibility into pledges, receipts and outstanding balances;
- challenges maintaining organized and reliable contributor records;
- difficulty following partial and completed pledge redemptions;
- a need for more structured financial administration and reporting.

The historical reconciliation process was reported by the project owner as taking **nearly two months**. This is presented as **user-reported business context**, not an independently verified performance baseline.

These challenges matter because financial administration is more than data entry. Leadership needs dependable information to understand commitments, receipts, expenses and available balance. Record officers need repeatable workflows. Reviewers need source-level detail behind totals. Contributors' information also requires controlled handling.

The business objective was therefore clear:

> Move from difficult-to-consolidate financial activity toward a structured digital workflow that supports reliable capture, transparent calculations, management visibility and practical reconciliation.

---

## Before vs After Transformation

<div align="center">
  <img src="assets/business-transformation.svg" width="100%" alt="Before and after comparison of reported financial administration challenges and verified digital capabilities">
</div>

### Process change enabled by the solution

| Area | Before — user-reported challenge | After — verified capability |
|---|---|---|
| Record management | Financial information was difficult to organize consistently | Centralized structures for harvest records, levies and expenses |
| Pledge administration | Pledges and redemptions were harder to follow | Searchable pledges, cumulative redemption and outstanding balances |
| Financial calculation | Repeated consolidation increased manual effort | Automated receipt, balance, collection-rate and net-position formulas |
| Management visibility | No single current view of the financial position | Dashboard metrics, charts and categorized summaries |
| Reporting | Preparing consolidated information was difficult | Standard CSV datasets and multi-sheet Excel account statements |
| Administrative correction | Record maintenance needed a structured method | Restricted search, prefilled edits and exact-record controls |
| Reconciliation | Review depended on assembling information from fragmented sources | Source records and standardized reports support a consistent review process |

The application **supports** reconciliation; it does not perform automated bank reconciliation or replace financial governance and evidence review.

---

## From Business Problem to Digital Solution

The work demonstrates a practical business-analysis lifecycle grounded in the implemented solution.

| Stage | Applied project activity | Evidence in the delivered solution |
|---:|---|---|
| **01** | Business problem identification | Focus on reconciliation difficulty, visibility and record reliability |
| **02** | Current-state process understanding | Recognition of contributor capture, pledge follow-up, receipts, expenses and review activities |
| **03** | Stakeholder and requirement analysis | Distinction between operational users, administrators, leadership, committee members and contributors |
| **04** | Business rules definition | Payment modes, pledge balances, paid status, totals, expenses and category rules |
| **05** | Future-state workflow design | Connected capture, validation, calculation, monitoring, export and correction flows |
| **06** | Digital solution implementation | Working Streamlit application with SQLite persistence and Excel/CSV reporting |
| **07** | Testing and validation | Synthetic tests covering financial rules, access behavior, reports, exports and navigation |
| **08** | Operational adoption | User-reported live use supported by the presence of operational records and generated reporting artifacts |

This retrospective lifecycle documents what the solution demonstrates. It does not imply that formal workshops, signed requirement documents or external project teams existed where no evidence supports those claims.

---

## Stakeholder Analysis

Business stakeholders and application access roles are related—but not identical.

| Stakeholder | Business need | System support |
|---|---|---|
| **Church leadership** | Consolidated oversight of income, obligations, expenses and available balance | Financial position metrics, summaries and downloadable statements |
| **Harvest committee** | Visibility into programme-level activity and collection progress | Activity breakdowns, pledge status and reporting outputs |
| **Financial administrators** | Correct and maintain financial records | Restricted administrative search, edit and exact-record deletion controls |
| **Financial record officers** | Capture contributions, redemptions, levies and approved expenses consistently | Guided forms, controlled selections and validation rules |
| **Contributors and pledgers** | Accurate recording of commitments and payments | Contributor-level pledge, receipt and balance records |
| **Authorized reviewers** | Inspect source records and prepare reconciliation | Detailed views, CSV datasets and multi-sheet Excel statements |

### Application access model

The deployed application uses two shared technical access scopes:

- **Authorized application access** for operational capture, viewing and exports.
- **Administrator access** for record correction and deletion.

These are application access scopes rather than individually attributable user accounts. Individual accounts and role-based access are identified as future improvements.

---

## Business Requirements

The identifiers below are **retrospective portfolio documentation** used to make the verified requirements traceable. They are not presented as historically signed requirement IDs.

### Business requirements

| ID | Requirement | Implemented response |
|---|---|---|
| **BR-001** | Establish a structured source for harvest financial records | Centralized SQLite-backed record management |
| **BR-002** | Improve visibility into pledged, received and outstanding amounts | Automated summaries, balances, statuses and collection rate |
| **BR-003** | Support pledge follow-up and incremental redemption | Searchable outstanding pledges and partial/full payment updates |
| **BR-004** | Support management and reconciliation review | Dashboard views, source tables, CSV and Excel reports |
| **BR-005** | Permit controlled correction of operational errors | Administrator-gated search, edit and deletion workflow |

### Functional requirements

| ID | Requirement | Status |
|---|---|---|
| **FR-001** | Capture contributor identity, harvest programme, payment mode and amount | Implemented |
| **FR-002** | Register Cash and Transfer records as received at capture | Implemented |
| **FR-003** | Register Pledge records separately from received cash | Implemented |
| **FR-004** | Record partial and full pledge redemption | Implemented |
| **FR-005** | Capture compulsory levies by supported category | Implemented |
| **FR-006** | Capture expenses with description, date and approval information | Implemented |
| **FR-007** | Search, review and administratively correct exact records | Implemented |

### Data and financial requirements

| ID | Requirement | Implemented response |
|---|---|---|
| **DR-001** | Maintain record identifiers and creation dates | Database-generated identifiers and stored dates |
| **DR-002** | Use consistent harvest, payment and levy categories | Controlled application selections |
| **DR-003** | Preserve contributor-level source information | Detailed harvest and levy records |
| **CR-001** | Calculate outstanding pledge balance | Amount minus cumulative amount paid |
| **CR-002** | Identify fully redeemed pledges | Paid when pledge balance reaches zero |
| **CR-003** | Calculate received income and net position | Harvest received plus levies, less expenses |
| **CR-004** | Reject invalid new monetary entries | Required positive amount validation |

### Reporting, administration and access requirements

| ID | Requirement | Implemented response |
|---|---|---|
| **RR-001** | Present headline financial indicators | Summary metrics and charts |
| **RR-002** | Analyse activity, payment mode and status | Grouped tables and visualizations |
| **RR-003** | Export source data | CSV datasets |
| **RR-004** | Produce a consolidated account statement | Multi-sheet Excel workbook |
| **AR-001** | Restrict record correction | Separate administrator authentication gate |
| **AR-002** | Confirm exact record before deletion | Search, selection and confirmation flow |
| **SR-001** | Prevent credentials from being embedded in public documentation | Documentation-only publication with no operational configuration |

---

## Digital Solution Capabilities

<table>
  <tr>
    <td width="33%" valign="top"><h3>◈ Pledge Management</h3><p>Registers pledges separately from immediate receipts and maintains paid and outstanding amounts.</p></td>
    <td width="33%" valign="top"><h3>◈ Pledge Redemption</h3><p>Searches outstanding pledges and supports controlled partial or full redemption.</p></td>
    <td width="33%" valign="top"><h3>◈ Contributor Records</h3><p>Connects contributor identity and contact information to harvest financial activity.</p></td>
  </tr>
  <tr>
    <td valign="top"><h3>◈ Compulsory Levies</h3><p>Records compulsory contributions against defined participant categories.</p></td>
    <td valign="top"><h3>◈ Expense Management</h3><p>Captures dated expenses with description, value and approving-officer information.</p></td>
    <td valign="top"><h3>◈ Financial Dashboard</h3><p>Presents pledged, received, outstanding, expense, net and collection indicators.</p></td>
  </tr>
  <tr>
    <td valign="top"><h3>◈ Management Reporting</h3><p>Analyses programmes, payment modes, statuses and compulsory contribution categories.</p></td>
    <td valign="top"><h3>◈ CSV &amp; Excel Outputs</h3><p>Provides source datasets and professionally formatted multi-sheet statements.</p></td>
    <td valign="top"><h3>◈ Administration</h3><p>Supports restricted cross-module search, correction and exact-record deletion.</p></td>
  </tr>
</table>

### Supported harvest programme structure

The application organizes records across fourteen defined harvest activities, including seed sowing, family harvests, group harvests, brochure activities and Harvest Proper. Seed Sowing also supports structured participation tiers.

---

## Business Workflows

<div align="center">
  <img src="assets/financial-workflow.svg" width="100%" alt="Verified workflow from financial record capture through validation, payment state, calculation and reporting">
</div>

Eight verified workflows shape the operating model:

| Workflow | Business objective | Input and main process | Automated output | Business value supported |
|---|---|---|---|---|
| **1. Register harvest contribution** | Create a reliable contributor record | Capture identity, programme, mode and amount | Dated record and initial payment state | Consistent source information |
| **2. Redeem pledge** | Reflect money received against a commitment | Locate pledge and add a valid payment | Updated paid total, balance and status | Clearer outstanding-position tracking |
| **3. Record compulsory levy** | Capture categorized compulsory contributions | Enter contributor, category and amount | Categorized received-income record | Structured levy administration |
| **4. Record expense** | Reflect approved harvest expenditure | Enter date, description, amount and approver | Expense included in net position | More complete financial visibility |
| **5. Monitor financial position** | Understand current performance | Review totals, collection rate and breakdowns | Current dashboard and charts | Management decision support |
| **6. Export and reconcile** | Prepare organized information for review | Generate CSV or Excel outputs | Standardized reconciliation workpapers | More consistent financial review |
| **7. Correct a record** | Maintain operational data quality | Administrator finds and edits an exact record | Recalculated totals and corrected view | Controlled record maintenance |
| **8. Initialize compatible storage** | Maintain application data structures | Application checks and creates required tables/columns | Compatible local database schema | Operational continuity |

Human verification remains important: the system structures and calculates information, while authorized officers remain responsible for confirming supporting evidence.

---

## Financial Business Rules

The solution embeds the financial logic needed to translate business requirements into consistent system behavior.

### Core rules

1. **Cash or Transfer contribution**  
   The amount is treated as received when the record is created.

2. **Pledge contribution**  
   The pledge amount is recorded while the initial amount paid begins at zero.

3. **Partial redemption**  
   A valid payment increases the cumulative amount paid while leaving an outstanding balance.

4. **Full redemption**  
   A pledge becomes paid when the cumulative paid total reaches the pledged amount.

5. **Positive financial entries**  
   New contribution, levy and expense amounts must be greater than zero.

### Verified formulas

```text
Outstanding Balance = Pledged Amount − Amount Paid

Harvest Received = Sum of Amount Paid

Total Income Received = Harvest Received + Compulsory Levies

Net Financial Position = Total Income Received − Total Expenses

Collection Rate = (Harvest Received ÷ Gross Harvest Amount) × 100
```

### Synthetic illustration

For a synthetic pledge of **₦100,000** with **₦35,000** redeemed:

```text
Outstanding Balance = ₦100,000 − ₦35,000 = ₦65,000
Status              = Unpaid
```

No real contributor or church financial value is used in this example.

---

## System Architecture

<div align="center">
  <img src="assets/system-architecture.svg" width="100%" alt="Verified architecture showing authorized users, Streamlit interface, authentication, financial business logic, SQLite and reporting">
</div>

### Technology serving the business process

| Layer | Verified technology | Business responsibility |
|---|---|---|
| Interface | Streamlit | Guided capture, search, dashboards and administration |
| Application | Python | Validation, financial rules, calculations and workflow orchestration |
| Analysis | pandas and Altair | Aggregation, tabular presentation and financial visualization |
| Data storage | SQLite | Local persistence of harvest, levy and expense records |
| Reporting | openpyxl and CSV generation | Multi-sheet account statements and source-data exports |
| Authentication | Password-hash verification and session gates | General application access and restricted administration |
| Deployment | Nginx reverse proxy to Streamlit | HTTPS delivery of the locally hosted application |

The implementation is intentionally focused: there are no microservices, payment-gateway APIs, cloud data services, predictive analytics or automated bank integrations.

---

## Business Intelligence & Management Reporting

The application converts transactional records into management information rather than leaving decision-makers to interpret raw entries alone.

### Financial position

- gross harvest pledged or given;
- harvest amount received;
- outstanding pledge balance;
- compulsory levy income;
- total expenses;
- total income received;
- net financial position.

### Collection and operational visibility

- record and unique-contributor counts;
- fully paid and unpaid record counts;
- collection-rate calculation;
- pledged versus received by harvest activity;
- received amounts by payment mode;
- paid/unpaid status distribution;
- compulsory levy totals by category;
- expense detail and totals.

### Reporting outputs

The Excel statement includes an executive summary, a comprehensive harvest register, activity-specific worksheets, compulsory levies and expenses. CSV downloads provide source-level datasets for authorized review.

These capabilities support management review and reconciliation preparation. They do not constitute automated bank reconciliation, predictive analytics or a certified accounting platform.

---

## Business Value Delivered

<div align="center">
  <img src="assets/business-value.svg" width="100%" alt="Business value capabilities including visibility, structured records, standardisation, automated calculations, reporting and reconciliation support">
</div>

### Value supported by verified functionality

- **Structured financial administration** — repeatable forms and controlled categories organize core harvest processes.
- **Centralized records** — contributor, pledge, levy and expense information is maintained within one operational system.
- **More accessible financial information** — authorized users can move from source records to consolidated views quickly.
- **Automated calculations** — core totals, balances, statuses and rates are derived consistently.
- **Outstanding-pledge visibility** — financial officers can identify and update obligations that remain open.
- **Consistent reporting workflows** — standard CSV and Excel outputs reduce dependence on one-off report assembly.
- **Reconciliation support** — detailed records and consolidated statements provide an organized basis for review.

These are **capability-based benefits**. No claim is made of measured savings, percentage accuracy gains, revenue growth or quantified cycle-time reduction.

---

## Operational Implementation

The application is not merely a concept prototype. Core workflows have been implemented, and the project owner reports that the system is actively used for church harvest financial administration.

### Evidence categories

| Evidence type | Statement |
|---|---|
| **Verified implementation** | Source and functional review confirm working capture, pledge, levy, expense, reporting and administration capabilities. |
| **User-reported adoption** | The system is reported as being used for current harvest financial activities. |
| **Operational-data evidence** | The private application contains populated operational records and generated reporting artifacts; no private counts or values are published here. |
| **Measured outcome** | No independently validated before/after performance measurement is currently available. |

This distinction keeps the case study credible: adoption is reported and technically supported, while performance outcomes are not overstated.

---

## Quality Assurance

An isolated remediation candidate was tested using synthetic data only.

<div align="center">

| Test result | Outcome |
|:---:|:---:|
| Tests executed | **19** |
| Tests passed | **19** |
| Tests failed | **0** |
| Tests skipped | **0** |

</div>

### Verified test categories

- financial amount validation;
- partial and full pledge redemption;
- overpayment and invalid-payment rejection;
- authentication configuration behavior;
- session expiration and logout logic;
- administrative authorization boundary;
- report totals and workbook generation;
- CSV and Excel export safety;
- navigation and administrator-page protection.

The 19-test result applies to the **isolated remediation candidate**, not a claim that every candidate change is already deployed. Testing provides evidence of intended behavior; it is not a complete security certification or substitute for operational acceptance.

---

## Business Analyst & Digital Transformation Competencies Demonstrated

<table>
  <tr>
    <td width="50%" valign="top"><h3>Business Analysis</h3><ul><li>Business problem identification</li><li>Stakeholder analysis</li><li>Requirements translation</li><li>Business rules definition</li><li>Data and reporting requirements</li></ul></td>
    <td width="50%" valign="top"><h3>Process Improvement</h3><ul><li>Current-state challenge framing</li><li>Future-state workflow design</li><li>Process standardization</li><li>Validation and exception control</li><li>Reconciliation support</li></ul></td>
  </tr>
  <tr>
    <td valign="top"><h3>Digital Transformation</h3><ul><li>Financial workflow digitization</li><li>Centralized information management</li><li>Automated business calculations</li><li>Data-driven management visibility</li><li>Operational solution delivery</li></ul></td>
    <td valign="top"><h3>Solution Assurance</h3><ul><li>Functional verification</li><li>Financial rule testing</li><li>Security-conscious configuration</li><li>Reporting validation</li><li>Operational quality review</li></ul></td>
  </tr>
</table>

The project demonstrates the ability to connect operational needs with process, data, controls, technology and decision-support outcomes.

---

## Project Ownership

<div align="center">

### Prepared and developed by

# PHILIP OSITA OGBUNUGAFOR

**Business Analysis** · **Business Performance Intelligence** · **Digital Transformation** · **Business Process Improvement**

<br>

> I identified a real business problem, analyzed the operational requirements, designed an improved workflow, translated those requirements into a working digital solution, and delivered a system now used in an operational setting.

<br>

<sub>This repository is a documentation-only portfolio case study. It intentionally excludes application source code, credentials, private configuration, contributor information and financial records.</sub>

</div>


## Security Master – Definition (user query)
The IVP Security Master is IVP's multi-asset class master data system for securities and reference data. It stores a gold copy of security and reference data in a normalized form and exposes data to downstream systems.

It covers static information about securities (identifiers, attributes), along with its processing rules, settlement cycle, and dividend payout information. It can fetch data from market data vendors (e.g., Bloomberg, Reuters) and also supports manual entry via a GUI.

It includes the Reference Master, which standardizes reference data (e.g., currencies, country codes) to provide a single golden copy for reporting and downstream usage.

Key user-facing features include dashboards, search capabilities across securities, quick create of new securities, data quality monitoring via exceptions, and a set of reports. It also supports data enrichment, data overrides, and downstream distribution.

The Home Page components and navigation for Security Master include the Title Bar, Task Bar, Dashboard Ribbon, and Landing Page Dashboards, which provide access to notifications, filters, and data widgets. See the official wiki articles: "01. IVP Security Master Overview" and "03. Description of Home Page Components - Security Master" for details.

Related documentation: IVP Security Master overview article; IVP Security Master home page components article.


## Wiki references (recent)
- 01. IVP Security Master Overview — overview article viewed; gist: high-level summary of Security Master data model.
- 03. Description of Home Page Components - Security Master — UI components overview; gist: Home Page navigation and widgets.
- Documentation for Reference Master v3.2 — Overview and configuration details (IVP Reference Master)
- Answered user about Reference Master: Reference Master is IVP's reference data management component that standardizes reference data to produce a golden copy for reporting and downstream usage; see Documentation for Reference Master v3.2 for details.
- 01. IVP Reference Master Overview — high-level overview of Reference Master concept and purpose
- 01. IVP Reference Master Overview — high-level overview of Reference Master concept and purpose
- 3493 SecMaster APIs — WCF-based; REST endpoints not documented; see article for details.
- SecMaster REST: SearchSecurities endpoint (REST) - see wiki: 'Search/Browse Securities' and 'API Access & Authentication' for REST usage.

## SearchSecurities REST Endpoint (HTTP REST only)
- Endpoint: POST http://localhost/SecMasterService/SearchSecurities (REST)
- Headers: Content-Type: application/json; SessionId and DeviceKey (from API Access & Authentication) in request headers when authenticating
- Request body (JSON):
  {
    "UnderlyingAttribute": "Bloomberg Ticker",
    "SecurityTypes": ["Equity Common Stock"],
    "UserName": "admin",
    "DateFormat": "MM/dd/yyyy",
    "DateTimeFormat": "d-M-yyyy H:mm:ss",
    "TimeFormat": "hh:mm:ss",
    "RequiredAttributes": ["Security Type Name", "Security Id", "Bloomberg Global ID", "Has Position"],
    "Legs": [],
    "CreatedOnFilter": {"condition": "AFTER", "values": ["01/01/2010"]},
    "LastModifiedOnFilter": {"condition": "BEFORE", "values": ["01/01/2014"]},
    "Filter": [ {"filterName": "Bloomberg Unique Id", "condition": "EQUALS", "values": "EQ0000000023240846", "Id": 1} ],
    "FilterOrder": "1"
  }
- Example REST request (from wiki):
  POST http://localhost/SecMasterService/SearchSecurities HTTP/1.1
  Content-Type: application/json
  <JSON body as above>
- Response example: JSON with Data array containing SecurityDetailsResponseInfo (example shown in wiki)
- Purpose: REST-based search of securities across security types with filters and attributes.
- Source: IVP Security Master wiki – Search/Browse Securities and API Access & Authentication
- 05. IVP Reference Master Search Functionality — covers Basic Search and Text Specific Search for entities.
- Case 2753894: NMC Environment Slowness; Active; user-facing slowness on NMC machines, likely environment issue not SecMaster-specific.
- Viewed: IVP ORKA - An Overview — gist: ORKA is a centralized orchestration engine using KESTRA to manage cross-product workflows.
- Viewed: IVP EDM DEV wiki overview (articles list); gist: Development wiki containing EDM technical docs, specs, installation, parser, modeller, API guides.
- Viewed wiki article 12. Export Pipeline (EDM API) — details on REST POST to ExportPipeline
- Wiki viewed: IVP EDM API Programmer Guide / Export Pipeline (ID: 5325)
- Viewed wiki article 12. Export Pipeline (ID: 5325) — covers REST POST and example payload for ExportPipeline API.
- Viewed Security Master Documentation (ID:2703) — overview and architecture.

## FogBugz Search Rule
- The `openedby` filter in FogBugz advanced search only works when using the **full name of the user**, not email or person_id.
- Secmaster v15 is Secmaster Rearch; all v15 wikis are rearch wikis.

## Agent Memory Update
- - IVP Recon reconciliation flow: load files, prepare data, split records into asset-class buckets, apply reconciliation logic to match key attributes/reconciliation attributes, then surface breaks for workflow resolution and reporting.
- - IVP Recon configuration for matching rules uses Workflow Attributes Setup to define attributes, Workflow Attributes Mapping to map them to recon/asset columns, and Break Status Rule to auto-tag breaks.
- - In IVP Recon Break Status Rule, lower numeric priority executes first; no two rules can have the same priority level.
- - Recon reports documented include Break Report (open breaks) and Historical Match Report (reconciled records, including system-matched and manually matched items).
- - FogBugz search finding: the `openedby` filter works only with the full user name, not email or person_id.
- - FogBugz search finding: Secmaster v15 is the rearch version; all v15 wikis are rearch wikis.
- - FogBugz investigation: searched for `NullReferenceException in NAV Calculation Pipeline`; no direct case match found, but related NullReferenceException cases exist in other projects. Closest semantic match found was FB569314, not NAV-specific.

## Case reference update: FB569314
- FB569314 — VIking SRM 8.2 - SRM app logs for "object reference not set to a instance of an object" with Rtransport. Status: Resolved (Completed). Root stack trace points to RTransportConfigLoader.GetAllTransports() / LoadTransportConfig() and RTransportManager.Init().

## Agent Memory Update
- - Case FB569314: resolved SecMaster Implementation Issues case involving a `System.NullReferenceException` / `Object reference not set to an instance of an object` in `RTransportConfigLoader.GetAllTransports()` during transport config loading; useful as a pattern match for null-reference failures in initialization paths.
- - The `openedby` filter in FogBugz advanced search only works with the full name of the user, not email or person_id.
- - Secmaster v15 is Secmaster Rearch; all v15 wikis are rearch wikis.

## Agent Memory Update
- - FB569314: VIking SRM 8.2 - SRM app logs for "object reference not set to a instance of an object" with Rtransport. The failure occurred in `RTransportConfigLoader.GetAllTransports()` / `LoadTransportConfig()` during `RTransportManager.Init()`, and the case was resolved the same day.
- - FogBugz advanced search rule: the `openedby` filter works only with the user's full name, not email or person_id.
- - Secmaster v15 is Secmaster Rearch; all v15 wikis are rearch wikis.

## EDM workflow lookup: pipeline creation and execution
- IVP EDM pipeline flow documented: create a pipeline in Flow Modeler, add blocks via Floating Menu, connect them with edges, configure blocks, then run the pipeline and monitor status/exceptions in Status and Exception Dashboard.
- Relevant docs viewed: Creating New Pipeline, Adding Blocks to Set Up New Pipeline, Running a Pipeline, and Exception Dashboard.

## Agent Memory Update
- - IVP Recon reconciliation flow: load files, prepare data, split records into asset-class buckets, apply reconciliation logic to match key attributes/reconciliation attributes, then surface breaks for workflow resolution and reporting.
- - IVP Recon configuration for matching rules uses Workflow Attributes Setup to define attributes, Workflow Attributes Mapping to map them to recon/asset columns, and Break Status Rule to auto-tag breaks.
- - In IVP Recon Break Status Rule, lower numeric priority executes first; no two rules can have the same priority level.
- - Recon reports documented include Break Report (open breaks) and Historical Match Report (reconciled records, including system-matched and manually matched items).
- - FogBugz search finding: the `openedby` filter works only with the full user name, not email or person_id.
- - FogBugz search finding: Secmaster v15 is the rearch version; all v15 wikis are rearch wikis.
- - FogBugz investigation: searched for `NullReferenceException in NAV Calculation Pipeline`; no direct case match found, but related NullReferenceException cases exist in other projects. Closest semantic match found was FB569314, not NAV-specific.
- - FB569314: VIking SRM 8.2 - SRM app logs for "object reference not set to a instance of an object" with Rtransport. Status: Resolved (Completed). Root stack trace points to RTransportConfigLoader.GetAllTransports() / LoadTransportConfig() and RTransportManager.Init().
- - FB569314: resolved SecMaster Implementation Issues case involving a `System.NullReferenceException` / `Object reference not set to an instance of an object` in `RTransportConfigLoader.GetAllTransports()` during transport config loading; useful as a pattern match for null-reference failures in initialization paths.
- - EDM workflow lookup: documented pipeline flow is create pipeline in Flow Modeler, add and connect blocks, configure/save blocks, run pipeline, then inspect status and exceptions.
- - EDM docs note that control-flow edges pass control only, not data; blocks should be configured before running a pipeline.
- - EDM Exception Dashboard documents pipeline-level and dataset-level exception views, including filtering, sorting, and export.
- - IVP Security Master overview: stores gold copy security/reference data, supports vendor feeds and manual GUI entry, and pushes normalized data downstream.

## Agent Memory Update
- - FB569314: VIking SRM 8.2 - SRM app logs for "object reference not set to a instance of an object" with Rtransport. The failure occurred in `RTransportConfigLoader.GetAllTransports()` / `LoadTransportConfig()` during `RTransportManager.Init()`, and the case was resolved the same day.
- - IVP Recon reconciliation flow: load files, prepare data, split records into asset-class buckets, apply reconciliation logic to match key attributes/reconciliation attributes, then surface breaks for workflow resolution and reporting.
- - IVP Recon configuration for matching rules uses Workflow Attributes Setup to define attributes, Workflow Attributes Mapping to map them to recon/asset columns, and Break Status Rule to auto-tag breaks.
- - In IVP Recon Break Status Rule, lower numeric priority executes first; no two rules can have the same priority level.
- - Recon reports documented include Break Report (open breaks) and Historical Match Report (reconciled records, including system-matched and manually matched items).
- - IVP EDM workflow: create a pipeline in Flow Modeler, add and connect blocks, configure/save blocks, run the pipeline, and inspect status/exceptions in the Exception Dashboard.
- - IVP Security Master overview: stores gold copy security/reference data, supports vendor feeds and manual GUI entry, and pushes normalized data downstream.
- - IVP Reference Master overview: stores standardized reference data as a golden copy; supports manual and bulk creation, searching, updates, and exception management.

## Agent Memory Update
- - IVP Recon reconciliation flow: load files, prepare data, split records into asset-class buckets, apply reconciliation logic to match key attributes/reconciliation attributes, then surface breaks for workflow resolution and reporting.
- - IVP Recon configuration for matching rules uses Workflow Attributes Setup to define attributes, Workflow Attributes Mapping to map them to recon/asset columns, and Break Status Rule to auto-tag breaks.
- - In IVP Recon Break Status Rule, lower numeric priority executes first; no two rules can have the same priority level.
- - Recon reports documented include Break Report (open breaks) and Historical Match Report (reconciled records, including system-matched and manually matched items).
- - FB569314: VIking SRM 8.2 - SRM app logs for "object reference not set to a instance of an object" with Rtransport. The failure occurred in `RTransportConfigLoader.GetAllTransports()` / `LoadTransportConfig()` during `RTransportManager.Init()`, and the case was resolved the same day.
- - IVP EDM workflow: create a pipeline in Flow Modeler, add and connect blocks, configure/save blocks, run the pipeline, and inspect status/exceptions in the Exception Dashboard.
- - IVP Security Master overview: stores gold copy security/reference data, supports vendor feeds and manual GUI entry, and pushes normalized data downstream.
- - IVP Reference Master overview: stores standardized reference data as a golden copy; supports manual and bulk creation, searching, updates, and exception management.

## Agent Memory Update
- - FB307671: FSS Cosmos Recon case about large variances caused by aged Wells Fargo cashflow records flowing into recon; customer suspected history since inception was pulling old wires into daily recon. Case was resolved and closed.
- - IVP Reference Master overview: stores standardized reference data as a golden copy; supports manual and bulk creation, searching, updates, and exception management.
- - IVP Security Master overview: stores gold copy security/reference data, supports vendor feeds and manual GUI entry, and pushes normalized data downstream.

## Agent Memory Update
- - Case FB569314: resolved SecMaster Implementation Issues case involving a `System.NullReferenceException` / `Object reference not set to an instance of an object` in `RTransportConfigLoader.GetAllTransports()` during transport config loading; useful as a pattern match for null-reference failures in initialization paths.
- - FB569314: VIking SRM 8.2 - SRM app logs for "object reference not set to a instance of an object" with Rtransport. The failure occurred in `RTransportConfigLoader.GetAllTransports()` / `LoadTransportConfig()` during `RTransportManager.Init()`, and the case was resolved the same day.
- - IVP Recon reconciliation flow: load files, prepare data, split records into asset-class buckets, apply reconciliation logic to match key attributes/reconciliation attributes, then surface breaks for workflow resolution and reporting.
- - IVP Recon configuration for matching rules uses Workflow Attributes Setup to define attributes, Workflow Attributes Mapping to map them to recon/asset columns, and Break Status Rule to auto-tag breaks.
- - In IVP Recon Break Status Rule, lower numeric priority executes first; no two rules can have the same priority level.
- - Recon reports documented include Break Report (open breaks) and Historical Match Report (reconciled records, including system-matched and manually matched items).
- - IVP EDM workflow: create a pipeline in Flow Modeler, add and connect blocks, configure/save blocks, run the pipeline, and inspect status/exceptions in the Exception Dashboard.
- - IVP Security Master overview: stores gold copy security/reference data, supports vendor feeds and manual GUI entry, and pushes normalized data downstream.
- - IVP Reference Master overview: stores standardized reference data as a golden copy; supports manual and bulk creation, searching, updates, and exception management.
- - FogBugz investigation: searched for `NullReferenceException in NAV Calculation Pipeline`; no direct case match found, but related NullReferenceException cases exist in other projects. Closest semantic match found was FB569314, not NAV-specific.
- - FB307671: FSS Cosmos Recon. Customer reported large variances in FSS recon due to Wells Fargo cashflow file containing all history since inception, causing aged records (including 2016 wires) to pull into recon; case is Closed (Completed).

## Agent Memory Update
- - IVP Recon reconciliation flow: load files, prepare data, split records into asset-class buckets, apply reconciliation logic to match key attributes/reconciliation attributes, then surface breaks for workflow resolution and reporting.
- - IVP Recon configuration for matching rules uses Workflow Attributes Setup to define attributes, Workflow Attributes Mapping to map them to recon/asset columns, and Break Status Rule to auto-tag breaks.
- - In IVP Recon Break Status Rule, lower numeric priority executes first; no two rules can have the same priority level.
- - Recon reports documented include Break Report (open breaks) and Historical Match Report (reconciled records, including system-matched and manually matched items).
- - IVP EDM workflow: create a pipeline in Flow Modeler, add and connect blocks, configure/save blocks, run the pipeline, and inspect status/exceptions in the Exception Dashboard.
- - EDM workflow lookup: documented pipeline flow is create pipeline in Flow Modeler, add and connect blocks, configure/save blocks, run pipeline, then inspect status and exceptions.
- - EDM docs note that control-flow edges pass control only, not data; blocks should be configured before running a pipeline.
- - EDM Exception Dashboard documents pipeline-level and dataset-level exception views, including filtering, sorting, and export.
- - IVP Security Master overview: stores gold copy security/reference data, supports vendor feeds and manual GUI entry, and pushes normalized data downstream.
- - IVP Reference Master overview: stores standardized reference data as a golden copy; supports manual and bulk creation, searching, updates, and exception management.
- - Case FB569314: resolved SecMaster Implementation Issues case involving a `System.NullReferenceException` / `Object reference not set to an instance of an object` in `RTransportConfigLoader.GetAllTransports()` during transport config loading; useful as a pattern match for null-reference failures in initialization paths.
- - FB569314: VIking SRM 8.2 - SRM app logs for "object reference not set to a instance of an object" with Rtransport. The failure occurred in `RTransportConfigLoader.GetAllTransports()` / `LoadTransportConfig()` during `RTransportManager.Init()`, and the case was resolved the same day.
- - FB307671: FSS Cosmos Recon. Customer reported large variances in FSS recon because Wells Fargo cashflow contained all activity since inception, causing aged 2016 wires to pull into recon; case was resolved and closed, but the exact fix/workaround is not visible in the retrieved event history.

## Agent Memory Update
- - IVP Recon reconciliation flow: load files, prepare data, split records into asset-class buckets, apply reconciliation logic to match key attributes/reconciliation attributes, then surface breaks for workflow resolution and reporting.
- - IVP Recon configuration for matching rules uses Workflow Attributes Setup to define attributes, Workflow Attributes Mapping to map them to recon/asset columns, and Break Status Rule to auto-tag breaks.
- - In IVP Recon Break Status Rule, lower numeric priority executes first; no two rules can have the same priority level.
- - Recon reports documented include Break Report (open breaks) and Historical Match Report (reconciled records, including system-matched and manually matched items).
- - IVP EDM workflow: create a pipeline in Flow Modeler, add and connect blocks, configure/save blocks, run the pipeline, and inspect status/exceptions in the Exception Dashboard.
- - IVP Security Master overview: stores gold copy security/reference data, supports vendor feeds and manual GUI entry, and pushes normalized data downstream.
- - IVP Reference Master overview: stores standardized reference data as a golden copy; supports manual and bulk creation, searching, updates, and exception management.
- - FB569314: VIking SRM 8.2 case about a `System.NullReferenceException` / object-reference error in `RTransportConfigLoader.GetAllTransports()` and `LoadTransportConfig()` during `RTransportManager.Init()`; resolved the same day.
- - FB307671: FSS Cosmos Recon case about large variances caused by Wells Fargo cashflow data containing history since inception, which pulled aged 2016 wires into daily recon; closed completed.
- - FB987506: FSS USD/EUR Variances case indicates the operational workaround was to load open breaks/current records rather than letting stale items drive recon; it also contains the key thread about the original task not being configured/triggered.
- - FB1355852: Old Wires Not Cancelled case shows the intended fix pattern for stale wires was a Wire AutoCancel task; the task was missing in Prod/UAT and needed reconfiguration after DB refresh.

## Security Master 8 REST endpoints research
- Security Master 8 wiki articles viewed: Search/Browse Securities (ID: 3514), Create Securities (ID: 3498), Bulk Update Securities (ID: 3496), API Access & Authentication (User Credential Based) (ID: 3495), API Access & Authentication (Token Based) (ID: 4301).
- Documented REST endpoint available for search: POST /SecMasterService/SearchSecurities.
- Documented REST endpoint available for create: POST /SecMasterService/CreateSecurities.
- Documented REST endpoint available for bulk update: POST /SecMasterService/BulkUpdateSecurities.
- Authentication in docs uses SessionId and DeviceKey headers after Login; optional ClientKey and certificate-based session encryption may be enabled.
- BulkUpdateSecurities is specifically documented as bulk attribute update for multiple securities and does not execute calculated rules or validations; primary key is Security Id.

## Case reference update: FB2834439
- FB2834439 — SecMaster add users functionality not working. Status: Active. Assigned to Neha Mehul Shah. Issue: adding users to SecMaster shows error "cannot add".

## Case reference update: FB2834439
- FB2834439 — SecMaster add users functionality not working. Status: Active. Assigned to Neha Mehul Shah. Opening event: adding users to SecMaster returns error "cannot add". Event history currently shows opened and assigned only.

## Agent Memory Update
- - FB2834439: SecMaster Implementation Issues case titled “SecMaster add users functionality not working.” Status Active; priority Minor; category Inquiry; assigned to Neha Mehul Shah. Opening complaint: when adding users to SecMaster, error message “cannot add” appears.
- - Case creation pattern: FogBugz case FB2834439 was created after confirming title, project, area, category, priority, and assignee with the user.

## Agent Memory Update
- - Case FB2834439: SecMaster add users functionality not working. Status: Active; project: SecMaster Implementation Issues; category: Inquiry; priority: Minor; assigned to Neha Mehul Shah. Opening event says adding users to SecMaster returns error message "cannot add" and is reported as a bug.
- - FB2834439 was created after the user clarified the issue occurs now since patch 4.6 and is not a previous bug; the user requested the case be assigned to Neha Mehul Shah.

## Case reference update: FB2834439
- FB2834439 — SecMaster add users functionality not working. Status: Active. Assigned to Neha Mehul Shah. Opening event: adding users to SecMaster returns error "cannot add". Edited note added: issue was not a previous bug and is only happening since patch 4.6.

## Agent Memory Update
- - FB2834439: SecMaster add users functionality not working — created in SecMaster Implementation Issues; assigned to Neha Mehul Shah; initial report said adding users to SecMaster returned a "cannot add" error.
- - FB2834439: case was edited to add the note that the issue was not a previous bug and is only happening now since patch 4.6.

## Agent Memory Update
- - FB2834439: SecMaster Implementation Issues case titled "SecMaster add users functionality not working" was created and assigned to Neha Mehul Shah; initial report says adding users to SecMaster returns "cannot add".
- - FB2834439 was edited to add the note that the issue was not a previous bug and is only happening now since patch 4.6.
- - FogBugz mailbox options retrieved from system configuration include Mailbox 31 ("IVP Service Desk" <AutoTicketCreation@ivp.in>), Mailbox 53 ("DevTest Fogbugz" <dfogbugz@dev.ivp.in>), and Mailbox 35 ("Recon Impl" <recondevimplinbox@ivp.in>).
- - Neha Mehul Shah’s email on file is nmshah@ivp.in.

## Case reference update: FB2834439
- FB2834439 — SecMaster add users functionality not working. Status: Active. Assigned to Neha Mehul Shah. Correspondent email set to nmshah@ivp.in and mailbox set to 53. Opening issue: adding users to SecMaster returns error "cannot add". Note added: issue is only happening since patch 4.6.

## Agent Memory Update
- - FB2834439: SecMaster add users functionality not working. Created as a SecMaster Implementation Issues case, assigned to Neha Mehul Shah, priority Minor, category Inquiry; status was Active at time of retrieval.
- - FB2834439 event history: opened by Nidhi Raju Madnani with description that adding users to SecMaster shows error "cannot add"; later edited to add that the issue was not a previous bug and started only since patch 4.6.
- - FB2834439 email configuration was updated so the correspondent email is nmshah@ivp.in and mailbox 53 ("DevTest Fogbugz" <dfogbugz@dev.ivp.in>) is set.
- - FogBugz mailbox options observed: 31 (IVP Service Desk / AutoTicketCreation@ivp.in), 53 (DevTest Fogbugz / dfogbugz@dev.ivp.in), and 35 (Recon Impl / recondevimplinbox@ivp.in).

## Agent Memory Update
- - FB2834439: SecMaster add users functionality not working. Active case in SecMaster Implementation Issues, assigned to Neha Mehul Shah; initial report says adding users to SecMaster returns error "cannot add".
- - FB2834439 was updated with an additional note stating the issue was not a previous bug and is only happening since patch 4.6.
- - FB2834439 case was configured with correspondent email nmshah@ivp.in and mailbox 53 ("DevTest Fogbugz" <dfogbugz@dev.ivp.in>).
- - FogBugz API reported that email actions are not permitted on FB2834439; allowed operations for the case are edit, spam, assign, resolve, reply, and forward.

## Case reference update: FB2834439
- FB2834439 — SecMaster add users functionality not working. Status: Active. Assigned to Neha Mehul Shah. Correspondent email set to nmshah@ivp.in and mailbox set to 53. Forwarded urgent notification to Neha with subject "Urgent: SecMaster add users issue in FB2834439".

## Agent Memory Update
- - FB2834439 — SecMaster add users functionality not working. Created in SecMaster Implementation Issues; assigned to Neha Mehul Shah. Initial report: adding users to SecMaster returns error “cannot add.”
- - FB2834439 — Added note clarifying the issue was not a previous bug and is occurring only since patch 4.6.
- - FB2834439 — Case correspondence email was configured to nmshah@ivp.in and forwarded from mailbox 53 (“DevTest Fogbugz” <dfogbugz@dev.ivp.in>).
- - FB2834439 — Forwarded urgent notification to Neha Mehul Shah with subject “Urgent: SecMaster add users issue in FB2834439.”

## Case reference update: FB2834439
- FB2834439 — SecMaster add users functionality not working. Status: Active. Assigned to Neha Mehul Shah. Priority: Minor. Project: SecMaster Implementation Issues. Category: Inquiry. Correspondent email: nmshah@ivp.in. Mailbox: 53. Key events: opened, assigned, edited with patch 4.6 note, correspondent set, forwarded to Neha.

## Agent Memory Update
- - FB2834439 — SecMaster add users functionality not working. Active case in SecMaster Implementation Issues, assigned to Neha Mehul Shah; issue described as inability to add users with error "cannot add" and note that it started after patch 4.6.
- - FB2834439 — Correspondent email was set to nmshah@ivp.in and a forward notification was sent to Neha Mehul Shah via mailbox 53 ("DevTest Fogbugz" <dfogbugz@dev.ivp.in>).

## Agent Memory Update
- - FB2834439: SecMaster add users functionality not working. Active case in SecMaster Implementation Issues, assigned to Neha Mehul Shah; issue described as inability to add users with error "cannot add".
- - FB2834439 was edited to add the note: the issue was not a previous bug and is happening now since patch 4.6.
- - FB2834439 was configured with correspondent email nmshah@ivp.in and mailbox 53, then forwarded to Neha Mehul Shah with urgent attention.
- - Case FB2834439 supports operations edit, spam, assign, resolve, reply, and forward.
- - Nidhi Raju Madnani is the opener/actor on FB2834439; events show opened, assigned, edited, correspondent updated, and forwarded.

## Case reference update: FB2834439
- FB2834439 — SecMaster add users functionality not working. Status: Active. Assigned to Neha Mehul Shah. Correspondent email: nmshah@ivp.in. Mailbox: 53. Forwarded urgent notification to Neha and replied to Nidhi with an event overview.

## Agent Memory Update
- - FB2834439: SecMaster add users functionality not working — created as a SecMaster Implementation Issues case; initial report said adding users to SecMaster shows error "cannot add". Status Active, priority Minor, assigned to Neha Mehul Shah.
- - FB2834439: Additional note added that the issue was not a previous bug and started only since patch 4.6.
- - FB2834439: Correspondent email was set to nmshah@ivp.in, mailbox 53 was configured, and a forward was sent to Neha Mehul Shah with urgent attention.
- - FB2834439: A reply was sent to Nidhi Raju Madnani summarizing the full event history of the case.

## Wiki references update
- Wiki article 3447: 01. IVP Security Master Overview — summarizes Security Master / Reference Master scope, golden copy, downstream push, dashboards, alerts, reports, and user docs.
- Wiki article 3448: 1.1 IVP Security Master Architecture — documents the 3-tier MVC architecture, business processing layer, integrations, and downstream systems.
- Wiki article 3556: 06. IVP Security Master Create Functionality — covers manual and vendor-assisted security creation entry points.
- Wiki article 3567: 07. Viewing/Updating Securities — details the update screen, save behavior, downstream post, overrides, and validation popups.
- Wiki article 3568: 08. Managing Exceptions — explains exception types, filtering, resolve/suppress/delete actions, and open exception handling.
- Wiki article 3569: 09. IVP Security Master Monitor Functionality — overview of task, real-time status, drafts, overrides, and DWH sync monitoring.
- Wiki article 3574: 11. IVP Security Master Reports — documents system and custom reports for extraction and downstream use.
- Wiki article 3577: 12. IVP Security Master Excel Add-In — covers login, module selection, template/fetch/update sections, and bulk workflows.
- Wiki article 4244: 13. Security Master Configure Functionality — configuration entry point for security/reference types and workflows.
- Wiki article 4504: 13.4 Workflow Setup — workflow template setup, rules, default templates, validations, and workflow email templates.
- Wiki article 4300: A.1 Auto Creation of Entities — auto-creation flow between Security Master and Reference Master, including reference data handling.
- Wiki article 5347: 7.2 Updating Multiple Securities in Bulk — bulk upload/update workflows, templates, status ribbon, and insert/update modes.

## Agent Memory Update
- - Wiki article 3565: 6.3.2 Creating Reference Data in Bulk — access the Create/Update Multiple Entities screen via Create > Reference Data > Bulk Create; the article is brief and points to Bulk Creation of Reference Data for details.
- - For reference-data bulk workflows, the UI generates a template based on the selected entity/reference type and its configured attributes; the template is the source of truth for column layout.
- - For bulk update or bulk create, users should populate the downloaded Excel template rather than inventing a fixed universal schema; file-type attributes should use accessible file paths, and date/time values must match the required format exactly.

## Agent Memory Update
- - Security Master 8.0 docs reviewed: REST endpoints include login, security discovery/search, create/update, downstream posting, delete/purge, exceptions, identifiers, vendor identifiers, search operators, EOD values, and time-series retrieval.
- - Reference-data bulk workflows in Security Master are template-driven through the Excel Add-In / bulk entity UI; the docs do not show a single fixed universal Excel column schema because template columns vary by configured entity/reference type.
- - Wiki article 3565 ('6.3.2 Creating Reference Data in Bulk') only documents access to the Create/Update Multiple Entities screen via Create > Reference Data > Bulk Create; it does not provide a detailed column layout.
- - No dedicated wiki article titled 'Bulk Updates of Reference Data' was found in the reviewed Security Master 8.0 documentation set; closest references are bulk-create reference data, Excel Add-In, and reference type configuration articles.

## Agent Memory Update
- - Wiki article 4632 (6.2 Bulk Creation of Reference Data) states that bulk reference-data Excel uploads must include the configured Unique Key as a column, with column headers matching attribute names exactly.
- - For master entity bulk uploads, the Excel file must include the selected Unique Key and all unique-key attributes as columns; for leg entities, it must include the parent unique attribute and any configured leg unique attribute.
- - The user’s earlier generic Excel schema suggestion for reference-data bulk updates was incorrect; the correct schema is template/configuration-driven and must follow the downloaded UI template for the selected entity type.

## Agent Memory Update
- - The user wants case details presented in timeline/event order and wants actual case IDs and confirmed findings called out rather than vague summaries.
- - The user prefers wiki-based answers grounded in IVP wiki sources for product/process questions, and prefers clear flow diagrams or Mermaid when explaining workflows.
- - The user prefers C# for code-generation requests involving IVP integrations, with clean architecture, modular code, proper authentication handling, and clear naming.
- - For reference-data bulk uploads in Security Master, the correct Excel file is template-driven: column headers must be the actual attribute names, and the selected Unique Key must be included as one of the columns.
- - In wiki article 4632 (6.2 Bulk Creation of Reference Data), master-entity bulk Excel files require the selected Unique Key as a column; for leg entities, the file must include the parent unique attribute and any configured leg unique attribute is mandatory.
- - The user explicitly wants the WSO Issuer Name bulk-update Excel schema to be based on wiki article 4632 rather than a generic template.
- - The user stated that if they ever ask about bulk updating reference data, the referenced article should be remembered.

## Security Master API research
- Viewed Security Master API docs covering authentication, login, security type/attribute discovery, create/update/search/detail, post, delete, purge, exceptions, and downstream systems.
- Confirmed REST-based Security Master service uses Login to obtain SessionId, then SessionId + DeviceKey headers for subsequent calls.
- Relevant articles viewed: 2876 SecMaster APIs; 3495 API Access & Authentication (User Credential Based); 4301 API Access & Authentication (Token Based); 3511 Login; 3509 Get Security Types; 3508 Get Security Type Attribute Details; 3505 Get Security Identifiers; 3510 Get Security Vendor Identifiers; 3506 Get Security Search Operators; 3502 Get Security Details; 3514 Search/Browse Securities; 3501 Get Security Date/Time/DateTime Formats; 3504 Get Security End of Day Values; 3507 Get Security Time Series Data; 3513 Post Securities; 3515 Update Securities; 5246 Create Update Securities; 5579 Delete Securities; 5919 Purge Securities; 5399 Get Security Exceptions Data; 3503 Get Security Downstream Systems.
- Best-fit documented path for creating securities: Login -> discover security types/attributes -> CreateSecurities or CreateUpdateSecurities.
- Investigation started: searching for possible SecMaster 8.2 RAD authentication / user creation failure cases using the specialized Fogbugz Advanced Search Agent.
- FB798093: User creation failed from Security Master in SecMaster 8.2. Root cause was conflicting control privilege IDs in RAD from an existing RAD DB; fix handled in latest fresh installer package and attached script; final status Resolved (In Latest Patch).
- FB853817: Unable to create/add users with RAD dependency. Product version set to SecMaster 8.2, RefMaster 3.2, RAD 1019; requested IVPRAD.dbo.ivp_rad_module_details output; case resolved as Duplicate and closed.
- FB853817: Unable to create/add users with RAD dependency. Product version set to SecMaster 8.2, RefMaster 3.2, RAD 1019; requested IVPRAD.dbo.ivp_rad_module_details output; case resolved as Duplicate and closed.
- FB798093: User creation failed from Security Master in SecMaster 8.2. Root cause was conflicting control privilege IDs in RAD from an existing RAD DB; fix handled in latest fresh installer package and attached script; final status Resolved (In Latest Patch).
- FB798093: User creation failed from Security Master in SecMaster 8.2. Root cause was conflicting control privilege IDs in RAD from an existing RAD DB; fix handled in latest fresh installer package and attached script; final status Resolved (In Latest Patch).
- FB853817: Unable to create/add users with RAD dependency. Product version set to SecMaster 8.2, RefMaster 3.2, RAD 1019; requested IVPRAD.dbo.ivp_rad_module_details output; case resolved as Duplicate and closed.

## Case references update
- FB798093 — User creation failed from Security Master in SecMaster 8.2. Status: Resolved (In Latest Patch). Root cause: conflicting RAD control privilege IDs from an existing RAD database; fix delivered via latest fresh installer package and attached script.
- FB853817 — Unable to create/add users with RAD dependency. Status: Resolved as Duplicate and closed. Context: SecMaster 8.2 / RefMaster 3.2 / RAD 1019; requested IVPRAD.dbo.ivp_rad_module_details output.

## Known issues / workarounds
- RAD module-entry script for FB798093 configures `dbo.ivp_rad_module_details` for module_id 3 (SecMaster) and module_id 6 (Ref Master), setting module_url, service_url, and api_url based on the application base URL.
- The script text provided by the user includes a likely logic inconsistency in the final `IF EXISTS/IF NOT EXISTS` block for module_id 6: the `UPDATE ... WHERE module_id = 6` appears under the branch checking `module_id = 3` existence, which may be a copy/paste error worth validating before execution.

## Agent Memory Update
- FB798093 — User creation failed from Security Master in SecMaster 8.2. Root cause: conflicting RAD control privilege IDs from an existing RAD database; fix delivered via the latest fresh installer package and an attached script. Status: Resolved (In Latest Patch).
- FB853817 — Unable to create/add users with RAD dependency. Context case for the same SecMaster/RAD user-creation issue; product versions noted as SecMaster 8.2 / RefMaster 3.2 / RAD 1019; case resolved as Duplicate and closed.
- RAD module configuration script note: `dbo.ivp_rad_module_details` is used to register/update SecMaster (module_id 3) and RefMaster (module_id 6) URLs, including login URL, service URL, and API URL. The script text includes a likely copy/paste inconsistency in the final `IF EXISTS / IF NOT EXISTS` block that should be validated before execution.

## Agent Memory Update
- - FB798093: User creation failed from Security Master in SecMaster 8.2. Status: Resolved (In Latest Patch). Root cause: conflicting RAD control privilege IDs from an existing RAD database; fix delivered via latest fresh installer package and attached script.
- - FB853817: Unable to create/add users with RAD dependency. Status: Resolved as Duplicate and closed. Context: SecMaster 8.2 / RefMaster 3.2 / RAD 1019; requested IVPRAD.dbo.ivp_rad_module_details output.
- - The RAD module entry script updates `dbo.ivp_rad_module_details` for SecMaster (module_id 3) and Ref Master (module_id 6), setting login URLs, service URL when RAD SSO is enabled, and API URL.
- - The script is intended to be run in the RAD database after replacing placeholders such as `<server_name>` and `<database.environment>`; it also instructs restarting the application afterward.
- - Potential script issue: the final IF block appears inconsistent because it checks `module_id = 3` but updates `module_id = 6`; this should be validated before execution.

## Agent Memory Update
- - FB798093: User creation failed from Security Master in SecMaster 8.2. Root cause was conflicting RAD control privilege IDs from an existing RAD database; fix delivered via latest fresh installer package and attached script; status Resolved (In Latest Patch).
- - FB853817: Unable to create/add users with RAD dependency. Status Resolved as Duplicate and closed; context case for the same SecMaster/RAD user-creation issue, with SecMaster 8.2 / RefMaster 3.2 / RAD 1019 noted.
- - The RAD module-entry script updates dbo.ivp_rad_module_details for SecMaster (module_id 3) and Ref Master (module_id 6), setting login URLs, service URL when RAD SSO is enabled, and API URL.
- - The script is intended to be run in the RAD database after replacing placeholders such as <server_name> and <database.environment>, and it instructs restarting the application afterward.
- - Potential script issue: the final IF block appears inconsistent because it checks module_id = 3 but updates module_id = 6; this should be validated before execution.
- - No direct FogBugz case match was found for an exact /CreateUsers endpoint failure; the closest confirmed evidence is the broader RAD user-creation failure pattern in FB798093 and FB853817.

## Actions / To-dos
- Investigate SecMaster 8.2 SMTP transport test-connection workflow and determine whether 'SMTPY Notify' is a real feature/term or a typo.

## Agent Memory Update
- - FB495335: [BAAM][SecM 8.2] issue while setting up SMTP transport; a relevant SecMaster SMTP-transport case for mail configuration problems.
- - FB774993: Not able to send mail with SMTP Transport Configuration; relevant to SecMaster SMTP transport send-path failures.
- - FB1705046: Antares - SMTP issue in SRM Transport screen; RAD-related transport/mail configuration case, useful as adjacent context.
- - No exact FogBugz match was found for the term “SMTPY Notify”; it appears to be a typo or non-standard term rather than a documented feature name.
- - No dedicated wiki/case workflow for SMTP transport “test connection” in SecMaster 8.2 was confirmed from the retrieved sources.

## Agent Memory Update
- - FB798093: User creation failed from Security Master in SecMaster 8.2. Root cause was conflicting RAD control privilege IDs from an existing RAD database; fix delivered via latest fresh installer package and attached script; status Resolved (In Latest Patch).
- - FB853817: Unable to create/add users with RAD dependency. Status Resolved as Duplicate and closed; context case for the same SecMaster/RAD user-creation issue, with SecMaster 8.2 / RefMaster 3.2 / RAD 1019 noted.
- - The RAD module-entry script updates dbo.ivp_rad_module_details for SecMaster (module_id 3) and Ref Master (module_id 6), setting login URLs, service URL when RAD SSO is enabled, and API URL.
- - The script is intended to be run in the RAD database after replacing placeholders such as <server_name> and <database.environment>, and it instructs restarting the application afterward.
- - Potential script issue: the final IF block appears inconsistent because it checks module_id = 3 but updates module_id = 6; this should be validated before execution.
- - No direct FogBugz case match was found for an exact /CreateUsers endpoint failure; the closest confirmed evidence is the broader RAD user-creation failure pattern in FB798093 and FB853817.
- - No exact FogBugz match was found for the term SMTPY Notify; related SecMaster/RAD SMTP transport cases exist, but a dedicated test-connection feature was not confirmed from the retrieved sources.
- - Related SMTP transport cases identified: FB495335 (issue while setting up SMTP transport), FB774993 (not able to send mail with SMTP transport configuration), and FB1705046 (SMTP issue in SRM transport screen).

## Case references update
- FB1558316 — RAD Transport - RabbitMQ test connection failing. Status: Active. Root event says test connection failed from SRM Transport Configuration even though the same credentials worked from the RabbitMQ URL; later guidance was to try from inside the app server and use the latest SM version with RAD 1019.
- FB495335 — [BAAM][SecM 8.2]: Issue while setting up SMTP transport. Status: Resolved (Completed).
- FB774993 — Not able to send mail with SMTP Transport Configuration. Status: Closed (Completed).

## Agent Memory Update
- - FB1558316: RAD Transport - RabbitMQ test connection failing. Test connection from SRM transport configuration failed even though the same credentials worked externally; support advised testing access from inside the app server. Useful pattern for transport connectivity troubleshooting.
- - FB495335: [BAAM][SecM 8.2]: Issue while setting up SMTP transport. Confirms SecMaster has SMTP transport setup issues tracked in FogBugz.
- - FB774993: Not able to send mail with SMTP Transport Configuration. Confirms SMTP mail-sending failures are tracked in SecMaster Implementation Issues.
- - Security Master v15 transport configuration docs cover Transport Task setup and Transport Tasks configuration, including transport type, remote/local file paths, enabled state, and custom classes, but do not document a dedicated SMTP test-connection workflow.
- - Known workaround pattern for transport connectivity issues: validate from the same app server/environment where the application runs, not only from an external client.
- - No verified FogBugz or wiki source confirmed a feature named "SMTPY Notify"; treat it as unconfirmed or likely a typo/non-standard term.
- - Transport Task configuration in Security Master is used to move files from remote locations to the local application server and can include pre/post transport custom classes.
- - Workflow Inbox / Workflow Setup in Security Master are relevant when transport-related tasks are governed by workflows or notifications.
- - RAD module-entry script note: `dbo.ivp_rad_module_details` is used to register/update SecMaster and Ref Master URLs, and the script should be validated before execution because the final IF block appears inconsistent.

## Agent Memory Update
- - FB1558316: RAD Transport - RabbitMQ test connection failing. Test connection from SRM transport configuration failed even though the same credentials worked externally; support advised testing access from inside the app server. Useful pattern for transport connectivity troubleshooting.
- - FB495335: [BAAM][SecM 8.2]: Issue while setting up SMTP transport. Confirms SecMaster has SMTP transport setup issues tracked in FogBugz.
- - FB774993: Not able to send mail with SMTP Transport Configuration. Confirms SMTP mail-sending failures are tracked in SecMaster Implementation Issues.
- - Security Master v15 transport configuration docs cover Transport Task setup and Transport Tasks configuration, including transport type, remote/local file paths, enabled state, and custom classes, but do not document a dedicated SMTP test-connection workflow.
- - Known workaround pattern for transport connectivity issues: validate from the same app server/environment where the application runs, not only from an external client.
- - No verified FogBugz or wiki source confirmed a feature named "SMTPY Notify"; treat it as unconfirmed or likely a typo/non-standard term.
- - Transport Task configuration in Security Master is used to move files from remote locations to the local application server and can include pre/post transport custom classes.
- - Workflow Inbox / Workflow Setup in Security Master are relevant when transport-related tasks are governed by workflows or notifications.
- - RAD module-entry script note: `dbo.ivp_rad_module_details` is used to register/update SecMaster and Ref Master URLs, and the script should be validated before execution because the final IF block appears inconsistent.

## Wiki references update
- Wiki article 6890: 15. Task Manager — explains pipelines/task chains, adding blocks, publishing, running, and monitoring task status.
- Wiki article 4876: 13.1.10 Security Type Transport Task Configuration — documents transport task setup, transport details, custom classes, and on/off state.

## Agent Memory Update
- - FB1558316: RAD Transport - RabbitMQ test connection failing. Test connection from SRM transport configuration failed even though the same credentials worked externally; support advised testing access from inside the app server. Useful pattern for transport connectivity troubleshooting.
- - FB495335: [BAAM][SecM 8.2]: Issue while setting up SMTP transport. Confirms SecMaster has SMTP transport setup issues tracked in FogBugz.
- - FB774993: Not able to send mail with SMTP Transport Configuration. Confirms SMTP mail-sending failures are tracked in SecMaster Implementation Issues.
- - FB1705046: Antares - SMTP issue in SRM Transport screen; RAD-related transport/mail configuration case, useful as adjacent context.
- - No exact FogBugz match was found for the term “SMTPY Notify”; it appears to be a typo or non-standard term rather than a documented feature name.
- - No dedicated wiki/case workflow for SMTP transport “test connection” in SecMaster 8.2 was confirmed from the retrieved sources.
- - The RAD module-entry script updates `dbo.ivp_rad_module_details` for SecMaster (module_id 3) and Ref Master (module_id 6), setting login URLs, service URL when RAD SSO is enabled, and API URL.
- - The script is intended to be run in the RAD database after replacing placeholders such as `<server_name>` and `<database.environment>`, and it instructs restarting the application afterward.
- - Potential script issue: the final IF block appears inconsistent because it checks `module_id = 3` but updates `module_id = 6`; this should be validated before execution.
- - Security Master v15 transport configuration docs cover Transport Task setup and Transport Tasks configuration, including transport type, remote/local file paths, enabled state, and custom classes, but do not document a dedicated SMTP test-connection workflow.
- - Known workaround pattern for transport connectivity issues: validate from the same app server/environment where the application runs, not only from an external client.
- - Transport Task configuration in Security Master is used to move files from remote locations to the local application server and can include pre/post transport custom classes.
- - Workflow Inbox / Workflow Setup in Security Master are relevant when transport-related tasks are governed by workflows or notifications.
- - No direct FogBugz case match was found for an exact /CreateUsers endpoint failure; the closest confirmed evidence is the broader RAD user-creation failure pattern in FB798093 and FB853817.
- - FB798093: User creation failed from Security Master in SecMaster 8.2. Root cause was conflicting RAD control privilege IDs from an existing RAD database; fix delivered via latest fresh installer package and attached script; status Resolved (In Latest Patch).
- - FB853817: Unable to create/add users with RAD dependency. Status Resolved as Duplicate and closed; context case for the same SecMaster/RAD user-creation issue, with SecMaster 8.2 / RefMaster 3.2 / RAD 1019 noted.
- - FB495335 / FB774993 / FB1705046 are the best confirmed case references for SMTP/transport-related troubleshooting.
- - Security Master transport setup is documented in the Transport Task and Transport Tasks wiki articles; these are the best wiki sources for transport validation steps.
- - The user asked for SecMaster application restart instructions using StopApplication.exe and StartApplication.exe; these files are typically part of the deployed installer folder or application package.
- - No wiki source in the retrieved material explicitly documented a separate SecMaster backend authentication token flow beyond the previously known SessionId + DeviceKey pattern.
- - For SecMaster REST authentication, the known pattern is Login first, then use SessionId plus DeviceKey on subsequent API requests.
- - The user wants case details presented in timeline/event order and wants actual case IDs and confirmed findings called out rather than vague summaries.
- - The user prefers wiki-based answers grounded in IVP wiki sources for product/process questions, and prefers clear flow diagrams or Mermaid when explaining workflows.
- - The user prefers C# for code-generation requests involving IVP integrations, with clean architecture, modular code, proper authentication handling, and clear naming.

## Agent Memory Update
- - FB1558316: RAD Transport - RabbitMQ test connection failing. Test connection from SRM transport configuration failed even though the same credentials worked externally; support advised testing access from inside the app server. Useful pattern for transport connectivity troubleshooting.
- - FB495335: [BAAM][SecM 8.2]: Issue while setting up SMTP transport. Confirms SecMaster has SMTP transport setup issues tracked in FogBugz.
- - FB774993: Not able to send mail with SMTP Transport Configuration. Confirms SMTP mail-sending failures are tracked in SecMaster Implementation Issues.
- - FB1705046: Antares - SMTP issue in SRM Transport screen; RAD-related transport/mail configuration case, useful as adjacent context.
- - No exact FogBugz match was found for the term “SMTPY Notify”; it appears to be a typo or non-standard term rather than a documented feature name.
- - No dedicated wiki/case workflow for SMTP transport “test connection” in SecMaster 8.2 was confirmed from the retrieved sources.
- - Security Master v15 transport configuration docs cover Transport Task setup and Transport Tasks configuration, including transport type, remote/local file paths, enabled state, and custom classes, but do not document a dedicated SMTP test-connection workflow.
- - Transport Task configuration in Security Master is used to move files from remote locations to the local application server and can include pre/post transport custom classes.
- - Workflow Inbox / Workflow Setup in Security Master are relevant when transport-related tasks are governed by workflows or notifications.
- - For SecMaster REST authentication, the known pattern is Login first, then use SessionId plus DeviceKey on subsequent API requests.
- - The user wants case details presented in timeline/event order and wants actual case IDs and confirmed findings called out rather than vague summaries.
- - The user prefers wiki-based answers grounded in IVP wiki sources for product/process questions, and prefers clear flow diagrams or Mermaid when explaining workflows.
- - The user prefers C# for code-generation requests involving IVP integrations, with clean architecture, modular code, proper authentication handling, and clear naming.
- - FB798093: User creation failed from Security Master in SecMaster 8.2. Root cause was conflicting RAD control privilege IDs from an existing RAD database; fix delivered via latest fresh installer package and attached script; status Resolved (In Latest Patch).
- - FB853817: Unable to create/add users with RAD dependency. Status Resolved as Duplicate and closed; context case for the same SecMaster/RAD user-creation issue, with SecMaster 8.2 / RefMaster 3.2 / RAD 1019 noted.
- - The RAD module-entry script updates dbo.ivp_rad_module_details for SecMaster (module_id 3) and Ref Master (module_id 6), setting login URLs, service URL when RAD SSO is enabled, and API URL.
- - The script is intended to be run in the RAD database after replacing placeholders such as <server_name> and <database.environment>, and it instructs restarting the application afterward.
- - Potential script issue: the final IF block appears inconsistent because it checks module_id = 3 but updates module_id = 6; this should be validated before execution.

## Recent SecMaster authentication findings
- FB1918320: SecMaster / Azure AD integration request. Case history shows the request was for Azure AD sync task support; a hotfix for v8.2.B6 was offered, but the case does not document a full Microsoft SSO backend request sequence.
- FB615082: RAD SSO integration patch for SecMaster 8.2 / RefMaster 3.2 / RAD 1019. Resolution explicitly says to enable RAD single sign on in `ConfigFiles\\LoginConfig.xml` by setting `ssoenable=true`.
- FB474667: SSO not working case. Resolution was `AllowAutoLogin was not set to True in appSettings`, indicating login configuration matters, but the case does not describe an API auth handshake.
- Current evidence still supports standard session-based auth after login; exact Microsoft SSO request flow remains undocumented in retrieved sources.

## SecMaster Login endpoint request details
- Wiki article 3511 documents the exact REST Login request for SecMaster: POST http://localhost/SecMasterService/Login with JSON body containing DeviceKey, UserName, and Password.
- Wiki article 3495 confirms Login returns SessionId, which must be reused together with DeviceKey in headers for subsequent API calls.
- Wiki article 4301 confirms the same token-based pattern and additionally notes optional ClientKey and certificate-based encryption when 2FA / dual-factor authentication is enabled.
- No wiki source retrieved documented a Microsoft SSO-specific REST body for /Login; the documented API login remains username/password plus DeviceKey.

## SecMaster 8.2 API login documentation confirmed
- Confirmed SecMaster 8.0/v15 API auth docs: Login is a session-initiating call using DeviceKey, UserName, and Password; SessionId + DeviceKey are required on subsequent REST calls.
- Confirmed optional security add-ons: client certificate-based auth/message encryption, and ClientKey header when enabled.
- The docs do not show a Microsoft SSO-specific API login body; the documented API access pattern remains credential-based Login followed by token reuse.

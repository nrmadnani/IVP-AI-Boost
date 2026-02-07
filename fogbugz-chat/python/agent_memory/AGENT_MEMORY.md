
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


## SecMaster REST Endpoint Preference
SecMaster REST Endpoint (HTTP REST only)
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
- Example REST request:
  POST http://localhost/SecMasterService/SearchSecurities HTTP/1.1
  Content-Type: application/json
  <JSON body as above>
- Response: JSON with Data array containing SecurityDetailsResponseInfo (as shown in wiki)
- Purpose: REST-based search of securities across security types with filters and attributes
- Source: IVP Security Master wiki – Search/Browse Securities and API Access & Authentication
- Preference: Always return HTTP REST endpoints and REST examples for any APIs referenced in FogBugz documentation.
User prefers detailed Security Master 8.0 API documentation in all responses.

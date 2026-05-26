
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
- User preference: User uses EDM exclusively (prefer EDM-first answers).
- User preference: Always include flowchart diagrams using Mermaid when possible.
- User defines "Facilities" as synonym for "Securities" for future conversations.
- User preference: User needs to add updates to case 23111

## User Preferences Update
- Use the specialized Fogbugz Advanced Search Agent for FogBugz case searches.
- When asking about documentation, prefer wiki-based answers grounded in the IVP wiki sources.
- For reconciliation topics, explain from the wiki step by step and keep the explanation grounded in the documentation.

## User Preferences Update
- When asking for case details, the user wants a detailed event-by-event summary in timeline order.
- The user prefers wiki-grounded explanations for product/process questions.

## User Preferences Update
- {'preference': 'When asking for product or workflow explanations, the user prefers wiki-based answers with clear step-by-step summaries and flow diagrams.'}
- {'preference': 'When investigating FogBugz cases, the user prefers searches and summaries grounded in the case history and related documentation, not speculation.'}
- {'preference': 'The user values detailed chronological summaries of case events when reviewing a specific FogBugz case.'}

## User Preferences Update
- The user prefers answers grounded in wiki documentation when asking how IVP products/workflows work.
- The user prefers clear flow diagrams when explaining workflows.
- The user prefers detailed, step-by-step explanations for process questions.
- The user prefers C# implementations when requesting code generation examples.

## User Preferences Update
- When asking about product behavior or workflows, the user prefers answers grounded in wiki documentation.
- The user prefers clear flow diagrams (often Mermaid) when explaining workflows or multi-step processes.
- The user prefers C# for code-generation requests involving IVP integrations.
- The user prefers clean architecture, modular code, proper authentication handling, and clear naming in generated code.
- The user prefers the least manual / most efficient documented workflow when asking how to create or add multiple entities.
- The user prefers detailed, step-by-step summaries for case event timelines when asking about FogBugz cases.

## User Preferences Update
- The user prefers documentation-grounded answers when asking product/process questions.
- The user prefers clear, concise case summaries with event timelines when asking for case details.

## User Preferences Update
- The user prefers answers grounded in wiki documentation or case history rather than speculation.
- The user prefers clear, step-by-step explanations when asking how workflows or matching rules work.
- The user prefers diagrams or flowcharts when explaining processes.
- The user prefers concise but detailed case summaries with timeline/order of events when asking about FogBugz cases.
- The user prefers code examples in C# when asking for implementation help.
- The user prefers clean architecture, modular functions, and clear naming in generated code.
- The user prefers the least manual / most efficient documented workflow when asking how to perform a data-entry task.

## User Preferences Update
- When searching FogBugz, the user prefers step-by-step investigation and explicit use of the specialized advanced search agent for case searches.
- The user prefers wiki-backed explanations for product/how-to questions rather than unsupported general knowledge.
- The user prefers clear diagrams/flowcharts or Mermaid-style flow diagrams when explaining workflows.
- The user prefers detailed, chronological summaries for FogBugz case histories and event timelines.
- The user prefers concise, practical recommendations when asking for the best or least manual workflow.
- The user prefers code answers in C# when requesting implementation examples.
- The user prefers clean architecture, modular code, and explicit authentication handling in generated code.
- The user wants actual case IDs and resolved findings called out when available, rather than vague summaries.

## User Preferences Update
- When asking for case details, the user prefers timeline-style summaries and direct event-based evidence.
- When asking for a fix/workaround, the user prefers a step-by-step explanation and visual flow diagram.
- The user prefers answers grounded in FogBugz case history and wiki documentation rather than unsupported inference.
- The user prefers concise, practical recommendations for operational tasks (for example, choosing bulk upload over manual entry when appropriate).

## User Preferences Update
- Use the specialized Fogbugz Advanced Search Agent for FogBugz case searches.
- When asking about documentation, prefer wiki-based answers grounded in the IVP wiki sources.
- For reconciliation topics, explain from the wiki step by step and keep the explanation grounded in the documentation.
- When asking for case details, the user wants a detailed event-by-event summary in timeline order.
- The user prefers wiki-grounded explanations for product/process questions.
- The user prefers answers grounded in wiki documentation when asking how IVP products/workflows work.
- The user prefers clear flow diagrams when explaining workflows.
- The user prefers detailed, step-by-step explanations for process questions.
- The user prefers C# implementations when requesting code generation examples.
- The user prefers clean architecture, modular code, proper authentication handling, and clear naming in generated code.
- The user prefers the least manual / most efficient documented workflow when asking how to create or add multiple entities.
- The user prefers detailed, chronological summaries for FogBugz case histories and event timelines.
- The user prefers concise, practical recommendations when asking for the best or least manual workflow.
- The user wants actual case IDs and resolved findings called out when available, rather than vague summaries.
- When asking for a fix/workaround, the user prefers a step-by-step explanation and visual flow diagram.
- The user prefers answers grounded in FogBugz case history and wiki documentation rather than unsupported inference.

## User Preferences Update
- When creating or updating FogBugz cases, the user wants the assignee explicitly set once confirmed.
- The user prefers case details and edits to be handled concretely, with the exact note or summary added to the case when requested.
- The user prefers direct, action-oriented FogBugz case management rather than speculative discussion.

## User Preferences Update
- {'preference': 'Use the specialized Fogbugz Advanced Search Agent for FogBugz case searches.'}
- {'preference': 'When asking about documentation, prefer wiki-based answers grounded in the IVP wiki sources.'}
- {'preference': 'For reconciliation topics, explain from the wiki step by step and keep the explanation grounded in the documentation.'}
- {'preference': 'When asking for case details, the user wants a detailed event-by-event summary in timeline order.'}
- {'preference': 'The user prefers wiki-grounded explanations for product/process questions.'}
- {'preference': 'When asking for product or workflow explanations, the user prefers wiki-based answers with clear step-by-step summaries and flow diagrams.'}
- {'preference': 'When investigating FogBugz cases, the user prefers searches and summaries grounded in the case history and related documentation, not speculation.'}
- {'preference': 'The user values detailed chronological summaries of case events when reviewing a specific FogBugz case.'}
- {'preference': 'The user prefers C# implementations when requesting code generation examples.'}
- {'preference': 'The user prefers clean architecture, modular code, proper authentication handling, and clear naming in generated code.'}
- {'preference': 'The user prefers the least manual / most efficient documented workflow when asking how to create or add multiple entities.'}
- {'preference': 'When asking for case details, the user prefers timeline-style summaries and direct event-based evidence.'}
- {'preference': 'When asking for a fix/workaround, the user prefers a step-by-step explanation and visual flow diagram.'}
- {'preference': 'The user wants actual case IDs and resolved findings called out when available, rather than vague summaries.'}
- {'preference': 'When asking about product behavior or workflows, the user prefers answers grounded in wiki documentation.'}
- {'preference': 'The user prefers clear flow diagrams (often Mermaid) when explaining workflows or multi-step processes.'}
- {'preference': 'The user prefers C# for code-generation requests involving IVP integrations.'}
- {'preference': 'The user prefers clean architecture, modular code, and explicit authentication handling in generated code.'}
- {'preference': 'The user prefers concise, practical recommendations when asking for the best or least manual workflow.'}

## User Preferences Update
- - The user wants case details presented in timeline/event order.
- - The user prefers concise but practical operational guidance when working in FogBugz.
- - The user prefers actual case IDs and confirmed findings rather than vague summaries.

## User Preferences Update
- - When asking for case details, the user prefers timeline-style summaries and direct event-based evidence.
- - When asking for a fix/workaround or case update, the user prefers a step-by-step explanation before changes are applied.
- - The user prefers concise, practical recommendations for operational tasks.
- - The user wants actual case IDs and resolved findings called out when available, rather than vague summaries.

## User Preferences Update
- When creating or updating FogBugz cases, the user wants a step-by-step approval flow before changes are applied.
- The user prefers case updates to reflect the exact operational context, including patch/version notes when relevant.
- For FogBugz notifications, the user is willing to use forwarding when direct email is not permitted.
- The user prefers the assigned recipient to be a specific named person when creating or updating a case.

## User Preferences Update
- - When asking for case details, the user prefers timeline-style summaries and direct event-based evidence.
- - When asking for a fix/workaround or case follow-up, the user prefers concise, practical operational actions rather than speculation.
- - The user prefers answers grounded in FogBugz case history rather than unsupported inference.

## User Preferences Update
- Use the specialized Fogbugz Advanced Search Agent for FogBugz case searches.
- When asking about documentation, prefer wiki-based answers grounded in IVP wiki sources.
- For reconciliation topics, explain from the wiki step by step and keep the explanation grounded in the documentation.
- When asking for case details, provide a detailed event-by-event summary in timeline order.
- Prefer wiki-grounded explanations for product/process questions.
- Prefer clear flow diagrams, often in Mermaid, when explaining workflows.
- Prefer C# implementations for code-generation examples involving IVP integrations.
- Prefer clean architecture, modular code, proper authentication handling, and clear naming in generated code.
- Prefer the least manual / most efficient documented workflow when asking how to create or add multiple entities.
- Prefer concise but detailed case summaries with timeline/order of events when asking about FogBugz cases.
- Prefer answers grounded in FogBugz case history and wiki documentation rather than unsupported inference.
- Want actual case IDs and resolved findings called out when available, rather than vague summaries.
- Prefer step-by-step investigation when searching FogBugz and want explicit use of the advanced search agent.
- Prefer concise, practical recommendations for operational tasks such as choosing bulk upload over manual entry when appropriate.
- Prefer direct event-based evidence and timeline-style summaries for FogBugz case histories.

## User Preferences Update
- - Use the specialized Fogbugz Advanced Search Agent for FogBugz case searches.
- - When asking about documentation, prefer wiki-based answers grounded in the IVP wiki sources.
- - For reconciliation topics, explain from the wiki step by step and keep the explanation grounded in the documentation.
- - When asking for case details, the user wants a detailed event-by-event summary in timeline order.
- - The user prefers wiki-grounded explanations for product/process questions.
- - When asking for product or workflow explanations, the user prefers wiki-based answers with clear step-by-step summaries and flow diagrams.
- - When investigating FogBugz cases, the user prefers searches and summaries grounded in the case history and related documentation, not speculation.
- - The user values detailed chronological summaries of case events when reviewing a specific FogBugz case.
- - The user prefers answers grounded in wiki documentation when asking how IVP products/workflows work.
- - The user prefers clear flow diagrams when explaining workflows.
- - The user prefers detailed, step-by-step explanations for process questions.
- - The user prefers C# implementations when requesting code generation examples.
- - The user prefers clean architecture, modular code, proper authentication handling, and clear naming in generated code.
- - The user prefers the least manual / most efficient documented workflow when asking how to create or add multiple entities.
- - The user prefers documentation-grounded answers when asking product/process questions.
- - The user prefers concise, clear case summaries with event timelines when asking for case details.
- - The user prefers answers grounded in wiki documentation or case history rather than speculation.
- - The user prefers diagrams or flowcharts when explaining processes.
- - The user prefers concise but detailed case summaries with timeline/order of events when asking about FogBugz cases.
- - The user prefers code examples in C# when asking for implementation help.
- - The user prefers clean architecture, modular functions, and clear naming in generated code.
- - The user prefers the least manual / most efficient documented workflow when asking how to perform a data-entry task.
- - When searching FogBugz, the user prefers step-by-step investigation and explicit use of the specialized advanced search agent for case searches.
- - The user prefers clear diagrams/flowcharts or Mermaid-style flow diagrams when explaining workflows.
- - The user prefers concise, practical recommendations when asking for the best or least manual workflow.
- - The user wants actual case IDs and resolved findings called out when available, rather than vague summaries.
- - When asking for case details, the user prefers timeline-style summaries and direct event-based evidence.
- - When asking for a fix/workaround, the user prefers a step-by-step explanation and visual flow diagram.

## User Preferences Update
- The user prefers wiki-based, documentation-grounded answers for IVP product/workflow questions.
- The user prefers clear step-by-step explanations for workflow and process questions.
- The user prefers flow diagrams or Mermaid when explaining multi-step workflows.
- The user prefers concise, practical examples such as sample schemas when asking for templates or formats.

## User Preferences Update
- - The user prefers wiki-based answers grounded in IVP wiki sources when asking documentation or workflow questions.
- - The user prefers answers grounded in wiki documentation or case history rather than speculation.
- - The user prefers clear flow diagrams, often in Mermaid, when explaining workflows or multi-step processes.
- - The user prefers concise but practical guidance for operational tasks.
- - The user prefers step-by-step summaries for workflow/process explanations.

## User Preferences Update
- The user prefers wiki-based answers grounded in IVP wiki sources when asking about product/process behavior.
- The user prefers clear, practical explanations for workflows and template usage.
- The user prefers sample schemas or concrete examples when asking about data formats.
- The user prefers concise answers that explicitly state when a requested article or finding was not found.

## User Preferences Update
- {'preference': 'The user prefers wiki-based answers grounded in IVP wiki sources when asking about product/process behavior.'}
- {'preference': 'The user prefers step-by-step explanations and flow diagrams for workflow or multi-step process questions.'}
- {'preference': 'The user prefers practical, template-driven guidance for bulk update tasks rather than speculative fixed schemas.'}
- {'preference': 'The user prefers searching FogBugz and wiki sources when investigating IVP/Security Master questions.'}

## User Preferences Update
- When asking about documentation, prefer wiki-based answers grounded in the IVP wiki sources.
- The user prefers answers grounded in wiki documentation when asking how IVP products/workflows work.
- The user prefers the least manual / most efficient documented workflow when asking how to create or add multiple entities.
- The user prefers concise, practical recommendations when asking for the best or least manual workflow.
- The user prefers clear flow diagrams, often in Mermaid, when explaining workflows or multi-step processes.
- When asked about bulk updating reference data, always reference wiki article 4632 (6.2 Bulk Creation of Reference Data) as the primary source.

## User Preferences Update
- The user wants case details presented in timeline/event order and wants actual case IDs and confirmed findings called out rather than vague summaries.
- The user prefers wiki-based answers grounded in IVP wiki sources for product/process questions.
- The user prefers clear flow diagrams or Mermaid when explaining workflows.
- The user prefers C# for code-generation requests involving IVP integrations.
- The user wants reference-data bulk Excel templates to be template-driven and to use actual attribute names as column headers.
- The user wants the selected Unique Key included as one of the columns in bulk reference-data Excel files.
- The user specifically wants bulk reference-data guidance to be grounded in wiki article 4632 when relevant.
- The user wants the WSO Issuer Name bulk-update Excel schema to be derived from the documented bulk-creation rules rather than a generic schema.

## User Preferences Update
- When asking for FogBugz case details, the user prefers detailed event-by-event summaries in timeline order.
- The user prefers actual case IDs and confirmed findings to be called out rather than vague summaries.
- The user prefers answers grounded in case history and documentation rather than speculation.
- The user prefers clear, step-by-step explanations for scripts and workflow/process questions.
- The user prefers flow diagrams or Mermaid when explaining multi-step processes.
- The user prefers wiki-based answers grounded in IVP sources for product/workflow questions.

## User Preferences Update
- The user prefers timeline-style summaries and direct event-based evidence when asking for FogBugz case details.
- The user prefers answers grounded in FogBugz case history and wiki/documentation rather than unsupported inference.
- The user prefers clear, practical explanations for scripts and workflows, including step-by-step breakdowns.
- The user values identification of possible script issues or oddities before execution.

## User Preferences Update
- When asking for case details, the user prefers a detailed event-by-event summary in timeline order.
- The user prefers actual case IDs and confirmed findings called out rather than vague summaries.
- The user prefers answers grounded in FogBugz case history and wiki documentation rather than unsupported inference.
- When searching FogBugz, the user prefers step-by-step investigation and explicit use of the specialized advanced search agent.
- When asking for workflow/process explanations, the user prefers clear flow diagrams or Mermaid when possible.
- The user prefers concise, practical recommendations for operational tasks.
- When creating or updating FogBugz cases, the user wants the assignee explicitly set once confirmed.
- The user prefers case updates to reflect the exact operational context, including patch/version notes when relevant.

## User Preferences Update
- When asking for case details, the user prefers a detailed event-by-event summary in timeline order.
- The user prefers wiki-based answers grounded in IVP wiki sources for product/process questions.
- The user prefers clear flow diagrams or Mermaid when explaining workflows.
- The user prefers C# for code-generation requests involving IVP integrations.
- The user wants actual case IDs and confirmed findings called out rather than vague summaries.
- The user prefers answers grounded in FogBugz case history and wiki documentation rather than unsupported inference.
- The user prefers concise, practical recommendations for operational tasks.
- The user prefers step-by-step investigation when searching FogBugz and wants explicit use of the specialized advanced search agent for case searches.

## User Preferences Update
- When asking for case details, the user wants a detailed event-by-event summary in timeline order.
- The user prefers wiki-based answers grounded in IVP wiki sources for product/process questions.
- The user prefers clear flow diagrams or Mermaid when explaining workflows.
- The user prefers C# for code-generation requests involving IVP integrations, with clean architecture, modular code, proper authentication handling, and clear naming.
- The user wants actual case IDs and confirmed findings called out rather than vague summaries.
- The user prefers answers grounded in FogBugz case history and wiki documentation rather than unsupported inference.
- When investigating FogBugz cases, the user prefers searches and summaries grounded in the case history and related documentation, not speculation.
- When asking about documentation, prefer wiki-based answers grounded in the IVP wiki sources.
- Use the specialized Fogbugz Advanced Search Agent for FogBugz case searches.
- For reference-data bulk uploads in Security Master, the correct Excel file is template-driven: column headers must be the actual attribute names, and the selected Unique Key must be included as one of the columns.
- When asked about bulk updating reference data, always reference wiki article 4632 (6.2 Bulk Creation of Reference Data) as the primary source.
- The user prefers concise, practical recommendations for operational tasks such as choosing bulk upload over manual entry when appropriate.
- The user prefers timeline-style summaries and direct event-based evidence for FogBugz case histories.

## User Preferences Update
- {'preference': 'Use the specialized Fogbugz Advanced Search Agent for FogBugz case searches.'}
- {'preference': 'When asking about documentation, prefer wiki-based answers grounded in the IVP wiki sources.'}
- {'preference': 'Prefer wiki-grounded explanations for product/process questions.'}
- {'preference': 'Prefer clear flow diagrams, often in Mermaid, when explaining workflows or multi-step processes.'}
- {'preference': 'Prefer answers grounded in FogBugz case history and wiki documentation rather than unsupported inference.'}
- {'preference': 'Prefer concise, practical recommendations for operational tasks such as choosing bulk upload over manual entry when appropriate.'}
- {'preference': 'Want actual case IDs and resolved findings called out when available, rather than vague summaries.'}

## User Preferences Update
- - The user prefers wiki-based, documentation-grounded answers for IVP product/workflow questions.
- - The user prefers answers grounded in FogBugz case history rather than unsupported inference.
- - The user prefers clear, step-by-step explanations for workflow and process questions.
- - The user prefers clear flow diagrams or Mermaid when explaining workflows or multi-step processes.
- - The user prefers concise, practical recommendations for operational tasks.
- - The user wants actual case IDs and confirmed findings called out when available, rather than vague summaries.
- - The user prefers timeline-style summaries and direct event-based evidence when asking for FogBugz case details.
- - The user prefers the specialized Fogbugz Advanced Search Agent for FogBugz case searches.
- - The user prefers concise but detailed case summaries with timeline/order of events when asking about FogBugz cases.
- - The user prefers practical, template-driven guidance for bulk update tasks rather than speculative fixed schemas.

## User Preferences Update
- When asking for case details, the user wants actual case IDs and confirmed findings called out rather than vague summaries.
- The user prefers wiki-based answers grounded in IVP wiki sources for product/process questions.
- The user prefers clear flow diagrams or Mermaid when explaining workflows or multi-step processes.
- The user prefers C# for code-generation requests involving IVP integrations.
- The user prefers answers grounded in FogBugz case history and wiki documentation rather than unsupported inference.
- The user prefers concise, practical recommendations for operational tasks.
- The user wants exact script or configuration details explained in plain English.
- The user prefers step-by-step explanations when asking how workflows, transport tasks, or configuration validation work.
- The user wants the relevant product names explicitly identified when troubleshooting issues across modules.

## User Preferences Update
- When asking for product or workflow explanations, the user prefers wiki-based answers with clear step-by-step summaries and flow diagrams.
- When investigating FogBugz cases, the user prefers searches and summaries grounded in the case history and related documentation, not speculation.
- The user values detailed chronological summaries of case events when reviewing a specific FogBugz case.
- The user prefers C# implementations when requesting code generation examples.
- The user prefers clean architecture, modular code, proper authentication handling, and clear naming in generated code.
- The user prefers the least manual / most efficient documented workflow when asking how to create or add multiple entities.
- When asking for case details, the user prefers timeline-style summaries and direct event-based evidence.
- When asking for a fix/workaround, the user prefers a step-by-step explanation and visual flow diagram.
- The user wants actual case IDs and resolved findings called out when available, rather than vague summaries.
- When asking about product behavior or workflows, the user prefers answers grounded in wiki documentation.
- The user prefers clear flow diagrams (often Mermaid) when explaining workflows or multi-step processes.
- When searching FogBugz, the user prefers step-by-step investigation and explicit use of the specialized advanced search agent for case searches.
- The user prefers concise, practical recommendations when asking for the best or least manual workflow.
- The user prefers concise but practical operational guidance when working in FogBugz.
- The user wants case details presented in timeline/event order and wants actual case IDs and confirmed findings called out rather than vague summaries.
- The user prefers wiki-based answers grounded in IVP wiki sources for product/process questions.
- The user explicitly wants the WSO Issuer Name bulk-update Excel schema to be based on wiki article 4632 rather than a generic template.
- The user stated that if they ever ask about bulk updating reference data, the referenced article should be remembered.
- The user prefers wiki-based answers grounded in IVP wiki sources when asking about product/process behavior.
- The user prefers step-by-step explanations and flow diagrams for workflow or multi-step process questions.
- The user prefers practical, template-driven guidance for bulk update tasks rather than speculative fixed schemas.
- The user prefers searching FogBugz and wiki sources when investigating IVP/Security Master questions.
- The user prefers wiki-based answers grounded in IVP wiki sources when asking about product/process behavior.
- The user prefers step-by-step explanations and flow diagrams for workflow or multi-step process questions.
- The user prefers practical, template-driven guidance for bulk update tasks rather than speculative fixed schemas.
- The user prefers searching FogBugz and wiki sources when investigating IVP/Security Master questions.
- The user wants case details presented in timeline/event order and wants actual case IDs and confirmed findings called out rather than vague summaries.
- The user prefers wiki-based answers grounded in IVP wiki sources for product/process questions.
- The user prefers clear flow diagrams or Mermaid when explaining workflows.
- The user prefers C# for code-generation requests involving IVP integrations.
- The user wants reference-data bulk Excel templates to be template-driven and to use actual attribute names as column headers.
- The user wants the selected Unique Key included as one of the columns in bulk reference-data Excel files.
- The user specifically wants bulk reference-data guidance to be grounded in wiki article 4632 when relevant.
- The user wants the WSO Issuer Name bulk-update Excel schema to be derived from the documented bulk-creation rules rather than a generic schema.
- Use the specialized Fogbugz Advanced Search Agent for FogBugz case searches.
- When asking about documentation, prefer wiki-based answers grounded in the IVP wiki sources.
- For reconciliation topics, explain from the wiki step by step and keep the explanation grounded in the documentation.
- When asking for case details, the user wants a detailed event-by-event summary in timeline order.
- The user prefers wiki-grounded explanations for product/process questions.
- The user prefers answers grounded in wiki documentation when asking how IVP products/workflows work.
- The user prefers clear flow diagrams when explaining workflows.
- The user prefers detailed, step-by-step explanations for process questions.
- The user prefers C# implementations when requesting code generation examples.
- The user prefers clean architecture, modular code, proper authentication handling, and clear naming in generated code.
- The user prefers the least manual / most efficient documented workflow when asking how to create or add multiple entities.
- The user prefers detailed, chronological summaries for FogBugz case histories and event timelines.
- The user prefers concise, practical recommendations when asking for the best or least manual workflow.
- The user wants actual case IDs and resolved findings called out when available, rather than vague summaries.
- When asking for a fix/workaround, the user prefers a step-by-step explanation and visual flow diagram.
- The user prefers answers grounded in FogBugz case history and wiki documentation rather than unsupported inference.
- When creating or updating FogBugz cases, the user wants the assignee explicitly set once confirmed.
- The user prefers case details and edits to be handled concretely, with the exact note or summary added to the case when requested.
- The user prefers direct, action-oriented FogBugz case management rather than speculative discussion.
- Use the specialized Fogbugz Advanced Search Agent for FogBugz case searches.
- When asking about documentation, prefer wiki-based answers grounded in the IVP wiki sources.
- For reconciliation topics, explain from the wiki step by step and keep the explanation grounded in the documentation.
- When asking for case details, provide a detailed event-by-event summary in timeline order.
- Prefer wiki-grounded explanations for product/process questions.
- Prefer clear flow diagrams, often in Mermaid, when explaining workflows.
- Prefer C# implementations for code-generation examples involving IVP integrations.
- Prefer clean architecture, modular code, proper authentication handling, and clear naming in generated code.
- Prefer the least manual / most efficient documented workflow when asking how to create or add multiple entities.
- Prefer concise but detailed case summaries with timeline/order of events when asking about FogBugz cases.
- Prefer answers grounded in FogBugz case history and wiki documentation rather than unsupported inference.
- Want actual case IDs and resolved findings called out when available, rather than vague summaries.
- Prefer step-by-step investigation when searching FogBugz and want explicit use of the advanced search agent.
- Prefer concise, practical recommendations for operational tasks such as choosing bulk upload over manual entry when appropriate.
- Prefer direct event-based evidence and timeline-style summaries for FogBugz case histories.
- The user prefers wiki-based, documentation-grounded answers for IVP product/workflow questions.
- The user prefers clear step-by-step explanations for workflow and process questions.
- The user prefers flow diagrams or Mermaid when explaining multi-step workflows.
- The user prefers concise, practical examples such as sample schemas when asking for templates or formats.
- The user prefers wiki-based answers grounded in IVP wiki sources when asking documentation or workflow questions.
- The user prefers answers grounded in wiki documentation or case history rather than speculation.
- The user prefers clear flow diagrams, often in Mermaid, when explaining workflows or multi-step processes.
- The user prefers concise but practical guidance for operational tasks.
- The user prefers step-by-step summaries for workflow/process explanations.
- The user prefers wiki-based answers grounded in IVP wiki sources when asking about product/process behavior.
- The user prefers clear, practical explanations for workflows and template usage.
- The user prefers sample schemas or concrete examples when asking about data formats.
- The user prefers concise answers that explicitly state when a requested article or finding was not found.
- When asking about documentation, prefer wiki-based answers grounded in the IVP wiki sources.
- The user prefers answers grounded in wiki documentation when asking how IVP products/workflows work.
- The user prefers the least manual / most efficient documented workflow when asking how to create or add multiple entities.
- The user prefers concise, practical recommendations when asking for the best or least manual workflow.
- The user prefers clear flow diagrams, often in Mermaid, when explaining workflows or multi-step processes.
- When asked about bulk updating reference data, always reference wiki article 4632 (6.2 Bulk Creation of Reference Data) as the primary source.
- The user wants case details presented in timeline/event order and wants actual case IDs and confirmed findings called out rather than vague summaries.
- The user prefers wiki-based answers grounded in IVP wiki sources for product/process questions.
- The user prefers clear flow diagrams or Mermaid when explaining workflows.
- The user prefers C# for code-generation requests involving IVP integrations.
- The user wants reference-data bulk Excel templates to be template-driven and to use actual attribute names as column headers.
- The user wants the selected Unique Key included as one of the columns in bulk reference-data Excel files.
- The user specifically wants bulk reference-data guidance to be grounded in wiki article 4632 when relevant.
- The user wants the WSO Issuer Name bulk-update Excel schema to be derived from the documented bulk-creation rules rather than a generic schema.
- The user prefers step-by-step guidance and practical checklists for transport and authentication troubleshooting.
- The user wants exact product ownership called out when a transport or auth issue spans SecMaster, RAD, RefMaster, or SRM.
- The user prefers operational restart instructions to identify the application server / installer folder where the control EXEs live.
- The user prefers not to infer undocumented features; if a term or workflow is not found in FogBugz/wiki, explicitly say so.
- The user prefers the known SecMaster REST auth pattern of Login first, then SessionId + DeviceKey on subsequent requests.

## User Preferences Update
- Use the specialized Fogbugz Advanced Search Agent for FogBugz case searches.
- When asking about documentation, prefer wiki-based answers grounded in the IVP wiki sources.
- For reconciliation topics, explain from the wiki step by step and keep the explanation grounded in the documentation.
- When asking for case details, the user wants a detailed event-by-event summary in timeline order.
- The user prefers wiki-grounded explanations for product/process questions.
- The user prefers clear flow diagrams when explaining workflows.
- The user prefers C# implementations when requesting code generation examples.
- The user prefers clean architecture, modular code, proper authentication handling, and clear naming in generated code.
- The user prefers the least manual / most efficient documented workflow when asking how to create or add multiple entities.
- The user prefers concise but practical operational guidance for FogBugz and workflow tasks.
- The user wants actual case IDs and confirmed findings called out rather than vague summaries.
- The user prefers answers grounded in FogBugz case history and wiki documentation rather than unsupported inference.
- The user prefers practical, template-driven guidance for bulk update tasks rather than speculative fixed schemas.
- When asking about product behavior or workflows, the user prefers answers grounded in wiki documentation.
- The user prefers step-by-step explanations and flow diagrams for workflow or multi-step process questions.
- The user prefers concise, practical recommendations when asking for the best or least manual workflow.
- The user prefers to be told explicitly when a requested article or feature was not found in the retrieved sources.
- The user wants reference-data bulk Excel templates to be template-driven and to use actual attribute names as column headers.
- The user wants the selected Unique Key included as one of the columns in bulk reference-data Excel files.
- When asked about bulk updating reference data, always reference wiki article 4632 (6.2 Bulk Creation of Reference Data) as the primary source.

## User Preferences Update
- {'preference': 'When asking about documentation or product behavior, the user prefers wiki-based, documentation-grounded answers rather than speculation.'}
- {'preference': 'When investigating FogBugz cases, the user prefers searches and summaries grounded in case history and related documentation.'}
- {'preference': 'When asking for case details, the user prefers timeline-style, event-based summaries with actual case IDs and confirmed findings.'}
- {'preference': 'The user prefers clear, practical explanations and step-by-step flow when discussing authentication or workflow behavior.'}

## User Preferences Update
- When asking about documentation or product/workflow behavior, prefer wiki-based answers grounded in IVP wiki sources.
- When investigating FogBugz cases, prefer searches and summaries grounded in case history and related documentation, not speculation.
- When asking for case details, prefer detailed event-by-event summaries in timeline order and actual case IDs.
- Prefer clear flow diagrams or Mermaid when explaining workflows or multi-step processes.
- Prefer concise but practical guidance for operational tasks.
- Prefer not to infer undocumented features; explicitly state when a term, article, or workflow is not found in the retrieved sources.
- For SecMaster REST authentication, prefer the known pattern: Login first, then SessionId + DeviceKey on subsequent requests.
- Prefer step-by-step explanations for workflow and authentication questions.

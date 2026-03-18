---
name: code-generation-skill
description: >
  Use this skill whenever the user wants to generate code, API wrappers, REST endpoint collections,
  or integration examples based on IVP FogBugz product documentation. Triggers include: any request
  to generate code in a specific language (Python, C#, Java, JavaScript, etc.) that interacts with
  IVP products, requests for Postman collections or REST/HTTP endpoint listings, requests like
  "generate Python code for X product", "give me the API calls for Y feature", "create a Postman
  collection for Z", "show me how to call the API for [product/feature]", or any request that
  involves turning documentation into runnable code. Always use this skill when the user mentions
  a product name alongside code, endpoints, API, or integration — even if phrased casually.
---

# code-generation-skill

## Overview

This skill enables the agent to autonomously research IVP product documentation stored in
FogBugz and synthesize clean, runnable output — either as **language-specific code**
(Python, JavaScript, Java, C#, etc.) or as a **Postman collection JSON** — based on a single
user prompt. The agent must work through the entire research-to-output pipeline with minimal
user interaction.

The agent has a **rich set of MCP tools** available and must use them intelligently and in
combination. Documentation is not always neatly organised in a single wiki; it may be spread
across wiki articles, case events, tagged items, or project areas. Deep discovery requires
reasoning about which tools to use and in what order.

---

## Available MCP Tools — Full Reference

Understand every tool, when to use it alone, and when to combine it with others.

---

### `list_wikis`
**Purpose:** Returns all wiki spaces in FogBugz (name, wiki_id, tagline, root_page_id).

**Use when:** You need to discover what documentation spaces exist, or map a product name to a wiki_id before listing or reading articles.

**Standalone example:**
> User asks: "Generate Python code for the Cerberus trading API."
> → Call `list_wikis` → find wiki named "Cerberus" or similar → extract `wiki_id` → proceed to `list_articles`.

**Combination example:**
> `list_wikis` → `list_articles(wiki_id)` → `view_article(article_id)`
> This is the standard wiki documentation pipeline. Always start here when the user names a product that is likely to have a dedicated wiki.

---

### `list_articles`
**Purpose:** Lists all articles within a given wiki (article_id, description, wiki_page).

**Use when:** You have a `wiki_id` from `list_wikis` and need to discover which articles cover the feature the user is asking about.

**Standalone example:**
> After identifying wiki_id=14 for "EDM Client Services", call `list_articles(wiki_id=14)` to see all available documentation pages and identify which ones cover authentication, endpoints, or data submission.

**Combination example:**
> `list_wikis` → `list_articles` → scan returned titles for keywords like "API", "endpoint", "integration", "auth", "upload", the user's feature term → `view_article` only on relevant matches.
> Do NOT call `view_article` on every article blindly. Prioritise based on title relevance.

---

### `view_article`
**Purpose:** Retrieves the full content of a specific wiki article (title, content, revision, tags).

**Use when:** You have identified a relevant `article_id` from `list_articles` (or from a cross-reference inside another article).

**Standalone example:**
> You already know article_id=302 is the "Trade Submission API" article. Call `view_article(302)` directly.

**Combination example:**
> When reading an article, look for cross-references like "see Authentication Guide" or "refer to article #215". 
> Follow those with additional `view_article` calls — documentation often spans multiple linked pages.
> Also check the `tags` field returned: matching tags can be searched with `list_tags` to find related articles across other wikis.

---

### `advanced_search`
**Purpose:** Executes a native FogBugz full-text search using structured query syntax. Returns matching cases with metadata.

**Use when:**
- A product name does not clearly map to a wiki (no obvious match from `list_wikis`)
- You need to find documentation or context buried in cases rather than wiki articles
- You want to discover endpoint details that were described in a support case, bug report, or feature request
- You are cross-referencing functionality across multiple projects or areas

**Standalone example:**
> User asks about "position reporting in EDM". Call:
> `advanced_search(query='Project:"EDM Client Services" position reporting API')`
> This surfaces cases where position reporting and API are discussed, even if no wiki article is dedicated to it.

**Combination example:**
> `list_wikis` finds no wiki matching "Varde". 
> → `advanced_search(query='Varde API endpoint')` → surfaces cases referencing Varde API work
> → `get_events_of_a_case(case_id)` on promising results → extract endpoint details from case discussion
>
> Another pattern:
> `list_articles(wiki_id)` finds an article titled "Authentication" but you also want cases where auth bugs were reported.
> → `advanced_search(query='Project:Cerberus authentication token endpoint')` alongside `view_article` for the same topic, then merge findings.

**Key syntax to use:**
```
Project:'Product Name'          — scope to a specific project
Area:'Area Name'                — scope to a specific area
Title:'keyword'                 — search case titles
Tag:'tag-name'                  — find cases with a specific tag
Status:open / Status:closed
Category:Bug / Category:Feature / Category:Inquiry
edited:"last month"             — recency filter
```

---

### `list_projects`
**Purpose:** Lists all active FogBugz projects (project_id, name).

**Use when:**
- You need to verify whether a product name corresponds to a FogBugz project (vs. a wiki)
- You want to enumerate all areas within a product using `list_areas`
- You are disambiguating between similarly named products

**Standalone example:**
> User asks about "400 Capital". Call `list_projects` to confirm the exact project name and get its project_id.

**Combination example:**
> `list_projects` → find project_id for "Cerberus" → `list_areas(project_id)` → discover that "EDM" is an area within Cerberus → `advanced_search(query='Project:Cerberus Area:EDM API')` for targeted case discovery.

---

### `list_areas`
**Purpose:** Lists all areas within a given project (area_id, area name, ownership metadata).

**Use when:**
- A product has multiple functional sub-areas and the user is asking about a specific one
- You want to scope your `advanced_search` query to a precise area
- You need to understand the structure of a large project before deciding where to look

**Standalone example:**
> `list_areas(project_id=7)` → returns ["EDM", "Reconciliation", "Trade Blotter", "Reporting"] 
> → user asked about "trade blotter", so scope all further searches to `Area:'Trade Blotter'`.

**Combination example:**
> `list_projects` → get project_id → `list_areas(project_id)` → identify relevant area → 
> `advanced_search(query='Project:"Cerberus" Area:"Trade Blotter" endpoint')` → 
> `get_events_of_a_case` on surfaced cases.

---

### `list_tags`
**Purpose:** Lists all tags in FogBugz with usage counts (tag_id, name, usage_count).

**Use when:**
- You are not sure where documentation lives and want to discover it through keyword/tag mapping
- An article's `tags` field references a tag you want to expand into related articles or cases
- You want to find all cases/articles marked with tags like "api", "integration", "endpoint", etc.

**Standalone example:**
> Call `list_tags` and look for tags like `api`, `rest`, `integration`, `endpoint`, `authentication`.
> High usage counts on these tags indicate active documentation areas.

**Combination example:**
> `view_article(305)` returns tags: ["authentication", "token", "cerberus-api"]
> → `list_tags` to confirm "cerberus-api" tag exists and its usage_count
> → `advanced_search(query='Tag:"cerberus-api"')` to find all cases and articles sharing that tag
> → `get_events_of_a_case` or `view_article` on the newly discovered items.

---

### `search_cases_by_project_and_area`
**Purpose:** Searches cases using human-readable project and area names (no need to resolve IDs first).

**Use when:**
- You know both the project name and area name clearly
- You want a fast path to cases without first resolving IDs via `list_projects` + `list_areas`

**Standalone example:**
> `search_cases_by_project_and_area(project_name="Cerberus", area_name="EDM")`
> → Returns all relevant cases in Cerberus/EDM, useful for spotting API documentation in case discussions.

**Combination example:**
> `search_cases_by_project_and_area("400 Capital", "Reporting")` → get case list →
> scan titles for "API", "endpoint", "integration" → `get_events_of_a_case(case_id)` on promising results.

---

### `get_events_of_a_case`
**Purpose:** Returns the full event history of a single case — all comments, updates, status changes, who did what and when.

**Use when:**
- A case title suggests it contains API or endpoint discussion and you need the details
- An article references a specific case number for further context
- You found a case via `advanced_search` or `search_cases_by_project_and_area` and want to extract technical detail from the conversation

**Standalone example:**
> `advanced_search` returns case #4821 titled "EDM Position API — new endpoint for bulk upload".
> → `get_events_of_a_case("4821")` → read through events to extract the endpoint path, request schema, and auth headers discussed in the thread.

**Combination example:**
> `list_wikis` → no relevant wiki found → `advanced_search(query='Product X API authentication')` →
> top result is case #3310 → `get_events_of_a_case("3310")` → extract endpoint and payload details
> from the case discussion → use these as the basis for generated code.

---

### `list_filters` + `list_cases`
**Purpose:** `list_filters` returns saved project-level filters; `list_cases(filter_id)` returns all cases under that filter (up to 10,000).

**Use when:**
- The user's request is broad ("tell me everything about the 400 Capital API")
- You need a full inventory of cases for a project before narrowing down
- `advanced_search` returns too few results and you need broader coverage

**Combination example:**
> `list_filters` → find filter named "400 Capital" with filter_id=23 →
> `list_cases(filter_id=23)` → scan case titles for API/endpoint/integration keywords →
> select top candidates → `get_events_of_a_case` on each for deep extraction.

**Important restriction:** Do NOT use `list_cases` for these projects:
- AG Managed Services
- DEG
- EDM Client Services
- HPS Managed Services
- Sec Master Implementation Issues

For those, use `advanced_search` or `search_cases_by_project_and_area` instead.

---

### `list_people` + `get_person_id_by_email`
**Purpose:** `list_people` returns all active users; `get_person_id_by_email` looks up a person by email.

**Use when:**
- An article or case refers to a person by name and you need their person_id to narrow searches
- You want to scope `advanced_search` to cases worked on by a specific developer or implementer

**Combination example:**
> An article mentions "contact John Smith for API credentials setup".
> → `list_people` → find John Smith's person_id → `advanced_search(query='AssignedTo:"John Smith" API endpoint')` to find cases he worked on.

---

### `list_categories` + `list_priorities`
**Purpose:** Return all case categories (Bug, Feature, Task, Inquiry, etc.) and priority levels.

**Use when:**
- You want to filter `advanced_search` results to only Feature or Inquiry cases (most likely to contain API documentation)
- You want to exclude Bug cases when looking for clean API design documentation

**Combination example:**
> `advanced_search(query='Project:Cerberus Category:Feature Tag:api')` 
> → scopes to feature cases with the api tag, which are more likely to contain endpoint specifications than bugs.

---

### `list_mailboxes` + `list_correspondant_email_addresses`
**Purpose:** Returns mailbox and correspondent email configurations.

**Use when:**
- The product integration being generated involves email-triggered workflows
- You need to document outbound/inbound email endpoints as part of the API code

**Combination example:**
> User asks: "Generate Python code for the IVP ticketing integration."
> → `list_mailboxes` → identify mailbox email addresses → include these as constants in the generated code alongside REST endpoints.

---

## Discovery Strategy: Reasoning Over Tools

The agent must reason about the best discovery path for each request. Do NOT default to only the wiki path. Use the following decision framework:

### Decision Tree

```
Does a wiki clearly exist for this product?
├── YES → list_wikis → list_articles → view_article (+ follow cross-references)
│          Also run advanced_search in parallel for case-based documentation
└── NO  → advanced_search(query='<product> API endpoint')
           └── Results found? → get_events_of_a_case on top matches
           └── No results? → list_projects → list_areas → search_cases_by_project_and_area
                              └── Still nothing? → list_filters → list_cases → scan + get_events_of_a_case

Is the product well-structured with multiple sub-areas?
└── YES → list_projects → list_areas → scope all searches to the relevant area

Are there tags in retrieved articles?
└── YES → list_tags → advanced_search(query='Tag:"<tag>"') to discover related documentation

Is the request broad ("everything about product X")?
└── YES → list_filters → list_cases → broad scan → targeted get_events_of_a_case
```

### Always Do This

- After `view_article`, check: does the article reference other articles or case numbers? If yes, follow them.
- After `advanced_search`, check: do any case titles suggest API/endpoint/schema content? If yes, `get_events_of_a_case`.
- After `list_articles`, do NOT read every article. Prioritise by title relevance to the user's feature request.
- Never stop after the first relevant result. Exhaust all plausible sources before synthesising output.

---

## Critical Output Mode Decision (Do This First)

**Before any research begins**, determine the output format from the user's prompt.

| User says… | Output mode |
|---|---|
| `python`, `javascript`, `java`, `c#`, `go`, `typescript`, any language name | **Language-specific code** |
| `REST`, `HTTP endpoints`, `API endpoints`, `postman`, `collection` | **Postman Collection JSON** |
| No language or format specified | Default to **Python** and proceed; do not ask |

---

### Language Mode — Critical Translation Rule

Documentation may present API calls as REST endpoints or as C# code snippets.

**Regardless of how documentation presents the API**, if the user requests any non-C# language:
1. Extract the HTTP method, URL, headers, and body from whatever form is in the docs
2. Rewrite as idiomatic code in the requested language
3. Never pass through C# to a Python/JS/Java user

> **Example:**
> Docs show: `client.PostAsync("/api/trade/submit", payload)` (C#)
> User requested: Python
> Agent must output:
> ```python
> response = requests.post(f"{BASE_URL}/api/trade/submit", json=payload, headers=headers)
> ```

---

## Workflow

All steps execute for a **single user prompt**. The agent must NOT prompt the user between steps.
Only one follow-up question is permitted across the entire skill run, and only if a product name
is completely unresolvable after exhausting all tool combinations.

---

### Step 0: Parse and Plan

1. Extract from the user's prompt:
   - **Product name(s)** (e.g., "Cerberus", "EDM", "400 Capital")
   - **Feature/functionality** per product (e.g., "trade submission", "position reporting")
   - **Output mode** (language or Postman)

2. For each product, reason about the most likely discovery path:
   - Is there likely a wiki? → start with `list_wikis`
   - Is the product name more likely a project/area? → also try `list_projects` + `list_areas`
   - Is the feature specific enough for `advanced_search` to find directly? → use it in parallel

3. Commit to a discovery plan per product before executing. Run it fully before moving to the next product.

---

### Step 1: Discover and Extract Documentation

For each product, execute the planned discovery path. Use multiple tool paths in combination:

#### 1a. Wiki Path (if applicable)
- `list_wikis` → match product to wiki → `list_articles(wiki_id)` → select relevant articles by title → `view_article(article_id)` for each
- Follow any cross-article references found in article content
- Cross-check article tags via `list_tags` + `advanced_search(query='Tag:"<tag>"')`

#### 1b. Case Path (always run alongside wiki path)
- `advanced_search(query='Project:"<product>" <feature keywords> API endpoint')` 
- `get_events_of_a_case` on cases whose titles suggest endpoint or schema documentation
- If `advanced_search` is too narrow: `list_filters` → `list_cases` → scan titles → `get_events_of_a_case`

#### 1c. Area-Scoped Path (for complex products)
- `list_projects` → `list_areas(project_id)` → identify the area matching the user's feature → scope all searches with `Area:"<area>"`

#### 1d. Build Endpoint Inventory

Internally maintain a structured list per product:

```
Product: <name>
Functionality: <user's requested feature>
Source articles: [list of article_ids used]
Source cases: [list of case_ids used]
Endpoints:
  - Method: POST
    Path: /api/v1/trades/submit
    Headers: { Authorization: Bearer <token>, Content-Type: application/json }
    Body: { tradeId: string, quantity: number, ... }
    Response: { status: string, tradeRef: string }
```

Every endpoint in this inventory must be traceable to a specific `view_article` result or `get_events_of_a_case` result. No hallucinated endpoints.

---

### Step 2: Synthesise Output

Once all endpoint inventories are complete, generate the final output.

#### If Output Mode = Language Code

1. Generate idiomatic code in the requested language wrapping all discovered endpoints.

2. **Chaining rule**: If one endpoint's output is logically needed as input to another — within
   or across products — chain them automatically.

   > Product A: `POST /auth/login` → `{ token }` → passed as `Authorization: Bearer <token>` to all subsequent calls
   > Product A: `GET /portfolios` → `{ portfolioId }` → passed to Product B: `GET /reports/summary?portfolioId=...`

3. Code structure:
   - Constants block: `BASE_URL`, `API_KEY`, credentials — clearly marked `YOUR_*`
   - One function per logical operation, named for what it does
   - `main()` block demonstrating the full chained flow with inline comments
   - Clean, directly runnable, no pseudocode

#### If Output Mode = Postman Collection

**STRICT OUTPUT RULE:** Output ONLY the Postman JSON block. No Python, no JS, no other language code blocks. Exactly ONE fenced code block in the entire response.

1. Generate valid **Postman Collection v2.1 JSON** with:
   - Collection name: `IVP API Collection`
   - One folder per product
   - One request per endpoint
   - Pre-request scripts for auth token injection
   - Environment variables: `{{base_url}}`, `{{api_key}}`, etc.

2. Output as a single fenced JSON block.

---

### Step 3: Format and Deliver

1. **One-paragraph summary** before the code block:
   - Products and features covered
   - Number of endpoints found
   - Which tool paths were used (wiki articles, cases, or both)
   - Chaining described if applied

2. **Single contiguous code block** — all code in one fenced block per language

3. **Short "Setup" note** after the block:
   - Dependencies to install (`pip install requests`, etc.)
   - Variables the user must fill in

4. No apologies, no meta-commentary about the research process. Deliver directly and professionally.

---

## Constraints and Guardrails

- **Single-prompt execution**: All research and synthesis happens from one message. No mid-workflow clarification unless a product is completely unresolvable.
- **One follow-up maximum**: If clarification is needed, ask everything in a single consolidated question.
- **No hallucinated endpoints**: Every endpoint must come from `view_article` or `get_events_of_a_case`. If inferred from C# code, explicitly derive the path and method — do not guess.
- **No raw C# to non-C# users**: Always translate to the requested language.
- **Complete coverage**: Do not stop after the first matching article or case. Exhaust all relevant sources.
- **Multi-tool discovery is expected**: Using only the wiki path when richer information exists in cases is a failure mode. Always cross-check with `advanced_search` and `get_events_of_a_case`.
- **Sequential product processing**: Fully complete one product's research before starting the next.
- **Chaining is mandatory when applicable**: Present connected API calls as a flow, not disconnected stubs.
- **Postman mode is JSON-only, no exceptions**: Any non-JSON code block in Postman mode is invalid output.
- **Respect the `list_cases` project restriction**: Never call `list_cases` for AG Managed Services, DEG, EDM Client Services, HPS Managed Services, or Sec Master Implementation Issues. Use `advanced_search` for those.
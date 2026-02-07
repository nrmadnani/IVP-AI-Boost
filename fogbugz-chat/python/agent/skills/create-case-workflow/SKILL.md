---
name: create-case-workflow
description: >
  Use this skill when the user wants to create, log, raise, or file a FogBugz case
  based on an error, issue, bug report, or feature request. This skill is
  responsible for collecting all required inputs, inferring missing values using
  FogBugz MCP tools when possible, and executing the create_fogbugz_case tool node.
---

# create-fogbugz-case-workflow

## Overview

This skill defines a strict workflow for creating a new FogBugz case.
The agent must gather, infer, validate, and normalize all required inputs
before invoking the `create_fogbugz_case` tool node.

The skill **must not** execute the case creation tool until all required
parameters are present and validated.

## Instructions

### Step 1: Collect Required Inputs for `create_fogbugz_case`

The agent must collect the following parameters **one by one**.
If a required parameter cannot be inferred with high confidence, the agent
**must explicitly ask the user** for that parameter before proceeding.

#### 1.1 `sTitle` (required)

- Definition: Short, precise title of the FogBugz case.
- Behavior:
  - Formulate a concise, action-oriented title based on the user’s input.
  - The title should clearly state the problem or failure.
  - Avoid vague titles such as “Bug” or “Issue”.
- If user intent is ambiguous:
  - Ask the user explicitly to confirm or provide a title.
- Examples:
  - “EDM pipeline fails on schema validation”
  - “Search API returns 500 for empty filters”

#### 1.2 `sEvent` (required)

- Definition: Detailed description of the issue.
- Behavior:
  - Generate a structured description containing:
    - Expected behavior
    - Actual behavior
    - Error messages, logs, or symptoms (if provided)
    - Any known reproduction steps or impact
  - Length constraint:
    - Maximum 2–3 concise paragraphs
  - Tone:
    - Technical, factual, and implementation-focused
- Do **not** include speculative fixes unless explicitly stated by the user.

#### 1.3 `sProject` (required)

- Definition: FogBugz project name.
- Resolution strategy:
  1. If the user explicitly specifies a project, use it directly.
  2. Otherwise:
     - Use the FogBugz MCP tool `list_projects`
     - Compare project names/descriptions against the user’s context
     - Select the **best matching project**
- Example inference:
  - User mentions “EDM ingestion failure”
  - Search projects → select “EDM”

- If no confident match exists:
  - Ask the user to explicitly choose the project.

#### 1.4 `sArea` (required)

- Definition: Area within the selected FogBugz project.
- Resolution strategy:
  1. If user explicitly mentions an area, use it.
  2. Otherwise:
     - Call FogBugz MCP tool `list_areas` for the selected project
     - Match area names against user context
- Example inference:
  - User mentions “EDM pipeline”
  - Areas include “Pipeline”, “Ingestion”, “Validation”
  - Select best semantic match
- If ambiguous:
  - Ask the user to confirm the area.

#### 1.5 `sCategory` (optional, default)

- Definition: FogBugz case category.
- Default value:
  - `"Documentation"`
- Inference rules:
  - Bug / failure → `"Bug"`
  - Feature request → `"Feature"`
  - Operational issue → `"Incident"`
- If unclear, keep default.

#### 1.6 `sPriority` (optional)

- Definition: Severity of the issue.
- Common values:
  - `"Major"`, `"Critical"`, `"Blocker"`
- Inference guidelines:
  - Production outage → `"Blocker"`
  - Data corruption / service failure → `"Critical"`
  - Partial degradation → `"Major"`
- If no strong signal exists:
  - Omit this parameter.

---

### Step 2: Validate Input Completeness

Before proceeding, the agent **must ensure**:

- `sTitle` is present and non-empty
- `sEvent` is present and non-empty
- `sProject` is resolved to a valid FogBugz project
- `sArea` is resolved to a valid area within the selected project

If **any required field is missing**, the agent must pause and request
the missing information from the user.

---

### Step 3: Execute FogBugz Case Creation

Once all required parameters are available:

1. Invoke the `create_fogbugz_case` tool node
2. Pass the collected and inferred parameters exactly as required
3. Capture the tool response

---

### Step 4: Return Result to User

- Return the full response from `create_fogbugz_case`
- Explicitly surface:
  - `case_id` (or equivalent identifier)
- Inform the user that the case has been successfully created
- Advise the user to use the case ID for tracking and follow-ups

---

## Constraints

- Do not create duplicate cases.
- Do not guess project or area when confidence is low.
- Do not execute the creation tool prematurely.
- Follow this workflow strictly and sequentially.

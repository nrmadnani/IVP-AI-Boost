---

name: create-case-workflow
description: >
Use this skill when the user wants to create, log, raise, or file a FogBugz case
based on an error, issue, bug report, or feature request. This skill is
responsible for collecting all required inputs, inferring missing values using
FogBugz MCP tools when possible, and executing the create_fogbugz_case tool node.
---------------------------------------------------------------------------------

# create-fogbugz-case-workflow

## Overview

This skill defines a strict workflow for creating a new FogBugz case.
The agent must gather, infer, validate, and normalize all required inputs
before invoking the `create_fogbugz_case` tool node.

The skill **must not** execute the case creation tool until all required
parameters are present, validated, and approved.

---

## Instructions

### Step 1: Collect Required Inputs for `create_fogbugz_case`

The agent must collect the following parameters **one by one**.
If a required parameter cannot be inferred with high confidence, the agent
**must explicitly ask the user** for that parameter before proceeding.

---

#### 1.1 `sTitle` (required)

* Definition: Short, precise title of the FogBugz case.
* Behavior:

  * Formulate a concise, action-oriented title based on the user’s input.
  * The title should clearly state the problem or failure.
  * Avoid vague titles such as “Bug” or “Issue”.
* If user intent is ambiguous:

  * Ask the user explicitly to confirm or provide a title.
* Examples:

  * “EDM pipeline fails on schema validation”
  * “Search API returns 500 for empty filters”

---

#### 1.2 `sEvent` (required)

* Definition: Detailed description of the issue.
* Behavior:

  * Generate a structured description containing:

    * Expected behavior
    * Actual behavior
    * Error messages, logs, or symptoms (if provided)
    * Any known reproduction steps or impact
  * Length constraint:

    * Maximum 2–3 concise paragraphs
  * Tone:

    * Technical, factual, and implementation-focused
* Do **not** include speculative fixes unless explicitly stated by the user.

---

#### 1.3 `ixProject` (required)

* Definition: Numeric FogBugz project identifier.

* Resolution strategy:

  1. Narrow on a **project name** from user context or explicit input.
  2. Call FogBugz MCP tool `list_projects`.
  3. Match on project name and/or description.
  4. Resolve the exact `project_id` and use it as `ixProject`.

* Example inference:

  * User mentions “EDM ingestion failure”
  * `list_projects` → find project `{ id: 12, name: "EDM" }`
  * Use `ixProject = 12`

* If no confident match exists:

  * Ask the user to explicitly choose the project.

---

#### 1.4 `ixArea` (required)

* Definition: Numeric area identifier within the selected project.

* Resolution strategy:

  1. Narrow on an **area name** from user input or context.
  2. Call FogBugz MCP tool `list_areas` using the resolved `ixProject`.
  3. Match area names semantically.
  4. Resolve the exact `area_id` and use it as `ixArea`.

* Example inference:

  * User mentions “EDM pipeline validation failure”
  * Areas include: `Pipeline`, `Ingestion`, `Validation`
  * Select `Validation → ixArea = 34`

* If ambiguous or no confident match exists:

  * Ask the user to confirm the area.

---

#### 1.5 `ixCategory` (optional)

* Definition: Numeric FogBugz case category identifier.

* Resolution strategy:

  1. Narrow on a **category name** if mentioned or inferred.
  2. Call FogBugz MCP tool `list_categories`.
  3. Match category name and resolve `category_id`.
  4. Use the resolved value as `ixCategory`.

* Inference guidelines:

  * Bug / failure → `Bug`
  * Feature request → `Feature`
  * Operational issue → `Incident`

* If unclear:

  * Omit this parameter.

---

#### 1.6 `ixPriority` (optional)

* Definition: Numeric FogBugz priority identifier.

* Resolution strategy:

  1. Narrow on a **priority name** if provided or inferred.
  2. Call FogBugz MCP tool `list_priorities`.
  3. Resolve the exact `priority_id`.
  4. Use it as `ixPriority`.

* Inference guidelines:

  * Production outage → `Blocker`
  * Data corruption / service failure → `Critical`
  * Partial degradation → `Major`

* If no strong signal exists:

  * Omit this parameter.

---

### 1.7 `ixPersonAssignedTo` (required — resolved via email)

This parameter must NOT be guessed.

The agent must:

1. Ask the user:
   "Which user (email address) should this case be assigned to?"

2. Validate that a valid email string is provided.

3. Call MCP tool:
   `get_person_id_by_email` and provide email as input

4. Extract the returned `person_id`.

5. Use that resolved numeric ID as `ixPersonAssignedTo`.

If:
- No match found
- Multiple matches found
- Email invalid

→ Ask user for clarification before proceeding.

The agent must never:
- Hardcode a default assignee
- Skip the resolution step
- Proceed without resolving a valid person ID

---

### Step 2: Validate Input Completeness

Before proceeding, the agent **must ensure**:

* `sTitle` is present and non-empty
* `sEvent` is present and non-empty
* `ixProject` is resolved to a valid FogBugz project ID
* `ixArea` is resolved to a valid area ID within the selected project
* `ixPersonAssignedTo` is resolved to valid person_id from email address

If **any required field is missing**, the agent must pause and request
the missing information from the user.

---

## Step 3: Present Case Summary (Human-in-the-Loop Approval — Mandatory)

Before executing the `create_fogbugz_case` tool node, the agent **must present a complete, normalized case summary to the user for explicit approval**.

Approval workflow:

1. Present a structured summary containing **all resolved parameters**, including:

   * `sTitle`
   * `sEvent`
   * `ixProject` (with resolved project name)
   * `ixArea` (with resolved area name)
   * `ixCategory` (if provided)
   * `ixPriority` (if provided)
   * `ixPersonAssignedTo` (with resolved email address)

2. Clearly indicate that **no case has been created yet**.

3. Ask the user for an explicit confirmation using unambiguous language, for example:

   * "Please confirm if I should create this FogBugz case with the above details."

4. The agent **must not** proceed unless the user provides an explicit approval such as:

   * "Yes, create the case"
   * "Approved"
   * "Proceed"

5. If the user requests changes:

   * Apply the changes
   * Re-present the updated summary
   * Request approval again

Rules:

* Implicit approval is **not allowed**
* Silence or unrelated responses do **not** count as approval
* Any modification after approval requires **re-approval**

---

### Step 4: Execute FogBugz Case Creation

Once explicit human approval is obtained:

1. Invoke the `create_fogbugz_case` tool node
2. Pass the collected and inferred parameters exactly as required
3. Capture the tool response

---

### Step 5: Return Result to User

* Return the full response from `create_fogbugz_case`
* Explicitly surface:

  * `case_id` (or equivalent identifier)
* Inform the user that the case has been successfully created
* Advise the user to use the case ID for tracking and follow-ups

---

## Constraints

* Do not create duplicate cases.
* Do not guess project, area, category, or priority IDs when confidence is low.
* Do not execute the creation tool prematurely.
* Follow this workflow strictly and sequentially.

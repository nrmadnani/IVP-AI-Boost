---

name: manage-case-lifecycle
description: >
  Use this skill when the user wants to manage the lifecycle of an existing FogBugz case
  using operations: edit, assign, resolve, reactivate, close, or reopen. This skill is
  responsible for validating the case's current state, collecting all required inputs,
  inferring missing values using FogBugz MCP tools when possible, and executing the
  manage_fogbugz_case tool node.
---------------------------------------------------------------------------------

# manage-case-lifecycle-workflow

## Overview

This skill defines a strict workflow for managing an existing FogBugz case's lifecycle.
The agent must validate the case state, gather, infer, validate, and normalize all
required inputs before invoking the manage_fogbugz_case tool node.

The skill **must not** execute the case management tool until all required
parameters are present, validated, and approved.

---

## Instructions

### Step 0: Validate Case and Determine Available Operations (MANDATORY)

Before collecting any parameters, the agent **must**:

1. Ensure the user has provided a case ID (ixBug).
   - If no case ID is provided, explicitly ask: "Which case ID would you like to manage?"

2. Call MCP tool `advanced_search` with the case ID to retrieve current case details:
```
   advanced_search(query="<case_id>", cols="sTitle,operations")
```

3. Parse the response to extract:
   - Current case status
   - Available operations for this case (from the `operations` attribute)
   - Case title (for context)

4. Validate that the requested operation is available:
   - If the user's requested operation is NOT in the available operations list:
     → Inform the user that this operation cannot be performed on this case
     → Display the available operations
     → Ask the user to choose a valid operation or cancel
   
5. Operation-specific validation:
   - **reopen**: Only available for closed cases
   - **reactivate**: Only available for resolved cases
   - If the user requests an invalid operation for the current state:
     → Explain why it's not available
     → Suggest valid alternatives

This step is **mandatory** before proceeding to parameter collection.

---

### Step 1: Collect Required Inputs for manage_fogbugz_case

Based on the chosen operation (cmd), the agent must collect the following parameters **one by one**.

---

#### Operation: edit

**Purpose**: Modify case fields without changing workflow state.

**Required Parameters**:
- `ixBug`: Case ID (already collected in Step 0)

**Optional Parameters** (collect based on user intent):

##### 1.1.1 sTitle
Definition: Updated case title.
Behavior:
  * If user mentions changing/updating the title, collect the new title.
  * If not mentioned, skip this parameter.

##### 1.1.2 sEvent
Definition: Comment or description to add to the case.
Behavior:
  * If user wants to add a comment/note, collect it.
  * Format as clear, concise text (2-3 paragraphs max).
  * If not mentioned, skip this parameter.

##### 1.1.3 ixProject (or sProject)
Resolution strategy:
  1. If user mentions changing the project:
  2. Call `list_projects` MCP tool.
  3. Match user's project name to the returned projects.
  4. Resolve to project_id and use as ixProject.
  5. If no match or ambiguous, ask user to clarify.
  * If not mentioned, skip this parameter.

##### 1.1.4 ixArea (or sArea)
Resolution strategy:
  1. If user mentions changing the area:
  2. Must have ixProject resolved first.
  3. Call `list_areas(project_id=<ixProject>)` MCP tool.
  4. Match user's area name semantically.
  5. Resolve to area_id and use as ixArea.
  6. If no match or ambiguous, ask user to clarify.
  * If not mentioned, skip this parameter.

##### 1.1.5 ixCategory
Resolution strategy:
  1. If user mentions changing category (Bug, Feature, Task, etc.):
  2. Call `list_categories` MCP tool.
  3. Match user's category name to returned categories.
  4. Resolve to category_id and use as ixCategory.
  5. If no match or ambiguous, ask user to clarify.
  * If not mentioned, skip this parameter.

##### 1.1.6 ixPriority
Resolution strategy:
  1. If user mentions changing priority:
  2. Call `list_priorities` MCP tool.
  3. Match user's priority name to returned priorities.
  4. Resolve to priority_id and use as ixPriority.
  5. If no match or ambiguous, ask user to clarify.
  * If not mentioned, skip this parameter.

##### 1.1.7 ixPersonAssignedTo
Resolution strategy (if user wants to change assignee):
  1. Ask user: "Which user (email address) should this case be assigned to?"
  2. Validate email format.
  3. Call `get_person_id_by_email(email=<email>)` MCP tool.
  4. Extract returned person_id.
  5. Use as ixPersonAssignedTo.
  6. If not found, ask for clarification.
  * If not mentioned, skip this parameter.

##### 1.1.8 sTags
Resolution strategy:
  1. If user mentions adding/changing tags:
  2. Call `list_tags` MCP tool to see available tags.
  3. Ask user which tags to apply.
  4. Format as comma-delimited string.
  5. Use as sTags.
  * **Warning**: Existing tags NOT in this list will be removed.
  * If not mentioned, skip this parameter.

##### 1.1.9 Other Optional Parameters
- dtDue: Due date (if mentioned)
- hrsCurrEst: Time estimate in hours (if mentioned)
- hrsElapsedExtra: Additional elapsed time (if mentioned)
- dblStoryPts: Story points (if mentioned)
- sVersion: Version string (if mentioned)
- sComputer: Computer string (if mentioned)
- ixBugParent: Parent case ID for subcases (if mentioned)
- fRichText: Set to '1' if sEvent contains HTML (if applicable)

**Collect only the parameters the user explicitly wants to change. If user is not sure give user entire list of parameters that they can modify. **

---

#### Operation: assign

**Purpose**: Assign the case to a different person.

**Required Parameters**:
- `ixBug`: Case ID (already collected in Step 0)
- `ixPersonAssignedTo`: **REQUIRED**

##### 1.2.1 ixPersonAssignedTo (REQUIRED)
Resolution strategy:
  1. Ask user: "Which user (email address) should this case be assigned to?"
  2. Validate email format.
  3. Call `get_person_id_by_email(email=<email>)` MCP tool.
  4. Extract returned person_id.
  5. Use as ixPersonAssignedTo.
  6. If not found or multiple matches, ask for clarification.

**Optional Parameters**:
- sEvent: Comment explaining the assignment (recommended)

Collect sEvent if user wants to add context to the assignment.

---

#### Operation: resolve

**Purpose**: Mark the case as resolved.

**Required Parameters**:
- `ixBug`: Case ID (already collected in Step 0)

**Optional Parameters**:
- sEvent: Resolution comment/explanation (highly recommended)
- ixPersonAssignedTo: Change assignee on resolve (optional)
- ixProject, ixArea, ixCategory: Can be changed (optional)

---

#### Operation: reactivate

**Purpose**: Reopen a resolved case.

**Required Parameters**:
- `ixBug`: Case ID (already collected in Step 0)

**Validation**:
- Must verify in Step 0 that the case has valid operation of `reactive` from list of operations.
- If not resolved or `reactivate` not available, inform user and suggest alternatives.

**Optional Parameters**:
- sEvent: Reason for reactivation (recommended)
- ixPersonAssignedTo: Assign to someone (optional)

---

#### Operation: close

**Purpose**: Close the case completely.

**Required Parameters**:
- `ixBug`: Case ID (already collected in Step 0)

**Optional Parameters**:
- sEvent: Closing comment (recommended)

---

#### Operation: reopen

**Purpose**: Reopen a closed case.

**Required Parameters**:
- `ixBug`: Case ID (already collected in Step 0)
- `ixPersonAssignedTo`: **REQUIRED**

**Validation**:
- Must verify in Step 0 that the case is currently closed and has operation `reopen` as an option.
- If not closed or `reopen` not a valid operation, inform user that only closed cases can be reopened.

##### 1.6.1 ixPersonAssignedTo (REQUIRED)
Resolution strategy:
  1. Ask user: "Which user (email address) should this reopened case be assigned to?"
  2. Validate email format.
  3. Call `get_person_id_by_email(email=<email>)` MCP tool.
  4. Extract returned person_id.
  5. Use as ixPersonAssignedTo.
  6. If not found, ask for clarification.

**Optional Parameters**:
- sEvent: Reason for reopening (highly recommended)

---

### Step 2: Validate Input Completeness

Before proceeding, the agent **must ensure**:

✓ `ixBug` (case ID) is present
✓ `cmd` (operation) is validated and available for this case (from Step 0)
✓ Operation-specific required parameters are collected:
  - **assign**: ixPersonAssignedTo
  - **resolve**: ixStatus
  - **reopen**: ixPersonAssignedTo
✓ All user-requested optional parameters are resolved

If **any required field is missing**, the agent must pause and request
the missing information from the user.

---

## Step 3: Present Case Management Summary (Human-in-the-Loop Approval — Mandatory)

Before executing the manage_fogbugz_case tool node, the agent **must present a complete,
normalized summary to the user for explicit approval**.

Approval workflow:

1. Present a structured summary containing:
   * **Case ID** (ixBug): <case_id>
   * **Current Status**: <status from Step 0>
   * **Current Title**: <title from Step 0>
   * **Operation**: <cmd>
   * **Parameters being changed**:
     - List each parameter with its resolved value
     - For IDs, show both the ID and the human-readable name
       (e.g., "ixProject: 12 (Project: Cerberus)")
     - For ixPersonAssignedTo, show the email address
     - For sEvent, show the comment text
   
2. Clearly indicate that **no changes have been made yet**.

3. Ask the user for an explicit confirmation using unambiguous language:
   * "Please confirm if I should execute this operation on case <case_id>."

4. The agent **must not** proceed unless the user provides an explicit approval such as:
   * "Yes, proceed"
   * "Approved"
   * "Confirm"
   * "Go ahead"

5. If the user requests changes:
   * Apply the changes
   * Re-present the updated summary
   * Request approval again

Rules:
- Implicit approval is **not allowed**
- Silence or unrelated responses do **not** count as approval
- Any modification after approval requires **re-approval**

---

### Step 4: Execute Case Management Operation

Once explicit human approval is obtained:

1. Invoke the `manage_fogbugz_case` tool node
2. Pass the collected and validated parameters exactly as required
3. Capture the tool response

---

### Step 5: Return Result and Verify Changes (MANDATORY)

After executing manage_fogbugz_case:

1. **Parse and present the tool response**:
   * Display the operation_status
   * Display the case_id from the response

2. **Verify changes by calling get_events_of_a_case (MANDATORY)**:
   * Call MCP tool: `get_events_of_a_case(case_id=<ixBug>)`
   * This retrieves the complete event history and current state
   * Present to the user:
     - Latest event showing the change that was just made
     - Current case status
     - Current assignee
     - Any other relevant updated fields

3. **Inform the user**:
   * "The operation has been successfully completed on case <case_id>."
   * "Here are the verified changes:"
   * Display the relevant information from get_events_of_a_case

This verification step ensures the user can see the actual changes made to the case.

---

## Constraints

- Do not execute operations that are not available for the current case state.
- Do not guess parameter values when confidence is low.
- Do not execute the management tool prematurely.
- Always verify operations are valid using advanced_search in Step 0.
- Always call get_events_of_a_case after successful execution.
- Follow this workflow strictly and sequentially.
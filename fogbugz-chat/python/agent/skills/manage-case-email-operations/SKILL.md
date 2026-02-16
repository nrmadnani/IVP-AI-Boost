---

name: manage-case-email-operations
description: >
  Use this skill when the user wants to send emails from a FogBugz case using
  operations: email, reply, or forward. This skill is responsible for validating
  the case's email configuration, collecting all required inputs, and executing
  the manage_fogbugz_case tool node for email operations.
---------------------------------------------------------------------------------

# manage-case-email-operations-workflow

## Overview

This skill defines a strict workflow for email operations on FogBugz cases.
The agent must validate the case state and email configuration, gather all
required inputs, and normalize them before invoking the manage_fogbugz_case
tool node.

The skill **must not** execute the email operation tool until all required
parameters are present, validated, and approved.

---

## Instructions

### Step 0: Validate Case and Email Configuration (MANDATORY)

Before collecting any parameters, the agent **must**:

1. Ensure the user has provided a case ID (ixBug).
   - If no case ID is provided, explicitly ask: "Which case ID would you like to send email from?"

2. Call MCP tool `get_events_of_a_case` with the case ID to retrieve current case details and email configuration:
```
   get_events_of_a_case(case_id="<case_id>")
```

3. Parse the response to extract from the case object:
   - ixBug: Case ID
   - operations: Available operations for this case
   - title: Case title (for context)
   - status: Current case status
   - **correspondant_email**: Customer email address (if set)
   - **ixMailbox**: Mailbox ID (if set)

4. Validate that email operations are available:
   - Check if the requested operation (email/reply/forward) is in the available operations list
   - If NOT available:
     → Inform the user that this operation cannot be performed
     → Display the available operations
     → Stop workflow

5. **Check email configuration (CRITICAL - MANDATORY VALIDATION)**:
   
   The agent **must** verify BOTH of the following are properly set:
   - `correspondant_email` is set AND is not null/empty
   - `ixMailbox` is set AND is not null/empty
   
   **If EITHER is missing or invalid:**
   
   a. Inform user clearly:
```
      "This case is not properly configured for email operations.
      Missing: [list what's missing: correspondant_email and/or ixMailbox]
      
      These fields must be set before sending emails from this case."
```
   
   b. **Trigger the manage-case-lifecycle workflow to configure email fields**:
      
      **Step 5.1: Collect correspondent email**
      - If `correspondant_email` is missing:
        1. Call `list_people` MCP tool to get all active users
        2. Display available people with their emails
        3. Ask user: "Which email address should be set as the correspondent for this case?"
        4. Validate that the provided email exists in the list_people results
        5. Store this as `sCustomerEmail` for the edit operation
      
      **Step 5.2: Collect mailbox ID**
      - If `ixMailbox` is missing:
        1. Call `list_mailboxes` MCP tool to get all available mailboxes
        2. Display available mailboxes with their IDs and email addresses
        3. Ask user: "Which mailbox should be associated with this case? (provide mailbox_id)"
        4. Validate it's a numeric ID that exists in the list_mailboxes results
        5. Store this as `ixMailbox` for the edit operation
      
      **Step 5.3: Execute the edit operation via manage-case-lifecycle workflow**
      - Invoke the **manage-case-lifecycle** skill with:
        * cmd: "edit"
        * ixBug: <case_id>
        * sCustomerEmail: <validated_email>
        * ixMailbox: <validated_mailbox_id>
        * sEvent: "Configuring case for email operations"
      
      - The manage-case-lifecycle workflow will:
        * Present the edit summary for approval
        * Execute the manage_fogbugz_case tool with cmd="edit"
        * Verify the changes using get_events_of_a_case
      
      **Step 5.4: Re-validate email configuration**
      - After the edit operation completes successfully:
        1. Call `get_events_of_a_case(case_id="<case_id>")` again
        2. Verify that both `correspondant_email` and `ixMailbox` are now set
        3. If still missing, report error and stop workflow
        4. If both are set, inform user: "Email configuration completed. Now proceeding with email operation."

6. **Resolve sFrom email address from mailbox (CRITICAL - MANDATORY)**:
   
   Once `ixMailbox` is validated and set on the case:
   
   a. Call `list_mailboxes` MCP tool to get all available mailboxes
   
   b. Match the case's `ixMailbox` ID with the `mailbox_id` from the list_mailboxes results
   
   c. Extract the **exact email string** from the matched mailbox object
      - The email format is: `"Mailbox Name" <email@domain.com>`
      - Example: `"DevTest Fogbugz" <dfogbugz@dev.ivp.in>`
      - Example: `"IVP Service Desk" <AutoTicketCreation@ivp.in>`
   
   d. Store this exact email string for use as `sFrom` in Step 1
      - **CRITICAL**: The email must be used EXACTLY as returned from list_mailboxes
      - Do NOT modify, reformat, or omit any part of the email string
      - Do NOT remove quotes, angle brackets, or spaces
      - Format: `"email name in quotes followed by 1 space" <emailid@mail.com>`
   
   e. If no matching mailbox_id is found:
      - Display all available mailboxes to the user
      - Report error: "ixMailbox <id> does not match any available mailbox"
      - Ask user to correct the ixMailbox value on the case
      - Stop workflow

**This validation step is MANDATORY and BLOCKING** — the agent cannot proceed to email parameter collection unless:
- Both `correspondant_email` and `ixMailbox` are properly set on the case
- The exact sFrom email address has been resolved from list_mailboxes

---

### Step 1: Collect Required Inputs for Email Operations

Based on the chosen email operation (cmd: email, reply, or forward), the agent must
collect the following parameters **one by one**.

**Prerequisites (from Step 0)**:
- Case email configuration is validated and complete
- Email operations are available for this case
- **sFrom email address has been resolved from list_mailboxes**

---

#### Common Required Parameters (All Email Operations)

##### 1.1 ixBug (REQUIRED)
Already collected in Step 0.

##### 1.2 sFrom (REQUIRED - AUTO-RESOLVED)
Definition: Sender email address.

**Resolution strategy (AUTOMATIC from Step 0)**:
1. **Use the exact email string resolved in Step 0** from the list_mailboxes match
2. This email was matched using the case's ixMailbox ID
3. **DO NOT ask the user** — this value is automatically determined
4. **DO NOT modify the email format** — use it exactly as returned

Format requirements (CRITICAL):
- The email MUST be in the exact format: `"Name" <email@domain.com>`
- Example: `"DevTest Fogbugz" <dfogbugz@dev.ivp.in>`
- Include quotes around the name
- Include angle brackets around the email address
- Include the space between the closing quote and opening angle bracket
- **DO NOT omit, change, or reformat any part of this string**

**Why this is critical**:
- If the email format is incorrect, the email WILL NOT be sent
- FogBugz requires this specific format for email operations
- The email must match a monitored mailbox so replies return to FogBugz

The agent should inform the user:
"Using mailbox email: <exact_sFrom_value> (from case's ixMailbox configuration)"

##### 1.3 sTo (REQUIRED)
Definition: Recipient email address.

Resolution strategy:
1. For **reply** operations:
   - Default to `correspondant_email` from the case (retrieved in Step 0)
   - Ask: "Should I reply to <correspondant_email>? Or specify a different recipient?"
   - If different recipient needed, validate email format

2. For **email** and **forward** operations:
   - Ask user: "Who should receive this email? (email address)"
   - Validate email format
   - Optionally suggest using `correspondant_email` if appropriate

3. Use the validated email as sTo

##### 1.4 sEvent (REQUIRED)
Definition: Email body text.

Behavior:
1. Ask user: "What message would you like to send?"
2. Collect the email body text
3. Format appropriately:
   - Keep it clear and professional
   - For replies, consider context from the case
   - Maximum 3-4 paragraphs unless user specifies more
4. Use as sEvent

**Optional**: fRichText
- If the user wants to send HTML-formatted email, set fRichText='1'
- Ask: "Should this email be sent as HTML?" (if relevant)

---

#### Operation-Specific Optional Parameters

##### 1.5 sSubject (Highly Recommended)
Definition: Email subject line.

Behavior:
1. For **email** operation:
   - Ask user: "What should the subject line be?"
   - If not provided, suggest: "Re: <Case Title>" or similar
   - Use as sSubject

2. For **reply** operation:
   - Auto-generate from case title: "Re: <Case Title>"
   - Allow user to override if desired

3. For **forward** operation:
   - Auto-generate: "Fwd: <Case Title>"
   - Allow user to override if desired

##### 1.6 sCC (Optional)
Definition: CC recipients (comma-separated email addresses).

Behavior:
- Ask: "Would you like to CC anyone? (comma-separated emails, or leave blank)"
- Validate email formats if provided
- Use as sCC if provided

##### 1.7 sBCC (Optional)
Definition: BCC recipients (comma-separated email addresses).

Behavior:
- Ask: "Would you like to BCC anyone? (comma-separated emails, or leave blank)"
- Validate email formats if provided
- Use as sBCC if provided

##### 1.8 ixBugEventAttachment (For forward operation only)
Definition: Bug event ID to include attachments from.

Behavior:
1. Only relevant for **forward** operation
2. If user wants to forward previous email attachments:
   - The agent already has case events from Step 0's get_events_of_a_case call
   - Display the available event IDs with descriptions from the events list
   - Show event type, datetime, and description for each event
   - Ask: "Which event ID should I include attachments from?"
   - Let user select the event
   - Use as ixBugEventAttachment
3. If not needed, skip this parameter

---

### Step 2: Validate Input Completeness

Before proceeding, the agent **must ensure**:

✓ `ixBug` (case ID) is present
✓ `cmd` (email operation) is validated and available (from Step 0)
✓ **Email configuration is valid** (correspondant_email and ixMailbox are set on the case - validated in Step 0)
✓ **sFrom has been auto-resolved** from list_mailboxes using the case's ixMailbox ID
✓ **All required email parameters are collected**:
  - sFrom (auto-resolved from mailbox, EXACT format preserved)
  - sTo (validated format, or from correspondant_email)
  - sEvent
✓ Optional parameters (sSubject, sCC, sBCC) are collected if user requested
✓ For forward: ixBugEventAttachment if user wants to include attachments

If **any required field is missing**, the agent must pause and request
the missing information from the user.

---

## Step 3: Present Email Operation Summary (Human-in-the-Loop Approval — Mandatory)

Before executing the manage_fogbugz_case tool node, the agent **must present a complete
email summary to the user for explicit approval**.

Approval workflow:

1. Present a structured summary containing:
   * **Case ID** (ixBug): <case_id>
   * **Case Title**: <title from Step 0>
   * **Operation**: <cmd> (email/reply/forward)
   * **Email Configuration** (verified in Step 0):
     - Correspondent Email: <correspondant_email>
     - Mailbox ID: <ixMailbox>
     - **Mailbox Email (sFrom)**: <exact_sFrom_value>
       * Show the exact format: `"Name" <email@domain.com>`
   * **Email Details**:
     - From: <sFrom> (exactly as resolved from mailbox)
     - To: <sTo>
     - Subject: <sSubject>
     - CC: <sCC> (if provided)
     - BCC: <sBCC> (if provided)
     - Message Body:
```
       <sEvent content>
```
     - Include Attachments From Event: <ixBugEventAttachment> (if applicable)

2. Clearly indicate that **no email has been sent yet**.

3. **Emphasize the exact sFrom format**:
   - Display: "The email will be sent from: <exact_sFrom_value>"
   - Note: "This exact format is required for FogBugz email operations"

4. Ask the user for an explicit confirmation using unambiguous language:
   * "Please confirm if I should send this email from case <case_id>."

5. The agent **must not** proceed unless the user provides an explicit approval such as:
   * "Yes, send it"
   * "Approved"
   * "Confirm"
   * "Go ahead"
   * "Send"

6. If the user requests changes:
   * Apply the changes to the email details
   * **DO NOT allow changes to sFrom** — it is determined by the case's ixMailbox
   * If user wants a different sFrom, they must change the case's ixMailbox first
   * Re-present the updated summary
   * Request approval again

Rules:
- Implicit approval is **not allowed**
- Silence or unrelated responses do **not** count as approval
- Any modification after approval requires **re-approval**
- **Double-check** sFrom, sTo, and sEvent before confirming
- **sFrom CANNOT be modified** by the user during this workflow

---

### Step 4: Execute Email Operation

Once explicit human approval is obtained:

1. Invoke the `manage_fogbugz_case` tool node
2. Pass the collected and validated parameters:
   - cmd (email/reply/forward)
   - ixBug
   - **sFrom (EXACT string from Step 0's mailbox resolution)**
   - sTo
   - sEvent
   - sSubject (if provided)
   - sCC (if provided)
   - sBCC (if provided)
   - ixBugEventAttachment (if provided for forward)
   - fRichText (if HTML email)
3. **CRITICAL**: Ensure sFrom is passed EXACTLY as resolved, with no modifications
4. Capture the tool response

---

### Step 5: Return Result and Verify Email Sent (MANDATORY)

After executing manage_fogbugz_case:

1. **Parse and present the tool response**:
   * Display the operation_status
   * Confirm whether the email was sent successfully
   * Display the case_id from the response
   * If email failed to send, check if sFrom format was correct

2. **Verify email was sent by calling get_events_of_a_case (MANDATORY)**:
   * Call MCP tool: `get_events_of_a_case(case_id=<ixBug>)`
   * This retrieves the complete event history including the email event
   * Present to the user:
     - Latest event showing the email that was just sent
     - Event type (should be email/reply/forward)
     - Timestamp of the email
     - Sender and recipient information
     - Email content (first few lines)

3. **Inform the user**:
   * "The email has been successfully sent from case <case_id>."
   * "Here is the verification from the case history:"
   * Display the relevant email event information from get_events_of_a_case

This verification step ensures the user can see the actual email event recorded in the case.

---

## Constraints

- **BLOCKING**: Do not proceed past Step 0 if correspondant_email or ixMailbox are not set on the case
- **MANDATORY**: If email configuration is missing, trigger manage-case-lifecycle workflow to set it first
- **CRITICAL**: sFrom MUST be resolved from list_mailboxes and used EXACTLY as returned
- **CRITICAL**: DO NOT modify, reformat, or change the sFrom email format in any way
- **CRITICAL**: The exact format `"Name" <email@domain.com>` is required for emails to be sent
- Do not execute email operations that are not available for the current case
- Do not allow user to manually specify sFrom — it is auto-determined from ixMailbox
- Do not execute the email tool prematurely
- Always verify email configuration in Step 0 using get_events_of_a_case
- Always resolve sFrom from list_mailboxes in Step 0
- Always call get_events_of_a_case after successful email send for verification
- Validate all recipient email addresses (sTo, sCC, sBCC) for proper format
- Follow this workflow strictly and sequentially
- Treat email operations with extra care - once sent, cannot be unsent

---

## Special Notes for Email Operations

**Email Configuration Prerequisites**:
1. **correspondant_email** must be set on the case (validated from list_people)
2. **ixMailbox** must be set on the case (numeric ID)
3. If either is missing, the workflow MUST pause and configure them via manage-case-lifecycle
4. Email configuration is validated using get_events_of_a_case (not advanced_search)

**sFrom Resolution (CRITICAL)**:
1. **sFrom is automatically determined** from the case's ixMailbox ID
2. The agent calls `list_mailboxes` and matches the mailbox_id to ixMailbox
3. The email value from the matched mailbox is used EXACTLY as-is
4. **Format**: `"Mailbox Name" <email@domain.com>`
5. **Example**: `"DevTest Fogbugz" <dfogbugz@dev.ivp.in>`
6. **DO NOT**:
   - Remove quotes around the name
   - Remove angle brackets around the email
   - Remove the space between quote and bracket
   - Reformat or simplify the email string
   - Ask the user to provide sFrom
7. **If the format is wrong, the email WILL NOT be sent**

**Best Practices**:
1. Always auto-resolve sFrom from list_mailboxes (never ask user)
2. For reply operations, default to correspondant_email from the case
3. Always include meaningful subject lines
4. For forward, explain what content/attachments will be forwarded
5. Double-check recipient addresses before sending
6. Verify the sFrom format is preserved exactly before executing

**Common Pitfalls to Avoid**:
- Attempting to send email without verifying case email configuration
- Modifying the sFrom email format from list_mailboxes
- Allowing user to manually specify sFrom
- Not matching ixMailbox correctly to list_mailboxes
- Forgetting to set correspondant_email and ixMailbox before email operations
- Missing subject lines (leads to poor email experience)
- Not verifying recipient addresses
- Forgetting to include context in sEvent for replies/forwards

**Troubleshooting**:
- If email fails to send, first check if sFrom was passed exactly as resolved
- Verify ixMailbox on the case matches an existing mailbox in list_mailboxes
- Ensure correspondant_email is set and valid
- Check that the email operation is available for the case's current state
import json
import os
import httpx
from typing import Optional, Dict, Any
from langchain.tools import tool
from dotenv import load_dotenv
import xml.etree.ElementTree as ET 

load_dotenv()

FOGBUGZ_URL = os.getenv("FOGBUGZ_URL")
FOGBUGZ_TOKEN = os.getenv("FOGBUGZ_TOKEN")

if not FOGBUGZ_URL or not FOGBUGZ_TOKEN:
    raise RuntimeError("FOGBUGZ_URL and FOGBUGZ_TOKEN must be set")


@tool
def create_fogbugz_case(
    sTitle: str,
    sEvent: str,
    ixProject: str,
    ixArea: str,
    ixCategory: Optional[str] = "13",
    ixPriority: Optional[str] = "4",
    ixPersonAssignedTo: str = "4124"
) -> Dict[str, str]:
    """
    Create a new case in FogBugz system.
    
    Args:
        sTitle: Title of the case (required)
        sEvent: Description/details of the issue (required)
        ixProject: FogBugz project id (required)
        ixArea: FogBugz area id within the project (required)
        ixCategory: Fogbugz category id (defaults to 13 i.e., Documentation)
        ixPriority: Priority id assigned to this case (defaults to 4 i.e., Minor)
        ixPersonAssignedTo: Id of person to whom this case should be assigned (required)
    Returns:
        Dictionary with case_id_created and case_status
    """
    # Prepare the request payload
    payload = {
        "cmd": "new",
        "sTitle": sTitle,
        "sEvent": sEvent,
        "ixProject": ixProject if ixProject else "393",
        "ixArea": ixArea if ixArea else "3518", 
        "ixCategory": ixCategory if ixCategory else "13",
        "token": FOGBUGZ_TOKEN,
        "ixPriority": ixPriority if ixPriority else "4", 
        "ixPersonAssignedTo": ixPersonAssignedTo if ixPersonAssignedTo else "4124"
    }
    
    try:
        # Make POST request to FogBugz API
        response = httpx.post(
            f"{FOGBUGZ_URL}/f/api/0/jsonapi",
            content=json.dumps(payload),
            headers={"Content-Type": "body-raw"},
            timeout=300,
        )
        response.raise_for_status()
        
        # Parse JSON response
        response_data = response.json()
        
        # Extract case ID from nested structure
        case_id = response_data.get("data", {}).get("case", {}).get("ixBug")
        
        if case_id:
            return {
                "case_id_created": str(case_id),
                "case_status": "Created successfully"
            }
        else:
            # Handle errors from FogBugz
            errors = response_data.get("errors", [])
            error_msg = "; ".join(str(e) for e in errors) if errors else "Unknown error - no case ID returned"
            return {
                "case_id_created": "N/A",
                "case_status": f"Failed to create case: {error_msg}"
            }
            
    except httpx.HTTPStatusError as e:
        return {
            "case_id_created": "N/A",
            "case_status": f"HTTP error {e.response.status_code}: {e.response.text}"
        }
    except httpx.RequestError as e:
        return {
            "case_id_created": "N/A",
            "case_status": f"Request error: {str(e)}"
        }
    except Exception as e:
        return {
            "case_id_created": "N/A",
            "case_status": f"Unexpected error: {str(e)}"
        }


@tool
def manage_fogbugz_case(
    cmd: str,
    ixBug: str,
    # Common case parameters
    ixBugEvent: Optional[str] = None,
    sTitle: Optional[str] = None,
    ixProject: Optional[str] = None,
    sProject: Optional[str] = None,
    ixArea: Optional[str] = None,
    sArea: Optional[str] = None,
    ixCategory: Optional[str] = None,
    sCategory: Optional[str] = None,
    ixPersonAssignedTo: Optional[str] = None,
    sPersonAssignedTo: Optional[str] = None,
    ixPriority: Optional[str] = None,
    sPriority: Optional[str] = None,
    sEvent: Optional[str] = None,
    fRichText: Optional[str] = None,
    sTags: Optional[str] = None,
    ixBugParent: Optional[str] = None,
    dtDue: Optional[str] = None,
    hrsCurrEst: Optional[str] = None,
    hrsElapsedExtra: Optional[str] = None,
    dblStoryPts: Optional[str] = None,
    sCustomerEmail: Optional[str] = None,
    ixMailbox: Optional[str] = None,
    # Email-specific parameters
    sFrom: Optional[str] = None,
    sTo: Optional[str] = None,
    sSubject: Optional[str] = None,
    sCC: Optional[str] = None,
    sBCC: Optional[str] = None,
    ixBugEventAttachment: Optional[str] = None,
    # Import/Admin parameters
    ixPersonEditedBy: Optional[str] = None,
    dt: Optional[str] = None,
    # Additional parameters not explicitly listed
    **kwargs: Any
) -> Dict[str, str]:
    """
    Manage the lifecycle of a FogBugz case (edit, assign, resolve, reactivate, close, reopen, email, reply, forward).
    
    Args:
        cmd: Operation to perform. Must be one of: 'edit', 'assign', 'resolve', 'reactivate', 
             'close', 'reopen', 'email', 'reply', 'forward' (required)
        ixBug: Case ID to operate on (required)
        
        Common parameters (all optional but recommended for different operations as required):
        ixBugEvent: Bug event ID for stale check
        sTitle: Case title
        ixProject: Project ID (alternative: sProject for project name)
        sProject: Project name (alternative: ixProject for project ID)
        ixArea: Area ID (alternative: sArea for area name)
        sArea: Area name (alternative: ixArea for area ID)
        ixCategory: Category ID (alternative: sCategory for category name)
        sCategory: Category name (alternative: ixCategory for category ID)
        ixPersonAssignedTo: Assigned person ID (alternative: sPersonAssignedTo for person name)
        sPersonAssignedTo: Assigned person name (alternative: ixPersonAssignedTo for person ID)
        ixPriority: Priority ID (alternative: sPriority for priority name)
        sPriority: Priority name (alternative: ixPriority for priority ID)
        sEvent: Description/comment text (HTML if fRichText='1')
        fRichText: Set to '1' for HTML content in sEvent
        sTags: Comma-delimited list of tags (existing tags not in list will be removed)
        ixBugParent: Parent case ID to make this case a subcase
        dtDue: Due date
        hrsCurrEst: Current time estimate in hours
        hrsElapsedExtra: Additional non-timesheet elapsed time in hours
        dblStoryPts: Story points for the case
        sCustomerEmail: Customer email address (case correspondent field)
        ixMailbox: Mailbox ID (recommended when setting sCustomerEmail)
        cols: Columns to return in the response
        
        For cmd=reopen (required):
        ixPersonAssignedTo: Person ID to assign the reopened case to
        
        For email operations - cmd=email, reply, forward (required):
        sFrom: Sender email address
        sTo: Recipient email address
        sEvent: Email body text
        sSubject: Email subject line (optional but recommended)
        sCC: CC recipients (optional)
        sBCC: BCC recipients (optional)
        ixBugEventAttachment: Bug event ID to include attachments from (for forward optional)
        
        Note: For email operations, ensure sCustomerEmail and ixMailbox are set on the case
        
        Import/Admin parameters (optional):
        ixPersonEditedBy: Person ID who edited (for accurate imports)
        dt: Date/time string (for accurate imports)
        
        **kwargs: Any additional parameters not explicitly listed above
    
    Returns:
        Dictionary with:
        - operation_status: Success message or error description
        - case_id: The case ID that was operated on
    
    Example usage:
        # Edit a case
        manage_fogbugz_case(cmd="edit", ixBug="12345", sTitle="New Title", sEvent="Updated description")
        
        # Assign a case
        manage_fogbugz_case(cmd="assign", ixBug="12345", ixPersonAssignedTo="4124")
        
        # Resolve a case  
        manage_fogbugz_case(cmd="resolve", ixBug="12345", sEvent="Fixed the issue")
        
        # Reopen a case (ixPersonAssignedTo required)
        manage_fogbugz_case(cmd="reopen", ixBug="12345", ixPersonAssignedTo="4124", sEvent="Reopening")
        
        # Close a case
        manage_fogbugz_case(cmd="close", ixBug="12345", sEvent="Closing case")
        
        # Send email from case (sFrom, sTo, sEvent required)
        manage_fogbugz_case(
            cmd="email", 
            ixBug="12345", 
            sFrom="support@example.com",
            sTo="customer@example.com", 
            sSubject="Update on your case",
            sEvent="We're working on your issue.",
            sCustomerEmail="customer@example.com",
            ixMailbox="1"
        )
        
        # Reply to email
        manage_fogbugz_case(
            cmd="reply",
            ixBug="12345",
            sFrom="support@example.com",
            sTo="customer@example.com",
            sEvent="Thanks for the additional information."
        )
        
        # Forward case email
        manage_fogbugz_case(
            cmd="forward",
            ixBug="12345",
            sFrom="support@example.com",
            sTo="engineering@example.com",
            sEvent="Please review this case.",
            ixBugEventAttachment="123456"
        )
    """
    
    # Validate cmd
    valid_commands = ['edit', 'assign', 'resolve', 'reactivate', 'close', 'reopen', 'email', 'reply', 'forward']
    if cmd not in valid_commands:
        return {
            "operation_status": f"Invalid command. Must be one of: {', '.join(valid_commands)}",
            "case_id": ixBug
        }
    
    # Validate ixBug
    if not ixBug:
        return {
            "operation_status": "Error: ixBug (case ID) is required for all operations",
            "case_id": "N/A"
        }
    
    # Validate email operations
    if cmd in ['email', 'reply', 'forward']:
        missing_fields = []
        if not sFrom:
            missing_fields.append('sFrom')
        if not sTo:
            missing_fields.append('sTo')
        if not sEvent:
            missing_fields.append('sEvent')
        
        if missing_fields:
            return {
                "operation_status": f"Error: Email operations require these fields: {', '.join(missing_fields)}",
                "case_id": ixBug
            }
        
        # Warn if sCustomerEmail or ixMailbox not set (non-blocking warning)
        if not sCustomerEmail or not ixMailbox:
            # Note: This is just informational, not blocking
            pass
    
    # Validate reopen operation
    if cmd == 'reopen' and not ixPersonAssignedTo:
        return {
            "operation_status": "Error: cmd=reopen requires ixPersonAssignedTo parameter",
            "case_id": ixBug
        }

    
    # Build query parameters - start with cmd, ixBug, and token
    params = {
        "cmd": cmd,
        "ixBug": ixBug,
        "token": FOGBUGZ_TOKEN
    }
    
    # Add all optional parameters if they are provided (not None)
    optional_params = {
        "ixBugEvent": ixBugEvent,
        "sTitle": sTitle,
        "ixProject": ixProject,
        "sProject": sProject,
        "ixArea": ixArea,
        "sArea": sArea,
        "ixCategory": ixCategory,
        "sCategory": sCategory,
        "ixPersonAssignedTo": ixPersonAssignedTo,
        "sPersonAssignedTo": sPersonAssignedTo,
        "ixPriority": ixPriority,
        "sPriority": sPriority,
        "sEvent": sEvent,
        "fRichText": fRichText,
        "sTags": sTags,
        "ixBugParent": ixBugParent,
        "dtDue": dtDue,
        "hrsCurrEst": hrsCurrEst,
        "hrsElapsedExtra": hrsElapsedExtra,
        "dblStoryPts": dblStoryPts,
        "sCustomerEmail": sCustomerEmail,
        "ixMailbox": ixMailbox,
        "sFrom": sFrom,
        "sTo": sTo,
        "sSubject": sSubject,
        "sCC": sCC,
        "sBCC": sBCC,
        "ixBugEventAttachment": ixBugEventAttachment,
        "ixPersonEditedBy": ixPersonEditedBy,
        "dt": dt,
    }
    
    # Only add parameters that have values
    for key, value in optional_params.items():
        if value is not None:
            params[key] = value
    
    # Add any additional kwargs parameters
    params.update(kwargs)
    
    try:
        # Make GET request to FogBugz API with query parameters
        response = httpx.get(
            f"{FOGBUGZ_URL}/api.asp",
            params=params,
            timeout=300,
        )
        
        response.raise_for_status()
        
        # Parse XML response
        try:
            root = ET.fromstring(response.text)
            
            # Check for error in response
            error_element = root.find('.//error')
            if error_element is not None:
                error_code = error_element.get('code', 'Unknown')
                error_msg = error_element.text or 'Unknown error'
                return {
                    "operation_status": f"FogBugz API Error {error_code}: {error_msg}",
                    "case_id": ixBug
                }
            
            # Look for case element with ixBug attribute
            case_element = root.find('.//case')
            if case_element is not None:
                returned_case_id = case_element.get('ixBug')
                operations = case_element.get('operations', '')
                
                if returned_case_id:
                    return {
                        "operation_status": f"Operation '{cmd}' completed successfully. Available operations: {operations}",
                        "case_id": returned_case_id
                    }
            
            # If we get here, response was OK but no case found
            return {
                "operation_status": f"Operation '{cmd}' sent but no case confirmation in response. Response: {response.text[:200]}",
                "case_id": ixBug
            }
            
        except ET.ParseError as e:
            return {
                "operation_status": f"Error parsing XML response: {str(e)}. Response: {response.text[:200]}",
                "case_id": ixBug
            }
    
    except httpx.HTTPStatusError as e:
        return {
            "operation_status": f"HTTP error {e.response.status_code}: {e.response.text[:200]}",
            "case_id": ixBug
        }
    
    except httpx.RequestError as e:
        return {
            "operation_status": f"Request error: {str(e)}",
            "case_id": ixBug
        }
    
    except Exception as e:
        return {
            "operation_status": f"Unexpected error: {str(e)}",
            "case_id": ixBug
        }
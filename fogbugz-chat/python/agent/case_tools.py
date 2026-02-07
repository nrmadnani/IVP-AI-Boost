import json
import os
import httpx
from typing import Optional, Dict
from langchain.tools import tool
from dotenv import load_dotenv

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
        "ixPersonAssignedTo": "4124"
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
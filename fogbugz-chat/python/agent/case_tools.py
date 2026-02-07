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
    sProject: str,
    sArea: str,
    sCategory: str = "Documentation",
    sPriority: Optional[str] = None,
) -> Dict[str, str]:
    """
    Create a new case in FogBugz system.
    
    Args:
        sTitle: Title of the case (required)
        sEvent: Description/details of the issue (required)
        sProject: FogBugz project name (required)
        sArea: FogBugz area name within the project (required)
        sCategory: Case category (default: "Documentation")
        sPriority: Priority level (optional, e.g., "Major", "Critical", "Blocker")
    
    Returns:
        Dictionary with case_id_created and case_status
    """
    # Prepare the request payload
    payload = {
        "cmd": "new",
        "sTitle": sTitle,
        "sEvent": sEvent,
        "sProject": sProject if sProject else "test",
        "sArea": sArea if sArea else "Undecided",
        "sCategory": sCategory,
        "token": FOGBUGZ_TOKEN,
        "sPriority": sPriority if sPriority else "Minor",
        "ixPersonAssignedTo": "4124"
    }
    
    try:
        # Make POST request to FogBugz API
        response = httpx.post(
            f"{FOGBUGZ_URL}/f/api/0/jsonapi",
            json=payload,
            headers={"Content-Type": "application/json"},
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
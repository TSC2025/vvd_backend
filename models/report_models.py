from pydantic import BaseModel, Field
from typing import Dict, Any

class GenerateReportPayload(BaseModel):
    """
    Defines the data sent from the frontend to generate a report.
    The 'activity_data' field is a flexible dictionary that can accept
    any key-value pairs from a dynamic form.
    """
    
    # This is the key field. It's a dictionary where keys are strings
    # (the form label, e.g., "Funder Name") and values can be anything
    # (string, number, etc.), so we use `Any`.
    activity_data: Dict[str, Any] = Field(..., description="A dictionary of all dynamic form fields and their values.")
    
    # We still keep the user's short description as a separate, required field,
    # as it's a core piece of input for the report narrative.
    user_description: str = Field(..., description="The short summary of the activity written by the staff member.")


class ReportResponse(BaseModel):
    """The JSON response containing the generated report."""
    report_text: str
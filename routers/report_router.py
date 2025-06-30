from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

# Import the Pydantic models we defined for this feature.
from models.report_models import GenerateReportPayload, ReportResponse

# Import the generator function that contains our LangChain logic.
from generators.report_generator import generate_activity_report

# --- Define the Router ---
# We create a new router for this feature to keep it organized.
router = APIRouter(
    prefix="/reports",
    tags=["Report Generation"]
)

# --- The Public "Generate Report" Endpoint ---
@router.post("/generate-activity-report/", response_model=ReportResponse)
async def handle_generate_report(payload: GenerateReportPayload):
    """
    This is an open, unauthenticated endpoint that accepts dynamic, structured 
    data from an activity form and uses an LLM to generate a narrative report.
    
    The request body should contain:
    - user_description: A string summary from the user.
    - activity_data: A flexible dictionary of key-value pairs from the form.
    """
    print(f"--- New Report Generation Request ---")
    print(f"User Description: '{payload.user_description}'")
    print(f"Dynamic Activity Data: {payload.activity_data}")

    try:
        # Call our generator function with the validated payload data.
        # The Pydantic model `payload` gives us type-safe access to the data.
        generated_text = await generate_activity_report(
            user_description=payload.user_description,
            activity_data=payload.activity_data
        )

        if "Error:" in generated_text:
            # This is a simple way to catch failures from the generator itself.
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=generated_text
            )

        # If successful, return the text in the expected response format.
        return ReportResponse(report_text=generated_text)

    except Exception as e:
        # Catch any other unexpected errors during the process.
        print(f"An unexpected error occurred during report generation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected internal error occurred while generating the report."
        )
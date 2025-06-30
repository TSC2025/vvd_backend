# response_models.py
# In agentic-system/models/response_models.py

from pydantic import BaseModel, Field
from typing import Any, Optional

class ChatResponse(BaseModel):
    """
    Defines the standard JSON response structure for the /chat endpoint.
    """
    # The 'response' field is flexible to handle either a string or a structured object.
    # 'Any' allows it to be a string, a list, or a dictionary, which Pydantic will
    # correctly serialize into JSON.
    response: Any = Field(..., description="The agent's final output. Can be a text string or a structured JSON object.")
    
    # It's good practice to include a session ID or other metadata for the frontend to use.
    # We can make it optional for now.
    session_id: Optional[str] = Field(None, description="The session ID for the conversation, if applicable.")


class HealthCheckResponse(BaseModel):
    """
    Defines the response for the root health check endpoint.
    """
    status: str
    message: str
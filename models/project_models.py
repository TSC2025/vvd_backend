# In agentic-system/models/project_models.py

from pydantic import BaseModel, Field, Extra
from typing import Dict, Any, List, Optional
from datetime import datetime

# ==============================================================================
#  The Core Concept for Your Dynamic Forms:
#  Because your forms use field names with spaces (e.g., "Project Name"),
#  we can't use them directly as Python attributes.
#  The solution is to define the few fields we KNOW exist (like the document 'id')
#  and then capture all other dynamic fields in a flexible dictionary called `data`.
# ==============================================================================


class VVDProject(BaseModel):
    """
    Represents a document from the 'VVDProjects' collection.
    It has one known field ('id') and a flexible 'data' field
    to hold all dynamically generated key-value pairs from the form builder.
    """
    id: str = Field(description="The unique ID of the project document in Firestore.")
    
    # The `data` field will contain everything else from the document,
    # including "Project Name", "Project ID", "Start Date", "Assigned to", etc.
    data: Dict[str, Any] = Field(default_factory=dict, description="All dynamic fields from the Firestore document.")

    class Config:
        # This allows the model to be created even if the input has fields not defined here.
        # We will manually populate the 'data' field in our data-fetching logic.
        extra = Extra.allow


class VVDActivity(BaseModel):
    """
    Represents a document from the 'VVDActivity' collection.
    Contains known metadata from the sub-form renderer and a flexible 'data' field
    for the rest of the dynamic form content.
    """
    id: str = Field(description="The unique ID of the activity document in Firestore.")
    
    # Known metadata fields that are added by your saving logic in FirestoreSubFormRenderer.js
    projectId: str
    subFormId: str
    templateId: Optional[str] = None
    projectType: Optional[str] = None
    subFormName: Optional[str] = None
    createdAt: datetime
    
    # The `data` field will contain all other dynamic fields from the sub-form,
    # like "Beneficiary", "Amount", "Description", "Image Upload", etc.
    data: Dict[str, Any] = Field(default_factory=dict, description="All dynamic fields from the Firestore sub-form document.")
    
    class Config:
        extra = Extra.allow


class VVDBudget(BaseModel):
    """
    Represents a document from the 'vvdbudget' collection.
    This structure is more static based on your accountant UI.
    """
    id: str = Field(description="The unique ID of the budget document.")
    projectId: str
    activityId: Optional[str] = Field(None, description="Present only for activity-level budgets.")
    amount: float
    createdAt: datetime
    createdBy: str
    parts: Optional[List[Dict[str, Any]]] = Field(None, description="Breakdown of the budget into parts.")


class VVDRebate(BaseModel):
    """ Represents a document from the 'vvdrebate' collection. """
    id: str
    projectId: str
    activityId: Optional[str] = None
    amount: float
    createdAt: datetime
    createdBy: str
    reason: Optional[str] = None


class ReimbursementEntry(BaseModel):
    """ Represents a single entry within a reimbursement document's 'entries' array. """
    amount: float
    description: str
    date: str # Kept as string as it's likely 'YYYY-MM-DD' from the UI
    approved: bool = False
    # Other potential fields like 'imageUrl' could be added here
    # We use 'extra = Extra.allow' to avoid errors if other keys exist
    class Config:
        extra = Extra.allow


class VVDReimbursement(BaseModel):
    """ Represents a document from the 'vvdreimbursement' collection. """
    id: str
    activityId: str
    entries: List[ReimbursementEntry]
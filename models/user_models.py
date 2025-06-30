# In agentic-system/models/user_models.py

from pydantic import BaseModel, EmailStr, Field
from typing import Literal, List

# Define the possible roles as a Literal type for strict validation.
UserRole = Literal["admin", "staff", "accountant"]

class User(BaseModel):
    """
    Represents a user document from the 'Users' collection in Firestore.
    This model is updated to match your exact data structure.
    """
    uid: str = Field(..., description="The user's unique ID from Firebase Authentication.")
    email: EmailStr = Field(..., description="The user's email address.")
    
    roles: List[UserRole] = Field(..., description="A list of roles assigned to the user.")
    
    # --- THIS IS THE LINE TO CHANGE ---
    # We tell Pydantic: "In Python, this field is called display_name.
    # But when you read the data from the database/dictionary, look for a key called 'name'."
    display_name: str = Field(..., alias="name", description="The full name of the user.")

    # A property to easily get the primary role, as used in your code.
    # This simplifies logic in other parts of the app.
    @property
    def primary_role(self) -> UserRole:
        """Returns the first role from the roles list."""
        if self.roles:
            return self.roles[0]
        raise ValueError("User has an empty roles list.")

    class Config:
        populate_by_name = True
        from_attributes = True
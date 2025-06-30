from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional

# Import the models we'll use
from models.user_models import User
from models.response_models import ChatResponse

# Import the authentication dependency
from services.auth_service import get_current_user

# Import the three agent executors we have built
from agents.admin_agent import admin_agent_executor
from agents.staff_agent import staff_agent_executor
from agents.accountant_agent import accountant_agent_executor


# --- Define the Router ---
# We define the router without a prefix here. The full path will be on the endpoint itself.
router = APIRouter(
    tags=["Chat Endpoint"]
)


# --- Define the Request Body Model ---
# This is now defined outside the endpoint function and is named to avoid conflicts.
class ChatRequestPayload(BaseModel):
    # CHANGED: The field is now 'query' to match the frontend.
    query: str


# --- The Main Chat Endpoint ---
# CHANGED: The path is now explicitly "/chat/" to avoid the 307 redirect.
@router.post("/chat/", response_model=ChatResponse)
async def handle_chat(
    # CHANGED: The request body is now validated against our new model.
    request: ChatRequestPayload,
    current_user: User = Depends(get_current_user)
):
    """
    This is the main endpoint for the agentic system. It performs the following steps:
    1. Authenticates the user using the bearer token via the `get_current_user` dependency.
    2. Determines the user's primary role.
    3. Selects the appropriate agent (Admin, Staff, or Accountant).
    4. Invokes the agent with the user's query and their unique ID.
    5. Returns the agent's final response.
    """
    role = current_user.primary_role
    # CHANGED: We now access the 'query' attribute from the request body.
    query = request.query
    
    print(f"--- New Request ---")
    print(f"User: {current_user.email} (Role: {role})")
    print(f"Query: '{query}'")

    # The input for the agent executor must be a dictionary.
    # It's crucial to pass the user's details so that tools can use them.
    # Note: We pass the user's display_name as user_id because our tools expect a name.
    agent_input = {
        "input": query,
        "user_id": current_user.display_name, # Pass the user's name
        "user_role": role # Pass the user's role for defense-in-depth checks
    }

    try:
        # --- Role-based Agent Routing ---
        if role == "admin":
            print("Routing to: Admin Agent")
            response = await admin_agent_executor.ainvoke(agent_input)
        
        elif role == "staff":
            print("Routing to: Staff Agent")
            response = await staff_agent_executor.ainvoke(agent_input)
        
        elif role == "accountant":
            print("Routing to: Accountant Agent")
            response = await accountant_agent_executor.ainvoke(agent_input)
        
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"User role '{role}' does not have a corresponding agent."
            )

        final_answer = response.get("output", "The agent did not provide a final answer.")
        print(f"Agent Final Response: {final_answer}")
        
        return ChatResponse(response=final_answer)

    except Exception as e:
        print(f"An error occurred during agent execution: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while processing your request: {e}"
        )
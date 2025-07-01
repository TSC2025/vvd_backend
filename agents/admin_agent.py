# In agentic-system/agents/admin_agent.py

import os
from langchain.agents import AgentExecutor, create_react_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

# Import all the tools this agent will have access to
from tools.performance_tools import get_staff_performance
from tools.project_tools import get_data_by_village, get_projects_by_beneficiary

# --- 1. Define the LLM ---
# We can reuse the same LLM configuration.
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0,
    convert_system_message_to_human=True
)

# --- 2. Define the Tools with Input Schemas ---
# We create a clear Pydantic schema for each tool's input to ensure reliability.

class StaffPerformanceInput(BaseModel):
    staff_name: Optional[str] = Field(None, description="The full name of the staff member. If omitted, a summary for all staff will be returned.")

@tool(args_schema=StaffPerformanceInput)
def get_staff_performance_tool(staff_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Use this tool to get a performance summary for a specific staff member or for all staff members.
    If you know the staff member's name, provide it. Otherwise, you can leave it empty to get a report on everyone.
    """
    return get_staff_performance(staff_name=staff_name)


class VillageDataInput(BaseModel):
    village_name: Optional[str] = Field(None, description="The name of the village. If omitted, a summary for all villages will be returned.")

@tool(args_schema=VillageDataInput)
def get_data_by_village_tool(village_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Use this tool to get a summary of projects and activities related to a specific village or all villages.
    If you know the village name, provide it. Otherwise, leave it empty for a full summary.
    """
    return get_data_by_village(village_name=village_name)


class BeneficiaryProjectsInput(BaseModel):
    beneficiary_name: str = Field(..., description="The name of the beneficiary group or individual to search for.")

@tool(args_schema=BeneficiaryProjectsInput)
def get_projects_by_beneficiary_tool(beneficiary_name: str) -> Dict[str, Any]:
    """

    Use this tool to find all projects and activities associated with a specific beneficiary.
    You must provide the beneficiary's name.
    """
    return get_projects_by_beneficiary(beneficiary_name=beneficiary_name)


# A list of all tools the Admin Agent can use.
admin_tools = [
    get_staff_performance_tool,
    get_data_by_village_tool,
    get_projects_by_beneficiary_tool,
]


# --- 3. Define the Agent Prompt ---
# The prompt is very similar to the staff agent's, but we give it a different persona.
prompt_template = """
You are a powerful administrative assistant for our organization.
You have broad access to query data about staff performance, village activities, and beneficiary involvement.
Answer the user's question based on the data you retrieve from the tools.

IMPORTANT BEHAVIOR RULES:

* If the user's input is a simple greeting (e.g., “hi”, “hello”, “good morning”) or small talk (e.g., “how are you?”, “what’s up?”, “thank you”), you should respond politely and conversationally without using any tools.

  * Example: If the user says “How are you?”, just say something like “I’m doing great, thank you! How can I support your work today?”

* Only use tools when the question involves a request for specific data related to staff, village, or beneficiaries.

* If the user says something ambiguous or vague, ask a clarifying question first.

You have access to the following tools:
{tools}

To answer the user's question, you must use the following format:

```
Question: the input question you must answer
Thought: you should always think about what to do and which tool is most appropriate. If no tool is needed, I will just provide a conversational response.
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action, as a JSON object matching the tool's input schema.
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question. Provide a clear and concise summary of the findings.
```

Begin!

Question: {input}
Thought:{agent\_scratchpad}

"""

prompt = ChatPromptTemplate.from_template(prompt_template)


# --- 4. Create the Agent ---
admin_agent = create_react_agent(llm, admin_tools, prompt)


# --- 5. Create the Agent Executor ---
admin_agent_executor = AgentExecutor(
    agent=admin_agent,
    tools=admin_tools,
    verbose=True,
    handle_parsing_errors=True,
)

print("Admin Agent and Executor created successfully.")
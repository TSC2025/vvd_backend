# In agentic-system/agents/staff_agent.py

import os
from langchain.agents import AgentExecutor, create_react_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool
from pydantic import BaseModel, Field

# Import the specific tool for this agent
from tools.performance_tools import get_my_performance

# --- 1. Define the LLM ---
# Initialize the Gemini model from Google AI Studio.
# Make sure GOOGLE_API_KEY is set in your .env file.
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0,
    convert_system_message_to_human=True # Helps with some models
)

# --- 2. Define the Tools ---
# LangChain's @tool decorator automatically converts our function into a BaseTool object.
# This is a cleaner way to register tools.
# We also define an input schema to guide the LLM.
class GetMyPerformanceInput(BaseModel):
    user_id: str = Field(description="The unique ID of the user asking the question. This is provided by the system.")

@tool(args_schema=GetMyPerformanceInput)
def get_my_performance_tool(user_id: str) -> str:
    """
    Use this tool to get a performance summary for the currently logged-in user.
    It finds all projects and activities assigned to you.
    You must provide the user_id of the person asking.
    """
    # This is a wrapper. The actual logic is in the imported function.
    return get_my_performance(user_id=user_id)


# A list of all tools the Staff Agent can use.
staff_tools = [
    get_my_performance_tool,
]

# --- 3. Define the Agent Prompt ---
# This prompt template is the "brain" of the agent. It tells the agent its persona,
# how to think, and how to use the tools. The ReAct (Reasoning and Acting)
# framework is a standard for tool-using agents.
prompt_template = """
You are a helpful assistant for our organization's staff members.
Your goal is to answer their questions about their own work assignments.

You have access to the following tools:

{tools}

To answer the user's question, you must use the following format:

Question: the input question you must answer
Thought: you should always think about what to do.
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action, which must be a JSON object matching the tool's schema. For example: {{"user_id": "some_user_id_abc123"}}
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question.

Begin!

Question: {input}
Thought:{agent_scratchpad}
"""

prompt = ChatPromptTemplate.from_template(prompt_template)


# --- 4. Create the Agent ---
# The create_react_agent function binds the LLM, tools, and prompt together.
staff_agent = create_react_agent(llm, staff_tools, prompt)


# --- 5. Create the Agent Executor ---
# The AgentExecutor is what actually runs the agent. It takes user input,
# invokes the agent, executes the chosen tools, and gets the final response.
# The `handle_parsing_errors=True` is important for production to gracefully
# handle cases where the LLM might output a malformed response.
staff_agent_executor = AgentExecutor(
    agent=staff_agent,
    tools=staff_tools,
    verbose=True, # Set to True to see the agent's thoughts and actions in the console. Great for debugging.
    handle_parsing_errors=True,
)

print("Staff Agent and Executor created successfully.")
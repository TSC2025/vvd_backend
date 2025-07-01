# In agentic-system/agents/accountant_agent.py

import os
from langchain.agents import AgentExecutor, create_react_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

# Import the specific tool for this agent
from tools.budget_tools import get_financial_report

# --- 1. Define the LLM ---
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0,
    convert_system_message_to_human=True
)

# --- 2. Define the Tools with Input Schemas ---

class FinancialReportInput(BaseModel):
    project_name: Optional[str] = Field(None, description="The name of the project. If omitted, a high-level summary of all project budgets will be returned.")

@tool(args_schema=FinancialReportInput)
def get_financial_report_tool(project_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Use this tool to get financial reports.
    If the user asks for a specific project's financials, provide the 'project_name'.
    If the user asks for a general budget overview or a summary of all projects, call this tool without any arguments.
    **IMPORTANT: If the user's input is a simple greeting like "hi" or a conversational question that does not require specific data, you should respond politely without using a tool. Only use tools when a specific question about data is asked.**

    """
    return get_financial_report(project_name=project_name)


# A list of all tools the Accountant Agent can use.
accountant_tools = [
    get_financial_report_tool,
]

# --- 3. Define the Agent Prompt ---
prompt_template = """
You are a specialized financial assistant for our organization's accounting department.
Your primary function is to provide budget and financial reports for projects.
Answer the user's questions based on the data you retrieve from your financial tool.

You have access to the following tools:

{tools}

To answer the user's question, you must use the following format:

Question: the input question you must answer
Thought: I need to determine if the user is asking for a specific project's financials or a general summary.
Action: the action to take, which should be one of [{tool_names}]
Action Input: the input to the action, as a JSON object. For a specific project, it would be {{"project_name": "Project Name"}}. For a general summary, it would be an empty object {{}}.
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now have the financial data and can answer the user's question.
Final Answer: Provide a clear, structured summary of the financial data. For example, list the project budget, then activity budgets, then rebates.

Begin!

Question: {input}
Thought:{agent_scratchpad}
"""

prompt = ChatPromptTemplate.from_template(prompt_template)


# --- 4. Create the Agent ---
accountant_agent = create_react_agent(llm, accountant_tools, prompt)


# --- 5. Create the Agent Executor ---
accountant_agent_executor = AgentExecutor(
    agent=accountant_agent,
    tools=accountant_tools,
    verbose=True,
    handle_parsing_errors=True,
)

print("Accountant Agent and Executor created successfully.")
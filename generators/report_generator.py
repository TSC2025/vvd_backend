import os
import json # We'll use this to format the dictionary nicely for the prompt
from langchain.chains import LLMChain
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate

# It's better to manage settings in a dedicated config file, but for now,
# we'll load the API key directly from the environment as this is a self-contained module.
# Assumes load_dotenv() has been called in main.py
google_api_key = os.getenv("GOOGLE_API_KEY")

# --- 1. The Prompt Template ---
# This prompt is specifically designed to handle a dynamic dictionary of data.
# It tells the LLM what its role is and how to interpret the flexible data structure.

REPORT_PROMPT_TEMPLATE = """
You are a professional report writer for an NGO. Your primary task is to write a formal, well-structured activity report using the data provided below. The report should be suitable for internal records and for sharing with stakeholders or funders.

**Key Instructions:**
1.  Begin the report with a suitable title.
2.  Your main goal is to create a coherent narrative. Start with the "Staff's Summary" and then skillfully weave in all the "Additional Data Points" into the report.
3.  The "Additional Data Points" will be provided as a dictionary. The keys are the labels from the form, and the values are the data. Intelligently integrate all of these points into your narrative.
4.  Do not simply list the data. For example, instead of writing "Male Attendees: 25", write "The event saw participation from 25 male attendees."
5.  Maintain a professional, objective, and positive tone throughout.
6.  The final output must be ONLY the generated report text. Do not include any extra commentary, headers, or conversational text.

**--- Data Provided for this Report ---**

**Staff's Summary:**
{user_description}

**Additional Data Points:**
{activity_data_str}

**--- Generated Report ---**
"""

# Create the PromptTemplate instance from the text above.
report_generator_prompt = PromptTemplate.from_template(REPORT_PROMPT_TEMPLATE)


# --- 2. The Language Model (LLM) ---
# Initialize the Gemini model. We use a slightly higher temperature
# to allow for more natural and creative language in the report writing.
if not google_api_key:
    print("WARNING: GOOGLE_API_KEY not found. Report generator will not work.")
    llm = None
else:
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash", # A good balance of cost and capability for writing tasks.
        temperature=0.4,
        google_api_key=google_api_key
    )


# --- 3. The LangChain Chain ---
# We use a simple LLMChain because we don't need an agent with tools.
# This is a direct "prompt -> LLM -> output" sequence.
if llm:
    report_generation_chain = LLMChain(llm=llm, prompt=report_generator_prompt)
    print("Report Generator Chain created successfully.")
else:
    report_generation_chain = None


# --- 4. The Main Function ---
# This is the function that our router will call.
async def generate_activity_report(user_description: str, activity_data: dict) -> str:
    """
    Invokes the LLMChain to generate a narrative report from dynamic, structured data.

    Args:
        user_description: The summary written by the user.
        activity_data: A dictionary containing all dynamic fields from the form.

    Returns:
        The generated report text as a string.
    """
    if not report_generation_chain:
        return "Error: The report generation service is not configured correctly. Please check the API key."

    # We format the dictionary into a clean, human-readable string for the prompt.
    # Using json.dumps with indentation makes it easier for the LLM to parse.
    activity_data_str = json.dumps(activity_data, indent=2)

    # Prepare the final input dictionary for the chain.
    input_data = {
        "user_description": user_description,
        "activity_data_str": activity_data_str
    }
    
    # We use ainvoke for asynchronous execution, which is best practice in FastAPI.
    response = await report_generation_chain.ainvoke(input_data)
    
    # The response from an LLMChain is a dictionary that contains a 'text' key.
    return response.get('text', 'Error: Could not generate a valid report text from the provided data.')
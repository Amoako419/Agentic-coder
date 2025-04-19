from google.adk.agents.sequential_agent import SequentialAgent
from google.adk.agents.llm_agent import LlmAgent
from google.adk.tools import google_search
from google.genai import types
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner

# --- Constants ---
APP_NAME = "code_assistant_app"
USER_ID = "developer_user_01"
SESSION_ID = "coding_session_01"
GEMINI_MODEL = "gemini-2.0-flash-exp"

# --- 1. Define Sub-Agents for Each Coding Task ---

# Code Understanding Agent
# Takes the user's query about a coding project/task and understands the requirements
code_understanding_agent = LlmAgent(
    name="CodeUnderstandingAgent",
    model=GEMINI_MODEL,
    instruction="""You are a Code Understanding AI.
    Based on the user's coding request, formulate a clear understanding of:
    1. The programming task or problem they're trying to solve
    2. The language, framework, or technologies involved
    3. Any specific requirements or constraints
    
    If the user has provided code, analyze it to understand its purpose and structure.
    If the user is reporting an error, identify what they're trying to accomplish.
    
    Output a concise summary of the coding task and what the user needs help with.
    """,
    description="Understands coding problems and requirements from user queries.",
    output_key="coding_task_understanding",
    tools=[google_search]
)

# Research Agent
# Searches for relevant documentation, examples, or error solutions
research_agent = LlmAgent(
    name="ResearchAgent",
    model=GEMINI_MODEL,
    instruction="""You are a Coding Research AI.
    Take the coding task understanding from the session state under the key 'coding_task_understanding'.
    
    Formulate 2-3 specific search queries to find:
    1. Official documentation relevant to the task
    2. Code examples solving similar problems
    3. Common issues or errors related to this task and their solutions
    
    Perform Google searches using these queries and collect the most relevant information.
    Focus on recent, authoritative sources like official documentation, GitHub repositories, Stack Overflow answers, and reputable coding blogs.
    
    Organize this information clearly, including:
    - Links to key documentation
    - Code snippets that demonstrate solutions
    - Explanations of common pitfalls or best practices
    """,
    description="Researches coding solutions and best practices.",
    output_key="coding_research",
    tools=[google_search]
)

# Code Generation/Debugging Agent
# Analyzes the research and generates code or debugging suggestions
code_generation_agent = LlmAgent(
    name="CodeGenerationAgent",
    model=GEMINI_MODEL,
    instruction="""You are a Code Generation and Debugging AI.
    Review the coding task understanding and research from the session state keys 'coding_task_understanding' and 'coding_research'.
    
    Based on this information:
    
    1. IF THE USER NEEDS NEW CODE:
       - Generate well-structured, efficient code that solves their problem
       - Include clear comments explaining key parts of the code
       - Follow best practices for the language/framework
       - Handle potential edge cases and errors
    
    2. IF THE USER HAS CODE WITH ERRORS:
       - Identify the likely causes of the error
       - Provide fixed code with corrections clearly marked
       - Explain what was causing the error and why the fix works
    
    3. IF THE USER WANTS TO IMPROVE EXISTING CODE:
       - Suggest optimizations for performance, readability, or maintainability
       - Provide refactored code examples
       - Explain the benefits of the improvements
    
    Output complete, executable code snippets that directly address the user's needs.
    """,
    description="Generates code solutions or provides debugging fixes.",
    output_key="code_solution",
)

# Explanation Agent
# Creates a clear, educational explanation of the solution
explanation_agent = LlmAgent(
    name="ExplanationAgent",
    model=GEMINI_MODEL,
    instruction="""You are a Code Explanation AI.
    Review the coding task understanding, research, and solution from the session state.
    
    Create a comprehensive but concise explanation that includes:
    
    1. SOLUTION OVERVIEW:
       - Summarize the approach taken to solve the problem
       - Explain why this approach is appropriate
    
    2. CODE WALKTHROUGH:
       - Break down how the key parts of the code work
       - Highlight important functions, methods, or patterns used
    
    3. LEARNING RESOURCES:
       - Suggest specific documentation or tutorials for further learning
       - Point out related concepts the user might want to explore
    
    4. NEXT STEPS:
       - Suggest how the user might extend or improve the solution
       - Mention potential edge cases or considerations for production use
    
    Make your explanation educational and helpful, assuming the user wants to understand not just what the solution is, but why it works and how they can learn from it.
    """,
    description="Provides clear explanations of code solutions and concepts.",
    output_key="code_explanation"
)

# --- 2. Create the SequentialAgent ---
# This agent orchestrates the code assistant pipeline
root_agent = SequentialAgent(
    name="CodeAssistantAgent",
    sub_agents=[code_understanding_agent, research_agent, code_generation_agent, explanation_agent],
    description="A comprehensive code assistant that helps with understanding problems, researching solutions, generating code, and explaining concepts."
)

# Session and Runner
session_service = InMemorySessionService()
session = session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
runner = Runner(agent=root_agent, app_name=APP_NAME, session_service=session_service)


# Agent Interaction
def call_agent(query):
    """
    Send a query to the code assistant and print its response.
    
    Args:
        query (str): The coding query from the user
    """
    print(f"\nUser Query: {query}")
    content = types.Content(role='user', parts=[types.Part(text=query)])
    events = runner.run(user_id=USER_ID, session_id=SESSION_ID, new_message=content)

    for event in events:
        if event.is_final_response():
            final_response = event.content.parts[0].text
            print("\nCode Assistant Response:")
            print(final_response)



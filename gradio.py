from google.adk.agents.sequential_agent import SequentialAgent
from google.adk.agents.llm_agent import LlmAgent
from google.adk.tools import google_search
from google.genai import types
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
import gradio as gr
import uuid

# --- Constants ---
APP_NAME = "code_assistant_app"
USER_ID = "developer_user_01"
GEMINI_MODEL = "gemini-2.0-flash-exp"

# --- 1. Define Sub-Agents for Each Coding Task ---

# Code Understanding Agent
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
    
    Format your response using Markdown for better readability, with code blocks for all code examples.
    """,
    description="Provides clear explanations of code solutions and concepts.",
    output_key="code_explanation"
)

# --- 2. Create the SequentialAgent ---
root_agent = SequentialAgent(
    name="CodeAssistantAgent",
    sub_agents=[code_understanding_agent, research_agent, code_generation_agent, explanation_agent],
    description="A comprehensive code assistant that helps with understanding problems, researching solutions, generating code, and explaining concepts."
)

# Session and Runner setup
session_service = InMemorySessionService()

# Dictionary to store session IDs for different users
user_sessions = {}

def get_session_id(user_identifier):
    """Generate or retrieve a unique session ID for each user"""
    if user_identifier not in user_sessions:
        user_sessions[user_identifier] = f"session_{uuid.uuid4()}"
    return user_sessions[user_identifier]

def new_session(user_identifier):
    """Create a new session for the user"""
    user_sessions[user_identifier] = f"session_{uuid.uuid4()}"
    session_id = user_sessions[user_identifier]
    session_service.create_session(app_name=APP_NAME, user_id=user_identifier, session_id=session_id)
    return f"Created new session: {session_id}"

def process_code_query(user_query, user_identifier="default_user"):
    """Process a code query from the user and return the assistant's response"""
    session_id = get_session_id(user_identifier)
    
    # Ensure a session exists for this user
    try:
        session = session_service.get_session(app_name=APP_NAME, user_id=user_identifier, session_id=session_id)
    except:
        session = session_service.create_session(app_name=APP_NAME, user_id=user_identifier, session_id=session_id)
    
    # Create a runner for the agent
    runner = Runner(agent=root_agent, app_name=APP_NAME, session_service=session_service)
    
    # Process the query
    content = types.Content(role='user', parts=[types.Part(text=user_query)])
    events = runner.run(user_id=user_identifier, session_id=session_id, new_message=content)
    
    # Get the final response
    final_response = ""
    for event in events:
        if event.is_final_response():
            final_response = event.content.parts[0].text
    
    if not final_response:
        final_response = "I encountered an issue processing your request. Please try again or start a new session."
    
    return final_response

# --- 3. Gradio UI Setup ---
with gr.Blocks(title="CodeAssist AI", theme=gr.themes.Soft()) as app:
    gr.Markdown("""
    # 🚀 CodeAssist AI
    
    Your intelligent coding companion that helps you:
    - Generate new code solutions
    - Debug existing code
    - Optimize for performance
    - Learn programming concepts
    
    *Powered by Gemini & Google Search*
    """)
    
    with gr.Row():
        with gr.Column(scale=2):
            user_id_input = gr.Textbox(
                label="User ID (optional)",
                placeholder="Enter a unique identifier or leave blank for default",
                value="default_user"
            )
            
            code_query = gr.Textbox(
                label="Describe your coding task or paste code with errors",
                placeholder="Example: 'How do I create a REST API in Python?' or 'I'm getting TypeError: cannot read property...'",
                lines=10
            )
            
            with gr.Row():
                submit_btn = gr.Button("Submit", variant="primary")
                new_session_btn = gr.Button("Start New Session")
            
        with gr.Column(scale=3):
            output = gr.Markdown(
                label="CodeAssist AI Response",
                value="Your solution will appear here..."
            )
            
    # Set up event handlers
    submit_btn.click(
        fn=process_code_query,
        inputs=[code_query, user_id_input],
        outputs=output
    )
    
    new_session_btn.click(
        fn=new_session,
        inputs=[user_id_input],
        outputs=gr.Textbox(label="Session Status")
    )
    
    # Examples
    gr.Examples(
        examples=[
            ["How do I create a REST API in Python using Flask?"],
            ["I'm getting this error: TypeError: can only concatenate str (not \"int\") to str\n\ndef calculate_total(items):\n    total = 0\n    for item in items:\n        total = total + item['price']\n    return \"Total: \" + total"],
            ["How can I make this React code more efficient? It's re-rendering too often:\n\nfunction UserList({ users }) {\n  const [filteredUsers, setFilteredUsers] = useState([]);\n  const [searchTerm, setSearchTerm] = useState('');\n  \n  useEffect(() => {\n    const filtered = users.filter(user => \n      user.name.toLowerCase().includes(searchTerm.toLowerCase())\n    );\n    setFilteredUsers(filtered);\n  }, [searchTerm, users]);\n  \n  return (\n    <div>\n      <input type=\"text\" onChange={(e) => setSearchTerm(e.target.value)} value={searchTerm} />\n      {filteredUsers.map(user => (\n        <UserItem key={user.id} user={user} />\n      ))}\n    </div>\n  );\n}"],
        ],
        inputs=code_query,
    )

    gr.Markdown("""
    ### Tips for best results:
    - Be specific about what you're trying to accomplish
    - Include error messages if you're debugging code
    - Mention the programming language, framework, or libraries you're using
    - Start a new session for unrelated coding tasks
    """)

# Launch the app
if __name__ == "__main__":
    app.launch(share=True, debug=True)
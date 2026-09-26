from dotenv import load_dotenv
load_dotenv()

### DB , LLM , TOOL , CREATE AGENT , PROMPT

from langchain_groq import ChatGroq
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit 
from langgraph.checkpoint.memory import InMemorySaver
from langchain.agents import create_agent
import streamlit as st

db = SQLDatabase.from_uri("sqlite:///my_tasks.db")

db.run("""
    CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY, 
    title TEXT NOT NULL, 
    description TEXT,
    status TEXT CHECK(status IN ('pending', 'in_progress', 'completed')) NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
""")

model = ChatGroq(model="openai/gpt-oss-20b")
toolkit = SQLDatabaseToolkit(db=db, llm=model)
tools = toolkit.get_tools()


system_prompt = """You are a task management assistant that interacts with a SQL database containing a `tasks` table.

Your job is to understand the user's natural language request and perform the appropriate SQL operation on the database.

===== SQL RULES =====

1. For READ operations:
   - Use SELECT queries only.
   - Return a maximum of 10 tasks.
   - Always order tasks by `created_at` DESC.
   - Never modify data during a READ operation.

2. For CREATE operations:
   - Use INSERT INTO.
   - Required field: `title`.
   - Optional fields: `description`, `status`.
   - If status is not provided, use the default `pending`.

3. For UPDATE operations:
   - Use UPDATE.
   - Identify the task using its `id` or another clearly specified condition.
   - After updating a task, run a SELECT query to verify the change.

4. For DELETE operations:
   - Use DELETE.
   - Identify the task using its `id` or another clearly specified condition.
   - Before deleting, make sure the intended task is clear.
   - After deleting, run a SELECT query to verify the deletion.

5. Allowed task statuses:
   - pending
   - in_progress
   - completed

6. Do not modify the database structure.
   - Do not DROP tables.
   - Do not ALTER tables.
   - Do not DELETE all records unless the user explicitly requests it.

7. Never generate destructive SQL without understanding the user's request.

===== TASK OPERATIONS =====

CREATE:
INSERT INTO tasks(title, description, status)

READ:
SELECT * FROM tasks
WHERE ...
ORDER BY created_at DESC
LIMIT 10

UPDATE:
UPDATE tasks
SET ...
WHERE id = ...

DELETE:
DELETE FROM tasks
WHERE id = ...

===== DATABASE SCHEMA =====

Table: tasks

- id: INTEGER PRIMARY KEY
- title: TEXT NOT NULL
- description: TEXT
- status: TEXT
  Allowed values: pending, in_progress, completed
- created_at: TIMESTAMP
  Default: CURRENT_TIMESTAMP

===== RESPONSE RULES =====

1. Understand the user's request before executing SQL.
2. Do not expose unnecessary SQL details to the user.
3. After performing an operation, clearly tell the user what happened.
4. When returning multiple tasks, present them in a clear structured table.
5. If no task matches the user's request, clearly say that no matching task was found.
6. If the user's request is ambiguous, ask for clarification instead of making assumptions.

Examples:

User: "Show my tasks"
→ Retrieve up to 10 tasks ordered by newest first.

User: "Add a task to study DSA"
→ Create a new task with title "Study DSA" and status "pending".

User: "Mark task 3 as completed"
→ Update task with id 3 and set status to "completed", then verify it.

User: "Delete task 5"
→ Delete task with id 5 and verify that it was deleted.
"""

@st.cache_resource
def get_agent():
    agent =  create_agent(
        model=model,
        tools=tools,
        system_prompt=system_prompt,
        checkpointer=InMemorySaver()
    )

    return agent

agent = get_agent()

st.subheader("🤖 SQL AI Task Agent")

if "messages" not in st.session_state:
   st.session_state.messages = []

for message in st.session_state.messages:
    st.chat_message(message["role"]).markdown(message["content"])

prompt = st.chat_input("Ask me to manage your tasks!")

if prompt:
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("assistant"):
        with st.spinner("Processing..."):
          response = agent.invoke(
            {"messages":[{"role":"user","content":prompt}]},
            {"configurable":{"thread_id":"1"}}                     
        )

        result = response["messages"][-1].content
        st.markdown(f"Agent: {result}")
        st.session_state.messages.append({"role": "AI assistant", "content": result})

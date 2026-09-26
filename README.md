# SQL Agent AI

AI-powered SQL agent that allows users to interact with a SQLite database using natural language.

## Features

- Natural language to SQL interaction
- Create tasks
- Read tasks
- Update tasks
- Delete tasks
- Groq LLM integration
- LangChain SQL toolkit
- LangGraph agent memory
- SQLite database
- Streamlit web interface

## Tech Stack

- Python
- LangChain
- LangGraph
- Groq
- SQLite
- Streamlit

## Run Locally

```bash
git clone 
cd SQL-Agent-AI

python -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt

streamlit run apps/app.py
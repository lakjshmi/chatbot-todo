# TodoBot: Minimalist LLM Task Manager

A distraction-free, two-tab todo list powered by a local LLM. Built with Python, Streamlit, and Ollama to ensure 100% privacy and open-source compliance.

## Features

- **Chat Interface**: You can tell the bot what you need to do in plain english and let it create a to-do that also Motivates you!
- **Local Intelligence**: Uses `Gemma 3 4B` via Ollama to extract tasks (No API keys needed).
- **Minimalistic Design**: Clean, UI Inspired by "Nothing" when it didnt meet my expectations of the "Essential Space", hence created this 2 tab UI: chats and tasks
- **Voice It**: (Under works) Integration for local speech-to-text

## Tech Stack
- **Frontend**: Streamlit
- **Brain**: Ollama(Gemma 3 4B)
- **Database**: SQLite 3
- **Language**: Python

## Setup Instructions

1. **Install Ollama and pull the model:**
```bash
ollama pull gemma3:4b
```
2. **Clone and Setup Environment:**
```bash
git clone https://github.com/lakjshmi/chatbot-todo.git
cd chatbot-todo
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```
3. **Run the app**
```bash
streamlit run app.py
```
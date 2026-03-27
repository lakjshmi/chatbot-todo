import sqlite3 
import streamlit as st
import ollama


#initialising the database
conn = sqlite3.connect('todo.db',check_same_thread=False)
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS tasks (id INTEGER PRIMARY KEY, task TEXT, status TEXT)')
conn.commit()

def extract_task(user_input):
    response = ollama.generate(
        model = 'gemma3:4b',
        system="You are a minimalist todo-list assistant. Extract the core task from the user's input. Respond with ONLY the task name. You are also very funny. You try to motivate the user to get ahead in life always. You frame the tasks in a pleasant and motivating way.",
        prompt=user_input
    )
    return response['response'].strip()

st.title("Todo Chat")
tab1, tab2= st.tabs(["Chat","My List"])

with tab1:
    user_text = st.chat_input("What's on your mind?")
    if user_text:
        #1. Process with LLM
        clean_task= extract_task(user_text)
        #2. Save to DB
        c.execute('INSERT INTO tasks (task,status) VALUES (?,?)',(clean_task,'pending'))
        conn.commit()
        st.success(f"Added:{clean_task}")

with tab2: 
    st.header("Pending Tasks")
    items = c.execute ('SELECT id,task FROM tasks WHERE status= "pending"').fetchall()
    for item_id, task_text in items:
        if st.checkbox(task_text, key=item_id):
            c.execute('UPDATE tasks SET status="done" WHERE id=?', (item_id,))
            conn.commit()
            st.rerun()

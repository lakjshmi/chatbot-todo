import sqlite3 
import streamlit as st
import ollama
import re


#initialising the database
conn = sqlite3.connect('todo.db',check_same_thread=False)
c = conn.cursor()

# Updated Table Creation
c.execute('''CREATE TABLE IF NOT EXISTS tasks 
             (id INTEGER PRIMARY KEY, 
              task TEXT, 
              status TEXT, 
              parent_id INTEGER DEFAULT NULL)''')
conn.commit()

system_prompt = """
You are a Literal Task Mirror. 

CORE RULES:
1. NO NUMBERING: Never add "Task 1", "Task 2", or any numbers/bullets. 
2. INDEPENDENT LINES: Every unrelated action gets its own line.
3. VERBATIM: Use the user's exact words. If the user says "buy fruits", the output is "buy fruits".
4. PROJECT RULE: Only use sub-tasks for single, massive goals (e.g., "Build a house"). For "buy fruits and lift weights", use two separate lines.

EXAMPLES:
User: buy fruits and lift weights
Output:
buy fruits
lift weights

User: build a pc
Output:
build a pc
order components
assemble parts
install OS
"""

def extract_task(user_input):
    response = ollama.generate(
        model = 'gemma3:4b',
        system=system_prompt,
        prompt=user_input
    )
    return response['response'].strip()

st.title("Todo Chat")
tab1, tab2,tab3= st.tabs(["Chat","My List","Completed"])

with tab1:
    user_text = st.chat_input("What's on your mind?")
    

    if user_text:
        raw_output = extract_task(user_text)
        # 1. Split into lines
        lines = [l.strip() for l in raw_output.split('\n') if l.strip()]
        
        # 2. SANITIZE: Remove any line that looks like "Task 1", "1.", or "Task:"
        # This acts as a second shield if the LLM ignores the prompt
        clean_lines = []
        for line in lines:
            if not re.match(r'^(Task\s*\d+|Task:|\d+\.)', line, re.IGNORECASE):
                clean_lines.append(line)

        # 3. SAVE AS INDEPENDENT TASKS
        # To prevent the "fake grouping" you saw, let's treat everything as a main task 
        # unless there is only one clear topic.
        for line in clean_lines:
            c.execute('INSERT INTO tasks (task, status) VALUES (?, ?)', (line, 'pending'))
                
        conn.commit()
        
        st.toast("Plan Architected.")
        st.success(f"Added:{line}")
        #st.rerun()


with tab2:
    st.header("Active Visions")
    main_tasks = c.execute('SELECT id, task FROM tasks WHERE parent_id IS NULL AND status="pending"').fetchall()
    
    for m_id, m_text in main_tasks:
    # Fetch subtasks
        subtasks = c.execute('SELECT id, task FROM tasks WHERE parent_id=? AND status="pending"', (m_id,)).fetchall()
        
        # If it's a simple task (no subtasks), just show a normal checkbox
        if not subtasks:
            if st.checkbox(f"○ {m_text}", key=f"main_{m_id}"):
                c.execute('UPDATE tasks SET status="done" WHERE id=?', (m_id,))
                conn.commit()
                st.rerun()
        # If it's a Project (has subtasks)
        else:
            # Use bolding and a distinct icon for the Vision
            if st.checkbox(f"**◈ {m_text.upper()}**", key=f"main_{m_id}"):
                c.execute('UPDATE tasks SET status="done" WHERE id=? OR parent_id=?', (m_id, m_id))
                conn.commit()
                st.rerun()
            
            # Indent the subtasks
            # Subtasks indented
            for s_id, s_text in subtasks:
                # We combine the L symbol AND the task text into the checkbox label itself
                # This removes the need for a separate st.write line
                if st.checkbox(f"&nbsp;&nbsp;&nbsp;&nbsp;└ {s_text}", key=f"sub_{s_id}"):
                    c.execute('UPDATE tasks SET status="done" WHERE id=?', (s_id,))
                    conn.commit()
                    st.rerun()
        
        

with tab3:
    st.header("Completed Tasks")
    items = c.execute('SELECT id,task,parent_id FROM tasks WHERE status="done"').fetchall()
    for c_id, c_text, p_id in items:
        # Show everything as checked by default (value=True)
        # If the user UNCHECKS it, the 'if' becomes False, triggering the 'else'
        is_checked = st.checkbox(f"{c_text}", value=True, key=f"done_{c_id}")
        
        if not is_checked:
            # Move it back to pending
            c.execute('UPDATE tasks SET status="pending" WHERE id=?', (c_id,))
            conn.commit()
            st.toast("Task restored to active list.")
            st.rerun()
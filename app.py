from flask import Flask, render_template, request, redirect
import sqlite3
import uuid
from datetime import datetime

app = Flask(__name__)
DATABASE = 'tasks.db'

def init_db():
    conn = sqlite3.connect(DATABASE)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            due_date TEXT
        )
    ''')
    conn.commit()
    conn.close()

def load_tasks():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cursor = conn.execute('SELECT * FROM tasks')
    tasks = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return tasks

def add_task(title, due_date=None):
    task_id = str(uuid.uuid4())
    conn = sqlite3.connect(DATABASE)
    conn.execute('INSERT INTO tasks (id, title, due_date) VALUES (?, ?, ?)', 
                 (task_id, title, due_date))
    conn.commit()
    conn.close()
    return task_id

def delete_task(task_id):
    conn = sqlite3.connect(DATABASE)
    conn.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
    conn.commit()
    conn.close()

@app.route('/')
def index():
    tasks = load_tasks()
    today = datetime.now().strftime('%Y-%m-%d')
    
    # Add status for each task based on due date
    for task in tasks:
        if task.get('due_date'):
            if task['due_date'] < today:
                task['status'] = 'overdue'
            elif task['due_date'] == today:
                task['status'] = 'due-today'
            else:
                task['status'] = 'upcoming'
    
    # Sort tasks by due date (None values last)
    tasks.sort(key=lambda x: x.get('due_date') or '9999-12-31')
    return render_template('index.html', tasks=tasks)

@app.route('/add', methods=['POST'])
def add():
    task_title = request.form.get('title')
    due_date = request.form.get('due_date')
    if task_title:
        add_task(task_title, due_date if due_date else None)
    return redirect('/')

@app.route('/delete/<task_id>', methods=['POST'])
def delete(task_id):
    delete_task(task_id)
    return redirect('/')

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)

from flask import Flask, render_template, request, redirect
import json
import os
import uuid
from datetime import datetime

app = Flask(__name__)
DATA_FILE = 'data.json'

def load_tasks():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return []

def save_tasks(tasks):
    with open(DATA_FILE, 'w') as f:
        json.dump(tasks, f)

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
        tasks = load_tasks()
        task = {'id': str(uuid.uuid4()), 'title': task_title}
        if due_date:
            task['due_date'] = due_date
        tasks.append(task)
        save_tasks(tasks)
    return redirect('/')

@app.route('/delete/<task_id>', methods=['POST'])
def delete(task_id):
    tasks = load_tasks()
    tasks = [task for task in tasks if task.get('id') != task_id]
    save_tasks(tasks)
    return redirect('/')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

import sqlite3
import uuid
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

def init_db():
    """データベースとテーブルの初期化"""
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            due_date TEXT
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    """メインページの表示 - タスクリスト込み"""
    tasks = load_tasks()
    return render_template('index.html', tasks=tasks)

def load_tasks():
    """SQLiteデータベースからタスクデータを読み込み"""
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, title, due_date FROM tasks ORDER BY due_date IS NULL, due_date')
    rows = cursor.fetchall()
    conn.close()
    
    tasks = []
    today = datetime.now().date()
    
    for row in rows:
        task = {
            'id': row[0],
            'title': row[1],
            'due_date': row[2]
        }
        
        # 締切状態の判定
        if task['due_date']:
            due_date = datetime.strptime(task['due_date'], '%Y-%m-%d').date()
            if due_date < today:
                task['status'] = 'overdue'
            elif due_date == today:
                task['status'] = 'due-today'
            else:
                task['status'] = 'upcoming'
        else:
            task['status'] = 'no-due-date'
        
        tasks.append(task)
    
    return tasks

@app.route('/add', methods=['POST'])
def add_task():
    """新規タスクの追加"""
    title = request.form.get('title', '').strip()
    due_date = request.form.get('due_date', '').strip()
    
    if title:
        add_task_to_db(title, due_date if due_date else None)
    
    return redirect(url_for('index'))

def add_task_to_db(title, due_date):
    """新しいタスクをデータベースに追加"""
    task_id = str(uuid.uuid4())
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO tasks (id, title, due_date) VALUES (?, ?, ?)', 
                   (task_id, title, due_date))
    conn.commit()
    conn.close()

@app.route('/delete/<task_id>', methods=['POST'])
def delete_task_route(task_id):
    """指定されたタスクの削除"""
    delete_task(task_id)
    return redirect(url_for('index'))

def delete_task(task_id):
    """指定されたタスクをデータベースから削除"""
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)

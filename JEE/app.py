from flask import Flask, render_template, request, jsonify
import sqlite3
import os

app = Flask(__name__)
app.config['DATABASE'] = os.path.join(app.instance_path, 'jee_results.db')

# Initialize the database
def init_db():
    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    conn = sqlite3.connect(app.config['DATABASE'])
    cursor = conn.cursor()
    
    # Create table for JEE results
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        registration_number TEXT UNIQUE NOT NULL,
        student_name TEXT NOT NULL,
        physics_marks REAL NOT NULL,
        chemistry_marks REAL NOT NULL,
        mathematics_marks REAL NOT NULL,
        total_marks REAL NOT NULL,
        percentile REAL NOT NULL
    )
    ''')
    
    # Insert some sample data if table is empty
    cursor.execute("SELECT COUNT(*) FROM results")
    if cursor.fetchone()[0] == 0:
        sample_data = [
            ('JEE2025001', 'Rahul Sharma', 85.5, 90.0, 95.5, 271.0, 98.5),
            ('JEE2025002', 'Priya Patel', 80.0, 92.5, 88.0, 260.5, 96.8),
            ('JEE2025003', 'Amit Kumar', 92.0, 78.5, 89.0, 259.5, 96.5),
            ('JEE2025004', 'Sneha Gupta', 88.5, 91.0, 94.5, 274.0, 99.1),
            ('JEE2025005', 'Raj Singh', 75.0, 82.5, 79.0, 236.5, 89.7)
        ]
        cursor.executemany('''
        INSERT INTO results 
        (registration_number, student_name, physics_marks, chemistry_marks, mathematics_marks, total_marks, percentile) 
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', sample_data)
    
    conn.commit()
    conn.close()

# Get results from database
def get_result(registration_number):
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT * FROM results WHERE registration_number = ?", 
        (registration_number,)
    )
    result = cursor.fetchone()
    
    conn.close()
    
    if result:
        return dict(result)
    return None

# Initialize database before first request (replacement for the deprecated before_first_request)
@app.route('/init-db')
def initialize_database():
    init_db()
    return "Database initialized successfully!"

@app.route('/')
def index():
    # Initialize the database when the app starts
    init_db()
    return render_template('index.html')

@app.route('/get_result', methods=['POST'])
def fetch_result():
    registration_number = request.form.get('registration_number')
    
    if not registration_number:
        return jsonify({'error': 'Registration number is required'}), 400
    
    result = get_result(registration_number)
    
    if result:
        return jsonify({'success': True, 'result': result})
    else:
        return jsonify({'success': False, 'message': 'No result found for this registration number'})

if __name__ == '__main__':
    # Initialize the database before running the app
    with app.app_context():
        init_db()
    app.run(debug=True)
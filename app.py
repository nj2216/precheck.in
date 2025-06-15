# PHC MVP Web App using Flask + SQLite + Together AI for Dynamic Question Generation

from flask import Flask, render_template, request, redirect, url_for, session, g
from datetime import datetime
import sqlite3
import os
import requests

app = Flask(__name__)
app.secret_key = 'phc_secret_key'
DATABASE = 'phc.db'
TOGETHER_API_KEY = '94ecfbf48815fad192c32d470cb5e1f3c35adc672797748a245bfb91040a86ad'  # Replace with your free Together AI key

# --- DB Setup ---
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS patients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                dob TEXT NOT NULL,
                age INTEGER NOT NULL,  -- Optional, can be calculated from dob
                email TEXT NULL,
                mobile TEXT NOT NULL,
                gender TEXT NOT NULL,
                blood_group TEXT NOT NULL,
                aadhar_number TEXT NOT NULL,
                reason TEXT NOT NULL,
                questions TEXT,            -- Optional, if you want to store questionnaire
                answers TEXT,              -- Optional, if you want to store answers
                token INTEGER,             -- Auto-assigned token number for queueing
                time TEXT DEFAULT CURRENT_TIMESTAMP,
                seen INTEGER DEFAULT 0,
                doctor_notes TEXT DEFAULT ''
            )
        ''')
        db.commit()

init_db()
# Initialize the database if it doesn't exist

def generate_questions_ai(symptom_desc):
    prompt = (
        f"The patient described the following issue: \"{symptom_desc}\".\n"
        "Generate exactly 5 relevant medical follow-up questions in bullet points that a doctor would ask "
        "before diagnosis. Keep the questions clear and short."
    )

    headers = {
        "Authorization": f"Bearer {TOGETHER_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
        "prompt": prompt,
        "max_tokens": 256,
        "temperature": 0.7,
        "top_p": 0.9,
        "top_k": 50
    }

    res = requests.post("https://api.together.xyz/v1/completions", headers=headers, json=data)

    if res.status_code == 200:
        try:
            output_text = res.json()["choices"][0]["text"]
            questions = [line.strip("•-1234567890. ").strip() for line in output_text.strip().split("\n") if line.strip()]
            return questions[:5] if len(questions) >= 5 else questions + ["(More needed)"] * (5 - len(questions))
        except Exception as e:
            print("Parsing error:", e)
            return ["Error in parsing AI response."] * 5
    else:
        print("API Error:", res.status_code, res.text)
        return ["Could not generate questions, please try again."] * 5


# --- Static Question Sets ---
symptom_questions = {
    # [same content as before for predefined sets]
    # unchanged to save space, assumed present
}

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        print("Form submitted")
        print(request.form)
        return redirect(url_for('submit'))
    return render_template('index.html')

@app.route('/submit', methods=['GET', 'POST'])
def submit():
    if request.method != 'POST':
        return render_template('personal.html')
    name = request.form['name']
    dob = request.form['dob']
    age = datetime.now().year - int(dob.split('-')[0])
    email = request.form['email']
    mobile = request.form['mobile']
    gender = request.form['cars']
    blood_group = request.form['blood_group']
    aadhar_number = request.form['aadharNum']
    reason = request.form['reason'].lower()
    # Store in session for questions page
    session['temp_patient'] = {
        'name': name,
        'dob': dob,
        'age': age,  # Calculate age from dob
        'email': email,
        'mobile': mobile,
        'gender': gender,
        'blood_group': blood_group,
        'aadhar_number': aadhar_number,
        'reason': reason
    }
    # Insert into DB with minimal info (questions/answers will be updated later)
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT MAX(token) FROM patients")
    last_token = cursor.fetchone()[0] or 0
    token = last_token + 1
    cursor.execute('''INSERT INTO patients 
        (name, dob, age, email, mobile, gender, blood_group, aadhar_number, reason, token, time) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
        (name, dob, age, email, mobile, gender, blood_group, aadhar_number, reason, token, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    db.commit()
    session['current_token'] = token
    return redirect(url_for('questions'))

@app.route('/edit_submit/<int:token>', methods=['GET', 'POST'])
def edit_submit(token):
    db = get_db()
    cursor = db.cursor()
    if request.method == 'GET':
        patient = cursor.execute("SELECT * FROM patients WHERE token=?", (token,)).fetchone()
        if not patient:
            return "Patient not found", 404
        return render_template('edit-personal.html', person=patient)
    # POST: update patient info
    name = request.form['name']
    dob = request.form['dob']
    age = datetime.now().year - int(dob.split('-')[0])  # Calculate age from dob
    email = request.form['email']
    mobile = request.form['mobile']
    gender = request.form['gender']
    blood_group = request.form['blood_group']
    aadhar_number = request.form['aadharNum']
    cursor.execute('''UPDATE patients SET
        name=?, dob=?, age=?, email=?, mobile=?, gender=?, blood_group=?, aadhar_number=?
        WHERE token=?''',
        (name, dob, age, email, mobile, gender, blood_group, aadhar_number, token))
    db.commit()
    return redirect(url_for('token_page', token=token))


@app.route('/questions', methods=['GET', 'POST'])
def questions():
    if request.method == 'GET':
        symptoms = session.get('temp_patient', {}).get('reason', '')
        keyword = next((key for key in symptom_questions if key in symptoms), None)
        if keyword:
            questions_list = symptom_questions.get(keyword, [])
        else:
            questions_list = generate_questions_ai(symptoms)
        session['selected_questions'] = questions_list
        return render_template('questions.html', questions=questions_list)
    else:
        answers = [request.form.get(f'q{i}') for i in range(5)]
        patient = session.pop('temp_patient', {})
        questions_list = session.pop('selected_questions', [])
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT MAX(token) FROM patients")
        last_token = cursor.fetchone()[0] or 0
        token = last_token + 1
        cursor.execute('''UPDATE patients SET questions=?, answers=? WHERE token=?''',
                   ('|'.join(questions_list), '|'.join(answers), session.get('current_token')))
        db.commit()
        return redirect(url_for('token_page', token=token-1))
        return redirect(url_for('queue_page'))

@app.route('/edit_answers/<int:token>', methods=['GET', 'POST'])
def edit_answers(token):
    db = get_db()
    cursor = db.cursor()
    if request.method == 'GET':
        patient = cursor.execute("SELECT * FROM patients WHERE token=?", (token,)).fetchone()
        if not patient:
            return "Patient not found", 404
        questions = patient['questions'].split('|') if patient['questions'] else []
        answers = patient['answers'].split('|') if patient['answers'] else []
        return render_template('edit-answers.html', patient=patient, questions=questions, answers=answers)
    else:
        # Get the original questions
        patient = cursor.execute("SELECT * FROM patients WHERE token=?", (token,)).fetchone()
        if not patient:
            return "Patient not found", 404
        questions = patient['questions'].split('|') if patient['questions'] else []
        # Collect edited answers from form fields named q0, q1, ...
        answers = [request.form.get(f'q{i}', '') for i in range(len(questions))]
        cursor.execute('''UPDATE patients SET answers=? WHERE token=?''',
                   ('|'.join(answers), token))
        db.commit()
        return redirect(url_for('token_page', token=token))

@app.route('/token/<int:token>')
def token_page(token):
    db = get_db()
    cursor = db.cursor()
    patient = cursor.execute("SELECT * FROM patients WHERE token=?", (token,)).fetchone()
    if not patient:
        return "Patient not found", 404
    return render_template('token.html', patient=patient)

@app.route('/queue')
def queue_page():
    db = get_db()
    cursor = db.cursor()
    # Get all patients who are not yet seen, ordered by token (queue)
    queue = cursor.execute("SELECT * FROM patients WHERE seen=0 ORDER BY token ASC").fetchall()
    # Get all patients who have been seen, ordered by token
    seen = cursor.execute("SELECT * FROM patients WHERE seen=1 ORDER BY token ASC").fetchall()
    return render_template('queue.html', queue=queue, seen=seen)

@app.route('/doctor', methods=['GET', 'POST'])
def doctor():
    db = get_db()
    cursor = db.cursor()
    if request.method == 'POST':
        notes = request.form['notes']
        token = request.form['token']
        cursor.execute("UPDATE patients SET doctor_notes=?, seen=1 WHERE token=?", (notes, token))
        db.commit()
        return redirect(url_for('doctor'))

    next_patient = cursor.execute("SELECT * FROM patients WHERE seen=0 ORDER BY token ASC LIMIT 1").fetchone()

    if next_patient:
        questions = next_patient["questions"].split('|') if next_patient["questions"] else []
        answers = next_patient["answers"].split('|') if next_patient["answers"] else []
        qa_pairs = list(zip(questions, answers))
    else:
        qa_pairs = []

    return render_template('doctor.html', patient=next_patient, qa_pairs=qa_pairs)


if __name__ == '__main__':
    if not os.path.exists(DATABASE):
        open(DATABASE, 'w').close()
    app.run(debug=True)

import sqlite3
import os
import requests
from dotenv import load_dotenv
from flask import Flask, render_template, request, flash, redirect, url_for

# Load hidden environment variables
load_dotenv()

app = Flask(__name__)
# Secret key for session/flash messages. In production, use os.environ.get('SECRET_KEY')
app.secret_key = 'super_secret_feedback_key_123'

DB_PATH = 'feedback.db'

# Telegram Configuration
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def send_telegram_message(name, rating, experience):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram bot token or chat ID not set. Skipping Telegram notification.")
        return False
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    message = (
        f"New Feedback Received:\n"
        f"Name: {name}\n"
        f"Rating: {rating}\n"
        f"Experience: {experience}"
    )
    
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message
    }
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return True
    except Exception as e:
        print(f"Failed to send Telegram message: {e}")
        return False

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    student_name = request.form.get('student_name', '').strip()
    email = request.form.get('email', '').strip()
    rating = request.form.get('rating')
    experience = request.form.get('experience', '').strip()
    
    if not student_name or not email or not rating:
        flash("Please fill out all required fields.", "error")
        return redirect(url_for('index'))
    
    # Save to database
    try:
        conn = get_db_connection()
        conn.execute(
            'INSERT INTO responses (student_name, email, rating, experience) VALUES (?, ?, ?, ?)',
            (student_name, email, rating, experience)
        )
        conn.commit()
        conn.close()
    except Exception as e:
        flash("An error occurred while saving your feedback.", "error")
        print(f"Database error: {e}")
        return redirect(url_for('index'))
    
    # Send Telegram notification
    send_telegram_message(student_name, rating, experience)
    
    flash("Thank you! Your feedback has been submitted successfully.", "success")
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)

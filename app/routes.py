import requests
from flask import Blueprint, request, jsonify
from app.model import model  # Assuming model.py has some functions or classes for prediction
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv
from my_library.message_processor import process_message  # Adjusted import statement

bp = Blueprint('local', __name__)

@bp.route('/predict', methods=['POST'])
def predict():
    data = request.get_json(force=True)
    prediction = model.predict([data['input']])
    return jsonify({'prediction': prediction.tolist()})

@bp.route('/modify_text', methods=['POST'])
def modify_text():
    data = request.get_json(force=True)
    input_text = data.get('text')
    if (input_text):
        try:
            response = requests.post(
                'http://localhost:11434/api/generate',
                json={
                    'model': 'llama3',
                    'prompt': input_text,
                    'stream': False
                }
            )
            response.raise_for_status()  # Raises an HTTPError if the HTTP request returned an unsuccessful status code
            response_data = response.json()
            modified_text = response_data.get('response', 'Error processing text')
            return jsonify({'modified_text': modified_text})
        except requests.exceptions.RequestException as e:
            return jsonify({'error': f'Failed to connect to Ollama: {str(e)}'}), 500
        except ValueError as e:
            return jsonify({'error': f'Failed to parse response from Ollama: {str(e)}'}), 500
    else:
        return jsonify({'error': 'No text provided'}), 400

@bp.route('/send-email', methods=['POST'])
def handle_send_email():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    message = data.get('message')

    subject = f'Contact Form Submission from {name}'
    body = f"Name: {name}\nEmail: {email}\n\nMessage:\n{message}"

    if (send_email('mcgowee@gmail.com', subject, body)):
        return jsonify({'message': 'Email sent successfully!'}), 200
    else:
        return jsonify({'error': 'Failed to send email'}), 500

@bp.route('/sql-chat', methods=['POST'])
def sql_msg():
    data = request.get_json()
    if (not data or 'message' not in data):
        return jsonify({'error': 'Bad Request - message field is required'}), 400
    message = data.get('message', '')
    processed_message = process_message(message)
    return jsonify({'message': processed_message})

# Load environment variables from .env file
load_dotenv()

# Email configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_USERNAME = os.getenv('EMAIL_USERNAME')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')

def send_email(to_address, subject, body):
    from_address = EMAIL_USERNAME

    # Create the email message
    msg = MIMEMultipart()
    msg['From'] = from_address
    msg['To'] = to_address
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        # Connect to the server and send email
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
        text = msg.as_string()
        server.sendmail(from_address, to_address, text)
        server.quit()
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False

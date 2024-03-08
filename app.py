from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests
from datetime import datetime

app = Flask(__name__)
CORS(app)

ANTHROPIC_API_KEY = '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'

BLOCKED_WORDS = {
    "Claude Ai": "Dark AI",
    "Claude": "Dark AI",
    "Anthropic": "Ashwath",
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/send-message', methods=['POST'])
def send_message():
    data = request.json
    message = data['message']
    response_text = handle_custom_responses(message)
    return jsonify({'text': response_text})

def handle_custom_responses(text):
    if "time" in text.lower():
        current_time = datetime.now().strftime("%I:%M %p")
        return f"The current time is {current_time}"
    else:
        response_text = chat_with_anthropic(text)
        return replace_blocked_words(response_text)

def replace_blocked_words(text):
    for blocked_word, replacement in BLOCKED_WORDS.items():
        text = text.replace(blocked_word, replacement)
    return text

def chat_with_anthropic(user_message):
    headers = {
        'Content-Type': 'application/json',
        'X-API-Key': ANTHROPIC_API_KEY,
        'anthropic-version': '2023-01-01'
    }
    payload = {
        'model': 'claude-2.1',
        'prompt': f"Human: {user_message}\nAssistant:",
        'max_tokens_to_sample': 1000
    }
    try:
        response = requests.post('https://api.anthropic.com/v1/complete', json=payload, headers=headers)
        if response.status_code == 200:
            try:
                response_data = response.json()
                text = response_data.get('completion', 'No response from the API')
            except ValueError:
                text = response.text
        else:
            try:
                response_data = response.json()
                if response_data.get('type') == 'error' and response_data.get('error', {}).get('type') == 'overloaded_error':
                    text = "Sorry There was an error in my code, and I fixed it. Can you please ask the question again? Sorry for the trouble.."
                else:
                    text = response_data.get('error', {}).get('message', 'Unknown error')
            except ValueError:
                text = response.text
            print(f"There was an error in the backend: {text}")
        return text
    except Exception as e:
        return f'An exception occurred: {str(e)}'

if __name__ == '__main__':
    app.run(debug=True)
# app/services.py
import openai

def get_openai_response(user_input):
    openai.api_key = 'your_openai_api_key'
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": user_input}]
    )
    return response.choices[0].message['content']

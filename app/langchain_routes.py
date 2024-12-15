# Project: langchain
# File Location: app/langchain_routes.py
# Author: Earl McGowen
# Date Created: 7/14/2024
# Date Last Modified: 7/14/2024
# Description: This file contains the routes for the LangChain API.

from flask import request, Blueprint, jsonify
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
from langchain_huggingface import HuggingFacePipeline
from langchain_community.utilities import SQLDatabase
from langchain.chains import create_sql_query_chain
import sqlite3

import openai
from langsmith.wrappers import wrap_openai
from langsmith import traceable

bp_langchain = Blueprint('langchain', __name__)

# Initialize the Hugging Face model and tokenizer
model_name = 'gpt2'
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

# Initialize the Hugging Face pipeline
generator = pipeline('text-generation', model=model, tokenizer=tokenizer)

# Initialize the SQLDatabase
db = SQLDatabase.from_uri("sqlite:///database/Chinook.db")

# Create the SQL query chain
llm_pipeline = HuggingFacePipeline(pipeline=generator)
chain = create_sql_query_chain(llm_pipeline, db)

@bp_langchain.route('/api/hello', methods=['GET', 'POST'])
def hello():
    try:
        if request.method == 'POST':
            return 'Hello, World!', 200
        else:
            return 'Hello, World!', 200
    except Exception as e:
        return str(e), 500

@bp_langchain.route('/api/generate', methods=['POST'])
def generate():
    try:
        data = request.json
        prompt = data.get('prompt', '')

        # Generate text using the Hugging Face model
        result = generator(prompt, max_new_tokens=150)

        return jsonify({'result': result[0]['generated_text']})
    except Exception as e:
        return str(e), 500

@bp_langchain.route('/api/query', methods=['POST'])
def query():
    try:
        data = request.json
        question = data.get('question', '')

        # Generate the SQL query from the question
        input_text = f"translate English to SQL: {question}"
        inputs = tokenizer.encode(input_text, return_tensors="pt", max_length=512, truncation=True)
        outputs = model.generate(inputs, max_new_tokens=150, num_beams=4, early_stopping=True)
        sql_query = tokenizer.decode(outputs[0], skip_special_tokens=True)

        # Log the generated SQL query for debugging
        print(f"Generated SQL Query: {sql_query}")

        # Run the generated SQL query
        result = db.run(sql_query)

        return jsonify({'response': result})
    except Exception as e:
        return str(e), 500

@bp_langchain.route('/api/langsmith', methods=['GET'])
def get_langsmith():
    try:
        # Auto-trace LLM calls in-context
        client = wrap_openai(openai.Client())

        @traceable # Auto-trace this function
        def pipeline(user_input: str):
            result = client.chat.completions.create(
                messages=[{"role": "user", "content": user_input}],
                model="gpt-3.5-turbo"
            )
            return result.choices[0].message.content

        # pipeline("Hello, world!")
        response_text = pipeline("Hello, world!")
        # Out:  Hello there! How can I assist you today?
        
        return jsonify({'response': response_text})
    except Exception as e:
        return str(e), 500

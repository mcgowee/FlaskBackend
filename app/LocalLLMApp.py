# Project: LocalLLMApp
# File Location: app/LocalLLMApp.py
# Author: Earl McGowen
# Date Created: 7/14/2024
# Date Last Modified: 7/14/2024
# Description: This file contains the routes for the LocalLLM API.

from flask import Blueprint, request, jsonify
from pandasai.llm.local_llm import LocalLLM
from pandasai.connectors import MySQLConnector
from pandasai import SmartDataframe

bp_pandasai = Blueprint('pandasai', __name__)

# Create a MySQLConnector object
my_connector = MySQLConnector(
    config={
        "host": "localhost",
        "port": 3306,
        "database": "customer_behaviour",
        "username": "root",
        "password": "4Feedom!",
        "table": "customer",
    }
)

# Create a LocalLLM object
model = LocalLLM(
    api_base="http://localhost:11434/v1",
    model="llama3",
)

df_connector = SmartDataframe(my_connector, config={"llm": model})

@bp_pandasai.route('/api/pandasai', methods=['POST'])
def query_request():
    try:
        data = request.json
        user_input = data.get('text', '')

        response = df_connector.chat(user_input)
        return jsonify({'response': response})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

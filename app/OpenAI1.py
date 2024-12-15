# Project: OpenAI1
# File Location: app/OpenAI1.py
# Author: Earl McGowen
# Date Created: 7/14/2024
# Date Last Modified: 7/14/2024
# Description: This file contains the routes for the OpenAI API.

from flask import Blueprint, request, jsonify
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.utilities import SQLDatabase
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough # RunnablePassthrough class is used to pass the query to the next step in the chain
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool # QuerySQLDataBaseTool class is used to execute the SQL query
from langchain.chains import create_sql_query_chain
from operator import itemgetter


from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent


bp_openai = Blueprint('openai', __name__)

@bp_openai.route('/api/translation', methods=['POST'])
def translation_request():
    try:
        data = request.json
        user_input = data.get('text', '')

        messages = [
            SystemMessage(content="Translate the following from English into Italian"),
            HumanMessage(content=user_input),
        ]
        model = ChatOpenAI(model="gpt-4")

        # Invoke the model with the messages and parse the result
        ai_message = model.invoke(messages)
        parser = StrOutputParser()  
        parsed_result = parser.invoke(ai_message.content)  # Ensure .content is used to get the string

        return jsonify({'response': parsed_result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp_openai.route('/api/customTranslation', methods=['POST'])
def custom_translation_request():
    try:
        data = request.json
        user_input = data.get('text', '')
        user_language = data.get('language', 'italian')  # Default to 'italian' if not provided

        # Define the system and user message templates
        system_template = "Translate the following into {language}:"
        prompt_template = ChatPromptTemplate.from_messages(
            [("system", system_template), ("user", "{text}")]
        )

        # Initialize the model
        model = ChatOpenAI(model="gpt-4")

        # Initialize the parser
        parser = StrOutputParser()

        # Chain together the prompt template, model, and parser
        chain = prompt_template | model | parser

        # Invoke the chain with the given inputs
        result = chain.invoke({"language": user_language, "text": user_input})

        return jsonify({'response': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp_openai.route('/api/sql_qa', methods=['POST'])
def sql_qa_request():
    try:
        data = request.json
        user_input = data.get('question', '')
        
        # Initialize the model
        llm = ChatOpenAI(model="gpt-3.5-turbo-0125")
        # Initialize the SQL database connection
        db = SQLDatabase.from_uri("sqlite:///database/Chinook.db")

        # Initialize the SQL query chain
        execute_query = QuerySQLDataBaseTool(db=db)
        write_query = create_sql_query_chain(llm, db)

        # Define the prompt template
        answer_prompt = PromptTemplate.from_template(
            """Given the following user question, corresponding SQL query, and SQL result, answer the user question.

        Question: {question}
        SQL Query: {query}
        SQL Result: {result}
        Answer: """
        )

        # Create the SQL query chain
        chain = (
            RunnablePassthrough.assign(query=write_query).assign(
                result=itemgetter("query") | execute_query
            )
            | answer_prompt
            | llm
            | StrOutputParser()
        )

        # Invoke the chain with the user's query
        result = chain.invoke({"question": user_input})

        return jsonify({'response': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@bp_openai.route('/api/chatbot_query', methods=['POST'])
def chatbot_query():
    try:
        data = request.json
        user_question = data.get('question', '')

        # Initialize the model
        llm = ChatOpenAI(model="gpt-3.5-turbo-0125")
        # Initialize the SQL database connection
        db = SQLDatabase.from_uri("sqlite:///database/Chinook.db")

        # Get the tools from the SQL database toolkit
        toolkit = SQLDatabaseToolkit(db=db, llm=llm)
        tools = toolkit.get_tools()

        SQL_PREFIX = """You are an agent designed to interact with a SQL database.
        Given an input question, create a syntactically correct SQLite query to run, then look at the results of the query and return the answer.
        Unless the user specifies a specific number of examples they wish to obtain, always limit your query to at most 5 results.
        You can order the results by a relevant column to return the most interesting examples in the database.
        Never query for all the columns from a specific table, only ask for the relevant columns given the question.
        You have access to tools for interacting with the database.
        Only use the below tools. Only use the information returned by the below tools to construct your final answer.
        You MUST double check your query before executing it. If you get an error while executing a query, rewrite the query and try again.

        DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.) to the database.

        To start you should ALWAYS look at the tables in the database to see what you can query.
        Do NOT skip this step.
        Then you should query the schema of the most relevant tables."""

        system_message = SystemMessage(content=SQL_PREFIX)

        agent_executor = create_react_agent(llm, tools, messages_modifier=system_message)

        responses = []
        for s in agent_executor.stream(
            {"messages": [HumanMessage(content=user_question)]}
            # Which country's customers spent the most?
        ):
            if 'agent' in s and 'messages' in s['agent']:
                for message in s['agent']['messages']:
                    if hasattr(message, 'content'):
                        responses.append(message.content)
                        print(message.content)



        response_text = " ".join(responses)

        return jsonify({'response': response_text})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Import necessary modules from the langchain_community and langchain_core packages
from langchain_community.chat_models import ChatOllama
from langchain_community.utilities import SQLDatabase
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
import json

# Initialize the ChatOllama model with specific parameters
# This model is used to generate SQL queries based on natural language questions
local_llm = "llama3"
llm = ChatOllama(model=local_llm, format="json", temperature=0)

# Initialize a connection to a SQLite database using the SQLDatabase utility
# The database file is located at a specific path on the user's machine
db = SQLDatabase.from_uri('sqlite:///C:\\Users\\mcgow\\Documents\\jupyter\\Chinook.db', sample_rows_in_table_info=0)

def get_schema(_):
    """
    Function to retrieve the schema of the database.
    This schema will be used to inform the model about the structure of the database.
    """
    return db.get_table_info()

def run_query(query):
    """
    Function to execute a SQL query against the database.
    """
    return db.run(query)

# Template for generating the prompt to be sent to the ChatOllama model
# This template includes the schema of the database and the user's question
# The model is expected to generate a SQL query based on this information
template = """Based on the table schema below, write a SQL query that would answer the user's question:
{schema}

Question: {question}
SQL Query:"""



# Create a ChatPromptTemplate instance with predefined messages
# This instance is used to format the input for the ChatOllama model
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "Given an input question, convert it to a SQL query. No pre-amble."),
        ("human", template),
    ]
)

# Define the sequence of operations to process a message and generate a SQL query
# This includes getting the schema, formatting the prompt, invoking the model, and parsing the output
sql_response = (
    RunnablePassthrough.assign(schema=get_schema)
    | prompt
    | llm.bind(stop=["\nSQLResult:"])
    | StrOutputParser()
)


def process_message(question):
    """
    Function to process a natural language question and return a SQL query.
    This function uses the sql_response sequence defined above.
    """
    # answer = sql_response.invoke({"question": question})

    # Given JSON string
    json_str = sql_response.invoke({"question": question})
    # Parse the JSON string
    parsed_json = json.loads(json_str)
    # Extract the SELECT statement
    select_statement = parsed_json['query']

    template = """Based on the table schema below, question, sql query, and sql response, write a natural language response:
    {schema}

    Question: {question}
    SQL Query: {query}
    SQL Response: {response}"""
    prompt_response = ChatPromptTemplate.from_template(template)

    def run_query(query):
        return db.run(query)

    full_chain = (
        RunnablePassthrough.assign(query=sql_response).assign(
            schema=get_schema,
            response=lambda vars: run_query(select_statement),
        )
        | prompt_response
        | llm
    )

    user_question = question
    answer = full_chain.invoke({"question": user_question})

    return f"Processed message: {answer}"
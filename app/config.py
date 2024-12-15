# Project: OpenAI1
# File Location: app/config.py
# Author: Earl McGowen
# Date Created: 7/14/2024
# Date Last Modified: 7/14/2024
# Description: This file contains the configuration settings for the app.

import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'my_secret_key')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

"""
Configuration module for the RAG Chatbot.
Loads settings from environment variables.
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Gemini API Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = "gemini-2.0-flash"

# RAG Settings
TOP_K_RESULTS = 5  # Number of chunks to retrieve
MAX_CONTEXT_LENGTH = 4000  # Max characters for context

# Server Settings
PORT = int(os.getenv("PORT", 5000))
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

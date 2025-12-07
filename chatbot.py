"""
Main Chatbot module using Gemini 2.0 Flash with RAG.
"""
import google.generativeai as genai
from typing import List, Dict, Optional

from config import GEMINI_API_KEY, GEMINI_MODEL, MAX_CONTEXT_LENGTH
from retriever import get_retriever


# System prompt template
SYSTEM_PROMPT = """You are a helpful assistant for NavShiksha, an education platform developed for Smart India Hackathon 2025.

Your role is to:
1. Answer questions about NavShiksha's features and functionalities
2. Guide users on how to use the platform (students, teachers, admins)
3. Explain the technical aspects like blockchain certificates, whiteboard, audio/video classes
4. Be friendly, concise, and helpful

IMPORTANT RULES:
- Only answer based on the provided context
- If the information is not in the context, politely say you don't have that information
- Keep responses clear and to the point
- Use bullet points or numbered lists for step-by-step instructions
- If asked about something unrelated to NavShiksha, redirect to platform-related help
"""

RAG_PROMPT_TEMPLATE = """Based on the following context from NavShiksha knowledge base, answer the user's question.

CONTEXT:
{context}

USER QUESTION: {question}

ANSWER:"""


class Chatbot:
    """RAG Chatbot using Gemini 2.0 Flash."""
    
    def __init__(self):
        if not GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        # Configure Gemini
        genai.configure(api_key=GEMINI_API_KEY)
        
        # Initialize model
        self.model = genai.GenerativeModel(
            model_name=GEMINI_MODEL,
            system_instruction=SYSTEM_PROMPT
        )
        
        # Initialize retriever
        self.retriever = get_retriever()
        
        # Conversation history
        self.history: List[Dict[str, str]] = []
        
        print(f"Chatbot initialized with model: {GEMINI_MODEL}")
    
    def _build_prompt(self, question: str) -> str:
        """Build RAG prompt with retrieved context."""
        context = self.retriever.get_context(question)
        
        # Truncate context if too long
        if len(context) > MAX_CONTEXT_LENGTH:
            context = context[:MAX_CONTEXT_LENGTH] + "..."
        
        return RAG_PROMPT_TEMPLATE.format(context=context, question=question)
    
    def chat(self, user_message: str) -> str:
        """
        Process user message and return response.
        
        Args:
            user_message: User's question/message
            
        Returns:
            Chatbot's response
        """
        try:
            # Build RAG prompt
            prompt = self._build_prompt(user_message)
            
            # Include conversation history for context
            messages = []
            for turn in self.history[-4:]:  # Last 4 turns
                messages.append({"role": "user", "parts": [turn["user"]]})
                messages.append({"role": "model", "parts": [turn["assistant"]]})
            
            # Add current prompt
            messages.append({"role": "user", "parts": [prompt]})
            
            # Generate response
            if messages:
                chat = self.model.start_chat(history=messages[:-1])
                response = chat.send_message(prompt)
            else:
                response = self.model.generate_content(prompt)
            
            assistant_response = response.text
            
            # Store in history
            self.history.append({
                "user": user_message,
                "assistant": assistant_response
            })
            
            return assistant_response
            
        except Exception as e:
            error_msg = f"Error generating response: {str(e)}"
            print(error_msg)
            return f"I'm sorry, I encountered an error. Please try again. ({str(e)})"
    
    def clear_history(self):
        """Clear conversation history."""
        self.history = []
        print("Conversation history cleared.")
    
    def get_history(self) -> List[Dict[str, str]]:
        """Get conversation history."""
        return self.history


# Singleton instance
_chatbot_instance: Optional[Chatbot] = None


def get_chatbot() -> Chatbot:
    """Get or create the chatbot singleton."""
    global _chatbot_instance
    if _chatbot_instance is None:
        _chatbot_instance = Chatbot()
    return _chatbot_instance


if __name__ == "__main__":
    # Test the chatbot
    bot = get_chatbot()
    
    test_questions = [
        "What is NavShiksha?",
        "How do I join a live class as a student?",
        "Tell me about the whiteboard features"
    ]
    
    for q in test_questions:
        print(f"\n{'='*60}")
        print(f"User: {q}")
        print(f"{'='*60}")
        response = bot.chat(q)
        print(f"\nAssistant: {response}")

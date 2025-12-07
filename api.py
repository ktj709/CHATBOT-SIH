"""
FastAPI Application for NavShiksha RAG Chatbot.
Deployable to Render with Uvicorn.
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional

from chatbot import get_chatbot
from config import PORT

# Create FastAPI app
app = FastAPI(
    title="NavShiksha Chatbot API",
    description="RAG-based chatbot for NavShiksha education platform",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models
class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str


class HealthResponse(BaseModel):
    status: str
    service: str


# HTML Template for the chat interface
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NavShiksha Assistant</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
            min-height: 100vh;
            color: #e4e4e7;
        }
        
        .container {
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }
        
        header {
            text-align: center;
            padding: 30px 0;
        }
        
        h1 {
            font-size: 2.5rem;
            background: linear-gradient(90deg, #e94560, #ff6b9d);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 10px;
        }
        
        .subtitle {
            color: #a1a1aa;
            font-size: 1rem;
        }
        
        .chat-container {
            flex: 1;
            background: rgba(255, 255, 255, 0.03);
            border-radius: 20px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }
        
        .messages {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
            display: flex;
            flex-direction: column;
            gap: 15px;
        }
        
        .message {
            max-width: 80%;
            padding: 15px 20px;
            border-radius: 18px;
            line-height: 1.5;
            animation: fadeIn 0.3s ease;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .user-message {
            align-self: flex-end;
            background: linear-gradient(135deg, #e94560, #ff6b9d);
            color: white;
            border-bottom-right-radius: 5px;
        }
        
        .bot-message {
            align-self: flex-start;
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-bottom-left-radius: 5px;
        }
        
        .input-container {
            padding: 20px;
            background: rgba(0, 0, 0, 0.2);
            display: flex;
            gap: 10px;
        }
        
        #user-input {
            flex: 1;
            padding: 15px 20px;
            border: none;
            border-radius: 25px;
            background: rgba(255, 255, 255, 0.1);
            color: white;
            font-size: 1rem;
            outline: none;
            transition: all 0.3s ease;
        }
        
        #user-input:focus {
            background: rgba(255, 255, 255, 0.15);
            box-shadow: 0 0 20px rgba(233, 69, 96, 0.2);
        }
        
        #user-input::placeholder {
            color: #71717a;
        }
        
        button {
            padding: 15px 30px;
            border: none;
            border-radius: 25px;
            background: linear-gradient(135deg, #e94560, #ff6b9d);
            color: white;
            font-size: 1rem;
            cursor: pointer;
            transition: all 0.3s ease;
            font-weight: 600;
        }
        
        button:hover {
            transform: scale(1.05);
            box-shadow: 0 5px 20px rgba(233, 69, 96, 0.4);
        }
        
        button:disabled {
            opacity: 0.5;
            cursor: not-allowed;
            transform: none;
        }
        
        .loading {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid #fff;
            border-radius: 50%;
            border-top-color: transparent;
            animation: spin 1s linear infinite;
        }
        
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        
        .welcome-message {
            text-align: center;
            padding: 40px;
            color: #a1a1aa;
        }
        
        .welcome-message h2 {
            margin-bottom: 15px;
            color: #e4e4e7;
        }
        
        .suggestions {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            justify-content: center;
            margin-top: 20px;
        }
        
        .suggestion {
            padding: 10px 20px;
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 20px;
            cursor: pointer;
            transition: all 0.3s ease;
            font-size: 0.9rem;
        }
        
        .suggestion:hover {
            background: rgba(233, 69, 96, 0.2);
            border-color: #e94560;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🎓 NavShiksha Assistant</h1>
            <p class="subtitle">Your AI guide to the NavShiksha education platform (FastAPI)</p>
        </header>
        
        <div class="chat-container">
            <div class="messages" id="messages">
                <div class="welcome-message">
                    <h2>Welcome! 👋</h2>
                    <p>I can help you learn about NavShiksha - courses, live classes, certificates, and more!</p>
                    <div class="suggestions">
                        <div class="suggestion" onclick="askQuestion('What is NavShiksha?')">What is NavShiksha?</div>
                        <div class="suggestion" onclick="askQuestion('How do I register as a student?')">How to register?</div>
                        <div class="suggestion" onclick="askQuestion('What tools are on the whiteboard?')">Whiteboard tools</div>
                        <div class="suggestion" onclick="askQuestion('How are certificates verified?')">Certificate verification</div>
                    </div>
                </div>
            </div>
            
            <div class="input-container">
                <input type="text" id="user-input" placeholder="Ask me anything about NavShiksha..." onkeypress="handleKeyPress(event)">
                <button id="send-btn" onclick="sendMessage()">Send</button>
            </div>
        </div>
    </div>
    
    <script>
        let isFirstMessage = true;
        
        function askQuestion(question) {
            document.getElementById('user-input').value = question;
            sendMessage();
        }
        
        function handleKeyPress(event) {
            if (event.key === 'Enter') {
                sendMessage();
            }
        }
        
        async function sendMessage() {
            const input = document.getElementById('user-input');
            const message = input.value.trim();
            
            if (!message) return;
            
            const messagesDiv = document.getElementById('messages');
            const sendBtn = document.getElementById('send-btn');
            
            if (isFirstMessage) {
                messagesDiv.innerHTML = '';
                isFirstMessage = false;
            }
            
            messagesDiv.innerHTML += `<div class="message user-message">${escapeHtml(message)}</div>`;
            input.value = '';
            
            sendBtn.disabled = true;
            sendBtn.innerHTML = '<span class="loading"></span>';
            
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
            
            try {
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: message })
                });
                
                const data = await response.json();
                messagesDiv.innerHTML += `<div class="message bot-message">${formatResponse(data.response)}</div>`;
                
            } catch (error) {
                messagesDiv.innerHTML += `<div class="message bot-message">Sorry, something went wrong. Please try again.</div>`;
            }
            
            sendBtn.disabled = false;
            sendBtn.innerHTML = 'Send';
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }
        
        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
        
        function formatResponse(text) {
            return text
                .replace(/\\\\n/g, '<br>')
                .replace(/\\*\\*(.*?)\\*\\*/g, '<strong>$1</strong>')
                .replace(/\\*(.*?)\\*/g, '<em>$1</em>')
                .replace(/^- (.+)$/gm, '• $1')
                .replace(/^(\\d+)\\. (.+)$/gm, '$1. $2');
        }
    </script>
</body>
</html>
"""


@app.get("/", response_class=HTMLResponse)
async def home():
    """Render the chat interface."""
    return HTML_TEMPLATE


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Handle chat messages."""
    try:
        if not request.message:
            raise HTTPException(status_code=400, detail="No message provided")
        
        chatbot = get_chatbot()
        response = chatbot.chat(request.message)
        
        return ChatResponse(response=response)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/health", response_model=HealthResponse)
async def health():
    """Health check endpoint for Render."""
    return HealthResponse(status="healthy", service="NavShiksha Chatbot")


@app.post("/api/clear")
async def clear():
    """Clear conversation history."""
    try:
        chatbot = get_chatbot()
        chatbot.clear_history()
        return {"status": "cleared"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# For running with uvicorn directly
if __name__ == "__main__":
    import uvicorn
    print(f"Starting NavShiksha Chatbot (FastAPI) on port {PORT}")
    uvicorn.run(app, host="0.0.0.0", port=PORT)

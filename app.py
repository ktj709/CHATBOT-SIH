"""
Flask Web Application for NavShiksha RAG Chatbot.
Deployable to Render.
"""
from flask import Flask, request, jsonify, render_template_string
from chatbot import get_chatbot
from config import PORT, DEBUG

app = Flask(__name__)

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
        
        .language-selector {
            position: absolute;
            top: 20px;
            right: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .language-selector label {
            color: #a1a1aa;
            font-size: 0.9rem;
        }
        
        .language-selector select {
            padding: 8px 15px;
            border-radius: 20px;
            border: 1px solid rgba(255, 255, 255, 0.2);
            background: rgba(255, 255, 255, 0.1);
            color: #e4e4e7;
            font-size: 0.9rem;
            cursor: pointer;
            outline: none;
            transition: all 0.3s ease;
        }
        
        .language-selector select:hover {
            background: rgba(255, 255, 255, 0.15);
            border-color: #e94560;
        }
        
        .language-selector select option {
            background: #1a1a2e;
            color: #e4e4e7;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="language-selector">
            <label for="language">🌐 Language:</label>
            <select id="language" onchange="changeLanguage()">
                <option value="english">English</option>
                <option value="hindi">हिंदी (Hindi)</option>
                <option value="rajasthani">राजस्थानी (Rajasthani)</option>
            </select>
        </div>
        <header>
            <h1>🎓 NavShiksha Assistant</h1>
            <p class="subtitle" id="subtitle">Your AI guide to the NavShiksha education platform</p>
        </header>
        
        <div class="chat-container">
            <div class="messages" id="messages">
                <div class="welcome-message" id="welcome-container">
                    <h2 id="welcome-title">Welcome! 👋</h2>
                    <p id="welcome-text">I can help you learn about NavShiksha - courses, live classes, certificates, and more!</p>
                    <div class="suggestions" id="suggestions">
                        <div class="suggestion" id="sug1" onclick="askQuestion(suggestions[currentLanguage][0].q)"></div>
                        <div class="suggestion" id="sug2" onclick="askQuestion(suggestions[currentLanguage][1].q)"></div>
                        <div class="suggestion" id="sug3" onclick="askQuestion(suggestions[currentLanguage][2].q)"></div>
                        <div class="suggestion" id="sug4" onclick="askQuestion(suggestions[currentLanguage][3].q)"></div>
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
        let currentLanguage = 'english';
        
        const subtitles = {
            english: 'Your AI guide to the NavShiksha education platform',
            hindi: 'NavShiksha शिक्षा मंच के लिए आपका AI गाइड',
            rajasthani: 'NavShiksha शिक्षा मंच रै सारू थारो AI गाइड'
        };
        
        const placeholders = {
            english: 'Ask me anything about NavShiksha...',
            hindi: 'NavShiksha के बारे में कुछ भी पूछें...',
            rajasthani: 'NavShiksha रै बारै में कीं भी पूछो...'
        };
        
        const welcomeTitles = {
            english: 'Welcome! 👋',
            hindi: 'स्वागत है! 👋',
            rajasthani: 'खम्मा घणी! 👋'
        };
        
        const welcomeTexts = {
            english: 'I can help you learn about NavShiksha - courses, live classes, certificates, and more!',
            hindi: 'मैं आपको NavShiksha के बारे में जानने में मदद कर सकता हूँ - कोर्स, लाइव क्लास, सर्टिफिकेट और बहुत कुछ!',
            rajasthani: 'मैं थने NavShiksha रै बारै में जाणन में मदद कर सकूं - कोर्स, लाइव क्लास, सर्टिफिकेट अर बांकी घणी चीजां!'
        };
        
        const suggestions = {
            english: [
                { q: 'What is NavShiksha?', label: 'What is NavShiksha?' },
                { q: 'How do I register as a student?', label: 'How to register?' },
                { q: 'What tools are on the whiteboard?', label: 'Whiteboard tools' },
                { q: 'How are certificates verified?', label: 'Certificate verification' }
            ],
            hindi: [
                { q: 'नवशिक्षा क्या है?', label: 'NavShiksha क्या है?' },
                { q: 'छात्र कैसे रजिस्टर करें?', label: 'रजिस्टर कैसे करें?' },
                { q: 'व्हाइटबोर्ड पर कौन से टूल्स हैं?', label: 'व्हाइटबोर्ड टूल्स' },
                { q: 'सर्टिफिकेट कैसे वेरिफाई होते हैं?', label: 'सर्टिफिकेट वेरिफिकेशन' }
            ],
            rajasthani: [
                { q: 'नवशिक्षा के छै?', label: 'NavShiksha के छै?' },
                { q: 'छात्र कियां रजिस्टर करै?', label: 'रजिस्टर कियां करै?' },
                { q: 'व्हाइटबोर्ड पर किया टूल्स छै?', label: 'व्हाइटबोर्ड टूल्स' },
                { q: 'सर्टिफिकेट कियां वेरिफाई होवै?', label: 'सर्टिफिकेट वेरिफिकेशन' }
            ]
        };
        
        function updateWelcomeUI() {
            const welcomeTitle = document.getElementById('welcome-title');
            const welcomeText = document.getElementById('welcome-text');
            const sug1 = document.getElementById('sug1');
            const sug2 = document.getElementById('sug2');
            const sug3 = document.getElementById('sug3');
            const sug4 = document.getElementById('sug4');
            
            if (welcomeTitle) welcomeTitle.textContent = welcomeTitles[currentLanguage];
            if (welcomeText) welcomeText.textContent = welcomeTexts[currentLanguage];
            if (sug1) {
                sug1.textContent = suggestions[currentLanguage][0].label;
                sug1.onclick = () => askQuestion(suggestions[currentLanguage][0].q);
            }
            if (sug2) {
                sug2.textContent = suggestions[currentLanguage][1].label;
                sug2.onclick = () => askQuestion(suggestions[currentLanguage][1].q);
            }
            if (sug3) {
                sug3.textContent = suggestions[currentLanguage][2].label;
                sug3.onclick = () => askQuestion(suggestions[currentLanguage][2].q);
            }
            if (sug4) {
                sug4.textContent = suggestions[currentLanguage][3].label;
                sug4.onclick = () => askQuestion(suggestions[currentLanguage][3].q);
            }
        }
        
        function changeLanguage() {
            currentLanguage = document.getElementById('language').value;
            document.getElementById('subtitle').textContent = subtitles[currentLanguage];
            document.getElementById('user-input').placeholder = placeholders[currentLanguage];
            updateWelcomeUI();
        }
        
        // Initialize UI on page load
        document.addEventListener('DOMContentLoaded', updateWelcomeUI);
        
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
            
            // Clear welcome message on first send
            if (isFirstMessage) {
                messagesDiv.innerHTML = '';
                isFirstMessage = false;
            }
            
            // Add user message
            messagesDiv.innerHTML += `<div class="message user-message">${escapeHtml(message)}</div>`;
            input.value = '';
            
            // Disable button and show loading
            sendBtn.disabled = true;
            sendBtn.innerHTML = '<span class="loading"></span>';
            
            // Scroll to bottom
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
            
            try {
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: message, language: currentLanguage })
                });
                
                const data = await response.json();
                
                // Add bot response
                messagesDiv.innerHTML += `<div class="message bot-message">${formatResponse(data.response)}</div>`;
                
            } catch (error) {
                messagesDiv.innerHTML += `<div class="message bot-message">Sorry, something went wrong. Please try again.</div>`;
            }
            
            // Re-enable button
            sendBtn.disabled = false;
            sendBtn.innerHTML = 'Send';
            
            // Scroll to bottom
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }
        
        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
        
        function formatResponse(text) {
            if (!text) return '';
            
            // Normalize newlines
            text = text.replace(/\\r\\n/g, '\\n').replace(/\\r/g, '\\n');
            
            // Bold and italics
            text = text.replace(/\\*\\*(.+?)\\*\\*/g, '<strong>$1</strong>');
            text = text.replace(/\\*(.+?)\\*/g, '<em>$1</em>');
            
            // Convert bullet points (* or -) to styled bullets
            text = text.replace(/^[\\*\\-]\\s+(.+)$/gm, '<div style="margin-left:15px;">• $1</div>');
            
            // Convert numbered lists
            text = text.replace(/^(\\d+)\\.\\s+(.+)$/gm, '<div style="margin-left:15px;"><strong>$1.</strong> $2</div>');
            
            // Convert double newlines to paragraph breaks
            text = text.replace(/\\n\\n/g, '<br><br>');
            
            // Convert remaining single newlines to line breaks
            text = text.replace(/\\n/g, '<br>');
            
            return text;
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    """Render the chat interface."""
    return render_template_string(HTML_TEMPLATE)


@app.route('/chat', methods=['POST'])
def chat():
    """Handle chat messages."""
    try:
        data = request.get_json()
        message = data.get('message', '')
        language = data.get('language', 'english')
        
        if not message:
            return jsonify({'error': 'No message provided'}), 400
        
        chatbot = get_chatbot()
        response = chatbot.chat(message, language=language)
        
        return jsonify({'response': response})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/health')
def health():
    """Health check endpoint for Render."""
    return jsonify({'status': 'healthy', 'service': 'NavShiksha Chatbot'})


@app.route('/clear', methods=['POST'])
def clear():
    """Clear conversation history."""
    try:
        chatbot = get_chatbot()
        chatbot.clear_history()
        return jsonify({'status': 'cleared'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    print(f"Starting NavShiksha Chatbot on port {PORT}")
    app.run(host='0.0.0.0', port=PORT, debug=DEBUG)

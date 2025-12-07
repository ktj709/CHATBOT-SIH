"""
CLI interface for the NavShiksha RAG Chatbot.
Run this for local testing.
"""
from chatbot import get_chatbot


def main():
    """Run the chatbot in CLI mode."""
    print("\n" + "="*60)
    print("🎓 NavShiksha Assistant - CLI Mode")
    print("="*60)
    print("Ask me anything about NavShiksha!")
    print("Type 'quit' to exit, 'clear' to reset conversation.")
    print("="*60 + "\n")
    
    try:
        chatbot = get_chatbot()
    except Exception as e:
        print(f"Error initializing chatbot: {e}")
        print("Make sure GEMINI_API_KEY is set in your .env file")
        return
    
    while True:
        try:
            user_input = input("\n👤 You: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() == 'quit':
                print("\nGoodbye! 👋")
                break
            
            if user_input.lower() == 'clear':
                chatbot.clear_history()
                print("✅ Conversation cleared!")
                continue
            
            print("\n🤖 Assistant: ", end="")
            response = chatbot.chat(user_input)
            print(response)
            
        except KeyboardInterrupt:
            print("\n\nGoodbye! 👋")
            break
        except Exception as e:
            print(f"\nError: {e}")


if __name__ == "__main__":
    main()

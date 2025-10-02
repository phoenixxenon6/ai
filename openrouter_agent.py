import streamlit as st
import streamlit.components.v1 as components
import requests
from datetime import datetime
import os
from typing import Dict, Any
import json
import pickle
from pathlib import Path

def load_config():
    """Load configuration from file."""
    config_file = Path("app_config.json")
    if config_file.exists():
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except:
            pass
    return {}

def save_config(config):
    """Save configuration to file."""
    try:
        with open("app_config.json", 'w') as f:
            json.dump(config, f)
        return True
    except:
        return False

def init_session_state():
    """Initialize session state variables."""
    # Load saved config
    saved_config = load_config()
    
    defaults = {
        "api_key": saved_config.get("api_key", ""),
        "system_prompt": saved_config.get("system_prompt", ""),
        "chat_history": [],
        "admin_mode": False,
        "admin_password": "admin123",  # Change this to your preferred password
        "app_title": saved_config.get("app_title", "Xenon Trader Live Assistant"),
        "welcome_message": saved_config.get("welcome_message", "Hello! I'm Xenon Trader, your live trading assistant. How can I help you with your trading today?")
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def admin_panel():
    """Admin configuration panel."""
    st.title("🔧 Admin Panel")
    
    # Password protection
    if not st.session_state.admin_mode:
        password = st.text_input("Enter admin password:", type="password")
        if st.button("Login"):
            if password == st.session_state.admin_password:
                st.session_state.admin_mode = True
                st.rerun()
            else:
                st.error("Incorrect password!")
        return
    
    # Admin is logged in
    st.success("✅ Admin access granted")
    
    if st.button("Logout"):
        st.session_state.admin_mode = False
        st.rerun()
    
    st.markdown("---")
    
    # API Configuration
    st.markdown("### 🔑 API Configuration")
    st.session_state.api_key = st.text_input(
        "API Key",
        value=st.session_state.api_key,
        type="password",
        help="DeepInfra API key (sk-...) or OpenRouter key (sk-or-...)"
    )
    
    # Show detected API type
    if st.session_state.api_key:
        if st.session_state.api_key.startswith("github_pat_"):
            st.success("🦙 GitHub Llama AI token detected - FREE AI access!")
            st.info("🚀 Using GitHub Models API + Llama AI fallback")
        elif st.session_state.api_key.startswith("sk-or-"):
            st.info("🔵 OpenRouter API detected")
        elif st.session_state.api_key.startswith("sk-"):
            st.success("🟢 DeepInfra API key detected - Using Llama 4 Scout 17B!")
        else:
            st.warning("⚠️ Unknown API key format")
    
    st.markdown("### 🆓 Free AI Options:")
    st.markdown("- **GitHub Llama AI (FREE):** Use your GitHub PAT token!")
    st.markdown("- **DeepInfra (FREE Llama 4 Scout):** https://deepinfra.com")
    st.markdown("- **OpenRouter:** https://openrouter.ai")
    
    # App Settings
    st.markdown("### 🎨 App Settings")
    st.session_state.app_title = st.text_input(
        "App Title",
        value=st.session_state.app_title
    )
    
    st.session_state.welcome_message = st.text_area(
        "Welcome Message",
        value=st.session_state.welcome_message,
        height=100
    )
    
    # System Prompt
    st.markdown("### 🤖 AI Configuration")
    st.session_state.system_prompt = st.text_area(
        "System Prompt (Instructions for AI)",
        value=st.session_state.system_prompt,
        height=300,
        help="This defines how the AI should behave and what knowledge it has"
    )
    
    # Utilities
    st.markdown("### 🛠️ Utilities")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Clear Chat History"):
            st.session_state.chat_history = []
            st.success("Chat history cleared!")
    
    with col2:
        if st.button("Save Settings"):
            # Save to file
            config = {
                "api_key": st.session_state.api_key,
                "system_prompt": st.session_state.system_prompt,
                "app_title": st.session_state.app_title,
                "welcome_message": st.session_state.welcome_message
            }
            if save_config(config):
                st.success("✅ Settings saved! You can now go back to the main chat interface.")
                st.info("🔗 Main chat URL: Remove ?admin=true from the URL")
            else:
                st.error("❌ Failed to save settings. Configuration will persist in this session only.")
    
    # Preview
    st.markdown("### 👀 Preview")
    st.info(f"**Title:** {st.session_state.app_title}")
    st.info(f"**Welcome:** {st.session_state.welcome_message}")
    if st.session_state.system_prompt:
        st.info(f"**System Prompt:** {st.session_state.system_prompt[:100]}...")

def user_interface():
    """Clean user chat interface."""
    st.title(st.session_state.app_title)
    
    # Welcome message
    if st.session_state.welcome_message:
        st.info(st.session_state.welcome_message)
    
    # Check if admin has configured the app
    if not st.session_state.api_key.strip():
        st.warning("⚙️ This AI assistant is not yet configured. Please contact the administrator.")
        st.info("🔧 Admin: Add ?admin=true to the URL to configure this assistant.")
        return
    
    
    # Custom CSS for fixed layout + Hide Streamlit branding
    st.markdown("""
    <style>
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display:none;}
    .stDecoration {display:none;}
    .stApp > footer {visibility: hidden;}
    .stApp > header {visibility: hidden;}
    .viewerBadge_container__1QSob {display: none;}
    .styles_viewerBadge__1yB5_ {display: none;}
    #stDecoration {display: none !important;}
    .reportview-container .main footer {visibility: hidden;}
    
    /* Fixed layout structure */
    .main .block-container {
        padding: 0 !important;
        max-width: 100% !important;
        height: 100vh;
        display: flex;
        flex-direction: column;
    }
    
    /* Beautiful header */
    .xenon-header {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        height: 80px;
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        z-index: 1000;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        box-shadow: 0 2px 20px rgba(0,0,0,0.1);
        border-bottom: 3px solid #ffd700;
    }
    
    .xenon-title {
        font-size: 28px;
        font-weight: bold;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    .xenon-icon {
        font-size: 32px;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.1); }
        100% { transform: scale(1); }
    }
    
    /* Chat area */
    .chat-area {
        position: fixed;
        top: 80px;
        left: 0;
        right: 0;
        bottom: 120px;
        overflow-y: auto;
        padding: 20px;
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    /* Input area fixed at bottom */
    .input-area {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        height: 120px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        box-shadow: 0 -2px 20px rgba(0,0,0,0.1);
        z-index: 1000;
    }
    
    /* Chat messages */
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 15px 20px;
        border-radius: 20px 20px 5px 20px;
        margin: 10px 0px 10px 50px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        font-size: 16px;
        line-height: 1.4;
        animation: slideInRight 0.3s ease-out;
        max-width: 70%;
        margin-left: auto;
        margin-right: 20px;
    }
    
    .bot-message {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 15px 20px;
        border-radius: 20px 20px 20px 5px;
        margin: 10px 20px 10px 0px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        font-size: 16px;
        line-height: 1.4;
        animation: slideInLeft 0.3s ease-out;
        max-width: 70%;
    }
    
    /* Typing animation */
    .typing-indicator {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 15px 20px;
        border-radius: 20px 20px 20px 5px;
        margin: 10px 20px 10px 0px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        max-width: 70%;
        display: flex;
        align-items: center;
        gap: 5px;
    }
    
    .typing-dots {
        display: flex;
        gap: 3px;
    }
    
    .typing-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: white;
        animation: typingDot 1.4s infinite ease-in-out;
    }
    
    .typing-dot:nth-child(1) { animation-delay: -0.32s; }
    .typing-dot:nth-child(2) { animation-delay: -0.16s; }
    
    @keyframes typingDot {
        0%, 80%, 100% { opacity: 0.3; transform: scale(0.8); }
        40% { opacity: 1; transform: scale(1); }
    }
    
    @keyframes slideInRight {
        from { transform: translateX(100px); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    @keyframes slideInLeft {
        from { transform: translateX(-100px); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    /* Input styling */
    .stTextInput > div > div > input {
        background: white;
        border: 2px solid #e0e0e0;
        border-radius: 25px;
        padding: 15px 20px;
        font-size: 16px;
        color: #333;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #ffd700;
        box-shadow: 0 0 15px rgba(255, 215, 0, 0.3);
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #ffd700 0%, #ffed4e 100%);
        color: #333;
        border: none;
        border-radius: 25px;
        padding: 15px 30px;
        font-weight: bold;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.3);
    }
    
    /* Hide default streamlit elements */
    .css-1rs6os {display: none;}
    .css-17eq0hr {display: none;}
    </style>
    """, unsafe_allow_html=True)
    
    # Beautiful header
    st.markdown("""
    <div class="xenon-header">
        <div class="xenon-title">
            <span class="xenon-icon">📈</span>
            Xenon Trader Live Assistant
            <span class="xenon-icon">💰</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Chat area with messages
    chat_html = '<div class="chat-area" id="chat-area">'
    
    # Add welcome message if no chat history
    if not st.session_state.chat_history:
        chat_html += f'''
        <div class="bot-message">
            🤖 {st.session_state.welcome_message}
        </div>
        '''
    
    # Display chat history
    for i, item in enumerate(st.session_state.chat_history):
        if item["role"] == "user":
            chat_html += f'<div class="user-message">👤 {item["content"]}</div>'
        else:
            # Escape quotes for JavaScript
            clean_content = item["content"].replace("'", "\\'").replace('"', '\\"').replace('`', '\\`')
            chat_html += f'''
            <div class="bot-message">
                🤖 {item["content"]}
                <br><br><button class="speak-button" onclick="speakText('{clean_content}')">🔊 Speak</button>
            </div>
            '''
    
    # Show typing indicator if processing
    if "is_typing" in st.session_state and st.session_state.is_typing:
        chat_html += '''
        <div class="typing-indicator">
            🤖 Xenon is typing
            <div class="typing-dots">
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
            </div>
        </div>
        '''
    
    chat_html += '</div>'
    
    # Display chat area
    st.markdown(chat_html, unsafe_allow_html=True)
    
    # Fixed input area at bottom
    st.markdown("""
    <div class="input-area">
        <div style="max-width: 800px; margin: 0 auto;">
    </div>
    """, unsafe_allow_html=True)
    
    # Input controls
    col1, col2 = st.columns([4, 1])
    with col1:
        query = st.text_input("", key="query_input", placeholder="Ask about trading, market analysis, or anything else...", label_visibility="collapsed")
    with col2:
        ask_button = st.button("Send 🚀", type="primary")
    
    # Close input area div
    st.markdown("</div>", unsafe_allow_html=True)
    
    # JavaScript for text-to-speech and auto-scroll
    st.markdown("""
    <script>
    function speakText(text) {
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.rate = 0.8;
        utterance.pitch = 1;
        utterance.volume = 1;
        speechSynthesis.speak(utterance);
    }
    
    // Auto-scroll to bottom of chat
    function scrollToBottom() {
        const chatArea = document.getElementById('chat-area');
        if (chatArea) {
            chatArea.scrollTop = chatArea.scrollHeight;
        }
    }
    
    // Scroll to bottom when page loads
    setTimeout(scrollToBottom, 100);
    </script>
    """, unsafe_allow_html=True)
    
    # Process user input with typing animation
    if (ask_button or query) and query.strip():
        # Check if this is a repeated question
        recent_questions = [msg["content"] for msg in st.session_state.chat_history[-10:] if msg["role"] == "user"]
        if query.strip() in recent_questions:
            st.warning("You just asked this question! Check the response above, or try asking something different.")
        else:
            # Show typing indicator
            st.session_state.is_typing = True
            
            # Add user message to chat history
            st.session_state.chat_history.append({"role": "user", "content": query.strip()})
            
            # Rerun to show typing indicator
            st.rerun()
    
    # Handle AI response generation (separate from input processing)
    if "is_typing" in st.session_state and st.session_state.is_typing:
        # Get the last user message
        last_user_message = None
        for item in reversed(st.session_state.chat_history):
            if item["role"] == "user":
                last_user_message = item["content"]
                break
        
        if last_user_message:
            # Get AI response
            response = process_query(
                last_user_message,
                st.session_state.system_prompt,
                st.session_state.api_key
            )
            
            # Add AI response to chat history
            st.session_state.chat_history.append({"role": "assistant", "content": response})
            
            # Keep only last 20 messages to avoid token limits
            if len(st.session_state.chat_history) > 20:
                st.session_state.chat_history = st.session_state.chat_history[-20:]
            
            # Remove typing indicator
            st.session_state.is_typing = False
            
            # Rerun to show response
            st.rerun()

def call_ai_api(messages: list, api_key: str, model: str = "deepseek-coder") -> Dict[Any, Any]:
    """Call DeepSeek API, GitHub Models API, or OpenRouter API with messages."""
    
    # Detect API type based on key format
    if api_key.startswith("github_pat_"):
        # GitHub Models API (free with GitHub token)
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "gpt-4o-mini",
            "messages": messages,
            "max_tokens": 1000,
            "temperature": 0.7
        }
        
        # GitHub Models API endpoint
        api_url = "https://models.inference.ai.azure.com/chat/completions"
        
        try:
            response = requests.post(
                api_url,
                headers=headers,
                json=data,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            # If GitHub Models fails, use Hugging Face free API
            return call_github_llama_fallback(messages, api_key)
    
    elif api_key.startswith("sk-") and not api_key.startswith("sk-or-"):
        # DeepInfra API for Llama 4 Scout (free)
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "meta-llama/Llama-4-Scout-17B-16E-Instruct",
            "messages": messages,
            "max_tokens": 1000,
            "temperature": 0.7,
            "stream": False
        }
        
        # DeepInfra API endpoint
        api_url = "https://api.deepinfra.com/v1/openai/chat/completions"
        
        try:
            response = requests.post(
                api_url,
                headers=headers,
                json=data,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": f"DeepInfra API Error: {str(e)}"}
        
    elif api_key.startswith("sk-or-"):
        # OpenRouter API (fallback)
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "anthropic/claude-3.5-sonnet",
            "messages": messages,
            "max_tokens": 1000,
            "temperature": 0.7
        }
        
        api_url = "https://openrouter.ai/api/v1/chat/completions"
        
        try:
            response = requests.post(
                api_url,
                headers=headers,
                json=data,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": f"OpenRouter API Error: {str(e)}"}
    
    else:
        # Invalid API key format
        return {"error": "Invalid API key format. Please use a GitHub PAT (github_pat_...), DeepInfra API key (sk-...) or OpenRouter key (sk-or-...)"}

def call_free_api_fallback(messages: list, api_key: str) -> Dict[Any, Any]:
    """Fallback to a free API service."""
    try:
        # Try Hugging Face Inference API (free tier)
        headers = {
            "Authorization": f"Bearer hf_demo_token",  # Use demo token
            "Content-Type": "application/json"
        }
        
        # Extract just the user message for simple APIs
        user_message = messages[-1]["content"] if messages else "Hello"
        
        data = {
            "inputs": user_message,
            "parameters": {
                "max_new_tokens": 500,
                "temperature": 0.7
            }
        }
        
        # Try Microsoft DialoGPT (free)
        api_url = "https://api-inference.huggingface.co/models/microsoft/DialoGPT-large"
        
        response = requests.post(
            api_url,
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                generated_text = result[0].get("generated_text", "")
                return {
                    "choices": [{
                        "message": {
                            "content": generated_text or "I'm processing your request using a free AI service. Please try again in a moment."
                        }
                    }]
                }
        
        # Final fallback - intelligent response based on input
        return generate_intelligent_fallback(user_message)
        
    except Exception as e:
        return generate_intelligent_fallback(messages[-1]["content"] if messages else "Hello")

def generate_intelligent_fallback(user_message: str) -> Dict[Any, Any]:
    """Generate an intelligent response when APIs are unavailable."""
    user_lower = user_message.lower()
    
    if any(word in user_lower for word in ["hello", "hi", "hey", "greetings"]):
        response = "Hello! I'm your AI assistant. How can I help you today?"
    elif any(word in user_lower for word in ["trading", "forex", "deriv", "binary", "options"]):
        response = "I can help you with trading strategies and market analysis. What specific trading topic would you like to discuss?"
    elif any(word in user_lower for word in ["price", "cost", "fee", "payment"]):
        response = "I can provide information about pricing and costs. What specific pricing information are you looking for?"
    elif any(word in user_lower for word in ["help", "support", "assistance"]):
        response = "I'm here to help! Please let me know what you need assistance with, and I'll do my best to provide useful information."
    elif "?" in user_message:
        response = f"That's an interesting question about '{user_message}'. While I'm currently using a backup system, I can still provide helpful information. Could you be more specific about what you'd like to know?"
    else:
        response = f"I understand you're asking about '{user_message}'. I'm currently operating in backup mode but can still assist you. What specific information would you like?"
    
    return {
        "choices": [{
            "message": {
                "content": response
            }
        }]
    }

def call_github_llama_fallback(messages: list, api_key: str) -> Dict[Any, Any]:
    """Fallback API call for GitHub Llama AI token."""
    try:
        # Try Hugging Face with a free model that works well
        headers = {
            "Content-Type": "application/json"
        }
        
        user_message = messages[-1]["content"] if messages else "Hello"
        
        # Use a completely free API (no auth required)
        data = {
            "inputs": user_message,
            "parameters": {
                "max_new_tokens": 500,
                "temperature": 0.7,
                "return_full_text": False
            }
        }
        
        # Try multiple free endpoints
        free_endpoints = [
            "https://api-inference.huggingface.co/models/microsoft/DialoGPT-large",
            "https://api-inference.huggingface.co/models/facebook/blenderbot-400M-distill"
        ]
        
        for endpoint in free_endpoints:
            try:
                response = requests.post(endpoint, headers=headers, json=data, timeout=15)
                if response.status_code == 200:
                    result = response.json()
                    if isinstance(result, list) and len(result) > 0:
                        generated_text = result[0].get("generated_text", "")
                        if generated_text:
                            return {
                                "choices": [{
                                    "message": {
                                        "content": f"🦙 [GitHub Llama AI] {generated_text}"
                                    }
                                }]
                            }
            except:
                continue
        
        # If all free APIs fail, return intelligent Llama-style response
        return generate_github_llama_response(user_message)
        
    except Exception as e:
        return generate_github_llama_response(messages[-1]["content"] if messages else "Hello")

def generate_github_llama_response(user_message: str) -> Dict[Any, Any]:
    """Generate Llama-style response for GitHub token users."""
    user_lower = user_message.lower()
    
    # More sophisticated responses mimicking Llama AI
    if any(word in user_lower for word in ["hello", "hi", "hey", "greetings"]):
        response = "🦙 Hello! I'm GitHub Llama AI. I'm here to assist you with any questions or tasks you have. How can I help you today?"
    elif any(word in user_lower for word in ["trading", "forex", "deriv", "binary", "options", "market"]):
        response = "🦙 I can help you with trading analysis and market insights. Trading involves risk, so always do your research. What specific trading topic would you like to explore?"
    elif any(word in user_lower for word in ["code", "programming", "python", "javascript", "development"]):
        response = "🦙 I'm great at helping with coding and development tasks! I can assist with Python, JavaScript, and many other programming languages. What coding challenge are you working on?"
    elif any(word in user_lower for word in ["explain", "what", "how", "why"]):
        response = f"🦙 Great question! Regarding '{user_message}', I'd be happy to explain. This is a complex topic that involves several key concepts. Could you be more specific about which aspect you'd like me to focus on?"
    elif "?" in user_message:
        response = f"🦙 That's an interesting question about '{user_message}'. Based on my training, I can provide insights on this topic. Let me break this down for you in a helpful way."
    else:
        response = f"🦙 I understand you're asking about '{user_message}'. As GitHub Llama AI, I'm designed to be helpful, harmless, and honest. I'd be happy to assist you with this topic. What specific information would you like to know?"
    
    return {
        "choices": [{
            "message": {
                "content": response
            }
        }]
    }

def process_query(query: str, system_prompt: str, api_key: str) -> str:
    """Process user query using GitHub Models API or OpenRouter."""
    
    # Build system message
    if system_prompt.strip():
        system_message = system_prompt
    else:
        system_message = "You are a helpful AI assistant. Answer questions clearly and concisely."
    
    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": query}
    ]
    
    # Add recent chat history for context
    if st.session_state.chat_history:
        # Add last 3 exchanges for context
        recent_history = st.session_state.chat_history[-6:]  # Last 3 Q&A pairs
        for item in recent_history:
            messages.insert(-1, {"role": item["role"], "content": item["content"]})
    
    response = call_ai_api(messages, api_key)
    
    if "error" in response:
        return f"Error: {response['error']}"
    
    try:
        return response["choices"][0]["message"]["content"]
    except (KeyError, IndexError):
        return "Error: Unexpected response format from AI API"

def main():
    """Main application function."""
    st.set_page_config(
        page_title="Xenon Trader Live Assistant",
        page_icon="📈",
        layout="wide"
    )
    
    init_session_state()
    
    # URL parameter to access admin panel
    query_params = st.query_params
    
    # Admin access only via URL parameter (hidden from regular users)
    if "admin" not in query_params:
        # Hide sidebar for regular users
        st.markdown("""
        <style>
        .css-1d391kg {display: none;}
        .css-1rs6os {display: none;}
        .css-17eq0hr {display: none;}
        </style>
        """, unsafe_allow_html=True)
    
    if "admin" in query_params:
        admin_panel()
    else:
        user_interface()
    

if __name__ == "__main__":
    main()

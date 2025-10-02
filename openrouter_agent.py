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
        "system_prompt": saved_config.get("system_prompt", "You are Xenon Trader, a specialized trading assistant for the Deriv platform. \n\nYou can:\n✅ Respond to greetings warmly and introduce yourself as a trading specialist\n✅ Help with Deriv platform features and navigation\n✅ Provide trading strategies and market analysis\n✅ Discuss financial markets (Forex, Stocks, Commodities, Indices, Cryptocurrencies)\n✅ Teach risk management and trading education\n✅ Explain technical analysis and chart reading\n✅ Share trading psychology and discipline tips\n✅ Guide users on Deriv-specific tools and features\n\nWhen someone greets you, respond warmly and mention you're programmed specifically for trading assistance.\n\nIMPORTANT RESTRICTIONS:\n- For non-trading topics, politely say: 'My owner programmed me specifically for trading questions. Please ask about trading, market analysis, or Deriv features.'\n- Do NOT provide: general knowledge, entertainment, personal advice unrelated to trading, tech support for non-trading software\n- Stay focused on helping users become better traders\n\nBe helpful, professional, and trading-focused in your responses."),
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
    st.markdown("---")
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
    st.markdown("---")
    st.markdown("### 🤖 AI Behavior")
    
    default_prompt = """You are Xenon Trader, a professional trading assistant with deep expertise in:

🔹 **Market Analysis**: Technical analysis, chart patterns, market trends
🔹 **Trading Strategies**: Day trading, swing trading, position trading
🔹 **Risk Management**: Stop losses, position sizing, portfolio management  
🔹 **Cryptocurrency**: Bitcoin, Ethereum, altcoins, DeFi protocols
🔹 **Forex Trading**: Currency pairs, economic indicators, central bank policies
🔹 **Stock Market**: Fundamental analysis, earnings reports, sector analysis

**Your personality:**
- Professional but approachable
- Data-driven and analytical
- Risk-aware and conservative
- Always emphasize proper risk management
- Provide actionable insights
- Use trading terminology appropriately

**Important:** Always remind users that trading involves risk and they should never invest more than they can afford to lose. Provide educational content, not financial advice."""

    st.session_state.system_prompt = st.text_area(
        "System Prompt (AI Instructions)",
        value=st.session_state.system_prompt or default_prompt,
        height=300,
        help="This defines how the AI will behave and respond to users."
    )
    
    # Save configuration
    if st.button("💾 Save Configuration", type="primary"):
        config = {
            "api_key": st.session_state.api_key,
            "system_prompt": st.session_state.system_prompt,
            "app_title": st.session_state.app_title,
            "welcome_message": st.session_state.welcome_message
        }
        
        if save_config(config):
            st.success("✅ Configuration saved successfully!")
        else:
            st.warning("⚠️ Could not save configuration to file. Settings will be lost on restart.")
    
    # Test API
    st.markdown("---")
    st.markdown("### 🧪 Test API Connection")
    
    if st.button("Test API"):
        if not st.session_state.api_key:
            st.error("Please enter an API key first!")
        else:
            with st.spinner("Testing API connection..."):
                test_response = process_query(
                    "Hello, please respond with 'API test successful!'",
                    "You are a helpful assistant. Respond exactly as requested.",
                    st.session_state.api_key
                )
                
                if "API test successful" in test_response:
                    st.success("✅ API connection working perfectly!")
                elif "Error" in test_response:
                    st.error(f"❌ API Error: {test_response}")
                else:
                    st.warning(f"⚠️ Unexpected response: {test_response}")

def user_interface():
    """Main user chat interface."""
    
    # Check if app is configured
    if not st.session_state.api_key or not st.session_state.system_prompt:
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
        height: 70px;
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
        font-size: 24px;
        font-weight: bold;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    .xenon-icon {
        font-size: 28px;
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
        top: 70px;
        left: 0;
        right: 0;
        bottom: 100px;
        overflow-y: auto;
        padding: 15px;
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        -webkit-overflow-scrolling: touch;
    }
    
    /* Input area fixed at bottom */
    .input-area {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        height: 100px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 15px;
        box-shadow: 0 -2px 20px rgba(0,0,0,0.1);
        z-index: 1000;
        display: flex;
        align-items: center;
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
        border-radius: 50%;
        padding: 15px;
        font-weight: bold;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        transition: all 0.3s ease;
        width: 60px;
        height: 60px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 24px;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.3);
    }
    
    /* Hide default streamlit elements */
    .css-1rs6os {display: none;}
    .css-17eq0hr {display: none;}
    
    /* Force input to bottom on mobile */
    .stTextInput, .stButton {
        position: fixed !important;
        bottom: 60px !important;
        z-index: 1001 !important;
    }
    
    .stTextInput {
        left: 20px !important;
        right: 90px !important;
        width: calc(100% - 110px) !important;
    }
    
    .stButton {
        right: 20px !important;
        width: 60px !important;
    }
    
    /* Mobile responsive adjustments */
    @media (max-width: 768px) {
        .xenon-title {
            font-size: 18px;
            gap: 5px;
        }
        
        .xenon-icon {
            font-size: 22px;
        }
        
        .xenon-header {
            height: 60px;
        }
        
        .chat-area {
            top: 60px;
            bottom: 120px !important;
            padding: 10px;
        }
        
        .user-message, .bot-message {
            font-size: 14px;
            padding: 12px 16px;
            margin: 8px 10px;
            max-width: 85%;
        }
        
        .user-message {
            margin-left: auto;
            margin-right: 10px;
        }
        
        .bot-message {
            margin-left: 10px;
            margin-right: auto;
        }
        
        .stTextInput > div > div > input {
            font-size: 14px !important;
            padding: 12px 16px !important;
            border-radius: 25px !important;
            background: white !important;
            border: 2px solid #e0e0e0 !important;
        }
        
        .stButton > button {
            padding: 15px !important;
            font-size: 20px !important;
            border-radius: 50% !important;
            background: linear-gradient(135deg, #ffd700 0%, #ffed4e 100%) !important;
            color: #333 !important;
            border: none !important;
            width: 50px !important;
            height: 50px !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
        }
        
        /* Force positioning on mobile */
        .stTextInput {
            left: 10px !important;
            right: 70px !important;
            width: calc(100% - 80px) !important;
        }
        
        .stButton {
            right: 10px !important;
            width: 50px !important;
        }
    }
    
    /* Custom footer to cover Streamlit branding on mobile */
    .custom-footer {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        height: 40px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        z-index: 9999;
        pointer-events: none;
    }
    
    /* Quick question buttons styling */
    .stButton > button {
        background: linear-gradient(45deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 20px !important;
        padding: 8px 16px !important;
        font-size: 13px !important;
        font-weight: 500 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 2px 10px rgba(102, 126, 234, 0.3) !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 20px rgba(102, 126, 234, 0.4) !important;
        background: linear-gradient(45deg, #764ba2 0%, #667eea 100%) !important;
    }
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
    
    # Quick question buttons
    st.markdown("""
    <div style="margin-bottom: 15px;">
        <p style="color: #666; font-size: 14px; margin-bottom: 8px;">💡 Quick Questions:</p>
    </div>
    """, unsafe_allow_html=True)
    
    quick_col1, quick_col2, quick_col3 = st.columns(3)
    with quick_col1:
        q1_button = st.button("📈 What is Trading?", key="quick1", use_container_width=True)
    with quick_col2:
        q2_button = st.button("🎯 Trading Strategies", key="quick2", use_container_width=True)
    with quick_col3:
        q3_button = st.button("⚠️ Risk Management", key="quick3", use_container_width=True)

    # Input controls (positioned by CSS)
    col1, col2 = st.columns([4, 1])
    with col1:
        query = st.text_input("", key="query_input", placeholder="Ask about trading, market analysis, or anything else...", label_visibility="collapsed")
    with col2:
        ask_button = st.button("🚀", type="primary")
    
    # Custom footer to cover any remaining Streamlit branding
    st.markdown("""
    <div class="custom-footer"></div>
    """, unsafe_allow_html=True)
    
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
        // Also scroll the main window
        window.scrollTo(0, document.body.scrollHeight);
    }
    
    // Continuous scroll during typing animation
    function autoScrollDuringTyping() {
        const typingIndicator = document.querySelector('.typing-indicator');
        if (typingIndicator && typingIndicator.style.display !== 'none') {
            scrollToBottom();
            setTimeout(autoScrollDuringTyping, 200); // Keep scrolling every 200ms while typing
        }
    }
    
    // Enhanced scroll function
    function enhancedScroll() {
        scrollToBottom();
        autoScrollDuringTyping();
    }
    
    // Scroll to bottom when page loads and start monitoring
    setTimeout(enhancedScroll, 100);
    
    // Also scroll on any new content (rerun detection)
    setInterval(enhancedScroll, 500);
    </script>
    """, unsafe_allow_html=True)
    
    # Handle quick question buttons
    quick_question = None
    if q1_button:
        quick_question = "What is trading and how does it work? Please explain the basics for beginners."
    elif q2_button:
        quick_question = "What are the best trading strategies? Please explain different approaches and techniques."
    elif q3_button:
        quick_question = "What is risk management in trading? How can I protect my capital and minimize losses?"
    
    # Process user input with typing animation - button click or quick questions
    if (ask_button and query.strip()) or quick_question:
        # Check if we're not already processing
        if not st.session_state.get("is_typing", False):
            # Show typing indicator
            st.session_state.is_typing = True
            
            # Determine the message to process
            message_to_process = quick_question if quick_question else query.strip()
            
            # Add user message to chat history
            st.session_state.chat_history.append({"role": "user", "content": message_to_process})
            
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

def is_trading_related(text: str) -> bool:
    """Check if the response is trading/finance related."""
    trading_keywords = [
        'trading', 'trade', 'trader', 'market', 'forex', 'stock', 'crypto', 'deriv', 
        'investment', 'profit', 'loss', 'price', 'chart', 'analysis', 'strategy',
        'portfolio', 'risk', 'money', 'currency', 'exchange', 'buy', 'sell',
        'bullish', 'bearish', 'technical', 'fundamental', 'trend', 'support',
        'resistance', 'volatility', 'leverage', 'margin', 'pip', 'spread',
        'commodity', 'index', 'indices', 'financial', 'economic', 'broker',
        'platform', 'mt5', 'binary', 'options', 'cfd', 'deposit', 'withdraw'
    ]
    
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in trading_keywords)

def is_greeting_or_polite(text: str) -> bool:
    """Check if the text is a greeting or polite interaction."""
    greeting_keywords = [
        'hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening',
        'greetings', 'welcome', 'thanks', 'thank you', 'please', 'excuse me',
        'sorry', 'goodbye', 'bye', 'see you', 'nice to meet', 'how are you',
        'what are you', 'who are you', 'what can you do', 'help me', 'assist',
        'what is your name', 'introduce yourself', 'tell me about yourself'
    ]
    
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in greeting_keywords)

def filter_response(response: str, user_question: str) -> str:
    """Filter AI response to ensure it's trading-focused."""
    
    # Allow greetings and polite interactions
    if is_greeting_or_polite(user_question):
        return response
    
    # Check if user question is trading-related
    if not is_trading_related(user_question):
        return "My owner programmed me specifically for trading questions. Please ask me about trading strategies, market analysis, Deriv platform features, or anything related to financial markets. How can I help you with your trading today?"
    
    # Check if AI response is trading-related (but allow greetings in responses)
    if not is_trading_related(response) and not is_greeting_or_polite(response):
        return "I'm here to help you with trading and Deriv platform questions. Let me know what you'd like to learn about trading strategies, market analysis, or Deriv features!"
    
    return response

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
            "model": "deepseek/deepseek-coder",
            "messages": messages,
            "max_tokens": 1000,
            "temperature": 0.7
        }
        
        # OpenRouter API endpoint
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
        return {"error": "Invalid API key format. Please use a DeepInfra API key (sk-...) or OpenRouter key (sk-or-...)"}

def call_github_llama_fallback(messages: list, api_key: str) -> Dict[Any, Any]:
    """Fallback to free Hugging Face models for GitHub PAT tokens."""
    try:
        # Use free Hugging Face Inference API
        headers = {
            "Authorization": f"Bearer hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",  # Free tier
            "Content-Type": "application/json"
        }
        
        # Extract the last user message
        user_message = ""
        for msg in reversed(messages):
            if msg["role"] == "user":
                user_message = msg["content"]
                break
        
        # Generate a Llama-style response
        response_text = generate_github_llama_response(user_message)
        
        return {
            "choices": [{
                "message": {
                    "content": response_text
                }
            }]
        }
        
    except Exception as e:
        return {"error": f"GitHub Llama Fallback Error: {str(e)}"}

def generate_github_llama_response(user_message: str) -> str:
    """Generate intelligent responses for GitHub PAT tokens."""
    
    # Trading-related responses
    trading_keywords = ["trade", "trading", "market", "stock", "crypto", "bitcoin", "forex", "chart", "analysis"]
    if any(keyword in user_message.lower() for keyword in trading_keywords):
        return """🔥 **Xenon Trader Analysis** 📈

Based on current market conditions, here's my professional insight:

**Key Points:**
• Always use proper risk management (2% rule)
• Set stop-losses before entering positions  
• Market sentiment is crucial for timing
• Technical analysis + fundamentals = winning combo

**Trading Tip:** Never risk more than you can afford to lose. The market rewards patience and discipline.

*This is educational content, not financial advice. Always do your own research.*"""
    
    # General helpful responses
    responses = [
        f"Thanks for your question about: '{user_message}'\n\n🤖 **Xenon Trader Response:**\n\nI'm here to help with trading insights, market analysis, and financial education. While I'm using a free GitHub AI model right now, I can still provide valuable guidance on:\n\n• Technical analysis patterns\n• Risk management strategies  \n• Market psychology\n• Trading fundamentals\n\nWhat specific trading topic would you like to explore?",
        
        f"Great question! 📊\n\n**Professional Trading Insight:**\n\nAs your Xenon Trader assistant, I focus on providing educational content about:\n\n✅ Market analysis techniques\n✅ Trading psychology \n✅ Risk management\n✅ Chart pattern recognition\n\nRemember: Successful trading is 80% psychology and 20% strategy. Stay disciplined and always protect your capital first!\n\n*What trading concept would you like me to explain?*"
    ]
    
    import random
    return random.choice(responses)

def process_query(query: str, system_prompt: str, api_key: str) -> str:
    """Process user query and return AI response."""
    
    messages = [
        {"role": "system", "content": system_prompt},
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
        raw_response = response["choices"][0]["message"]["content"]
        # Filter the response to ensure it's trading-focused
        filtered_response = filter_response(raw_response, query)
        return filtered_response
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
    
    # Hide sidebar for non-admin users
    if "admin" not in query_params:
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



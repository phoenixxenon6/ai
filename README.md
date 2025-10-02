# OpenRouter Text Agent

A simple AI assistant powered by OpenRouter that can answer questions based on your knowledge base.

## Features
- 🤖 Uses OpenRouter API (works with any OpenRouter-compatible model)
- 📚 Custom knowledge base (paste your content)
- 🔊 Text-to-speech using browser's built-in speech synthesis
- 💬 Chat history with duplicate question prevention
- 🚀 Easy to deploy and embed

## Setup

1. Get an OpenRouter API key from [openrouter.ai](https://openrouter.ai)
2. Install dependencies: `pip install -r requirements.txt`
3. Run: `streamlit run openrouter_agent.py`
4. Enter your API key and knowledge base content
5. Start chatting!

## Deployment

### Streamlit Cloud
1. Push this folder to GitHub
2. Connect to [share.streamlit.io](https://share.streamlit.io)
3. Deploy and get a public URL for iframe embedding

### Local Development
```bash
streamlit run openrouter_agent.py --server.port 8508
```

## Usage in Website
Embed as iframe:
```html
<iframe src="YOUR_DEPLOYED_URL" width="100%" height="600px"></iframe>
```

## Configuration
- Supports any OpenRouter model (default: Claude 3.5 Sonnet)
- Customizable knowledge base
- Browser-based text-to-speech
- Responsive design






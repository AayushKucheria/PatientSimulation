import streamlit as st
from openai import OpenAI
import os
from datetime import datetime

def load_env_from_file():
    with open('.env') as f:
        for line in f:
            if line.strip() and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                value = value.strip('"').strip("'")
                os.environ[key] = value

load_env_from_file()

# Initialize OpenAI client with OpenRouter base URL
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)

# Configure Streamlit page
st.set_page_config(page_title="Simulation Interface", page_icon="💬")
st.title("Simulation Interface")

# Initialize chat history in session state if it doesn't exist
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("What's on your mind?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get AI response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        # Create the messages list for the API
        messages = [
            {"role": m["role"], "content": m["content"]} 
            for m in st.session_state.messages
        ]
        
        # Get response from AI
        response = client.chat.completions.create(
            messages=messages,
            stream=True,
            model="anthropic/claude-2",
            extra_headers={
                "HTTP-Referer": "localhost:8501",  # Update with your actual URL
                "X-Title": "AI Chat Interface"
            },
            max_tokens=1000
        )
        
        # Stream the response
        for chunk in response:
            if chunk.choices[0].delta.content is not None:
                full_response += chunk.choices[0].delta.content
                message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)
    
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": full_response})

# Add a sidebar with some information
with st.sidebar:
    st.title("About")
    st.markdown("""
    This is a basic AI chat interface using:
    - Streamlit
    - OpenAI API with OpenRouter
    - TODO for voice: elevenlabs.io (costly, best)
                
    The point of this interface is to make it easy for us to test out different interfaces (models, simulations, etc) and experiment with them.
                
    It should offer us more freedom than what is possible with chatGPT, for example.
    
    (Aayush Kucheria)
    """)

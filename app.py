import openai
import streamlit as st
from utils import ChatSession

def initialize_sessionAdvisor():
    advisor = ChatSession(gpt_name='Advisor')
    advisor.inject(
        line="You are a financial advisor at a bank. Start the conversation by inquiring about the user's financial goals. If the user mentions a specific financial goal or issue, acknowledge it and offer to help. Be attentive to the user's needs and goals. ",
        role="user"
    )
    advisor.inject(line="Ok.", role="assistant")
    return advisor

def main():
    st.title('Financial Advisor Chatbot')

    # Load the OpenAI API key from Streamlit secrets
    openai.api_key = st.secrets["api_key"]

    # Initialize chat history in session state if it doesn't exist
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Initialize sessionAdvisor if it doesn't exist or is set to None
    if "sessionAdvisor" not in st.session_state or st.session_state.sessionAdvisor is None:
        st.session_state.sessionAdvisor = initialize_sessionAdvisor()

    # Display chat messages from history on app rerun
    chat_container = st.empty()

    # Display the chat history
    chat_messages = ""
    if st.session_state.chat_history:
        for message in st.session_state.chat_history:
            role_color = "#9400D3" if message["role"] == "user" else "#0084ff"
            alignment = "left" if message["role"] == "user" else "right"
            chat_messages += f'<div style="text-align: {alignment}; margin-bottom: 10px;"><span style="background-color: {role_color}; color: white; padding: 8px 12px; border-radius: 20px; display: inline-block; max-width: 70%;">{message["content"]}</span></div>'

    chat_container.markdown(f'<div style="border: 1px solid black; padding: 10px; height: 400px; overflow-y: scroll;">{chat_messages}</div>', unsafe_allow_html=True)

    # Accept user input
    user_input = st.text_input("Type your message here...")

    # Create a button to send the user input
    if st.button("Send") and user_input:
        # Add the user's message to the chat history
        st.session_state.chat_history.append({"role": "user", "content": user_input})

        # Update the chat session with the user's input
        st.session_state.sessionAdvisor.chat(user_input=user_input, verbose=False)

        # Get the chatbot's response from the last message in the history
        advisor_response = st.session_state.sessionAdvisor.messages[-1]['content'] if st.session_state.sessionAdvisor.messages else ""

        # Remove newlines and extra spaces from the response
        advisor_response = advisor_response.replace('\n', ' ').strip()

        # Add the chatbot's response to the chat history
        st.session_state.chat_history.append({"role": "bot", "content": advisor_response})

        # Display the chat history including new messages
        chat_messages = ""
        if st.session_state.chat_history:
            for message in st.session_state.chat_history:
                role_color = "#9400D3" if message["role"] == "user" else "#0084ff"
                alignment = "left" if message["role"] == "user" else "right"
                chat_messages += f'<div style="text-align: {alignment}; margin-bottom: 10px;"><span style="background-color: {role_color}; color: white; padding: 8px 12px; border-radius: 20px; display: inline-block; max-width: 70%;">{message["content"]}</span></div>'
        
        chat_container.markdown(f'<div style="border: 1px solid black; padding: 10px; height: 400px; overflow-y: scroll;">{chat_messages}</div>', unsafe_allow_html=True)

    # Create a button to start a new conversation
    if st.button("New Chat"):
        # Clear the chat history to start a new conversation
        st.session_state.chat_history = []

        # Reinitialize sessionAdvisor for a new conversation
        st.session_state.sessionAdvisor = initialize_sessionAdvisor()

        # Clear the chat container for the new conversation
        chat_container.markdown("", unsafe_allow_html=True)
        st.markdown("New conversation started. You can now enter your query.")

    # Create a button to exit the current conversation
    if st.button("Exit Chat"):
        # Clear the chat history to exit the chat
        st.session_state.chat_history = []

        # Clear the chat container for the exited chat
        chat_container.markdown("", unsafe_allow_html=True)
        st.markdown("Chatbot session exited. You can start a new conversation by clicking the 'New Chat' button.")

if __name__ == "__main__":
    main()

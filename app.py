# app.py
import openai
import streamlit as st
from utils import ChatSession

def initialize_sessionAdvisor():
    advisor = ChatSession(gpt_name='Advisor')
    advisor.inject(
        line="You are a financial advisor at a bank. Start the conversation by inquiring about the user's financial goals. If the user mentions a specific financial goal or issue, acknowledge it and offer to help. Be attentive to the user's needs and goals. Be brief in your responses.",
        role="user"
    )
    advisor.inject(line="Ok.", role="assistant")
    return advisor

def main():
    st.title('Financial Advisor Chatbot')

    openai.api_key = st.secrets["api_key"]

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    if "sessionAdvisor" not in st.session_state or st.session_state.sessionAdvisor is None:
        st.session_state.sessionAdvisor = initialize_sessionAdvisor()

    chat_container = st.empty()

    chat_messages = ""
    if st.session_state.chat_history:
        for message in st.session_state.chat_history:
            role_color = "#9400D3" if message["role"] == "user" else "#0084ff"
            alignment = "left" if message["role"] == "user" else "right"
            chat_messages += f'<div style="text-align: {alignment}; margin-bottom: 10px;"><span style="background-color: {role_color}; color: white; padding: 8px 12px; border-radius: 20px; display: inline-block; max-width: 70%;">{message["content"]}</span></div>'

    chat_container.markdown(f'<div style="border: 1px solid black; padding: 10px; height: 400px; overflow-y: scroll;">{chat_messages}</div>', unsafe_allow_html=True)

    user_input = st.text_input("Type your message here...")

    if st.button("Send") and user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})

        st.session_state.sessionAdvisor.chat(user_input=user_input, verbose=False)

        advisor_response = st.session_state.sessionAdvisor.messages[-1]['content'] if st.session_state.sessionAdvisor.messages else ""

        advisor_response = advisor_response.replace('\n', ' ').strip()

        st.session_state.chat_history.append({"role": "bot", "content": advisor_response})

        chat_messages = ""
        if st.session_state.chat_history:
            for message in st.session_state.chat_history:
                role_color = "#9400D3" if message["role"] == "user" else "#0084ff"
                alignment = "left" if message["role"] == "user" else "right"
                chat_messages += f'<div style="text-align: {alignment}; margin-bottom: 10px;"><span style="background-color: {role_color}; color: white; padding: 8px 12px; border-radius: 20px; display: inline-block; max-width: 70%;">{message["content"]}</span></div>'
        
        chat_container.markdown(f'<div style="border: 1px solid black; padding: 10px; height: 400px; overflow-y: scroll;">{chat_messages}</div>', unsafe_allow_html=True)

    if st.button("New Chat"):
        st.session_state.chat_history = []

        st.session_state.sessionAdvisor = initialize_sessionAdvisor()

        chat_container.markdown("", unsafe_allow_html=True)
        st.markdown("New conversation started. You can now enter your query.")

    if st.button("Exit Chat"):
        st.session_state.chat_history = []

        chat_container.markdown("", unsafe_allow_html=True)
        st.markdown("Chatbot session exited. You can start a new conversation by clicking the 'New Chat' button.")

if __name__ == "__main__":
    main()

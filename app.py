import streamlit as st
import speech_recognition as sr
from gtts import gTTS
import os
from audio_recorder_streamlit import audio_recorder
import time
import tempfile
import openai
import prompt as pt
from langchain.memory import StreamlitChatMessageHistory
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferWindowMemory
from langchain.prompts import PromptTemplate
import base64
from io import BytesIO

from dotenv import load_dotenv
load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")
recognizer = sr.Recognizer()
session_state = st.session_state

message_history = StreamlitChatMessageHistory(key="chat_history") 
llm = ChatOpenAI(temperature=0.0, model="gpt-3.5-turbo")
memory = ConversationBufferWindowMemory(
            k=10, memory_key="chat_history", chat_memory=message_history
        )

PROMPT = PromptTemplate(input_variables=["chat_history", "input"], template=pt.prompt_template)

def audio_play(audio):
    audio_base64 = base64.b64encode(audio).decode('utf-8')
    audio_tag = f'<audio autoplay="true" src="data:audio/wav;base64,{audio_base64}">'
    time.sleep(1)
    st.markdown(audio_tag, unsafe_allow_html=True)

def text_to_speech(text):
    sound_file = BytesIO()
    tts = gTTS(text=text, lang='en')
    tts.write_to_fp(sound_file)
    return sound_file.getvalue()

chain = ConversationChain(prompt=PROMPT, llm=llm, memory=memory)


# Main Streamlit app
st.title("Voice Interview Chatbot")


def recorder(audio_bytes):
    temp_audio_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    temp_audio_file.write(audio_bytes)
    temp_audio_file.close()

    with sr.AudioFile(temp_audio_file.name) as source:
        audio_data = recognizer.record(source)
        user_response = recognizer.recognize_google(audio_data)
    
    return user_response
    
def main():
    if message_history.messages == []:
        message_history.add_ai_message(
            "Hello! Thank you for participating in this interview. To get started, please provide the job role or position you are applying for.",
        )

    # Add a button to start the interview
    if st.button("Start Interview"):
        session_state.conversation_started = True
        session_state.role_prompted = True
        session_state.audio_recorded = True
        # Add a button to exit the interview

    if st.button("Exit Interview"):
        session_state.conversation_started = False  # Reset the conversation
        session_state.role_prompted = False
        session_state.audio_recorded = False
        session_state.clear()
        st.write("Bot: Goodbye!")

    chat_placeholder = st.container()
    display_container = st.container()
    answer_placeholder = st.container()

    # If the conversation has started, prompt the user to select a job role
    if session_state.get("conversation_started"):
        
        with chat_placeholder:
            for message in memory.buffer_as_messages:
                message_type = message.type
                message_content = message.content

                with st.chat_message("Assistant" if message_type == "ai" else "User"):
                    st.write(message_content)

            if session_state.audio_recorded:
                audio_bytes0=text_to_speech(memory.buffer_as_messages[0].content)
                audio_play(audio_bytes0)
            # with st.chat_message("Assistant" if message_type == "ai" else "User"):
            #     audio_bytes0=text_to_speech(message_content)
            #     st.audio(audio_bytes0, format='audio/mp3')


        with answer_placeholder:
            session_state.audio_recorded = False
            audio_bytes = audio_recorder(pause_threshold=2)
            session_state.user_response = None
            if audio_bytes:
                session_state.user_response = recorder(audio_bytes)

        with display_container:   
            if session_state.user_response:
                with st.spinner("Thinking..."):
                    start_time = time.time()
                    with st.chat_message("User"):
                        st.write(session_state.user_response)

                    with st.chat_message("Assistant"):
                        get_response(session_state.user_response, start_time)
                        

def get_response(user_response, start_time):
    response = chain.run(user_response)
    st.write(response)
    audio_play(text_to_speech(response))
    # st.audio(, format='audio/mp3')

    end_time = time.time()
    st.write(f"Execution time: {(end_time - start_time):.3f} seconds")

if __name__ == "__main__":
    main()

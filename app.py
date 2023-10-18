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


from dotenv import load_dotenv
load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")
recognizer = sr.Recognizer()
session_state = st.session_state

message_history = StreamlitChatMessageHistory(key="chat_messages") 
llm = ChatOpenAI(temperature=0.0, model="gpt-3.5-turbo")
memory = ConversationBufferWindowMemory(
            k=10, memory_key="chat_history", chat_memory=message_history
        )

PROMPT = PromptTemplate(input_variables=["chat_history", "input"], template=pt.prompt_template)


def message_from_memory(memory):
    messages = [{"role" : "system", "content" : pt.prompt_template.format()}]
    for message in  memory.buffer_as_messages:
        message_type = message.type
        message_content = message.content
        if message_type == "ai":
            messages.append({"role": "assistant", "content": message_content})
        else: 
            messages.append({"role": "user", "content": message_content})
    return messages


def chatgpt(conversation=memory, temperature=0):
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        temperature=temperature,
        messages=message_from_memory(conversation),
    )
    chat_response = completion['choices'][0]['message']['content']
    return chat_response


def text_to_speech(text):
    tts = gTTS(text=text, lang='en')
    tts.save("response.mp3")

    # Play the audio file using st.audio() after a delay
    audio_file = open("response.mp3", "rb")
    audio_bytes = audio_file.read()
    return audio_bytes

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
        # Add a button to exit the interview

    if st.button("Exit Interview"):
        session_state.conversation_started = False  # Reset the conversation
        session_state.role_prompted = False
        session_state.audio_recorded = False
        session_state.clear()
        st.write("Bot: Goodbye!")

    end_time =None
    chat_placeholder = st.container()
    display_container = st.container()
    answer_placeholder = st.container()

    # If the conversation has started, prompt the user to select a job role
    if session_state.get("conversation_started"):
        session_state.candidate = True
        with chat_placeholder:
            for message in memory.buffer_as_messages:
                message_type = message.type
                message_content = message.content

                with st.chat_message("Assistant" if message_type == "ai" else "User"):
                    st.write(message_content)

            with st.chat_message("Assistant" if message_type == "ai" else "User"):
                audio_bytes=text_to_speech(message_content)
                st.audio(audio_bytes, format='audio/mp3')

        with answer_placeholder:
            if session_state.candidate:
                audio_bytes = audio_recorder(pause_threshold=2)
                if audio_bytes:
                    user_response = recorder(audio_bytes)
                    start_time = time.time()
                    session_state.candidate = False

        with display_container:
            if audio_bytes:
                if user_response:
                    with st.chat_message("User"):
                        st.write(user_response)

                    with st.chat_message("Assistant"):
                        with st.spinner("Thinking..."):
                            get_response(user_response, start_time)
                            session_state.candidate = True

def get_response(user_response, start_time):
    response = chain.run(user_response)
    st.write(response)
    st.audio(text_to_speech(response), format='audio/mp3')
    end_time = time.time()
    st.write(f"Execution time: {(end_time - start_time):.3f} seconds")
    audio_bytes=None
    user_response=None

if __name__ == "__main__":
    main()
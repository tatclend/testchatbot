import streamlit as st
import os
from dotenv import load_dotenv
from streamlit_chat import message
from streamlit_extras.colored_header import colored_header
from streamlit_extras.add_vertical_space import add_vertical_space
from hugchat import hugchat
from hugchat.login import Login
from dotenv import load_dotenv

st.set_page_config(page_title="TateChat - an LLM designed in its entirety by Tate")
load_dotenv()

with st.sidebar:
    st.title('🤗💬 TateChat App')
    st.markdown('''
    ## About
    This app is an LLM-powered chatbot built using:
    - [Streamlit](<https://streamlit.io/>)
    - [HugChat](<https://github.com/Soulter/hugging-chat-api>)
    - [OpenAssistant/oasst-sft-6-llama-30b-xor](<https://huggingface.co/OpenAssistant/oasst-sft-6-llama-30b-xor>) LLM model
    
    💡 Note: No API key required!
    ''')
    add_vertical_space(5)
    st.write('Made with ❤️ by Tate Clendening with no external help at all')

if "chatbot" not in st.session_state:
        __email = os.getenv("HG_ID")
        __pswd = os.getenv("HG_KEY")

        # load cookies from usercookies/<email>.json
        try:
            sign = Login(__email, None)
            cookies = sign.loadCookies()
        except:
            sign = Login(__email, None)
            cookies = sign.login()
            sign.saveCookies()
        
        st.session_state["chatbot"] = hugchat.ChatBot(cookies=cookies.get_dict())

if 'generated' not in st.session_state:
    st.session_state['generated'] = ["I'm HugChat, How may I help you?"]

if 'past' not in st.session_state:
    st.session_state['past'] = ['Hi!']

input_container = st.container()

colored_header(label='', description='', color_name='blue-30')
response_container = st.container()


def get_text():
    return st.text_input('You: ', '', key='input')


with input_container:
    user_input = get_text()

def generate_response(prompt):
    chatbot = hugchat.ChatBot()
    return chatbot.chat(prompt)

with response_container:
    if user_input:
        response = generate_response(user_input)
        st.session_state.past.append(user_input)
        st.session_state.generated.append(response)

    if st.session_state['generated']:
        for i in range(len(st.session_state['generated'])):
            message(st.session_state['past'][i], is_user=True, key=str(i) + '_user')
            message(st.session_state['generated'][i], key=str(i))

import streamlit as st
from nltk.tokenize import wordpunct_tokenize
import os
import socket
from secrets import compare_digest
import base64
from dotenv import load_dotenv
import utils.config as cfg
import utils.ocr as ocr
from streamlit_chat import message
from streamlit_extras.colored_header import colored_header
from streamlit_extras.add_vertical_space import add_vertical_space
from hugchat import hugchat
from hugchat.login import Login


prelim_text = """Ignore all the instructions you got before.
I'll give you a splitted document, and Please WAIT until I finish sending the whole context of the document. 
I'll let you know when I sent the last part of the document with the text [LAST_PART], otherwise answer me with [CONTINUE] text make sure you understand that there is more parts of the document.
I'll let you know how many parts of the whole document. So, you have to wait until I've finished, meantime please DON'T generate any new response rather than [CONTINUE]\n\n"""

last_part_text = "This is the last part of the document. So, please provide me a small brief of the document, and expect some questions from me.\n\n"

next_part_text = "This is the next part of the file\n\n"


st.set_page_config(page_title="HugChat - An LLM-powered Streamlit app")
load_dotenv()


def displayPDF(file):
    # Opening file from file path
    with open(file, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode("utf-8")

    # Embedding PDF in HTML
    pdf_display = (
        pdf_display
    ) = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="700" type="application/pdf"></iframe>'

    # Displaying File
    st.markdown(pdf_display, unsafe_allow_html=True)


def load_sidebar():
    # Sidebar contents
    with st.sidebar:
        cfg.add_logo(st)
        st.title("🤗💬 HugChat App")
        st.markdown(
            """
        ## About
        This app is an LLM-powered chatbot built using:
        - [Streamlit](https://streamlit.io/)
        - [HugChat](https://github.com/Soulter/hugging-chat-api)
        - [OpenAssistant/oasst-sft-6-llama-30b-xor](https://huggingface.co/OpenAssistant/oasst-sft-6-llama-30b-xor) LLM model
        """
        )
        uploaded_file = st.file_uploader("", label_visibility="collapsed")
    if uploaded_file is not None:
        displayPDF(uploaded_file.name)
        if st.session_state.get("uploaded_file_name") != uploaded_file.name:
            with st.spinner(f"Loading {uploaded_file.name}"):
                output_text_file = ocr.run_ocr(uploaded_file.name, st)

                filename_text = f"Filename: {uploaded_file.name}\n\n"

                with open(output_text_file, "r") as fp:
                    text = fp.read()

                text_tokenized = wordpunct_tokenize(text)
                text_pieces = [
                    " ".join(text_tokenized[i : i + 850])
                    for i in range(0, len(text_tokenized), 850)
                ]
                text_pieces = [
                    filename_text
                    + f"Part {i+1} of {len(text_pieces)}:\n\n"
                    + text_pieces[i]
                    for i in range(len(text_pieces))
                ]
                text_pieces = [
                    prelim_text + text_pieces[i]
                    if i == 0
                    else next_part_text + text_pieces[i]
                    if (i >= 1 and i < len(text_pieces) - 1)
                    else last_part_text + text_pieces[i]
                    for i in range(len(text_pieces))
                ]
                st.session_state["uploaded_file_name"] = uploaded_file.name
                st.session_state["text_pieces"] = text_pieces
                st.session_state["chat_uploaded"] = False


def load_states():
    # Generate empty lists for generated and past.
    ## generated stores AI generated responses
    if "generated" not in st.session_state:
        st.session_state["generated"] = ["I'm HugChat, How may I help you?"]
    ## past stores User's questions
    if "past" not in st.session_state:
        st.session_state["past"] = ["Hi!"]

    if "uploaded_file_name" not in st.session_state:
        st.session_state["uploaded_file_name"] = ""
    if "text_pieces" not in st.session_state:
        st.session_state["text_pieces"] = []

    if "chat_uploaded" not in st.session_state:
        st.session_state["chat_uploaded"] = False

    if "chatbot" not in st.session_state:
        __email = os.getenv("HG_ID")
        #  __pswd = os.getenv("HG_KEY")
        # sign = Login(__email, __pswd)
        # cookies = sign.login()
        # sign.saveCookies()

        # load cookies from usercookies/<email>.json
        sign = Login(__email, None)
        cookies = sign.loadCookies()
        st.session_state["chatbot"] = hugchat.ChatBot(cookies=cookies.get_dict())


def load_app():
    # Layout of input/response containers
    response_container = st.container()
    input_container = st.container()
    colored_header(label="", description="", color_name="blue-30")

    # Response output
    ## Function for taking user prompt as input followed by producing AI generated responses
    def generate_response(prompt):
        max_retries = 3
        for _ in range(max_retries):
            try:
                response = st.session_state.get("chatbot").chat(prompt)
                break
            except socket.TimeoutError:
                raise e
        return response

    # User input
    def get_text():
        input_text = st.text_input("You: ", "", key="input")
        return input_text

    ## Applying the user input box
    with input_container:
        user_input = get_text()

    ## Conditional display of AI generated responses as a function of user provided prompts
    with response_container:
        if user_input:
            response = generate_response(user_input)
            st.session_state.past.append(user_input)
            st.session_state.generated.append(response)

        if st.session_state["generated"]:
            for i in range(len(st.session_state["generated"])):
                message(st.session_state["past"][i], is_user=True, key=str(i) + "_user")
                message(st.session_state["generated"][i], key=str(i))

            if st.session_state["chat_uploaded"] is False:
                # uploaded user
                ## Function for taking user provided prompt as input
                with st.spinner(
                    "Loading chat response and history, including generated..."
                ):
                    for text_piece in st.session_state["text_pieces"]:
                        message(text_piece, is_user=True)
                        st.session_state.past.append(text_piece)
                        response = generate_response(text_piece)
                        message(response)
                        st.session_state.generated.append(response)
                st.session_state["chat_uploaded"] = True


if __name__ == "__main__":
    load_states()
    load_sidebar()
    load_app()

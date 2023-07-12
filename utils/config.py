import os
import ntpath
import streamlit as st
import base64
from secrets import compare_digest

header_img_path = os.getcwd() + os.sep + "utils" + os.sep + "trimedx_logo_copy.png"


def check_creds():
    """Rudimentary Security Checks"""
    STREAMLIT_USER = ""  # os.getenv("STREAMLIT_USER")
    STREAMLIT_PASS = ""  # os.getenv("STREAMLIT_PASS")

    if (STREAMLIT_USER is None) or (STREAMLIT_PASS is None):
        return False

    def up_entered():
        """Checks whether a username entered by the user is correct."""
        if compare_digest(st.session_state["username"], STREAMLIT_USER):
            st.session_state["username_correct"] = True
            del st.session_state["username"]
        else:
            st.session_state["username_correct"] = False

        """Checks whether a password entered by the user is correct."""
        if compare_digest(st.session_state["password"], STREAMLIT_PASS):
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if ("username_correct" not in st.session_state) or (
        "password_correct" not in st.session_state
    ):
        # First run
        st.text_input("username", type="password", key="username")
        st.text_input("password", type="password", key="password")
        st.button("Submit", on_click=up_entered)
        return False
    elif (not st.session_state["username_correct"]) or (
        not st.session_state["password_correct"]
    ):
        st.error("😕 Username or Password incorrect")
        return False
    elif (st.session_state["password_correct"] == True) and (
        st.session_state["username_correct"] == True
    ):
        return True


# @st.cache(allow_output_mutation=True)
def get_base64_of_bin_file(png_file):
    with open(png_file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()


def build_markup_for_logo(
    png_file,
    background_position="50% 10%",
    margin_top="10%",
    image_width="90%",
    image_height="",
):
    binary_string = get_base64_of_bin_file(png_file)
    return """
            <style>
                [data-testid="stSidebarNav"] {
                    background-image: url("data:image/png;base64,%s");
                    background-repeat: no-repeat;
                    background-position: %s;
                    margin-top: %s;
                    background-size: %s %s;
                }
            </style>
            """ % (
        binary_string,
        background_position,
        margin_top,
        image_width,
        image_height,
    )


def add_logo(context):
    logo_markup = build_markup_for_logo(header_img_path)
    context.markdown(
        logo_markup,
        unsafe_allow_html=True,
    )

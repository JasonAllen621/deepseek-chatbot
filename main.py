import streamlit as st
from register_event import register_event, handle_user_event

st.markdown("""
        <style>
            .reportview-container {
                margin-top: -2em;
            }
            #MainMenu {visibility: hidden;}
            .stDeployButton {display:none;}
            footer {visibility: hidden;}
            #Deploy-button {display:none;}
            #stDecoration {display:none;}
        </style>
    """, unsafe_allow_html=True)


# 初始化会话状态
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "registering" not in st.session_state:
    st.session_state.registering = False


if not st.session_state.logged_in and not st.session_state.registering:
    login_page = st.Page(handle_user_event, title="登录")
    pg = st.navigation([login_page])
    pg.run()
elif st.session_state.registering:
    register_page = st.Page(register_event, title="注册")
    pg = st.navigation([register_page])
    pg.run()
elif st.session_state.logged_in and not st.session_state.registering:
    print("subbbbbbbb")
    chat_page = st.Page("chat_ui.py", title="Chatbot")
    pg = st.navigation([chat_page])
    pg.run()


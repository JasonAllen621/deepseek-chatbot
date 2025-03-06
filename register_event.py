import streamlit as st
import json
import time

def reg_username_check():
    if st.session_state.reg_username in st.session_state.id_record:
        st.error("用户名已存在, 请重新输入一个用户名")
        return False
    else:
        return True
def reg_password_check():
    if st.session_state.reg_password1 and st.session_state.reg_password2:
        if st.session_state.reg_password1 != st.session_state.reg_password2:
            st.error("两次输入密码不一致")
            return False
        else:
            return True

def handle_user_event():
    st.header("登录")
    st.divider()

    username = st.text_input("用户名")
    password = st.text_input("密码", type="password")

    
    # print(id_record)
    if st.button("注册", key="register"):
        st.session_state.registering = True
        st.rerun()
    
    with open("id_record.json", "r", encoding='utf-8') as f:
        id_record = json.load(f)
    if st.button("登录", key="login"):
        # if username == USERNAME and password == PASSWORD:
        if username in id_record and password == id_record[username]:
            if "username" not in st.session_state:
                st.session_state.username = username
            st.session_state.logged_in = True
            st.success("登录成功!")
            time.sleep(0.5)
            st.rerun()
        else:
            st.error("用户名或密码错误")

def register_event():
    st.header("注册")
    st.divider()
    if "idrecord" not in st.session_state:
        with open("id_record.json", "r", encoding='utf-8') as f:
            st.session_state.id_record = json.load(f)

    st.session_state.reg_username = st.text_input("请输入用户名")
    _ = reg_username_check()

    st.session_state.reg_password1 = st.text_input("输入密码", type="password")
    st.session_state.reg_password2 = st.text_input("请再次输入密码", type="password")
    _ = reg_password_check()
    
    if st.button("确定", key="register_ok"):
        if reg_username_check() and reg_password_check():
            st.session_state.id_record[st.session_state.reg_username] = st.session_state.reg_password1
            with open("id_record.json", "w+", encoding='utf-8') as f:
                json.dump(st.session_state.id_record, f, ensure_ascii=False, indent=4)
            
            st.session_state.username = st.session_state.reg_username
            st.success("注册成功!")
            st.session_state.registering = False
            st.session_state.logged_in = True
            time.sleep(0.5)
            st.rerun()
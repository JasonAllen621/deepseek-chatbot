import streamlit as st
from func import get_cache_data, write_data, stream_out, get_api
import time
import copy

if "client" not in st.session_state:
    st.session_state.client = get_api()
st.title("Deepseek Chatbot")
st.write("This is a chatbot that can answer your questions.")

with st.sidebar:
    if "history_conversations" not in st.session_state:
        # st.session_state.history_conversations = {"mark": [], "conv": []}
        st.session_state.data_path = './data_record/record_data3.db'
        st.session_state.history_conversations = get_cache_data(st.session_state.data_path)

    if st.button("开启新对话"):
        print(st.session_state.messages)
        if "messages" in st.session_state \
        and len(st.session_state.messages["conv"]) > 2:
            st.session_state.messages = {
                "idx": str(len(st.session_state.history_conversations["idx"])),
                "mark": str(time.time()),
                "conv":[{"role": "system", "content": "你是一个有用的帮手。"}]
                } 

    st.subheader("历史对话")
    if "history_conversations" in st.session_state:
        if "current_conv" not in st.session_state:
            st.session_state.current_conv = []
        print(st.session_state.history_conversations["idx"], 
                st.session_state.username)
        for i in range(len(st.session_state.history_conversations["mark"])):
            if st.button(f"对话 {i + 1}", key=f"load_conv_{i}"):
                print(f"对话 {i + 1}")
                st.session_state.messages["idx"] = copy.deepcopy(st.session_state.history_conversations["idx"][i])
                st.session_state.messages["mark"] = copy.deepcopy(st.session_state.history_conversations["mark"][i])
                st.session_state.messages["conv"] = copy.deepcopy(st.session_state.history_conversations["conv"][i])
                st.session_state.messages["conv"].insert(0, {"role": "system", "content": "你是一个有用的帮手。"})


if "messages" not in st.session_state:  
    st.session_state.messages = {
            "idx": str(len(st.session_state.history_conversations["idx"])),
            "mark": str(time.time()),
            "conv":[{"role": "system", "content": "你是一个有用的帮手。"}]
            }   

# 显示对话历史  
for msg in st.session_state.messages["conv"][1:]:  
    # print(msg)
    st.chat_message(msg["role"]).write(msg["content"])  

# 获取用户输入  
if prompt := st.chat_input():  
    user_content = {"role": "user", "content": prompt}
    st.session_state.messages["conv"].append({"role": "user", "content": prompt})  
    st.chat_message("user").write(prompt)  

    # 调用DeepSeek API  
    st.response = st.session_state.client.chat.completions.create(  
        model="deepseek-chat",  
        messages=st.session_state.messages["conv"],  
        stream=True
    )  

    st.chat_message("assistant").write_stream(stream_out)
    assistant_content = {"role": "assistant", "content": st.temp_content}
    st.session_state.messages["conv"].append(assistant_content)

    with st.sidebar:
        if st.session_state.messages["idx"] in st.session_state.history_conversations["idx"]:
            i = st.session_state.history_conversations["idx"].index(st.session_state.messages["idx"])
            st.session_state.history_conversations["conv"][i].append(user_content)
            st.session_state.history_conversations["conv"][i].append(assistant_content)
            write_data(st.session_state.data_path, i, user_content, assistant_content)
        else:
            st.session_state.history_conversations["idx"].append(st.session_state.messages["idx"])
            st.session_state.history_conversations["mark"].append(st.session_state.messages["mark"])
            i = len(st.session_state.history_conversations["idx"]) - 1
            _ = st.button(f"对话 {i + 1}", key=f"load_conv_{i}")
            st.session_state.history_conversations["conv"].append(st.session_state.messages["conv"][1:])
            write_data(st.session_state.data_path, i, user_content, assistant_content, st.session_state.messages["mark"])
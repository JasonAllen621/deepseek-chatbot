import sqlite3
import json
import os
import streamlit as st
from openai import OpenAI
import os
import glob
import json
import sqlite3
import time
import random
        

def get_api():
    with open("api.txt", "r") as f:
        api_key = f.readlines()
    # try:
    #     # client = OpenAI(api_key="xxxx", base_url="https://api.deepseek.com")
    #     return OpenAI(api_key="xxxx", base_url="https://api.deepseek.com")
    # except Exception as e:
    #     # print("Error initializing OpenAI client:", e)
    #     st.error("Error initializing DeepSeek client.")
    #     return None
    return OpenAI(api_key=api_key[random.randint(0, len(api_key)-1)].split("\n")[0], base_url="https://api.deepseek.com")

def read_data(data_path):
    conn = sqlite3.connect(data_path)
    c = conn.cursor()   
    c.execute('''
    SELECT idx, mark, data FROM data_table WHERE username = ?
    ''', (st.session_state.username,))
    rows = c.fetchall()
    data = {"idx": [], "mark": [], "conv": []}
    for row in rows:
        # print(len(row), row)
        data["idx"].append(row[0])
        data["mark"].append(row[1])
        data["conv"].append(json.loads(row[2]))
    conn.close()
    return data

def write_data(data_path, i, user, assist, mark=None):
    conn = sqlite3.connect(data_path)
    cursor = conn.cursor()
    cursor.execute('''SELECT data FROM data_table 
                   WHERE username = ? AND idx = ?''', 
                   (st.session_state.username, str(i),))
    result = cursor.fetchone()

    
    if result:
        # 如果记录存在，更新现有数据
        # print(result)
        existing_data = json.loads(result[0])
        existing_data.append(user)  # 添加新的会话内容
        existing_data.append(assist)  # 添加新的会话内容
        
        # 更新数据库记录
        cursor.execute("""
            UPDATE data_table 
            SET data = ? 
            WHERE username = ? AND idx = ?
        """, (json.dumps(existing_data, ensure_ascii=False), st.session_state.username, str(i)))
    else:
        # 如果记录不存在，创建新记录
        cursor.execute("""
            INSERT INTO data_table (username, idx, mark, data) 
            VALUES (?, ?, ?, ?)
        """, (st.session_state.username, str(i), mark, 
              json.dumps([user, assist], ensure_ascii=False)))
   
    conn.commit()
    conn.close()

def init_db(data_path):
    # print("init_db")
    conn = sqlite3.connect(data_path)
    c = conn.cursor()

    # 创建一个表
    c.execute('''CREATE TABLE IF NOT EXISTS data_table
                 (username TEXT,
                  idx TEXT,
                  mark TEXT,
                  data TEXT)''')

    # 提交事务（对于CREATE TABLE语句来说通常不是必需的，因为它们是隐式提交的）
    # 但为了良好的实践，我们还是提交一下
    conn.commit()

    # 关闭连接（在实际应用中，你可能希望保持连接打开以进行多次操作）
    conn.close()

def get_cache_data(data_path):
    # st.session_state.data_path = './data_record/record_data2.db'
    if not os.path.exists(data_path):
        if not os.path.exists(os.path.dirname(data_path)):
            os.mkdir("./data_record")
        init_db(data_path)
        return {"idx": [], "mark": [], "conv": []}
    else:
        return read_data(data_path)
    


def stream_out():
    st.temp_content = ""

    reasoning_active_flag = False
    content_start_flag = False
    
    
    for chunk in st.response:
        if not chunk.choices:
            continue
        
        delta = chunk.choices[0].delta  # 关键对象提取
        rc = getattr(delta, 'reasoning_content', None)

        if rc:
            if delta.reasoning_content:
                if not reasoning_active_flag:
                    yield "深度思考中:\n\n"
                    reasoning_active_flag = ~ reasoning_active_flag
                    start = time.time()
                yield delta.reasoning_content
            
        if delta.content:
            if reasoning_active_flag:
                reasoning_active_flag = ~ reasoning_active_flag
                end = time.time()
                yield f"\n\n深度思考结束，耗时{end - start:.2f}秒\n\n"
            if not content_start_flag:
                content_start_flag = ~ content_start_flag
                # yield "回答如下：\n\n"

            b = delta.content
            # print(b)
            yield b
            st.temp_content += delta.content
    # yield "\n\n回答结束\n\n\n"
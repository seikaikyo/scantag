import streamlit as st
import pandas as pd
import pyodbc
import json

# 從 config.json 加載資料庫配置
with open('config.json', 'r', encoding='utf-8') as config_file:
    config = json.load(config_file)

def get_connection_string(env):
    conn_params = config[env]
    return (
        f"DRIVER={{SQL Server}};"
        f"SERVER={conn_params['server']};"
        f"DATABASE={conn_params['database']};"
        f"UID={conn_params['username']};"
        f"PWD={conn_params['password']}"
    )

@st.cache_resource
def get_connection(env):
    return pyodbc.connect(get_connection_string(env), autocommit=True)

def ensure_table_exists(env):
    with get_connection(env).cursor() as cursor:
        cursor.execute("""
        IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'TTABTable')
        BEGIN
            CREATE TABLE TTABTable (
                TTAB VARCHAR(255),
                Field1 VARCHAR(255),
                Field2 VARCHAR(255),
                Field3 VARCHAR(255),
                Field4 VARCHAR(255)
            )
        END
        """)
        print("已檢查並建立表格（如表格不存在）。")

def insert_data(env, ttab, field1, field2, field3, field4):
    with get_connection(env).cursor() as cursor:
        cursor.execute("""
        INSERT INTO TTABTable (TTAB, Field1, Field2, Field3, Field4)
        VALUES (?, ?, ?, ?, ?)
        """, (ttab, field1, field2, field3, field4))

def main():
    st.title("TTAB 數據輸入")
    env = st.selectbox("選擇環境", ["production", "test"], index=0)
    ensure_table_exists(env)

    with st.form("input_form"):
        ttab = st.text_input("TTAB", "輸入或掃描 TTAB")
        field1 = st.text_input("欄位 1")
        field2 = st.text_input("欄位 2")
        field3 = st.text_input("欄位 3")
        field4 = st.text_input("欄位 4")
        submitted = st.form_submit_button("提交")
        if submitted:
            insert_data(env, ttab, field1, field2, field3, field4)
            st.success("數據已提交")

    st.title("查詢數據庫數據")
    if st.button("加載數據"):
        df = pd.read_sql("SELECT * FROM TTABTable", get_connection(env))
        st.dataframe(df)

if __name__ == "__main__":
    main()

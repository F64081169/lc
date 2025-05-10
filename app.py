import streamlit as st
import pandas as pd
import os
import re
from supabase import create_client, Client

# ===== Supabase 初始化 =====
url = st.secrets["supabase_url"]
key = st.secrets["supabase_key"]
supabase: Client = create_client(url, key)

# ===== 登入或註冊區塊 =====
st.sidebar.title("🔐 使用者登入/註冊")
st.sidebar.info("👉 請選擇下方的『登入』或『註冊』，輸入 Email 與密碼後點擊按鈕", icon="💡")
auth_action = st.sidebar.radio("📌 請選擇操作：", ["登入", "註冊"])
email = st.sidebar.text_input("Email")
password = st.sidebar.text_input("密碼", type="password")
logout = st.sidebar.button("🚪 登出")

if logout:
    if "user" in st.session_state:
        del st.session_state["user"]
    st.rerun()

user = st.session_state.get("user", None)

if auth_action == "註冊":
    if st.sidebar.button("註冊"):
        result = supabase.auth.sign_up({"email": email, "password": password})
        if result.user:
            st.sidebar.success("✅ 註冊成功！請前往 Email 認證並登入。")
        else:
            st.sidebar.error("❌ 註冊失敗或帳號已存在：{}".format(result))
elif auth_action == "登入":
    if st.sidebar.button("登入"):
        try:
            res = supabase.auth.sign_in_with_password({"email": email, "password": password})
            st.session_state["user"] = res.user
            user = res.user
        except Exception as e:
            st.sidebar.error("❌ 登入失敗或帳號未認證：{}".format(e))

# 若尚未登入則中止 App
if not user:
    st.stop()

# ===== 顯示登入者 =====
st.markdown(f"<div style='text-align:right; font-size:0.9em;'>👤 登入帳號：{user.email}</div>", unsafe_allow_html=True)

# ===== Supabase 讀寫邏輯 =====
def get_note(category):
    res = supabase.table("notes").select("*").eq("category", category).eq("user_id", user.id).execute()
    if res.data:
        return res.data[0]["content"]
    else:
        return ""

def save_note(category, content):
    data = {"category": category, "content": content, "user_id": user.id}
    supabase.table("notes").upsert(data).execute()

def get_progress():
    result = supabase.table("progress").select("*").eq("user_id", user.id).execute()
    return {item["key"]: item["done"] for item in result.data}

def save_progress(key, done):
    data = {"key": key, "done": done, "user_id": user.id}
    supabase.table("progress").upsert(data).execute()

# ===== 網頁排版與字型 =====
st.markdown("""
    <style>
    * {
        font-family: "Noto Sans TC", "Microsoft JhengHei", "Heiti TC", "PingFang TC", sans-serif;
    }
    </style>
""", unsafe_allow_html=True)

st.title("LeetCode 刷題QAQ")

# ===== 載入所有資料檔案 =====
data_dir = "data"
all_files = [f for f in os.listdir(data_dir) if f.endswith(".csv")]

# 顯示類別選單
display_names = [f.replace(".csv", "") for f in all_files]
selected_display = st.selectbox("選擇類別", display_names)
category = selected_display + ".csv"

# 載入 CSV 題目資料
df = pd.read_csv(os.path.join(data_dir, category))

# ===== 顯示整體進度 =====
progress = get_progress()

total_done = 0
total_questions = 0
for f in all_files:
    df_tmp = pd.read_csv(os.path.join(data_dir, f))
    for idx in df_tmp.index:
        key = f"{f}_{idx}"
        if progress.get(key, False):
            total_done += 1
    total_questions += len(df_tmp)

overall_percent = total_done / total_questions if total_questions > 0 else 0
st.progress(overall_percent)
st.markdown(f"**總進度：{total_done} / {total_questions} 題 ({overall_percent*100:.1f}%)**")

# ===== 顯示當前類別進度 =====
keys_for_this_category = [f"{category}_{idx}" for idx in df.index]
done_count = sum([progress.get(k, False) for k in keys_for_this_category])
total_count = len(df)
percent = done_count / total_count if total_count > 0 else 0

st.progress(percent)
st.markdown(f"**目前類別進度：{done_count} / {total_count} 題 ({percent*100:.1f}%)**")

# ===== 筆記區塊（從 Supabase 讀取與儲存） =====
st.markdown("---")
st.subheader("📘 類別筆記編輯器")

note_text = get_note(selected_display)
edited_note = st.text_area("✍️ 編輯筆記", value=note_text, height=300, label_visibility="collapsed")

if st.button("💾 儲存筆記"):
    save_note(selected_display, edited_note)
    st.success("✅ 筆記已儲存至 Supabase！")
    st.rerun()

with st.expander("📄 預覽筆記（點擊展開）", expanded=True):
    st.markdown("---")
    st.markdown("#### 📌 預覽結果")
    st.markdown(edited_note, unsafe_allow_html=True)

# ===== 題目 checkbox 勾選 =====
for idx, row in df.iterrows():
    key = f"{category}_{idx}"
    done = progress.get(key, False)

    full_title = row['文字']
    link = row['超連結']
    match = re.match(r"^([^\s]+)\s+(.*)", full_title)
    if match:
        qnum = match.group(1)
        qtitle = match.group(2)
    else:
        qnum = ""
        qtitle = full_title

    col1, col2 = st.columns([4, 1])
    with col1:
        checked = st.checkbox(f"{qnum}. {qtitle}", value=done, key=key)
    with col2:
        st.markdown(
            f"<div style='text-align:right'><a href='{link}' target='_blank'>🔗 題目連結</a></div>",
            unsafe_allow_html=True
        )

    if checked != progress.get(key, False):
        save_progress(key, checked)
        st.rerun()

import streamlit as st
import pandas as pd
import os
import re
from google_sheet import get_note, save_note, get_progress, save_progress

# ===== OIDC 登入區塊 =====
if not st.user.is_logged_in:
    st.sidebar.title("🔐 使用者登入")
    st.sidebar.info("👉 請先使用 Google 登入", icon="💡")
    st.sidebar.button("使用 Google 登入", on_click=st.login)
    st.stop()

if st.sidebar.button("🚪 登出"):
    st.logout()

user = st.user
user_id = user.get("email") or user.get("sub") or "unknown_user"

# ===== 顯示登入者 =====
st.markdown(
    f"<div style='text-align:right; font-size:0.9em;'>👤 登入帳號：{user_id}</div>",
    unsafe_allow_html=True
)

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

# ===== 讀取進度 =====
progress = get_progress(user_id)

# ===== 顯示整體進度 =====
total_done = 0
total_questions = 0

for f in all_files:
    df_tmp = pd.read_csv(os.path.join(data_dir, f))
    for idx in df_tmp.index:
        qkey = f"{f}_{idx}"
        if progress.get(qkey, False):
            total_done += 1
    total_questions += len(df_tmp)

overall_percent = total_done / total_questions if total_questions > 0 else 0
st.progress(overall_percent)
st.markdown(f"**總進度：{total_done} / {total_questions} 題 ({overall_percent*100:.1f}%)**")

# ===== 顯示當前類別進度 =====
keys_for_this_category = [f"{category}_{idx}" for idx in df.index]
done_count = sum(progress.get(k, False) for k in keys_for_this_category)
total_count = len(df)
percent = done_count / total_count if total_count > 0 else 0

st.progress(percent)
st.markdown(f"**目前類別進度：{done_count} / {total_count} 題 ({percent*100:.1f}%)**")

# ===== 筆記區塊 =====
st.markdown("---")
st.subheader("📘 類別筆記編輯器")

note_text = get_note(user_id, selected_display)
edited_note = st.text_area("✍️ 編輯筆記", value=note_text, height=300, label_visibility="collapsed")

if st.button("💾 儲存筆記"):
    save_note(user_id, selected_display, edited_note)
    st.success("✅ 筆記已儲存至 Google Sheets！")
    st.rerun()

with st.expander("📄 預覽筆記（點擊展開）", expanded=True):
    st.markdown("---")
    st.markdown("#### 📌 Note")
    st.markdown(edited_note, unsafe_allow_html=True)

# ===== 題目 checkbox 勾選 =====
for idx, row in df.iterrows():
    qkey = f"{category}_{idx}"
    done = progress.get(qkey, False)

    full_title = row["文字"]
    link = row["超連結"]

    match = re.match(r"^([^\s]+)\s+(.*)", full_title)
    if match:
        qnum = match.group(1)
        qtitle = match.group(2)
    else:
        qnum = ""
        qtitle = full_title

    col1, col2 = st.columns([4, 1])
    with col1:
        checked = st.checkbox(f"{qnum}. {qtitle}", value=done, key=qkey)
    with col2:
        st.markdown(
            f"<div style='text-align:right'><a href='{link}' target='_blank'>🔗 題目連結</a></div>",
            unsafe_allow_html=True
        )

    if checked != progress.get(qkey, False):
        save_progress(user_id, qkey, checked)
        st.rerun()
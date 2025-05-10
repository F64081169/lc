import streamlit as st
import pandas as pd
import os
import json
import re
import subprocess  # 新增 subprocess 模組來執行 git 指令

# 中文字體設定
st.markdown("""
    <style>
    * {
        font-family: "Noto Sans TC", "Microsoft JhengHei", "Heiti TC", "PingFang TC", sans-serif;
    }
    </style>
""", unsafe_allow_html=True)

st.title("LeetCode 刷題QAQ")

# Git push 函式
def git_push(commit_msg="Auto-update"):
    try:
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", commit_msg], check=True)
        subprocess.run(["git", "push"], check=True)
    except subprocess.CalledProcessError as e:
        st.error(f"❌ Git 操作失敗：{e}")

# 設定資料與進度檔
data_dir = "data"
progress_file = "progress.json"

# 初始化 progress.json
progress = {}
if not os.path.exists(progress_file) or os.path.getsize(progress_file) == 0:
    with open(progress_file, "w", encoding="utf-8") as f:
        f.write("{}")
try:
    with open(progress_file, "r", encoding="utf-8") as f:
        progress = json.load(f)
except json.JSONDecodeError:
    st.warning("⚠️ progress.json 格式錯誤，已重置進度資料。")
    progress = {}

# 計算總進度（跨所有 CSV 類別）
total_done = 0
total_questions = 0
all_files = [f for f in os.listdir(data_dir) if f.endswith(".csv")]

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

# 顯示類別選單
display_names = [f.replace(".csv", "") for f in all_files]
selected_display = st.selectbox("選擇類別", display_names)
category = selected_display + ".csv"

# 載入選取的題目檔案
df = pd.read_csv(os.path.join(data_dir, category))

# 類別進度
keys_for_this_category = [f"{category}_{idx}" for idx in df.index]
done_count = sum([progress.get(k, False) for k in keys_for_this_category])
total_count = len(df)
percent = done_count / total_count if total_count > 0 else 0

st.progress(percent)
st.markdown(f"**目前類別進度：{done_count} / {total_count} 題 ({percent*100:.1f}%)**")

# 筆記處理
notes_dir = "notes"
os.makedirs(notes_dir, exist_ok=True)
note_path = os.path.join(notes_dir, selected_display + ".md")

if not os.path.exists(note_path):
    with open(note_path, "w", encoding="utf-8") as f:
        f.write(f"# {selected_display} 類別筆記\n\n<!-- 在此撰寫筆記內容 -->")

with open(note_path, "r", encoding="utf-8") as f:
    current_note = f.read()

st.markdown("---")
st.subheader("📘 類別筆記編輯器")
edited_note = st.text_area("✍️ 編輯筆記", value=current_note, height=300, label_visibility="collapsed")

if st.button("💾 儲存筆記"):
    with open(note_path, "w", encoding="utf-8") as f:
        f.write(edited_note)
    git_push(commit_msg=f"Update note: {selected_display}")
    st.success("✅ 筆記已儲存並推送至 GitHub！")
    st.rerun()

with st.expander("📄 預覽筆記（點擊展開）", expanded=True):
    st.markdown("---")
    st.markdown("#### 📌 預覽結果")
    st.markdown(edited_note, unsafe_allow_html=True)

# 題目與互動 checkbox
for idx, row in df.iterrows():
    key = f"{category}_{idx}"
    done = progress.get(key, False)

    full_title = row['文字']
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
            f"<div style='text-align:right'><a href='{row['超連結']}' target='_blank'>🔗 題目連結</a></div>",
            unsafe_allow_html=True
        )

    if checked != progress.get(key, False):
        progress[key] = checked
        with open(progress_file, "w", encoding="utf-8") as f:
            json.dump(progress, f, ensure_ascii=False, indent=2)
        git_push(commit_msg=f"Update progress: {category}")
        st.rerun()

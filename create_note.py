import os

data_dir = "data"
notes_dir = "notes"

# 確保 notes 資料夾存在
os.makedirs(notes_dir, exist_ok=True)

# 取得 data 底下所有 .csv 檔案
csv_files = [f for f in os.listdir(data_dir) if f.endswith(".csv")]

for csv_file in csv_files:
    # 去掉 .csv 副檔名，組出 .md 檔案名稱
    base_name = os.path.splitext(csv_file)[0]
    md_file = os.path.join(notes_dir, base_name + ".md")
    
    # 如果筆記檔不存在就建立空白檔案
    if not os.path.exists(md_file):
        with open(md_file, "w", encoding="utf-8") as f:
            f.write(f"# {base_name} 筆記\n\n<!-- 在此加入這個類別的筆記 -->")
        print(f"✅ Created: {md_file}")
    else:
        print(f"⚠️ Already exists: {md_file}")

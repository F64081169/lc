from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import csv
from bs4 import BeautifulSoup

# 初始化 Chrome driver（無頭）
options = webdriver.ChromeOptions()
options.add_argument('--headless')
driver = webdriver.Chrome(options=options)

# 目標網址
url = 'https://leetcode.cn/discuss/post/3144832/fen-xiang-gun-ti-dan-zi-fu-chuan-kmpzhan-ugt4/'
driver.get(url)
time.sleep(3)

# 獲取動態渲染後的 HTML
html = driver.page_source
soup = BeautifulSoup(html, 'html.parser')

driver.quit()

# 找所有 <ul> 標籤
uls = soup.find_all('ul')

# 寫入 CSV：只儲存含 `/problems/` 的連結
with open('string.csv', mode='w', newline='', encoding='utf-8-sig') as file:
    writer = csv.writer(file)
    writer.writerow(['文字', '超連結'])

    for ul in uls:
        lis = ul.find_all('li')
        for li in lis:
            a = li.find('a')
            if a and '/problems/' in a.get('href', ''):
                writer.writerow([a.get_text(strip=True), a['href']])

print("✅ 已儲存符合條件的連結到 .csv")

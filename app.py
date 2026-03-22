import streamlit as st
from google_sheet import get_spreadsheet

st.title("Google Sheet 測試")

if not st.user.is_logged_in:
    st.write("請先登入")
    st.button("使用 Google 登入", on_click=st.login)
    st.stop()

st.success("OIDC 登入成功")

user_id = st.user.get("email") or st.user.get("sub")
st.write("user_id =", user_id)

try:
    st.write(list(st.secrets.keys()))
    st.write(st.secrets["gcp_service_account"]["client_email"])
    sh = get_spreadsheet()
    st.success("Google Sheet 連線成功")
    st.write("Spreadsheet title:", sh.title)
    
    worksheets = sh.worksheets()
    st.write("Worksheets:")
    
    for ws in worksheets:
        st.write("-", ws.title)

except Exception as e:
    st.error("Google Sheet 連線失敗")
    st.error(repr(e))
    st.exception(e)
    st.exception(e)

if st.button("登出"):
    st.logout()
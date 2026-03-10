@echo off
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
cd /d "C:\Users\owner\Desktop\一時\Google_Antigravity_Proj\art_critic_app"
start "" streamlit run app.py

import streamlit as st
import feedparser
from urllib.parse import quote

# ページ設定
st.set_page_config(page_title="AIニュース収集ダッシュボード", layout="wide")

# CSSによるスタイル設定 (カード型デザイン)
st.markdown("""
<style>
.news-card {
    background-color: #f9f9f9;
    border-radius: 10px;
    padding: 20px;
    margin-bottom: 20px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    border-left: 5px solid #1f77b4;
    transition: transform 0.2s;
}
.news-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
}
.news-title {
    font-size: 1.25rem;
    font-weight: bold;
    color: #333;
    margin-bottom: 10px;
}
.news-date {
    font-size: 0.9rem;
    color: #666;
    margin-bottom: 10px;
}
.news-summary {
    font-size: 1rem;
    color: #444;
    margin-bottom: 15px;
    line-height: 1.5;
}
.news-link {
    display: inline-block;
    padding: 8px 16px;
    background-color: #1f77b4;
    color: white !important;
    text-decoration: none;
    border-radius: 5px;
    font-weight: bold;
}
.news-link:hover {
    background-color: #155a8a;
}
</style>
""", unsafe_allow_html=True)

# ヘッダー
st.title("📰 AIニュース収集ダッシュボード")
st.write("Google NewsのRSSを利用して、最新のニュースを自動収集・表示します。")

# サイドバー検索設定
st.sidebar.header("検索設定")
search_query = st.sidebar.text_input("検索キーワード", value="Artificial Intelligence")

# RSS URLの生成
def generate_rss_url(query):
    # Google News RSS (英語圏のニュースを中心に取得する例。日本語の場合はhl=ja&gl=JP&ceid=JP:ja)
    # 要件に合わせて柔軟に変更可能ですが、ここでは標準的なグローバルニュースを取得します
    encoded_query = quote(query)
    # 日本語の検索も考慮し、hl=ja&gl=JPを設定しています
    return f"https://news.google.com/rss/search?q={encoded_query}&hl=ja&gl=JP&ceid=JP:ja"

# ニュース取得と表示
if search_query:
    rss_url = generate_rss_url(search_query)
    
    with st.spinner(f"「{search_query}」のニュースを取得中..."):
        feed = feedparser.parse(rss_url)
        
    if feed.entries:
        st.success(f"{len(feed.entries)}件のニュースを取得しました！")
        
        # ニュースをカードで表示
        for entry in feed.entries:
            # データの取得
            title = entry.get('title', 'No Title')
            published = entry.get('published', 'No Date')
            # 概要はHTMLが含まれることが多いため、簡易的に文字列として扱います（必要に応じてBeautifulSoup等で除去を推奨）
            # 今回は要件に従い表示
            summary = entry.get('summary', 'No Summary provided.<br>')
            link = entry.get('link', '#')
            
            # HTMLを用いてカードを描画
            card_html = f"""
            <div class="news-card">
                <div class="news-title">{title}</div>
                <div class="news-date">📅 発行日: {published}</div>
                <div class="news-summary">{summary}</div>
                <a href="{link}" target="_blank" class="news-link">元の記事を読む ↗</a>
            </div>
            """
            st.markdown(card_html, unsafe_allow_html=True)
            
    else:
        st.warning("指定されたキーワードでのニュースが見つかりませんでした。別のキーワードをお試しください。")
else:
    st.info("左側のサイドバーで検索キーワードを入力してください。")

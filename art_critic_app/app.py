import streamlit as st
import google.genai as genai
from PIL import Image
import pandas as pd
import plotly.express as px
import re

def get_critic_response(api_key, image):
    # Gemini APIの設定
    try:
        client = genai.Client(api_key=api_key)
    except Exception as e:
        return f"クライアントの初期化に失敗しました: {e}"

    # プロの画家としてのプロンプト
    prompt = """
あなたは世界的に著名なプロの画家であり、厳威ある美術評論家です。
ユーザーから提供された絵画（イラストや画像）を深く観察し、以下の形式に従って日本語で評価と講評を行ってください。

【評価の基準（10段階評価）】
※AI生成画像も多く含まれるため、技術的な完成度だけでなく、真のオリジナリティや深み、細部の破綻のなさなどを厳しく評価してください。
1. 構図と全体的なバランス（視線誘導や空間の取り方）
2. 色彩感覚とライティング（光と影の説得力、色彩の調和）
3. 表現力・オリジナリティ（ありきたりではない独自の視点や発想があるか）
4. 筆致・テクスチャ・細部の描写（デジタル/アナログ問わず、細部の描き込みに不自然さや破綻がないか）
5. 全体的な印象と感情への訴えかけ（作品から明確なメッセージや感情が伝わってくるか）

【出力フォーマット】
以下のフォーマットで出力してください。必ず指定された項目名を含めてください。Markdownを利用して読みやすく記述してください。箇条書きなども使ってわかりやすくしてください。

### タイトル提案 (English)
（この絵画にふさわしい、魅力的で芸術的な英語のタイトルを1つ提案し、その理由を日本語で簡潔に添えてください）

### レーダーチャート用スコア
※必ず以下のフォーマットで、1から10までの整数で出力してください。
- 構図: [スコア]
- 色彩: [スコア]
- 独創性: [スコア]
- 描写: [スコア]
- 印象: [スコア]

### 総合評価: ★[★の数] / ★10
（1から10までの星（★）で評価してください。半分（☆）などは使わず整数としてください。例えば★7の場合は「★7 / ★10」としてください。安易に満点をつけず、プロの厳しい目線でメリハリをつけて採点してください）

### 批評と賛辞
（プロの画家からの温かい賛辞と、プロならではの視点での詳しい批評を述べてください）

### 今後のアドバイス
（さらに良くなるための具体的なアドバイスを記載してください）
"""
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[prompt, image]
        )
        return response.text
    except Exception as e:
        return f"エラーが発生しました: {e}"

def extract_scores(text):
    scores = {}
    categories = ["構図", "色彩", "独創性", "描写", "印象"]
    
    for category in categories:
        match = re.search(rf"- {category}:\s*(\d+)", text)
        if match:
            scores[category] = int(match.group(1))
        else:
            scores[category] = 0 # Default if parsing fails
            
    return scores

def create_radar_chart(scores):
    df = pd.DataFrame(dict(
        r=list(scores.values()),
        theta=list(scores.keys())
    ))
    
    # グラフの始点と終点を繋ぐためにデータを追加
    if not df.empty:
        df = pd.concat([df, df.iloc[[0]]], ignore_index=True)
        
    fig = px.line_polar(df, r='r', theta='theta', line_close=True, range_r=[0, 10])
    fig.update_traces(fill='toself', line_color='#ff4b4b')
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 10])
        ),
        showlegend=False,
        margin=dict(l=40, r=40, t=20, b=20)
    )
    return fig

def main():
    st.set_page_config(page_title="AIアート評論家", page_icon="🎨", layout="centered")
    
    # セッションステートの初期化（履歴保存用）
    if 'history' not in st.session_state:
        st.session_state.history = []
    
    st.title("👨‍🎨 AIアート評論家")
    st.write("あなたの描いた絵や作成した画像（スクリーンショットなどでも可）をアップロードすると、AIがプロの画家として講評と星評価（最大評価:10）をしてくれます！")
    
    # サイドバーでAPIキーを取得
    with st.sidebar:
        st.header("設定")
        api_key = st.text_input("Google Gemini API キーを入力", type="password")
        st.markdown("[APIキーの取得手順はこちら(Google AI Studio)](https://aistudio.google.com/app/apikey)")
        st.info("※ APIキーは保存されず、このセッションの実行のみに使用されます。")
    
    # メインエリア：画像アップロード
    uploaded_file = st.file_uploader("評価してもらいたい画像をアップロードしてください", type=["png", "jpg", "jpeg"])
    
    if uploaded_file is not None:
        try:
            image = Image.open(uploaded_file)
            st.image(image, caption="アップロードされた画像", use_container_width=True)
            
            # 評価ボタン
            if st.button("この画像を評価してもらう", type="primary"):
                if not api_key:
                    st.error("左のサイドバーからGemini APIキーを入力してください。")
                else:
                    with st.spinner("プロの画家（AI）が絵を鑑賞しています... 少々お待ちください。"):
                        result = get_critic_response(api_key, image)
                        st.subheader("👨‍🎨 評論結果")
                        
                        # エラーでなければレーダーチャートを描画
                        if not result.startswith("エラーが発生しました") and not result.startswith("クライアントの初期化に失敗しました"):
                            scores = extract_scores(result)
                            # 全てのスコアが0でなければチャートを表示
                            if any(score > 0 for score in scores.values()):
                                st.write("### 📊 評価パラメータ")
                                st.write("グラフの右上にカーソルを合わせると表示される📷(または💾)アイコンから画像としてダウンロード・コピーができます。")
                                fig = create_radar_chart(scores)
                                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': True, 'toImageButtonOptions': {'format': 'png', 'filename': 'radar_chart'}})
                                
                        st.markdown(result)
                        
                        st.divider()
                        st.subheader("📋 テキストをコピーする")
                        st.write("右上のコピーアイコン(📋)をクリックして全体をコピーできます。")
                        
                        # Markdownの強調記号(**)を削除してプレーンテキスト化
                        clean_result = result.replace("**", "")
                        st.code(clean_result, language="text")
                        
                        # エラーの場合は履歴に追加しない
                        if not result.startswith("エラーが発生しました") and not result.startswith("クライアントの初期化に失敗しました"):
                            # スコアを履歴にも保存（チャート再描画用）
                            scores = extract_scores(result)
                            
                            # 最新のものが先頭にくるように挿入
                            st.session_state.history.insert(0, {
                                "image": image,
                                "result": clean_result, # プレーンテキスト版を履歴に保存してコピーしやすくする
                                "raw_result": result,   # 表示用にはマークダウン版を残す
                                "scores": scores
                            })
                            
                            # 履歴を最大5件に保つ
                            if len(st.session_state.history) > 5:
                                st.session_state.history = st.session_state.history[:5]
                            
        except Exception as e:
            st.error(f"画像の読み込みに失敗しました: {e}")

    # 履歴セクションの表示
    if getattr(st.session_state, 'history', []):
        st.divider()
        st.header("🕰️ 過去の評価履歴（最新5件）")
        
        for i, item in enumerate(st.session_state.history):
            with st.expander(f"履歴 {i+1}件目", expanded=(i==0)):
                cols = st.columns([1, 2])
                with cols[0]:
                    st.image(item["image"], use_container_width=True)
                with cols[1]:
                    if "scores" in item and any(score > 0 for score in item["scores"].values()):
                        fig = create_radar_chart(item["scores"])
                        st.plotly_chart(fig, use_container_width=True, key=f"history_chart_{i}", config={'displayModeBar': True, 'toImageButtonOptions': {'format': 'png', 'filename': 'radar_chart'}})
                        
                    raw_text = item.get("raw_result", item["result"]) # 後方互換性のため
                    st.markdown(raw_text[:200] + "..." if len(raw_text) > 200 else raw_text)
                    st.write("右上のコピーアイコン(📋)をクリックして全体をコピーできます。")
                    st.code(item["result"], language="text")

if __name__ == "__main__":
    main()

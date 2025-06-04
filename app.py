import streamlit as st
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def get_qiita_og_image_url(qiita_url):
    """
    QiitaのURLからog:imageのURLを抽出します。
    Args:
        qiita_url (str): Qiita記事のURL。
    Returns:
        str: og:imageのURL。見つからない場合はNone。
    """
    if not qiita_url.startswith("https://qiita.com/"):
        return None # QiitaのURLではない場合

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(qiita_url, headers=headers, timeout=10)
        response.raise_for_status()  # HTTPエラーがあれば例外を発生させる
        soup = BeautifulSoup(response.text, 'html.parser')

        # OGP画像 (og:image) を探す
        og_image_tag = soup.find('meta', property='og:image')
        if og_image_tag and 'content' in og_image_tag.attrs:
            image_url = og_image_tag['content']
            # 相対URLの場合に対応（Qiitaの場合は通常絶対URLですが念のため）
            return urljoin(qiita_url, image_url)
        
        # もしog:imageが見つからない場合、代替でTwitter Cardの画像を探す（ある場合）
        twitter_image_tag = soup.find('meta', property='twitter:image')
        if twitter_image_tag and 'content' in twitter_image_tag.attrs:
            image_url = twitter_image_tag['content']
            return urljoin(qiita_url, image_url)

        return None
    except requests.exceptions.RequestException as e:
        st.error(f"URL `{qiita_url}` の取得中にエラーが発生しました: {e}")
        return None
    except Exception as e:
        st.error(f"URL `{qiita_url}` のデータ解析中にエラーが発生しました: {e}")
        return None

st.set_page_config(page_title="複数Qiita記事サムネイル抽出アプリ", layout="wide")
st.title('🖼️ 複数Qiita記事サムネイル抽出アプリ')

st.write("""
このアプリは、入力された複数のQiita記事のURLから、それぞれの記事のサムネイル画像（主にOGP画像）を抽出して表示します。
URLは改行区切りで入力してください。
""")

# テキストエリアで複数のURLを受け付ける
qiita_urls_input = st.text_area(
    'Qiita記事のURLを1行に1つずつ入力してください', 
    'https://qiita.com/yamamoto_kenta/items/8a34d7d0a2f4a5a5f6e8\nhttps://qiita.com/kazukazu_pon/items/bb19782414704b2a30d5\nhttps://qiita.com/taniokahikaru/items/7fb81837077a280c7d5c',
    height=200
)

if st.button('サムネイルを抽出'):
    if qiita_urls_input:
        urls = [url.strip() for url in qiita_urls_input.split('\n') if url.strip()]
        
        if not urls:
            st.warning('URLが入力されていません。')
        else:
            st.subheader('抽出結果')
            extracted_count = 0
            for i, url in enumerate(urls):
                st.markdown(f"---")
                st.markdown(f"### {i+1}. URL: {url}")
                
                if not url.startswith("https://qiita.com/"):
                    st.error(f"**無効なURL:** `{url}` はQiitaのURLではありません。`https://qiita.com/` から始まるURLを入力してください。")
                    continue
                
                with st.spinner(f'URL `{url}` のサムネイルを抽出中...'):
                    extracted_image_url = get_qiita_og_image_url(url)

                    if extracted_image_url:
                        try:
                            # ここで画像の幅を調整 (例: 400ピクセル)
                            st.image(extracted_image_url, caption=f'抽出されたサムネイル from {url}', width=600) # widthを200から600に変更
                            st.markdown(f"**画像URL:** `{extracted_image_url}`")
                            extracted_count += 1
                        except Exception as e:
                            st.error(f"**画像の表示に失敗しました:** `{url}` の画像URLが不正な形式である可能性があります。")
                            st.write(f"抽出された画像URL: `{extracted_image_url}`")
                    else:
                        st.warning(f"**サムネイルを抽出できませんでした:** `{url}` にOGP画像が見つからないか、URLが不正な可能性があります。")
            
            st.markdown("---")
            st.success(f"**抽出完了:** {extracted_count}件のサムネイルを抽出しました。")
    else:
        st.warning('Qiita記事のURLを入力してください。')

st.markdown("""
<style>
.stTextArea > div > div > textarea {
    font-size: 1.2em;
    height: 100%; /* テキストエリアの高さを調整 */
}
.stTextInput > div > div > input {
    font-size: 1.2em;
}
.stButton > button {
    font-size: 1.2em;
    padding: 10px 20px;
}
/* st.imageの幅を調整するため、カスタムCSSで最大幅を設定することも可能 */
.stImage > img {
    max-width: 100%; /* 親要素の幅に合わせて最大化 */
    height: auto; /* 高さは自動調整 */
}
</style>
""", unsafe_allow_html=True)

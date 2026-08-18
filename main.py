import os
import random
import feedparser
import requests
import openai
from googleapiclient.discovery import build

# API 설정
openai.api_key = os.environ.get("OPENAI_API_KEY")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
UNSPLASH_ACCESS_KEY = os.environ.get("UNSPLASH_ACCESS_KEY")

def get_latest_it_trend():
    """IT 뉴스 RSS에서 최신 트렌드 키워드 가져오기"""
    # 구글 뉴스 IT 카테고리 RSS
    rss_url = "https://news.google.com/rss/headlines/section/topic/TECHNOLOGY?hl=ko&gl=KR&ceid=KR:ko"
    feed = feedparser.parse(rss_url)
    if feed.entries:
        # 상위 3개 뉴스 제목을 합쳐서 AI에게 트렌드 정보로 제공
        titles = [entry.title for entry in feed.entries[:3]]
        return "최신 트렌드 뉴스: " + ", ".join(titles)
    return "최신 IT 트렌드에 대해 작성해줘."

def get_unsplash_image_by_keyword(keyword):
    """AI가 생성한 글에서 핵심 키워드를 뽑아 이미지 검색"""
    if not UNSPLASH_ACCESS_KEY: return ""
    # AI가 제안한 키워드로 이미지 검색
    url = f"https://api.unsplash.com/photos/random?query={keyword}&client_id={UNSPLASH_ACCESS_KEY}"
    try:
        response = requests.get(url).json()
        return response.get("urls", {}).get("regular", "")
    except: return ""

def generate_ai_post():
    trend_info = get_latest_it_trend()
    
    prompt = f"""
    당신은 전문 IT 블로거입니다. 아래 정보를 바탕으로 블로그 글을 작성하세요.
    정보: {trend_info}
    
    요구사항:
    1. HTML 형식으로 작성 (제목은 h1, 본문은 h2, p, ul 등 사용)
    2. 본문 내용에 맞는 '이미지 검색용 키워드'를 맨 마지막에 [키워드: 단어] 형식으로 하나만 적어줘.
    3. 글은 전문적이고 읽기 쉽게 작성해줘.
    """
    
    client = openai.OpenAI()
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )
    
    full_content = response.choices[0].message.content
    
    # [키워드: ...] 추출
    import re
    keyword_match = re.search(r"\[키워드:\s*(.*?)\]", full_content)
    search_keyword = keyword_match.group(1) if keyword_match else "technology"
    clean_content = re.sub(r"\[키워드:.*?\]", "", full_content)
    
    # 이미지 삽입
    img_url = get_unsplash_image_by_keyword(search_keyword)
    body = f'<img src="{img_url}"/><br>' + clean_content if img_url else clean_content
    
    return "오늘의 IT 트렌드 분석", body

def post_to_blogger(title, content):
    service = build("blogger", "v3", developerKey=os.environ.get("BLOGGER_API_KEY"))
    body = {"title": title, "content": content, "status": "DRAFT"}
    try:
        service.posts().insert(blogId=os.environ.get("BLOG_ID"), body=body, isDraft=True).execute()
        requests.post(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage", 
                      json={"chat_id": TELEGRAM_CHAT_ID, "text": "✅ 자동 포스팅 성공 (트렌드 반영 완료)"})
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    title, content = generate_ai_post()
    post_to_blogger(title, content)
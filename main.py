import os
import random
import feedparser
import requests
import openai
import time
import re
from googleapiclient.discovery import build

# 설정값
HISTORY_FILE = "history.txt"
openai.api_key = os.environ.get("OPENAI_API_KEY")

def load_history():
    if not os.path.exists(HISTORY_FILE): return set()
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        return set(line.strip() for line in f)

def save_history(title):
    with open(HISTORY_FILE, "a", encoding="utf-8") as f:
        f.write(title + "\n")

def get_latest_it_trend(history):
    rss_url = "https://news.google.com/rss/headlines/section/topic/TECHNOLOGY?hl=ko&gl=KR&ceid=KR:ko"
    feed = feedparser.parse(rss_url)
    for entry in feed.entries:
        if entry.title not in history:
            return entry.title
    return "최신 AI 기술 동향"

def generate_ai_post_with_retry(trend_title, retries=3):
    for i in range(retries):
        try:
            prompt = f"""
            주제: {trend_title}에 대한 전문적인 IT 블로그 글을 작성해줘.
            요구사항:
            1. HTML 형식 (h1, h2, p, ul)
            2. 본문 끝에 [태그: 키워드1, 키워드2, 키워드3] 형식으로 태그를 달아줘.
            3. 이미지 검색용 키워드는 마지막에 [이미지: 키워드] 형식으로 적어줘.
            """
            client = openai.OpenAI()
            response = client.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": prompt}])
            return response.choices[0].message.content
        except Exception as e:
            if i == retries - 1: raise e
            time.sleep(2)

def post_to_blogger(title, content):
    # 태그와 이미지 키워드 파싱
    tags = re.findall(r"\[태그:\s*(.*?)\]", content)
    img_match = re.search(r"\[이미지:\s*(.*?)\]", content)
    
    clean_content = re.sub(r"\[태그:.*?\]", "", content)
    clean_content = re.sub(r"\[이미지:.*?\]", "", clean_content)
    
    # 이미지 삽입
    img_url = f"https://source.unsplash.com/800x400/?{img_match.group(1)}" if img_match else ""
    final_content = f'<img src="{img_url}"/><br>' + clean_content if img_url else clean_content

    service = build("blogger", "v3", developerKey=os.environ.get("BLOGGER_API_KEY"))
    body = {"title": title, "content": final_content, "status": "DRAFT", "labels": tags}
    service.posts().insert(blogId=os.environ.get("BLOG_ID"), body=body, isDraft=True).execute()

if __name__ == "__main__":
    history = load_history()
    trend = get_latest_it_trend(history)
    content = generate_ai_post_with_retry(trend)
    post_to_blogger(trend, content)
    save_history(trend)
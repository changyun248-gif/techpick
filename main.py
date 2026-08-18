import os
import random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from googleapiclient.discovery import build
import openai
import requests

# 1. 크롬 옵션 설정 (헤드리스 모드)
options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")
driver = webdriver.Chrome(options=options)

# 2. API 키 설정 (깃허브 Secrets에서 불러옴)
openai.api_key = os.environ.get("OPENAI_API_KEY")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
UNSPLASH_ACCESS_KEY = os.environ.get("UNSPLASH_ACCESS_KEY") # 선택사항 (없어도 실행됨)

def send_telegram_message(message):
    """텔레그램으로 실행 결과 알림 전송"""
    if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message
        }
        try:
            requests.post(url, json=payload)
        except Exception as e:
            print(f"텔레그램 알림 전송 실패: {e}")

def get_unsplash_image(query):
    """Unsplash API를 이용해 주제에 맞는 무료 이미지 URL 가져오기"""
    if not UNSPLASH_ACCESS_KEY:
        return ""
    url = f"https://api.unsplash.com/photos/random?query={query}&client_id={UNSPLASH_ACCESS_KEY}"
    try:
        response = requests.get(url).json()
        return response.get("urls", {}).get("regular", "")
    except Exception:
        return ""

def generate_ai_post():
    """ChatGPT를 이용해 SEO 최적화된 구체적 IT 글 생성"""
    print("AI가 고퀄리티 블로그 글을 작성 중입니다...")
    
    # 1. 주제 다양화 후보군
    topics = [
        "파이썬(Python) 업무 자동화를 효율적으로 만드는 3가지 실전 팁",
        "개발자가 꼭 알아야 할 Git & GitHub 필수 명령어와 트러블슈팅",
        "최신 인공지능(AI) 트렌드와 개발 생산성을 극대화하는 활용법",
        "초보자를 위한 웹 크롤링(Selenium) 안정성 높이기 가이드"
    ]
    selected_topic = random.choice(topics)
    
    prompt = f"""
    주제: {selected_topic}
    위 주제에 대해 독자들이 이해하기 쉽고 유익하며, 검색 유입(SEO)에 최적화된 블로그 글을 작성해줘.
    조건:
    1. 첫 번째 줄은 블로그 제목으로 작성하고 앞에 '#'이나 특수문자를 붙이지 마.
    2. 본문은 HTML 태그(<h2>, <p>, <ul>, <li>, <code> 등)를 사용하여 가독성 있게 작성해줘.
    3. 실무자들에게 도움이 되는 알찬 팁을 포함해줘.
    """
    
    client = openai.OpenAI()
    response = client.chat.completions.create(
        model="gpt-4o",  # 또는 gpt-3.5-turbo
        messages=[
            {"role": "system", "content": "너는 전문 IT 테크 블로거야."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
    )
    
    content = response.choices.message.content
    lines = content.strip().split('\n')
    title = lines[0].replace("제목:", "").strip() if lines else selected_topic
    body = "\n".join(lines[1:]) if len(lines) > 1 else content
    
    # 이미지 자동 첨부 (Unsplash 연동)
    img_url = get_unsplash_image("technology coding")
    if img_url:
        image_html = f'<p style="text-align: center;"><img src="{img_url}" style="max-width: 100%; height: auto;"/></p><br>'
        body = image_html + body
        
    return title, body

def post_to_blogger(title, content):
    """Blogger API를 이용해 '임시저장(Draft)' 상태로 업로드"""
    api_key = os.environ.get("BLOGGER_API_KEY")
    blog_id = os.environ.get("BLOG_ID")

    service = build("blogger", "v3", developerKey=api_key)
    body = {
        "title": title,
        "content": content,
        "status": "DRAFT"  # 안전하게 임시저장 상태로 발행
    }

    try:
        posts = service.posts()
        request = posts.insert(blogId=blog_id, body=body, isDraft=True)
        response = request.execute()
        print(f"포스팅 임시저장 성공!")
        
        # 텔레그램 성공 알림
        send_telegram_message(f"✅ [블로그 자동화 성공]\n제목: {title}\n상태: 임시저장(Draft) 완료")
        
    except Exception as e:
        error_msg = f"포스팅 실패 에러: {e}"
        print(error_msg)
        # 텔레그램 실패 알림
        send_telegram_message(f"❌ [블로그 자동화 실패]\n에러: {e}")

if __name__ == "__main__":
    driver.quit()
    
    try:
        title, content = generate_ai_post()
        post_to_blogger(title, content)
    except Exception as e:
        send_telegram_message(f"❌ [스크립트 실행 에러]\n에러: {e}")
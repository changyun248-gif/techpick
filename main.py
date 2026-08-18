from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os
from googleapiclient.discovery import build

options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")

# 1. 기존에 쓰시던 드라이버 생성 코드 (여기는 그대로 두기)
driver = webdriver.Chrome(options=options)

# --- (중간 생략: 셀레니움으로 블로그에 올릴 제목과 내용을 크롤링하는 코드) ---
# 예시:
# title = "가져온 제목"
# content = "가져온 본문 내용"


# 2. 방금 안내해 드린 블로그 포스팅 함수 추가
def post_to_blogger(title, content):
  api_key = os.environ.get("BLOGGER_API_KEY")
  blog_id = os.environ.get("BLOG_ID")

  service = build("blogger", "v3", developerKey=api_key)
  body = {"title": title, "content": content}

  try:
    posts = service.posts()
    request = posts.insert(blogId=blog_id, body=body)
    response = request.execute()
    print(f"포스팅 성공! URL: {response.get('url')}")
  except Exception as e:
    print(f"포스팅 실패 에러: {e}")


# 3. 크롤링이 끝난 뒤 함수 실행하기
# post_to_blogger(title, content)
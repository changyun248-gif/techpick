import os
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ['https://www.googleapis.com/auth/blogger']

def main():
    client_secrets_file = 'credentials.json'

    if not os.path.exists(client_secrets_file):
        print(f"에러: '{client_secrets_file}' 파일을 찾을 수 없습니다.")
        return

    flow = InstalledAppFlow.from_client_secrets_file(client_secrets_file, SCOPES)
    creds = flow.run_local_server(port=0)

    print("\n" + "="*50)
    print("🎉 인증 성공! 아래의 세 가지 값을 모두 복사하세요.")
    print("="*50)
    print(f"CLIENT_ID: {creds.client_id}")
    print(f"CLIENT_SECRET: {creds.client_secret}")
    print(f"REFRESH_TOKEN: {creds.refresh_token}")
    print("="*50)

if __name__ == '__main__':
    main()
# 배포 가이드

## 🚀 Streamlit Community Cloud 배포

### 1. 준비사항

#### GitHub 레포지토리 생성
```bash
cd c:\Users\y2k_w\projects\mflow-license-manager
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/your-username/mflow-license-manager.git
git push -u origin main
```

⚠️ **중요**: `.gitignore`가 제대로 설정되었는지 확인!
- `secrets.toml` ❌ (커밋 금지)
- `mflow_admin.json` ❌ (커밋 금지)
- `.env` ❌ (커밋 금지)

### 2. Streamlit Community Cloud 설정

#### 2.1 회원가입 및 앱 생성
1. https://streamlit.io/cloud 접속
2. GitHub 계정으로 로그인
3. "New app" 클릭
4. 레포지토리 선택: `your-username/mflow-license-manager`
5. Main file path: `streamlit_app.py`
6. "Deploy!" 클릭

#### 2.2 Secrets 설정
앱 대시보드에서 "Settings" → "Secrets" 클릭 후 다음 내용 입력:

**중요**: Firebase 인증 정보를 secrets에 직접 입력합니다. (파일 업로드 불가)

1. **로컬의 `mflow_admin.json` 파일 열기**
2. **내용 전체 복사**
3. **Streamlit Cloud Secrets에 다음 형식으로 붙여넣기:**

```toml
# Firebase 서비스 계정 정보 (mflow_admin.json 내용)
[firebase]
type = "service_account"
project_id = "your-project-id"
private_key_id = "your-private-key-id"
private_key = "-----BEGIN PRIVATE KEY-----\nYour-Private-Key-Here\n-----END PRIVATE KEY-----\n"
client_email = "firebase-adminsdk-xxxxx@your-project.iam.gserviceaccount.com"
client_id = "123456789"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs/firebase-adminsdk-xxxxx%40your-project.iam.gserviceaccount.com"

# SMTP 이메일 설정
SMTP_EMAIL = "your-email@gmail.com"
SMTP_PASSWORD = "your-app-password"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465

# 관리자 계정 설정
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD_HASH = "your-password-hash"
```

⚠️ **주의사항**:
- `private_key`는 반드시 `\n`으로 줄바꿈을 표시해야 합니다
- JSON에서 복사할 때 `"` 따옴표는 제거하고 값만 입력
- 모든 필드가 정확히 입력되었는지 확인

**작동 방식**:
- 코드가 자동으로 `st.secrets["firebase"]`를 감지
- 있으면 secrets에서 로드 (Streamlit Cloud)
- 없으면 `mflow_admin.json` 파일에서 로드 (로컬)

### 3. 로컬 개발 환경

#### 3.1 Secrets 파일 생성
```bash
# .streamlit/secrets.toml 파일 생성
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```

#### 3.2 실제 값 입력
`.streamlit/secrets.toml` 파일을 열고 실제 값 입력:
- SMTP 이메일 정보
- 관리자 비밀번호 해시
- Firebase 경로

#### 3.3 로컬 실행
```powershell
.\venv\Scripts\python.exe -m streamlit run streamlit_app.py
```

## 🔐 보안 체크리스트

배포 전 확인사항:

- [ ] `.gitignore`에 `secrets.toml` 추가됨
- [ ] `.gitignore`에 `mflow_admin.json` 추가됨
- [ ] `.gitignore`에 `.env` 추가됨
- [ ] GitHub에 secrets 파일이 커밋되지 않았는지 확인
- [ ] Streamlit Cloud의 Secrets에 모든 값 입력 완료
- [ ] 관리자 비밀번호를 기본값에서 변경
- [ ] Firebase 인증 파일이 안전하게 관리되는지 확인

## 🌐 대체 배포 옵션

### 옵션 1: ngrok (로컬 서버 외부 공개)
```powershell
# ngrok 설치
choco install ngrok

# Streamlit 실행
.\venv\Scripts\python.exe -m streamlit run streamlit_app.py

# 다른 터미널에서 ngrok 실행
ngrok http 8501
```

장점:
- ✅ 빠른 설정 (5분)
- ✅ Firebase 파일 문제 없음
- ✅ 무료

단점:
- ❌ URL이 매번 변경됨 (유료 플랜에서 고정 가능)
- ❌ PC가 켜져 있어야 함

### 옵션 2: Cloudflare Tunnel
```powershell
# Cloudflare Tunnel 설치
cloudflared tunnel create mflow-license

# 터널 실행
cloudflared tunnel --url http://localhost:8501
```

장점:
- ✅ 무료
- ✅ 고정 URL 가능
- ✅ HTTPS 자동 적용

단점:
- ❌ PC가 켜져 있어야 함

### 옵션 3: Heroku
```bash
# Procfile 생성
echo "web: streamlit run streamlit_app.py --server.port=$PORT" > Procfile

# requirements.txt 생성
pip freeze > requirements.txt

# Heroku 배포
heroku create mflow-license-manager
git push heroku main
```

장점:
- ✅ 24/7 실행
- ✅ 무료 티어 제공

단점:
- ❌ 무료 티어는 30분 미사용 시 슬립

### 옵션 4: AWS EC2 / Azure VM
- 완전한 제어
- 24/7 실행
- 비용 발생

## 📱 도메인 연결 (선택사항)

### Streamlit Cloud에 커스텀 도메인 연결
1. Streamlit Cloud 대시보드 → Settings → Custom domain
2. 도메인 제공업체에서 CNAME 레코드 추가:
   ```
   CNAME: app.yourdomain.com → your-app.streamlit.app
   ```

### ngrok에 커스텀 도메인 연결 (유료)
```powershell
ngrok http 8501 --domain=your-custom-domain.com
```

## 🔄 자동 업데이트

### Streamlit Cloud
- GitHub에 push하면 자동으로 재배포됨
- 수동 재시작: 앱 대시보드 → "Reboot app"

### 로컬 서버
```powershell
# Git pull 후 재시작
git pull origin main
# Ctrl+C로 종료 후 재실행
.\venv\Scripts\python.exe -m streamlit run streamlit_app.py
```

## 🆘 문제 해결

### Firebase 연결 실패
- Secrets에 Firebase 설정이 올바른지 확인
- `mflow_admin.json` 파일 경로 확인
- Firebase 프로젝트 권한 확인

### SMTP 이메일 발송 실패
- Gmail 2단계 인증 활성화 확인
- 앱 비밀번호 생성 및 사용
- SMTP 포트 확인 (465 또는 587)

### 로그인 실패
- `ADMIN_PASSWORD_HASH`가 올바른지 확인
- `setup_admin.py`로 새 해시 생성
- Secrets 재시작 (앱 reboot)

## 📞 지원

문제가 계속되면:
1. Streamlit Cloud 로그 확인
2. GitHub Issues 생성
3. Streamlit Community Forum 질문

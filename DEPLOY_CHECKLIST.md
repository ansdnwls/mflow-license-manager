# 🚀 배포 체크리스트

Streamlit Cloud 배포 전 확인사항입니다.

## ✅ 필수 확인사항

### 1. Git 저장소 준비

- [ ] Git 저장소 초기화 완료
- [ ] `.gitignore` 확인 (secrets.toml, mflow_admin.json 제외)
- [ ] 모든 파일 커밋 완료
- [ ] GitHub 레포지토리 생성 및 연결

**명령어:**
```powershell
git init
git add .
git commit -m "Initial commit: MFLOW License Manager"
git remote add origin https://github.com/your-username/mflow-license-manager.git
git branch -M main
git push -u origin main
```

### 2. 보안 파일 확인

- [ ] `.streamlit/secrets.toml`이 Git에 커밋되지 않았는지 확인
- [ ] `mflow_admin.json`이 Git에 커밋되지 않았는지 확인
- [ ] `.env` 파일이 Git에 커밋되지 않았는지 확인

**확인 방법:**
```powershell
git status
# secrets.toml, mflow_admin.json이 표시되면 안 됨!
```

### 3. 필수 파일 확인

- [ ] `streamlit_app.py` 존재
- [ ] `requirements.txt` 존재
- [ ] `license_core.py` 존재
- [ ] `.streamlit/config.toml` 존재
- [ ] `.streamlit/secrets.toml.example` 존재 (예시 파일)

### 4. Streamlit Cloud 설정

#### 4.1 앱 생성
- [ ] Streamlit Cloud 계정 생성 (https://streamlit.io/cloud)
- [ ] GitHub 계정 연결
- [ ] 새 앱 생성
- [ ] 레포지토리 선택: `your-username/mflow-license-manager`
- [ ] Main file path: `streamlit_app.py`

#### 4.2 Secrets 설정
Streamlit Cloud → Settings → Secrets에 다음 설정:

**Firebase 설정:**
- [ ] `[firebase]` 섹션 추가
- [ ] 모든 필드 입력 완료
- [ ] `private_key`에 `\n` 포함 확인

**SMTP 설정:**
- [ ] `SMTP_EMAIL` 입력
- [ ] `SMTP_PASSWORD` 입력 (Gmail 앱 비밀번호)
- [ ] `SMTP_SERVER` 입력
- [ ] `SMTP_PORT` 입력

**관리자 계정:**
- [ ] `ADMIN_USERNAME` 입력
- [ ] `ADMIN_PASSWORD_HASH` 입력 (setup_admin.py로 생성)

**Secrets 형식:**
```toml
[firebase]
type = "service_account"
project_id = "your-project-id"
private_key_id = "your-private-key-id"
private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
client_email = "firebase-adminsdk-xxxxx@your-project.iam.gserviceaccount.com"
client_id = "123456789"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs/firebase-adminsdk-xxxxx%40your-project.iam.gserviceaccount.com"

SMTP_EMAIL = "your-email@gmail.com"
SMTP_PASSWORD = "your-app-password"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD_HASH = "your-password-hash"
```

### 5. 배포 후 테스트

- [ ] 앱이 정상적으로 로드되는지 확인
- [ ] 로그인 페이지 표시 확인
- [ ] 관리자 로그인 성공 확인
- [ ] Firebase 연결 성공 메시지 확인
- [ ] 라이선스 목록 로드 확인
- [ ] 라이선스 발급 테스트
- [ ] 이메일 발송 테스트 (SMTP 테스트 기능 사용)

## 🔍 문제 해결

### 배포 실패 시

1. **로그 확인**
   - Streamlit Cloud → Manage app → Logs
   - 에러 메시지 확인

2. **일반적인 문제**
   - `requirements.txt` 누락 → 파일 생성
   - Secrets 오류 → 형식 확인
   - Firebase 연결 실패 → Secrets의 Firebase 설정 확인
   - Import 에러 → requirements.txt 패키지 확인

### Firebase 연결 실패

- Secrets의 `[firebase]` 섹션 확인
- `private_key`에 `\n` 포함 확인
- 모든 필드 입력 확인

### SMTP 연결 실패

- Gmail 앱 비밀번호 확인
- Streamlit Cloud에서 SMTP outbound 차단 가능 → SendGrid 권장

## 📋 최종 체크리스트

배포 전 최종 확인:

- [ ] 모든 코드 커밋 및 푸시 완료
- [ ] 보안 파일이 Git에 포함되지 않음
- [ ] Streamlit Cloud Secrets 설정 완료
- [ ] 앱 배포 성공
- [ ] 로그인 테스트 성공
- [ ] 기본 기능 테스트 성공

## 🎉 배포 완료!

배포가 완료되면:
1. 앱 URL 확인
2. 팀원에게 공유
3. 정기적으로 모니터링

## 📞 도움말

- [배포 가이드](DEPLOYMENT.md) - 상세한 배포 방법
- [Secrets 설정](SECRETS_SETUP.md) - Firebase Secrets 설정
- [이메일 설정](EMAIL_SETUP.md) - SMTP/SendGrid 설정

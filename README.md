# MFLOW 라이선스 관리 시스템

Streamlit 기반의 웹 라이선스 관리 대시보드입니다.

## ✨ 주요 기능

- 🔐 관리자 인증 시스템
- 📝 라이선스 발급 (단일/일괄)
- 📊 라이선스 조회 및 검색
- 🎯 플랜 변경 (PRO, DIAMOND, MASTER)
- 📧 이메일 자동 발송 (SMTP/SendGrid)
- 💾 Excel 내보내기
- 📱 모바일 최적화

## 🚀 빠른 시작

### 로컬 개발

1. **가상환경 생성 및 활성화**
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

2. **패키지 설치**
   ```powershell
   pip install -r requirements.txt
   ```

3. **Secrets 설정**
   ```powershell
   # .streamlit/secrets.toml.example을 복사
   cp .streamlit/secrets.toml.example .streamlit/secrets.toml
   ```
   
   `.streamlit/secrets.toml` 파일을 열고 실제 값 입력:
   - Firebase 설정
   - SMTP 이메일 설정
   - 관리자 계정 설정

4. **Firebase 인증 파일 준비**
   - `mflow_admin.json` 파일을 프로젝트 루트에 배치

5. **실행**
   ```powershell
   streamlit run streamlit_app.py
   ```

### Streamlit Cloud 배포

자세한 배포 가이드는 [DEPLOYMENT.md](DEPLOYMENT.md)를 참고하세요.

**간단 요약:**
1. GitHub 레포지토리에 푸시
2. Streamlit Cloud에서 앱 생성
3. Secrets 설정 (Firebase, SMTP, 관리자 계정)
4. 배포 완료!

## 📁 프로젝트 구조

```
mflow-license-manager/
├── streamlit_app.py          # 메인 애플리케이션
├── license_core.py           # 라이선스 생성/검증 로직
├── setup_admin.py            # 관리자 비밀번호 설정 도구
├── requirements.txt           # Python 패키지 의존성
├── .streamlit/
│   ├── config.toml           # Streamlit 설정
│   ├── secrets.toml          # Secrets (Git 제외)
│   └── secrets.toml.example  # Secrets 예시
├── .gitignore                # Git 제외 파일
├── README.md                 # 이 파일
├── DEPLOYMENT.md             # 배포 가이드
├── AUTH_SETUP.md             # 인증 설정 가이드
├── EMAIL_SETUP.md            # 이메일 설정 가이드
└── SECRETS_SETUP.md          # Secrets 설정 가이드
```

## 🔐 보안

- ✅ 관리자 인증 (SHA256 해싱)
- ✅ Secrets 관리 (Git 제외)
- ✅ Firebase 인증 파일 보호
- ✅ 환경변수로 민감 정보 관리

## 📚 문서

- [배포 가이드](DEPLOYMENT.md) - Streamlit Cloud 배포 방법
- [인증 설정](AUTH_SETUP.md) - 관리자 계정 설정
- [이메일 설정](EMAIL_SETUP.md) - SMTP/SendGrid 설정
- [Secrets 설정](SECRETS_SETUP.md) - Firebase Secrets 설정

## 🛠️ 개발

### 필수 패키지

- `streamlit`: 웹 프레임워크
- `pandas`: 데이터 처리
- `openpyxl`: Excel 파일 생성
- `firebase-admin`: Firebase 연동
- `python-dotenv`: 환경변수 관리

### 환경변수

`.streamlit/secrets.toml` 또는 Streamlit Cloud Secrets에 설정:

```toml
# Firebase
FIREBASE_CREDENTIALS_PATH = "mflow_admin.json"
# 또는 [firebase] 섹션 (배포용)

# SMTP
SMTP_EMAIL = "your-email@gmail.com"
SMTP_PASSWORD = "your-app-password"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465

# 관리자
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD_HASH = "your-password-hash"
```

## 📝 라이선스

© 2025 MFLOW. All rights reserved.

## 📞 지원

문제가 발생하면:
1. 문서 확인 (위의 문서 섹션)
2. Streamlit Cloud 로그 확인
3. GitHub Issues 생성

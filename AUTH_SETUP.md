# 관리자 인증 설정 가이드

## 🔒 보안 설정

MFLOW 라이선스 관리 시스템에 관리자 인증이 추가되었습니다.

## 📋 기본 계정

**기본 계정 (개발/테스트용)**
- 사용자명: `admin`
- 비밀번호: `admin123`

⚠️ **운영 환경에서는 반드시 비밀번호를 변경하세요!**

## 🔧 비밀번호 변경 방법

### 방법 1: 자동 설정 스크립트 사용 (권장)

```powershell
# 가상환경 활성화
cd c:\Users\y2k_w\projects\mflow-license-manager
.\venv\Scripts\Activate.ps1

# 비밀번호 설정 스크립트 실행
python setup_admin.py
```

스크립트가 안내하는 대로:
1. 사용자명 입력 (기본값: admin)
2. 새 비밀번호 입력 (최소 8자)
3. 비밀번호 확인
4. 생성된 해시를 `.env` 파일에 추가

### 방법 2: 수동 설정

1. **비밀번호 해시 생성**

Python에서 직접 해시 생성:
```python
import hashlib
password = "your_secure_password"
hash_value = hashlib.sha256(password.encode()).hexdigest()
print(hash_value)
```

2. **`.env` 파일에 추가**

`.env` 파일을 열고 다음 내용 추가:
```env
ADMIN_USERNAME=admin
ADMIN_PASSWORD_HASH=생성된_해시값
```

예시:
```env
ADMIN_USERNAME=admin
ADMIN_PASSWORD_HASH=8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918
```

3. **Streamlit 재시작**

```powershell
# 기존 실행 중인 앱 종료 (Ctrl+C)
# 다시 실행
.\venv\Scripts\python.exe -m streamlit run streamlit_app.py
```

## 🔐 보안 권장사항

### 비밀번호 요구사항
- ✅ 최소 8자 이상
- ✅ 영문 대소문자 조합
- ✅ 숫자 포함
- ✅ 특수문자 포함 권장

### 보안 체크리스트
- [ ] 기본 비밀번호 변경 완료
- [ ] `.env` 파일을 `.gitignore`에 추가
- [ ] 비밀번호를 안전한 곳에 보관
- [ ] 정기적으로 비밀번호 변경 (3개월마다)
- [ ] 의심스러운 접속 시도 모니터링

## 🚀 로그인 방법

1. 웹 브라우저에서 앱 접속
2. 로그인 페이지에서 사용자명과 비밀번호 입력
3. "🚀 로그인" 버튼 클릭
4. 로그인 성공 시 메인 대시보드로 이동

## 🚪 로그아웃

- 우측 상단 "🚪 로그아웃" 버튼 클릭
- 세션이 종료되고 로그인 페이지로 이동

## 🔑 비밀번호 분실 시

1. `setup_admin.py` 스크립트를 다시 실행
2. 새 비밀번호로 해시 생성
3. `.env` 파일의 `ADMIN_PASSWORD_HASH` 업데이트
4. Streamlit 재시작

## 📝 환경변수 전체 예시

`.env` 파일 전체 구성:

```env
# Firebase 설정
FIREBASE_CREDENTIALS_PATH=mflow_admin.json

# SMTP 설정
SMTP_EMAIL=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=465

# 관리자 계정 설정
ADMIN_USERNAME=admin
ADMIN_PASSWORD_HASH=8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918
```

## 🛡️ 추가 보안 기능 (향후 추가 예정)

- [ ] 2단계 인증 (2FA)
- [ ] IP 화이트리스트
- [ ] 로그인 시도 제한
- [ ] 세션 타임아웃
- [ ] 접속 로그 기록
- [ ] 다중 관리자 계정

## ❓ 문제 해결

### 로그인이 안 돼요
1. 사용자명과 비밀번호를 정확히 입력했는지 확인
2. `.env` 파일의 해시값이 올바른지 확인
3. Streamlit을 재시작했는지 확인

### 비밀번호를 잊어버렸어요
1. `setup_admin.py`로 새 비밀번호 설정
2. `.env` 파일 업데이트
3. Streamlit 재시작

### 기본 비밀번호가 작동하지 않아요
- `.env` 파일에 `ADMIN_PASSWORD_HASH`가 설정되어 있는지 확인
- 설정되어 있다면 해당 비밀번호를 사용해야 합니다
- 설정되어 있지 않다면 기본 비밀번호 `admin123` 사용

## 📞 지원

문제가 계속되면 관리자에게 문의하세요.

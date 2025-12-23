# Secrets 설정 가이드

## 🔐 Firebase 인증 정보를 Secrets에 추가하기

### 로컬 개발 환경

로컬에서는 `mflow_admin.json` 파일을 그대로 사용합니다.

`.streamlit/secrets.toml`:
```toml
FIREBASE_CREDENTIALS_PATH = "mflow_admin.json"
```

### Streamlit Cloud 배포

Streamlit Cloud에는 파일을 업로드할 수 없으므로, Firebase 인증 정보를 secrets에 직접 입력합니다.

#### 단계별 가이드:

**1단계: mflow_admin.json 파일 열기**

```json
{
  "type": "service_account",
  "project_id": "your-project-123",
  "private_key_id": "abc123...",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC...\n-----END PRIVATE KEY-----\n",
  "client_email": "firebase-adminsdk-xxxxx@your-project.iam.gserviceaccount.com",
  "client_id": "123456789",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs/firebase-adminsdk-xxxxx%40your-project.iam.gserviceaccount.com"
}
```

**2단계: Streamlit Cloud Secrets 형식으로 변환**

Streamlit Cloud 앱 대시보드 → Settings → Secrets에 다음 형식으로 입력:

```toml
[firebase]
type = "service_account"
project_id = "your-project-123"
private_key_id = "abc123..."
private_key = "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC...\n-----END PRIVATE KEY-----\n"
client_email = "firebase-adminsdk-xxxxx@your-project.iam.gserviceaccount.com"
client_id = "123456789"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs/firebase-adminsdk-xxxxx%40your-project.iam.gserviceaccount.com"
```

**3단계: 나머지 Secrets 추가**

```toml
# SMTP 이메일 설정
SMTP_EMAIL = "your-email@gmail.com"
SMTP_PASSWORD = "your-app-password"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465

# 관리자 계정 설정
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD_HASH = "240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9"
```

## ⚠️ 주의사항

### private_key 처리

**잘못된 예** (줄바꿈이 실제로 들어감):
```toml
private_key = "-----BEGIN PRIVATE KEY-----
MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC...
-----END PRIVATE KEY-----"
```

**올바른 예** (`\n`으로 줄바꿈 표시):
```toml
private_key = "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC...\n-----END PRIVATE KEY-----\n"
```

### 따옴표 제거

JSON에서 복사할 때 `"` 따옴표는 제거하고 값만 입력:

**JSON**:
```json
"project_id": "my-project-123"
```

**TOML** (따옴표 유지):
```toml
project_id = "my-project-123"
```

### 특수문자 이스케이프

- `@` 기호는 URL에서 `%40`으로 인코딩됨
- 그대로 복사하면 됨

## 🔍 검증 방법

### 로컬에서 테스트

1. `.streamlit/secrets.toml`에 `[firebase]` 섹션 추가
2. 앱 실행:
   ```powershell
   .\venv\Scripts\python.exe -m streamlit run streamlit_app.py
   ```
3. "✅ Firebase 연결 성공" 메시지 확인

### Streamlit Cloud에서 테스트

1. 앱 배포
2. 로그 확인 (앱 대시보드 → Manage app → Logs)
3. Firebase 연결 에러가 없는지 확인

## 🛠️ 문제 해결

### "Firebase 초기화 실패" 에러

**원인 1: private_key 형식 오류**
- `\n`이 실제 줄바꿈으로 변환되었는지 확인
- 한 줄로 이어져야 함 (중간에 실제 줄바꿈 없음)

**원인 2: 필드 누락**
- 모든 필드가 입력되었는지 확인
- 특히 `type`, `project_id`, `private_key`, `client_email` 필수

**원인 3: 따옴표 문제**
- TOML 형식에서는 값에 따옴표 필요
- `project_id = my-project` ❌
- `project_id = "my-project"` ✅

### "Invalid private key" 에러

private_key를 다시 확인:
1. `-----BEGIN PRIVATE KEY-----`로 시작
2. `-----END PRIVATE KEY-----`로 끝
3. 중간에 `\n` 문자열 포함 (실제 줄바꿈 아님)

### Streamlit Cloud에서만 에러

1. Secrets 페이지에서 내용 재확인
2. 앱 재시작 (Reboot app)
3. 로그에서 정확한 에러 메시지 확인

## 📋 체크리스트

배포 전 확인:

- [ ] `mflow_admin.json` 파일 내용 확인
- [ ] Streamlit Cloud Secrets에 `[firebase]` 섹션 추가
- [ ] `private_key`에 `\n` 포함 확인
- [ ] 모든 필드 입력 완료
- [ ] SMTP 설정 추가
- [ ] 관리자 비밀번호 해시 추가
- [ ] 앱 배포 및 로그 확인
- [ ] Firebase 연결 성공 메시지 확인

## 💡 팁

### Python 스크립트로 변환

`mflow_admin.json`을 TOML 형식으로 자동 변환:

```python
import json

# JSON 파일 읽기
with open('mflow_admin.json', 'r') as f:
    data = json.load(f)

# TOML 형식으로 출력
print("[firebase]")
for key, value in data.items():
    print(f'{key} = "{value}"')
```

실행:
```powershell
python convert_to_toml.py
```

출력을 복사하여 Streamlit Cloud Secrets에 붙여넣기!

## 🔒 보안

- ✅ `mflow_admin.json` 파일은 Git에 커밋하지 않음 (`.gitignore`)
- ✅ Secrets는 Streamlit Cloud에서 암호화되어 저장
- ✅ 로그에 민감 정보가 출력되지 않도록 주의
- ✅ Firebase 서비스 계정 권한을 최소한으로 설정

## 📞 도움이 필요하면

1. Streamlit Cloud 로그 확인
2. Firebase Console에서 서비스 계정 권한 확인
3. `mflow_admin.json` 파일 재다운로드
4. Streamlit Community Forum 질문

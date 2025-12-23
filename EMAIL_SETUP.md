# 이메일 설정 가이드

## 📧 이메일 발송 방식

### 옵션 1: Gmail SMTP (간단, 로컬 테스트용)

#### 장점:
- ✅ 무료
- ✅ 설정 간단
- ✅ 로컬 개발에 적합

#### 단점:
- ❌ Streamlit Cloud에서 불안정 (outbound 차단 가능)
- ❌ 하루 500통 제한
- ❌ 스팸 필터에 걸릴 수 있음

#### 설정 방법:

1. **Gmail 2단계 인증 활성화**
   - https://myaccount.google.com/security
   - "2단계 인증" 활성화

2. **앱 비밀번호 생성**
   - https://myaccount.google.com/apppasswords
   - "앱 선택" → "메일"
   - "기기 선택" → "기타" → "MFLOW"
   - 생성된 16자리 비밀번호 복사

3. **Secrets 설정**
   ```toml
   SMTP_EMAIL = "your-email@gmail.com"
   SMTP_PASSWORD = "abcd efgh ijkl mnop"  # 16자리 앱 비밀번호
   SMTP_SERVER = "smtp.gmail.com"
   SMTP_PORT = 465
   ```

### 옵션 2: SendGrid API (추천, 운영용)

#### 장점:
- ✅ 안정적 (API 기반)
- ✅ Streamlit Cloud에서 정상 작동
- ✅ 하루 100통 무료
- ✅ 전송 통계 제공
- ✅ 스팸 필터 회피

#### 단점:
- ❌ 회원가입 필요
- ❌ 도메인 인증 권장 (선택사항)

#### 설정 방법:

1. **SendGrid 회원가입**
   - https://signup.sendgrid.com/
   - 무료 플랜 선택

2. **API 키 생성**
   - Settings → API Keys → Create API Key
   - "Full Access" 또는 "Mail Send" 권한
   - API 키 복사 (한 번만 표시됨!)

3. **Secrets 설정**
   ```toml
   SENDGRID_API_KEY = "SG.xxxxxxxxxxxxxxxxxxxxx"
   SENDGRID_FROM_EMAIL = "noreply@yourdomain.com"
   ```

4. **코드 수정 필요** (아래 참고)

### 옵션 3: AWS SES (대용량, 저렴)

#### 장점:
- ✅ 매우 저렴 (1000통당 $0.10)
- ✅ 안정적
- ✅ AWS 인프라

#### 단점:
- ❌ AWS 계정 필요
- ❌ 설정 복잡
- ❌ 샌드박스 모드 해제 필요

## 🔧 SendGrid 구현 (추천)

### 1. SendGrid 패키지 설치

`requirements.txt`에 추가:
```
sendgrid==6.11.0
```

### 2. 코드 수정

`streamlit_app.py`에 SendGrid 함수 추가:

```python
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

# Secrets에서 SendGrid 설정 로드
SENDGRID_API_KEY = get_secret("SENDGRID_API_KEY", "")
SENDGRID_FROM_EMAIL = get_secret("SENDGRID_FROM_EMAIL", "")

def send_email_sendgrid(to_email, subject, body):
    """SendGrid API로 이메일 발송"""
    if not SENDGRID_API_KEY:
        st.warning("SendGrid API 키가 설정되지 않았습니다.")
        return False
    
    try:
        message = Mail(
            from_email=SENDGRID_FROM_EMAIL,
            to_emails=to_email,
            subject=subject,
            plain_text_content=body
        )
        
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        
        return response.status_code == 202
    
    except Exception as e:
        st.error(f"SendGrid 이메일 발송 실패: {e}")
        return False

def send_license_email(email, license_key, plan):
    """라이선스 키를 이메일로 발송 (SendGrid 우선)"""
    subject = f"[MFLOW] {plan} 플랜 라이센스 발급 완료"
    body = f"""
안녕하세요!

MFLOW {plan} 플랜 라이센스가 발급되었습니다.

📧 이메일: {email}
🔑 라이센스 키: {license_key}
🎯 플랜: {plan}

라이센스 키를 프로그램에 입력하여 활성화하세요.

감사합니다.
MFLOW 팀
    """
    
    # SendGrid 우선 시도
    if SENDGRID_API_KEY:
        return send_email_sendgrid(email, subject, body)
    
    # SMTP 대체
    return send_email_smtp(email, subject, body)
```

## 🔍 에러 진단

### SMTP 에러 유형

#### 1. SMTPAuthenticationError
```
❌ SMTP 인증 실패: 이메일 또는 비밀번호가 올바르지 않습니다.
```

**해결 방법:**
- Gmail 앱 비밀번호 재생성
- 2단계 인증 활성화 확인
- secrets.toml의 SMTP_EMAIL, SMTP_PASSWORD 확인

#### 2. SMTPConnectError / Connection timed out
```
❌ 연결 시간 초과: SMTP 서버에 연결할 수 없습니다.
```

**원인:**
- Streamlit Cloud에서 SMTP outbound 차단
- 방화벽 차단
- 네트워크 문제

**해결 방법:**
- SendGrid API로 전환 (추천)
- 다른 SMTP 서버 시도 (Mailgun, Postmark)
- ngrok으로 로컬 서버 공개

#### 3. SMTPServerDisconnected
```
❌ SMTP 서버 연결 끊김
```

**해결 방법:**
- 네트워크 안정성 확인
- timeout 값 증가
- 재시도 로직 추가

## 📊 이메일 발송 테스트

### 로컬 테스트

```python
# streamlit_app.py에 테스트 함수 추가
def test_email_config():
    """이메일 설정 테스트"""
    st.write("### 📧 이메일 설정 테스트")
    
    st.write(f"SMTP_EMAIL: {SMTP_EMAIL if SMTP_EMAIL else '❌ 설정 안 됨'}")
    st.write(f"SMTP_PASSWORD: {'✅ 설정됨' if SMTP_PASSWORD else '❌ 설정 안 됨'}")
    st.write(f"SMTP_SERVER: {SMTP_SERVER}")
    st.write(f"SMTP_PORT: {SMTP_PORT}")
    
    if st.button("테스트 이메일 발송"):
        if send_license_email("test@example.com", "TEST-1234-5678-9012", "PRO"):
            st.success("✅ 이메일 발송 성공!")
        else:
            st.error("❌ 이메일 발송 실패")

# 사이드바에 추가
with st.sidebar:
    if st.checkbox("이메일 테스트 모드"):
        test_email_config()
```

### Streamlit Cloud 테스트

1. 앱 배포
2. 로그 확인 (Manage app → Logs)
3. 테스트 라이선스 발급
4. 에러 메시지 확인

## 🚀 운영 권장 사항

### 단계별 전환

**1단계: 개발 (로컬)**
- Gmail SMTP 사용
- 빠른 테스트

**2단계: 스테이징 (Streamlit Cloud)**
- SendGrid 무료 플랜
- 실제 이메일 발송 테스트

**3단계: 운영 (프로덕션)**
- SendGrid 유료 플랜 또는 AWS SES
- 도메인 인증
- 전송 통계 모니터링

### 모니터링

- 이메일 발송 성공률 추적
- 실패 로그 수집
- 사용자 피드백 수집

## 📝 체크리스트

배포 전 확인:

- [ ] SMTP 또는 SendGrid 설정 완료
- [ ] secrets.toml에 이메일 설정 추가
- [ ] 테스트 이메일 발송 성공
- [ ] 에러 처리 로직 확인
- [ ] 사용자에게 이메일 발송 실패 시 안내 메시지 표시

## 💡 팁

### Gmail 대신 다른 SMTP 서비스

**Mailgun:**
```toml
SMTP_EMAIL = "postmaster@yourdomain.mailgun.org"
SMTP_PASSWORD = "your-mailgun-password"
SMTP_SERVER = "smtp.mailgun.org"
SMTP_PORT = 587
```

**Outlook/Hotmail:**
```toml
SMTP_EMAIL = "your-email@outlook.com"
SMTP_PASSWORD = "your-password"
SMTP_SERVER = "smtp-mail.outlook.com"
SMTP_PORT = 587
```

### 이메일 템플릿 개선

- HTML 이메일 사용
- 로고 이미지 추가
- 반응형 디자인
- 버튼 링크 추가

## 📞 지원

문제가 계속되면:
1. Streamlit Cloud 로그 확인
2. SendGrid 대시보드에서 전송 상태 확인
3. Gmail 계정 보안 설정 확인
4. 이메일 제공업체 지원팀 문의

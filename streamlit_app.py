import streamlit as st
import pandas as pd
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import os
from dotenv import load_dotenv
from license_core import generate_license
import smtplib
from email.mime.text import MIMEText
import hashlib
import hmac

# 환경변수 로드 (로컬 개발용)
load_dotenv()

# Streamlit secrets 사용 (배포용, 로컬에서도 사용 가능)
def get_secret(key, default=""):
    """Streamlit secrets 또는 환경변수에서 값 가져오기"""
    # 1순위: Streamlit secrets
    try:
        if hasattr(st, 'secrets'):
            # secrets 객체 직접 접근 시도
            try:
                value = st.secrets[key]
                if value is not None:
                    value_str = str(value).strip()
                    if value_str:
                        return value_str
            except KeyError:
                # 키가 없으면 다음 단계로
                pass
            except Exception:
                # 기타 오류는 무시
                pass
            
            # dict로 변환하여 재시도
            try:
                secrets_dict = dict(st.secrets)
                if key in secrets_dict:
                    value = secrets_dict[key]
                    if value is not None:
                        value_str = str(value).strip()
                        if value_str:
                            return value_str
            except Exception:
                pass
    except Exception:
        pass
    
    # 2순위: 환경변수 (.env)
    try:
        env_value = os.getenv(key)
        if env_value:
            return env_value
    except:
        pass
    
    return default

# 페이지 설정 (모바일 최적화)
st.set_page_config(
    page_title="MFLOW 라이선스 관리",
    page_icon="🔑",
    layout="wide",
    initial_sidebar_state="collapsed",  # 모바일에서 기본적으로 닫힘
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': "# MFLOW License Manager v2.0\n모바일 최적화 웹 대시보드"
    }
)

# Firebase 초기화 (한 번만 실행)
@st.cache_resource
def init_firebase():
    """Firebase 초기화"""
    try:
        if not firebase_admin._apps:
            # Streamlit Cloud용: secrets에서 Firebase 인증 정보 직접 로드
            try:
                # st.secrets가 있는지 확인
                if hasattr(st, 'secrets'):
                    # secrets를 dict로 변환하여 확인
                    try:
                        secrets_dict = dict(st.secrets)
                        available_keys = list(secrets_dict.keys())
                        
                        # firebase 섹션이 있는지 확인
                        if "firebase" in secrets_dict:
                            firebase_config = dict(st.secrets["firebase"])
                            # 필수 필드 확인
                            required_fields = ["type", "project_id", "private_key", "client_email"]
                            missing_fields = [f for f in required_fields if f not in firebase_config]
                            
                            if missing_fields:
                                st.error(f"❌ Firebase Secrets에 필수 필드 누락: {', '.join(missing_fields)}")
                                return None
                            
                            cred = credentials.Certificate(firebase_config)
                        else:
                            # firebase 섹션이 없음 - 디버깅 정보 표시
                            st.warning(f"⚠️ Secrets에 'firebase' 섹션이 없습니다.")
                            st.caption(f"사용 가능한 Secrets 키: {available_keys}")
                            raise KeyError("firebase section not found in secrets")
                    except Exception as secrets_error:
                        # secrets 읽기 오류
                        st.warning(f"⚠️ Secrets 읽기 오류: {secrets_error}")
                        raise
                else:
                    # st.secrets가 없음
                    raise AttributeError("st.secrets not available")
            except (KeyError, AttributeError) as e:
                # 로컬 개발용: 파일에서 로드
                firebase_credentials_path = get_secret("FIREBASE_CREDENTIALS_PATH", "mflow_admin.json")
                if not os.path.exists(firebase_credentials_path):
                    st.error(f"❌ Firebase 인증 파일을 찾을 수 없습니다: {firebase_credentials_path}")
                    st.warning("""
                    **Streamlit Cloud 배포 시:**
                    
                    Firebase 인증 정보를 Secrets에 추가해야 합니다.
                    
                    1. Streamlit Cloud → Settings → Secrets
                    2. `[firebase]` 섹션이 있는지 확인
                    3. 모든 필드가 올바르게 입력되었는지 확인
                    4. 앱 재시작 (Reboot app)
                    
                    **디버깅 정보:**
                    - st.secrets 존재: """ + str(hasattr(st, 'secrets')) + """
                    - 사용 가능한 Secrets 키: """ + (str(list(st.secrets.keys())) if hasattr(st, 'secrets') else "N/A") + """
                    
                    **중요:** Secrets를 저장한 후 반드시 앱을 재시작하세요! (Reboot app)
                    """)
                    return None
                cred = credentials.Certificate(firebase_credentials_path)
            
            firebase_admin.initialize_app(cred)
        
        db = firestore.client()
        st.success("✅ Firebase 연결 성공")
        return db
    except Exception as e:
        error_msg = str(e)
        st.error(f"⚠️ Firebase 초기화 실패: {error_msg}")
        
        # 상세한 에러 정보 표시
        if "firebase" in error_msg.lower() or "certificate" in error_msg.lower():
            st.info("""
            **가능한 원인:**
            1. Secrets의 `[firebase]` 섹션 형식 오류
            2. `private_key`에 `\\n`이 올바르게 포함되지 않음
            3. 필수 필드 누락
            
            **해결 방법:**
            - `SECRETS_SETUP.md` 파일 참고
            - Secrets 페이지에서 형식 재확인
            - 앱 재시작
            """)
        
        return None

# Secrets에서 설정값 가져오기
SMTP_EMAIL = get_secret("SMTP_EMAIL")
SMTP_PASSWORD = get_secret("SMTP_PASSWORD")
SMTP_SERVER = get_secret("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(get_secret("SMTP_PORT", "465"))

# 관리자 계정 설정
ADMIN_USERNAME = get_secret("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD_HASH = get_secret("ADMIN_PASSWORD_HASH", "")

# 디버깅: Secrets 읽기 확인 (개발용 - 운영 시 제거 가능)
if not ADMIN_PASSWORD_HASH:
    # Secrets에서 읽지 못한 경우 기본값 사용
    pass

# 비밀번호 해싱 함수
def hash_password(password: str) -> str:
    """비밀번호를 SHA256으로 해싱"""
    return hashlib.sha256(password.encode()).hexdigest()

# 비밀번호 검증 함수
def verify_password(password: str, password_hash: str) -> bool:
    """비밀번호 검증"""
    return hmac.compare_digest(hash_password(password), password_hash)

# 로그인 확인 함수
def check_login(username: str, password: str) -> bool:
    """로그인 검증"""
    if not ADMIN_PASSWORD_HASH:
        # 환경변수에 해시가 없으면 기본 비밀번호 사용 (개발용)
        default_hash = hash_password("admin123")
        return username == ADMIN_USERNAME and hash_password(password) == default_hash
    
    return username == ADMIN_USERNAME and verify_password(password, ADMIN_PASSWORD_HASH)

# 세션 상태 초기화
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'username' not in st.session_state:
    st.session_state.username = ""

# Firebase 초기화
db = init_firebase()

# 로그인 페이지 함수
def show_login_page():
    """로그인 페이지 표시"""
    st.markdown("""
    <style>
        .login-container {
            max-width: 400px;
            margin: 0 auto;
            padding: 2rem;
            background: linear-gradient(135deg, rgba(30, 41, 59, 0.9) 0%, rgba(15, 23, 42, 0.9) 100%);
            border-radius: 16px;
            border: 2px solid #334155;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            margin-top: 10vh;
        }
        
        .login-title {
            text-align: center;
            color: #f1f5f9;
            font-size: 2rem;
            margin-bottom: 2rem;
            font-weight: 700;
        }
        
        .login-subtitle {
            text-align: center;
            color: #94a3b8;
            margin-bottom: 2rem;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # 로그인 컨테이너
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        
        st.markdown('<h1 class="login-title">🔑 MFLOW</h1>', unsafe_allow_html=True)
        st.markdown('<p class="login-subtitle">라이선스 관리 시스템</p>', unsafe_allow_html=True)
        
        # 도움말 버튼 (폼 밖에서)
        if st.button("❓ 기본 계정 정보", width="stretch"):
            st.info("💡 기본 계정: admin / admin123")
        
        # 로그인 폼
        with st.form("login_form"):
            st.write("로그인")
            username = st.text_input("👤 사용자명", placeholder="admin 입력")
            password = st.text_input("🔒 비밀번호", type="password", placeholder="admin123 입력")
            
            submit = st.form_submit_button("🚀 로그인", width="stretch")
            
            if submit:
                # 입력값 확인
                if not username or not password:
                    st.error("⚠️ 사용자명과 비밀번호를 입력해주세요.")
                elif check_login(username, password):
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.success("✅ 로그인 성공!")
                    st.rerun()
                else:
                    st.error("❌ 사용자명 또는 비밀번호가 올바르지 않습니다.")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 안내 메시지
        st.markdown("---")
        st.caption("🔒 보안을 위해 환경변수에서 관리자 계정을 설정하세요.")
        
        # 디버깅 정보 (개발용)
        if not ADMIN_PASSWORD_HASH:
            st.warning("⚠️ Secrets에 ADMIN_PASSWORD_HASH가 설정되지 않았습니다. 기본 비밀번호(admin123)를 사용합니다.")
            
            # 디버깅: 사용 가능한 Secrets 키 표시
            try:
                if hasattr(st, 'secrets'):
                    secrets_dict = dict(st.secrets)
                    available_keys = list(secrets_dict.keys())
                    st.caption(f"🔍 사용 가능한 Secrets 키: {available_keys}")
                    
                    # ADMIN 관련 키 확인
                    admin_keys = [k for k in available_keys if 'ADMIN' in k.upper() or 'admin' in k.lower()]
                    if admin_keys:
                        st.caption(f"📋 ADMIN 관련 키: {admin_keys}")
            except:
                pass
            
            st.caption("💡 Streamlit Cloud → Settings → Secrets에 다음을 추가하세요:")
            st.code("ADMIN_USERNAME = \"admin\"\nADMIN_PASSWORD_HASH = \"your-password-hash\"", language="toml")
        else:
            st.caption("✅ 관리자 비밀번호가 Secrets에서 로드되었습니다.")
            st.caption(f"👤 사용자명: {ADMIN_USERNAME}")

# 로그아웃 함수
def logout():
    """로그아웃 처리"""
    st.session_state.authenticated = False
    st.session_state.username = ""
    st.rerun()

# 인증 확인 - 로그인하지 않은 경우 로그인 페이지 표시
if not st.session_state.authenticated:
    show_login_page()
    st.stop()

# 모바일 뷰포트 메타 태그 추가
st.markdown("""
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0, user-scalable=yes">
<meta name="theme-color" content="#0f172a">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
""", unsafe_allow_html=True)

# CSS 스타일
st.markdown("""
<style>
    /* 전체 배경 */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
    }
    
    /* 메인 컨테이너 */
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 2rem;
        max-width: 100%;
        padding-left: 1rem;
        padding-right: 1rem;
    }
    
    /* 사이드바가 닫혔을 때 메인 영역 최대화 */
    section[data-testid="stSidebar"][aria-expanded="false"] ~ .main {
        margin-left: 0 !important;
    }
    
    section[data-testid="stSidebar"][aria-expanded="true"] ~ .main {
        margin-left: 0 !important;
    }
    
    /* 카드 스타일 */
    .stCard {
        background-color: rgba(30, 41, 59, 0.7);
        border: 2px solid #334155;
        border-radius: 12px;
        padding: 20px;
        margin: 10px 0;
    }
    
    /* 버튼 스타일 */
    .stButton > button {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
        min-height: 44px; /* 터치 친화적 최소 높이 */
        font-size: 14px;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
    }
    
    .stButton > button:active {
        transform: translateY(0px);
    }
    
    /* 테이블 스타일 */
    .dataframe {
        background-color: rgba(30, 41, 59, 0.5) !important;
        color: #f1f5f9 !important;
        font-size: 14px;
    }
    
    /* 입력 필드 */
    .stTextInput > div > div > input,
    .stSelectbox > div > div > select,
    .stTextArea > div > div > textarea {
        background-color: rgba(30, 41, 59, 0.8);
        color: #f1f5f9;
        border: 2px solid #334155;
        border-radius: 8px;
        min-height: 44px; /* 터치 친화적 */
        font-size: 16px; /* iOS 자동 줌 방지 */
    }
    
    /* 제목 */
    h1 {
        color: #f1f5f9;
        font-size: clamp(1.5rem, 5vw, 2.5rem); /* 반응형 폰트 */
    }
    
    h2 {
        color: #f1f5f9;
        font-size: clamp(1.2rem, 4vw, 1.8rem);
    }
    
    h3 {
        color: #f1f5f9;
        font-size: clamp(1rem, 3vw, 1.5rem);
    }
    
    /* 사이드바 */
    .css-1d391kg {
        background-color: rgba(15, 23, 42, 0.9);
    }
    
    /* 통계 메트릭 */
    [data-testid="stMetricValue"] {
        font-size: clamp(1rem, 3vw, 1.5rem);
    }
    
    [data-testid="stMetricLabel"] {
        font-size: clamp(0.8rem, 2vw, 1rem);
    }
    
    /* 모바일 최적화 (768px 이하) */
    @media (max-width: 768px) {
        .main .block-container {
            padding-top: 0.5rem;
            padding-bottom: 1rem;
            padding-left: 0.75rem;
            padding-right: 0.75rem;
        }
        
        /* 모바일에서 사이드바 완전히 숨김 */
        section[data-testid="stSidebar"] {
            width: 0 !important;
            min-width: 0 !important;
        }
        
        section[data-testid="stSidebar"][aria-expanded="true"] {
            width: 85vw !important;
            max-width: 320px !important;
        }
        
        /* 메인 영역 전체 너비 사용 */
        .main {
            margin-left: 0 !important;
            width: 100% !important;
        }
        
        .stButton > button {
            width: 100%;
            padding: 0.75rem 1rem;
            font-size: 13px;
        }
        
        /* 테이블 스크롤 가능하게 */
        .dataframe {
            font-size: 12px;
            overflow-x: auto;
        }
        
        /* 사이드바 폼 */
        .stTextInput > div > div > input,
        .stSelectbox > div > div > select {
            font-size: 16px; /* iOS 자동 줌 방지 */
        }
        
        /* 컬럼 간격 조정 */
        [data-testid="column"] {
            padding: 0.25rem;
            min-width: 0 !important;
        }
        
        /* 타이틀 영역 최적화 */
        h1 {
            margin-top: 0;
            padding-top: 0;
        }
        
        /* 메트릭 카드 */
        [data-testid="stMetric"] {
            background-color: rgba(30, 41, 59, 0.6);
            padding: 0.75rem;
            border-radius: 8px;
            border: 1px solid #334155;
        }
    }
    
    /* 초소형 모바일 (480px 이하) */
    @media (max-width: 480px) {
        h1 {
            font-size: 1.3rem;
            margin-bottom: 0.5rem;
        }
        
        h2 {
            font-size: 1.1rem;
        }
        
        h3 {
            font-size: 1rem;
        }
        
        .stButton > button {
            padding: 0.7rem 0.5rem;
            font-size: 12px;
            white-space: nowrap;
        }
        
        .dataframe {
            font-size: 10px;
        }
        
        /* 페이지네이션 버튼 */
        [data-testid="column"] > div > div > button {
            font-size: 11px;
            padding: 0.6rem 0.3rem;
        }
        
        /* 통계 카드 */
        [data-testid="stMetric"] {
            padding: 0.5rem;
        }
        
        [data-testid="stMetricValue"] {
            font-size: 1.2rem;
        }
        
        [data-testid="stMetricLabel"] {
            font-size: 0.75rem;
        }
    }
    
    /* 터치 디바이스 최적화 */
    @media (hover: none) and (pointer: coarse) {
        .stButton > button {
            min-height: 48px; /* 터치 권장 크기 */
        }
        
        .stCheckbox {
            min-height: 44px;
        }
        
        /* 테이블 셀 패딩 증가 */
        .dataframe td, .dataframe th {
            padding: 12px 8px;
        }
    }
    
    /* 가로 스크롤 개선 */
    .element-container {
        overflow-x: auto;
    }
    
    /* 데이터 에디터 반응형 */
    [data-testid="stDataFrame"] {
        overflow-x: auto;
        -webkit-overflow-scrolling: touch; /* iOS 부드러운 스크롤 */
    }
    
    /* 스크롤바 스타일 (모바일 친화적) */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(30, 41, 59, 0.5);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: rgba(59, 130, 246, 0.5);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(59, 130, 246, 0.7);
    }
    
    /* 터치 피드백 */
    .stButton > button:active,
    [data-testid="stCheckbox"]:active {
        opacity: 0.7;
    }
    
    /* 로딩 애니메이션 */
    .stSpinner > div {
        border-color: #3b82f6 !important;
    }
    
    /* 알림 메시지 모바일 최적화 */
    .stAlert {
        font-size: 14px;
        padding: 0.75rem;
    }
    
    /* 폼 요소 간격 */
    .stForm {
        padding: 0.5rem;
    }
    
    /* 사이드바 모바일 최적화 */
    @media (max-width: 768px) {
        [data-testid="stSidebar"][aria-expanded="true"] {
            position: fixed !important;
            z-index: 999999 !important;
            background-color: rgba(15, 23, 42, 0.98) !important;
        }
        
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h2 {
            font-size: 1.2rem;
        }
        
        /* 사이드바 열렸을 때 오버레이 */
        [data-testid="stSidebar"][aria-expanded="true"]::before {
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background-color: rgba(0, 0, 0, 0.5);
            z-index: -1;
        }
    }
    
    /* 빈 공간 클릭 방지 */
    .main {
        touch-action: pan-y;
    }
</style>
""", unsafe_allow_html=True)

# 세션 상태 초기화
if 'selected_emails' not in st.session_state:
    st.session_state.selected_emails = set()
if 'page' not in st.session_state:
    st.session_state.page = 1
if 'items_per_page' not in st.session_state:
    st.session_state.items_per_page = 20
if 'search_query' not in st.session_state:
    st.session_state.search_query = ""

def load_licenses():
    """Firestore에서 라이선스 목록 로드"""
    if db is None:
        return []
    
    try:
        licenses_ref = db.collection("licenses")
        docs = licenses_ref.stream()
        
        licenses = []
        for doc in docs:
            data = doc.to_dict()
            created_at = data.get("created_at", "")
            if created_at:
                try:
                    created_at = created_at.strftime("%Y-%m-%d %H:%M")
                except:
                    created_at = "N/A"
            
            licenses.append({
                "email": doc.id,
                "device_id": data.get("device_id", ""),
                "depositor": data.get("depositor", ""),
                "plan": data.get("plan", "BASIC"),
                "license_key": data.get("license_key", ""),
                "created_at": created_at
            })
        
        return licenses
    except Exception as e:
        st.error(f"데이터 로드 실패: {e}")
        return []

def send_license_email(email, license_key, plan):
    """라이선스 키를 이메일로 발송"""
    # SMTP 설정 확인
    if not SMTP_EMAIL or not SMTP_PASSWORD:
        st.warning("⚠️ SMTP 설정이 없어 이메일을 발송할 수 없습니다. secrets.toml을 확인하세요.")
        return False
    
    try:
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
        
        msg = MIMEText(body, "plain", "utf-8")
        msg["Subject"] = subject
        msg["From"] = SMTP_EMAIL
        msg["To"] = email
        
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, timeout=10) as server:
            server.login(SMTP_EMAIL, SMTP_PASSWORD)
            server.send_message(msg)
        
        return True
    
    except smtplib.SMTPAuthenticationError as e:
        st.error(f"❌ SMTP 인증 실패: 이메일 또는 비밀번호가 올바르지 않습니다.")
        st.caption(f"상세 에러: {str(e)}")
        return False
    
    except smtplib.SMTPConnectError as e:
        st.error(f"❌ SMTP 서버 연결 실패: {SMTP_SERVER}:{SMTP_PORT}")
        st.caption(f"상세 에러: {str(e)}")
        return False
    
    except TimeoutError as e:
        st.error(f"❌ 연결 시간 초과: SMTP 서버에 연결할 수 없습니다.")
        st.caption("Streamlit Cloud에서 SMTP outbound가 차단되었을 수 있습니다.")
        st.info("💡 대안: SendGrid, AWS SES 등의 이메일 API 사용을 권장합니다.")
        return False
    
    except Exception as e:
        error_type = type(e).__name__
        st.error(f"❌ 이메일 발송 실패 ({error_type}): {str(e)}")
        
        # 일반적인 에러 가이드
        if "timed out" in str(e).lower():
            st.caption("⚠️ 연결 시간 초과: 방화벽 또는 네트워크 문제일 수 있습니다.")
        elif "authentication" in str(e).lower():
            st.caption("⚠️ 인증 실패: Gmail 앱 비밀번호를 확인하세요.")
        
        return False

def send_plan_change_email(email, old_plan, new_plan, license_key):
    """플랜 변경 알림 이메일 발송"""
    # SMTP 설정 확인
    if not SMTP_EMAIL or not SMTP_PASSWORD:
        return False
    
    try:
        subject = f"[MFLOW] 라이센스 플랜 변경 안내 ({old_plan} → {new_plan})"
        body = f"""
안녕하세요!

귀하의 MFLOW 라이센스 플랜이 변경되었습니다.

📧 이메일: {email}
🔑 라이센스 키: {license_key}

📊 변경 내역:
   이전 플랜: {old_plan}
   새 플랜: {new_plan} ✨

변경된 플랜은 즉시 적용됩니다.
프로그램을 재시작하시면 새로운 플랜의 기능을 사용하실 수 있습니다.

감사합니다.
MFLOW 팀
        """
        
        msg = MIMEText(body, "plain", "utf-8")
        msg["Subject"] = subject
        msg["From"] = SMTP_EMAIL
        msg["To"] = email
        
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, timeout=10) as server:
            server.login(SMTP_EMAIL, SMTP_PASSWORD)
            server.send_message(msg)
        
        return True
    
    except (smtplib.SMTPAuthenticationError, smtplib.SMTPConnectError, TimeoutError):
        # 에러는 조용히 처리 (플랜 변경은 성공했으므로)
        return False
    
    except Exception:
        return False

# 메인 타이틀 (모바일 최적화) + 로그아웃 버튼
col_title, col_user, col_logout = st.columns([3, 1, 1])

with col_title:
    st.markdown("""
    <h1 style='margin: 0; font-size: clamp(1.3rem, 5vw, 2.5rem);'>🔑 MFLOW 라이선스 관리</h1>
    """, unsafe_allow_html=True)

with col_user:
    st.markdown(f"""
    <div style='text-align: right; padding-top: 0.5rem;'>
        <span style='color: #94a3b8; font-size: 0.9rem;'>👤 {st.session_state.username}</span>
    </div>
    """, unsafe_allow_html=True)

with col_logout:
    if st.button("🚪 로그아웃", key="logout_btn", width="stretch"):
        logout()

# 사이드바 안내 메시지
st.info("💡 좌측 상단 '>' 버튼을 눌러 라이선스 발급 메뉴를 열 수 있습니다.", icon="ℹ️")

st.markdown("---")

# 사이드바 - 라이선스 발급
with st.sidebar:
    st.header("📝 라이선스 발급")
    
    with st.form("issue_license_form"):
        email = st.text_input("📧 이메일", placeholder="user@example.com")
        device_id = st.text_input("💻 Device ID (선택사항)", placeholder="자동 생성 가능")
        depositor = st.text_input("👤 입금자명 (선택사항)", placeholder="입금자명")
        plan = st.selectbox("🎯 플랜 선택", ["BASIC", "PRO", "DIAMOND", "MASTER"], index=1)
        send_email = st.checkbox("이메일 자동 발송", value=True)
        
        submitted = st.form_submit_button("🚀 라이선스 발급", width="stretch")
        
        if submitted:
            if not email:
                st.error("이메일을 입력해주세요.")
            elif db is None:
                st.error("Firebase 연결 실패")
            else:
                try:
                    # Device ID 생성 (입력되지 않은 경우)
                    if not device_id:
                        from license_core import get_device_id
                        device_id = get_device_id()
                    
                    # 라이선스 키 생성
                    license_key = generate_license(email, device_id)
                    
                    # Firestore에 저장
                    doc_ref = db.collection("licenses").document(email)
                    doc_ref.set({
                        "license_key": license_key,
                        "device_id": device_id,
                        "depositor": depositor,
                        "plan": plan,
                        "created_at": firestore.SERVER_TIMESTAMP
                    })
                    
                    st.success(f"✅ 라이선스 발급 완료!\n\n🔑 {license_key}")
                    
                    # 이메일 발송
                    if send_email and SMTP_EMAIL and SMTP_PASSWORD:
                        if send_license_email(email, license_key, plan):
                            st.success("📧 이메일 발송 완료")
                    
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"발급 실패: {e}")
    
    st.markdown("---")
    
    # 일괄 발급
    st.header("📦 일괄 발급")
    bulk_text = st.text_area(
        "이메일 목록 (한 줄에 하나씩)",
        placeholder="email1@example.com\nemail2@example.com",
        height=100
    )
    bulk_plan = st.selectbox("일괄 플랜", ["BASIC", "PRO", "DIAMOND", "MASTER"], index=1, key="bulk_plan")
    
    if st.button("📦 일괄 발급", width="stretch"):
        if not bulk_text:
            st.error("이메일을 입력해주세요.")
        elif db is None:
            st.error("Firebase 연결 실패")
        else:
            emails = [e.strip() for e in bulk_text.split("\n") if e.strip()]
            success_count = 0
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for idx, email in enumerate(emails):
                try:
                    from license_core import get_device_id
                    device_id = get_device_id()
                    license_key = generate_license(email, device_id)
                    
                    doc_ref = db.collection("licenses").document(email)
                    doc_ref.set({
                        "license_key": license_key,
                        "device_id": device_id,
                        "depositor": "",
                        "plan": bulk_plan,
                        "created_at": firestore.SERVER_TIMESTAMP
                    })
                    
                    success_count += 1
                    status_text.text(f"처리 중: {idx + 1}/{len(emails)}")
                    progress_bar.progress((idx + 1) / len(emails))
                    
                except Exception as e:
                    st.error(f"{email} 발급 실패: {e}")
            
            st.success(f"✅ {success_count}/{len(emails)}개 발급 완료")
            st.rerun()
    
    st.markdown("---")
    
    # SMTP 테스트 섹션
    st.header("📧 SMTP 테스트")
    
    # SMTP 설정 상태 확인
    st.subheader("설정 상태")
    col1, col2 = st.columns(2)
    with col1:
        if SMTP_EMAIL:
            st.success(f"✅ 이메일: {SMTP_EMAIL[:20]}...")
        else:
            st.error("❌ SMTP_EMAIL 미설정")
    
    with col2:
        if SMTP_PASSWORD:
            st.success("✅ 비밀번호 설정됨")
        else:
            st.error("❌ SMTP_PASSWORD 미설정")
    
    st.caption(f"서버: {SMTP_SERVER}:{SMTP_PORT}")
    
    # 테스트 이메일 발송
    st.subheader("테스트 발송")
    with st.form("smtp_test_form"):
        test_email = st.text_input("테스트 이메일 주소", placeholder="test@example.com")
        test_submit = st.form_submit_button("📤 테스트 이메일 발송", width="stretch")
        
        if test_submit:
            if not test_email:
                st.error("이메일 주소를 입력해주세요.")
            elif not SMTP_EMAIL or not SMTP_PASSWORD:
                st.error("SMTP 설정이 완료되지 않았습니다. secrets.toml을 확인하세요.")
            else:
                with st.spinner("이메일 발송 중..."):
                    # 간단한 테스트 이메일 발송
                    try:
                        subject = "[MFLOW] SMTP 테스트 이메일"
                        body = f"""
안녕하세요!

이것은 MFLOW 라이선스 관리 시스템의 SMTP 테스트 이메일입니다.

📧 수신 이메일: {test_email}
⏰ 발송 시간: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

SMTP 설정이 정상적으로 작동하고 있습니다! ✅

감사합니다.
MFLOW 팀
                        """
                        
                        msg = MIMEText(body, "plain", "utf-8")
                        msg["Subject"] = subject
                        msg["From"] = SMTP_EMAIL
                        msg["To"] = test_email
                        
                        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, timeout=10) as server:
                            server.login(SMTP_EMAIL, SMTP_PASSWORD)
                            server.send_message(msg)
                        
                        st.success(f"✅ 테스트 이메일이 {test_email}로 발송되었습니다!")
                        st.info("📬 받은편지함(스팸함 포함)을 확인해주세요.")
                        
                    except smtplib.SMTPAuthenticationError as e:
                        st.error("❌ SMTP 인증 실패")
                        st.caption("Gmail 앱 비밀번호를 확인하세요.")
                        st.caption(f"상세: {str(e)}")
                        
                    except smtplib.SMTPConnectError as e:
                        st.error(f"❌ SMTP 서버 연결 실패")
                        st.caption(f"서버: {SMTP_SERVER}:{SMTP_PORT}")
                        st.caption(f"상세: {str(e)}")
                        
                    except TimeoutError as e:
                        st.error("❌ 연결 시간 초과")
                        st.warning("Streamlit Cloud에서 SMTP outbound가 차단되었을 수 있습니다.")
                        st.info("💡 대안: SendGrid API 사용을 권장합니다.")
                        
                    except Exception as e:
                        error_type = type(e).__name__
                        st.error(f"❌ 이메일 발송 실패 ({error_type})")
                        st.caption(f"상세: {str(e)}")
                        
                        if "timed out" in str(e).lower():
                            st.caption("⚠️ 연결 시간 초과: 방화벽 또는 네트워크 문제")
                        elif "authentication" in str(e).lower():
                            st.caption("⚠️ 인증 실패: Gmail 앱 비밀번호 확인 필요")

# 메인 영역 - 라이선스 목록
st.header("📊 라이선스 목록")

# 검색 및 필터 (모바일 최적화 - 세로 배치)
# 화면 크기에 따라 레이아웃 변경
search_query = st.text_input("🔍 검색 (이메일, Device ID, 입금자명)", value=st.session_state.search_query, key="search_input", placeholder="검색어 입력...")
st.session_state.search_query = search_query

col_filter1, col_filter2 = st.columns([2, 1])
with col_filter1:
    plan_filter = st.selectbox("플랜 필터", ["전체", "BASIC", "PRO", "DIAMOND", "MASTER"])
with col_filter2:
    if st.button("🔄 새로고침", width="stretch"):
        st.rerun()

# 라이선스 로드
licenses = load_licenses()

# 필터링
if search_query:
    licenses = [
        lic for lic in licenses
        if search_query.lower() in lic["email"].lower() or
           search_query.lower() in lic["device_id"].lower() or
           search_query.lower() in lic["depositor"].lower()
    ]

if plan_filter != "전체":
    licenses = [lic for lic in licenses if lic["plan"] == plan_filter]

# 통계 표시 (모바일 최적화 - 컴팩트 배치)
st.markdown("### 📈 통계")

# 모바일에서는 2줄, 데스크톱에서는 1줄
col1, col2 = st.columns(2)
with col1:
    st.metric("📊 총 라이선스", len(licenses))
with col2:
    pro_count = len([l for l in licenses if l["plan"] == "PRO"])
    st.metric("⬆️ PRO", pro_count)

col3, col4 = st.columns(2)
with col3:
    diamond_count = len([l for l in licenses if l["plan"] == "DIAMOND"])
    st.metric("💎 DIAMOND", diamond_count)
with col4:
    master_count = len([l for l in licenses if l["plan"] == "MASTER"])
    st.metric("👑 MASTER", master_count)

st.markdown("---")

# 페이지네이션
items_per_page = st.session_state.items_per_page
total_pages = (len(licenses) + items_per_page - 1) // items_per_page if licenses else 1
current_page = st.session_state.page

# 페이지 범위 조정
if current_page > total_pages:
    current_page = total_pages
if current_page < 1:
    current_page = 1
st.session_state.page = current_page

start_idx = (current_page - 1) * items_per_page
end_idx = min(start_idx + items_per_page, len(licenses))
page_licenses = licenses[start_idx:end_idx]

# 액션 버튼 (모바일 최적화 - 2줄 배치)
st.markdown("### 🔧 일괄 작업")
st.caption("선택된 라이선스에 대해 일괄 작업을 수행할 수 있습니다.")

# 첫 번째 줄: 플랜 변경 버튼
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("⬆️ PRO", width="stretch", key="btn_pro"):
        if st.session_state.selected_emails:
            success_count = 0
            email_sent_count = 0
            
            for email in st.session_state.selected_emails:
                try:
                    # 기존 플랜 정보 가져오기
                    doc = db.collection("licenses").document(email).get()
                    if doc.exists:
                        old_plan = doc.to_dict().get("plan", "BASIC")
                        license_key = doc.to_dict().get("license_key", "")
                        
                        # 플랜 변경
                        db.collection("licenses").document(email).update({"plan": "PRO"})
                        success_count += 1
                        
                        # 이메일 발송 (SMTP 설정이 있는 경우)
                        if SMTP_EMAIL and SMTP_PASSWORD and old_plan != "PRO":
                            if send_plan_change_email(email, old_plan, "PRO", license_key):
                                email_sent_count += 1
                except:
                    pass
            
            if email_sent_count > 0:
                st.success(f"✅ {success_count}개 PRO로 변경 완료 (이메일 {email_sent_count}개 발송)")
            else:
                st.success(f"✅ {success_count}개 PRO로 변경 완료")
            
            st.session_state.selected_emails.clear()
            st.rerun()
        else:
            st.warning("선택된 라이선스가 없습니다.")

with col2:
    if st.button("💎 DIAMOND", width="stretch", key="btn_diamond"):
        if st.session_state.selected_emails:
            success_count = 0
            email_sent_count = 0
            
            for email in st.session_state.selected_emails:
                try:
                    # 기존 플랜 정보 가져오기
                    doc = db.collection("licenses").document(email).get()
                    if doc.exists:
                        old_plan = doc.to_dict().get("plan", "BASIC")
                        license_key = doc.to_dict().get("license_key", "")
                        
                        # 플랜 변경
                        db.collection("licenses").document(email).update({"plan": "DIAMOND"})
                        success_count += 1
                        
                        # 이메일 발송 (SMTP 설정이 있는 경우)
                        if SMTP_EMAIL and SMTP_PASSWORD and old_plan != "DIAMOND":
                            if send_plan_change_email(email, old_plan, "DIAMOND", license_key):
                                email_sent_count += 1
                except:
                    pass
            
            if email_sent_count > 0:
                st.success(f"✅ {success_count}개 DIAMOND로 변경 완료 (이메일 {email_sent_count}개 발송)")
            else:
                st.success(f"✅ {success_count}개 DIAMOND로 변경 완료")
            
            st.session_state.selected_emails.clear()
            st.rerun()
        else:
            st.warning("선택된 라이선스가 없습니다.")

with col3:
    if st.button("👑 MASTER", width="stretch", key="btn_master"):
        if st.session_state.selected_emails:
            success_count = 0
            email_sent_count = 0
            
            for email in st.session_state.selected_emails:
                try:
                    # 기존 플랜 정보 가져오기
                    doc = db.collection("licenses").document(email).get()
                    if doc.exists:
                        old_plan = doc.to_dict().get("plan", "BASIC")
                        license_key = doc.to_dict().get("license_key", "")
                        
                        # 플랜 변경
                        db.collection("licenses").document(email).update({"plan": "MASTER"})
                        success_count += 1
                        
                        # 이메일 발송 (SMTP 설정이 있는 경우)
                        if SMTP_EMAIL and SMTP_PASSWORD and old_plan != "MASTER":
                            if send_plan_change_email(email, old_plan, "MASTER", license_key):
                                email_sent_count += 1
                except:
                    pass
            
            if email_sent_count > 0:
                st.success(f"✅ {success_count}개 MASTER로 변경 완료 (이메일 {email_sent_count}개 발송)")
            else:
                st.success(f"✅ {success_count}개 MASTER로 변경 완료")
            
            st.session_state.selected_emails.clear()
            st.rerun()
        else:
            st.warning("선택된 라이선스가 없습니다.")

# 두 번째 줄: 삭제, 선택 해제, Excel 버튼
col4, col5, col6 = st.columns(3)
with col4:
    if st.button("🗑️ 삭제", width="stretch", key="btn_delete"):
        if st.session_state.selected_emails:
            for email in st.session_state.selected_emails:
                try:
                    db.collection("licenses").document(email).delete()
                except:
                    pass
            st.success(f"{len(st.session_state.selected_emails)}개 삭제 완료")
            st.session_state.selected_emails.clear()
            st.rerun()
        else:
            st.warning("선택된 라이선스가 없습니다.")

with col5:
    if st.button("☐ 선택 해제", width="stretch", key="btn_clear"):
        st.session_state.selected_emails.clear()
        st.rerun()

with col6:
    if st.button("💾 Excel", width="stretch", key="btn_excel"):
        if licenses:
            df = pd.DataFrame(licenses)
            # 선택된 컬럼만 내보내기
            df = df[["email", "device_id", "depositor", "plan", "license_key", "created_at"]]
            
            # Excel 파일로 저장
            filename = f"licenses_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            df.to_excel(filename, index=False, engine='openpyxl')
            st.success(f"✅ {filename} 저장 완료")
        else:
            st.warning("내보낼 데이터가 없습니다.")

st.markdown("---")

# 라이선스 테이블
if page_licenses:
    # 데이터프레임 생성
    df = pd.DataFrame(page_licenses)
    
    # 체크박스 컬럼 추가
    df.insert(0, "선택", False)
    
    # 선택 상태 복원
    for idx, row in df.iterrows():
        if row["email"] in st.session_state.selected_emails:
            df.at[idx, "선택"] = True
    
    # 데이터 에디터 (체크박스 포함, 모바일 최적화)
    edited_df = st.data_editor(
        df,
        column_config={
            "선택": st.column_config.CheckboxColumn(
                "✓",
                help="선택하여 일괄 작업 수행",
                default=False,
                width="small"
            ),
            "email": st.column_config.TextColumn(
                "📧 Email",
                width="medium",
                help="이메일 주소"
            ),
            "device_id": st.column_config.TextColumn(
                "💻 Device",
                width="small",
                help="Device ID"
            ),
            "depositor": st.column_config.TextColumn(
                "👤 입금자",
                width="small",
                help="입금자명"
            ),
            "plan": st.column_config.TextColumn(
                "🎯 Plan",
                width="small",
                help="플랜"
            ),
            "license_key": st.column_config.TextColumn(
                "🔑 License Key",
                width="medium",
                help="라이선스 키"
            ),
            "created_at": st.column_config.TextColumn(
                "📅 생성일",
                width="small",
                help="생성일시"
            )
        },
        hide_index=True,
        width="stretch",
        disabled=["email", "device_id", "depositor", "plan", "license_key", "created_at"],
        height=400  # 고정 높이로 스크롤 가능
    )
    
    # 선택 상태 업데이트
    st.session_state.selected_emails = set(
        edited_df[edited_df["선택"] == True]["email"].tolist()
    )
    
    # 페이지네이션 컨트롤 (모바일 최적화)
    st.markdown("---")
    
    # 페이지 정보 표시
    st.markdown(f"<div style='text-align: center; color: #94a3b8; font-size: 1.1rem; margin-bottom: 1rem;'>페이지: <strong>{current_page}</strong> / {total_pages}</div>", unsafe_allow_html=True)
    
    # 페이지네이션 버튼 (2줄 배치)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⏮ 첫 페이지", width="stretch", key="page_first"):
            st.session_state.page = 1
            st.rerun()
    with col2:
        if st.button("마지막 페이지 ⏭", width="stretch", key="page_last"):
            st.session_state.page = total_pages
            st.rerun()
    
    col3, col4 = st.columns(2)
    with col3:
        if st.button("◀ 이전", width="stretch", key="page_prev", disabled=(st.session_state.page <= 1)):
            if st.session_state.page > 1:
                st.session_state.page -= 1
                st.rerun()
    with col4:
        if st.button("다음 ▶", width="stretch", key="page_next", disabled=(st.session_state.page >= total_pages)):
            if st.session_state.page < total_pages:
                st.session_state.page += 1
                st.rerun()
    
    # 선택된 항목 표시
    if st.session_state.selected_emails:
        st.info(f"✅ {len(st.session_state.selected_emails)}개 선택됨")

else:
    st.info("라이선스가 없습니다. 사이드바에서 라이선스를 발급하세요.")

# 푸터
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #94a3b8; padding: 20px;'>
    <p>MFLOW License Manager v2.0 (Streamlit)</p>
    <p>© 2025 MFLOW. All rights reserved.</p>
</div>
""", unsafe_allow_html=True)

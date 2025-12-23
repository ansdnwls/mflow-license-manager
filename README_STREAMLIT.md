# MFLOW 라이선스 관리 웹 대시보드 (Streamlit)

## 📱 모바일 최적화 버전

PyQt5 데스크톱 애플리케이션을 Streamlit 웹 애플리케이션으로 변환한 버전입니다.

## ✨ 주요 기능

### 1. 라이선스 관리
- ✅ 라이선스 발급 (단일/일괄)
- ✅ 라이선스 조회 및 검색
- ✅ 플랜 변경 (PRO, DIAMOND, MASTER)
- ✅ 라이선스 삭제
- ✅ Excel 내보내기

### 2. Firebase 연동
- ✅ Firestore 데이터베이스 연동
- ✅ 실시간 데이터 동기화
- ✅ 자동 타임스탬프

### 3. 이메일 발송
- ✅ 라이선스 키 자동 발송
- ✅ SMTP 설정 지원

### 4. 모바일 최적화
- ✅ 반응형 디자인 (데스크톱, 태블릿, 모바일)
- ✅ 터치 친화적 UI (최소 44px 터치 영역)
- ✅ 가로/세로 스크롤 최적화
- ✅ iOS 자동 줌 방지 (16px 폰트)
- ✅ 부드러운 스크롤 (-webkit-overflow-scrolling)
- ✅ PWA 지원 (앱처럼 설치 가능)

## 🚀 설치 및 실행

### 1. 가상환경 활성화
```powershell
cd c:\Users\y2k_w\projects\mflow-license-manager
.\venv\Scripts\Activate.ps1
```

### 2. 필요한 패키지 설치 (이미 완료)
```powershell
pip install streamlit pandas openpyxl firebase-admin python-dotenv
```

### 3. 환경변수 설정
`.env` 파일에 다음 내용 추가:
```env
FIREBASE_CREDENTIALS_PATH=mflow_admin.json
SMTP_EMAIL=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=465
```

### 4. 실행
```powershell
streamlit run streamlit_app.py
```

또는 가상환경 Python 직접 사용:
```powershell
.\venv\Scripts\python.exe -m streamlit run streamlit_app.py
```

## 📱 모바일 접속

### 로컬 네트워크 접속
1. 실행 시 표시되는 `Network URL` 확인
2. 같은 Wi-Fi에 연결된 모바일 기기에서 해당 URL 접속
3. 예: `http://192.168.0.10:8501`

### 외부 접속 (선택사항)
```powershell
streamlit run streamlit_app.py --server.address 0.0.0.0
```

### PWA로 설치 (모바일)
1. 모바일 브라우저에서 접속
2. Chrome: 메뉴 → "홈 화면에 추가"
3. Safari: 공유 → "홈 화면에 추가"
4. 앱처럼 사용 가능!

## 🎨 모바일 최적화 상세

### 반응형 브레이크포인트
- **데스크톱**: 769px 이상
- **태블릿**: 481px ~ 768px
- **모바일**: 480px 이하

### 터치 최적화
- 모든 버튼: 최소 44px 높이 (터치 권장 크기)
- 체크박스: 최소 44px 크기
- 입력 필드: 최소 44px 높이
- 터치 피드백: 클릭 시 투명도 변경

### 폰트 크기
- 제목: `clamp(1.5rem, 5vw, 2.5rem)` (반응형)
- 본문: 14px (데스크톱), 12px (모바일)
- 입력 필드: 16px (iOS 자동 줌 방지)

### 레이아웃
- 데스크톱: 6열 버튼 배치
- 모바일: 3열 × 2줄 버튼 배치
- 통계: 5열 → 1+4열 배치
- 페이지네이션: 5열 → 2×2 배치

### 스크롤
- 가로 스크롤: 테이블 자동 스크롤
- iOS 부드러운 스크롤: `-webkit-overflow-scrolling: touch`
- 커스텀 스크롤바: 8px 너비, 파란색

## 🔧 설정 파일

### `.streamlit/config.toml`
```toml
[theme]
primaryColor = "#3b82f6"
backgroundColor = "#0f172a"
secondaryBackgroundColor = "#1e293b"
textColor = "#f1f5f9"

[server]
headless = true
port = 8501
enableCORS = false
```

## 📊 화면 구성

### 메인 화면
1. **헤더**: 타이틀 + 메뉴 버튼
2. **통계**: 총 라이선스 + 플랜별 통계
3. **검색/필터**: 검색창 + 플랜 필터
4. **일괄 작업**: 플랜 변경, 삭제, Excel 버튼
5. **테이블**: 라이선스 목록 (페이지네이션)
6. **페이지네이션**: 첫/이전/다음/마지막 버튼

### 사이드바
1. **라이선스 발급**: 단일 발급 폼
2. **일괄 발급**: 여러 이메일 동시 발급

## 🌐 브라우저 지원

- ✅ Chrome (데스크톱/모바일)
- ✅ Safari (iOS)
- ✅ Firefox (데스크톱/모바일)
- ✅ Edge (데스크톱)
- ✅ Samsung Internet

## 🔒 보안

- XSRF 보호 활성화
- CORS 비활성화 (로컬 네트워크만)
- Firebase 인증 파일 보호 (.gitignore)
- 환경변수로 민감 정보 관리

## 📝 TODO

- [ ] 다크/라이트 모드 토글
- [ ] 라이선스 만료일 관리
- [ ] 사용자 권한 관리
- [ ] 실시간 알림
- [ ] 차트/그래프 추가

## 🐛 문제 해결

### Firebase 연결 실패
```
⚠️ Firebase 초기화 실패
```
→ `mflow_admin.json` 파일 경로 확인
→ `.env` 파일의 `FIREBASE_CREDENTIALS_PATH` 확인

### 모바일에서 레이아웃 깨짐
→ 브라우저 캐시 삭제
→ 강력 새로고침 (Ctrl + Shift + R)

### 터치가 반응하지 않음
→ 버튼 크기 확인 (최소 44px)
→ CSS 충돌 확인

## 📞 지원

문제가 발생하면 다음을 확인하세요:
1. Python 버전: 3.11+
2. Streamlit 버전: 1.52+
3. Firebase Admin SDK 설치 확인
4. 환경변수 설정 확인

## 📄 라이선스

© 2025 MFLOW. All rights reserved.

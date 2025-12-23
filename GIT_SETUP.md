# Git 저장소 설정 가이드

## 🔧 현재 상태

원격 레포지토리 URL이 예시로 설정되어 있습니다. 실제 GitHub 레포지토리를 생성하고 연결해야 합니다.

## 📝 단계별 설정

### 1단계: GitHub 레포지토리 생성

1. **GitHub 접속**
   - https://github.com 접속
   - 로그인

2. **새 레포지토리 생성**
   - 우측 상단 "+" 버튼 클릭
   - "New repository" 선택
   - Repository name: `mflow-license-manager` (또는 원하는 이름)
   - Description: "MFLOW 라이선스 관리 시스템"
   - Public 또는 Private 선택
   - **"Initialize this repository with a README" 체크 해제** (이미 로컬에 파일이 있으므로)
   - "Create repository" 클릭

3. **레포지토리 URL 복사**
   - 생성된 레포지토리 페이지에서
   - "Code" 버튼 클릭
   - HTTPS URL 복사 (예: `https://github.com/your-username/mflow-license-manager.git`)

### 2단계: 로컬 Git 설정

#### 옵션 A: 기존 원격 제거 후 새로 추가 (권장)

```powershell
cd c:\Users\y2k_w\projects\mflow-license-manager

# 기존 원격 제거
git remote remove origin

# 실제 GitHub 레포지토리 URL로 추가 (your-username을 실제 사용자명으로 변경)
git remote add origin https://github.com/your-username/mflow-license-manager.git

# 확인
git remote -v
```

#### 옵션 B: 원격 URL 변경

```powershell
cd c:\Users\y2k_w\projects\mflow-license-manager

# 원격 URL 변경 (your-username을 실제 사용자명으로 변경)
git remote set-url origin https://github.com/your-username/mflow-license-manager.git

# 확인
git remote -v
```

### 3단계: 코드 푸시

```powershell
# 현재 브랜치 확인
git branch

# main 브랜치로 전환 (필요시)
git checkout -b main

# 모든 파일 추가 (secrets.toml, mflow_admin.json은 자동 제외)
git add .

# 커밋 (아직 안 했다면)
git commit -m "Initial commit: MFLOW License Manager"

# 푸시
git push -u origin main
```

### 4단계: 확인

```powershell
# 원격 레포지토리 확인
git remote -v

# 상태 확인
git status
```

## ⚠️ 주의사항

### 보안 파일 확인

푸시 전에 보안 파일이 포함되지 않았는지 확인:

```powershell
git status
```

다음 파일들이 표시되면 안 됨:
- `.streamlit/secrets.toml`
- `mflow_admin.json`
- `.env`

### 이미 커밋된 경우

만약 보안 파일이 이미 커밋되었다면:

```powershell
# Git 캐시에서 제거 (파일은 로컬에 유지)
git rm --cached .streamlit/secrets.toml
git rm --cached mflow_admin.json
git rm --cached .env

# .gitignore 확인
cat .gitignore

# 다시 커밋
git add .
git commit -m "Remove sensitive files from Git"

# 푸시
git push origin main
```

## 🔍 문제 해결

### "Repository not found" 에러

- GitHub 레포지토리가 실제로 생성되었는지 확인
- 레포지토리 이름이 정확한지 확인
- GitHub 사용자명이 정확한지 확인
- 레포지토리가 Private인 경우 인증 필요

### "Permission denied" 에러

- GitHub 인증 필요
- Personal Access Token 사용 또는 SSH 키 설정

### "Authentication failed" 에러

```powershell
# GitHub Personal Access Token 생성 필요
# Settings → Developer settings → Personal access tokens → Tokens (classic)
# 또는 Git Credential Manager 사용
```

## ✅ 완료 확인

성공적으로 푸시되면:
1. GitHub 레포지토리 페이지에서 파일 확인
2. Streamlit Cloud에서 레포지토리 선택 가능
3. 배포 진행 가능

## 📞 다음 단계

Git 설정이 완료되면:
1. [DEPLOY_CHECKLIST.md](DEPLOY_CHECKLIST.md) 확인
2. Streamlit Cloud 배포 진행
3. Secrets 설정

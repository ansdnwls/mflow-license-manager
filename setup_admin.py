"""
관리자 비밀번호 해시 생성 도구

사용법:
    python setup_admin.py

이 스크립트는 관리자 비밀번호를 입력받아 SHA256 해시를 생성합니다.
생성된 해시를 .env 파일의 ADMIN_PASSWORD_HASH에 추가하세요.
"""

import hashlib
import getpass

def hash_password(password: str) -> str:
    """비밀번호를 SHA256으로 해싱"""
    return hashlib.sha256(password.encode()).hexdigest()

def main():
    print("=" * 60)
    print("MFLOW 라이선스 관리 - 관리자 비밀번호 설정")
    print("=" * 60)
    print()
    
    # 사용자명 입력
    username = input("관리자 사용자명 (기본값: admin): ").strip()
    if not username:
        username = "admin"
    
    # 비밀번호 입력
    print("\n비밀번호 요구사항:")
    print("- 최소 8자 이상")
    print("- 영문, 숫자 조합 권장")
    print()
    print("⚠️  주의: PowerShell에서는 비밀번호가 화면에 표시됩니다.")
    print()
    
    while True:
        # PowerShell에서 getpass가 제대로 작동하지 않을 수 있으므로 input 사용
        password = input("관리자 비밀번호: ").strip()
        
        if not password:
            print("❌ 비밀번호를 입력해주세요.")
            continue
        
        if len(password) < 8:
            print("❌ 비밀번호는 최소 8자 이상이어야 합니다.")
            continue
        
        password_confirm = input("비밀번호 확인: ").strip()
        
        if not password:
            print("❌ 비밀번호를 입력해주세요.")
            continue
        
        if len(password) < 8:
            print("❌ 비밀번호는 최소 8자 이상이어야 합니다.")
            continue
        
        if password != password_confirm:
            print("❌ 비밀번호가 일치하지 않습니다. 다시 입력해주세요.")
            print()
            continue
        
        break
    
    # 해시 생성
    password_hash = hash_password(password)
    
    print("\n" + "=" * 60)
    print("✅ 비밀번호 해시 생성 완료!")
    print("=" * 60)
    print()
    print("다음 내용을 Streamlit Cloud Secrets 또는 .env 파일에 추가하세요:")
    print()
    print("-" * 60)
    print(f"ADMIN_USERNAME = \"{username}\"")
    print(f"ADMIN_PASSWORD_HASH = \"{password_hash}\"")
    print("-" * 60)
    print()
    print("⚠️  주의사항:")
    print("1. .env 파일은 절대 Git에 커밋하지 마세요!")
    print("2. 비밀번호 해시는 안전하게 보관하세요.")
    print("3. 정기적으로 비밀번호를 변경하세요.")
    print()
    print("📝 Streamlit Cloud 배포 시:")
    print("   위 내용을 Streamlit Cloud → Settings → Secrets에 추가하세요.")
    print()
    print("설정 완료 후 Streamlit 앱을 재시작하세요.")
    print()

if __name__ == "__main__":
    main()

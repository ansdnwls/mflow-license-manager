"""
Firebase 인증 파일을 Streamlit Secrets TOML 형식으로 변환하는 도구

사용법:
    python convert_firebase_to_toml.py
"""

import json
import os

def convert_firebase_to_toml():
    """mflow_admin.json을 TOML 형식으로 변환"""
    firebase_file = "mflow_admin.json"
    
    if not os.path.exists(firebase_file):
        print(f"❌ {firebase_file} 파일을 찾을 수 없습니다.")
        print(f"   현재 디렉토리: {os.getcwd()}")
        return
    
    try:
        with open(firebase_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print("=" * 70)
        print("Streamlit Cloud Secrets에 붙여넣을 Firebase 설정")
        print("=" * 70)
        print()
        print("[firebase]")
        
        for key, value in data.items():
            # private_key는 특별 처리 (줄바꿈 유지)
            if key == "private_key":
                # 이미 \n이 포함되어 있으면 그대로 사용
                if "\\n" in str(value):
                    print(f'{key} = "{value}"')
                else:
                    # 실제 줄바꿈을 \n으로 변환
                    value_str = str(value).replace("\n", "\\n")
                    print(f'{key} = "{value_str}"')
            else:
                # 나머지 필드는 그대로
                print(f'{key} = "{value}"')
        
        print()
        print("=" * 70)
        print("✅ 위 내용을 Streamlit Cloud → Settings → Secrets에 붙여넣으세요!")
        print("=" * 70)
        print()
        print("⚠️  주의사항:")
        print("1. private_key에 \\n이 포함되어 있는지 확인")
        print("2. 모든 필드가 정확히 입력되었는지 확인")
        print("3. 따옴표가 올바르게 입력되었는지 확인")
        
    except json.JSONDecodeError as e:
        print(f"❌ JSON 파싱 오류: {e}")
    except Exception as e:
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    convert_firebase_to_toml()

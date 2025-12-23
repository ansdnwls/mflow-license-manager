"""
테스트용 가상 데이터 생성 및 삭제 스크립트
"""
import os
import sys
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

import firebase_admin
from firebase_admin import credentials, firestore
from license_core import generate_license

# Firebase 초기화
FIREBASE_CREDENTIALS_PATH = os.getenv("FIREBASE_CREDENTIALS_PATH", "mflow_admin.json")

try:
    if not os.path.exists(FIREBASE_CREDENTIALS_PATH):
        raise FileNotFoundError(f"Firebase 인증 파일을 찾을 수 없습니다: {FIREBASE_CREDENTIALS_PATH}")
    
    cred = credentials.Certificate(FIREBASE_CREDENTIALS_PATH)
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    print("✅ Firebase initialized successfully")
except Exception as e:
    print(f"❌ Firebase 초기화 실패: {e}")
    sys.exit(1)

# 테스트용 가상 데이터
TEST_DATA = [
    {"email": "test.user1@example.com", "name": "김철수", "device_id": "DEV001"},
    {"email": "test.user2@example.com", "name": "이영희", "device_id": "DEV002"},
    {"email": "test.user3@example.com", "name": "박민수", "device_id": "DEV003"},
    {"email": "test.user4@example.com", "name": "최지영", "device_id": "DEV004"},
    {"email": "test.user5@example.com", "name": "정대현", "device_id": "DEV005"},
    {"email": "test.user6@example.com", "name": "강수진", "device_id": "DEV006"},
    {"email": "test.user7@example.com", "name": "윤성호", "device_id": "DEV007"},
    {"email": "test.user8@example.com", "name": "장미라", "device_id": "DEV008"},
    {"email": "test.user9@example.com", "name": "임동욱", "device_id": "DEV009"},
    {"email": "test.user10@example.com", "name": "한소연", "device_id": "DEV010"},
]

PLANS = ["BASIC", "PRO", "DIAMOND", "MASTER"]


def create_test_data():
    """테스트용 라이센스 데이터 생성"""
    print("\n📝 테스트 데이터 생성 시작...\n")
    
    created_count = 0
    for i, user_data in enumerate(TEST_DATA):
        try:
            email = user_data["email"]
            device_id = user_data["device_id"]
            depositor = user_data["name"]
            
            # 플랜을 순환하여 다양하게 생성
            plan = PLANS[i % len(PLANS)]
            
            # 라이센스 키 생성
            license_key = generate_license(email, device_id)
            
            # Firestore에 저장
            license_data = {
                "email": email,
                "device_id": device_id,
                "depositor": depositor,
                "plan": plan,
                "license_key": license_key,
                "created_at": firestore.SERVER_TIMESTAMP
            }
            
            db.collection("licenses").document(email).set(license_data)
            
            print(f"✅ [{i+1}/10] {email} ({depositor}) - {plan} 플랜 생성 완료")
            print(f"   Device ID: {device_id}")
            print(f"   License Key: {license_key}\n")
            
            created_count += 1
            
        except Exception as e:
            print(f"❌ [{i+1}/10] {user_data['email']} 생성 실패: {e}\n")
    
    print(f"\n🎉 총 {created_count}개의 테스트 데이터가 생성되었습니다!")
    return created_count


def delete_test_data():
    """테스트용 라이센스 데이터 삭제"""
    print("\n🗑️ 테스트 데이터 삭제 시작...\n")
    
    deleted_count = 0
    failed_count = 0
    
    for i, user_data in enumerate(TEST_DATA):
        try:
            email = user_data["email"]
            db.collection("licenses").document(email).delete()
            print(f"✅ [{i+1}/10] {email} 삭제 완료")
            deleted_count += 1
        except Exception as e:
            print(f"❌ [{i+1}/10] {email} 삭제 실패: {e}")
            failed_count += 1
    
    print(f"\n📊 삭제 결과:")
    print(f"   ✅ 성공: {deleted_count}개")
    if failed_count > 0:
        print(f"   ❌ 실패: {failed_count}개")
    else:
        print(f"   🎉 모든 테스트 데이터가 삭제되었습니다!")
    
    return deleted_count, failed_count


def list_test_data():
    """테스트 데이터 목록 확인"""
    print("\n📋 테스트 데이터 목록:\n")
    
    for i, user_data in enumerate(TEST_DATA):
        try:
            email = user_data["email"]
            doc_ref = db.collection("licenses").document(email)
            doc = doc_ref.get()
            
            if doc.exists:
                data = doc.to_dict()
                print(f"[{i+1}] {user_data['name']} ({email})")
                print(f"     Plan: {data.get('plan', 'N/A')}")
                print(f"     Device ID: {data.get('device_id', 'N/A')}")
                print(f"     License Key: {data.get('license_key', 'N/A')[:20]}...")
                print()
            else:
                print(f"[{i+1}] {user_data['name']} ({email}) - 데이터 없음\n")
        except Exception as e:
            print(f"[{i+1}] {user_data['email']} - 확인 실패: {e}\n")


if __name__ == "__main__":
    print("=" * 60)
    print("🧪 MFLOW 라이센스 관리 테스트 데이터 생성기")
    print("=" * 60)
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "create":
            create_test_data()
        elif command == "delete":
            delete_test_data()
        elif command == "list":
            list_test_data()
        else:
            print(f"\n❌ 알 수 없는 명령어: {command}")
            print("\n사용법:")
            print("  python test_data_generator.py create  - 테스트 데이터 생성")
            print("  python test_data_generator.py delete  - 테스트 데이터 삭제")
            print("  python test_data_generator.py list    - 테스트 데이터 목록 확인")
    else:
        print("\n사용법:")
        print("  python test_data_generator.py create  - 테스트 데이터 생성")
        print("  python test_data_generator.py delete  - 테스트 데이터 삭제")
        print("  python test_data_generator.py list    - 테스트 데이터 목록 확인")
        print("\n또는 대화형 모드:")
        print("  python test_data_generator.py")
        
        print("\n" + "=" * 60)
        print("\n선택하세요:")
        print("1. 테스트 데이터 생성")
        print("2. 테스트 데이터 삭제")
        print("3. 테스트 데이터 목록 확인")
        print("4. 종료")
        
        choice = input("\n번호를 입력하세요 (1-4): ").strip()
        
        if choice == "1":
            create_test_data()
        elif choice == "2":
            confirm = input("\n⚠️ 정말로 모든 테스트 데이터를 삭제하시겠습니까? (yes/no): ").strip().lower()
            if confirm == "yes":
                delete_test_data()
            else:
                print("❌ 삭제가 취소되었습니다.")
        elif choice == "3":
            list_test_data()
        elif choice == "4":
            print("👋 종료합니다.")
        else:
            print("❌ 잘못된 선택입니다.")


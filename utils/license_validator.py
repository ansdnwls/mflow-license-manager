import sqlite3
import json
import os
import platform
import uuid
from datetime import datetime, timedelta

class LicenseValidator:
    def __init__(self):
        # 기존 설정 유지
        self.license_limits = {
            '베이직': {'tabs': 1, 'slots': 20},
            '사파이어': {'tabs': 3, 'slots': 20},
            '다이아': {'tabs': 5, 'slots': 20},
            '프리미엄': {'tabs': float('inf'), 'slots': float('inf')}
        }
        self.trial_period = 15  # 체험판 기간 (일)

        # AppData 경로 설정 추가
        app_data_path = os.path.join(os.getenv('APPDATA'), 'Mflow')
        if not os.path.exists(app_data_path):
            os.makedirs(app_data_path)
            
        # 파일 경로 설정
        self.db_path = os.path.join(app_data_path, 'licenses.db')
        self.settings_path = os.path.join(app_data_path, 'user_license.json')
        
    def get_device_id(self):
        """현재 PC의 고유 식별자 생성"""
        try:
            system_info = platform.uname()
            machine_id = f"{system_info.node}-{system_info.processor}"
            return str(uuid.uuid5(uuid.NAMESPACE_DNS, machine_id))
        except:
            return str(uuid.uuid4())  # 실패시 랜덤 ID 생성
            
    def validate_license(self, email, license_key):
        """라이센스 유효성 검증"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 라이센스 조회
            cursor.execute("""
                SELECT l.type, l.expiry_date, l.status
                FROM licenses l
                JOIN users u ON l.user_id = u.id
                WHERE u.email = ? AND l.license_key = ?
            """, (email, license_key))
            
            result = cursor.fetchone()
            
            if not result:
                return False, "유효하지 않은 라이센스입니다."
                
            license_type, expiry_date, status = result
            
            # 라이센스 상태 확인
            if status != 'active':
                return False, "비활성화된 라이센스입니다."
                
            # 라이센스 만료 확인
            if expiry_date:
                expiry = datetime.strptime(expiry_date, '%Y-%m-%d').date()
                if expiry < datetime.now().date():
                    return False, "만료된 라이센스입니다."
            
            # 디바이스 정보 확인
            device_id = self.get_device_id()
            cursor.execute("""
                SELECT COUNT(*) FROM devices 
                WHERE license_id = (
                    SELECT id FROM licenses 
                    WHERE license_key = ?
                )
            """, (license_key,))
            
            device_count = cursor.fetchone()[0]
            if device_count > 0:
                cursor.execute("""
                    SELECT device_id FROM devices 
                    WHERE license_id = (
                        SELECT id FROM licenses 
                        WHERE license_key = ?
                    )
                """, (license_key,))
                registered_device = cursor.fetchone()[0]
                if registered_device != device_id:
                    return False, "이미 다른 PC에서 사용 중인 라이센스입니다."
            
            # 새 디바이스 등록
            cursor.execute("""
                INSERT OR REPLACE INTO devices (
                    license_id, device_id, device_name, last_active
                ) VALUES (
                    (SELECT id FROM licenses WHERE license_key = ?),
                    ?, ?, CURRENT_TIMESTAMP
                )
            """, (license_key, device_id, platform.node()))
            
            conn.commit()
            
            # 라이센스 정보 저장
            self.save_license_info(email, license_key, license_type, expiry_date)
            
            return True, "라이센스가 성공적으로 등록되었습니다."
            
        except Exception as e:
            return False, f"라이센스 검증 중 오류 발생: {str(e)}"
        finally:
            conn.close()
            
    def save_license_info(self, email, license_key, license_type, expiry_date):
        """라이센스 정보 저장"""
        license_info = {
            'email': email,
            'license_key': license_key,
            'type': license_type,
            'expiry_date': expiry_date,
            'device_id': self.get_device_id(),
            'registered_date': datetime.now().strftime('%Y-%m-%d')
        }
        
        with open(self.settings_path, 'w', encoding='utf-8') as f:
            json.dump(license_info, f, ensure_ascii=False, indent=4)
            
    def load_license_info(self):
        """저장된 라이센스 정보 로드"""
        try:
            if os.path.exists(self.settings_path):
                with open(self.settings_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return self.create_trial_license()  # 라이센스 없으면 체험판 생성
        except:
            return self.create_trial_license()
            
    def create_trial_license(self):
        """체험판 라이센스 생성"""
        trial_start = datetime.now()
        trial_end = trial_start + timedelta(days=self.trial_period)
        
        trial_info = {
            'email': 'trial@user',
            'license_key': 'TRIAL-LICENSE',
            'type': '베이직',
            'is_trial': True,
            'trial_start': trial_start.strftime('%Y-%m-%d'),
            'expiry_date': trial_end.strftime('%Y-%m-%d'),
            'device_id': self.get_device_id()
        }
        
        with open(self.settings_path, 'w', encoding='utf-8') as f:
            json.dump(trial_info, f, ensure_ascii=False, indent=4)
            
        return trial_info
            
    def get_license_limits(self, license_type):
        """라이센스 유형별 제한사항 반환"""
        return self.license_limits.get(license_type, {'tabs': 1, 'slots': 20})

    def check_tab_limit(self, license_type, current_tabs):
        """탭 개수 제한 확인"""
        limits = self.get_license_limits(license_type)
        return current_tabs < limits['tabs']

    def check_slot_limit(self, license_type, current_slots):
        """슬롯 개수 제한 확인"""
        limits = self.get_license_limits(license_type)
        return current_slots < limits['slots']
        
    def get_license_status(self):
        """현재 라이센스 상태 정보 반환"""
        license_info = self.load_license_info()
        
        if not license_info:
            return "체험판", "라이센스 정보 없음"
            
        is_trial = license_info.get('is_trial', False)
        expiry_date = datetime.strptime(license_info['expiry_date'], '%Y-%m-%d').date()
        days_left = (expiry_date - datetime.now().date()).days
        
        if is_trial:
            return "체험판", f"{days_left}일 남음 (탭 1개, 슬롯 20개)"
        else:
            license_type = license_info['type']
            limits = self.get_license_limits(license_type)
            return license_type, f"만료일: {license_info['expiry_date']} (탭 {limits['tabs']}개, 슬롯 {limits['slots']}개)"
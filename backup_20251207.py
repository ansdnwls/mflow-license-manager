import sys
import os
import smtplib
from email.mime.text import MIMEText

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel,
    QLineEdit, QPushButton, QMessageBox, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QHeaderView, QPlainTextEdit, QComboBox
)
from PyQt5.QtCore import Qt

import firebase_admin
from firebase_admin import credentials, firestore

from license_core import generate_license  # 핵심
# license_core.py 파일이 같은 폴더에 있어야 함

# Firebase Admin SDK 초기화
try:
    cred = credentials.Certificate(
        os.path.join(os.getcwd(), "mflow_admin.json")
    )
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    print("✅ Firebase initialized successfully")
except Exception as e:
    db = None
    print(f"⚠ Firebase 초기화 실패: {e}")
    QMessageBox.critical(None, "오류", f"Firebase 초기화 실패!\n{e}\n\nmflow_admin.json 파일을 확인하세요.")
SMTP_EMAIL = "800308wj@gmail.com"  # 발신자 이메일
SMTP_PASSWORD = "iyav dbmf qoot rsnt"  # 앱 비밀번호 (절대 일반 PW 아님)
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465


class LicenseManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MFLOW License Manager (Firestore)")
        self.setFixedSize(600, 400)

        if db is None:
            QMessageBox.critical(self, "오류", "Firebase 초기화 실패!\n프로그램을 종료합니다.")
            sys.exit(1)

        self.initUI()
        self.load_table()



    def initUI(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # --- 단일 발급 영역 ---
        self.email_edit = QLineEdit()
        self.email_edit.setPlaceholderText("이메일 입력")
        layout.addWidget(self.email_edit)

        self.device_edit = QLineEdit()
        self.device_edit.setPlaceholderText("Device ID (선택사항 - 비워두면 첫 로그인 시 자동 등록)")
        layout.addWidget(self.device_edit)

        self.depositor_edit = QLineEdit()
        self.depositor_edit.setPlaceholderText("입금자명 (선택, 이메일과 동일 권장)")
        layout.addWidget(self.depositor_edit)

        # 플랜 선택 (BASIC / PRO / DIAMOND / MASTER)
        plan_layout = QHBoxLayout()
        plan_label = QLabel("플랜:")
        self.plan_combo = QComboBox()
        self.plan_combo.addItems(["BASIC", "PRO", "DIAMOND", "MASTER"])
        plan_layout.addWidget(plan_label)
        plan_layout.addWidget(self.plan_combo)
        layout.addLayout(plan_layout)

        btn_issue = QPushButton("라이선스 발급")
        btn_issue.clicked.connect(self.issue_license)
        layout.addWidget(btn_issue)

        # --- 일괄 발급 영역 ---
        bulk_label = QLabel("일괄 발급 (이메일,디바이스ID(선택),입금자명 형식으로 한 줄당 한 명):")
        layout.addWidget(bulk_label)

        self.bulk_edit = QPlainTextEdit()
        self.bulk_edit.setPlaceholderText("예)\nuser1@example.com,,홍길동\nuser2@example.com,DEVICEID2,이철수\n(Device ID는 비워두면 첫 로그인 시 자동 등록)")
        layout.addWidget(self.bulk_edit)

        btn_bulk = QPushButton("일괄 발급 (위 플랜으로)")
        btn_bulk.clicked.connect(self.bulk_issue_licenses)
        layout.addWidget(btn_bulk)

        # --- 테이블 ---
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(
            ["Email", "Device ID", "입금자명", "Plan", "License Key"]
        )
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)

        # --- 하단 버튼들: 키 복사 / 삭제 / PRO로 변경 ---
        btn_layout = QHBoxLayout()
        layout.addLayout(btn_layout)

        btn_copy = QPushButton("키 복사")
        btn_delete = QPushButton("선택 삭제")
        btn_upgrade = QPushButton("선택 PRO로 변경")

        btn_layout.addWidget(btn_copy)
        btn_layout.addWidget(btn_delete)
        btn_layout.addWidget(btn_upgrade)

        btn_copy.clicked.connect(self.copy_license)
        btn_delete.clicked.connect(self.delete_license)
        btn_upgrade.clicked.connect(self.upgrade_to_pro)

        self.setCentralWidget(widget)




    def load_table(self):
        """Firestore에서 라이선스 목록 로드"""
        try:
            self.table.setRowCount(0)
            
            # Firestore에서 모든 라이선스 가져오기
            licenses_ref = db.collection("licenses")
            docs = licenses_ref.stream()
            
            rows = []
            for doc in docs:
                data = doc.to_dict()
                # 컬럼: Email, Device ID, 입금자명, Plan, License Key
                rows.append([
                    doc.id,  # email (document ID)
                    data.get("device_id", ""),
                    data.get("depositor", ""),
                    data.get("plan", "BASIC"),
                    data.get("license_key", "")
                ])
            
            # 테이블에 표시
            for row in rows:
                row_idx = self.table.rowCount()
                self.table.insertRow(row_idx)
                for col, value in enumerate(row):
                    self.table.setItem(row_idx, col, QTableWidgetItem(str(value)))
                    
        except Exception as e:
            QMessageBox.warning(self, "오류", f"데이터 로드 실패:\n{e}")





    def copy_license(self):
        """선택한 라이선스 키를 클립보드에 복사"""
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "선택 없음", "복사할 라이선스를 선택하세요.")
            return

        # License Key는 이제 4번 컬럼 (Email, Device ID, 입금자명, Plan, License Key)
        key_item = self.table.item(row, 4)
        if key_item:
            key = key_item.text()
            QApplication.clipboard().setText(key)
            QMessageBox.information(self, "복사 완료", "라이선스 키가 복사되었습니다.")

    def delete_license(self):
        """Firestore에서 라이선스 삭제"""
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "선택 없음", "삭제할 라이선스를 선택하세요.")
            return

        email_item = self.table.item(row, 0)  # 첫 번째 컬럼이 email (document ID)
        if not email_item:
            return

        email = email_item.text()

        reply = QMessageBox.question(
            self,
            "삭제 확인",
            f"{email} 라이선스를 정말 삭제하시겠습니까?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.No:
            return

        try:
            # Firestore에서 삭제
            db.collection("licenses").document(email).delete()
            self.load_table()
            QMessageBox.information(self, "삭제 완료", "라이선스가 삭제되었습니다.")
        except Exception as e:
            QMessageBox.warning(self, "오류", f"삭제 실패:\n{e}")


    
    def issue_license(self):
        """Firestore에 라이선스 발급"""
        email = self.email_edit.text().strip()
        device_id = self.device_edit.text().strip().upper()
        depositor = self.depositor_edit.text().strip()
        plan = self.plan_combo.currentText()

        if not email:
            QMessageBox.warning(self, "입력 오류", "이메일을 입력하세요.")
            return

        # Device ID가 없으면 임시 값 사용 (첫 로그인 시 자동 업데이트됨)
        if not device_id:
            device_id = "PENDING"
        
        # 라이선스 키 생성
        license_key = generate_license(email, device_id)

        try:
            # Firestore에 저장 (email을 document ID로 사용)
            license_data = {
                "email": email,
                "device_id": device_id,
                "depositor": depositor,
                "plan": plan,
                "license_key": license_key,
                "created_at": firestore.SERVER_TIMESTAMP
            }
            
            db.collection("licenses").document(email).set(license_data)

            # 이메일 발송
            email_sent = self.send_email(email, license_key, plan)
            
            success_msg = f"[{plan}] 라이선스 키가 발급되었습니다:\n\n{license_key}\n\n✅ Firestore에 저장 완료!"
            if email_sent:
                success_msg += f"\n✅ {email}로 이메일 발송 완료!"
            else:
                success_msg += f"\n⚠ 이메일 발송 실패 (Firestore 저장은 완료)"

            QMessageBox.information(self, "발급 완료", success_msg)

            self.load_table()
            self.email_edit.clear()
            self.device_edit.clear()
            self.depositor_edit.clear()
            
        except Exception as e:
            QMessageBox.warning(self, "오류", f"라이선스 발급 실패:\n{e}")





    def bulk_issue_licenses(self):
        """Firestore에 일괄 라이선스 발급"""
        text = self.bulk_edit.toPlainText().strip()
        if not text:
            QMessageBox.warning(self, "입력 없음", "일괄 발급할 목록을 입력하세요.")
            return

        plan = self.plan_combo.currentText()

        lines = [line.strip() for line in text.splitlines() if line.strip()]
        if not lines:
            QMessageBox.warning(self, "입력 없음", "유효한 라인이 없습니다.")
            return

        success_count = 0
        email_sent_count = 0
        fail_lines = []

        for line in lines:
            # email,device_id,입금자명 형식 (device_id는 선택사항)
            parts = [p.strip() for p in line.split(",")]
            if len(parts) < 1:
                fail_lines.append(line)
                continue

            email = parts[0]
            device_id = parts[1].upper() if len(parts) >= 2 and parts[1] else "PENDING"
            depositor = parts[2] if len(parts) >= 3 else ""

            if not email:
                fail_lines.append(line)
                continue

            license_key = generate_license(email, device_id)

            try:
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
                
                # 이메일 발송
                if self.send_email(email, license_key, plan):
                    email_sent_count += 1
                success_count += 1
            except Exception as e:
                print(f"발급 실패: {line}, 오류: {e}")
                fail_lines.append(line)

        msg = f"✅ {success_count}개 라이선스가 Firestore에 발급되었습니다.\n"
        msg += f"✅ {email_sent_count}개 이메일 발송 완료"
        
        if success_count > email_sent_count:
            msg += f"\n⚠ {success_count - email_sent_count}개 이메일 발송 실패 (Firestore 저장은 완료)"
        
        if fail_lines:
            msg += "\n\n❌ 실패한 라인들:\n" + "\n".join(fail_lines)

        QMessageBox.information(self, "일괄 발급 결과", msg)

        self.load_table()
        # self.bulk_edit.clear()  # 필요하면 자동 초기화


    def send_email(self, email, license_key, plan, upgraded=False):
        if upgraded:
            subject = f"[MFLOW] {plan} 업그레이드 완료 안내"
            body = f"""
    MFLOW를 이용해주셔서 감사합니다.

    아래 라이선스 정보로 {plan} 업그레이드가 완료되었습니다.

    ===============================
    Email: {email}
    License Key: {license_key}
    Plan: {plan}
    ===============================

    프로그램에서 등록을 다시 한 번 진행해 주세요.
    """
        else:
            # 플랜별 가격 및 설명
            if plan == "BASIC":
                price = "15,000원"
                features = "탭 3개 / 슬롯 20개"
            elif plan == "PRO":
                price = "30,000원"
                features = "탭 5개 / 슬롯 30개"
            elif plan == "DIAMOND":
                price = "50,000원"
                features = "탭·슬롯 무제한"
            elif plan == "MASTER":
                price = "관리자 계정"
                features = "탭·슬롯 무제한"
            else:
                price = "알 수 없음"
                features = "기본"

            subject = f"[MFLOW] {plan} 라이선스 안내"
            body = f"""
    MFLOW를 구매해주셔서 감사합니다.

    [{plan}] 플랜 라이선스 정보는 아래와 같습니다.

    ===============================
    Email: {email}
    License Key: {license_key}
    Plan: {plan}
    가격: {price}
    사용 범위: {features}
    ===============================

    프로그램 실행 후 라이선스 등록 창에서
    위 Email과 License Key 정보를 입력해 주세요.

    ※ 이 라이선스는 등록된 PC(Device ID)에만 유효합니다.
    """

        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = SMTP_EMAIL
        msg["To"] = email

        try:
            with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
                server.login(SMTP_EMAIL, SMTP_PASSWORD)
                server.sendmail(SMTP_EMAIL, [email], msg.as_string())
            print(f"✅ 이메일 발송 성공: {email}")
            return True
        except Exception as e:
            print(f"⚠ 이메일 발송 실패: {email} - {e}")
            # 일괄 발급 시에는 팝업 안 띄우고 로그만 출력
            # QMessageBox.warning(self, "메일 전송 실패", str(e))
            return False


    def upgrade_to_pro(self):
        """Firestore에서 라이선스를 PRO로 업그레이드"""
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "선택 없음", "업그레이드할 라이선스를 선택하세요.")
            return

        email_item = self.table.item(row, 0)  # 첫 번째 컬럼이 email
        
        if not email_item:
            return

        email = email_item.text()

        reply = QMessageBox.question(
            self,
            "PRO 업그레이드",
            f"{email}\n이 라이선스를 PRO로 변경하시겠습니까?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply != QMessageBox.Yes:
            return

        try:
            # Firestore에서 업데이트
            db.collection("licenses").document(email).update({
                "plan": "PRO"
            })

            # 테이블에서 기존 license_key 읽기 (5번 컬럼 → 4번 컬럼으로 변경)
            key_item = self.table.item(row, 4)
            license_key = key_item.text() if key_item else ""

            # PRO로 변경되었다는 안내 메일 발송
            self.send_email(email, license_key, "PRO", upgraded=True)

            self.load_table()
            QMessageBox.information(self, "완료", "선택한 라이선스가 PRO로 변경되었습니다.")
            
        except Exception as e:
            QMessageBox.warning(self, "오류", f"업그레이드 실패:\n{e}")



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LicenseManager()
    window.show()
    sys.exit(app.exec_())

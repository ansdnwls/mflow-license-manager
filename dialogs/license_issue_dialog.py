from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QDateEdit, QTextEdit, QMessageBox
)
from PyQt5.QtCore import Qt, QDate
from datetime import datetime, timedelta

class LicenseIssueDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("새 라이센스 발급")
        self.setFixedWidth(400)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        # 이메일 입력
        email_layout = QHBoxLayout()
        email_label = QLabel("이메일:")
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("user@example.com")
        email_layout.addWidget(email_label)
        email_layout.addWidget(self.email_input)
        layout.addLayout(email_layout)

        # 라이센스 등급 선택
        grade_layout = QHBoxLayout()
        grade_label = QLabel("라이센스 등급:")
        self.grade_combo = QComboBox()
        self.grade_combo.addItems(["베이직", "사파이어", "다이아", "프리미엄"])
        grade_layout.addWidget(grade_label)
        grade_layout.addWidget(self.grade_combo)
        layout.addLayout(grade_layout)

        # 기간 선택 버튼들
        duration_label = QLabel("사용 기간:")
        layout.addWidget(duration_label)
        
        duration_buttons = QHBoxLayout()
        durations = [("1개월", 1), ("6개월", 6), ("1년", 12), ("2년", 24)]
        
        for text, months in durations:
            btn = QPushButton(text)
            btn.clicked.connect(lambda checked, m=months: self.set_duration(m))
            duration_buttons.addWidget(btn)
        
        layout.addLayout(duration_buttons)

        # 만료일 선택
        expiry_layout = QHBoxLayout()
        expiry_label = QLabel("만료일:")
        self.expiry_date = QDateEdit()
        self.expiry_date.setCalendarPopup(True)
        self.expiry_date.setMinimumDate(QDate.currentDate())
        self.expiry_date.setDate(QDate.currentDate().addMonths(1))
        expiry_layout.addWidget(expiry_label)
        expiry_layout.addWidget(self.expiry_date)
        layout.addLayout(expiry_layout)

        # 라이센스 키 표시
        key_layout = QHBoxLayout()
        key_label = QLabel("라이센스 키:")
        self.key_display = QLineEdit()
        self.key_display.setReadOnly(True)
        self.key_display.setStyleSheet("background-color: #f0f0f0;")
        key_layout.addWidget(key_label)
        key_layout.addWidget(self.key_display)
        layout.addLayout(key_layout)

        # 메모 입력
        memo_label = QLabel("메모:")
        self.memo_input = QTextEdit()
        self.memo_input.setMaximumHeight(100)
        layout.addWidget(memo_label)
        layout.addWidget(self.memo_input)

        # 등급별 설명
        grade_info = {
            "베이직": "1개 탭, 20개 슬롯",
            "사파이어": "3개 탭, 20개 슬롯",
            "다이아": "5개 탭, 20개 슬롯",
            "프리미엄": "무제한 탭/슬롯"
        }
        
        self.grade_info_label = QLabel()
        self.grade_info_label.setStyleSheet("color: gray; font-size: 10pt;")
        layout.addWidget(self.grade_info_label)
        
        # 등급 변경 시 설명 업데이트
        self.grade_combo.currentTextChanged.connect(
            lambda text: self.grade_info_label.setText(grade_info[text])
        )
        # 초기 설명 설정
        self.grade_info_label.setText(grade_info[self.grade_combo.currentText()])

        # 버튼 영역
        button_layout = QHBoxLayout()
        self.generate_button = QPushButton("발급하기")
        self.generate_button.clicked.connect(self.generate_license)
        cancel_button = QPushButton("취소")
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.generate_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

    def set_duration(self, months):
        """기간 버튼 클릭 시 만료일 설정"""
        new_date = QDate.currentDate().addMonths(months)
        self.expiry_date.setDate(new_date)

    def generate_license(self):
        """라이센스 발급"""
        # 입력 검증
        if not self.validate_input():
            return

        # 라이센스 데이터 수집
        license_data = {
            'email': self.email_input.text(),
            'grade': self.grade_combo.currentText(),
            'expiry_date': self.expiry_date.date().toPyDate(),
            'memo': self.memo_input.toPlainText(),
            'key': self.generate_license_key()
        }

        self.key_display.setText(license_data['key'])
        
        # 성공 메시지
        QMessageBox.information(
            self,
            "라이센스 발급 완료",
            f"라이센스가 성공적으로 발급되었습니다.\n\n"
            f"이메일: {license_data['email']}\n"
            f"등급: {license_data['grade']}\n"
            f"라이센스 키: {license_data['key']}"
        )
        
        self.accept()

    def validate_input(self):
        """입력값 검증"""
        if not self.email_input.text():
            QMessageBox.warning(self, "입력 오류", "이메일을 입력하세요.")
            return False
            
        if not '@' in self.email_input.text():
            QMessageBox.warning(self, "입력 오류", "올바른 이메일 형식이 아닙니다.")
            return False
            
        if self.expiry_date.date() <= QDate.currentDate():
            QMessageBox.warning(self, "입력 오류", "만료일은 현재 날짜보다 이후여야 합니다.")
            return False
            
        return True

    def generate_license_key(self):
        """라이센스 키 생성"""
        import random
        import string
        
        # 4개의 블록, 각 블록은 4자리 영숫자
        blocks = []
        for _ in range(4):
            # 영문 대문자와 숫자로 구성
            chars = string.ascii_uppercase + string.digits
            block = ''.join(random.choice(chars) for _ in range(4))
            blocks.append(block)
            
        return '-'.join(blocks)

    def get_license_data(self):
        """발급된 라이센스 데이터 반환"""
        return {
            'email': self.email_input.text(),
            'grade': self.grade_combo.currentText(),
            'expiry_date': self.expiry_date.date().toPyDate(),
            'memo': self.memo_input.toPlainText(),
            'key': self.key_display.text()
        }
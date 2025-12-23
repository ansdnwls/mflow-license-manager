from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QFormLayout, QMessageBox, QFileDialog,
    QLineEdit, QTextEdit
)
import json
import os
import codecs

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("설정")
        self.setMinimumWidth(400)
        self.settings_file = 'settings.json'
        self.load_settings()
        self.setup_ui()

    def get_default_template(self):
        return """안녕하세요,

Mflow Paste 라이센스가 발급되었습니다.

라이센스 정보:
- 이메일: {email}
- 라이센스 키: {license_key}
- 등급: {grade}
- 만료일: {expiry_date}

감사합니다."""

    def setup_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        form_layout = QFormLayout()

        # 라이센스 접두어 설정
        self.license_prefix = QLineEdit(self.settings.get('license_prefix', 'MF-'))
        form_layout.addRow("라이센스 접두어:", self.license_prefix)

        # 백업 설정
        self.backup_path = QLineEdit(self.settings.get('backup_path', ''))
        backup_browse = QPushButton("찾아보기")
        backup_browse.clicked.connect(self.browse_backup_path)
        backup_layout = QHBoxLayout()
        backup_layout.addWidget(self.backup_path)
        backup_layout.addWidget(backup_browse)
        form_layout.addRow("백업 경로:", backup_layout)

        # 이메일 설정 부분 추가
        self.email_sender = QLineEdit(self.settings.get('email_sender', ''))
        self.email_password = QLineEdit(self.settings.get('email_password', ''))
        self.email_password.setEchoMode(QLineEdit.Password)
        self.email_template = QTextEdit()
        self.email_template.setPlainText(self.settings.get('email_template', self.get_default_template()))

        form_layout.addRow("발신 이메일:", self.email_sender)
        form_layout.addRow("이메일 비밀번호:", self.email_password)
        form_layout.addRow("이메일 템플릿:", self.email_template)

        layout.addLayout(form_layout)

        # 버튼
        button_layout = QHBoxLayout()
        save_button = QPushButton("저장")
        save_button.clicked.connect(self.save_settings)
        cancel_button = QPushButton("취소")
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

    def browse_backup_path(self):
        dir_path = QFileDialog.getExistingDirectory(self, "백업 경로 선택")
        if dir_path:
            self.backup_path.setText(dir_path)

    def load_settings(self):
        try:
            # UTF-8로 파일 읽기
            with codecs.open(self.settings_file, 'r', encoding='utf-8') as f:
                self.settings = json.load(f)
        except FileNotFoundError:
            # 파일이 존재하지 않으면 기본 설정을 생성
            self.settings = {
                'license_prefix': 'MF-',
                'backup_path': '',
                'email_sender': '',
                'email_password': '',
                'email_template': self.get_default_template()
            }
            # 기본 설정 저장 (UTF-8로)
            with codecs.open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=4)
        except Exception as e:
            self.settings = {}
            QMessageBox.critical(self, "오류", f"설정 로드 중 오류: {str(e)}")

    def save_settings(self):
        settings_data = {
            'license_prefix': self.license_prefix.text(),
            'backup_path': self.backup_path.text(),
            'email_sender': self.email_sender.text(),
            'email_password': self.email_password.text(),
            'email_template': self.email_template.toPlainText()
        }
        
        try:
            # UTF-8로 파일 쓰기
            with codecs.open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings_data, f, ensure_ascii=False, indent=4)
            QMessageBox.information(self, "알림", "설정이 저장되었습니다.")
            self.settings = settings_data
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "오류", f"설정 저장 중 오류 발생: {str(e)}")
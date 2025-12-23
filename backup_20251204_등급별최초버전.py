import sys
import sqlite3
from datetime import datetime, timedelta
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QTextEdit, QTableWidget, QTableWidgetItem,
    QLabel, QComboBox, QMessageBox, QDialog, QInputDialog, QHeaderView
)
from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtGui import QMouseEvent
from dialogs.license_issue_dialog import LicenseIssueDialog
from dialogs.stats_dialog import StatsDialog
from dialogs.settings_dialog import SettingsDialog
from utils.email_sender import EmailSender

import random
import string
import json
import os
import math

class LicenseManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mflow License Manager")
        
        try:
            home_dir = os.path.expanduser("~")
        except AttributeError:
            home_dir = os.getenv("USERPROFILE", "C:\\Users\\Default")  # Windows 기본값
        self.license_file = os.path.join(home_dir, "Documents", "license_info.json")
        self.trial_file = os.path.join(home_dir, "Documents", "trial_info.json")
        self.app_data_path = os.path.join(os.getenv('APPDATA', ''), 'Mflow')
        self.db_path = os.path.join(self.app_data_path, 'licenses.db')
        if not os.path.exists(self.app_data_path):
            os.makedirs(self.app_data_path)
        self.conn = None
       

        # 페이지네이션 및 필터 관련 변수
        self.items_per_page = 20  # 페이지당 표시할 데이터 수
        self.current_page = 1  # 현재 페이지
        self.total_pages = 1  # 전체 페이지 수
        self.all_licenses = []  # 전체 라이센스 데이터
        self.filtered_licenses = []  # 필터링된 라이센스 데이터
        self.current_filter = None  # 현재 적용된 등급 필터 (None이면 전체 표시)

        self.init_database()
        self.init_ui()

        self.setup_license_management()

    def init_database(self):
        app_data_path = os.path.join(os.getenv('APPDATA'), 'Mflow')
        os.makedirs(app_data_path, exist_ok=True)
        db_path = os.path.join(app_data_path, 'licenses.db')
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                name TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS licenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                license_key TEXT UNIQUE NOT NULL,
                type TEXT NOT NULL,
                issued_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                expiry_date DATETIME,
                status TEXT DEFAULT 'active',
                note TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS devices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                license_id INTEGER,
                device_id TEXT NOT NULL,
                device_name TEXT,
                last_active DATETIME,
                FOREIGN KEY (license_id) REFERENCES licenses (id)
            )
        ''')
        self.conn.commit()

    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        self.setMinimumSize(800, 600)
        self.resize(850, 600)
        
        # 상단 버튼 영역
        button_layout = QHBoxLayout()
        issue_button = QPushButton("새 라이센스 발급")
        issue_button.setFixedHeight(40)
        issue_button.clicked.connect(self.show_license_issue_dialog)
        
        stats_button = QPushButton("통계")
        stats_button.setFixedHeight(40)
        stats_button.clicked.connect(self.show_stats)
        
        settings_button = QPushButton("설정")
        settings_button.setFixedHeight(40)
        settings_button.clicked.connect(self.show_settings)
        
        button_layout.addWidget(issue_button)
        button_layout.addWidget(stats_button)
        button_layout.addWidget(settings_button)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        # 검색 영역
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("이메일 또는 라이센스 키로 검색")
        search_layout.addWidget(self.search_input)
        
        layout.addLayout(search_layout)
        
        # 라이센스 목록 테이블
        self.license_table = QTableWidget()
        self.license_table.setColumnCount(9)
        self.license_table.setHorizontalHeaderLabels([
            "이메일", "라이센스 키", "등급", "발급일", "만료일", "상태",
            "연장", "삭제", "메일발송"
        ])
        self.license_table.verticalHeader().setVisible(False)
        self.license_table.setSelectionBehavior(QTableWidget.SelectRows)
        # 헤더 클릭 이벤트 연결
        self.license_table.horizontalHeader().sectionClicked.connect(self.header_clicked)

        # 컬럼 너비 설정
        self.license_table.setColumnWidth(0, 200)
        self.license_table.setColumnWidth(1, 150)
        self.license_table.setColumnWidth(2, 80)
        self.license_table.setColumnWidth(3, 100)
        self.license_table.setColumnWidth(4, 100)
        self.license_table.setColumnWidth(5, 60)
        self.license_table.setColumnWidth(6, 60)
        self.license_table.setColumnWidth(7, 60)
        self.license_table.setColumnWidth(8, 80)
        
        layout.addWidget(self.license_table)
        
        # 페이지 네비게이션 영역
        self.pagination_layout = QHBoxLayout()
        self.prev_button = QPushButton("이전")
        self.prev_button.clicked.connect(self.prev_page)
        self.next_button = QPushButton("다음")
        self.next_button.clicked.connect(self.next_page)
        self.page_label = QLabel("1 / 1")
        
        self.pagination_layout.addStretch()
        self.pagination_layout.addWidget(self.prev_button)
        self.pagination_layout.addWidget(self.page_label)
        self.pagination_layout.addWidget(self.next_button)
        self.pagination_layout.addStretch()
        
        layout.addLayout(self.pagination_layout)
        
        self.load_licenses()

        self.search_input.textChanged.connect(self.search_licenses)

    def setup_license_management(self):
        self.search_input.textChanged.connect(self.search_licenses)
        self.license_table.setContextMenuPolicy(Qt.CustomContextMenu)
        
        header = self.license_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        
        self.license_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.license_table.setSelectionMode(QTableWidget.SingleSelection)

    def header_clicked(self, logical_index):
        # "등급" 컬럼(인덱스 2)이 클릭되었을 때 동작
        if logical_index == 2:
            current_row = self.license_table.currentRow()
            if current_row >= 0:
                selected_grade = self.license_table.item(current_row, 2).text()
                if self.current_filter == selected_grade:
                    # 동일한 등급을 다시 클릭하면 필터 해제
                    self.current_filter = None
                else:
                    self.current_filter = selected_grade
                self.current_page = 1  # 필터 적용 시 첫 페이지로 리셋
                self.load_licenses()

    def show_stats(self):
        dialog = StatsDialog(self, self.cursor)
        dialog.exec_()

    def show_settings(self):
        dialog = SettingsDialog(self)
        dialog.exec_()

    def generate_license_key(self):
        def generate_block():
            chars = string.ascii_uppercase + string.digits
            return ''.join(random.choice(chars) for _ in range(4))
        return '-'.join(generate_block() for _ in range(4))

    def load_licenses(self):
        # 검색 조건이 없으면 전체 데이터 로드
        if not self.search_input.text():
            self.cursor.execute('''
                SELECT users.email, licenses.license_key, licenses.type,
                    licenses.issued_date, licenses.expiry_date, licenses.status
                FROM licenses
                JOIN users ON licenses.user_id = users.id
                ORDER BY licenses.issued_date DESC
            ''')
            self.all_licenses = self.cursor.fetchall()
        else:
            self.cursor.execute('''
                SELECT users.email, licenses.license_key, licenses.type,
                       licenses.issued_date, licenses.expiry_date, licenses.status
                FROM licenses
                JOIN users ON licenses.user_id = users.id
                WHERE users.email LIKE ? OR licenses.license_key LIKE ?
                ORDER BY licenses.issued_date DESC
            ''', (f'%{self.search_input.text()}%', f'%{self.search_input.text()}%'))
            self.all_licenses = self.cursor.fetchall()

        # 등급 필터 적용
        if self.current_filter:
            self.filtered_licenses = [license for license in self.all_licenses if license[2] == self.current_filter]
        else:
            self.filtered_licenses = self.all_licenses

        # 전체 페이지 수 계산
        total_items = len(self.filtered_licenses)
        self.total_pages = max(1, math.ceil(total_items / self.items_per_page))
        
        # 현재 페이지 데이터 범위 계산
        start_idx = (self.current_page - 1) * self.items_per_page
        end_idx = start_idx + self.items_per_page
        current_page_licenses = self.filtered_licenses[start_idx:end_idx]

        # 테이블에 데이터 표시
        self.license_table.setRowCount(len(current_page_licenses))
        for row, license in enumerate(current_page_licenses):
            for col, value in enumerate(license):
                item = QTableWidgetItem(str(value))
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                self.license_table.setItem(row, col, item)
            
            # 버튼 추가
            extend_btn = QPushButton("연장")
            delete_btn = QPushButton("삭제")
            email_btn = QPushButton("메일발송")
            
            extend_btn.setStyleSheet("background-color: #4CAF50; color: white;")
            delete_btn.setStyleSheet("background-color: #f44336; color: white;")
            email_btn.setStyleSheet("background-color: #2196F3; color: white;")
            
            extend_btn.clicked.connect(lambda checked, r=row: self.extend_license(r))
            delete_btn.clicked.connect(lambda checked, r=row: self.delete_license(r))
            email_btn.clicked.connect(lambda checked, r=row: self.send_license_email(r))
            
            self.license_table.setCellWidget(row, 6, extend_btn)
            self.license_table.setCellWidget(row, 7, delete_btn)
            self.license_table.setCellWidget(row, 8, email_btn)

        # 페이지 레이블 업데이트
        self.page_label.setText(f"{self.current_page} / {self.total_pages}")
        
        # 이전/다음 버튼 활성화 여부
        self.prev_button.setEnabled(self.current_page > 1)
        self.next_button.setEnabled(self.current_page < self.total_pages)

    def search_licenses(self, text):
        self.current_page = 1
        self.load_licenses()

    def prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.load_licenses()

    def next_page(self):
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.load_licenses()

    def extend_license(self, row):
        license_key = self.license_table.item(row, 1).text()
        months, ok = QInputDialog.getInt(self, "라이센스 연장", 
                                        "연장 기간(월):", 1, 1, 24)
        if ok:
            try:
                self.cursor.execute("""
                    UPDATE licenses 
                    SET expiry_date = datetime(expiry_date, '+' || ? || ' months')
                    WHERE license_key = ?
                """, (months, license_key))
                self.conn.commit()
                self.load_licenses()
                QMessageBox.information(self, "성공", "라이센스가 연장되었습니다.")
            except sqlite3.Error as e:
                QMessageBox.critical(self, "오류", f"라이센스 연장 중 오류 발생: {str(e)}")

    def delete_license(self, row):
        email = self.license_table.item(row, 0).text()
        license_key = self.license_table.item(row, 1).text()
        reply = QMessageBox.question(self, "라이센스 삭제", 
                                "선택한 라이센스를 삭제하시겠습니까?",
                                QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                self.cursor.execute("""
                    DELETE FROM licenses 
                    WHERE license_key = ?
                """, (license_key,))
                self.conn.commit()
                self.load_licenses()
                QMessageBox.information(self, "성공", "라이센스가 삭제되었습니다.")
            except sqlite3.Error as e:
                self.conn.rollback()
                QMessageBox.critical(self, "오류", f"라이센스 삭제 중 오류 발생: {str(e)}")
                return

            reply = QMessageBox.question(self, "이메일 발송", 
                                    "삭제 알림을 이메일로 발송하시겠습니까?",
                                    QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                try:
                    if not os.path.exists('settings.json'):
                        QMessageBox.warning(self, "경고", "이메일 설정이 필요합니다. 설정 메뉴에서 이메일 정보를 입력해주세요.")
                        return
                    with open('settings.json', 'r', encoding='utf-8') as f:
                        settings = json.load(f)
                    email_sender = EmailSender(
                        settings['email_sender'],
                        settings['email_password']
                    )
                    license_data = {
                        'email': email,
                        'key': license_key,
                        'grade': self.license_table.item(row, 2).text(),
                        'expiry_date': self.license_table.item(row, 4).text()
                    }
                    success, message = email_sender.send_license_email(
                        email,
                        license_data,
                        settings['email_template']
                    )
                    if success:
                        QMessageBox.information(self, "성공", message)
                    else:
                        QMessageBox.warning(self, "경고", message)
                except Exception as e:
                    QMessageBox.warning(self, "경고", f"이메일 발송 중 오류 발생: {str(e)}")

    def send_license_email(self, row):
        email = self.license_table.item(row, 0).text()
        license_key = self.license_table.item(row, 1).text()
        grade = self.license_table.item(row, 2).text()
        expiry_date = self.license_table.item(row, 4).text()
        
        if not os.path.exists('settings.json'):
            QMessageBox.warning(self, "경고", "이메일 설정이 필요합니다. 설정 메뉴에서 이메일 정보를 입력해주세요.")
            return

        try:
            with open('settings.json', 'r', encoding='utf-8') as f:
                settings = json.load(f)
            email_sender = EmailSender(
                settings['email_sender'],
                settings['email_password']
            )
            license_data = {
                'email': email,
                'license_key': license_key,
                'grade': grade,
                'expiry_date': expiry_date
            }
            success, message = email_sender.send_license_email(
                email,
                license_data,
                settings['email_template']
            )
            if success:
                QMessageBox.information(self, "성공", message)
            else:
                QMessageBox.warning(self, "경고", message)
        except Exception as e:
            QMessageBox.critical(self, "오류", f"이메일 발송 중 오류 발생: {str(e)}")

    def show_license_issue_dialog(self):
        dialog = LicenseIssueDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            license_data = dialog.get_license_data()
            try:
                self.cursor.execute(
                    "INSERT OR IGNORE INTO users (email) VALUES (?)",
                    (license_data['email'],)
                )
                self.cursor.execute(
                    "SELECT id FROM users WHERE email = ?",
                    (license_data['email'],)
                )
                user_id = self.cursor.fetchone()[0]
                self.cursor.execute("""
                    INSERT INTO licenses 
                    (user_id, license_key, type, expiry_date, note)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    user_id,
                    license_data['key'],
                    license_data['grade'],
                    license_data['expiry_date'],
                    license_data['memo']
                ))
                self.conn.commit()
                self.load_licenses()
                reply = QMessageBox.question(
                    self,
                    "이메일 발송",
                    "라이센스 정보를 이메일로 발송하시겠습니까?",
                    QMessageBox.Yes | QMessageBox.No
                )
                if reply == QMessageBox.Yes:
                    try:
                        if not os.path.exists('settings.json'):
                            QMessageBox.warning(self, "경고", "이메일 설정이 필요합니다. 설정 메뉴에서 이메일 정보를 입력해주세요.")
                            return
                        with open('settings.json', 'r', encoding='utf-8') as f:
                            settings = json.load(f)
                        email_sender = EmailSender(
                            settings['email_sender'],
                            settings['email_password']
                        )
                        success, message = email_sender.send_license_email(
                            license_data['email'],
                            license_data,
                            settings['email_template']
                        )
                        if success:
                            QMessageBox.information(self, "성공", message)
                        else:
                            QMessageBox.warning(self, "경고", message)
                    except Exception as e:
                        QMessageBox.warning(self, "경고", f"이메일 발송 중 오류 발생: {str(e)}")
            except Exception as e:
                self.conn.rollback()
                QMessageBox.critical(
                    self,
                    "오류",
                    f"라이센스 저장 중 오류가 발생했습니다: {str(e)}"
                )

    def closeEvent(self, event):
        self.conn.close()
        super().closeEvent(event)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = LicenseManager()
    window.show()
    sys.exit(app.exec_())
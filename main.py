import sys
import os
import smtplib
from email.mime.text import MIMEText

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel,
    QLineEdit, QPushButton, QMessageBox, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QHeaderView, QPlainTextEdit, QComboBox, QFrame,
    QGroupBox, QSplitter, QDialog, QCheckBox, QWidget
)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, pyqtSignal, QEvent, QTimer
from PyQt5.QtGui import QFont, QPalette, QColor, QIcon

import firebase_admin
from firebase_admin import credentials, firestore

# 환경변수 로드
from dotenv import load_dotenv
load_dotenv()

from license_core import generate_license

# 환경변수에서 설정값 가져오기
FIREBASE_CREDENTIALS_PATH = os.getenv("FIREBASE_CREDENTIALS_PATH", "mflow_admin.json")
SMTP_EMAIL = os.getenv("SMTP_EMAIL")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "465"))

# Firebase Admin SDK 초기화
try:
    if not os.path.exists(FIREBASE_CREDENTIALS_PATH):
        raise FileNotFoundError(f"Firebase 인증 파일을 찾을 수 없습니다: {FIREBASE_CREDENTIALS_PATH}")
    
    cred = credentials.Certificate(FIREBASE_CREDENTIALS_PATH)
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    print("✅ Firebase initialized successfully")
except FileNotFoundError as e:
    db = None
    print(f"⚠️ Firebase 초기화 실패: {e}")
    QMessageBox.critical(
        None, 
        "오류", 
        f"Firebase 인증 파일을 찾을 수 없습니다!\n\n"
        f"경로: {FIREBASE_CREDENTIALS_PATH}\n\n"
        f".env 파일의 FIREBASE_CREDENTIALS_PATH 설정을 확인하세요."
    )
except Exception as e:
    db = None
    print(f"⚠️ Firebase 초기화 실패: {e}")
    QMessageBox.critical(
        None, 
        "오류", 
        f"Firebase 초기화 실패!\n{e}\n\n"
        f"{FIREBASE_CREDENTIALS_PATH} 파일의 내용을 확인하세요."
    )


def validate_environment():
    """필수 환경변수가 설정되어 있는지 확인"""
    missing_vars = []
    
    if not SMTP_EMAIL:
        missing_vars.append("SMTP_EMAIL")
    if not SMTP_PASSWORD:
        missing_vars.append("SMTP_PASSWORD")
    
    if missing_vars:
        error_msg = f"⚠️ 필수 환경변수가 설정되지 않았습니다:\n\n"
        error_msg += "\n".join(f"  - {var}" for var in missing_vars)
        error_msg += "\n\n.env 파일을 확인하고 필요한 값을 설정해주세요."
        QMessageBox.critical(None, "환경변수 오류", error_msg)
        return False
    
    return True


# 🎨 모던 스타일시트
MODERN_STYLESHEET = """
QMainWindow {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                stop:0 #0f172a, stop:1 #1e293b);
}

QWidget {
    background-color: transparent;
    color: #e2e8f0;
    font-family: 'Segoe UI', Arial, sans-serif;
}

/* 그룹박스 스타일 */
QGroupBox {
    background-color: rgba(30, 41, 59, 0.7);
    border: 2px solid #334155;
    border-radius: 12px;
    margin-top: 20px;
    padding: 20px;
    font-weight: bold;
    font-size: 14px;
    color: #94a3b8;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 5px 15px;
    background-color: #3b82f6;
    border-radius: 6px;
    color: white;
    left: 20px;
}

/* 입력 필드 */
QLineEdit, QPlainTextEdit {
    background-color: rgba(51, 65, 85, 0.5);
    border: 2px solid #475569;
    border-radius: 8px;
    padding: 12px 16px;
    color: #f1f5f9;
    font-size: 13px;
    selection-background-color: #3b82f6;
}

QLineEdit:focus, QPlainTextEdit:focus {
    border: 2px solid #3b82f6;
    background-color: rgba(51, 65, 85, 0.8);
}

QLineEdit:hover, QPlainTextEdit:hover {
    border-color: #64748b;
}

QPlainTextEdit {
    min-height: 100px;
}

/* 콤보박스 */
QComboBox {
    background-color: rgba(51, 65, 85, 0.5);
    border: 2px solid #475569;
    border-radius: 8px;
    padding: 10px 16px;
    color: #f1f5f9;
    font-size: 13px;
    font-weight: bold;
}

QComboBox:hover {
    border-color: #64748b;
}

QComboBox:focus {
    border-color: #3b82f6;
}

QComboBox::drop-down {
    border: none;
    width: 30px;
}

QComboBox::down-arrow {
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 6px solid #94a3b8;
    margin-right: 10px;
}

QComboBox QAbstractItemView {
    background-color: #1e293b;
    border: 2px solid #3b82f6;
    border-radius: 8px;
    selection-background-color: #3b82f6;
    color: #f1f5f9;
    padding: 5px;
}

/* 버튼 - 기본 */
QPushButton {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #3b82f6, stop:1 #2563eb);
    border: none;
    border-radius: 8px;
    color: white;
    padding: 12px 24px;
    font-size: 13px;
    font-weight: bold;
    min-height: 20px;
}

QPushButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #60a5fa, stop:1 #3b82f6);
}

QPushButton:pressed {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #2563eb, stop:1 #1d4ed8);
}

/* 주요 액션 버튼 */
QPushButton#primaryButton {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #10b981, stop:1 #059669);
    font-size: 14px;
    padding: 14px 28px;
}

QPushButton#primaryButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #34d399, stop:1 #10b981);
}

/* 일괄 발급 버튼 */
QPushButton#bulkButton {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #8b5cf6, stop:1 #7c3aed);
}

QPushButton#bulkButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #a78bfa, stop:1 #8b5cf6);
}

/* 삭제 버튼 */
QPushButton#deleteButton {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #ef4444, stop:1 #dc2626);
}

QPushButton#deleteButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #f87171, stop:1 #ef4444);
}

/* 업그레이드 버튼 */
QPushButton#upgradeButton {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #f59e0b, stop:1 #d97706);
}

QPushButton#upgradeButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #fbbf24, stop:1 #f59e0b);
}

/* 테이블 */
QTableWidget {
    background-color: rgba(30, 41, 59, 0.5);
    border: 2px solid #334155;
    border-radius: 12px;
    gridline-color: #475569;
    color: #f1f5f9;
    selection-background-color: #3b82f6;
    selection-color: white;
}

QTableWidget::item {
    padding: 4px 2px;
    border-bottom: 1px solid #334155;
    background-color: rgba(30, 41, 59, 0.5);
    color: #f1f5f9;
}

QTableWidget::item:alternate {
    background-color: rgba(51, 65, 85, 0.5);
    color: #f1f5f9;
}

QTableWidget::item:selected {
    background-color: #3b82f6;
    color: white;
}

QTableWidget::item:hover {
    background-color: rgba(59, 130, 246, 0.2);
}

QHeaderView::section {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #1e293b, stop:1 #0f172a);
    color: #94a3b8;
    padding: 6px 2px;
    border: none;
    border-bottom: 2px solid #3b82f6;
    font-weight: bold;
    font-size: 11px;
}

QHeaderView::section:first {
    border-top-left-radius: 10px;
}

QHeaderView::section:last {
    border-top-right-radius: 10px;
}

/* 스크롤바 */
QScrollBar:vertical {
    background: rgba(30, 41, 59, 0.5);
    width: 12px;
    border-radius: 6px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background: #475569;
    border-radius: 6px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background: #64748b;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    background: rgba(30, 41, 59, 0.5);
    height: 12px;
    border-radius: 6px;
    margin: 0px;
}

QScrollBar::handle:horizontal {
    background: #475569;
    border-radius: 6px;
    min-width: 20px;
}

QScrollBar::handle:horizontal:hover {
    background: #64748b;
}

/* 레이블 */
QLabel {
    color: #cbd5e1;
    font-size: 13px;
}

QLabel#titleLabel {
    color: #f1f5f9;
    font-size: 28px;
    font-weight: bold;
    padding: 10px;
}

QLabel#subtitleLabel {
    color: #94a3b8;
    font-size: 14px;
    padding-bottom: 20px;
}

/* 다이얼로그 */
QDialog {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                stop:0 #0f172a, stop:1 #1e293b);
}
"""


class LicenseTableDialog(QDialog):
    """라이센스 목록 관리 전용 창"""
    
    license_changed = pyqtSignal()  # 라이센스 변경 시그널
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("📊 라이센스 관리 대시보드")
        self.setMinimumSize(1400, 700)
        self.setStyleSheet(MODERN_STYLESHEET)
        
        # 페이지네이션 관련 변수
        self.current_page = 1
        self.items_per_page = 20
        self.all_licenses = []  # 전체 라이센스 데이터
        self.selected_emails = set()  # 선택된 이메일 목록 (페이지 이동 시에도 유지)
        
        self.initUI()
        self.load_table()
    
    def initUI(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # 헤더
        header_layout = QVBoxLayout()
        title_label = QLabel("📊 발급된 라이센스 관리")
        title_label.setObjectName("titleLabel")
        title_label.setAlignment(Qt.AlignCenter)
        
        subtitle_label = QLabel(f"총 라이센스 수: 0개")
        subtitle_label.setObjectName("subtitleLabel")
        subtitle_label.setAlignment(Qt.AlignCenter)
        self.subtitle_label = subtitle_label
        
        header_layout.addWidget(title_label)
        header_layout.addWidget(subtitle_label)
        layout.addLayout(header_layout)
        
        # 검색 바
        search_layout = QHBoxLayout()
        search_label = QLabel("🔍 검색:")
        search_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("이메일, Device ID, 입금자명으로 검색...")
        self.search_edit.textChanged.connect(self.filter_table)
        
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_edit)
        layout.addLayout(search_layout)
        
        # 테이블
        self.table = QTableWidget(0, 7)  # 순번 컬럼 제거로 7개로 변경
        self.table.setHorizontalHeaderLabels(
            ["", "📧 Email", "💻 Device ID", "👤 입금자명", "🎯 Plan", "🔑 License Key", "📅 생성일"]
        )
        # 선택창 컬럼 (0번) - 최소 너비 (체크박스만 표시)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self.table.setColumnWidth(0, 18)
        # 나머지 컬럼은 자동 조정
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.ExtendedSelection)
        self.table.setSortingEnabled(True)
        # 정렬 후 순번 재계산을 위한 시그널 연결
        self.table.horizontalHeader().sortIndicatorChanged.connect(self.on_sort_changed)
        # 체크박스 컬럼 클릭 시 행 선택 방지
        self.table.cellClicked.connect(self.on_cell_clicked)
        layout.addWidget(self.table)
        
        # 페이지네이션 컨트롤
        pagination_layout = QHBoxLayout()
        pagination_layout.addStretch()
        
        self.page_label = QLabel("페이지: 1 / 1")
        self.page_label.setStyleSheet("font-weight: bold; font-size: 13px; color: #94a3b8;")
        
        btn_prev = QPushButton("◀ 이전")
        btn_next = QPushButton("다음 ▶")
        btn_first = QPushButton("⏮ 첫 페이지")
        btn_last = QPushButton("마지막 페이지 ⏭")
        
        btn_prev.clicked.connect(self.prev_page)
        btn_next.clicked.connect(self.next_page)
        btn_first.clicked.connect(self.first_page)
        btn_last.clicked.connect(self.last_page)
        
        pagination_layout.addWidget(btn_first)
        pagination_layout.addWidget(btn_prev)
        pagination_layout.addWidget(self.page_label)
        pagination_layout.addWidget(btn_next)
        pagination_layout.addWidget(btn_last)
        pagination_layout.addStretch()
        
        layout.addLayout(pagination_layout)
        
        # 버튼들
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)
        
        btn_select_all = QPushButton("☑ 전체 선택")
        btn_select_none = QPushButton("☐ 전체 해제")
        btn_refresh = QPushButton("🔄 새로고침")
        btn_copy = QPushButton("📋 키 복사")
        btn_delete = QPushButton("🗑️ 삭제")
        btn_delete.setObjectName("deleteButton")
        btn_upgrade_pro = QPushButton("⬆️ PRO")
        btn_upgrade_pro.setObjectName("upgradeButton")
        btn_upgrade_diamond = QPushButton("💎 DIAMOND")
        btn_upgrade_diamond.setObjectName("upgradeButton")
        btn_upgrade_master = QPushButton("👑 MASTER")
        btn_upgrade_master.setObjectName("upgradeButton")
        btn_export = QPushButton("💾 Excel 내보내기")
        
        btn_layout.addWidget(btn_select_all)
        btn_layout.addWidget(btn_select_none)
        btn_layout.addWidget(btn_refresh)
        btn_layout.addWidget(btn_copy)
        btn_layout.addWidget(btn_delete)
        btn_layout.addWidget(btn_upgrade_pro)
        btn_layout.addWidget(btn_upgrade_diamond)
        btn_layout.addWidget(btn_upgrade_master)
        btn_layout.addWidget(btn_export)
        btn_layout.addStretch()
        
        btn_select_all.clicked.connect(self.select_all)
        btn_select_none.clicked.connect(self.select_none)
        btn_refresh.clicked.connect(self.load_table)
        btn_copy.clicked.connect(self.copy_license)
        btn_delete.clicked.connect(self.delete_license)
        btn_upgrade_pro.clicked.connect(lambda: self.upgrade_plan("PRO"))
        btn_upgrade_diamond.clicked.connect(lambda: self.upgrade_plan("DIAMOND"))
        btn_upgrade_master.clicked.connect(lambda: self.upgrade_plan("MASTER"))
        btn_export.clicked.connect(self.export_to_excel)
        
        layout.addLayout(btn_layout)
        self.setLayout(layout)
    
    def load_table(self):
        """Firestore에서 라이센스 목록 로드"""
        try:
            licenses_ref = db.collection("licenses")
            docs = licenses_ref.stream()
            
            self.all_licenses = []
            for doc in docs:
                data = doc.to_dict()
                created_at = data.get("created_at", "")
                if created_at:
                    try:
                        created_at = created_at.strftime("%Y-%m-%d %H:%M")
                    except:
                        created_at = "N/A"
                
                self.all_licenses.append({
                    "email": doc.id,
                    "device_id": data.get("device_id", ""),
                    "depositor": data.get("depositor", ""),
                    "plan": data.get("plan", "BASIC"),
                    "license_key": data.get("license_key", ""),
                    "created_at": created_at
                })
            
            # 총 개수 업데이트
            self.subtitle_label.setText(f"총 라이센스 수: {len(self.all_licenses)}개")
            
            # 페이지 표시 업데이트
            self.display_page()
                    
        except Exception as e:
            QMessageBox.warning(self, "오류", f"데이터 로드 실패:\n{e}")
    
    def display_page(self):
        """현재 페이지의 데이터를 테이블에 표시"""
        self.table.setSortingEnabled(False)
        self.table.setRowCount(0)
        
        # 현재 페이지에 해당하는 데이터 계산
        total_pages = (len(self.all_licenses) + self.items_per_page - 1) // self.items_per_page
        if total_pages == 0:
            total_pages = 1
        
        # 현재 페이지 범위 조정
        if self.current_page > total_pages:
            self.current_page = total_pages
        if self.current_page < 1:
            self.current_page = 1
        
        start_idx = (self.current_page - 1) * self.items_per_page
        end_idx = min(start_idx + self.items_per_page, len(self.all_licenses))
        
        # 현재 페이지의 데이터만 표시
        for i in range(start_idx, end_idx):
            license_data = self.all_licenses[i]
            row_idx = self.table.rowCount()
            self.table.insertRow(row_idx)
            
            # 체크박스 추가 (0번 컬럼) - 체크 표시를 위한 커스텀 위젯
            checkbox_widget = QWidget()
            checkbox_widget.setFixedSize(18, 18)
            checkbox_widget.setStyleSheet("background-color: transparent;")
            
            checkbox = QCheckBox(checkbox_widget)
            checkbox.setText("")  # 텍스트 제거
            checkbox.setGeometry(0, 0, 18, 18)
            checkbox.setStyleSheet("""
                QCheckBox {
                    background-color: transparent;
                    padding: 0px;
                    margin: 0px;
                    spacing: 0px;
                }
                QCheckBox::indicator {
                    width: 16px;
                    height: 16px;
                    border: 2px solid #64748b;
                    border-radius: 3px;
                    background-color: rgba(30, 41, 59, 0.8);
                }
                QCheckBox::indicator:checked {
                    background-color: #3b82f6;
                    border-color: #3b82f6;
                }
                QCheckBox::indicator:hover {
                    border-color: #94a3b8;
                    background-color: rgba(30, 41, 59, 1.0);
                }
                QCheckBox::indicator:checked:hover {
                    background-color: #2563eb;
                    border-color: #2563eb;
                }
            """)
            checkbox.setContentsMargins(0, 0, 0, 0)
            
            # 체크 표시를 위한 라벨 (체크박스 위에 겹쳐서 표시)
            check_label = QLabel("✓", checkbox_widget)
            check_label.setGeometry(0, 0, 16, 16)
            check_label.setStyleSheet("""
                QLabel {
                    color: white;
                    font-size: 13px;
                    font-weight: bold;
                    background-color: transparent;
                    padding: 0px;
                    margin: 0px;
                }
            """)
            check_label.setAlignment(Qt.AlignCenter)
            check_label.hide()  # 초기에는 숨김
            check_label.raise_()  # 체크박스 위에 표시되도록
            check_label.setAttribute(Qt.WA_TransparentForMouseEvents)  # 마우스 이벤트 무시 (클릭 이벤트가 체크박스로 전달됨)
            
            # 위젯에 체크박스와 라벨 참조 저장 (select_all에서 사용)
            checkbox_widget.checkbox = checkbox
            checkbox_widget.check_label = check_label
            checkbox_widget.row_idx = row_idx  # 행 인덱스 저장
            
            # 선택 상태 복원
            email = license_data["email"]
            if email in self.selected_emails:
                checkbox.setChecked(True)
                check_label.show()
            
            # 체크 상태 변경 시 체크 표시 표시/숨김 (올바른 행에만)
            # 클로저 문제를 방지하기 위해 함수 생성
            def make_state_handler(e, lbl):
                def on_state_changed(state):
                    if state == Qt.Checked:
                        lbl.show()
                    else:
                        lbl.hide()
                    self.update_selection(e, state)
                return on_state_changed
            
            checkbox.stateChanged.connect(make_state_handler(email, check_label))
            
            # 체크박스 위젯 클릭 시 행 선택 방지 (체크박스 토글은 정상 작동)
            # 클로저 문제를 방지하기 위해 체크박스를 명시적으로 캡처
            def make_click_handler(cb):
                def widget_clicked(event):
                    # 현재 체크 상태를 반전
                    cb.setChecked(not cb.isChecked())
                    # 행 선택은 나중에 해제
                    QTimer.singleShot(10, lambda: self.table.clearSelection())
                return widget_clicked
            
            click_handler = make_click_handler(checkbox)
            checkbox_widget.mousePressEvent = click_handler
            
            # 체크박스 추가 (0번 컬럼)
            self.table.setCellWidget(row_idx, 0, checkbox_widget)  # 0번 컬럼에 체크박스 위젯
            
            # 데이터 추가 (1번 컬럼부터 시작)
            data_items = [
                license_data["email"],
                license_data["device_id"],
                license_data["depositor"],
                license_data["plan"],
                license_data["license_key"],
                license_data["created_at"]
            ]
            
            for col, value in enumerate(data_items, start=1):  # 1번 컬럼부터 시작
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row_idx, col, item)
        
        # 페이지 정보 업데이트
        self.page_label.setText(f"페이지: {self.current_page} / {total_pages}")
        
        self.table.setSortingEnabled(True)
    
    def on_cell_clicked(self, row, col):
        """셀 클릭 이벤트 처리 - 체크박스 컬럼 클릭 시 행 선택 방지"""
        if col == 0:  # 체크박스 컬럼 클릭 시 (0번 컬럼)
            # 행 선택 해제 (체크박스는 정상 작동)
            QTimer.singleShot(0, lambda: self.table.clearSelection())
    
    def on_sort_changed(self, logical_index, order):
        """정렬 변경 시 처리 (순번 컬럼 제거로 더 이상 필요 없음)"""
        pass
    
    def update_selection(self, email, state):
        """체크박스 상태 변경 시 선택 목록 업데이트"""
        if state == Qt.Checked:
            self.selected_emails.add(email)
        else:
            self.selected_emails.discard(email)
    
    def prev_page(self):
        """이전 페이지로 이동"""
        if self.current_page > 1:
            self.current_page -= 1
            self.display_page()
    
    def next_page(self):
        """다음 페이지로 이동"""
        total_pages = (len(self.all_licenses) + self.items_per_page - 1) // self.items_per_page
        if total_pages == 0:
            total_pages = 1
        if self.current_page < total_pages:
            self.current_page += 1
            self.display_page()
    
    def first_page(self):
        """첫 페이지로 이동"""
        self.current_page = 1
        self.display_page()
    
    def last_page(self):
        """마지막 페이지로 이동"""
        total_pages = (len(self.all_licenses) + self.items_per_page - 1) // self.items_per_page
        if total_pages == 0:
            total_pages = 1
        self.current_page = total_pages
        self.display_page()
    
    def filter_table(self, text):
        """테이블 필터링 - 검색 기능은 나중에 구현 예정"""
        # 검색 기능은 페이지네이션과 함께 구현하기 복잡하므로
        # 일단 검색어가 없으면 전체 표시
        if not text:
            self.current_page = 1
            self.display_page()
    
    def copy_license(self):
        """선택한 라이센스 키를 클립보드에 복사"""
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "선택 없음", "복사할 라이센스를 선택하세요.")
            return

        key_item = self.table.item(row, 5)  # License Key는 5번째 컬럼 (0: 체크박스, 1: Email, 2: Device ID, 3: 입금자명, 4: Plan, 5: License Key, 6: 생성일)
        if key_item:
            key = key_item.text()
            QApplication.clipboard().setText(key)
            QMessageBox.information(self, "✅ 복사 완료", "라이센스 키가 클립보드에 복사되었습니다.")
    
    def delete_license(self):
        """선택된 라이센스들을 삭제 (체크박스로 선택된 항목 또는 현재 선택된 행)"""
        selected_emails = list(self.selected_emails)
        
        # 체크박스로 선택된 항목이 없으면 현재 행 선택
        if not selected_emails:
            row = self.table.currentRow()
            if row < 0:
                QMessageBox.warning(self, "선택 없음", "삭제할 라이센스를 선택하세요.")
                return
            
            email_item = self.table.item(row, 1)  # Email은 1번 컬럼 (0: 체크박스, 1: Email)
            if not email_item:
                return
            selected_emails = [email_item.text()]
        
        if not selected_emails:
            QMessageBox.warning(self, "선택 없음", "삭제할 라이센스를 선택하세요.")
            return
        
        reply = QMessageBox.question(
            self,
            "🗑️ 삭제 확인",
            f"선택된 {len(selected_emails)}개의 라이센스를\n정말 삭제하시겠습니까?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            return
        
        success_count = 0
        fail_count = 0
        
        for email in selected_emails:
            try:
                db.collection("licenses").document(email).delete()
                self.selected_emails.discard(email)
                success_count += 1
            except Exception as e:
                print(f"⚠️ {email} 삭제 실패: {e}")
                fail_count += 1
        
        self.load_table()
        self.license_changed.emit()
        
        if fail_count == 0:
            QMessageBox.information(self, "✅ 완료", f"{success_count}개의 라이센스가 삭제되었습니다!")
        else:
            QMessageBox.warning(self, "⚠️ 부분 완료", f"성공: {success_count}개\n실패: {fail_count}개")
    
    def select_all(self):
        """현재 페이지의 모든 체크박스 선택 및 전체 데이터에도 선택 상태 저장"""
        for row in range(self.table.rowCount()):
            checkbox_widget = self.table.cellWidget(row, 0)  # 0번 컬럼에 체크박스
            if checkbox_widget and hasattr(checkbox_widget, 'checkbox'):
                checkbox = checkbox_widget.checkbox
                check_label = checkbox_widget.check_label
                checkbox.setChecked(True)
                check_label.show()
                # 이메일은 1번 컬럼에 있음 (0: 체크박스, 1: 이메일)
                email_item = self.table.item(row, 1)
                if email_item:
                    self.selected_emails.add(email_item.text())
    
    def select_none(self):
        """현재 페이지의 모든 체크박스 해제 및 전체 선택 상태에서 제거"""
        for row in range(self.table.rowCount()):
            checkbox_widget = self.table.cellWidget(row, 0)  # 0번 컬럼에 체크박스
            if checkbox_widget and hasattr(checkbox_widget, 'checkbox'):
                checkbox = checkbox_widget.checkbox
                check_label = checkbox_widget.check_label
                checkbox.setChecked(False)
                check_label.hide()
                # 이메일은 1번 컬럼에 있음 (0: 체크박스, 1: 이메일)
                email_item = self.table.item(row, 1)
                if email_item:
                    self.selected_emails.discard(email_item.text())
    
    def get_selected_emails(self):
        """체크박스로 선택된 라이센스의 이메일 목록 반환 (모든 페이지 포함)"""
        return list(self.selected_emails)
    
    def upgrade_plan(self, plan_name):
        """선택된 라이센스들을 지정된 플랜으로 업그레이드"""
        selected_emails = self.get_selected_emails()
        
        if not selected_emails:
            QMessageBox.warning(self, "선택 없음", f"{plan_name}로 변경할 라이센스를 선택하세요.")
            return
        
        plan_display = {"PRO": "⬆️ PRO", "DIAMOND": "💎 DIAMOND", "MASTER": "👑 MASTER"}.get(plan_name, plan_name)
        
        reply = QMessageBox.question(
            self,
            f"{plan_display} 변경",
            f"선택된 {len(selected_emails)}개의 라이센스를\n{plan_name} 플랜으로 변경하시겠습니까?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            return
        
        success_count = 0
        fail_count = 0
        
        for email in selected_emails:
            try:
                # 전체 데이터에서 라이센스 키 가져오기
                license_key = ""
                for license_data in self.all_licenses:
                    if license_data["email"] == email:
                        license_key = license_data["license_key"]
                        break
                
                db.collection("licenses").document(email).update({
                    "plan": plan_name
                })
                
                # 이메일 발송
                if license_key:
                    self.send_upgrade_email(email, license_key, plan_name)
                
                success_count += 1
            except Exception as e:
                print(f"⚠️ {email} 업그레이드 실패: {e}")
                fail_count += 1
        
        self.load_table()
        self.license_changed.emit()
        
        if fail_count == 0:
            QMessageBox.information(self, "✅ 완료", f"{success_count}개의 라이센스가 {plan_name} 플랜으로 변경되었습니다!")
        else:
            QMessageBox.warning(self, "⚠️ 부분 완료", f"성공: {success_count}개\n실패: {fail_count}개")
    
    def send_upgrade_email(self, email, license_key, plan_name="PRO"):
        """업그레이드 안내 이메일 발송"""
        plan_display = {"PRO": "PRO", "DIAMOND": "DIAMOND", "MASTER": "MASTER"}.get(plan_name, plan_name)
        subject = f"[MFLOW] {plan_display} 업그레이드 완료 안내"
        body = f"""
MFLOW를 이용해주셔서 감사합니다.

아래 라이센스 정보로 {plan_display} 업그레이드가 완료되었습니다.

===============================
Email: {email}
License Key: {license_key}
Plan: {plan_display}
===============================

프로그램에서 등록을 다시 한 번 진행해 주세요.
"""
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = SMTP_EMAIL
        msg["To"] = email

        try:
            with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
                server.login(SMTP_EMAIL, SMTP_PASSWORD)
                server.sendmail(SMTP_EMAIL, [email], msg.as_string())
            print(f"✅ 업그레이드 이메일 발송 성공: {email}")
        except Exception as e:
            print(f"⚠️ 이메일 발송 실패: {email} - {e}")
    
    def export_to_excel(self):
        """테이블 데이터를 Excel로 내보내기"""
        try:
            import csv
            from datetime import datetime
            
            filename = f"licenses_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
            with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                
                # 헤더 (순번, 체크박스 컬럼 제외)
                headers = []
                for col in range(1, self.table.columnCount()):  # 0번째 컬럼(체크박스) 제외
                    headers.append(self.table.horizontalHeaderItem(col).text())
                writer.writerow(headers)
                
                # 데이터 (순번, 체크박스 컬럼 제외)
                for row in range(self.table.rowCount()):
                    if not self.table.isRowHidden(row):
                        row_data = []
                        for col in range(1, self.table.columnCount()):  # 0번째 컬럼(체크박스) 제외
                            item = self.table.item(row, col)
                            row_data.append(item.text() if item else "")
                        writer.writerow(row_data)
            
            QMessageBox.information(self, "✅ 내보내기 완료", f"CSV 파일이 생성되었습니다:\n{filename}")
            
        except Exception as e:
            QMessageBox.warning(self, "오류", f"내보내기 실패:\n{e}")


class LicenseManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🚀 MFLOW License Manager")
        self.setMinimumSize(900, 650)
        
        if db is None:
            QMessageBox.critical(self, "오류", "Firebase 초기화 실패!\n프로그램을 종료합니다.")
            sys.exit(1)

        self.table_dialog = None  # 테이블 창 참조
        self.initUI()
        
        # 스타일시트 적용
        self.setStyleSheet(MODERN_STYLESHEET)

    def initUI(self):
        # 중앙 위젯 및 메인 레이아웃
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)

        # 헤더
        header_layout = QVBoxLayout()
        title_label = QLabel("🎫 MFLOW License Manager")
        title_label.setObjectName("titleLabel")
        title_label.setAlignment(Qt.AlignCenter)
        
        subtitle_label = QLabel("라이센스 발급 및 관리 시스템")
        subtitle_label.setObjectName("subtitleLabel")
        subtitle_label.setAlignment(Qt.AlignCenter)
        
        header_layout.addWidget(title_label)
        header_layout.addWidget(subtitle_label)
        main_layout.addLayout(header_layout)

        # 상단 영역 (단일 발급 + 일괄 발급)
        top_splitter = QSplitter(Qt.Horizontal)
        
        # === 단일 발급 그룹 ===
        single_group = QGroupBox("📝 단일 라이센스 발급")
        single_layout = QVBoxLayout()
        single_layout.setSpacing(12)

        self.email_edit = QLineEdit()
        self.email_edit.setPlaceholderText("📧 이메일 입력")
        single_layout.addWidget(self.email_edit)

        self.device_edit = QLineEdit()
        self.device_edit.setPlaceholderText("💻 Device ID (선택사항)")
        single_layout.addWidget(self.device_edit)

        self.depositor_edit = QLineEdit()
        self.depositor_edit.setPlaceholderText("👤 입금자명 (선택사항)")
        single_layout.addWidget(self.depositor_edit)

        # 플랜 선택
        plan_layout = QHBoxLayout()
        plan_label = QLabel("🎯 플랜:")
        plan_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        self.plan_combo = QComboBox()
        self.plan_combo.addItems(["BASIC", "PRO", "DIAMOND", "MASTER"])
        self.plan_combo.setCurrentIndex(1)  # PRO 기본 선택
        plan_layout.addWidget(plan_label)
        plan_layout.addWidget(self.plan_combo)
        single_layout.addLayout(plan_layout)

        btn_issue = QPushButton("✨ 라이센스 발급")
        btn_issue.setObjectName("primaryButton")
        btn_issue.clicked.connect(self.issue_license)
        single_layout.addWidget(btn_issue)
        
        single_layout.addStretch()
        single_group.setLayout(single_layout)

        # === 일괄 발급 그룹 ===
        bulk_group = QGroupBox("📦 일괄 라이센스 발급")
        bulk_layout = QVBoxLayout()
        bulk_layout.setSpacing(12)

        bulk_info = QLabel("형식: 이메일,디바이스ID(선택),입금자명")
        bulk_info.setStyleSheet("color: #94a3b8; font-size: 12px; font-style: italic;")
        bulk_layout.addWidget(bulk_info)

        self.bulk_edit = QPlainTextEdit()
        self.bulk_edit.setPlaceholderText(
            "예시:\n"
            "user1@example.com,,홍길동\n"
            "user2@example.com,DEVICE123,이철수\n"
            "user3@example.com,,김영희"
        )
        bulk_layout.addWidget(self.bulk_edit)

        btn_bulk = QPushButton("🚀 일괄 발급 실행")
        btn_bulk.setObjectName("bulkButton")
        btn_bulk.clicked.connect(self.bulk_issue_licenses)
        bulk_layout.addWidget(btn_bulk)

        bulk_group.setLayout(bulk_layout)

        # 스플리터에 추가
        top_splitter.addWidget(single_group)
        top_splitter.addWidget(bulk_group)
        top_splitter.setStretchFactor(0, 1)
        top_splitter.setStretchFactor(1, 1)
        
        main_layout.addWidget(top_splitter)

        # === 라이센스 관리 버튼 ===
        manage_group = QGroupBox("📊 라이센스 관리")
        manage_layout = QVBoxLayout()
        
        info_label = QLabel("발급된 라이센스를 확인하고 관리하려면 아래 버튼을 클릭하세요.")
        info_label.setStyleSheet("color: #94a3b8; font-size: 13px;")
        info_label.setAlignment(Qt.AlignCenter)
        manage_layout.addWidget(info_label)
        
        btn_open_table = QPushButton("📊 라이센스 관리 대시보드 열기")
        btn_open_table.setObjectName("primaryButton")
        btn_open_table.setMinimumHeight(50)
        btn_open_table.clicked.connect(self.open_license_table)
        manage_layout.addWidget(btn_open_table)
        
        manage_group.setLayout(manage_layout)
        main_layout.addWidget(manage_group)

        self.setCentralWidget(central_widget)
    
    def open_license_table(self):
        """라이센스 관리 대시보드 열기"""
        if self.table_dialog is None or not self.table_dialog.isVisible():
            self.table_dialog = LicenseTableDialog(self)
            self.table_dialog.license_changed.connect(self.on_license_changed)
        
        self.table_dialog.show()
        self.table_dialog.raise_()
        self.table_dialog.activateWindow()
    
    def on_license_changed(self):
        """라이센스 변경 시 호출"""
        pass  # 필요시 메인 창 업데이트

    def load_table(self):
        """더 이상 사용하지 않음 - 호환성 유지용"""
        pass

    def issue_license(self):
        """Firestore에 라이센스 발급"""
        email = self.email_edit.text().strip()
        device_id = self.device_edit.text().strip().upper()
        depositor = self.depositor_edit.text().strip()
        plan = self.plan_combo.currentText()

        if not email:
            QMessageBox.warning(self, "입력 오류", "이메일을 입력하세요.")
            return

        if not device_id:
            device_id = "PENDING"
        
        license_key = generate_license(email, device_id)

        try:
            license_data = {
                "email": email,
                "device_id": device_id,
                "depositor": depositor,
                "plan": plan,
                "license_key": license_key,
                "created_at": firestore.SERVER_TIMESTAMP
            }
            
            db.collection("licenses").document(email).set(license_data)

            email_sent = self.send_email(email, license_key, plan)
            
            success_msg = f"🎉 [{plan}] 라이센스가 발급되었습니다!\n\n"
            success_msg += f"🔑 Key: {license_key}\n\n"
            success_msg += "✅ Firestore 저장 완료!"
            
            if email_sent:
                success_msg += f"\n✅ {email}로 이메일 발송 완료!"
            else:
                success_msg += f"\n⚠️ 이메일 발송 실패 (저장은 완료)"

            QMessageBox.information(self, "✨ 발급 완료", success_msg)

            # 테이블 창이 열려있으면 새로고침
            if self.table_dialog and self.table_dialog.isVisible():
                self.table_dialog.load_table()
            
            self.email_edit.clear()
            self.device_edit.clear()
            self.depositor_edit.clear()
            
        except Exception as e:
            QMessageBox.warning(self, "오류", f"라이센스 발급 실패:\n{e}")

    def bulk_issue_licenses(self):
        """Firestore에 일괄 라이센스 발급"""
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
                license_data = {
                    "email": email,
                    "device_id": device_id,
                    "depositor": depositor,
                    "plan": plan,
                    "license_key": license_key,
                    "created_at": firestore.SERVER_TIMESTAMP
                }
                
                db.collection("licenses").document(email).set(license_data)
                
                if self.send_email(email, license_key, plan):
                    email_sent_count += 1
                success_count += 1
            except Exception as e:
                print(f"발급 실패: {line}, 오류: {e}")
                fail_lines.append(line)

        msg = f"🎉 일괄 발급 완료!\n\n"
        msg += f"✅ {success_count}개 라이센스 발급\n"
        msg += f"✅ {email_sent_count}개 이메일 발송"
        
        if success_count > email_sent_count:
            msg += f"\n⚠️ {success_count - email_sent_count}개 이메일 발송 실패"
        
        if fail_lines:
            msg += f"\n\n❌ 실패: {len(fail_lines)}개\n" + "\n".join(fail_lines[:5])
            if len(fail_lines) > 5:
                msg += f"\n... 외 {len(fail_lines) - 5}개"

        QMessageBox.information(self, "📦 일괄 발급 결과", msg)
        
        # 테이블 창이 열려있으면 새로고침
        if self.table_dialog and self.table_dialog.isVisible():
            self.table_dialog.load_table()

    def send_email(self, email, license_key, plan, upgraded=False):
        """이메일 발송"""
        if upgraded:
            subject = f"[MFLOW] {plan} 업그레이드 완료 안내"
            body = f"""
MFLOW를 이용해주셔서 감사합니다.

아래 라이센스 정보로 {plan} 업그레이드가 완료되었습니다.

===============================
Email: {email}
License Key: {license_key}
Plan: {plan}
===============================

프로그램에서 등록을 다시 한 번 진행해 주세요.
"""
        else:
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

            subject = f"[MFLOW] {plan} 라이센스 안내"
            body = f"""
MFLOW를 구매해주셔서 감사합니다.

[{plan}] 플랜 라이센스 정보는 아래와 같습니다.

===============================
Email: {email}
License Key: {license_key}
Plan: {plan}
가격: {price}
사용 범위: {features}
===============================

프로그램 실행 후 라이센스 등록 창에서
위 Email과 License Key 정보를 입력해 주세요.

* 이 라이센스는 등록된 PC(Device ID)에만 유효합니다.
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
            print(f"⚠️ 이메일 발송 실패: {email} - {e}")
            return False

    def upgrade_to_pro(self):
        """더 이상 메인 창에서 사용하지 않음 - 호환성 유지용"""
        QMessageBox.information(
            self, 
            "안내", 
            "라이센스 업그레이드는\n'라이센스 관리 대시보드'에서 진행해주세요."
        )


if __name__ == "__main__":
    if not validate_environment():
        sys.exit(1)
    
    app = QApplication(sys.argv)
    
    # 다크모드 폰트 설정
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    window = LicenseManager()
    window.show()
    sys.exit(app.exec_())
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QTableWidget, QTableWidgetItem
)
from PyQt5.QtChart import QChart, QChartView, QBarSeries, QBarSet, QValueAxis, QBarCategoryAxis
from PyQt5.QtCore import Qt

class StatsDialog(QDialog):
    def __init__(self, parent=None, cursor=None):
        super().__init__(parent)
        self.cursor = cursor
        self.setWindowTitle("라이센스 통계")
        self.setMinimumSize(600, 400)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        # 요약 정보
        summary_layout = QHBoxLayout()
        
        # 활성 라이센스 수
        self.cursor.execute("""
            SELECT COUNT(*) FROM licenses 
            WHERE status = 'active'
        """)
        active_count = self.cursor.fetchone()[0]
        
        # 등급별 통계
        self.cursor.execute("""
            SELECT type, COUNT(*) FROM licenses 
            GROUP BY type
        """)
        grade_stats = self.cursor.fetchall()

        # 통계 표시
        stats_text = f"""
        전체 발급 현황:
        - 활성 라이센스: {active_count}개
        
        등급별 현황:"""
        
        for grade, count in grade_stats:
            stats_text += f"\n- {grade}: {count}개"

        stats_label = QLabel(stats_text)
        summary_layout.addWidget(stats_label)
        
        layout.addLayout(summary_layout)

        # 월별 발급 현황 테이블
        self.cursor.execute("""
            SELECT strftime('%Y-%m', issued_date) as month,
                   COUNT(*) as count
            FROM licenses
            GROUP BY month
            ORDER BY month DESC
            LIMIT 12
        """)
        monthly_stats = self.cursor.fetchall()

        table = QTableWidget()
        table.setColumnCount(2)
        table.setHorizontalHeaderLabels(["월", "발급 수"])
        table.setRowCount(len(monthly_stats))

        for i, (month, count) in enumerate(monthly_stats):
            table.setItem(i, 0, QTableWidgetItem(month))
            table.setItem(i, 1, QTableWidgetItem(str(count)))

        layout.addWidget(table)
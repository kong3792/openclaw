"""
TKT-20260303-0001: QMS 4.4 Dark Theme Dashboard
REV-20260303-001
Main Dashboard UI Implementation

Model: gpt-5.1-codex-mini
Purpose: Main dashboard window with dark theme, 2-column layout, and integrated charts
Features:
  - Left sidebar menu (240px fixed, collapsible to 60px)
  - Right content area with dashboard components
  - Real-time data update capability
  - Matplotlib and Plotly chart integration
  - Dark theme with #1a1a1a background
"""

import json
import sys
from typing import Optional, Dict, Any
from datetime import datetime

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame, QScrollArea, QTableWidget, QTableWidgetItem,
    QListWidget, QListWidgetItem, QSizePolicy, QHeaderView, QSpacerItem,
    QMessageBox, QMenu, QAction
)
from PyQt5.QtCore import Qt, pyqtSignal, QSize, QPropertyAnimation, QRect, QTimer
from PyQt5.QtGui import QIcon, QPixmap, QFont, QColor
from PyQt5.QtChart import QChart, QChartView, QPieSeries, QPieSlice

from data_models_qms_dashboard import (
    DashboardDataModel, get_dashboard_model, ActivityType, ActivityStatus
)
from chart_components import (
    QualityScoreChart, ApprovalStatusChart, TrendAnalysisChart, ChartUpdateManager
)


class SidebarWidget(QFrame):
    """Left sidebar navigation widget."""
    
    menu_clicked = pyqtSignal(str)  # Emitted when menu item is clicked
    
    def __init__(self, parent=None):
        """Initialize the sidebar."""
        super().__init__(parent)
        self.setObjectName("SidebarWidget")
        self.is_collapsed = False
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI elements."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Logo/Title
        logo_widget = QFrame()
        logo_layout = QVBoxLayout(logo_widget)
        logo_layout.setContentsMargins(15, 15, 15, 15)
        
        logo_label = QLabel("🏠")
        logo_label.setFont(QFont("Arial", 20))
        logo_label.setAlignment(Qt.AlignCenter)
        
        title_label = QLabel("QMS 4.4")
        title_label.setFont(QFont("Malgun Gothic", 12, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #e8e8e8;")
        
        logo_layout.addWidget(logo_label)
        logo_layout.addWidget(title_label)
        layout.addWidget(logo_widget)
        
        # Divider
        divider1 = QFrame()
        divider1.setFrameShape(QFrame.HLine)
        divider1.setStyleSheet("background-color: #333333;")
        divider1.setFixedHeight(1)
        layout.addWidget(divider1)
        
        # Menu items
        menu_items = [
            ("📊", "Dashboard"),
            ("📄", "Documents"),
            ("⚠️", "Issues & CAPA"),
            ("🔍", "Audits"),
            ("📚", "Training"),
            ("🏭", "Suppliers"),
            ("📊", "Reports"),
        ]
        
        self.menu_buttons = {}
        for icon, name in menu_items:
            btn = QPushButton(f"{icon} {name}")
            btn.setObjectName("SidebarButton")
            btn.setFixedHeight(50)
            btn.setFont(QFont("Malgun Gothic", 11))
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda checked, n=name: self._on_menu_click(n))
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #1a1a1a;
                    color: #b0b0b0;
                    border: none;
                    padding: 12px 15px;
                    text-align: left;
                    font-size: 11px;
                }
                QPushButton:hover {
                    background-color: #333333;
                    color: #e8e8e8;
                }
                QPushButton:pressed {
                    background-color: #0277bd;
                    color: #ffffff;
                }
            """)
            
            if name == "Dashboard":
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #0277bd;
                        color: #ffffff;
                        border: none;
                        padding: 12px 15px;
                        text-align: left;
                        font-size: 11px;
                        font-weight: 600;
                    }
                    QPushButton:hover {
                        background-color: #01579b;
                    }
                """)
            
            layout.addWidget(btn)
            self.menu_buttons[name] = btn
        
        # Spacer
        layout.addSpacing(20)
        
        # Divider
        divider2 = QFrame()
        divider2.setFrameShape(QFrame.HLine)
        divider2.setStyleSheet("background-color: #333333;")
        divider2.setFixedHeight(1)
        layout.addWidget(divider2)
        
        # Collapse button
        collapse_btn = QPushButton("⊗ Collapse")
        collapse_btn.setObjectName("CollapseButton")
        collapse_btn.setFixedHeight(40)
        collapse_btn.setFont(QFont("Malgun Gothic", 10))
        collapse_btn.setCursor(Qt.PointingHandCursor)
        collapse_btn.clicked.connect(self.toggle_collapse)
        collapse_btn.setStyleSheet("""
            QPushButton {
                background-color: #252525;
                color: #b0b0b0;
                border: none;
                padding: 8px 10px;
            }
            QPushButton:hover {
                background-color: #333333;
                color: #e8e8e8;
            }
        """)
        layout.addWidget(collapse_btn)
        
        self.collapse_btn = collapse_btn
    
    def _on_menu_click(self, menu_name: str):
        """Handle menu click."""
        # Update button styles
        for name, btn in self.menu_buttons.items():
            if name == menu_name:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #0277bd;
                        color: #ffffff;
                        border: none;
                        padding: 12px 15px;
                        text-align: left;
                        font-size: 11px;
                        font-weight: 600;
                    }
                """)
            else:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #1a1a1a;
                        color: #b0b0b0;
                        border: none;
                        padding: 12px 15px;
                        text-align: left;
                        font-size: 11px;
                    }
                    QPushButton:hover {
                        background-color: #333333;
                        color: #e8e8e8;
                    }
                """)
        
        self.menu_clicked.emit(menu_name)
    
    def toggle_collapse(self):
        """Toggle sidebar collapse state."""
        self.is_collapsed = not self.is_collapsed
        
        if self.is_collapsed:
            # Hide menu text
            for name, btn in self.menu_buttons.items():
                icon = btn.text().split()[0]
                btn.setText(icon)
            self.collapse_btn.setText("⊕")
            self.setFixedWidth(60)
        else:
            # Show full menu
            menu_items = [
                ("📊", "Dashboard"),
                ("📄", "Documents"),
                ("⚠️", "Issues & CAPA"),
                ("🔍", "Audits"),
                ("📚", "Training"),
                ("🏭", "Suppliers"),
                ("📊", "Reports"),
            ]
            for (icon, name), btn in zip(menu_items, self.menu_buttons.values()):
                btn.setText(f"{icon} {name}")
            self.collapse_btn.setText("⊗ Collapse")
            self.setFixedWidth(240)


class ContentAreaWidget(QFrame):
    """Main content area widget."""
    
    def __init__(self, data_model: DashboardDataModel, parent=None):
        """Initialize the content area."""
        super().__init__(parent)
        self.data_model = data_model
        self.setObjectName("ContentArea")
        self.setStyleSheet("background-color: #1a1a1a;")
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI elements."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Page title
        title = QLabel("Dashboard")
        title_font = QFont("Malgun Gothic", 28, QFont.Bold)
        title.setFont(title_font)
        title.setStyleSheet("color: #ffffff;")
        layout.addWidget(title)
        
        # Create scroll area for content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                background-color: #1a1a1a;
                border: none;
            }
            QScrollBar:vertical {
                background-color: #1a1a1a;
                width: 12px;
            }
            QScrollBar::handle:vertical {
                background-color: #4a4a4a;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #5a5a5a;
            }
        """)
        
        # Create content widget
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(20)
        content_layout.setContentsMargins(0, 0, 0, 20)
        
        # Top row: Quality Score + Approval Status
        top_row = QHBoxLayout()
        top_row.setSpacing(20)
        
        # Quality Score Chart
        quality_panel = self._create_panel("Overall Quality Score")
        quality_layout = QVBoxLayout()
        self.quality_chart = QualityScoreChart()
        quality_layout.addWidget(self.quality_chart)
        quality_panel.setLayout(quality_layout)
        top_row.addWidget(quality_panel)
        
        # Approval Status Chart
        approval_panel = self._create_panel("Approval Status")
        approval_layout = QVBoxLayout()
        self.approval_chart = ApprovalStatusChart()
        approval_layout.addWidget(self.approval_chart)
        approval_panel.setLayout(approval_layout)
        top_row.addWidget(approval_panel)
        
        content_layout.addLayout(top_row)
        
        # Middle row: Trend Analysis
        trend_panel = self._create_panel("Trend Analysis (Last 4 Months)")
        trend_layout = QVBoxLayout()
        self.trend_chart = TrendAnalysisChart()
        trend_layout.addWidget(self.trend_chart)
        trend_panel.setLayout(trend_layout)
        content_layout.addWidget(trend_panel)
        
        # Bottom row: Recent Activities + Upcoming Audits
        bottom_row = QHBoxLayout()
        bottom_row.setSpacing(20)
        
        # Recent Activities Table
        activities_panel = self._create_panel("Recent Activities")
        activities_layout = QVBoxLayout()
        self.activities_table = self._create_activities_table()
        activities_layout.addWidget(self.activities_table)
        activities_panel.setLayout(activities_layout)
        bottom_row.addWidget(activities_panel, 3)
        
        # Upcoming Audits List
        audits_panel = self._create_panel("Upcoming Audits")
        audits_layout = QVBoxLayout()
        self.audits_list = self._create_audits_list()
        audits_layout.addWidget(self.audits_list)
        audits_panel.setLayout(audits_layout)
        bottom_row.addWidget(audits_panel, 2)
        
        content_layout.addLayout(bottom_row)
        
        # Add stretch at the end
        content_layout.addStretch()
        
        scroll.setWidget(content_widget)
        layout.addWidget(scroll)
        
        # Populate with data
        self.refresh_data()
    
    def _create_panel(self, title: str) -> QFrame:
        """Create a panel/card widget."""
        panel = QFrame()
        panel.setObjectName("CardPanel")
        panel.setStyleSheet("""
            QFrame {
                background-color: #252525;
                border: 1px solid #333333;
                border-radius: 6px;
            }
        """)
        
        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(15, 15, 15, 15)
        panel_layout.setSpacing(10)
        
        title_label = QLabel(title)
        title_font = QFont("Malgun Gothic", 14, QFont.SemiBold)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #e8e8e8;")
        panel_layout.addWidget(title_label)
        
        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        divider.setStyleSheet("background-color: #333333;")
        divider.setFixedHeight(1)
        panel_layout.addWidget(divider)
        
        # Store the layout reference for content
        panel._content_layout = panel_layout
        
        return panel
    
    def _create_activities_table(self) -> QTableWidget:
        """Create the recent activities table."""
        table = QTableWidget()
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels(
            ["Timestamp", "Activity Type", "Module", "Status", "User"]
        )
        table.setStyleSheet("""
            QTableWidget {
                background-color: #1a1a1a;
                alternate-background-color: #252525;
                gridline-color: #333333;
                border: none;
            }
            QTableWidget::item {
                padding: 8px;
                color: #e8e8e8;
                background-color: #1a1a1a;
            }
            QTableWidget::item:selected {
                background-color: #0277bd;
                color: #ffffff;
            }
            QTableWidget::item:hover {
                background-color: #333333;
            }
            QHeaderView::section {
                background-color: #252525;
                color: #e8e8e8;
                padding: 8px;
                border: none;
                border-right: 1px solid #333333;
                border-bottom: 1px solid #333333;
                font-weight: 600;
            }
        """)
        
        # Set column widths
        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)
        
        table.setRowCount(0)
        table.setMaximumHeight(300)
        
        return table
    
    def _create_audits_list(self) -> QListWidget:
        """Create the upcoming audits list."""
        list_widget = QListWidget()
        list_widget.setStyleSheet("""
            QListWidget {
                background-color: #1a1a1a;
                border: none;
            }
            QListWidget::item {
                background-color: #252525;
                color: #e8e8e8;
                padding: 10px;
                margin: 5px 0px;
                border-radius: 4px;
                border: 1px solid #333333;
            }
            QListWidget::item:selected {
                background-color: #0277bd;
                color: #ffffff;
            }
            QListWidget::item:hover {
                background-color: #333333;
            }
        """)
        
        return list_widget
    
    def refresh_data(self):
        """Refresh all data displays."""
        # Update charts
        self.quality_chart.update_data(
            self.data_model.quality_score.overall,
            self.data_model.quality_score.level
        )
        
        self.approval_chart.update_data(
            self.data_model.approval_status.approved,
            self.data_model.approval_status.pending,
            self.data_model.approval_status.rejected
        )
        
        self.trend_chart.update_data(self.data_model.trend_data)
        
        # Update activities table
        self._populate_activities_table()
        
        # Update audits list
        self._populate_audits_list()
    
    def _populate_activities_table(self):
        """Populate the activities table with data."""
        self.activities_table.setRowCount(0)
        
        for activity in self.data_model.activities[:10]:  # Show last 10
            row = self.activities_table.rowCount()
            self.activities_table.insertRow(row)
            
            # Timestamp
            ts_item = QTableWidgetItem(activity.timestamp)
            ts_item.setFont(QFont("Malgun Gothic", 10))
            self.activities_table.setItem(row, 0, ts_item)
            
            # Activity Type
            type_item = QTableWidgetItem(activity.activity_type.value)
            type_item.setFont(QFont("Malgun Gothic", 10))
            self.activities_table.setItem(row, 1, type_item)
            
            # Module
            module_item = QTableWidgetItem(activity.module)
            module_item.setFont(QFont("Malgun Gothic", 10))
            self.activities_table.setItem(row, 2, module_item)
            
            # Status with color
            status_item = QTableWidgetItem(activity.status.value)
            status_item.setFont(QFont("Malgun Gothic", 10))
            
            status_colors = {
                ActivityStatus.SUCCESS: "#66bb6a",
                ActivityStatus.WARNING: "#ffa726",
                ActivityStatus.ERROR: "#ef5350",
                ActivityStatus.PENDING: "#ff9800",
            }
            color = status_colors.get(activity.status, "#e8e8e8")
            status_item.setForeground(QColor(color))
            self.activities_table.setItem(row, 3, status_item)
            
            # User
            user_item = QTableWidgetItem(activity.user)
            user_item.setFont(QFont("Malgun Gothic", 10))
            self.activities_table.setItem(row, 4, user_item)
            
            self.activities_table.setRowHeight(row, 35)
    
    def _populate_audits_list(self):
        """Populate the audits list with data."""
        self.audits_list.clear()
        
        for audit in self.data_model.upcoming_audits[:5]:  # Show next 5
            item_text = f"📅 {audit.date}\n{audit.audit_type.value}\n{audit.department} - {audit.auditor}"
            item = QListWidgetItem(item_text)
            item.setFont(QFont("Malgun Gothic", 9))
            self.audits_list.addItem(item)
            self.audits_list.setItemWidget(item, self._create_audit_item_widget(audit))
    
    def _create_audit_item_widget(self, audit) -> QWidget:
        """Create a widget for an audit list item."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(2)
        
        date_label = QLabel(f"📅 {audit.date}")
        date_label.setFont(QFont("Malgun Gothic", 10, QFont.Bold))
        date_label.setStyleSheet("color: #2196f3;")
        layout.addWidget(date_label)
        
        type_label = QLabel(audit.audit_type.value)
        type_label.setFont(QFont("Malgun Gothic", 9))
        type_label.setStyleSheet("color: #b0b0b0;")
        layout.addWidget(type_label)
        
        dept_label = QLabel(f"{audit.department} • {audit.auditor}")
        dept_label.setFont(QFont("Malgun Gothic", 8))
        dept_label.setStyleSheet("color: #808080;")
        layout.addWidget(dept_label)
        
        return widget


class DashboardQMS(QMainWindow):
    """Main QMS Dashboard window with dark theme."""
    
    def __init__(self, parent=None):
        """
        Initialize the dashboard.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        
        # Window properties
        self.setWindowTitle("QMS 4.4 Dashboard - Dark Theme")
        self.setGeometry(100, 100, 1400, 900)
        self.setMinimumSize(1000, 700)
        
        # Data model
        self.data_model = get_dashboard_model()
        
        # Chart update manager
        self.chart_manager = ChartUpdateManager(self)
        
        # Initialize UI
        self.init_ui()
        
        # Apply dark theme stylesheet
        self.apply_stylesheet()
    
    def init_ui(self):
        """Initialize main UI layout."""
        # Create central widget
        central = QWidget()
        central.setStyleSheet("background-color: #1a1a1a;")
        self.setCentralWidget(central)
        
        # Main layout (horizontal)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Left sidebar
        self.sidebar = SidebarWidget(self)
        self.sidebar.setFixedWidth(240)
        self.sidebar.menu_clicked.connect(self._on_menu_click)
        main_layout.addWidget(self.sidebar)
        
        # Right content area
        self.content = ContentAreaWidget(self.data_model, self)
        self.content.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        main_layout.addWidget(self.content, 1)
        
        # Register charts for updates
        self.chart_manager.register_chart('quality_score', self.content.quality_chart)
        self.chart_manager.register_chart('approval_status', self.content.approval_chart)
        self.chart_manager.register_chart('trend_analysis', self.content.trend_chart)
        self.chart_manager.set_data_model(self.data_model)
        self.chart_manager.set_update_interval(60000)  # 1 minute
        self.chart_manager.start_updates()
    
    def apply_stylesheet(self):
        """Apply dark theme stylesheet."""
        # Read the stylesheet file
        try:
            with open('styles_dark_theme.qss', 'r', encoding='utf-8') as f:
                stylesheet = f.read()
                self.setStyleSheet(stylesheet)
        except FileNotFoundError:
            # If file not found, use basic styles
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #1a1a1a;
                    color: #e8e8e8;
                }
                QWidget {
                    background-color: #1a1a1a;
                    color: #e8e8e8;
                }
            """)
    
    def _on_menu_click(self, menu_name: str):
        """Handle menu click."""
        print(f"Menu clicked: {menu_name}")
        
        if menu_name == "Dashboard":
            self.content.refresh_data()
        else:
            # In a real application, you would load different content
            QMessageBox.information(
                self, "Coming Soon",
                f"The {menu_name} module is coming soon!"
            )
    
    def closeEvent(self, event):
        """Handle window close event."""
        self.chart_manager.stop_updates()
        event.accept()


def main():
    """Main entry point."""
    app = QApplication(sys.argv)
    
    # Create and show the dashboard
    dashboard = DashboardQMS()
    dashboard.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

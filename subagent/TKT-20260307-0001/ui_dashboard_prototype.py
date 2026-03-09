import sys, os, subprocess
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import importlib.util

# Use absolute workspace design path
WORKSPACE_DESIGN = '/home/myhome/.openclaw/workspace/설계'
if WORKSPACE_DESIGN not in sys.path:
    sys.path.insert(0, WORKSPACE_DESIGN)

from utils import get_permission_level, can_access_module
from error_handler import ErrorHandler

class Dashboard(QMainWindow):
    def __init__(self, department="품질관리", role="user", username="사용자", permission="조회"):
        super().__init__()
        self.department = department
        self.role = role
        self.username = username
        self.permission = permission
        self.current_level = get_permission_level(permission)

        self.setWindowTitle(f"🛡️ QMS Prototype - {self.username} ({self.department})")
        self.resize(1200, 800)
        self.main_font = QFont("Malgun Gothic", 10)
        self.setFont(self.main_font)
        self.initUI()

    def initUI(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)

        header = QLabel("Prototype Dashboard - 주요 메뉴")
        main_layout.addWidget(header)

        grid_widget = self.create_card_grid()
        main_layout.addWidget(grid_widget)

    def create_card_grid(self):
        grid_widget = QWidget()
        grid_layout = QGridLayout(grid_widget)

        menu_cards = [
            ("검사관리", "검사 계획, 실적, 이력 관리", "🔍", "#3f51b5", "inspection_manager.py"),
            ("부적합관리", "NCR 등록, 처리, 추적", "⚠️", "#f44336", "defect_reg_app.py"),
            ("품질관리", "품질 지표, 목표, 대시보드", "📈", "#4caf50", "quality_manager.py"),
        ]

        for i, (title, desc, icon, color, module) in enumerate(menu_cards):
            row = i // 2
            col = i % 2
            enabled = can_access_module(self.permission, module)
            card = self.create_menu_card(title, desc, icon, color, enabled, module)
            grid_layout.addWidget(card, row, col)

        return grid_widget

    def create_menu_card(self, title, description, icon, color, enabled=True, module=None):
        card = QFrame()
        card.setFixedSize(360, 160)
        card_layout = QVBoxLayout(card)

        title_label = QLabel(title)
        desc_label = QLabel(description)
        card_layout.addWidget(title_label)
        card_layout.addWidget(desc_label)

        if enabled and module:
            btn = QPushButton("열기 →")
            # bind with default arg using lambda m=module: ...
            btn.clicked.connect(lambda _, m=module: self.open_module(m))
            card_layout.addWidget(btn)
        else:
            card_layout.addWidget(QLabel("🔒 권한 부족"))

        return card

    def open_module(self, module_name):
        try:
            # Absolute path to design script
            script_path = os.path.join(WORKSPACE_DESIGN, module_name)
            script_path = os.path.normpath(script_path)
            if not os.path.exists(script_path):
                print(f"Module not found: {script_path}")
                return
            # Try import and call main-like entry if available (safer for integration tests)
            spec = importlib.util.spec_from_file_location(module_name.rstrip('.py'), script_path)
            mod = importlib.util.module_from_spec(spec)
            try:
                spec.loader.exec_module(mod)
                if hasattr(mod, 'main'):
                    # call main in-process for integration test
                    mod.main(self.department, self.role, self.username, self.permission)
                else:
                    # fallback: spawn subprocess
                    subprocess.Popen([sys.executable, script_path, self.department, self.role, self.username, self.permission])
            except Exception as e:
                print('In-process module exec failed, falling back to subprocess:', e)
                subprocess.Popen([sys.executable, script_path, self.department, self.role, self.username, self.permission])
        except Exception as e:
            print("Error launching module:", e)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Dashboard("품질관리", "admin", "테스트", "관리자")
    window.show()
    sys.exit(app.exec_())

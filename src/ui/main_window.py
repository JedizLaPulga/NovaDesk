import sys
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
                               QLineEdit, QListWidget, QApplication)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QColor, QPalette, QFont

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NovaDesk")
        
        # 1. Window Flags: Frameless, Always on Top, Tool (no taskbar entry optional)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # 2. Central Widget & Layout
        self.central_widget = QWidget()
        self.central_widget.setObjectName("CentralWidget") # For QSS
        
        # Apply strict styling to the container to ensure rounded corners show clearly
        # Note: In QSS, the Window itself is transparent, we style the central widget
        self.central_widget.setStyleSheet("""
            #CentralWidget {
                background-color: #1e1e2e;
                border: 1px solid #45475a;
                border-radius: 12px;
            }
        """)
        
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setContentsMargins(15, 15, 15, 15)
        self.layout.setSpacing(10)
        
        # 3. Search Bar
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Ask NovaDesk... (e.g. 'Open Spotify')")
        self.search_input.returnPressed.connect(self.process_command)
        
        # 4. Results Area (Hidden by default, shown when typing)
        self.results_list = QListWidget()
        self.results_list.hide()
        
        self.layout.addWidget(self.search_input)
        self.layout.addWidget(self.results_list)
        
        self.setCentralWidget(self.central_widget)
        
        # 5. Sizing & Positioning
        self.resize(700, 80) # Compact height initially
        self.center_on_screen()
        
        # Load external QSS for children widgets
        self.load_stylesheet()

    def load_stylesheet(self):
        try:
            with open("src/ui/styles.qss", "r") as f:
                self.setStyleSheet(self.styleSheet() + f.read())
        except FileNotFoundError:
            print("Warning: styles.qss not found")

    def center_on_screen(self):
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 3 # Slightly above center looks better
        self.move(x, y)

    def process_command(self):
        query = self.search_input.text()
        if not query: return
        
        # Placeholder Logic
        print(f"Processing: {query}")
        self.results_list.addItem(f"Simulated Result: Executing '{query}'...")
        self.results_list.show()
        self.resize(700, 300) # Expand window

    # Allow dragging the frameless window
    def mousePressEvent(self, event):
        self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event):
        delta = event.globalPos() - self.oldPos
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPos()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

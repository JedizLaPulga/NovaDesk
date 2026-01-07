import sys
import os
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                               QPushButton, QLabel, QLineEdit, QListWidget, 
                               QApplication, QListWidgetItem)
from PySide6.QtCore import Qt, QSize, QThread, Signal
from PySide6.QtGui import QColor, QPalette, QFont, QIcon, QPixmap
from src.engine.sound import SoundEngine

# Thread to load the AI Model without freezing the UI
class LoaderThread(QThread):
    loaded = Signal(object, object) # Signals back the (nlp_engine, commander)

    def run(self):
        from src.engine.nlp import IntentClassifier
        from src.engine.commander import Commander
        
        nlp = IntentClassifier()
        cmd = Commander()
        self.loaded.emit(nlp, cmd)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NovaDesk v0.1")
        
        # Set App Icon (Taskbar)
        icon_path = "img/NovaDesk.png"
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        self.nlp = None
        self.commander = None
        self.is_loading = True

        # 1. Window Flags
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # 2. Central Widget
        self.central_widget = QWidget()
        self.central_widget.setObjectName("CentralWidget")
        
        # Main Layout
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(15)
        
        # 3. Custom Title Bar
        self.setup_title_bar()
        
        # 4. Search Bar
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Initializing Brain... please wait")
        self.search_input.setEnabled(False)
        self.search_input.returnPressed.connect(self.process_command)
        
        # 5. Results List
        self.results_list = QListWidget()
        self.results_list.hide()
        self.results_list.itemClicked.connect(self.launch_item) # Click to Launch
        
        self.layout.addWidget(self.search_input)
        self.layout.addWidget(self.results_list)

        # 6. Footer
        self.setup_footer()
        
        self.setCentralWidget(self.central_widget)

    def setup_footer(self):
        footer_widget = QWidget()
        footer_layout = QHBoxLayout(footer_widget)
        footer_layout.setContentsMargins(5, 0, 5, 0)
        
        self.btn_clear_history = QPushButton("Clear History")
        self.btn_clear_history.setCursor(Qt.PointingHandCursor)
        self.btn_clear_history.setFixedSize(100, 30)
        self.btn_clear_history.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: 1px solid #f38ba8;
                color: #f38ba8;
                border-radius: 6px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #f38ba8;
                color: #1e1e2e;
            }
        """)
        self.btn_clear_history.clicked.connect(self.clear_interface)
        
        # Sound Toggle
        self.btn_sound = QPushButton("Sound: OFF")
        self.btn_sound.setCursor(Qt.PointingHandCursor)
        self.btn_sound.setFixedSize(100, 30)
        self.btn_sound.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: 1px solid #6c7086;
                color: #6c7086;
                border-radius: 6px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                border: 1px solid #a6adc8;
                color: #a6adc8;
            }
        """)
        self.btn_sound.clicked.connect(self.toggle_sound)

        footer_layout.addWidget(self.btn_clear_history)
        footer_layout.addWidget(self.btn_sound)
        footer_layout.addStretch()
        
        self.layout.addWidget(footer_widget)
        
        # 6. Sizing

    def toggle_sound(self):
        SoundEngine.ENABLED = not SoundEngine.ENABLED
        if SoundEngine.ENABLED:
            self.btn_sound.setText("Sound: ON")
            self.btn_sound.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: 1px solid #a6e3a1;
                    color: #a6e3a1;
                    border-radius: 6px;
                    font-weight: bold;
                    font-size: 12px;
                }
            """)
            SoundEngine.play('success')
        else:
            self.btn_sound.setText("Sound: OFF")
            self.btn_sound.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: 1px solid #6c7086;
                    color: #6c7086;
                    border-radius: 6px;
                    font-weight: bold;
                    font-size: 12px;
                }
            """)
        self.resize(950, 150) 
        self.center_on_screen()
        
        self.load_stylesheet()
        
        # Start Loading AI
        self.loader_thread = LoaderThread()
        self.loader_thread.loaded.connect(self.on_ai_loaded)
        self.loader_thread.start()

    # ... (setup_title_bar, on_ai_loaded, load_stylesheet, center_on_screen remain same)

    def launch_item(self, item):
        # Fallback for clicking the row itself (if not clicking the button)
        # Only works if text was set, but with setItemWidget, item.text() is empty usually
        # unless we explicitly set it. We'll leave this as legacy or empty for now.
        pass

    def setup_title_bar(self):
        self.title_bar = QWidget()
        self.title_bar.setObjectName("TitleBar")
        header_layout = QHBoxLayout(self.title_bar)
        header_layout.setContentsMargins(10, 0, 5, 0) # Slightly more left margin for logo
        
        # Logo Icon
        logo_label = QLabel()
        logo_pixmap = QPixmap("img/NovaDesk.png")
        if not logo_pixmap.isNull():
            logo_label.setPixmap(logo_pixmap.scaled(20, 20, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            logo_label.setFixedSize(20, 20)
            header_layout.addWidget(logo_label)
            
        # Title Text
        title_label = QLabel("NovaDesk v0.1")
        title_label.setStyleSheet("color: #a6adc8; font-weight: bold; font-size: 13px; margin-left: 5px;")
        header_layout.addWidget(title_label)
        
        # Window Controls
        self.btn_min = QPushButton("－")
        self.btn_min.setObjectName("BtnMinimize")
        self.btn_min.setFixedSize(30, 30)
        self.btn_min.clicked.connect(self.showMinimized)
        
        self.btn_close = QPushButton("✕")
        self.btn_close.setObjectName("BtnClose")
        self.btn_close.setFixedSize(30, 30)
        self.btn_close.clicked.connect(self.close)

        header_layout.addStretch()
        header_layout.addWidget(self.btn_min)
        header_layout.addWidget(self.btn_close)
        
        self.layout.addWidget(self.title_bar)

    def clear_interface(self):
        self.search_input.clear()
        self.results_list.clear()
        self.results_list.hide()
        self.resize(950, 150)
        self.center_on_screen()

    def on_ai_loaded(self, nlp, commander):
        self.nlp = nlp
        self.commander = commander
        self.is_loading = False
        self.search_input.setPlaceholderText("Ask NovaDesk... (e.g. 'Open Spotify')")
        self.search_input.setEnabled(True)
        self.search_input.setFocus()
        SoundEngine.play('startup')

    def load_stylesheet(self):
        try:
            with open("src/ui/styles.qss", "r") as f:
                self.setStyleSheet(self.styleSheet() + f.read())
        except FileNotFoundError:
            print("Warning: styles.qss not found")

    def center_on_screen(self):
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 3 
        self.move(x, y)

    def process_command(self):
        query = self.search_input.text()
        if not query: return
        
        self.results_list.clear() 
        self.results_list.show()
        self.resize(950, 500)
        
        # 1. Predict Intent
        intent, score, entity = self.nlp.predict(query)
        print(f"Predicted: {intent} ({score}) -> {entity}")

        # 2. Get Candidates
        candidates = self.commander.fetch_candidates(intent, entity)
        
        if candidates:
            SoundEngine.play('search')
            # Add Header
            header = QListWidgetItem(f"✨ Found {len(candidates)} suggestions for '{query}':")
            header.setFlags(Qt.NoItemFlags) # Make header non-selectable
            self.results_list.addItem(header)
            
            for app in candidates:
                # Create Item
                item = QListWidgetItem(self.results_list)
                
                # Create Custom Widget for the Item
                widget = QWidget()
                layout = QHBoxLayout(widget)
                layout.setContentsMargins(20, 10, 20, 10)
                
                # App Name Label
                name_label = QLabel(f"🚀 {app['name']}")
                name_label.setStyleSheet("color: #cdd6f4; font-size: 15px; font-weight: 500;")
                
                # OPEN Button (Compact Icon Style)
                open_btn = QPushButton("➜")
                open_btn.setCursor(Qt.PointingHandCursor)
                open_btn.setFixedSize(40, 30)
                open_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #89b4fa; 
                        color: #1e1e2e; 
                        border-radius: 15px; /* Circular aesthetics */
                        font-weight: bold;
                        font-size: 16px;
                    }
                    QPushButton:hover {
                        background-color: #b4befe;
                    }
                """)
                
                # Connect Button using a lambda to capture specific app path/command
                # We usage app['path'] for execution (contains full path or special command)
                open_btn.clicked.connect(lambda checked=False, p=app['path']: self.execute_suggestion(p))
                
                layout.addWidget(name_label)
                layout.addStretch()
                layout.addWidget(open_btn)
                
                item.setSizeHint(widget.sizeHint())
                self.results_list.setItemWidget(item, widget)
            
        else:
            # 3. Direct Execution fallback
            if score > 0.35:
                result_msg = self.commander.execute(intent, entity)
                self.results_list.addItem(f"✅ {result_msg}")
                SoundEngine.play('success')
            else:
                self.results_list.addItem("❓ I'm not sure what you mean.")
            
        self.search_input.clear()

    def execute_suggestion(self, app_name):
        self.results_list.addItem(f"Executing: {app_name}...")
        # Scroll to bottom to show action
        self.results_list.scrollToBottom()
        # Execute
        msg = self.commander.handle_generic_open(app_name)
        # Update status
        self.results_list.addItem(f"✅ {msg}")
        self.results_list.scrollToBottom()
        SoundEngine.play('success')

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

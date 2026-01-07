from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                               QPushButton, QLabel, QLineEdit, QListWidget, QApplication)
from PySide6.QtCore import Qt, QSize, QThread, Signal
from PySide6.QtGui import QColor, QPalette, QFont

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
        self.setWindowTitle("NovaDesk")
        
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
        self.layout.setContentsMargins(10, 10, 10, 15)
        self.layout.setSpacing(5)
        
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
        
        self.setCentralWidget(self.central_widget)
        
        # 6. Sizing
        self.resize(800, 120) 
        self.center_on_screen()
        
        self.load_stylesheet()
        
        # Start Loading AI
        self.loader_thread = LoaderThread()
        self.loader_thread.loaded.connect(self.on_ai_loaded)
        self.loader_thread.start()

    # ... (setup_title_bar, on_ai_loaded, load_stylesheet, center_on_screen remain same)

    def launch_item(self, item):
        text = item.text()
        if "🚀" in text:
            # Parse app name: "🚀 Google Chrome" -> "Google Chrome"
            app_name = text.replace("🚀 ", "").strip()
            
            # Execute via Commander (Generic Open will find it by fuzzy match)
            # This is a shortcut; ideally we store the full path in UserRole
            self.results_list.addItem(f"Executing: {app_name}...")
            msg = self.commander.handle_generic_open(app_name)
            self.results_list.addItem(f"✅ {msg}")

    def setup_title_bar(self):
        self.title_bar = QWidget()
        self.title_bar.setObjectName("TitleBar")
        header_layout = QHBoxLayout(self.title_bar)
        header_layout.setContentsMargins(5, 0, 5, 0)
        
        title_label = QLabel("✨ NovaDesk")
        title_label.setStyleSheet("color: #a6adc8; font-weight: bold; font-size: 13px;")
        
        self.btn_min = QPushButton("－")
        self.btn_min.setObjectName("BtnMinimize")
        self.btn_min.setFixedSize(30, 30)
        self.btn_min.clicked.connect(self.showMinimized)
        
        self.btn_close = QPushButton("✕")
        self.btn_close.setObjectName("BtnClose")
        self.btn_close.setFixedSize(30, 30)
        self.btn_close.clicked.connect(self.close)
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.btn_min)
        header_layout.addWidget(self.btn_close)
        
        self.layout.addWidget(self.title_bar)

    def on_ai_loaded(self, nlp, commander):
        self.nlp = nlp
        self.commander = commander
        self.is_loading = False
        self.search_input.setPlaceholderText("Ask NovaDesk... (e.g. 'Open Spotify')")
        self.search_input.setEnabled(True)
        self.search_input.setFocus()

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
        
        self.results_list.clear() # Clear previous
        self.results_list.show()
        self.resize(800, 300)
        
        # 1. Predict Intent
        intent, score, entity = self.nlp.predict(query)
        print(f"Predicted: {intent} ({score}) -> {entity}")

        # 2. Get Candidates (The Smart Suggestion Step)
        candidates = self.commander.fetch_candidates(intent, entity)
        
        if candidates:
            self.results_list.addItem(f"✨ Found {len(candidates)} suggestions for '{query}':")
            for app in candidates:
                # Add clickable item
                # Format: "[App Name]  --  (Click to Open)"
                item_text = f"🚀 {app['name']}"
                self.results_list.addItem(item_text)
                
                # Store data in item (using separate logic in a minute, for now just text)
                # Ideally we sublcass QListWidgetItem, but for simplicity we'll just handle clicks via text matching
                # or lazy execution:
            
            # Auto-click handling logic needs to be in a separate slot (on_item_clicked)
            # We will wire that up in __init__
            
        else:
            # 3. Direct Execution fallback if no suggestions (e.g. System Control)
            if score > 0.35:
                result_msg = self.commander.execute(intent, entity)
                self.results_list.addItem(f"✅ {result_msg}")
            else:
                self.results_list.addItem("❓ I'm not sure what you mean.")
            
        self.search_input.clear()

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

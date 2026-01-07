import sys
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
                               QLineEdit, QListWidget, QApplication)
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

        # 1. Window Flags: Frameless, Always on Top
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # 2. Central Widget & Layout
        self.central_widget = QWidget()
        self.central_widget.setObjectName("CentralWidget")
        
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
        self.search_input.setPlaceholderText("Initializing Brain... please wait")
        self.search_input.setEnabled(False) # Disable until model loads
        self.search_input.returnPressed.connect(self.process_command)
        
        # 4. Results List
        self.results_list = QListWidget()
        self.results_list.hide()
        
        self.layout.addWidget(self.search_input)
        self.layout.addWidget(self.results_list)
        
        self.setCentralWidget(self.central_widget)
        
        # 5. Sizing & Positioning
        self.resize(700, 80)
        self.center_on_screen()
        
        self.load_stylesheet()
        
        # Start Loading AI in Background
        self.loader_thread = LoaderThread()
        self.loader_thread.loaded.connect(self.on_ai_loaded)
        self.loader_thread.start()

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
        
        self.results_list.addItem(f"Thinking: '{query}'...")
        self.results_list.show()
        self.resize(700, 300)
        
        # 1. Predict Intent
        intent, score, entity = self.nlp.predict(query)
        
        # 2. Heuristic Override: Single Word App Launch
        # If confidence is low, but the query itself is a valid app, treat as Open App.
        if score < 0.4:
            # Check if the raw query matches an app
            # (Note: we access the indexer safely via commander)
            potential_app = self.commander.indexer.find_best_match(query)
            if potential_app:
                intent = "OPEN_APP"
                entity = query
                score = 0.99 # Boost confidence
                self.results_list.addItem(f"💡 Recognized App: {query}")

        self.results_list.addItem(f"Intent: {intent} ({score:.2f}) | Entity: {entity}")
        self.results_list.scrollToBottom()

        # 3. Execute
        if score > 0.3: # Confidence threshold
            result_msg = self.commander.execute(intent, entity)
            self.results_list.addItem(f"✅ {result_msg}")
        else:
            self.results_list.addItem("❓ I'm not sure what you mean.")
            
        self.search_input.clear()
        self.results_list.scrollToBottom()

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

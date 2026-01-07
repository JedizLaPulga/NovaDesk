import os
import subprocess
import ctypes
import webbrowser
import shutil
import difflib

class AppIndexer:
    def __init__(self):
        self.app_map = {} # {'chrome': 'path/to/chrome.lnk', ...}
        self.common_aliases = {
            "browser": ["google chrome", "microsoft edge", "firefox", "brave"],
            "internet": ["google chrome", "microsoft edge"],
            "editor": ["visual studio code", "notepad++", "notepad"],
            "calc": ["calculator"],
            "music": ["spotify", "youtube music"],
            "term": ["windows terminal", "powershell", "cmd"]
        }
        self.scan_start_menu()

    def scan_start_menu(self):
        """
        Scans common Windows Start Menu locations for .lnk files.
        """
        # Common locations for shortcuts
        paths = [
            os.path.join(os.environ['ProgramData'], r'Microsoft\Windows\Start Menu\Programs'),
            os.path.join(os.environ['APPDATA'], r'Microsoft\Windows\Start Menu\Programs')
        ]

        print("Indexing Apps...")
        for root_path in paths:
            if not os.path.exists(root_path): continue
            
            for root, dirs, files in os.walk(root_path):
                for file in files:
                    if file.endswith(".lnk"):
                        # Clean name: "Google Chrome.lnk" -> "google chrome"
                        name = file.lower().replace(".lnk", "")
                        full_path = os.path.join(root, file)
                        self.app_map[name] = full_path
        print(f"Index complete: {len(self.app_map)} apps found.")

    def find_best_match(self, query):
        query = query.lower()
        
        # 1. Direct Alias Lookup
        if query in self.common_aliases:
            # Try to find one of the aliased apps in our index
            for candidate in self.common_aliases[query]:
                best_match = self._fuzzy_search(candidate)
                if best_match: return best_match

        # 2. Fuzzy Search in App Map
        return self._fuzzy_search(query)

    def _fuzzy_search(self, query):
        # Exact match check first
        if query in self.app_map:
            return self.app_map[query]
            
        # Containment check ("chrome" in "google chrome")
        candidates = [name for name in self.app_map if query in name]
        if candidates:
            # Return shortest match (likely the most relevant, e.g. "Word" vs "Wordpad")
            candidates.sort(key=len)
            return self.app_map[candidates[0]]
            
        # Difflib close match (typo tolerance)
        matches = difflib.get_close_matches(query, self.app_map.keys(), n=1, cutoff=0.6)
        if matches:
            return self.app_map[matches[0]]
            
        return None

class Commander:
    def __init__(self):
        self.indexer = AppIndexer()

    def execute(self, intent, entity):
        print(f"Commander received: {intent} -> {entity}")
        
        if intent == "OPEN_APP":
            return self.open_app(entity)
        elif intent == "SEARCH_FILE":
            return self.search_file(entity)
        elif intent == "WEB_SEARCH":
            return self.web_search(entity)
        elif intent == "SYSTEM_CONTROL":
            return self.system_control(entity)
        else:
            return "I'm not sure how to do that yet."

    def open_app(self, app_name):
        # 1. Try resolving via AppIndexer
        path = self.indexer.find_best_match(app_name)
        
        if path:
            try:
                os.startfile(path)
                return f"Launching {os.path.basename(path)}..."
            except Exception as e:
                return f"Error launching app: {e}"
        
        # 2. If index fails, try raw command (e.g. 'calc', 'notepad')
        # Windows Run can handle these directly
        try:
            os.startfile(app_name) 
            return f"Launching system command '{app_name}'..."
        except:
            return f"Could not find app called '{app_name}'."

    def web_search(self, query):
        url = f"https://www.google.com/search?q={query}"
        webbrowser.open(url)
        return f"Searching Google for: {query}"

    def system_control(self, command):
        cmd = command.lower()
        if "lock" in cmd:
            ctypes.windll.user32.LockWorkStation()
            return "PC Locked."
        elif "shutdown" in cmd:
            return "Shutdown command recognized (Simulated)."
        return "System command not fully implemented."

    def search_file(self, filename):
        return f"File search for '{filename}' coming shortly."

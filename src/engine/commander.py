import os
import subprocess
import ctypes
import webbrowser
import shutil
import difflib
from src.engine.knowledge_base import INTENT_DB

class AppIndexer:
    def __init__(self):
        self.app_map = {} 
        self.scan_start_menu()

    def scan_start_menu(self):
        paths = [
            os.path.join(os.environ['ProgramData'], r'Microsoft\Windows\Start Menu\Programs'),
            os.path.join(os.environ['APPDATA'], r'Microsoft\Windows\Start Menu\Programs')
        ]
        
        # Also auto-add common windows apps that might not have shortcuts
        self.app_map["notepad"] = "notepad.exe"
        self.app_map["calculator"] = "calc.exe"
        self.app_map["cmd"] = "cmd.exe"
        self.app_map["powershell"] = "powershell.exe"
        self.app_map["explorer"] = "explorer.exe"

        for root_path in paths:
            if not os.path.exists(root_path): continue
            for root, dirs, files in os.walk(root_path):
                for file in files:
                    if file.endswith(".lnk"):
                        name = file.lower().replace(".lnk", "")
                        self.app_map[name] = os.path.join(root, file)

    def fuzzy_find(self, query):
        if not query: return None
        query = query.lower()
        
        # 1. Exact Access
        if query in self.app_map: return self.app_map[query]
        
        # 2. Substring Search
        candidates = [name for name in self.app_map if query in name]
        if candidates:
            candidates.sort(key=len)
            return self.app_map[candidates[0]]
            
        return None

class Commander:
    def __init__(self):
        self.indexer = AppIndexer()

    def execute(self, intent_id, entity):
        print(f"Commander received: {intent_id} -> {entity}")
        
        if intent_id not in INTENT_DB:
            return f"Unknown intent: {intent_id}"
            
        intent_data = INTENT_DB[intent_id]
        action_type = intent_data["action"]
        targets = intent_data["targets"]
        
        if action_type == "open_priority_app":
            return self.handle_priority_app(targets)
        elif action_type == "system_uri":
            return self.handle_uri(targets[0])
        elif action_type == "key_press":
            return self.handle_keypress(targets[0])
        elif action_type == "win_api":
            return self.handle_win_api(targets[0])
        elif action_type == "generic_search":
            return self.handle_generic_open(entity)
            
        return "Action not implemented."

    def fetch_candidates(self, intent_id, entity):
        candidates = []
        
        if intent_id in INTENT_DB:
            intent_data = INTENT_DB[intent_id]
            targets = intent_data.get("targets", [])
            
            # Category lookups
            if intent_data["action"] == "open_priority_app":
                for app_name in targets:
                    path = self.indexer.fuzzy_find(app_name)
                    if path:
                        display_name = os.path.splitext(os.path.basename(path))[0]
                        # Dedup check
                        if not any(c['path'] == path for c in candidates):
                            candidates.append({"name": display_name, "path": path, "type": "app"})
        
        # Generic fallback
        if not candidates and entity:
            path = self.indexer.fuzzy_find(entity)
            if path:
                display_name = os.path.splitext(os.path.basename(path))[0]
                candidates.append({"name": display_name, "path": path, "type": "app"})

        return candidates

    def handle_priority_app(self, target_list):
        """
        Iterates through the target list (e.g. ['spotify', 'itunes'])
        and tries to launch the first one found in the index.
        """
        for app_name in target_list:
            path = self.indexer.fuzzy_find(app_name)
            if path:
                try:
                    os.startfile(path)
                    return f"Launching {app_name}..."
                except: continue
        
        return f"Could not find any installed app for this category ({target_list[0]})."

    def handle_generic_open(self, app_name):
        path = self.indexer.fuzzy_find(app_name)
        if path:
            os.startfile(path)
            return f"Launching {app_name}..."
        
        try:
            os.startfile(app_name)
            return f"Launching command '{app_name}'..."
        except:
            return f"Could not find app '{app_name}'."

    def handle_uri(self, uri):
        try:
            os.startfile(uri)
            return f"Opening {uri}..."
        except:
            return "Failed to open System URI."

    def handle_keypress(self, key_code):
        import keyboard
        if key_code == "volume_up": keyboard.send("volume up")
        elif key_code == "volume_down": keyboard.send("volume down")
        elif key_code == "volume_mute": keyboard.send("volume mute")
        return f"Executed: {key_code}"

    def handle_win_api(self, api_call):
        if api_call == "lock_workstation":
            ctypes.windll.user32.LockWorkStation()
            return "PC Locked 🔒"
        return "Unknown API call."

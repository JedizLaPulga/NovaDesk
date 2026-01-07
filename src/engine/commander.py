import os
import subprocess
import ctypes
import webbrowser

class Commander:
    def __init__(self):
        pass

    def execute(self, intent, entity):
        """
        Routes the intent to the specific handler.
        """
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
        """
        Uses Windows 'start' command behavior via os.startfile or subprocess.
        """
        try:
            # os.startfile interprets text like the Windows Run dialog
            # This works for "calc", "notepad", "chrome" automatically if in PATH/Registry
            os.startfile(app_name) 
            return f"Launching {app_name}..."
        except FileNotFoundError:
            return f"Could not find application: {app_name}"
        except Exception as e:
            return f"Error launching {app_name}: {e}"

    def web_search(self, query):
        url = f"https://www.google.com/search?q={query}"
        webbrowser.open(url)
        return f"Searching Google for: {query}"

    def system_control(self, command):
        """
        Basic system commands using ctypes for Windows API calls.
        """
        cmd = command.lower()
        
        if "lock" in cmd:
            ctypes.windll.user32.LockWorkStation()
            return "PC Locked."
        elif "shutdown" in cmd:
            # os.system("shutdown /s /t 1") 
            return "Shutdown command recognized (Simulated for safety)."
        
        return "System command not fully implemented yet."

    def search_file(self, filename):
        """
        Placeholder for Windows Search. 
        """
        return f"File search for '{filename}' coming in next update."

# Singleton instance
# commander = Commander()

# The Brains: Valid Intents and their Metadata

INTENT_DB = {
    # --- Applications (Category: open_known) ---
    "APP_BROWSER": {
        "triggers": ["open browser", "start internet", "launch chrome", "go online", "open web"],
        "action": "open_priority_app",
        "targets": ["chrome", "msedge", "firefox", "brave", "opera"]
    },
    "APP_MUSIC": {
        "triggers": ["open music", "play tunes", "start spotify", "launch apple music", "play music"],
        "action": "open_priority_app",
        "targets": ["spotify", "music", "itunes", "aimp", "vlc"] 
    },
    "APP_CODE": {
        "triggers": ["open code", "start coding", "launch vscode", "open editor", "start ide"],
        "action": "open_priority_app",
        "targets": ["code", "visual studio", "sublime", "notepad++", "pycharm", "cursor"]
    },
    "APP_TERMINAL": {
        "triggers": ["open terminal", "start cmd", "open powershell", "command prompt", "run cli"],
        "action": "open_priority_app",
        "targets": ["alacritty", "windowsterminal", "powershell", "cmd", "git bash"]
    },
    "APP_SETTINGS": {
        "triggers": ["open settings", "change preferences", "system config", "control panel"],
        "action": "system_uri",
        "targets": ["ms-settings:", "control"]
    },
    "APP_FILES": {
        "triggers": ["open files", "file explorer", "show documents", "my computer", "explore"],
        "action": "system_uri",
        "targets": ["explorer"]
    },
    "APP_CALC": {
        "triggers": ["open calculator", "calc", "do math"],
        "action": "open_priority_app",
        "targets": ["calculator", "calc"]
    },

    # --- System Control (Category: system) ---
    "SYS_VOLUME_UP": {
        "triggers": ["volume up", "louder", "increase sound", "turn up"],
        "action": "key_press",
        "targets": ["volume_up"]
    },
    "SYS_VOLUME_DOWN": {
        "triggers": ["volume down", "quieter", "lower sound", "turn down"],
        "action": "key_press",
        "targets": ["volume_down"]
    },
    "SYS_MUTE": {
        "triggers": ["mute", "silence", "shut up", "no sound"],
        "action": "key_press",
        "targets": ["volume_mute"]
    },
    "SYS_LOCK": {
        "triggers": ["lock pc", "lock screen", "secure computer", "away"],
        "action": "win_api",
        "targets": ["lock_workstation"]
    },
    "SYS_SHUTDOWN": {
        "triggers": ["shutdown", "turn off computer", "power off"],
        "action": "cmd_exec",
        "targets": ["shutdown /s /t 10"]
    },
    
    # --- Generic Fallbacks ---
    "GENERIC_OPEN": {
        "triggers": ["open", "launch", "start", "run"],
        "action": "generic_search", # Will use spaCy entity extraction
        "targets": []
    },
    "GENERIC_SEARCH": {
        "triggers": ["find", "search for", "where is", "locate"],
        "action": "file_search",
        "targets": []
    }
}

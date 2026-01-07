import PyInstaller.__main__
import os
import shutil

# Clean previous builds
if os.path.exists("app"):
    shutil.rmtree("app")
if os.path.exists("build"):
    shutil.rmtree("build")
if os.path.exists("NovaDesk.spec"):
    os.remove("NovaDesk.spec")

# Define assets
# Format: "source_path;dest_path"
add_data = [
    "img;img",
    "src/ui/styles.qss;src/ui",
    "src/engine/model_cache;src/engine/model_cache"
]

# Formatting --add-data args
ws = ";" # Windows Separator
data_args = []
for d in add_data:
    src, dest = d.split(";")
    data_args.append(f"--add-data={src}{ws}{dest}")

# Run PyInstaller
print("Building NovaDesk.exe...")

args = [
    "run.py",                       # Script
    "--name=NovaDesk",              # Name
    "--onefile",                    # Single Exe
    "--noconsole",                  # No Terminal
    "--distpath=app",               # Output Dir
    "--clean",                      # Clean Cache
    "--hidden-import=spacy",        # Hidden Imports
    "--hidden-import=en_core_web_sm",
    "--hidden-import=speech_recognition",
    "--hidden-import=pyaudio",
    "--hidden-import=isort",        # Often needed for clean imports
] + data_args

# Add Icon if exists (optional but good context)
if os.path.exists("img/NovaDesk.ico"):
    args.append("--icon=img/NovaDesk.ico")

PyInstaller.__main__.run(args)

print("Build Complete! Check the 'app' folder.")

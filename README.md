# NovaDesk 🚀

**Your Intelligent Desktop Companion**

NovaDesk is a modern, AI-powered spotlight search replacement designed exclusively for **Windows 10 & 11**. It combines a sleek, frameless UI with a fast, CPU-optimized neural network to understand your intent and control your system.

## 🌟 Key Features

*   **Natural Language Control:** Type "Open Chrome", "Find that invoice pdf", or "Turn up the volume" — no rigid syntax required.
*   **Built for Windows:** Deep integration with Windows APIs (`win32`, `ctypes`) for maximum performance on Windows 10/11.
*   **Lightweight & Private:** Powered by `all-MiniLM-L6-v2` (running locally via ONNX/PyTorch). Your data never leaves your machine.
*   **Visual Excellence:** A stunning, dark-themed, glass-morphic interface built with **PySide6**.
*   **Portable:** Compiles to a standalone single-file `.exe` — no Python installation required for end users.

## 🛠️ Technology Stack

*   **UI:** PySide6 (Qt for Python) with custom QSS styling.
*   **AI Engine:** `sentence-transformers` (MiniLM) for Intent Classification.
*   **System Backend:** `pywin32`, `ctypes`, and `subprocess`.
*   **Packaging:** PyInstaller (optimized for one-file distribution).

## 🚀 Getting Started

### Prerequisites
*   Windows 10 or 11
*   Python 3.9+

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/JedizLaPulga/NovaDesk.git
    cd NovaDesk
    ```

2.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

    *Note: For the final build, we will use a dedicated script to ensure only necessary libraries are packaged.*

3.  **Run Development Mode:**
    ```bash
    python run.py
    ```

## 📦 Building for Distribution

To create the standalone `.exe`:

```bash
pyinstaller --noconfirm --onefile --windowed --name "NovaDesk" --add-data "src/ui/styles.qss;src/ui" --clean run.py
```

## 📝 Roadmap

*   [x] **Core UI:** Frameless, sophisticated search bar.
*   [ ] **AI Integration:** Local intent classification engine (MiniLM).
*   [ ] **Windows Integration:** File search (Search Index implementation) and Process Management.
*   [ ] **Optimization:** Convert AI models to ONNX for smaller executable size.

---

*Designed with ❤️ for efficiency.*

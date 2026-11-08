# ✦ Afnan's AI - Autonomous Neural Assistant

A futuristic, cyberpunk-styled local AI assistant created for **Afnan**. Designed with an adaptive compute engine supporting both **Hardware Accelerated GPU Mode** and **CPU Mode for non-GPU laptops**.

Features both a **Futuristic Native Windows Desktop GUI (PyQt6)** and a **Web GUI (Streamlit)** with background SQLite persistence, token streaming, and neural persona switching.

---

## ⚡ Key Highlights

- **Futuristic Cyberpunk Interface**: Deep obsidian dark mode (`#060810`), neon cyan accents (`#00F0FF`), glowing borders, and modern glassmorphic cards.
- **Adaptive Compute Engine (GPU & CPU Modes)**:
  - 🚀 **GPU Mode (Accelerated)**: Leverages GPU acceleration for ultra-low latency (~60-80 tokens/sec) and minimal resource footprint (~574 MB VRAM).
  - 💻 **CPU Mode (Universal)**: Offloads 0 GPU layers, running 100% on system RAM so it runs on any non-GPU laptop or low-power device.
- **Clean Interface (Zero Hardware Clutter)**: Raw technical model specs, VRAM figures, and driver numbers are hidden, replaced by clean, high-tech status indicators (`● NEURAL LINK: ACTIVE`).
- **Background SQLite Database**: Automatically saves all conversations and messages to `data/chatbot.db`.
- **Session Vault**: Browse past chat history, start new conversations, and export to Markdown or JSON.
- **Neural Personas**:
  - 🌟 **General Helper**: Balanced, intuitive assistant for everyday tasks.
  - 💻 **Code & Bug Assistant**: Python, JS, C++, ML pipelines, syntax debugging, and software design.
  - 🧠 **Concept Explainer**: Explains complex theories in intuitive ELI5 analogies.
  - ⚡ **Quick Answer Bot**: Zero fluff, high-density facts and steps.
  - 📝 **Writing & Brainstormer**: Drafts executive briefs, essays, and creative copy.

---

## 🚀 How to Launch Afnan's AI

Go to the project folder:  
📁 [c:/Users/hp/Desktop/Github projects/ML/ai-helper-chatbot](file:///c:/Users/hp/Desktop/Github%20projects/ML/ai-helper-chatbot)

### Option 1: Native Desktop Neural Interface (Recommended)
Double-click [run_desktop.bat](file:///c:/Users/hp/Desktop/Github%20projects/ML/ai-helper-chatbot/run_desktop.bat) or run:
```powershell
& "C:\Users\hp\miniconda3\envs\ml\python.exe" desktop_app.py
```

### Option 2: Web Browser Interface
Double-click [run_web.bat](file:///c:/Users/hp/Desktop/Github%20projects/ML/ai-helper-chatbot/run_web.bat) or run:
```powershell
& "C:\Users\hp\miniconda3\envs\ml\Scripts\streamlit.exe" run web_app.py
```
Then open [http://localhost:8501](http://localhost:8501) in your browser.

---

## 💻 Running on Non-GPU Laptops (CPU Mode)

If using a laptop without an NVIDIA GPU:
1. Open **Afnan's AI** (either Desktop or Web GUI).
2. Under **`// COMPUTE ENGINE`** in the sidebar, select **`💻 CPU Mode (Universal / Low Power)`**.
3. The engine automatically routes 100% of the inference to your CPU and RAM (`gpu_layers: 0`). Your preference is remembered automatically in the background SQLite database!

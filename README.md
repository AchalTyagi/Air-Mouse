# 🖐️ AirMouse – Virtual Mouse Using Hand Gestures

AirMouse is a Python-based virtual mouse that allows you to control your computer cursor using **hand gestures captured through a webcam**. It uses **computer vision and hand tracking** to move the mouse and perform click actions—no physical mouse required.

---

## 🚀 Features

- Move mouse cursor using **index finger**
- Perform **mouse click** using thumb–index finger gesture
- Real-time hand tracking via webcam
- Smooth and intuitive interaction
- Lightweight and beginner-friendly project

---

## 🧠 How It Works

- The webcam captures live video frames
- MediaPipe detects hand landmarks
- The **index finger tip (Landmark 8)** controls cursor movement
- When the **thumb tip (Landmark 4)** comes close to the index finger, a click is triggered
- PyAutoGUI maps hand coordinates to screen coordinates

---

## 🛠️ Tech Stack

- **Python**
- **OpenCV** – Video capture & image processing
- **MediaPipe** – Hand landmark detection
- **PyAutoGUI** – Mouse control automation

---

## 📦 Installation

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/AchalTyagi/AirMouse.git
cd AirMouse
```

### 2️⃣ Install Dependencies
```bash
pip install opencv-python mediapipe pyautogui
```
⚠️ Make sure your webcam is working properly before running the script.

---

### ▶️ Usage
Run the script using:
```bash
python AirMouse.py
```

Controls
🖱️ Move Cursor: Move your index finger
👆 Left Click: Bring thumb and index finger close together
❌ Exit Program: Press q on the keyboard

---

### ⚠️ Notes & Limitations

Works best in good lighting
Sudden hand movements may cause jitter
Click delay is intentionally added to avoid multiple clicks
Cursor movement speed can be fine-tuned in the code

---

### 🔮 Future Improvements

Add right-click and scroll gestures
Improve cursor smoothing
Support multi-hand detection
Add gesture-based shortcuts
Convert into a desktop application

---

### 🙌 Acknowledgements

MediaPipe Hands by Google
OpenCV Community
PyAutoGUI Developers

---

### 📜 License
This project is open-source and available under the MIT License.

# Security Sentinel AI

**Real-time security surveillance system with YOLOv8 threat detection and instant Telegram alerts.**

---

## 🎯 Features

### **Dual Operating Modes**
- **📹 Live Webcam Monitoring** - Real-time threat detection from your webcam
- **📤 Video Upload Analysis** - Process pre-recorded videos with YOLO detections

### **Threat Detection**
The system triggers alerts for these specific conditions:
- ✅ **Person + Knife** detected together
- ✅ **Person + Weapon (Gun)** detected together
- ✅ **Balaclava** detected (standalone)
- ✅ **Phone** detected (standalone)

### **Telegram Integration**
- 📸 Instant photo alerts sent to your Telegram chat
- 🕐 5-second cooldown to prevent spam
- 📝 Detailed captions with threat type and timestamp

### **Video Processing**
- 🎬 Upload videos (MP4, AVI, MOV, MKV)
- 🎨 Real-time YOLO annotation overlay
- ⬇️ Download processed videos with detections burned in
- 📁 Automatic file management with unique timestamps

### **Professional UI**
- 🎨 Natural color palette (Sage Green, Slate Blue)
- 📊 Live detection logs
- 📱 Responsive design
- 🔄 Smooth mode switching

---

## 📦 Installation

### **Prerequisites**
- Python 3.8 or higher
- Webcam (for live mode)
- Telegram Bot (for alerts)

### **1. Clone the Repository**
```bash
git clone https://github.com/SamiAwawda/Security-Sentinel-AI.git
cd Security-Sentinel-AI
```

### **2. Install Dependencies**
```bash
pip install -r requirements.txt
```

**Packages installed:**
- Flask (web framework)
- opencv-python (video processing)
- ultralytics (YOLOv8)
- requests (Telegram API)
- numpy & Pillow (image processing)

### **3. Download Your YOLOv8 Model**
Place your trained `best.pt` model file in the project root directory.

---

## ⚙️ Configuration

### **Telegram Bot Setup**

**1. Create a Telegram Bot:**
- Open Telegram and search for `@BotFather`
- Send `/newbot` and follow prompts
- Copy your bot token (e.g., `123456789:ABCdef...`)

**2. Get Your Chat ID:**
- Search for `@userinfobot` on Telegram
- Start a chat and copy your `Id` number

**3. Update `app.py` (Lines 20-21):**
```python
TELEGRAM_BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
CHAT_ID = "YOUR_CHAT_ID_HERE"
```

---

## 🚀 Usage

### **Start the Server**
```bash
python app.py
```

Expected output:
```
==================================================
🛡️  SECURITY SENTINEL AI
==================================================
✅ Model loaded successfully from best.pt
✅ Camera initialized successfully (index: 0)
📡 Access dashboard at: http://localhost:5000
==================================================
```

### **Access the Dashboard**
Open your browser and navigate to:
```
http://localhost:5000
```

### **Live Webcam Mode**
1. Click "📹 Live Webcam" (default mode)
2. Webcam feed starts automatically
3. Detections appear in real-time
4. Threats trigger Telegram alerts

### **Video Upload Mode**
1. Click "📤 Upload Video"
2. Select a video file (MP4, AVI, MOV, MKV)
3. Click "Upload & Process Video"
4. Watch processing in real-time
5. Download processed video when complete

---

## 📁 Project Structure

```
Security-Sentinel-AI/
├── app.py                  # Flask backend
├── templates/
│   └── index.html         # Frontend dashboard
├── uploads/               # User uploaded videos (auto-created)
├── processed/             # Processed output videos (auto-created)
├── best.pt                # YOLOv8 model (you provide)
├── requirements.txt       # Python dependencies
├── SETUP_GUIDE.md        # Detailed setup instructions
└── .gitignore            # Git exclusions
```

---

## 🎨 Technical Details

### **Performance Optimization**
- **Camera Resolution:** 640x480 (optimized for speed)
- **Inference Size:** 320px (real-time processing)
- **FPS:** 15-25 (live mode), 10-20 (upload mode)

### **Video Processing**
- Uses `cv2.VideoWriter` to save annotated frames
- Supports multiple concurrent uploads
- Unique timestamped filenames prevent overwrites
- Max upload size: 500MB

### **Threat Detection Logic**
```python
# Condition priorities:
1. Balaclava (highest)
2. Person + Knife
3. Person + Weapon
4. Phone (standalone)
```

### **File Storage**
- No database required
- Local file system management
- `uploads/` excluded from Git
- `processed/` excluded from Git

---

## 🧪 Testing

Comprehensive testing guide available in `testing_guide.md`.

**Quick Test:**
```bash
# Test webcam
python app.py
# Open http://localhost:5000
# Show your phone to the camera
# Check Telegram for alert
```

---

## 🔧 Troubleshooting

### Camera Not Working
```bash
# Check camera access
ls -l /dev/video0

# Test with OpenCV
python -c "import cv2; cap = cv2.VideoCapture(0); print('OK' if cap.isOpened() else 'FAIL')"
```

### Upload Fails
- Check file size (<500MB)
- Verify file extension (mp4, avi, mov, mkv)
- Ensure sufficient disk space

### Telegram Alerts Not Sending
- Verify bot token and chat ID are correct
- Message your bot first (start a conversation)
- Check console for API errors

### Flask Reloader Issues
**Fixed:** `use_reloader=False` prevents camera conflicts

---

## 🛡️ Security Notes

- **Keep your bot token secret** - Never commit to Git
- **Chat ID privacy** - Don't share publicly
- **Local storage** - Videos stored locally (not cloud)
- **Network access** - Runs on `0.0.0.0` for network accessibility

---

## 📝 License

This project is open source. Feel free to modify and distribute.

---

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

---

## 📧 Contact

**Developer:** Sami Awawda  
**Email:** samitur02@gmail.com  
**GitHub:** [@SamiAwawda](https://github.com/SamiAwawda)

---

## 🙏 Acknowledgments

- **Ultralytics YOLOv8** - Object detection framework
- **Flask** - Web framework
- **OpenCV** - Computer vision library
- **Telegram Bot API** - Alert system

---

## 📊 System Requirements

**Minimum:**
- CPU: Dual-core 2.0 GHz
- RAM: 4 GB
- Disk: 2 GB free space
- OS: Linux, macOS, Windows

**Recommended:**
- CPU: Quad-core 3.0 GHz
- RAM: 8 GB
- GPU: NVIDIA (CUDA support for faster inference)
- Disk: 10 GB free space

---

**Built with ❤️ for security and surveillance applications**

🛡️ **Stay Safe!**

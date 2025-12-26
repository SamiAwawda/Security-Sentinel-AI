# 🛡️ Security Sentinel AI - Forensic Edition

**Professional forensic surveillance system with YOLOv8 threat detection, pre-event video recording, instant Telegram photo alerts, and comprehensive video gallery.**

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/flask-3.0-green.svg)](https://flask.palletsprojects.com/)
[![YOLOv8](https://img.shields.io/badge/YOLOv8-Ultralytics-purple.svg)](https://github.com/ultralytics/ultralytics)

---

## 🎯 Key Features

### **🎥 Forensic Video Recording**
- **5-Second Pre-Event Buffer** - Captures what happened BEFORE threat detection
- **5-Second Post-Event Recording** - Documents response and outcome
- **Ring Buffer Technology** - Continuous 100-frame memory loop
- **YOLO Annotations Burned In** - All saved videos include detection overlays
- **Local Storage** - Videos saved to `alerts/` folder for later review

### **📸 Instant Telegram Photo Alerts**
- **Photo-Based Alerts** - Fast, data-efficient (2-3 seconds delivery)
- **Annotated Snapshots** - Bounding boxes included in alerts
- **Smart Cooldown** - 5-second post-recording cooldown prevents spam
- **Detailed Captions** - Threat type, timestamp, forensic video confirmation

### **🎬 Video Gallery**
- **Web-Based Review** - Browse all saved forensic videos
- **Video Player Modal** - Play videos directly in browser
- **Metadata Display** - Size, date, threat type for each video
- **Delete Management** - Remove unwanted videos to free space
- **Dual Folder Support** - View alerts + processed videos

### **🎨 Modern Landing Page**
- **3 Operating Modes:**
  - 📹 **Live Webcam** - Real-time surveillance with lazy-loaded camera
  - � **Upload Video** - Analyze pre-recorded footage
  - 🎬 **Video Gallery** - Review saved forensic evidence
- **Lazy Camera Loading** - Camera only activates when webcam mode selected
- **Mode Switching** - Easy navigation with "Back to Home" button

### **🔊 Audio Alarms**
- **Frontend Beep** - Audible alert when threat detected
- **Visual Indicators** - Flashing red "RECORDING ALERT" badge
- **Non-intrusive** - Plays once per threat event

### **🎯 Threat Detection**
Alerts trigger for these specific conditions:
- ✅ **Person + Knife** detected together
- ✅ **Person + Weapon (Gun)** detected together
- ✅ **Balaclava** detected (standalone)
- ✅ **Phone** detected (standalone)

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
- `Flask` - Web framework
- `opencv-python` - Video processing
- `ultralytics` - YOLOv8 engine
- `requests` - Telegram API communication
- `numpy` & `Pillow` - Image processing

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

**3. Update `app.py` (Lines 23-24):**
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
🛡️  SECURITY SENTINEL AI - FORENSIC MODE
==================================================
✅ Model loaded successfully from best.pt
📋 Detected classes: {0: 'Balaclava', 1: 'Gun', ...}
✅ Camera initialized successfully (index: 0)
� Resolution: 640x480

🚀 Starting Forensic Alert System...
�📡 Access dashboard at: http://localhost:5000
⚡ Performance: Resolution=640x480, Inference=320px
🎥 Forensic Recording: 5s before + 5s after detection
📹 Ring Buffer Size: ~100 frames
==================================================
```

### **Access the Dashboard**
Open your browser and navigate to:
```
http://localhost:5000
```

### **Choose Your Mode**

**📹 Live Webcam Mode:**
1. Click "Live Webcam" on landing page
2. Camera activates and feed starts
3. Real-time detections appear
4. Threats trigger:
   - 🔊 Audio alarm (frontend)
   - 📸 Telegram photo alert (instant)
   - 🎥 Forensic video recording (10s total)

**📤 Video Upload Mode:**
1. Click "Upload Video"
2. Select file (MP4, AVI, MOV, MKV)
3. Click "Upload & Process Video"
4. Watch real-time processing
5. Download processed video with annotations

**🎬 Video Gallery Mode:**
1. Click "Video Gallery"
2. Browse all saved forensic videos
3. Click "▶ Play" to watch in modal
4. Click "🗑️" to delete unwanted videos
5. View metadata (date, size, threat type)

---

## 📁 Project Structure

```
Security-Sentinel-AI/
├── app.py                      # Flask backend with forensic logic
├── templates/
│   ├── index.html             # Landing page & dashboard
│   └── gallery.html           # Video gallery interface
├── alerts/                    # Forensic alert videos (auto-created)
│   ├── alert_Phone_Detected_20251226_183710.mp4
│   └── alert_Person_Knife_20251226_192345.mp4
├── uploads/                   # User uploaded videos (auto-created)
├── processed/                 # Processed output videos (auto-created)
├── best.pt                    # YOLOv8 model (you provide)
├── requirements.txt           # Python dependencies
├── README.md                  # This file
└── .gitignore                # Git exclusions (alerts/ included)
```

---

## 🎨 Technical Details

### **Forensic Recording Architecture**

**Ring Buffer Implementation:**
```python
from collections import deque

# Initialize buffer
frame_buffer = deque(maxlen=100)  # 5s at 20 FPS

# Continuous filling
while True:
    annotated_frame = yolo_model.plot()
    frame_buffer.append(annotated_frame.copy())  # Always has last 5s
```

**Alert Workflow:**
```
Threat Detected
   ↓
Instant Telegram Photo (2-3s) ←─────────────┐
   ↓                                         │
Dump Ring Buffer (5s pre-event)              │  Non-blocking
   ↓                                         │  Threading
Record Post-Event (5s)                       │
   ↓                                         │
Save MP4 (mp4v codec) ─────────────────────┘
   ↓
Cooldown (5s)
   ↓
Ready for Next Alert
```

### **Performance Optimization**
- **Camera Resolution:** 640x480 (speed optimized)
- **Inference Size:** 320px (real-time processing)
- **FPS:** 15-25 (live), 10-20 (upload)
- **Buffer Memory:** ~90MB RAM (100 frames × 900KB)
- **Video Codec:** mp4v (Telegram compatible)

### **Video Storage**
- **Alert Videos:** `alerts/alert_[ThreatType]_[Timestamp].mp4`
- **Processed Videos:** `processed/processed_[Filename]_[Timestamp].mp4`
- **File Size:** ~500KB - 2MB per 10s clip
- **Retention:** Manual deletion via gallery

### **Threat Detection Logic**
```python
# Priority order (highest to lowest)
1. Balaclava (immediate alert)
2. Person + Knife (combination)
3. Person + Weapon (combination)
4. Phone (standalone)
```

---

## 🎯 API Endpoints

### **Frontend Routes**
- `GET /` - Landing page with mode selection
- `GET /gallery` - Video gallery interface
- `GET /video_feed/<mode>` - Live video stream (MJPEG)

### **API Routes**
- `GET /api/videos` - List all forensic videos (JSON)
- `GET /video/<folder>/<filename>` - Serve video file for playback
- `DELETE /delete_video/<folder>/<filename>` - Delete video
- `GET /logs` - Detection logs (JSON)
- `GET /threat_status` - Active threat status (for audio alarm)

### **Upload Routes**
- `POST /upload` - Upload video file
- `GET /download_processed` - Download processed video

---

## 🧪 Testing

### **Test Forensic Recording**
```bash
python app.py
# 1. Open http://localhost:5000
# 2. Click "Live Webcam"
# 3. Show phone to camera
# 4. Wait for "🎥 Starting forensic recording..."
# 5. Check console for "✅ Forensic video saved"
# 6. Click "Video Gallery" to verify
```

**Expected Console Output:**
```
🎥 Starting forensic recording: alert_Phone_Detected_20251226_183758.mp4
📹 Writing 100 pre-event frames WITH ANNOTATIONS...
📹 Recording 5s post-event (100 frames)...
✅ Telegram photo alert sent: Phone Detected
✅ Forensic video saved: alerts/alert_Phone_Detected_20251226_183758.mp4
```

### **Test Video Gallery**
```bash
# 1. Navigate to http://localhost:5000/gallery
# 2. Verify videos are listed
# 3. Click "▶ Play" on any video
# 4. Verify video plays in modal
# 5. Close modal, click "🗑️" to test delete
```

---

## 🔧 Troubleshooting

### **Camera Not Working**
```bash
# Check camera access
ls -l /dev/video0

# Test with OpenCV
python -c "import cv2; cap = cv2.VideoCapture(0); print('OK' if cap.isOpened() else 'FAIL')"

# Fix permissions
sudo usermod -a -G video $USER
```

### **Telegram Photo Not Sending**
- Verify bot token and chat ID are correct
- Message your bot first (start a conversation)
- Check console for "✅ Telegram photo alert sent"
- Look for API errors in console

### **Video Gallery Empty**
- Trigger at least one threat detection first
- Check `alerts/` folder exists and contains .mp4 files
- Verify browser console for API errors
- Try refreshing the page

### **Ring Buffer Issues**
```python
# Check buffer is filling (add to app.py for debug)
print(f"Buffer size: {len(frame_buffer)} frames")
# Should show ~100 after 5 seconds
```

### **Video Playback Fails**
- Ensure mp4v codec is supported by browser
- Try different browser (Chrome recommended)
- Check file permissions on alerts/ folder
- Verify video file isn't corrupted

---

## 🛡️ Security Notes

- **Keep your bot token secret** - Never commit to Git
- **Chat ID privacy** - Don't share publicly
- **Local storage** - Videos stored locally (not cloud)
- **Network access** - Runs on `0.0.0.0` for LAN accessibility
- **Video retention** - Delete old videos via gallery to free space

---

## 📊 System Requirements

**Minimum:**
- CPU: Dual-core 2.0 GHz
- RAM: 4 GB
- Disk: 5 GB free space (for video storage)
- OS: Linux, macOS, Windows

**Recommended:**
- CPU: Quad-core 3.0 GHz
- RAM: 8 GB
- GPU: NVIDIA (CUDA support for faster inference)
- Disk: 20 GB free space

**Network:**
- Internet: Required for Telegram alerts
- Bandwidth: Minimal (photos only, ~50KB per alert)

---

## 🎬 Feature Comparison

| Feature | Basic Mode | Forensic Mode |
|---------|-----------|---------------|
| **Threat Detection** | ✅ Yes | ✅ Yes |
| **Telegram Alerts** | Photo | Photo |
| **Pre-Event Recording** | ❌ No | ✅ 5 seconds |
| **Post-Event Recording** | ❌ No | ✅ 5 seconds |
| **Video Gallery** | ❌ No | ✅ Yes |
| **Audio Alarms** | ❌ No | ✅ Yes |
| **Landing Page** | Simple | 3-Mode Selector |
| **Video Storage** | Temp only | Permanent |

---

## 📝 License

This project is open source. Feel free to modify and distribute.

---

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

**Suggested Improvements:**
- H.264 video encoding for smaller files
- Person tracking with unique IDs (ByteTrack)
- Multi-camera support
- Cloud storage integration (S3, Drive)
- Email alert notifications
- User management system

---

## 📧 Contact

**Developer:** Sami Awawda  
**Email:** samitur02@gmail.com  
**GitHub:** [@SamiAwawda](https://github.com/SamiAwawda)

---

## 🙏 Acknowledgments

- **Ultralytics YOLOv8** - State-of-the-art object detection
- **Flask** - Lightweight web framework
- **OpenCV** - Computer vision library
- **Telegram Bot API** - Instant notification system
- **Python Community** - Amazing ecosystem

---

## � Roadmap

**Completed:**
- ✅ Forensic pre-event recording
- ✅ Video gallery with playback
- ✅ Telegram photo alerts
- ✅ Audio alarms
- ✅ Landing page mode selection

**Upcoming:**
- 🔄 Person tracking with Re-ID
- 🔄 SQLite incident database
- 🔄 Email alert notifications
- 🔄 Advanced playback controls
- 🔄 Multi-camera support
- 🔄 H.264 encoding

---

**Built with ❤️ for forensic security and surveillance applications**

🛡️ **Stay Safe with Forensic Evidence!**

---

## ⚡ Quick Start

```bash
# 1. Clone
git clone https://github.com/SamiAwawda/Security-Sentinel-AI.git
cd Security-Sentinel-AI

# 2. Install
pip install -r requirements.txt

# 3. Configure Telegram (edit app.py)
TELEGRAM_BOT_TOKEN = "YOUR_TOKEN"
CHAT_ID = "YOUR_ID"

# 4. Run
python app.py

# 5. Open browser
http://localhost:5000

# 6. Choose mode and start monitoring!
```

**Pro Tip:** Place your YOLOv8 `best.pt` model in the root directory before running!

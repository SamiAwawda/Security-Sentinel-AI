# Security Sentinel AI 🛡️

Advanced AI-powered security monitoring system with real-time threat detection, forensic video recording, and multi-camera support.

![Version](https://img.shields.io/badge/version-2.0-blue)
![Python](https://img.shields.io/badge/python-3.8+-green)
![License](https://img.shields.io/badge/license-MIT-blue)

## ✨ Features

### 🎯 Core Features
- **Real-time YOLOv8 Detection** - AI-powered threat identification (Gun, Knife, Balaclava, Phone, Money)
- **Forensic Video Recording** - Pre & post-event buffer capture with annotations
- **Multi-Camera Grid View** - Monitor 1, 2, 4, or 8 cameras simultaneously
- **Instant Telegram Alerts** - Real-time notifications with snapshots
- **SQLite Database** - Persistent alert storage and analytics
- **Glassmorphism UI** - Modern dark security operations center design

### 📹 Advanced Monitoring
- **Smart Streaming** - Only one camera streams at a time (resource efficient)
- **Named Cameras** - Custom locations (School Entrance, Parking Lot, etc.)
- **Optimized Performance** - 640x480 @ 30 FPS, YOLO 320px inference
- **Detection Log** - Real-time threat timeline with color coding
- **Alert Archive** - Complete forensic video library with side-panel preview

### 🎨 Professional Interface
- **Dashboard** - System stats, recent alerts, quick actions
- **Live Monitor** - Multi-camera grid with AI detection overlay
- **Alerts Page** - Integrated video preview with click-to-view panel
- **Settings** - Configuration management and system info

## 📁 Project Structure

```
Project-V2/
├── backend/                    # Backend Python application
│   ├── app/
│   │   ├── __init__.py        # Flask app factory
│   │   ├── config.py          # Configuration (cameras, paths, alerts)
│   │   ├── routes.py          # API endpoints
│   │   └── services/          # Core services
│   │       ├── yolo_service.py       # YOLO inference
│   │       ├── camera_service.py     # Camera management
│   │       ├── recorder_service.py   # Forensic recording
│   │       ├── database_service.py   # SQLite operations
│   │       ├── telegram_service.py   # Telegram alerts
│   │       └── threat_logic.py       # Threat detection rules
│   ├── models/                # YOLO model files
│   ├── database/             # SQLite database
│   ├── storage/              # Video storage
│   │   ├── alerts/          # Forensic videos
│   │   ├── uploads/         # User uploads
│   │   └── processed/       # Processed videos
│   └── run.py               # Application entry point
│
├── frontend/                  # Frontend web interface
│   ├── static/
│   │   ├── css/             # Glassmorphism styles
│   │   └── js/              # Client-side logic
│   └── templates/           # HTML pages
│       ├── dashboard.html
│       ├── monitor.html
│       ├── alerts.html
│       └── settings.html
│
├── README.md
├── SETUP_GUIDE.md
└── requirements.txt
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Webcam or IP camera
- YOLO model (`best.pt`)
- Telegram Bot (optional)

### Installation

```bash
# 1. Clone repository
git clone https://github.com/YOUR_USERNAME/Security-Sentinel-AI.git
cd Security-Sentinel-AI

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Place YOLO model
# Copy your best.pt to backend/models/

# 5. Run application
cd backend
python run.py
```

### Access
- **Dashboard:** http://localhost:5000
- **Live Monitor:** http://localhost:5000/monitor
- **Alerts:** http://localhost:5000/alerts
- **Settings:** http://localhost:5000/settings

## ⚙️ Configuration

Edit `backend/app/config.py`:

```python
# Camera Names
CAMERAS = {
    0: {'name': 'School Entrance', 'location': 'Front Gate'},
    1: {'name': 'Back Hallway', 'location': 'Building A'},
    # ... customize your cameras
}

# Forensic Recording
PRE_EVENT_SECONDS = 5   # Buffer before detection
POST_EVENT_SECONDS = 5  # Record after detection
COOLDOWN_SECONDS = 5    # Alert cooldown

# Telegram (optional)
TELEGRAM_BOT_TOKEN = "your_bot_token"
CHAT_ID = "your_chat_id"
```

## 📊 Camera Optimization

**Settings Applied:**
- Resolution: 640x480 (speed optimized)
- Frame Rate: 30 FPS
- Buffer Size: 1 (minimal latency)
- Auto-exposure: Disabled (consistent FPS)
- YOLO Inference: 320px (4x faster)

**Display:**
- Single view: 720px height (50% larger!)
- Grid views: Responsive layouts
- Resource efficient: Only 1 stream active

## 🎯 Detection Classes

| Class | Threat Level | Alert |
|-------|-------------|-------|
| Gun | CRITICAL | ✅ |
| Knife | CRITICAL | ✅ |
| Balaclava | HIGH | ✅ |
| Phone | MEDIUM | ✅ |
| Money | MEDIUM | ✅ |
| Person | INFO | ❌ |

## 📸 Screenshots

### Dashboard
Modern glassmorphism design with real-time statistics

### Live Monitor
Multi-camera grid view with AI detection overlay

### Alerts Archive
Integrated video preview with forensic evidence

## 🔧 Technology Stack

- **Backend:** Flask (Python)
- **AI/ML:** YOLOv8 (Ultralytics)
- **Computer Vision:** OpenCV
- **Database:** SQLite3
- **Frontend:** HTML5, CSS3 (Glassmorphism), Vanilla JS
- **Notifications:** Telegram Bot API
- **Icons:** Font Awesome

## 📝 Version History

### v2.0.0 (2025-12-29)
- ✨ Multi-camera grid view (1, 2, 4, 8 cameras)
- ✨ Glassmorphism UI redesign
- ✨ Merged gallery into alerts with side panel
- ✨ Camera naming system
- ✨ Smart streaming (resource efficient)
- 🚀 Performance optimization (640x480 @ 30FPS)
- 🚀 Larger video display (720px single view)
- 🐛 Fixed detection log JSON parsing
- 🗑️ Cleaned up unused files

### v1.0.0 (2025-12-28)
- Initial release
- YOLOv8 integration
- Forensic recording
- Telegram alerts
- SQLite database

## 🤝 Contributing

Contributions welcome! Please feel free to submit pull requests.

## 📄 License

MIT License - See LICENSE file for details

## 👤 Author

**Sami Awawda**
- GitHub: [@SamiAwawda](https://github.com/SamiAwawda)

## 🙏 Acknowledgments

- YOLOv8 by Ultralytics
- Flask framework
- OpenCV community

---

**⭐ Star this repo if you find it useful!**

Last Updated: 2025-12-29

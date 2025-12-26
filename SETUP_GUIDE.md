# Security Sentinel AI - Setup Guide

A complete guide to setting up and running your Security Sentinel AI surveillance system.

---

## 📋 Table of Contents
1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Telegram Bot Configuration](#telegram-bot-configuration)
4. [Running the Application](#running-the-application)
5. [Testing the System](#testing-the-system)
6. [Troubleshooting](#troubleshooting)

---

## 🔧 Prerequisites

Before you begin, ensure you have the following:

### System Requirements
- **Operating System:** Linux, macOS, or Windows
- **Python Version:** Python 3.8 or higher
- **Webcam:** Built-in or external USB webcam
- **Internet Connection:** Required for Telegram alerts

### Check Python Version
```bash
python --version
# or
python3 --version
```

If Python is not installed, download it from [python.org](https://www.python.org/downloads/).

---

## 📦 Installation

### Step 1: Navigate to Project Directory
```bash
cd /media/sami/72F20DFDF20DC5F7/Users/Sami/Project-V2
```

### Step 2: (Optional but Recommended) Create a Virtual Environment
Creating a virtual environment keeps your dependencies isolated from other Python projects.

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

This will install:
- Flask (Web framework)
- opencv-python (Webcam capture)
- ultralytics (YOLOv8 model)
- requests (Telegram API)
- numpy (Array operations)
- Pillow (Image processing)

### Step 4: Verify Model File
Ensure your trained YOLOv8 model file `best.pt` is in the project root directory:
```bash
ls -lh best.pt
```

If the file is missing, you'll need to place your trained model in the project directory.

---

## 🤖 Telegram Bot Configuration

To receive threat alerts on Telegram, you need to create a bot and get your chat ID.

### Step 1: Create a Telegram Bot

1. Open Telegram and search for **@BotFather**
2. Start a chat and send the command: `/newbot`
3. Follow the prompts:
   - Choose a name for your bot (e.g., "Security Sentinel")
   - Choose a username (must end in 'bot', e.g., "my_security_sentinel_bot")
4. **BotFather will give you a token** that looks like this:
   ```
   123456789:ABCdefGHIjklMNOpqrsTUVwxyz
   ```
5. **Copy this token** — you'll need it in the next step!

### Step 2: Get Your Chat ID

**Option A: Using Your Personal Chat**
1. Search for your bot in Telegram and start a conversation
2. Send any message to your bot (e.g., "Hello")
3. Open this URL in your browser (replace `YOUR_BOT_TOKEN` with your actual token):
   ```
   https://api.telegram.org/botYOUR_BOT_TOKEN/getUpdates
   ```
4. Look for `"chat":{"id":` in the response. The number after `id` is your Chat ID (e.g., `987654321`)

**Option B: Using a Channel**
1. Create a Telegram channel
2. Add your bot as an administrator
3. Post a message in the channel
4. Use the same `getUpdates` URL to find the channel's Chat ID

### Step 3: Update app.py with Your Credentials

Open `app.py` in a text editor and find these lines near the top:
```python
TELEGRAM_BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"  # Replace with your Telegram Bot Token
CHAT_ID = "YOUR_CHAT_ID_HERE"  # Replace with your Telegram Chat ID
```

Replace them with your actual credentials:
```python
TELEGRAM_BOT_TOKEN = "123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
CHAT_ID = "987654321"
```

**⚠️ Important:** Keep these credentials secure! Do not share them publicly.

---

## 🚀 Running the Application

### Step 1: Start the Flask Server
```bash
python app.py
```

You should see output like this:
```
==================================================
🛡️  SECURITY SENTINEL AI
==================================================
✅ Model loaded successfully from best.pt
📋 Detected classes: {0: 'Balaclava', 1: 'Gun', 2: 'Knife', 3: 'Money', 4: 'Person', 5: 'Phone'}
✅ Camera initialized successfully (index: 0)

🚀 Starting Flask server...
📡 Access dashboard at: http://localhost:5000
==================================================
```

### Step 2: Access the Dashboard

Open your web browser and navigate to:
```
http://localhost:5000
```

You should see:
- **Header:** "Security Sentinel AI" with a green status badge
- **Live Camera Feed:** Your webcam stream with YOLOv8 detections
- **Live Detection Logs:** Real-time threat detection timestamps

### Step 3: System is Now Active! 🎉

The system is now monitoring for threats. When one of the following conditions is detected:
- **Person + Knife**
- **Person + Weapon**
- **Balaclava**

The system will:
1. Log the detection with a timestamp
2. Send a photo alert to your Telegram chat
3. Apply a 5-second cooldown before the next alert

---

## 🧪 Testing the System

### Test 1: Verify Video Stream
- Check that your webcam feed is visible in the browser
- Ensure bounding boxes appear around detected objects

### Test 2: Test Threat Detection
To trigger an alert, simulate one of the threat conditions:
- Hold a knife while visible in frame (triggers "Person + Knife")
- Present a weapon with a person visible (triggers "Person + Weapon")
- Display or wear a balaclava (triggers "Balaclava Detected")

### Test 3: Verify Telegram Alerts
- Check your Telegram chat/channel
- You should receive a photo with a caption like:
  ```
  🚨 THREAT DETECTED: Person + Knife
  🕐 Time: 2025-12-25 18:15:30
  ```

### Test 4: Verify Cooldown Mechanism
- Trigger multiple detections within 5 seconds
- Verify only ONE alert is sent
- Wait 5 seconds, trigger again
- A new alert should be sent

---

## 🔧 Troubleshooting

### Issue 1: "Failed to load model"
**Problem:** Model file not found or corrupted

**Solution:**
- Verify `best.pt` exists in the project directory
- Check file permissions:
  ```bash
  ls -l best.pt
  ```
- Ensure the model is a valid YOLOv8 model

---

### Issue 2: "Failed to initialize camera"
**Problem:** Camera is not accessible

**Solutions:**
1. **Check if camera is in use by another application:**
   - Close other apps using the camera (Zoom, Skype, etc.)

2. **Verify camera permissions (Linux):**
   ```bash
   ls -l /dev/video0
   sudo usermod -a -G video $USER
   ```
   Then log out and log back in.

3. **Try a different camera index:**
   In `app.py`, change:
   ```python
   CAMERA_INDEX = 0  # Try 1, 2, etc.
   ```

4. **Test camera with OpenCV:**
   ```bash
   python -c "import cv2; cap = cv2.VideoCapture(0); print('Success!' if cap.isOpened() else 'Failed'); cap.release()"
   ```

---

### Issue 3: Telegram Alerts Not Sending
**Problem:** Photos not appearing in Telegram

**Solutions:**
1. **Verify credentials are correct:**
   - Double-check your `TELEGRAM_BOT_TOKEN` and `CHAT_ID`
   - Ensure there are no extra spaces

2. **Test the bot manually:**
   Open this URL in your browser:
   ```
   https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getMe
   ```
   You should see your bot's information.

3. **Check console for errors:**
   Look for messages like:
   ```
   ❌ Telegram API error: 401 - Unauthorized
   ```

4. **Ensure you've messaged your bot first:**
   Send any message to your bot before the first alert

---

### Issue 4: Video Feed Not Loading in Browser
**Problem:** Dashboard shows blank video area

**Solutions:**
1. **Refresh the page** (Ctrl+R or Cmd+R)
2. **Check Flask console for errors**
3. **Try a different browser** (Chrome, Firefox, Edge)
4. **Clear browser cache**

---

### Issue 5: Low Frame Rate / Laggy Video
**Problem:** Video is choppy or slow

**Solutions:**
1. **Reduce inference size:**
   In `app.py`, modify the inference call:
   ```python
   results = model(frame, imgsz=320, verbose=False)  # Smaller size = faster
   ```

2. **Skip frames:**
   Add frame skipping logic in the `generate_frames()` function

3. **Use a smaller YOLOv8 model:**
   - YOLOv8n (nano) is fastest
   - YOLOv8s (small) is a good balance
   - YOLOv8l (large) is most accurate but slower

---

### Issue 6: "Address already in use" Error
**Problem:** Port 5000 is already in use

**Solution:**
Change the port in `app.py`:
```python
app.run(debug=True, threaded=True, host='0.0.0.0', port=5001)  # Use 5001 instead
```

Then access: `http://localhost:5001`

---

## ⚙️ Advanced Configuration

### Change Cooldown Duration
In `app.py`, modify:
```python
COOLDOWN_SECONDS = 10  # Change from 5 to 10 seconds
```

### Customize Detection Classes
Your model detects these classes:
- Balaclava
- Gun  
- Knife
- Money
- Person
- Phone

The threat detection logic is in the `check_threat_conditions()` function. You can customize the conditions as needed.

### Run on Network (Access from Other Devices)
The app is already configured to run on `0.0.0.0`, so it's accessible on your local network.

Find your IP address:
```bash
# Linux/macOS
hostname -I

# Windows
ipconfig
```

Access from another device on the same network:
```
http://YOUR_IP_ADDRESS:5000
```

---

## 🛑 Stopping the Application

To stop the Flask server:
1. Go to the terminal where the app is running
2. Press `Ctrl+C`

The camera will be released automatically.

---

## 📝 Summary

You now have a fully functional Security Sentinel AI system! 

**Key Features:**
✅ Real-time webcam threat detection  
✅ Instant Telegram alerts with photos  
✅ Professional web dashboard  
✅ 5-second cooldown mechanism  
✅ Graceful error handling  

**Next Steps:**
- Test the system thoroughly
- Customize threat conditions if needed
- Deploy on a dedicated machine for 24/7 monitoring
- Consider adding database logging for audit trails

**Need Help?**
If you encounter any issues not covered in this guide, check:
- Flask documentation: https://flask.palletsprojects.com/
- Ultralytics YOLOv8 docs: https://docs.ultralytics.com/
- Telegram Bot API: https://core.telegram.org/bots/api

---

**Stay Safe! 🛡️**

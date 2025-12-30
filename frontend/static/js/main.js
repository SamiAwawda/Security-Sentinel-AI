let currentMode = null;
let previousLogCount = 0;
let alarmSound = document.getElementById('alarm-sound');
let lastThreatCheck = false;
let logsInterval = null;
let threatInterval = null;

// ============================================
// MODE SELECTION & LAZY LOADING
// ============================================
function startMode(mode) {
    currentMode = mode;

    // Hide welcome screen
    document.getElementById('welcome-screen').style.display = 'none';

    if (mode === 'webcam') {
        // Show webcam area
        document.getElementById('webcam-area').classList.add('active');

        // CRITICAL: Lazy load camera feed (only now!)
        const videoFeed = document.getElementById('video-feed');
        videoFeed.src = '/video_feed/camera?' + new Date().getTime();

        // Update status badge
        document.getElementById('system-status').innerHTML = '<div class="status-indicator"></div><span>System Active</span>';

        // Start monitoring
        startMonitoring();
    }
}

function backToHome() {
    // Stop all monitoring
    stopMonitoring();

    // Stop camera feed by clearing src
    const videoFeed = document.getElementById('video-feed');
    videoFeed.src = '';

    // Hide work areas
    document.getElementById('webcam-area').classList.remove('active');

    // Show welcome screen
    document.getElementById('welcome-screen').style.display = 'flex';

    // Reset status
    document.getElementById('system-status').innerHTML = '<div class="status-indicator"></div><span>System Ready</span>';
    document.getElementById('alert-status').style.display = 'none';

    // Reset state
    currentMode = null;
    previousLogCount = 0;
}

function startMonitoring() {
    // Start log polling
    logsInterval = setInterval(fetchLogs, 500);

    // Start threat status polling
    threatInterval = setInterval(checkThreatStatus, 500);
}

function stopMonitoring() {
    if (logsInterval) {
        clearInterval(logsInterval);
        logsInterval = null;
    }

    if (threatInterval) {
        clearInterval(threatInterval);
        threatInterval = null;
    }
}

// ============================================
// THREAT MONITORING
// ============================================
function checkThreatStatus() {
    fetch('/threat_status')
        .then(response => response.json())
        .then(data => {
            const alertBadge = document.getElementById('alert-status');

            if (data.active_threat) {
                alertBadge.style.display = 'flex';

                if (!lastThreatCheck) {
                    playAlarm();
                }
                lastThreatCheck = true;
            } else {
                alertBadge.style.display = 'none';
                lastThreatCheck = false;
            }
        })
        .catch(error => {
            console.error('Error checking threat status:', error);
        });
}

function playAlarm() {
    try {
        alarmSound.currentTime = 0;
        alarmSound.play().catch(e => {
            console.log('Audio play failed (may require user interaction):', e);
        });
    } catch (e) {
        console.error('Error playing alarm:', e);
    }
}

// ============================================
// LOGS
// ============================================
function fetchLogs() {
    fetch('/logs')
        .then(response => response.json())
        .then(data => {
            const logsContainer = document.getElementById('logs-container');
            const logs = data.logs;

            if (logs.length === 0) {
                logsContainer.innerHTML = '<div class="log-empty">Waiting for detections...</div>';
                return;
            }

            logsContainer.innerHTML = '';
            logs.forEach(log => {
                const logEntry = document.createElement('div');
                logEntry.className = log.includes('🚨') ? 'log-entry threat' : 'log-entry';
                logEntry.textContent = log;
                logsContainer.appendChild(logEntry);
            });

            if (logs.length > previousLogCount) {
                logsContainer.scrollTop = logsContainer.scrollHeight;
                previousLogCount = logs.length;
            }
        })
        .catch(error => {
            console.error('Error fetching logs:', error);
        });
}

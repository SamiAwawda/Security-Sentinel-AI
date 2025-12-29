// Live Monitor JavaScript
let currentCamera = 0;
let logsInterval = null;
let threatInterval = null;
let alarmSound = document.getElementById('alarm-sound');

// Start monitoring when page loads
startMonitoring();

function startMonitoring() {
    const videoFeed = document.getElementById('video-feed');
    videoFeed.src = `/video_feed/camera?camera=${currentCamera}&t=` + new Date().getTime();

    // Start polling for logs and threats
    logsInterval = setInterval(fetchLogs, 500);
    threatInterval = setInterval(checkThreatStatus, 500);

    console.log('Monitoring started for camera:', currentCamera);
}

function stopMonitoring() {
    const videoFeed = document.getElementById('video-feed');
    videoFeed.src = '';

    if (logsInterval) clearInterval(logsInterval);
    if (threatInterval) clearInterval(threatInterval);

    console.log('Monitoring stopped');
}

function switchCamera() {
    const selector = document.getElementById('camera-selector');
    currentCamera = parseInt(selector.value);

    stopMonitoring();
    startMonitoring();

    document.getElementById('active-camera').textContent = currentCamera + 1;
}

function refreshFeed() {
    stopMonitoring();
    setTimeout(startMonitoring, 500);
}

function fetchLogs() {
    fetch('/logs')
        .then(response => response.json())
        .then(data => {
            const container = document.getElementById('logs-container');
            const logs = data.logs || [];

            if (logs.length === 0) {
                container.innerHTML = '<div style="text-align: center; color: #9CA3AF; padding: 2rem;">Waiting for detections...</div>';
                return;
            }

            container.innerHTML = logs.map(log => {
                const isThreat = log.includes('🚨');
                return `
                    <div style="
                        padding: 0.75rem;
                        margin-bottom: 0.5rem;
                        background: ${isThreat ? '#FEE2E2' : 'white'};
                        border-left: 3px solid ${isThreat ? '#EF4444' : '#2563EB'};
                        border-radius: 6px;
                        font-size: 0.85rem;
                        color: ${isThreat ? '#991B1B' : '#6B7280'};
                    ">${log}</div>
                `;
            }).join('');

            container.scrollTop = container.scrollHeight;
        })
        .catch(error => console.error('Error fetching logs:', error));
}

function checkThreatStatus() {
    fetch('/threat_status')
        .then(response => response.json())
        .then(data => {
            const banner = document.getElementById('threat-banner');
            const status = document.getElementById('recording-status');

            if (data.active_threat) {
                banner.style.display = 'block';
                status.textContent = '🚨 THREAT DETECTED';
                status.style.color = '#EF4444';
                playAlarm();
            } else {
                status.textContent = 'Monitoring Active';
                status.style.color = '#10B981';
            }
        })
        .catch(error => console.error('Error checking threat:', error));
}

function playAlarm() {
    try {
        alarmSound.currentTime = 0;
        alarmSound.play().catch(e => console.log('Audio play prevented:', e));
    } catch (e) {
        console.error('Error playing alarm:', e);
    }
}

function dismissAlert() {
    document.getElementById('threat-banner').style.display = 'none';
}

function clearLogs() {
    // This would call a backend endpoint to clear logs
    document.getElementById('logs-container').innerHTML = '<div style="text-align: center; color: #9CA3AF; padding: 2rem;">Logs cleared</div>';
}

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    stopMonitoring();
});

// Gallery JavaScript
let videos = [];

loadVideos();

function loadVideos() {
    fetch('/api/videos')
        .then(response => response.json())
        .then(data => {
            videos = data.videos || [];
            renderVideos();
            updateStats();
        })
        .catch(error => {
            console.error('Error:', error);
            document.getElementById('loading').innerHTML = '<p style="color: #FF006B;">Error loading videos</p>';
        });
}

function renderVideos() {
    const grid = document.getElementById('video-grid');
    const loading = document.getElementById('loading');
    const emptyState = document.getElementById('empty-state');

    loading.style.display = 'none';

    if (videos.length === 0) {
        emptyState.style.display = 'block';
        return;
    }

    emptyState.style.display = 'none';
    grid.innerHTML = '';

    videos.forEach(video => {
        const card = document.createElement('div');
        card.className = 'video-card';
        card.innerHTML = `
            <div class="video-thumbnail">
                <span class="video-type-badge">${video.folder === 'alerts' ? 'Forensic Alert' : 'Processed'}</span>
                🎥
            </div>
            <div class="video-info">
                <div class="video-filename">${video.filename}</div>
                <div class="video-meta">
                    <span>📅 ${video.created}</span>
                    <span>💾 ${video.size_mb} MB</span>
                </div>
                <div class="video-actions">
                    <button class="btn btn-play" onclick='playVideo("${video.folder}", "${video.filename}")'>
                        ▶ Play
                    </button>
                    <button class="btn btn-delete" onclick='deleteVideo("${video.folder}", "${video.filename}")'>
                        🗑️ Delete
                    </button>
                </div>
            </div>
        `;
        grid.appendChild(card);
    });
}

function updateStats() {
    const count = videos.length;
    const totalSize = videos.reduce((sum, v) => sum + v.size_mb, 0);
    
    document.getElementById('video-count').textContent = count;
    document.getElementById('total-size').textContent = totalSize.toFixed(2) + ' MB';
}

function playVideo(folder, filename) {
    const modal = document.getElementById('video-modal');
    const video = document.getElementById('modal-video');
    const title = document.getElementById('modal-title');

    video.src = `/video/${folder}/${filename}`;
    title.textContent = filename;
    modal.classList.add('active');
    
    // Auto play
    video.play().catch(e => console.log('Autoplay prevented:', e));
}

function closeModal() {
    const modal = document.getElementById('video-modal');
    const video = document.getElementById('modal-video');

    video.pause();
    video.src = '';
    modal.classList.remove('active');
}

function deleteVideo(folder, filename) {
    if (!confirm(`Delete "${filename}"?\n\nThis cannot be undone.`)) {
        return;
    }

    fetch(`/delete_video/${folder}/${filename}`, { method: 'DELETE' })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('✅ Video deleted');
                loadVideos();
            } else {
                alert('❌ Error: ' + (data.error || 'Delete failed'));
            }
        })
        .catch(error => alert('❌ Error: ' + error.message));
}

// Keyboard shortcuts
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') closeModal();
});

// Click backdrop to close
document.getElementById('video-modal').addEventListener('click', (e) => {
    if (e.target.id === 'video-modal') closeModal();
});

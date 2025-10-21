// 视频详情页逻辑

document.addEventListener('DOMContentLoaded', function() {
    loadVideoDetail();

    // 删除按钮
    document.getElementById('delete-btn').addEventListener('click', deleteVideo);
});

async function loadVideoDetail() {
    showLoading(true);

    try {
        const result = await apiRequest(`/api/video/${videoId}`);

        if (result.success) {
            displayVideoDetail(result.data);
        }
    } catch (error) {
        console.error('Error loading video:', error);
        alert('加载视频失败: ' + error.message);
        window.location.href = '/videos';
    } finally {
        showLoading(false);
        document.getElementById('video-detail').style.display = 'block';
    }
}

function displayVideoDetail(video) {
    // 基本信息
    document.getElementById('video-title').textContent = video.title;
    document.getElementById('video-status-badge').innerHTML = getStatusBadge(video.status);
    document.getElementById('video-channel').textContent = video.channel || 'N/A';
    document.getElementById('video-duration').textContent = formatDuration(video.duration);
    document.getElementById('video-views').textContent = formatNumber(video.view_count);
    document.getElementById('video-date').textContent = formatDate(video.upload_date);

    const urlLink = document.getElementById('video-url');
    urlLink.href = video.url;

    // 缩略图
    if (video.thumbnail) {
        document.getElementById('video-thumbnail-container').innerHTML = `
            <img src="${video.thumbnail}" style="width: 100%; border-radius: 8px; margin-top: 1rem;" alt="${video.title}">
        `;
    }

    // 分类
    if (video.categories && video.categories.length > 0) {
        document.getElementById('video-categories').innerHTML = `
            <div><strong>分类：</strong></div>
            <div class="video-tags">${video.categories.map(c => `<span class="tag">${c}</span>`).join('')}</div>
        `;
    }

    // 标签
    if (video.tags && video.tags.length > 0) {
        document.getElementById('video-tags').innerHTML = `
            <div><strong>标签：</strong></div>
            <div class="video-tags">${createTagsHTML(video.tags)}</div>
        `;
    }

    // 摘要
    if (video.summary) {
        displaySummary(video.summary);
    }

    // 字幕
    if (video.transcript) {
        displayTranscript(video.transcript);
    }
}

function displaySummary(summary) {
    let html = '<div class="card"><div class="card-header">🎯 AI 智能摘要</div>';

    if (summary.core_summary) {
        html += `
            <div class="summary-section">
                <div class="summary-title">核心摘要</div>
                <div class="summary-content">${summary.core_summary}</div>
            </div>
        `;
    }

    if (summary.key_points && summary.key_points.length > 0) {
        html += `
            <div class="summary-section">
                <div class="summary-title">关键要点</div>
                <ul class="summary-list">
                    ${summary.key_points.map(point => `<li>${point}</li>`).join('')}
                </ul>
            </div>
        `;
    }

    if (summary.detailed_summary) {
        html += `
            <div class="summary-section">
                <div class="summary-title">详细摘要</div>
                <div class="summary-content">${summary.detailed_summary}</div>
            </div>
        `;
    }

    if (summary.target_audience) {
        html += `
            <div class="summary-section">
                <div class="summary-title">适合人群</div>
                <div class="summary-content">${summary.target_audience}</div>
            </div>
        `;
    }

    if (summary.difficulty) {
        html += `
            <div class="summary-section">
                <div class="summary-title">难度等级</div>
                <div class="summary-content">${summary.difficulty}</div>
            </div>
        `;
    }

    html += '</div>';
    document.getElementById('summary-container').innerHTML = html;
}

function displayTranscript(transcript) {
    const html = `
        <div class="card">
            <div class="card-header">📄 视频字幕</div>
            <div class="summary-content" style="max-height: 400px; overflow-y: auto; background: var(--light-color); padding: 1rem; border-radius: 8px;">
                ${transcript.substring(0, 2000)}${transcript.length > 2000 ? '...' : ''}
            </div>
            <div class="text-muted mt-2" style="font-size: 0.9rem;">
                共 ${transcript.length} 字符
            </div>
        </div>
    `;
    document.getElementById('transcript-container').innerHTML = html;
}

async function deleteVideo() {
    if (!confirm('确定要删除这个视频吗？此操作无法撤销。')) {
        return;
    }

    try {
        const result = await apiRequest(`/api/video/${videoId}`, 'DELETE');

        if (result.success) {
            alert('视频已删除');
            window.location.href = '/videos';
        }
    } catch (error) {
        console.error('Error deleting video:', error);
        alert('删除失败: ' + error.message);
    }
}

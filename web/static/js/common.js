// 公共函数库

/**
 * 显示消息提示
 */
function showMessage(message, type = 'info', containerId = 'message-container') {
    const container = document.getElementById(containerId);
    if (!container) return;

    const alertClass = type === 'error' ? 'alert-error' :
                      type === 'success' ? 'alert-success' : 'alert-info';

    const icon = type === 'error' ? '❌' :
                type === 'success' ? '✅' : 'ℹ️';

    container.innerHTML = `
        <div class="alert ${alertClass}">
            <span>${icon}</span>
            <span>${message}</span>
        </div>
    `;

    // 3秒后自动消失
    setTimeout(() => {
        container.innerHTML = '';
    }, 5000);
}

/**
 * 发送 API 请求
 */
async function apiRequest(url, method = 'GET', data = null) {
    const options = {
        method: method,
        headers: {
            'Content-Type': 'application/json',
        }
    };

    if (data && method !== 'GET') {
        options.body = JSON.stringify(data);
    }

    try {
        const response = await fetch(url, options);
        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.detail || '请求失败');
        }

        return result;
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

/**
 * 格式化时长（秒 -> 分:秒）
 */
function formatDuration(seconds) {
    if (!seconds) return 'N/A';

    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;

    if (hours > 0) {
        return `${hours}:${String(minutes).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
    }
    return `${minutes}:${String(secs).padStart(2, '0')}`;
}

/**
 * 格式化数字（添加千分位）
 */
function formatNumber(num) {
    if (!num) return '0';
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
}

/**
 * 格式化日期
 */
function formatDate(dateString) {
    if (!dateString) return 'N/A';

    // 处理 YYYYMMDD 格式
    if (dateString.length === 8) {
        const year = dateString.substring(0, 4);
        const month = dateString.substring(4, 6);
        const day = dateString.substring(6, 8);
        return `${year}-${month}-${day}`;
    }

    const date = new Date(dateString);
    return date.toLocaleDateString('zh-CN');
}

/**
 * 获取状态徽章 HTML
 */
function getStatusBadge(status) {
    const badges = {
        'added': '<span class="badge badge-info">📥 已添加</span>',
        'downloaded': '<span class="badge badge-warning">📄 已下载</span>',
        'summarized': '<span class="badge badge-success">✅ 已摘要</span>'
    };
    return badges[status] || badges['added'];
}

/**
 * 创建标签 HTML
 */
function createTagsHTML(tags) {
    if (!tags || tags.length === 0) return '';

    return tags.slice(0, 5).map(tag =>
        `<span class="tag">${tag}</span>`
    ).join('');
}

/**
 * 创建视频卡片 HTML
 */
function createVideoCard(video) {
    const thumbnailHTML = video.thumbnail ?
        `<img src="${video.thumbnail}" class="video-thumbnail" alt="${video.title}">` :
        `<div class="video-thumbnail"></div>`;

    const tagsHTML = createTagsHTML(video.tags);
    const categoriesHTML = video.categories ?
        `<div class="text-muted" style="font-size: 0.9rem; margin-bottom: 0.5rem;">
            📂 ${video.categories.join(', ')}
        </div>` : '';

    return `
        <div class="video-card" onclick="location.href='/video/${video.video_id}'">
            ${thumbnailHTML}
            <div class="video-content">
                <div class="video-title">${video.title}</div>
                ${categoriesHTML}
                <div class="video-meta">
                    📺 ${video.channel || 'N/A'} · ${formatDuration(video.duration)}
                </div>
                <div class="video-tags">
                    ${getStatusBadge(video.status)}
                    ${tagsHTML}
                </div>
            </div>
        </div>
    `;
}

/**
 * 显示/隐藏加载状态
 */
function showLoading(show = true) {
    const loading = document.getElementById('loading');
    if (loading) {
        loading.style.display = show ? 'flex' : 'none';
    }
}

/**
 * 显示进度条
 */
function showProgress(show = true, text = '处理中...', percentage = 0) {
    const container = document.getElementById('progress-container');
    const fill = document.getElementById('progress-fill');
    const textElement = document.getElementById('progress-text');

    if (container) {
        if (show) {
            container.classList.add('active');
            if (textElement) textElement.textContent = text;
            if (fill) fill.style.width = percentage + '%';
        } else {
            container.classList.remove('active');
        }
    }
}

/**
 * 禁用/启用按钮
 */
function setButtonDisabled(buttonId, disabled = true) {
    const button = document.getElementById(buttonId);
    if (button) {
        button.disabled = disabled;
        if (disabled) {
            button.style.opacity = '0.5';
            button.style.cursor = 'not-allowed';
        } else {
            button.style.opacity = '1';
            button.style.cursor = 'pointer';
        }
    }
}

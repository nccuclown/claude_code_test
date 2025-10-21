// 统计页面逻辑

document.addEventListener('DOMContentLoaded', function() {
    loadStatistics();
});

async function loadStatistics() {
    showLoading(true);

    try {
        const result = await apiRequest('/api/stats');

        if (result.success) {
            displayStatistics(result.data);
        }
    } catch (error) {
        console.error('Error loading statistics:', error);
        showMessage('加载统计信息失败: ' + error.message, 'error');
    } finally {
        showLoading(false);
    }
}

function displayStatistics(stats) {
    // 总体统计
    const overviewHTML = `
        <div class="stat-card">
            <div class="stat-icon">📚</div>
            <div class="stat-value">${stats.total_videos}</div>
            <div class="stat-label">总视频数</div>
        </div>
        <div class="stat-card">
            <div class="stat-icon">✅</div>
            <div class="stat-value">${stats.summarized}</div>
            <div class="stat-label">已生成摘要</div>
        </div>
        <div class="stat-card">
            <div class="stat-icon">📄</div>
            <div class="stat-value">${stats.with_transcript}</div>
            <div class="stat-label">已下载字幕</div>
        </div>
        <div class="stat-card">
            <div class="stat-icon">📈</div>
            <div class="stat-value">${Math.round(stats.summarized / stats.total_videos * 100) || 0}%</div>
            <div class="stat-label">完成率</div>
        </div>
    `;

    document.getElementById('stats-overview').innerHTML = overviewHTML;
    document.getElementById('stats-overview').style.display = 'grid';

    // 分类统计
    if (stats.categories && Object.keys(stats.categories).length > 0) {
        const categoriesHTML = Object.entries(stats.categories)
            .sort((a, b) => b[1] - a[1])
            .map(([category, count]) => `
                <div class="stat-card" style="text-align: left;">
                    <div class="d-flex justify-between align-center">
                        <div>
                            <div style="font-size: 1.2rem; font-weight: bold; margin-bottom: 0.5rem;">
                                ${category}
                            </div>
                            <div class="text-muted">${count} 个视频</div>
                        </div>
                        <div style="font-size: 2rem; font-weight: bold; color: var(--primary-color);">
                            ${count}
                        </div>
                    </div>
                    <div style="margin-top: 0.5rem; background: var(--border-color); height: 8px; border-radius: 4px; overflow: hidden;">
                        <div style="background: linear-gradient(90deg, var(--primary-color), var(--secondary-color)); height: 100%; width: ${count / stats.total_videos * 100}%;"></div>
                    </div>
                </div>
            `).join('');

        document.getElementById('categories-list').innerHTML = `
            <div class="stats-grid">${categoriesHTML}</div>
        `;
        document.getElementById('categories-section').style.display = 'block';
    }

    // 热门标签
    if (stats.tags && Object.keys(stats.tags).length > 0) {
        const tagsHTML = Object.entries(stats.tags)
            .sort((a, b) => b[1] - a[1])
            .slice(0, 20)
            .map(([tag, count]) => {
                const size = Math.min(2, 0.8 + (count / Math.max(...Object.values(stats.tags))) * 1.2);
                return `<span class="tag" style="font-size: ${size}rem; cursor: pointer;" onclick="window.location.href='/videos'">${tag} (${count})</span>`;
            }).join('');

        document.getElementById('tags-cloud').innerHTML = tagsHTML;
        document.getElementById('tags-section').style.display = 'block';
    }
}

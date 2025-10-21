// 视频列表页逻辑

let allVideos = [];
let currentFilter = 'all';

document.addEventListener('DOMContentLoaded', function() {
    loadVideos();

    // 搜索功能
    const searchInput = document.getElementById('search-input');
    searchInput.addEventListener('input', function(e) {
        const query = e.target.value.toLowerCase().trim();
        filterAndDisplayVideos(query);
    });

    // 筛选按钮
    const filterButtons = document.querySelectorAll('[data-filter]');
    filterButtons.forEach(button => {
        button.addEventListener('click', function() {
            // 更新按钮状态
            filterButtons.forEach(btn => btn.classList.remove('btn-primary'));
            filterButtons.forEach(btn => btn.classList.add('btn-outline'));
            this.classList.remove('btn-outline');
            this.classList.add('btn-primary');

            // 更新筛选条件
            currentFilter = this.dataset.filter;
            filterAndDisplayVideos(searchInput.value.toLowerCase().trim());
        });
    });

    // 默认激活"全部"按钮
    filterButtons[0].classList.remove('btn-outline');
    filterButtons[0].classList.add('btn-primary');
});

async function loadVideos() {
    showLoading(true);

    try {
        const result = await apiRequest('/api/videos');

        if (result.success) {
            allVideos = result.data;
            displayVideos(allVideos);

            // 更新计数
            document.getElementById('video-count').textContent = `共 ${result.total} 个`;
        }
    } catch (error) {
        console.error('Error loading videos:', error);
        showMessage('加载视频失败: ' + error.message, 'error');
    } finally {
        showLoading(false);
    }
}

function filterAndDisplayVideos(searchQuery = '') {
    let filtered = allVideos;

    // 按状态筛选
    if (currentFilter !== 'all') {
        filtered = filtered.filter(v => v.status === currentFilter);
    }

    // 搜索筛选
    if (searchQuery) {
        filtered = filtered.filter(v => {
            const title = v.title?.toLowerCase() || '';
            const channel = v.channel?.toLowerCase() || '';
            const tags = v.tags?.join(' ').toLowerCase() || '';
            const categories = v.categories?.join(' ').toLowerCase() || '';

            return title.includes(searchQuery) ||
                   channel.includes(searchQuery) ||
                   tags.includes(searchQuery) ||
                   categories.includes(searchQuery);
        });
    }

    displayVideos(filtered);
}

function displayVideos(videos) {
    const container = document.getElementById('videos-container');
    const emptyState = document.getElementById('empty-state');
    const loading = document.getElementById('loading');

    loading.style.display = 'none';

    if (videos.length === 0) {
        container.style.display = 'none';
        emptyState.style.display = 'block';
        return;
    }

    emptyState.style.display = 'none';
    container.style.display = 'grid';

    // 按日期排序（最新的在前）
    videos.sort((a, b) => {
        const dateA = new Date(a.added_date || 0);
        const dateB = new Date(b.added_date || 0);
        return dateB - dateA;
    });

    // 生成视频卡片
    container.innerHTML = videos.map(video => createVideoCard(video)).join('');
}

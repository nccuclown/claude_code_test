// 首页逻辑

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('process-form');
    const submitBtn = document.getElementById('submit-btn');

    form.addEventListener('submit', async function(e) {
        e.preventDefault();

        const url = document.getElementById('video-url').value.trim();
        const lang = document.getElementById('video-lang').value;

        if (!url) {
            showMessage('请输入 YouTube 视频链接', 'error');
            return;
        }

        // 验证 URL 格式
        if (!url.includes('youtube.com') && !url.includes('youtu.be')) {
            showMessage('请输入有效的 YouTube 链接', 'error');
            return;
        }

        // 禁用按钮
        setButtonDisabled('submit-btn', true);
        submitBtn.textContent = '⏳ 处理中...';

        // 显示进度
        showProgress(true, '正在获取视频信息...', 10);

        try {
            // 发送处理请求
            const result = await apiRequest('/api/video/process', 'POST', {
                url: url,
                lang: lang
            });

            if (result.success) {
                showProgress(true, '✅ 处理完成！', 100);
                showMessage('视频处理成功！即将跳转...', 'success');

                // 2秒后跳转到视频详情页
                setTimeout(() => {
                    window.location.href = `/video/${result.data.video_id}`;
                }, 2000);
            }
        } catch (error) {
            console.error('Error:', error);
            showMessage('处理失败: ' + error.message, 'error');
            showProgress(false);
            setButtonDisabled('submit-btn', false);
            submitBtn.textContent = '✨ 一键处理（添加 + 下载 + 摘要）';
        }
    });

    // 实时验证 URL
    document.getElementById('video-url').addEventListener('input', function(e) {
        const url = e.target.value.trim();
        if (url && !url.includes('youtube.com') && !url.includes('youtu.be')) {
            e.target.style.borderColor = 'var(--danger-color)';
        } else {
            e.target.style.borderColor = 'var(--border-color)';
        }
    });
});

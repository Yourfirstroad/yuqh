# coding=utf-8
"""
RSS HTML 报告渲染模块

提供 RSS 订阅内容的 HTML 格式报告生成功能
"""

from datetime import datetime
from typing import Dict, List, Optional, Callable

from trendradar.report.helpers import html_escape


def render_rss_html_content(
    rss_items: List[Dict],
    total_count: int,
    feeds_info: Optional[Dict[str, str]] = None,
    *,
    get_time_func: Optional[Callable[[], datetime]] = None,
) -> str:
    """渲染 RSS HTML 内容

    Args:
        rss_items: RSS 条目列表，每个条目包含:
            - title: 标题
            - feed_id: RSS 源 ID
            - feed_name: RSS 源名称
            - url: 链接
            - published_at: 发布时间
            - summary: 摘要（可选）
            - author: 作者（可选）
        total_count: 条目总数
        feeds_info: RSS 源 ID 到名称的映射
        get_time_func: 获取当前时间的函数（可选，默认使用 datetime.now）

    Returns:
        渲染后的 HTML 字符串
    """
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>RSS 订阅内容</title>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js" integrity="sha512-BNaRQnYJYiPSqHHDb58B0yaPfCu+Wgds8Gp/gU33kqBtgNS4tSPHuGibyoeqMV/TJlSKda6FXzoEyYGjTe+vXA==" crossorigin="anonymous" referrerpolicy="no-referrer"></script>
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@600;700;900&display=swap" rel="stylesheet">
        <style>
            /* finesse · register=product · A=paper+vermilion · B=serif-900/sans-400 · C=single-card-report
             * D=static · E=newsprint-editorial · SOUL=6 SPECTACLE=1 DENSITY=8 */
            :root {
                --page: #f4f1e8;
                --card: #fdfbf5;
                --sunk: #f1ede2;
                --ink: #221e17;
                --ink-2: #59503f;
                --ink-3: #6f6754;
                --line: rgba(53, 45, 30, 0.16);
                --line-soft: rgba(53, 45, 30, 0.09);
                --accent: #b3401f;
                --accent-deep: #8f3316;
                --header-bg: #221e17;
                --header-btn: rgba(244, 241, 232, 0.10);
                --header-btn-hover: rgba(244, 241, 232, 0.20);
                --header-btn-line: rgba(244, 241, 232, 0.24);
                --shadow-card: 0 1px 2px rgba(53, 45, 30, 0.05), 0 10px 30px rgba(53, 45, 30, 0.08);
                --font-serif: 'Noto Serif SC', 'Source Han Serif SC', 'Songti SC', 'STSong', 'SimSun', serif;
            }

            * { box-sizing: border-box; }
            html, body { overflow-x: clip; }

            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
                margin: 0;
                padding: 16px;
                background: var(--page);
                color: var(--ink);
                line-height: 1.5;
            }

            .container {
                max-width: 700px;
                margin: 0 auto;
                background: var(--card);
                border: 1px solid var(--line-soft);
                border-radius: 4px;
                overflow: hidden;
                box-shadow: var(--shadow-card);
            }

            /* ===== 报头 ===== */
            .header {
                background: var(--header-bg);
                color: var(--page);
                padding: 36px 24px 28px;
                text-align: center;
                position: relative;
                border-bottom: 3px solid var(--accent);
            }

            .save-buttons {
                position: absolute;
                top: 16px;
                right: 16px;
                display: flex;
                gap: 8px;
            }

            .save-btn {
                background: var(--header-btn);
                border: 1px solid var(--header-btn-line);
                color: var(--page);
                padding: 8px 16px;
                border-radius: 3px;
                cursor: pointer;
                font-size: 13px;
                font-weight: 500;
                transition: background 0.15s ease, border-color 0.15s ease, transform 0.15s ease;
                white-space: nowrap;
            }

            .save-btn:hover { background: var(--header-btn-hover); }
            .save-btn:active { transform: translateY(1px); }
            .save-btn:disabled { opacity: 0.55; cursor: not-allowed; }
            .save-btn:focus-visible {
                outline: 2px solid var(--accent);
                outline-offset: 2px;
            }

            .header-title {
                font-family: var(--font-serif);
                font-size: 26px;
                font-weight: 900;
                letter-spacing: 0.06em;
                margin: 0 0 20px 0;
            }

            .header-info {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 16px;
                font-size: 14px;
            }

            .info-item { text-align: center; }

            .info-label {
                display: block;
                font-size: 11px;
                letter-spacing: 0.12em;
                opacity: 0.6;
                margin-bottom: 5px;
            }

            .info-value {
                font-weight: 600;
                font-size: 16px;
                font-variant-numeric: tabular-nums;
            }

            .content { padding: 26px; }

            /* ===== RSS 订阅分组 ===== */
            .feed-group { margin-bottom: 32px; }
            .feed-group:last-child { margin-bottom: 0; }

            .feed-header {
                display: flex;
                align-items: baseline;
                justify-content: space-between;
                margin-bottom: 16px;
                padding-bottom: 10px;
                border-bottom: 1px solid var(--line);
            }

            .feed-name {
                font-family: var(--font-serif);
                font-size: 17px;
                font-weight: 700;
                letter-spacing: 0.01em;
                color: var(--ink);
                overflow-wrap: anywhere;
                min-width: 0;
            }

            .feed-count {
                color: var(--ink-3);
                font-size: 13px;
                font-weight: 500;
                font-variant-numeric: tabular-nums;
                white-space: nowrap;
            }

            .rss-item {
                margin-bottom: 14px;
                padding: 16px;
                background: var(--sunk);
                border: 1px solid var(--line-soft);
                border-radius: 6px;
            }

            .rss-item:last-child { margin-bottom: 0; }

            .rss-meta {
                display: flex;
                align-items: center;
                gap: 12px;
                margin-bottom: 8px;
                flex-wrap: wrap;
            }

            .rss-time {
                color: var(--ink-3);
                font-size: 12px;
                font-variant-numeric: tabular-nums;
            }

            .rss-author {
                color: var(--ink-2);
                font-size: 12px;
                font-weight: 500;
            }

            .rss-title {
                font-size: 15px;
                line-height: 1.5;
                color: var(--ink);
                margin: 0 0 8px 0;
                font-weight: 500;
                overflow-wrap: anywhere;
            }

            .rss-link {
                color: inherit;
                text-decoration: none;
                transition: color 0.15s ease;
            }

            .rss-link:hover {
                color: var(--accent);
                text-decoration: underline;
                text-underline-offset: 3px;
            }

            .rss-link:focus-visible {
                outline: 2px solid var(--accent);
                outline-offset: 1px;
            }

            .rss-link:visited { color: var(--ink-3); }

            .rss-summary {
                font-size: 13px;
                color: var(--ink-2);
                line-height: 1.6;
                margin: 0;
                display: -webkit-box;
                -webkit-line-clamp: 3;
                -webkit-box-orient: vertical;
                overflow: hidden;
            }

            /* ===== 页脚 ===== */
            .footer {
                margin-top: 32px;
                padding: 20px 24px;
                background: transparent;
                border-top: 1px solid var(--line);
                text-align: center;
            }

            .footer-content {
                font-size: 13px;
                color: var(--ink-2);
                line-height: 1.6;
            }

            .footer-link {
                color: var(--accent);
                text-decoration: none;
                font-weight: 500;
                transition: color 0.15s ease;
            }

            .footer-link:hover {
                color: var(--accent-deep);
                text-decoration: underline;
                text-underline-offset: 3px;
            }

            .footer-link:focus-visible {
                outline: 2px solid var(--accent);
                outline-offset: 1px;
            }

            .project-name {
                font-family: var(--font-serif);
                font-weight: 700;
                color: var(--ink);
            }

            @media (prefers-reduced-motion: reduce) {
                *, *::before, *::after {
                    animation-duration: 0.01ms !important;
                    transition-duration: 0.01ms !important;
                }
            }

            @media (max-width: 480px) {
                body { padding: 12px; }
                .header { padding: 28px 20px 22px; }
                .content { padding: 20px; }
                .footer { padding: 16px 20px; }
                .header-info { grid-template-columns: 1fr; gap: 12px; }
                .rss-meta { gap: 8px; }
                .rss-item { padding: 12px; }
                .save-buttons {
                    position: static;
                    margin-bottom: 16px;
                    display: flex;
                    gap: 8px;
                    justify-content: center;
                    flex-direction: column;
                    width: 100%;
                }
                .save-btn { width: 100%; }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="save-buttons">
                    <button class="save-btn" onclick="saveAsImage()">保存为图片</button>
                </div>
                <div class="header-title">RSS 订阅内容</div>
                <div class="header-info">
                    <div class="info-item">
                        <span class="info-label">订阅条目</span>
                        <span class="info-value">"""

    html += f"{total_count} 条"

    html += """</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">生成时间</span>
                        <span class="info-value">"""

    # 使用提供的时间函数或默认 datetime.now
    if get_time_func:
        now = get_time_func()
    else:
        now = datetime.now()
    html += now.strftime("%m-%d %H:%M")

    html += """</span>
                    </div>
                </div>
            </div>

            <div class="content">"""

    # 按 feed_id 分组
    feeds_map: Dict[str, List[Dict]] = {}
    for item in rss_items:
        feed_id = item.get("feed_id", "unknown")
        if feed_id not in feeds_map:
            feeds_map[feed_id] = []
        feeds_map[feed_id].append(item)

    # 渲染每个 RSS 源的内容
    for feed_id, items in feeds_map.items():
        feed_name = items[0].get("feed_name", feed_id) if items else feed_id
        if feeds_info and feed_id in feeds_info:
            feed_name = feeds_info[feed_id]

        escaped_feed_name = html_escape(feed_name)

        html += f"""
                <div class="feed-group">
                    <div class="feed-header">
                        <div class="feed-name">{escaped_feed_name}</div>
                        <div class="feed-count">{len(items)} 条</div>
                    </div>"""

        for item in items:
            raw_title = item.get("title", "")
            if not raw_title or not raw_title.strip():
                raw_title = item.get("url", "") or item.get("feed_name", "")
            escaped_title = html_escape(raw_title)
            url = item.get("url", "")
            published_at = item.get("published_at", "")
            author = item.get("author", "")
            summary = item.get("summary", "")

            html += """
                    <div class="rss-item">
                        <div class="rss-meta">"""

            if published_at:
                html += f'<span class="rss-time">{html_escape(published_at)}</span>'

            if author:
                html += f'<span class="rss-author">by {html_escape(author)}</span>'

            html += """
                        </div>
                        <div class="rss-title">"""

            if url:
                escaped_url = html_escape(url)
                html += f'<a href="{escaped_url}" target="_blank" class="rss-link">{escaped_title}</a>'
            else:
                html += escaped_title

            html += """
                        </div>"""

            if summary:
                escaped_summary = html_escape(summary)
                html += f"""
                        <p class="rss-summary">{escaped_summary}</p>"""

            html += """
                    </div>"""

        html += """
                </div>"""

    html += """
            </div>

            <div class="footer">
                <div class="footer-content">
                    由 <span class="project-name">TrendRadar</span> 生成 ·
                    <a href="https://github.com/sansan0/TrendRadar" target="_blank" class="footer-link">
                        GitHub 开源项目
                    </a>
                </div>
            </div>
        </div>

        <script>
            async function saveAsImage() {
                const button = event.target;
                const originalText = button.textContent;

                try {
                    button.textContent = '生成中...';
                    button.disabled = true;
                    window.scrollTo(0, 0);

                    await new Promise(resolve => setTimeout(resolve, 200));

                    const buttons = document.querySelector('.save-buttons');
                    buttons.style.visibility = 'hidden';

                    await new Promise(resolve => setTimeout(resolve, 100));

                    const container = document.querySelector('.container');

                    const canvas = await html2canvas(container, {
                        backgroundColor: '#f4f1e8',
                        scale: 1.5,
                        useCORS: true,
                        allowTaint: false,
                        imageTimeout: 10000,
                        removeContainer: false,
                        foreignObjectRendering: false,
                        logging: false,
                        width: container.offsetWidth,
                        height: container.offsetHeight,
                        x: 0,
                        y: 0,
                        scrollX: 0,
                        scrollY: 0,
                        windowWidth: window.innerWidth,
                        windowHeight: window.innerHeight
                    });

                    buttons.style.visibility = 'visible';

                    const link = document.createElement('a');
                    const now = new Date();
                    const filename = `TrendRadar_RSS订阅_${now.getFullYear()}${String(now.getMonth() + 1).padStart(2, '0')}${String(now.getDate()).padStart(2, '0')}_${String(now.getHours()).padStart(2, '0')}${String(now.getMinutes()).padStart(2, '0')}.png`;

                    link.download = filename;
                    link.href = canvas.toDataURL('image/png', 1.0);

                    document.body.appendChild(link);
                    link.click();
                    document.body.removeChild(link);

                    button.textContent = '保存成功!';
                    setTimeout(() => {
                        button.textContent = originalText;
                        button.disabled = false;
                    }, 2000);

                } catch (error) {
                    const buttons = document.querySelector('.save-buttons');
                    buttons.style.visibility = 'visible';
                    button.textContent = '保存失败';
                    setTimeout(() => {
                        button.textContent = originalText;
                        button.disabled = false;
                    }, 2000);
                }
            }

            document.addEventListener('DOMContentLoaded', function() {
                window.scrollTo(0, 0);
            });
        </script>
    </body>
    </html>
    """

    return html

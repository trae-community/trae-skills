#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
热榜报告生成脚本
将 fetch_news.py 输出的 JSON 数据转换为格式化的 Markdown / Text / HTML 报告

用法：python3 generate_report.py --data /tmp/hot_news.json --format markdown
"""

import json
import sys
import argparse
from datetime import datetime


def load_data(filepath):
    """加载 JSON 数据"""
    try:
        if filepath == "-":
            return json.loads(sys.stdin.read())
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[ERROR] 无法加载数据: {e}", file=sys.stderr)
        sys.exit(1)


def format_hot_value(hot_display):
    """格式化热度显示值"""
    if not hot_display or hot_display == "-":
        return "🔥"
    return f"🔥 {hot_display}"


def generate_markdown(data):
    """生成 Markdown 格式报告"""
    lines = []
    timestamp = data.get("timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    lines.append(f"# 🔥 今日全网热榜 | {timestamp}")
    lines.append("")

    if data.get("fail_count", 0) > 0:
        failed = data.get("failed", [])
        lines.append(f"> ⚠️ 以下平台数据暂时不可用：{', '.join(failed)}")
        lines.append("")

    platforms = data.get("platforms", {})

    if not platforms:
        lines.append("❌ 未获取到任何平台数据，请检查网络连接后重试。")
        return "\n".join(lines)

    for platform_key, platform_data in platforms.items():
        emoji = platform_data.get("emoji", "📌")
        name = platform_data.get("name", platform_key)
        items = platform_data.get("items", [])

        lines.append("---")
        lines.append("")
        lines.append(f"## {emoji} {name}")
        lines.append("")
        lines.append("| 排名 | 话题 | 热度 |")
        lines.append("|:----:|------|:----:|")

        for item in items:
            rank = item.get("rank", "-")
            title = item.get("title", "未知")
            hot_display = format_hot_value(item.get("hot_display", "-"))
            url = item.get("url", "")

            if url:
                title_display = f"[{title}]({url})"
            else:
                title_display = title

            rank_display = {1: "🥇", 2: "🥈", 3: "🥉"}.get(rank, str(rank))

            lines.append(f"| {rank_display} | {title_display} | {hot_display} |")

        lines.append("")

    lines.append("---")
    lines.append("")
    lines.append(f"> 📊 **数据更新时间**：{timestamp}")

    source_names = [p.get("name", "") for p in platforms.values()]
    lines.append(f"> 📡 **数据来源**：{' | '.join(source_names)}")
    lines.append("> ⚠️ **声明**：热榜数据来自各平台公开接口，实时变化，仅供参考")

    return "\n".join(lines)


def generate_text(data):
    """生成纯文本格式报告"""
    lines = []
    timestamp = data.get("timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    lines.append(f"🔥 今日全网热榜 | {timestamp}")
    lines.append("=" * 50)

    platforms = data.get("platforms", {})

    for platform_key, platform_data in platforms.items():
        emoji = platform_data.get("emoji", "📌")
        name = platform_data.get("name", platform_key)
        items = platform_data.get("items", [])

        lines.append("")
        lines.append(f"{emoji} {name}")
        lines.append("-" * 40)

        for item in items:
            rank = item.get("rank", "-")
            title = item.get("title", "未知")
            hot_display = item.get("hot_display", "")

            hot_str = f" [{hot_display}]" if hot_display and hot_display != "-" else ""
            lines.append(f"  {rank}. {title}{hot_str}")

    lines.append("")
    lines.append("=" * 50)
    lines.append(f"更新时间: {timestamp}")

    return "\n".join(lines)


def generate_html(data):
    """生成 HTML 格式报告"""
    timestamp = data.get("timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    platforms = data.get("platforms", {})

    html_parts = [
        "<!DOCTYPE html>",
        '<html lang="zh-CN">',
        "<head>",
        '<meta charset="UTF-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">',
        f"<title>🔥 今日全网热榜 | {timestamp}</title>",
        "<style>",
        "  * { margin: 0; padding: 0; box-sizing: border-box; }",
        "  body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;",
        "         background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);",
        "         min-height: 100vh; padding: 20px; }",
        "  .container { max-width: 900px; margin: 0 auto; }",
        "  h1 { color: #fff; text-align: center; margin-bottom: 30px;",
        "       font-size: 28px; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }",
        "  .platform { background: #fff; border-radius: 16px; padding: 24px;",
        "              margin-bottom: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); }",
        "  .platform h2 { font-size: 20px; margin-bottom: 16px; color: #333;",
        "                  border-bottom: 2px solid #f0f0f0; padding-bottom: 10px; }",
        "  .item { display: flex; align-items: center; padding: 10px 0;",
        "          border-bottom: 1px solid #f5f5f5; }",
        "  .item:last-child { border-bottom: none; }",
        "  .rank { width: 36px; height: 36px; border-radius: 50%;",
        "          display: flex; align-items: center; justify-content: center;",
        "          font-weight: bold; font-size: 14px; margin-right: 12px; flex-shrink: 0; }",
        "  .rank-1 { background: #FFD700; color: #fff; }",
        "  .rank-2 { background: #C0C0C0; color: #fff; }",
        "  .rank-3 { background: #CD7F32; color: #fff; }",
        "  .rank-n { background: #f0f0f0; color: #666; }",
        "  .title { flex: 1; font-size: 15px; color: #333; }",
        "  .title a { color: #333; text-decoration: none; }",
        "  .title a:hover { color: #667eea; }",
        "  .hot { color: #ff6b6b; font-size: 13px; font-weight: 500;",
        "         white-space: nowrap; margin-left: 10px; }",
        "  .footer { text-align: center; color: rgba(255,255,255,0.8);",
        "            margin-top: 20px; font-size: 13px; line-height: 1.8; }",
        "</style>",
        "</head>",
        "<body>",
        '<div class="container">',
        f'<h1>🔥 今日全网热榜</h1>',
    ]

    for platform_key, platform_data in platforms.items():
        emoji = platform_data.get("emoji", "📌")
        name = platform_data.get("name", platform_key)
        items = platform_data.get("items", [])

        html_parts.append(f'<div class="platform">')
        html_parts.append(f"<h2>{emoji} {name}</h2>")

        for item in items:
            rank = item.get("rank", 0)
            title = item.get("title", "未知")
            hot_display = item.get("hot_display", "")
            url = item.get("url", "")

            rank_class = f"rank-{rank}" if rank <= 3 else "rank-n"
            title_html = (
                f'<a href="{url}" target="_blank">{title}</a>' if url else title
            )
            hot_html = (
                f'<span class="hot">🔥 {hot_display}</span>'
                if hot_display and hot_display != "-"
                else ""
            )

            html_parts.append(f'<div class="item">')
            html_parts.append(f'  <div class="rank {rank_class}">{rank}</div>')
            html_parts.append(f'  <div class="title">{title_html}</div>')
            html_parts.append(f"  {hot_html}")
            html_parts.append("</div>")

        html_parts.append("</div>")

    html_parts.extend([
        '<div class="footer">',
        f"<p>📊 数据更新时间：{timestamp}</p>",
        "<p>⚠️ 热榜数据来自各平台公开接口，实时变化，仅供参考</p>",
        "</div>",
        "</div>",
        "</body>",
        "</html>",
    ])

    return "\n".join(html_parts)


def main():
    parser = argparse.ArgumentParser(description="热榜报告生成器")
    parser.add_argument(
        "--data",
        type=str,
        required=True,
        help="输入 JSON 数据文件路径（使用 - 从 stdin 读取）",
    )
    parser.add_argument(
        "--format",
        type=str,
        choices=["markdown", "text", "html"],
        default="markdown",
        help="输出格式（默认 markdown）",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="",
        help="输出文件路径（默认输出到 stdout）",
    )

    args = parser.parse_args()
    data = load_data(args.data)

    generators = {
        "markdown": generate_markdown,
        "text": generate_text,
        "html": generate_html,
    }

    report = generators[args.format](data)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"[INFO] 报告已保存到: {args.output}", file=sys.stderr)
    else:
        print(report)


if __name__ == "__main__":
    main()

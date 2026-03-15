#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
今日新闻热榜数据抓取脚本
数据源优先级：
  1. 韩小韩 API (api.vvhan.com) - 免费稳定，首选
  2. 60s API (60s.viki.moe) - 开源免费，备选
  3. 小众独行 API (xzdx.top) - 备选
  
依赖：仅使用 Python 标准库（无需 pip install）
用法：python3 fetch_news.py --platforms weibo,baidu,zhihu --top 10
"""

import json
import sys
import argparse
import urllib.request
import urllib.error
import urllib.parse
import time
import os
from datetime import datetime


# ========== 配置区 ==========

REQUEST_TIMEOUT = 15      # 请求超时时间（秒）
REQUEST_INTERVAL = 1       # 请求间隔（秒），避免频率限制
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)


# ========== API 数据源配置 ==========

# 方案一（首选）: 韩小韩 API - https://api.vvhan.com/hotlist.html
VVHAN_API_BASE = "https://api.vvhan.com/api/hotlist"

# 方案二（备选）: 60s API - https://docs.60s-api.viki.moe
SIXTY_S_API_BASE = os.environ.get("SIXTY_S_API_BASE", "https://60s.viki.moe")

# 方案三（备选）: 小众独行 API
XZDX_API_BASE = "https://xzdx.top/api/tophub"

# 方案四（自建）: DailyHotApi - https://github.com/imsyy/DailyHotApi
DAILY_HOT_API_BASE = os.environ.get("DAILY_HOT_API_BASE", "")


# ========== 平台配置 ==========

PLATFORM_CONFIG = {
    "weibo": {
        "name": "微博热搜",
        "emoji": "📱",
        # 韩小韩API路径
        "vvhan_type": "wbHot",
        # 60s API 路径
        "sixty_s_path": "/v2/weibo",
        # 小众独行 type
        "xzdx_type": "weibo",
        # DailyHotApi 路径
        "dailyhot_path": "/weibo",
    },
    "baidu": {
        "name": "百度热搜",
        "emoji": "🔍",
        "vvhan_type": "baiduRD",
        "sixty_s_path": "/v2/baidu",
        "xzdx_type": "baidu",
        "dailyhot_path": "/baidu",
    },
    "zhihu": {
        "name": "知乎热榜",
        "emoji": "💡",
        "vvhan_type": "zhihuHot",
        "sixty_s_path": "/v2/zhihu",
        "xzdx_type": "zhihu",
        "dailyhot_path": "/zhihu",
    },
    "toutiao": {
        "name": "今日头条",
        "emoji": "📰",
        "vvhan_type": "toutiao",
        "sixty_s_path": "/v2/toutiao",
        "xzdx_type": "toutiao",
        "dailyhot_path": "/toutiao",
    },
    "bilibili": {
        "name": "哔哩哔哩",
        "emoji": "📺",
        "vvhan_type": "bilihot",
        "sixty_s_path": "/v2/bilibili",
        "xzdx_type": "bilihot",
        "dailyhot_path": "/bilibili",
    },
    "douyin": {
        "name": "抖音热搜",
        "emoji": "🎵",
        "vvhan_type": "douyinHot",
        "sixty_s_path": "/v2/douyin",
        "xzdx_type": "douyin",
        "dailyhot_path": "/douyin",
    },
}

ALL_PLATFORMS = list(PLATFORM_CONFIG.keys())


# ========== 工具函数 ==========

def make_request(url, timeout=REQUEST_TIMEOUT):
    """发起 HTTP GET 请求，返回 JSON 数据"""
    try:
        req = urllib.request.Request(url)
        req.add_header("User-Agent", USER_AGENT)
        req.add_header("Accept", "application/json")

        with urllib.request.urlopen(req, timeout=timeout) as response:
            data = response.read().decode("utf-8")
            return json.loads(data)
    except urllib.error.HTTPError as e:
        print(f"[ERROR] HTTP {e.code}: {url}", file=sys.stderr)
        return None
    except urllib.error.URLError as e:
        print(f"[ERROR] URL Error: {e.reason} - {url}", file=sys.stderr)
        return None
    except json.JSONDecodeError:
        print(f"[ERROR] JSON decode failed: {url}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"[ERROR] Request failed: {e} - {url}", file=sys.stderr)
        return None


def format_hot_value(raw_hot):
    """格式化热度值"""
    if raw_hot is None or raw_hot == "":
        return "-"
    if isinstance(raw_hot, str):
        return raw_hot
    if isinstance(raw_hot, (int, float)):
        if raw_hot >= 100000000:
            return f"{raw_hot / 100000000:.1f}亿"
        elif raw_hot >= 10000:
            return f"{raw_hot / 10000:.1f}万"
        elif raw_hot > 0:
            return str(int(raw_hot))
    return "-"


# ========== 数据源适配器 ==========

def fetch_from_vvhan(platform, top=10):
    """
    方案一（首选）：从韩小韩 API 获取
    接口: https://api.vvhan.com/api/hotlist/{type}
    返回: { "success": true, "title": "...", "data": [...] }
    """
    config = PLATFORM_CONFIG.get(platform)
    if not config:
        return None

    vvhan_type = config.get("vvhan_type", "")
    if not vvhan_type:
        return None

    url = f"{VVHAN_API_BASE}/{vvhan_type}"
    print(f"  [韩小韩API] 请求: {url}", file=sys.stderr)

    raw_data = make_request(url)
    if not raw_data:
        return None

    # 韩小韩 API 返回格式: { "success": true, "data": [ { "index": 1, "title": "...", "hot": "...", "url": "..." } ] }
    if not raw_data.get("success"):
        print(f"  [韩小韩API] 返回 success=false", file=sys.stderr)
        return None

    data_list = raw_data.get("data", [])
    if not isinstance(data_list, list) or len(data_list) == 0:
        return None

    items = []
    for i, item in enumerate(data_list[:top]):
        entry = {
            "rank": item.get("index", i + 1),
            "title": item.get("title", "未知标题"),
            "hot": item.get("hot", ""),
            "hot_display": format_hot_value(item.get("hot", "")),
            "url": item.get("url", item.get("mobilUrl", "")),
        }
        items.append(entry)

    return items


def fetch_from_60s(platform, top=10):
    """
    方案二（备选）：从 60s API 获取
    接口: https://60s.viki.moe/v2/{platform}
    返回: { "code": 200, "data": [...] }
    """
    config = PLATFORM_CONFIG.get(platform)
    if not config:
        return None

    api_path = config.get("sixty_s_path", "")
    if not api_path:
        return None

    url = f"{SIXTY_S_API_BASE}{api_path}"
    print(f"  [60s API] 请求: {url}", file=sys.stderr)

    raw_data = make_request(url)
    if not raw_data:
        return None

    # 60s API v2 返回格式: { "code": 200, "data": [ { "title": "...", ... } ] }
    if raw_data.get("code") != 200:
        print(f"  [60s API] 返回 code={raw_data.get('code')}", file=sys.stderr)
        return None

    data_list = raw_data.get("data", [])
    if not isinstance(data_list, list) or len(data_list) == 0:
        return None

    items = []
    for i, item in enumerate(data_list[:top]):
        # 60s API 返回字段可能是 title, hot/heat, url/link 等
        title = item.get("title", item.get("name", "未知标题"))
        hot = item.get("hot", item.get("heat", item.get("score", "")))
        url_val = item.get("url", item.get("link", item.get("mobileUrl", "")))

        entry = {
            "rank": i + 1,
            "title": title,
            "hot": hot,
            "hot_display": format_hot_value(hot),
            "url": url_val,
        }
        items.append(entry)

    return items


def fetch_from_xzdx(platform, top=10):
    """
    方案三（备选）：从小众独行 API 获取
    接口: https://xzdx.top/api/tophub?type={type}
    """
    config = PLATFORM_CONFIG.get(platform)
    if not config:
        return None

    xzdx_type = config.get("xzdx_type", "")
    if not xzdx_type:
        return None

    url = f"{XZDX_API_BASE}?type={xzdx_type}"
    print(f"  [小众独行API] 请求: {url}", file=sys.stderr)

    raw_data = make_request(url)
    if not raw_data:
        return None

    # 尝试解析返回数据
    data_list = raw_data.get("data", [])
    if not isinstance(data_list, list) or len(data_list) == 0:
        # 如果 data 字段不存在，可能整个返回就是列表
        if isinstance(raw_data, list):
            data_list = raw_data
        else:
            return None

    items = []
    for i, item in enumerate(data_list[:top]):
        title = item.get("title", item.get("name", "未知标题"))
        hot = item.get("heat", item.get("hot", item.get("score", "")))
        url_val = item.get("url", item.get("link", ""))

        entry = {
            "rank": item.get("index", i + 1),
            "title": title,
            "hot": hot,
            "hot_display": format_hot_value(hot),
            "url": url_val,
        }
        items.append(entry)

    return items


def fetch_from_dailyhot(platform, top=10):
    """
    方案四（自建）：从自建 DailyHotApi 获取
    接口: {DAILY_HOT_API_BASE}/{platform}
    返回: { "code": 200, "data": [...] }
    """
    if not DAILY_HOT_API_BASE:
        return None

    config = PLATFORM_CONFIG.get(platform)
    if not config:
        return None

    api_path = config.get("dailyhot_path", "")
    if not api_path:
        return None

    url = f"{DAILY_HOT_API_BASE}{api_path}"
    print(f"  [DailyHotApi] 请求: {url}", file=sys.stderr)

    raw_data = make_request(url)
    if not raw_data:
        return None

    data_list = raw_data.get("data", [])
    if not isinstance(data_list, list) or len(data_list) == 0:
        return None

    items = []
    for i, item in enumerate(data_list[:top]):
        entry = {
            "rank": i + 1,
            "title": item.get("title", "未知标题"),
            "hot": item.get("hot", ""),
            "hot_display": format_hot_value(item.get("hot", "")),
            "url": item.get("url", item.get("mobileUrl", "")),
        }
        items.append(entry)

    return items


# ========== 核心逻辑 ==========

def fetch_platform(platform, top=10):
    """
    获取指定平台的热榜数据
    按优先级依次尝试多个数据源，直到成功
    """
    config = PLATFORM_CONFIG.get(platform)
    if not config:
        print(f"[WARN] 不支持的平台: {platform}", file=sys.stderr)
        return None

    platform_name = config["name"]
    print(f"[INFO] 正在获取 {platform_name} 数据...", file=sys.stderr)

    # 数据源优先级列表
    sources = [
        ("韩小韩API", fetch_from_vvhan),
        ("60s API", fetch_from_60s),
        ("小众独行API", fetch_from_xzdx),
        ("DailyHotApi(自建)", fetch_from_dailyhot),
    ]

    for source_name, fetch_func in sources:
        try:
            result = fetch_func(platform, top)
            if result and len(result) > 0:
                print(f"  ✅ {platform_name} 数据获取成功 (来源: {source_name}，共 {len(result)} 条)", file=sys.stderr)
                return result
        except Exception as e:
            print(f"  [WARN] {source_name} 异常: {e}", file=sys.stderr)
            continue

    print(f"  ❌ {platform_name} 所有数据源均失败", file=sys.stderr)
    return None


def fetch_all(platforms=None, top=10):
    """获取所有指定平台的热榜数据"""
    if platforms is None:
        platforms = ALL_PLATFORMS

    result = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "platforms": {},
        "failed": [],
    }

    for i, platform in enumerate(platforms):
        if platform not in PLATFORM_CONFIG:
            print(f"[WARN] 跳过不支持的平台: {platform}", file=sys.stderr)
            result["failed"].append(platform)
            continue

        data = fetch_platform(platform, top)

        if data:
            result["platforms"][platform] = {
                "name": PLATFORM_CONFIG[platform]["name"],
                "emoji": PLATFORM_CONFIG[platform]["emoji"],
                "items": data,
                "count": len(data),
            }
        else:
            result["failed"].append(platform)

        # 请求间隔，避免频率限制
        if i < len(platforms) - 1:
            time.sleep(REQUEST_INTERVAL)

    result["success_count"] = len(result["platforms"])
    result["fail_count"] = len(result["failed"])

    return result


def generate_markdown_report(data):
    """将数据直接生成 Markdown 格式报告"""
    lines = []
    timestamp = data.get("timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    lines.append(f"# 🔥 今日全网热榜 | {timestamp}")
    lines.append("")

    if data.get("fail_count", 0) > 0:
        failed = data.get("failed", [])
        failed_names = []
        for p in failed:
            if p in PLATFORM_CONFIG:
                failed_names.append(PLATFORM_CONFIG[p]["name"])
            else:
                failed_names.append(p)
        lines.append(f"> ⚠️ 以下平台数据暂时不可用：{', '.join(failed_names)}")
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
            hot_display = item.get("hot_display", "-")
            url = item.get("url", "")

            # 排名 emoji
            rank_display = {1: "🥇", 2: "🥈", 3: "🥉"}.get(
                rank if isinstance(rank, int) else 0, str(rank)
            )

            # 标题（可选加链接）
            if url:
                title_display = f"[{title}]({url})"
            else:
                title_display = title

            # 热度
            hot_str = f"🔥 {hot_display}" if hot_display and hot_display != "-" else "🔥"

            lines.append(f"| {rank_display} | {title_display} | {hot_str} |")

        lines.append("")

    # 页脚
    lines.append("---")
    lines.append("")
    lines.append(f"> 📊 **数据更新时间**：{timestamp}")
    source_names = [p.get("name", "") for p in platforms.values()]
    lines.append(f"> 📡 **数据来源**：{' | '.join(source_names)}")
    lines.append("> ⚠️ **声明**：热榜数据来自各平台公开接口，实时变化，仅供参考")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="今日新闻热榜数据抓取")
    parser.add_argument(
        "--platforms",
        type=str,
        default=",".join(ALL_PLATFORMS),
        help=f"平台列表，逗号分隔。支持: {', '.join(ALL_PLATFORMS)}",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=10,
        help="每个平台返回的条目数（默认10）",
    )
    parser.add_argument(
        "--format",
        type=str,
        choices=["json", "markdown"],
        default="json",
        help="输出格式（默认 json）",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="",
        help="输出文件路径（默认输出到 stdout）",
    )

    args = parser.parse_args()
    platforms = [p.strip() for p in args.platforms.split(",") if p.strip()]

    print(f"\n{'='*50}", file=sys.stderr)
    print(f"🔥 今日新闻热榜抓取器", file=sys.stderr)
    print(f"📋 平台: {', '.join(platforms)}", file=sys.stderr)
    print(f"🔢 每平台 Top: {args.top}", file=sys.stderr)
    print(f"📄 输出格式: {args.format}", file=sys.stderr)
    print(f"{'='*50}\n", file=sys.stderr)

    # 获取数据
    result = fetch_all(platforms=platforms, top=args.top)

    print(f"\n{'='*50}", file=sys.stderr)
    print(f"✅ 成功: {result['success_count']} 个平台", file=sys.stderr)
    if result["fail_count"] > 0:
        print(f"❌ 失败: {result['fail_count']} 个平台 ({', '.join(result['failed'])})", file=sys.stderr)
    print(f"{'='*50}\n", file=sys.stderr)

    # 生成输出
    if args.format == "markdown":
        output = generate_markdown_report(result)
    else:
        output = json.dumps(result, ensure_ascii=False, indent=2)

    # 输出
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"[INFO] 已保存到: {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()

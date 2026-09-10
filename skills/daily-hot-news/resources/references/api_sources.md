# 今日新闻热榜 - API 数据源参考

## 数据源优先级

### 1. 韩小韩 API ⭐ 首选（免费、稳定、国内可访问）
- **官网**: https://api.vvhan.com/hotlist.html
- **聚合接口**: `https://api.vvhan.com/api/hotlist/all`
- **单平台接口**: `https://api.vvhan.com/api/hotlist/{type}`
- **支持平台 type 值**:
  - `wbHot` - 微博热搜
  - `baiduRD` - 百度热搜
  - `zhihuHot` - 知乎热榜
  - `toutiao` - 今日头条
  - `bilihot` - 哔哩哔哩热搜
  - `biliall` - 哔哩哔哩全站日榜
  - `douyinHot` - 抖音热搜
  - `36Ke` - 36氪
  - `netEaseHot` - 网易热搜
  - `history` - 历史上的今天
- **返回格式**: `{ "success": true, "title": "...", "subtitle": "...", "update_time": "...", "data": [{ "index": 1, "title": "...", "hot": "...", "url": "...", "mobilUrl": "..." }] }`
- **限制**: 免费无需注册，建议调用间隔 ≥ 5秒

### 2. 60s API（开源、全球 CDN、需科学上网）
- **官网文档**: https://docs.60s-api.viki.moe
- **GitHub**: https://github.com/vikiboss/60s
- **主域名**: `https://60s.viki.moe`
- **热榜接口**:
  - `/v2/weibo` - 微博热搜
  - `/v2/baidu` - 百度热搜
  - `/v2/zhihu` - 知乎热榜
  - `/v2/toutiao` - 头条热榜
  - `/v2/bilibili` - B站热搜
  - `/v2/douyin` - 抖音热搜
  - `/v2/60s` - 每日60秒新闻
- **返回格式**: `{ "code": 200, "message": "...", "data": [...] }`
- **注意**: 部署在 Deno Deploy，部分地区可能被墙，可自行部署

### 3. 小众独行 API（免费）
- **接口地址**: `https://xzdx.top/api/tophub?type={type}`
- **支持 type**: weibo, baidu, zhihu, douyin, bilihot, biliall, sspai, toutiao
- **返回字段**: index, title, hot/heat, url

### 4. DailyHotApi（自建，最稳定）
- **GitHub**: https://github.com/imsyy/DailyHotApi
- **支持 40+ 平台**
- **部署方式**:
  ```bash
  # Docker 部署
  docker pull imsyy/dailyhot-api:latest
  docker run -p 6688:6688 -d imsyy/dailyhot-api:latest

  # 然后设置环境变量
  export DAILY_HOT_API_BASE="http://localhost:6688"
  ```

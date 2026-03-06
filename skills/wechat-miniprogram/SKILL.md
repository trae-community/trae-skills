---
name: "wechat-miniprogram"
description: "微信小程序开发专用技能，提供标准项目结构、请求封装、接口管理等规范。Invoke when developing WeChat mini-programs or when user asks for mini-program development support."
---

# 微信小程序开发专用 Skill

## 核心功能

提供微信小程序开发的完整规范和最佳实践，包括：
- 标准项目结构生成
- 统一请求封装
- 接口地址统一管理
- 配置文件规范

## 标准项目结构

```
├── app.js                 // 小程序入口逻辑文件
├── app.json               // 小程序全局配置文件
├── app.wxss               // 小程序全局样式文件
├── sitemap.json           // 站点地图配置（SEO 相关）
├── pages/                 // 页面文件夹
│   ├── index/             // 首页
│   │   ├── index.js       // 页面逻辑
│   │   ├── index.json     // 页面配置
│   │   ├── index.wxml     // 页面结构
│   │   └── index.wxss     // 页面样式
│   └── [其他页面]/        // 其他页面遵循相同结构
├── components/            // 自定义组件文件夹
├── utils/                 // 工具函数文件夹
├── assets/                // 静态资源文件夹
│   ├── images/            // 图片资源
│   └── icons/             // 图标资源
└── .trae/                 // TRAE 配置文件夹
```

## 接口统一管理 (utils/api.js)

```javascript
// 接口统一管理
export default {
  // 用户模块
  user: {
    login: '/user/login',
    info: '/user/info',
    update: '/user/update'
  },
  // 商品模块
  goods: {
    list: '/goods/list',
    detail: '/goods/detail',
    search: '/goods/search'
  },
  // 订单模块
  order: {
    create: '/order/create',
    list: '/order/list',
    detail: '/order/detail'
  }
};
```

## 统一请求封装 (utils/request.js)

### 请求拦截器功能
- 自动拼接完整请求地址（baseUrl + 接口路径）
- 自动添加统一请求头（Content-Type: application/json）
- 自动注入用户认证 token
- 自动添加公共参数
- 支持自定义请求头、超时时间、加载状态
- 自动处理 GET/POST 参数格式

### 响应拦截器功能
- 统一隐藏加载状态
- HTTP 状态码 200-299 视为成功
- 业务状态码 code: 0 为成功
- 自动返回业务数据 data 字段
- 业务失败自动弹窗提示
- 401 自动跳转登录页并清除 token
- 5xx 和网络错误统一处理

### 标准实现代码

```javascript
import config from './config.js';
import api from './api.js';

const request = (options) => {
  return new Promise((resolve, reject) => {
    const showLoading = options.showLoading !== false;
    if (showLoading) {
      wx.showLoading({
        title: options.loadingText || '加载中...',
        mask: true
      });
    }

    const token = wx.getStorageSync('token');
    let url = config.baseUrl + options.url;
    
    if (options.method === 'GET' && options.data) {
      const queryParams = Object.keys(options.data)
        .map(key => `${encodeURIComponent(key)}=${encodeURIComponent(options.data[key])}`)
        .join('&');
      url += (url.includes('?') ? '&' : '?') + queryParams;
    }

    wx.request({
      url: url,
      method: options.method || 'GET',
      data: options.method !== 'GET' ? options.data : {},
      header: {
        'Content-Type': 'application/json',
        'Authorization': token ? `Bearer ${token}` : '',
        ...options.header
      },
      timeout: options.timeout || config.timeout,
      success: (res) => {
        if (showLoading) wx.hideLoading();
        const { statusCode, data } = res;

        if (statusCode >= 200 && statusCode < 300) {
          if (data.code === 0) {
            resolve(data.data || {});
          } else {
            if (data.code === 401) {
              wx.removeStorageSync('token');
              wx.removeStorageSync('userInfo');
              wx.redirectTo({ url: '/pages/login/login' });
            }
            wx.showToast({
              title: data.msg || '请求失败',
              icon: 'none',
              duration: 2000
            });
            reject(data);
          }
        } else {
          wx.showToast({
            title: '网络错误',
            icon: 'none',
            duration: 2000
          });
          reject(res);
        }
      },
      fail: (err) => {
        if (showLoading) wx.hideLoading();
        wx.showToast({
          title: '网络连接失败',
          icon: 'none',
          duration: 2000
        });
        reject(err);
      }
    });
  });
};

export default request;
```

## 配置文件 (utils/config.js)

```javascript
export default {
  baseUrl: 'https://api.example.com',
  timeout: 10000,
  appId: 'your-app-id'
};
```

## 使用示例

```javascript
import request from '../../utils/request.js';
import api from '../../utils/api.js';

// 获取用户信息
request({
  url: api.user.info,
  method: 'GET'
}).then(data => {
  console.log('用户信息:', data);
});

// 登录
request({
  url: api.user.login,
  method: 'POST',
  data: {
    code: 'xxx'
  }
}).then(data => {
  wx.setStorageSync('token', data.token);
});
```

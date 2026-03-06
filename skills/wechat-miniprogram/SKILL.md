---
name: "wechat-miniprogram"
description: "WeChat mini-program development skill with standard project structure, request wrapper, and API management. Invoke when developing WeChat mini-programs or when user asks for mini-program development support."
---

# WeChat Mini-Program Development Skill

A comprehensive skill for WeChat mini-program development, providing standard project structure, unified request wrapper, API endpoint management, and configuration file conventions.

## Description

This skill helps developers quickly scaffold and develop WeChat mini-programs with best practices and standardized code structure. It provides:

- Standard project directory structure
- Unified HTTP request wrapper with interceptors
- Centralized API endpoint management
- Configuration file conventions

## Usage Scenario

Invoke this skill when:
- User asks to create a new WeChat mini-program project
- User needs help with WeChat mini-program development
- User asks for HTTP request wrapper for WeChat mini-program
- User wants to set up API management in WeChat mini-program

## Instructions

### 1. Project Structure Setup

Create the following directory structure for the WeChat mini-program:

```
├── app.js                 // Mini-program entry logic
├── app.json               // Mini-program global configuration
├── app.wxss               // Mini-program global styles
├── sitemap.json           // Sitemap configuration (SEO related)
├── pages/                 // Pages folder
│   ├── index/             // Home page
│   │   ├── index.js       // Page logic
│   │   ├── index.json     // Page configuration
│   │   ├── index.wxml     // Page structure
│   │   └── index.wxss     // Page styles
│   └── [other pages]/     // Other pages follow same structure
├── components/            // Custom components folder
├── utils/                 // Utility functions folder
├── assets/                // Static assets folder
│   ├── images/            // Image resources
│   └── icons/             // Icon resources
└── .trae/                 // TRAE configuration folder
```

### 2. Create Configuration File (utils/config.js)

Create `utils/config.js` with CommonJS syntax:

```javascript
module.exports = {
  baseUrl: 'https://api.example.com',
  timeout: 10000,
  appId: 'your-app-id'
};
```

### 3. Create API Management (utils/api.js)

Create `utils/api.js` with centralized endpoint management:

```javascript
module.exports = {
  // User module
  user: {
    login: '/user/login',
    info: '/user/info',
    update: '/user/update'
  },
  // Goods module
  goods: {
    list: '/goods/list',
    detail: '/goods/detail',
    search: '/goods/search'
  },
  // Order module
  order: {
    create: '/order/create',
    list: '/order/list',
    detail: '/order/detail'
  }
};
```

### 4. Create Request Wrapper (utils/request.js)

Create `utils/request.js` with unified request/response interceptors:

**Request Interceptor Features:**
- Automatically concatenate full request URL (baseUrl + endpoint path)
- Automatically add unified request headers (Content-Type: application/json)
- Automatically inject user authentication token
- Support custom headers, timeout, loading state
- Let wx.request handle parameter serialization natively

**Response Interceptor Features:**
- Unified loading state management
- HTTP status code 200-299 considered successful
- Business status code === 0 considered successful
- Automatically return business data field
- Business failure automatically shows toast
- 401 automatically redirects to login page and clears token
- 5xx and network errors handled uniformly

```javascript
const config = require('./config.js');

const request = (options) => {
  return new Promise((resolve, reject) => {
    const showLoading = options.showLoading !== false;
    if (showLoading) {
      wx.showLoading({
        title: options.loadingText || 'Loading...',
        mask: true
      });
    }

    const token = wx.getStorageSync('token');
    const url = config.baseUrl + options.url;

    wx.request({
      url: url,
      method: options.method || 'GET',
      data: options.data || {},
      header: {
        'Content-Type': 'application/json',
        'Authorization': token ? 'Bearer ' + token : '',
        ...options.header
      },
      timeout: options.timeout || config.timeout,
      success: (res) => {
        if (showLoading) wx.hideLoading();
        const { statusCode, data } = res;

        if (statusCode >= 200 && statusCode < 300) {
          if (data.code === 0) {
            resolve(data.data !== undefined ? data.data : {});
          } else {
            if (data.code === 401) {
              wx.removeStorageSync('token');
              wx.removeStorageSync('userInfo');
              wx.redirectTo({ url: '/pages/login/login' });
            } else {
              wx.showToast({
                title: data.msg || 'Request failed',
                icon: 'none',
                duration: 2000
              });
            }
            reject(data);
          }
        } else {
          if (statusCode === 401) {
            wx.removeStorageSync('token');
            wx.removeStorageSync('userInfo');
            wx.redirectTo({ url: '/pages/login/login' });
          } else {
            wx.showToast({
              title: 'Network error',
              icon: 'none',
              duration: 2000
            });
          }
          reject(res);
        }
      },
      fail: (err) => {
        if (showLoading) wx.hideLoading();
        wx.showToast({
          title: 'Network connection failed',
          icon: 'none',
          duration: 2000
        });
        reject(err);
      }
    });
  });
};

module.exports = request;
```

### 5. Usage Examples

Show how to use the request wrapper in pages:

```javascript
const request = require('../../utils/request.js');
const api = require('../../utils/api.js');

// Get user info
request({
  url: api.user.info,
  method: 'GET'
}).then(data => {
  console.log('User info:', data);
});

// Login
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

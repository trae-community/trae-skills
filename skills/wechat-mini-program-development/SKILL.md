---
name: "wechat-mini-program-development"
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
              wx.reLaunch({ url: '/pages/login/login' });
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
            wx.reLaunch({ url: '/pages/login/login' });
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

### 5. Create Utility Functions (utils/util.js)

Create `utils/util.js` with common utility functions:

```javascript
// Format time
const formatTime = date => {
  const year = date.getFullYear();
  const month = date.getMonth() + 1;
  const day = date.getDate();
  const hour = date.getHours();
  const minute = date.getMinutes();
  const second = date.getSeconds();
  return [year, month, day].map(formatNumber).join('/') + ' ' + 
         [hour, minute, second].map(formatNumber).join(':');
};

const formatNumber = n => {
  n = n.toString();
  return n[1] ? n : '0' + n;
};

// Show loading
const showLoading = (title = 'Loading...') => {
  wx.showLoading({ title, mask: true });
};

// Hide loading
const hideLoading = () => {
  wx.hideLoading();
};

// Show toast
const showToast = (title, icon = 'none') => {
  wx.showToast({ title, icon, duration: 2000 });
};

// Show success
const showSuccess = (title = 'Success') => {
  showToast(title, 'success');
};

// Show confirm dialog
const showConfirm = (content, title = 'Confirm') => {
  return new Promise((resolve) => {
    wx.showModal({
      title,
      content,
      success: (res) => resolve(res.confirm)
    });
  });
};

module.exports = {
  formatTime,
  showLoading,
  hideLoading,
  showToast,
  showSuccess,
  showConfirm
};
```

### 6. Setup Global Login Check (app.js)

Create `app.js` with global login status check:

```javascript
App({
  onLaunch() {
    console.log('Mini-program launched');
    this.checkLoginStatus();
  },
  
  onShow() {
    console.log('Mini-program shown');
  },
  
  onHide() {
    console.log('Mini-program hidden');
  },

  // Check login status on app launch
  checkLoginStatus() {
    const token = wx.getStorageSync('token');
    if (!token) {
      wx.reLaunch({ url: '/pages/login/login' });
    }
  },

  globalData: {
    userInfo: null
  }
});
```

### 7. Configure TabBar (app.json)

Add tabBar configuration in `app.json`:

```json
{
  "pages": [
    "pages/index/index",
    "pages/login/login"
  ],
  "window": {
    "backgroundTextStyle": "dark",
    "navigationBarBackgroundColor": "#ffffff",
    "navigationBarTitleText": "Mini Program",
    "navigationBarTextStyle": "black"
  },
  "tabBar": {
    "color": "#999999",
    "selectedColor": "#ff6b4a",
    "backgroundColor": "#ffffff",
    "borderStyle": "white",
    "list": [
      {
        "pagePath": "pages/index/index",
        "text": "Home"
      },
      {
        "pagePath": "pages/menu/menu",
        "text": "Menu"
      },
      {
        "pagePath": "pages/cart/cart",
        "text": "Cart"
      },
      {
        "pagePath": "pages/mine/mine",
        "text": "Mine"
      }
    ]
  },
  "style": "v2",
  "sitemapLocation": "sitemap.json"
}
```

### 8. Usage Examples

Show how to use the request wrapper in pages:

```javascript
const request = require('../../utils/request.js');
const api = require('../../utils/api.js');
const util = require('../../utils/util.js');

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
  data: { code: 'xxx' }
}).then(data => {
  wx.setStorageSync('token', data.token);
  util.showSuccess('Login successful');
});

// Show loading and make request
util.showLoading('Loading data...');
request({
  url: api.goods.list,
  method: 'GET',
  showLoading: false  // Disable default loading
}).then(data => {
  util.hideLoading();
  console.log('Goods list:', data);
}).catch(err => {
  util.hideLoading();
  util.showError('Failed to load data');
});
```

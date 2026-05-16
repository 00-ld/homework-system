# 班级作业提交系统 - 微信小程序

本项目是"班级作业提交系统"的微信小程序端，通过 `<web-view>` 组件加载已部署的 Hugging Face Space Web 应用。

## 目录结构

```
miniprogram/
├── app.json                 # 小程序全局配置
├── app.js                   # 小程序入口文件
├── app.wxss                 # 全局样式
├── project.config.json      # 项目配置文件
├── sitemap.json             # 站点地图
├── pages/
│   └── index/
│       ├── index.wxml       # 首页模板（web-view 容器）
│       ├── index.js         # 页面逻辑（加载状态管理）
│       ├── index.json       # 页面配置
│       └── index.wxss       # 页面样式（加载动画 + 错误页面）
└── README.md                # 本文件
```

## 发布前准备

### 1. 注册微信小程序账号

1. 访问 [微信公众平台](https://mp.weixin.qq.com/) 注册小程序账号
2. 完成主体信息登记（个人或企业均可）
3. 登录后获取 **AppID**（在"开发 > 开发设置"中查看）

### 2. 部署 Web 应用

确保 Web 应用已部署到公网可访问的 HTTPS 地址上，例如 Hugging Face Space：
- 参考项目根目录的 `部署到云端.md` 完成云端部署
- 部署后会获得一个形如 `https://你的用户名-homework-system.hf.space` 的地址

## 发布步骤

### 第一步：修改 AppID

打开 `miniprogram/project.config.json`，确认 `appid` 字段已配置（已为你配置好）：

```json
{
  "appid": "wxe92848dccffcc9f3"
}
```

### 第二步：修改 WebView 地址

在 `miniprogram/app.js` 中，找到 `globalData.webviewUrl`，替换为实际的 Web 应用地址：

```javascript
globalData: {
  webviewUrl: 'https://你的用户名-homework-system.hf.space'
}
```

### 第三步：配置域名白名单

在微信小程序后台（`开发 > 开发管理 > 开发设置 > 业务域名`）中：

1. 点击"修改"
2. 添加 Web 应用部署的域名（如 `hf.space` 或你绑定的自定义域名）
3. 下载校验文件并上传到 Web 服务器对应目录完成域名验证

> **重要提醒**：微信小程序中 web-view 加载的域名必须在小程序后台配置为业务域名，否则加载会失败。

### 第四步：使用微信开发者工具上传

1. 下载并安装 [微信开发者工具](https://developers.weixin.qq.com/miniprogram/dev/devtools/download.html)
2. 打开开发者工具，选择"小程序"项目
3. 项目目录选择 `miniprogram/` 文件夹
4. 填入你的 AppID
5. 点击"确认"打开项目
6. 在开发者工具中测试功能是否正常
7. 点击工具栏的"上传"按钮
8. 填写版本号和项目备注
9. 提交审核

### 第五步：提交审核与发布

1. 登录 [微信公众平台](https://mp.weixin.qq.com/)
2. 进入"版本管理"
3. 在"开发版本"中找到刚刚上传的版本
4. 点击"提交审核"
5. 填写审核说明（描述小程序的功能和使用场景）
6. 等待审核通过（通常 1-7 个工作日）
7. 审核通过后，点击"发布"

## 常见问题

### Q: web-view 页面显示空白

- 检查域名是否已在微信小程序后台配置为业务域名
- 确保 Web 应用使用 HTTPS 协议
- 检查手机网络是否正常

### Q: 加载时提示"域名未在白名单中"

- 这是 web-view 的常见限制，必须在微信小程序后台配置业务域名
- 个人主体的小程序最多可配置 20 个业务域名

### Q: iOS 和 Android 显示效果不一致

- web-view 在不同系统上的 webview 内核不同（iOS 使用 WKWebView，Android 使用 X5 内核）
- 建议在 Web 端就做好响应式适配

### Q: 如何修改小程序的标题？

- 导航栏标题：修改 `app.json` 中的 `navigationBarTitleText`
- 页面标题：修改 `pages/index/index.json` 中的 `navigationBarTitleText`

## 版本记录

| 版本 | 日期 | 说明 |
|------|------|------|
| 1.0.0 | - | 初始版本，基于 web-view 的微信小程序 |

## 技术支持

- 项目源码：见本仓库根目录
- Web 应用部署说明：见 `部署到云端.md`
- 微信小程序文档：https://developers.weixin.qq.com/miniprogram/dev/framework/

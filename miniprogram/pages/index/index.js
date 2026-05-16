/**
 * 首页 - 页面逻辑
 *
 * 功能：
 * 1. 通过 web-view 加载部署的 Web 应用
 * 2. 处理 web-view 的加载状态（加载中 / 加载成功 / 加载失败）
 * 3. 提供重试机制
 */
Page({
  data: {
    // web-view 要加载的 URL
    webviewUrl: '',
    // 是否正在加载
    loading: true,
    // 是否加载出错
    error: false,
    // 错误信息
    errorMsg: ''
  },

  onLoad() {
    // 从 app 的 globalData 获取 webview URL
    const app = getApp();
    const url = app.globalData.webviewUrl;

    this.setData({
      webviewUrl: url
    });

    // 设置加载超时（15秒后如果还没加载完成，提示用户）
    this.loadTimeout = setTimeout(() => {
      if (this.data.loading) {
        this.setData({
          error: true,
          errorMsg: '加载超时，请检查网络连接后重试'
        });
      }
    }, 15000);
  },

  /**
   * web-view 加载成功回调
   */
  onWebviewLoad() {
    console.log('web-view 加载成功');
    this.setData({
      loading: false,
      error: false,
      errorMsg: ''
    });
    // 清除加载超时
    if (this.loadTimeout) {
      clearTimeout(this.loadTimeout);
      this.loadTimeout = null;
    }
  },

  /**
   * web-view 加载失败回调
   */
  onWebviewError(e) {
    console.error('web-view 加载失败', e.detail);

    let errMsg = '页面加载失败，请检查网络连接';

    if (e.detail && e.detail.errMsg) {
      if (e.detail.errMsg.indexOf('not in domain list') !== -1) {
        errMsg = '域名未在白名单中，请在小程序后台配置业务域名';
      } else if (e.detail.errMsg.indexOf('fail') !== -1) {
        errMsg = '网络请求失败，请检查网络连接或稍后重试';
      }
    }

    this.setData({
      loading: false,
      error: true,
      errorMsg: errMsg
    });

    // 清除加载超时
    if (this.loadTimeout) {
      clearTimeout(this.loadTimeout);
      this.loadTimeout = null;
    }
  },

  /**
   * 重试加载
   */
  retryLoad() {
    this.setData({
      loading: true,
      error: false,
      errorMsg: ''
    });

    // 重新设置 webviewUrl 会触发 web-view 重新加载
    const app = getApp();
    const currentUrl = this.data.webviewUrl;
    this.setData({
      webviewUrl: ''
    });

    // 重置超时
    if (this.loadTimeout) {
      clearTimeout(this.loadTimeout);
    }
    this.loadTimeout = setTimeout(() => {
      if (this.data.loading) {
        this.setData({
          error: true,
          errorMsg: '加载超时，请检查网络连接后重试'
        });
      }
    }, 15000);

    // 重新设置 URL 触发 web-view 加载
    setTimeout(() => {
      this.setData({
        webviewUrl: currentUrl
      });
    }, 300);
  },

  /**
   * 页面卸载时清理资源
   */
  onUnload() {
    if (this.loadTimeout) {
      clearTimeout(this.loadTimeout);
      this.loadTimeout = null;
    }
  }
});

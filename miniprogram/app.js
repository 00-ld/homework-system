/**
 * 班级作业提交系统 - 微信小程序入口
 *
 * 本小程序通过 web-view 组件加载 Hugging Face Space 上部署的 Web 应用。
 * 使用前请确保：
 * 1. 已在微信公众平台注册小程序并获取 appid
 * 2. Web 应用已部署到公网可访问的地址
 * 3. 微信小程序后台已配置 web-view 域名白名单
 */
App({
  onLaunch() {
    // 检查小程序更新
    const updateManager = wx.getUpdateManager();
    updateManager.onUpdateReady(() => {
      wx.showModal({
        title: '更新提示',
        content: '新版本已准备就绪，是否立即更新？',
        success(res) {
          if (res.confirm) {
            updateManager.applyUpdate();
          }
        }
      });
    });

    updateManager.onUpdateFailed(() => {
      // 新版本下载失败，不阻塞用户使用
      console.log('新版本下载失败');
    });
  },

  globalData: {
    // 默认加载的 Web 应用地址
    // 部署后请修改为实际的 Hugging Face Space 地址
    webviewUrl: 'https://web-production-de95b.up.railway.app'
  }
});

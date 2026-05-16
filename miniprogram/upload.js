// Node.js v25+ 兼容补丁：miniprogram-ci 依赖全局 localStorage
if (!globalThis.localStorage || typeof globalThis.localStorage.getItem !== 'function') {
  const store = {};
  globalThis.localStorage = {
    getItem: (key) => store[key] ?? null,
    setItem: (key, val) => { store[key] = String(val); },
    removeItem: (key) => { delete store[key]; },
    clear: () => { Object.keys(store).forEach(k => delete store[k]); },
    get length() { return Object.keys(store).length; },
    key: (i) => Object.keys(store)[i] ?? null,
  };
}

// 强制 IPv4 解析（微信上传不支持 IPv6）
const dns = require('dns');
dns.setDefaultResultOrder('ipv4first');

const ci = require('miniprogram-ci');
const path = require('path');

(async () => {
  const project = new ci.Project({
    appid: 'wxe92848dccffcc9f3',
    type: 'miniProgram',
    projectPath: path.join(__dirname),
    privateKeyPath: 'D:\\private.wxe92848dccffcc9f3.key',
    ignores: ['node_modules', 'upload.js', 'package.json', 'package-lock.json', 'polyfill.js'],
  });

  console.log('正在上传小程序代码...');
  const result = await ci.upload({
    project,
    version: '1.0.0',
    desc: '首次发布：作业提交系统微信小程序版',
    setting: {
      es6: true,
      es7: true,
      minify: true,
      autoPrefixWXSS: true,
    },
  });
  console.log('上传成功！', result);
})().catch(err => {
  console.error('上传失败：', err);
  process.exit(1);
});

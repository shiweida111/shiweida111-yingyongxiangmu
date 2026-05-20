const app = getApp()
const { i18n } = require('../../utils/i18n.js')

Page({
  data: {
    lang: 'zh',
    locale: {},
    fontScale: 1
  },

  onLoad: function () {
    this.loadSettings()
    wx.showShareMenu({
      withShareTicket: true,
      menus: ['shareAppMessage', 'shareTimeline']
    })
  },

  onShow: function () {
    this.loadSettings()
  },

  loadSettings: function() {
    const lang = app.getLanguage()
    const locale = app.getLocale()
    const fontScale = app.getFontScale()
    
    this.setData({
      lang: lang,
      locale: locale,
      fontScale: fontScale
    })
    
    wx.setNavigationBarTitle({
      title: locale.appName || '识伪防诈助手'
    })
  },

  goToDetect: function () {
    wx.navigateTo({
      url: '/pages/detect/detect?type=deepfake'
    })
  },

  goToFraudDetect: function () {
    wx.navigateTo({
      url: '/pages/detect/detect?type=fraud'
    })
  },

  goToChatFraudDetect: function () {
    wx.navigateTo({
      url: '/pages/detect/detect?type=chat_fraud'
    })
  },

  onShareAppMessage: function () {
    return {
      title: this.data.locale.appName || '识伪防诈助手',
      desc: this.data.locale.appDesc || '图像检测与风险分析工具',
      path: '/pages/index/index'
    }
  },

  onShareTimeline: function () {
    return {
      title: this.data.locale.appName || '识伪防诈助手',
      query: ''
    }
  }
})

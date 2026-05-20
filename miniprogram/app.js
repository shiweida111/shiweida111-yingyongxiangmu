const { i18n } = require('./utils/i18n.js')

App({
  onLaunch: function () {
    console.log('小程序启动')
    this.initGlobalSettings()
  },
  
  onShow: function () {
    console.log('小程序显示')
  },
  
  onHide: function () {
    console.log('小程序隐藏')
  },
  
  globalData: {
    apiBase: 'http://localhost:5173',
    userInfo: null,
    tempDetectResult: null,
    fontSize: 16,
    fontScale: 1,
    language: 'zh',
    locale: {}
  },
  
  setFontSize: function(size) {
    this.globalData.fontSize = size
    this.globalData.fontScale = size / 16
    wx.setStorageSync('fontSize', size)
  },
  
  getFontSize: function() {
    return this.globalData.fontSize
  },
  
  getFontScale: function() {
    return this.globalData.fontScale
  },
  
  loadFontSize: function() {
    const fontSize = wx.getStorageSync('fontSize') || 16
    this.globalData.fontSize = fontSize
    this.globalData.fontScale = fontSize / 16
    return fontSize
  },
  
  setLanguage: function(lang) {
    this.globalData.language = lang
    this.globalData.locale = i18n[lang] || i18n.zh
    wx.setStorageSync('language', lang)
  },
  
  getLanguage: function() {
    return this.globalData.language
  },
  
  getLocale: function() {
    if (Object.keys(this.globalData.locale).length === 0) {
      this.loadLanguage()
    }
    return this.globalData.locale
  },
  
  loadLanguage: function() {
    const language = wx.getStorageSync('language') || 'zh'
    this.globalData.language = language
    this.globalData.locale = i18n[language] || i18n.zh
    return language
  },
  
  initGlobalSettings: function() {
    this.loadFontSize()
    this.loadLanguage()
  }
})

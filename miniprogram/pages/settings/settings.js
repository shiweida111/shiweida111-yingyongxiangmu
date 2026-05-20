const app = getApp()
const { i18n } = require('../../utils/i18n.js')

Page({
  data: {
    fontSize: 16,
    fontScale: 1,
    fontSizeLabel: '标准',
    fontSizeOptions: [
      { label: '特小号', value: 12 },
      { label: '小号', value: 14 },
      { label: '标准', value: 16 },
      { label: '大号', value: 18 },
      { label: '特大号', value: 20 }
    ],
    showFontModal: false,
    language: 'zh',
    languageLabel: '中文',
    locale: {},
    languageOptions: [
      { label: '中文', value: 'zh', desc: '简体中文' },
      { label: 'English', value: 'en', desc: '英语' },
      { label: '日本語', value: 'ja', desc: '日语' },
      { label: 'Français', value: 'fr', desc: '法语' },
      { label: '한국어', value: 'ko', desc: '韩语' },
      { label: 'Deutsch', value: 'de', desc: '德语' }
    ],
    showLangModal: false
  },

  onLoad: function () {
    this.loadSettings()
  },

  onShow: function () {
    this.loadSettings()
  },

  loadSettings: function () {
    const fontSize = app.getFontSize()
    const fontScale = app.getFontScale()
    const language = app.getLanguage()
    const locale = app.getLocale()
    
    const fontSizeLabel = this.data.fontSizeOptions.find(opt => opt.value === fontSize)?.label || '标准'
    const languageLabel = this.data.languageOptions.find(opt => opt.value === language)?.label || '中文'

    this.setData({
      fontSize: fontSize,
      fontScale: fontScale,
      fontSizeLabel: fontSizeLabel,
      language: language,
      languageLabel: languageLabel,
      locale: locale
    })
    
    wx.setNavigationBarTitle({
      title: locale.settingsTitle || '设置'
    })
  },

  showFontSizeModal: function () {
    this.setData({
      showFontModal: true
    })
  },

  closeFontModal: function () {
    this.setData({
      showFontModal: false
    })
  },

  setFontSize: function (e) {
    const value = parseInt(e.currentTarget.dataset.value)
    const label = this.data.fontSizeOptions.find(opt => opt.value === value)?.label || '标准'

    app.setFontSize(value)
    
    this.setData({
      fontSize: value,
      fontScale: value / 16,
      fontSizeLabel: label
    })

    wx.showToast({
      title: this.data.locale.settingsFontUpdated || '字体大小已更新',
      icon: 'success'
    })

    setTimeout(function() {
      wx.switchTab({
        url: '/pages/index/index'
      })
    }, 1500)
  },

  showLangModal: function () {
    this.setData({
      showLangModal: true
    })
  },

  closeLangModal: function () {
    this.setData({
      showLangModal: false
    })
  },

  setLanguage: function (e) {
    const value = e.currentTarget.dataset.value
    const label = this.data.languageOptions.find(opt => opt.value === value)?.label || '中文'

    app.setLanguage(value)
    
    this.setData({
      language: value,
      languageLabel: label,
      locale: i18n[value] || i18n.zh
    })

    wx.showToast({
      title: this.data.locale.settingsLangUpdated || '语言已更新',
      icon: 'success'
    })

    setTimeout(function() {
      wx.switchTab({
        url: '/pages/index/index'
      })
    }, 1500)
  },

  resetSettings: function () {
    wx.showModal({
      title: this.data.locale.settingsResetConfirmTitle || '确认恢复',
      content: this.data.locale.settingsResetConfirm || '确定要将所有设置恢复为默认值吗？',
      success: (res) => {
        if (res.confirm) {
          wx.removeStorageSync('fontSize')
          wx.removeStorageSync('language')
          app.setFontSize(16)
          app.setLanguage('zh')

          this.setData({
            fontSize: 16,
            fontScale: 1,
            fontSizeLabel: '标准',
            language: 'zh',
            languageLabel: '中文',
            locale: i18n.zh
          })

          wx.showToast({
            title: this.data.locale.settingsResetSuccess || '已恢复默认设置',
            icon: 'success'
          })

          setTimeout(function() {
            wx.switchTab({
              url: '/pages/index/index'
            })
          }, 1500)
        }
      }
    })
  },

  preventClose: function () {}
})

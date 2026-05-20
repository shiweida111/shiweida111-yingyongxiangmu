const app = getApp()

Page({
  data: {
    record: {},
    locale: {}
  },

  onLoad: function (options) {
    this.loadLocale()
    const recordData = decodeURIComponent(options.record)
    const record = JSON.parse(recordData)
    
    const locale = app.getLocale()
    if (record.type === 'deepfake') {
      record.typeIcon = '🎨'
      record.typeName = locale.deepfake || '图像深伪鉴别'
    } else if (record.type === 'fraud') {
      record.typeIcon = '🛡️'
      record.typeName = locale.fraud || '涉诈程序截图检测'
    } else if (record.type === 'chat_fraud') {
      record.typeIcon = '💬'
      record.typeName = locale.chatFraud || '涉诈聊天记录检测'
    }
    
    this.setData({
      record: record
    })
  },

  onShow: function () {
    this.loadLocale()
  },

  loadLocale: function () {
    const locale = app.getLocale()
    this.setData({
      locale: locale
    })
    wx.setNavigationBarTitle({
      title: locale.historyDetailTitle || '分析详情'
    })
  },

  previewImage: function () {
    wx.previewImage({
      current: this.data.record.imageUrl,
      urls: [this.data.record.imageUrl]
    })
  },

  goBack: function () {
    wx.navigateBack()
  }
})

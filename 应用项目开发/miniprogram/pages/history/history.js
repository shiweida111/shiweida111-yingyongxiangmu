const app = getApp()

Page({
  data: {
    records: [],
    locale: {}
  },

  onLoad: function () {
    this.loadRecords()
    this.loadLocale()
  },

  onShow: function () {
    this.loadRecords()
    this.loadLocale()
  },

  loadLocale: function () {
    const locale = app.getLocale()
    this.setData({
      locale: locale
    })
    wx.setNavigationBarTitle({
      title: locale.historyTitle || '分析记录'
    })
  },

  loadRecords: function () {
    const records = wx.getStorageSync('detectRecords') || []
    const locale = this.data.locale || app.getLocale()
    
    records.forEach(record => {
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
      
      if (record.result && record.result.length > 80) {
        record.displayResult = record.result.substring(0, 80) + '...'
      } else {
        record.displayResult = record.result
      }
    })
    
    this.setData({
      records: records
    })
  },

  previewImage: function (e) {
    const url = e.currentTarget.dataset.url
    wx.previewImage({
      current: url,
      urls: [url]
    })
  },

  viewDetail: function (e) {
    const record = e.currentTarget.dataset.record
    const recordStr = encodeURIComponent(JSON.stringify(record))
    wx.navigateTo({
      url: `/pages/history-detail/history-detail?record=${recordStr}`
    })
  },

  clearHistory: function () {
    wx.showModal({
      title: this.data.locale.historyClearConfirmTitle || '确认清空',
      content: this.data.locale.historyClearConfirm || '确定要清空所有分析记录吗？',
      success: (res) => {
        if (res.confirm) {
          wx.removeStorageSync('detectRecords')
          this.setData({
            records: []
          })
          wx.showToast({
            title: this.data.locale.historyCleared || '已清空记录',
            icon: 'success'
          })
        }
      }
    })
  }
})

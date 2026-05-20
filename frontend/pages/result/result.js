const app = getApp()

Page({
  data: {
    detectResult: null,
    formattedAnalysisResult: ''
  },

  onLoad: function (options) {
    const result = app.globalData.tempDetectResult
    
    if (result) {
      this.setData({
        detectResult: result,
        formattedAnalysisResult: this.formatAnalysisResult(result.analysis_result)
      })
    } else {
      console.error('未找到检测结果')
      app.utils.showToast('未找到检测结果')
    }
  },

  formatAnalysisResult: function (text) {
    if (!text) return ''
    
    let html = text
      .replace(/【一、.*?】/g, '<strong style="font-size: 36rpx; font-weight: bold; color: #1F2937; display: block; margin-top: 24rpx; margin-bottom: 16rpx;">$&</strong>')
      .replace(/【二、.*?】/g, '<strong style="font-size: 36rpx; font-weight: bold; color: #1F2937; display: block; margin-top: 24rpx; margin-bottom: 16rpx;">$&</strong>')
      .replace(/【三、.*?】/g, '<strong style="font-size: 36rpx; font-weight: bold; color: #1F2937; display: block; margin-top: 24rpx; margin-bottom: 16rpx;">$&</strong>')
      .replace(/【四、.*?】/g, '<strong style="font-size: 36rpx; font-weight: bold; color: #1F2937; display: block; margin-top: 24rpx; margin-bottom: 16rpx;">$&</strong>')
      .replace(/【五、.*?】/g, '<strong style="font-size: 36rpx; font-weight: bold; color: #1F2937; display: block; margin-top: 24rpx; margin-bottom: 16rpx;">$&</strong>')
      .replace(/\n/g, '<br/>')
    
    return html
  },

  goBack: function () {
    wx.navigateBack({
      delta: 1
    })
  }
})
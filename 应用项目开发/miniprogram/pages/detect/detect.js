const app = getApp()
const { i18n } = require('../../utils/i18n.js')

Page({
  data: {
    selectedImage: '',
    isDetecting: false,
    uploadProgress: 0,
    analysisResult: null,
    detectType: 'deepfake',
    pageTitle: '',
    locale: {},
    fontScale: 1
  },

  onLoad: function (options) {
    const type = options.type || 'deepfake'
    this.setData({
      detectType: type,
      locale: app.getLocale(),
      fontScale: app.getFontScale()
    })
    this.updateTitle(type)
  },

  onShow: function () {
    this.setData({
      locale: app.getLocale(),
      fontScale: app.getFontScale()
    })
    this.updateTitle(this.data.detectType)
  },

  updateTitle: function(type) {
    const locale = this.data.locale || app.getLocale()
    let pageTitle = locale.deepfake || '图像深伪鉴别'
    if (type === 'fraud') {
      pageTitle = locale.fraud || '涉诈程序截图检测'
    } else if (type === 'chat_fraud') {
      pageTitle = locale.chatFraud || '涉诈聊天记录检测'
    }
    this.setData({
      pageTitle: pageTitle
    })
    wx.setNavigationBarTitle({
      title: pageTitle
    })
  },

  chooseImage: function () {
    this.setData({
      analysisResult: null
    })
    wx.chooseImage({
      count: 1,
      sizeType: ['compressed'],
      sourceType: ['album'],
      success: (res) => {
        const tempFilePath = res.tempFilePaths[0]
        wx.getFileInfo({
          filePath: tempFilePath,
          success: (fileInfo) => {
            const maxSize = 20 * 1024 * 1024
            if (fileInfo.size > maxSize) {
              wx.showToast({
                title: this.data.locale.detectImageTooLarge || '您上传的图片不符合要求，请压缩至20MB以内后重新上传',
                icon: 'none',
                duration: 3000
              })
              return
            }
            wx.compressImage({
              src: tempFilePath,
              quality: 60,
              success: (compressRes) => {
                this.setData({
                  selectedImage: compressRes.tempFilePath
                })
              },
              fail: () => {
                this.setData({
                  selectedImage: tempFilePath
                })
              }
            })
          },
          fail: () => {
            wx.compressImage({
              src: tempFilePath,
              quality: 60,
              success: (compressRes) => {
                this.setData({
                  selectedImage: compressRes.tempFilePath
                })
              },
              fail: () => {
                this.setData({
                  selectedImage: tempFilePath
                })
              }
            })
          }
        })
      },
      fail: (err) => {
        console.error('选择图片失败:', err)
        wx.showToast({
          title: this.data.locale.detectSelectFailed || '选择图片失败',
          icon: 'none'
        })
      }
    })
  },

  clearImage: function () {
    this.setData({
      selectedImage: '',
      analysisResult: null
    })
  },

  clearAnalysis: function () {
    this.setData({
      analysisResult: null
    })
  },

  startDetection: function () {
    if (!this.data.selectedImage || this.data.isDetecting) {
      return
    }

    this.setData({
      isDetecting: true,
      uploadProgress: 0,
      analysisResult: {
        summary: this.data.locale.detectAnalyzing || '正在分析中，请稍候...',
        formattedSummary: this.data.locale.detectAnalyzing || '正在分析中，请稍候...',
        rawData: null
      }
    })

    const uploadTask = wx.uploadFile({
      url: `${app.globalData.apiBase}/api/analyze`,
      filePath: this.data.selectedImage,
      name: 'file',
      formData: { category: this.data.detectType },
      success: (res) => {
        try {
          const result = JSON.parse(res.data)
          if (result.success) {
            app.globalData.tempDetectResult = result.data

            const analysisResult = this.parseAnalysisResult(result.data)
            this.setData({
              analysisResult: analysisResult
            })

            this.saveRecord(result.data)
          } else {
            wx.showToast({
              title: result.message || this.data.locale.detectFailed || '检测失败',
              icon: 'none'
            })
            this.setData({
              analysisResult: {
                summary: this.data.locale.detectFailed || '分析失败',
                formattedSummary: result.message || this.data.locale.detectFailed || '检测失败',
                rawData: null
              }
            })
          }
        } catch (e) {
          console.error('解析结果失败:', e)
          wx.showToast({
            title: this.data.locale.detectParseError || '数据解析失败',
            icon: 'none'
          })
          this.setData({
            analysisResult: {
              summary: this.data.locale.detectParseError || '数据解析失败',
              formattedSummary: this.data.locale.detectParseError || '数据解析失败',
              rawData: null
            }
          })
        }
      },
      fail: (err) => {
        console.error('上传失败:', err)
        wx.showToast({
          title: this.data.locale.detectUploadFailed || '上传失败',
          icon: 'none'
        })
        this.setData({
          analysisResult: {
            summary: this.data.locale.detectUploadFailed || '上传失败',
            formattedSummary: this.data.locale.detectUploadFailed || '上传失败',
            rawData: null
          }
        })
      },
      complete: () => {
        this.setData({
          isDetecting: false,
          uploadProgress: 0
        })
      }
    })

    uploadTask.onProgressUpdate((progress) => {
      if (progress.progress >= 100) {
        this.setData({
          uploadProgress: 100,
          'analysisResult.formattedSummary': this.data.locale.detectAnalyzing || '正在分析中，请稍候...'
        })
      } else {
        this.setData({
          uploadProgress: progress.progress
        })
      }
    })
  },

  parseAnalysisResult: function (data) {
    let summary = ''
    let formattedSummary = ''
    if (data.analysis_result) {
      let resultText = data.analysis_result
      if (resultText.length > 500) {
        resultText = resultText.substring(0, 500) + '...'
      }
      summary = resultText
      formattedSummary = this.formatAnalysisResult(data.analysis_result)
    } else {
      summary = this.data.locale.detectNoResult || '分析完成。由于响应问题，未能获取详细分析结果。'
    }

    return {
      summary: summary,
      formattedSummary: formattedSummary,
      rawData: data
    }
  },

  formatAnalysisResult: function (text) {
    if (!text) return ''
    
    let html = text
      .replace(/【一、.*?】/g, '<strong style="font-size: 32rpx; font-weight: bold; color: #1F2937; display: block; margin-top: 32rpx; margin-bottom: 20rpx; padding-bottom: 12rpx; border-bottom: 2rpx solid #E5E7EB;">$&</strong>')
      .replace(/【二、.*?】/g, '<strong style="font-size: 32rpx; font-weight: bold; color: #1F2937; display: block; margin-top: 32rpx; margin-bottom: 20rpx; padding-bottom: 12rpx; border-bottom: 2rpx solid #E5E7EB;">$&</strong>')
      .replace(/【三、.*?】/g, '<strong style="font-size: 32rpx; font-weight: bold; color: #1F2937; display: block; margin-top: 32rpx; margin-bottom: 20rpx; padding-bottom: 12rpx; border-bottom: 2rpx solid #E5E7EB;">$&</strong>')
      .replace(/【四、.*?】/g, '<strong style="font-size: 32rpx; font-weight: bold; color: #1F2937; display: block; margin-top: 32rpx; margin-bottom: 20rpx; padding-bottom: 12rpx; border-bottom: 2rpx solid #E5E7EB;">$&</strong>')
      .replace(/【五、.*?】/g, '<strong style="font-size: 32rpx; font-weight: bold; color: #1F2937; display: block; margin-top: 32rpx; margin-bottom: 20rpx; padding-bottom: 12rpx; border-bottom: 2rpx solid #E5E7EB;">$&</strong>')
      .replace(/(\d+[。、])/g, '<br/>\n$1')
      .replace(/\n/g, '<br/>')
    
    return html
  },

  saveRecord: function (data) {
    const records = wx.getStorageSync('detectRecords') || []
    const self = this

    const newRecord = {
      id: 'record_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9),
      type: self.data.detectType,
      imageUrl: self.data.selectedImage || data.image_url || '',
      result: data.analysis_result || this.data.locale.detectNoResult || '无分析结果',
      time: data.analyze_time || new Date().toLocaleString('zh-CN')
    }

    records.unshift(newRecord)

    if (records.length > 50) {
      records.splice(50)
    }

    wx.setStorageSync('detectRecords', records)
  }
})

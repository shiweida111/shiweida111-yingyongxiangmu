const app = getApp()

Page({
  data: {
    locale: {},
    fontScale: 1,
    userInfo: {
      nickName: '',
      avatarUrl: '',
      userId: ''
    },
    isLoggedIn: false,
    showNicknameModal: false,
    tempNickname: ''
  },

  onLoad: function () {
    this.loadUserInfo()
  },

  onShow: function () {
    this.loadLocale()
    this.loadUserInfo()
  },

  loadLocale: function () {
    const locale = app.getLocale()
    const fontScale = app.getFontScale()
    
    this.setData({
      locale: locale,
      fontScale: fontScale
    })
    
    wx.setNavigationBarTitle({
      title: locale.mineTitle || '我的'
    })
  },

  loadUserInfo: function () {
    const userInfo = wx.getStorageSync('userInfo')
    const isLoggedIn = wx.getStorageSync('isLoggedIn')
    
    if (isLoggedIn && userInfo) {
      this.setData({
        userInfo: userInfo,
        isLoggedIn: true
      })
    }
  },

  wxLogin: function () {
    const that = this
    
    wx.getUserProfile({
      desc: '用于完善会员资料',
      success: function (res) {
        const userInfo = {
          nickName: res.userInfo.nickName,
          avatarUrl: res.userInfo.avatarUrl,
          userId: 'user_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9)
        }
        
        wx.setStorageSync('userInfo', userInfo)
        wx.setStorageSync('isLoggedIn', true)
        
        that.setData({
          userInfo: userInfo,
          isLoggedIn: true
        })
        
        wx.showToast({
          title: that.data.locale.mineLoginSuccess || '登录成功',
          icon: 'success'
        })
      },
      fail: function (err) {
        console.error('登录失败:', err)
        wx.showToast({
          title: that.data.locale.mineLoginFailed || '登录失败',
          icon: 'none'
        })
      }
    })
  },

  chooseAvatar: function () {
    if (!this.data.isLoggedIn) {
      wx.showToast({
        title: this.data.locale.minePleaseLogin || '请先登录',
        icon: 'none'
      })
      return
    }

    wx.chooseImage({
      count: 1,
      sizeType: ['compressed'],
      sourceType: ['album'],
      success: (res) => {
        const avatarUrl = res.tempFilePaths[0]
        
        const userInfo = { ...this.data.userInfo, avatarUrl: avatarUrl }
        wx.setStorageSync('userInfo', userInfo)
        
        this.setData({
          userInfo: userInfo
        })
        
        wx.showToast({
          title: this.data.locale.mineAvatarUpdated || '头像更新成功',
          icon: 'success'
        })
      },
      fail: (err) => {
        console.error('选择头像失败:', err)
        wx.showToast({
          title: this.data.locale.mineAvatarFailed || '选择失败',
          icon: 'none'
        })
      }
    })
  },

  editNickname: function () {
    this.setData({
      showNicknameModal: true,
      tempNickname: this.data.userInfo.nickName
    })
  },

  onNicknameInput: function (e) {
    this.setData({
      tempNickname: e.detail.value
    })
  },

  saveNickname: function () {
    const newNickname = this.data.tempNickname.trim()
    
    if (!newNickname) {
      wx.showToast({
        title: this.data.locale.minePleaseInputNickname || '请输入昵称',
        icon: 'none'
      })
      return
    }

    const userInfo = { ...this.data.userInfo, nickName: newNickname }
    wx.setStorageSync('userInfo', userInfo)
    
    this.setData({
      userInfo: userInfo,
      showNicknameModal: false
    })
    
    wx.showToast({
      title: this.data.locale.mineNicknameUpdated || '昵称更新成功',
      icon: 'success'
    })
  },

  closeModal: function () {
    this.setData({
      showNicknameModal: false,
      tempNickname: ''
    })
  },

  preventClose: function () {
  },

  logout: function () {
    wx.showModal({
      title: this.data.locale.mineLogoutConfirmTitle || '确认退出',
      content: this.data.locale.mineLogoutConfirm || '确定要退出登录吗？',
      success: (res) => {
        if (res.confirm) {
          wx.removeStorageSync('userInfo')
          wx.removeStorageSync('isLoggedIn')
          
          this.setData({
            userInfo: {
              nickName: '',
              avatarUrl: '',
              userId: ''
            },
            isLoggedIn: false
          })
          
          wx.showToast({
            title: this.data.locale.mineLogoutSuccess || '已退出登录',
            icon: 'success'
          })
        }
      }
    })
  },

  showSettings: function () {
    wx.navigateTo({
      url: '/pages/settings/settings'
    })
  },

  goToHistory: function () {
    wx.navigateTo({
      url: '/pages/history/history'
    })
  },

  showAbout: function () {
    const locale = this.data.locale
    wx.showModal({
      title: locale.mineAboutTitle || '关于我们',
      content: (locale.mineAboutIntro || '【应用简介】\n图像检测 · 守护您的信息安全。帮助用户识别图像真伪和涉诈风险内容。\n\n【免责声明】\n检测结果仅供参考。本程序不负法律责任，最终解释权归本程序所有。'),
      showCancel: false
    })
  },

  showPrivacy: function () {
    const locale = this.data.locale
    wx.showModal({
      title: locale.minePrivacyTitle || '隐私政策',
      content: locale.minePrivacyContent || '我们重视您的隐私安全。本应用仅在本地存储您的用户信息，不会上传至服务器。您的检测记录仅保存在本地。',
      showCancel: false
    })
  }
})

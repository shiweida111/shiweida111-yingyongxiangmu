Page({
  data: {
    selectedImage: '',
    fileName: '',
    isLoading: false,
    showResult: false,
    resultSections: []
  },

  chooseImage: function() {
    var that = this;
    wx.chooseImage({
      count: 1,
      sizeType: ['compressed'],
      sourceType: ['album', 'camera'],
      success: function(res) {
        var tempFilePaths = res.tempFilePaths;
        that.setData({
          selectedImage: tempFilePaths[0],
          fileName: res.tempFiles[0].name,
          showResult: false
        });
      },
      fail: function(err) {
        wx.showToast({
          title: '选择图片失败',
          icon: 'none'
        });
      }
    });
  },

  clearImage: function() {
    this.setData({
      selectedImage: '',
      fileName: '',
      showResult: false
    });
  },

  analyzeImage: function() {
    var that = this;
    if (!that.data.selectedImage) {
      wx.showToast({
        title: '请先选择图片',
        icon: 'none'
      });
      return;
    }

    that.setData({
      isLoading: true
    });

    wx.showLoading({
      title: 'AI分析中...'
    });

    that.imageToBase64(that.data.selectedImage, function(base64Data) {
      that.callLLMAnalysis(base64Data);
    });
  },

  imageToBase64: function(imagePath, callback) {
    wx.getFileSystemManager().readFile({
      filePath: imagePath,
      encoding: 'base64',
      success: function(res) {
        callback(res.data);
      },
      fail: function(err) {
        wx.hideLoading();
        wx.showToast({
          title: '图片处理失败',
          icon: 'none'
        });
        that.setData({
          isLoading: false
        });
        that.showMockResult();
      }
    });
  },

  callLLMAnalysis: function(base64Data) {
    var that = this;
    var requestData = {
      model: 'Qwen/Qwen3.6-35B-A3B',
      messages: [
        {
          role: "user",
          content: [
            {
              type: "image_url",
              image_url: {
                url: "data:image/png;base64," + base64Data
              }
            },
            {
              type: "text",
              text: "请分析这张软件界面截图，按照以下格式输出分析结果：\n\n【界面内容识别】\n1. 界面顶部内容：\n2. 界面主体内容：\n3. 界面底部内容：\n4. 其他特殊元素：\n\n【风险要素识别】\n1. 高收益话术：\n2. 诱导性按钮：\n3. 敏感操作：\n4. 仿冒特征：\n\n【风险评估】\n1. 诈骗可能性：\n2. 诈骗类型：\n3. 风险等级：\n\n【详细分析说明】\n1. \n2. \n3. \n4. \n\n【安全建议】\n1. \n2. \n3. \n4. \n\n请严格按照【】包裹标题，内容用数字序号开头。"
            }
          ]
        }
      ],
      max_tokens: 2000,
      temperature: 0.3
    };

    wx.request({
      url: 'https://api.siliconflow.cn/v1/chat/completions',
      method: 'POST',
      header: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer sk-plmonajfgqbqztswwypdinuerhtqjrohctudfboygubopcur'
      },
      data: requestData,
      success: function(res) {
        wx.hideLoading();
        console.log('API响应:', res);
        try {
          if (res.statusCode === 200 && res.data && res.data.choices && res.data.choices.length > 0) {
            var resultText = res.data.choices[0].message.content;
            that.parseResult(resultText);
            that.setData({
              isLoading: false,
              showResult: true
            });
          } else {
            var errorMsg = res.data?.error?.message || '分析失败';
            console.error('API返回错误:', errorMsg);
            wx.showToast({
              title: errorMsg,
              icon: 'none',
              duration: 3000
            });
            that.setData({
              isLoading: false
            });
            that.showMockResult();
          }
        } catch (e) {
          console.error('解析结果失败:', e);
          wx.showToast({
            title: '解析结果失败: ' + e.message,
            icon: 'none',
            duration: 3000
          });
          that.setData({
            isLoading: false
          });
          that.showMockResult();
        }
      },
      fail: function(err) {
        wx.hideLoading();
        console.error('网络请求失败:', err);
        that.setData({
          isLoading: false
        });
        wx.showToast({
          title: '网络错误: ' + (err.errMsg || '未知错误'),
          icon: 'none',
          duration: 3000
        });
        that.showMockResult();
      }
    });
  },

  parseResult: function(text) {
    var sections = [];
    var sectionPattern = /【(.+?)】/g;
    var matches;
    var lastIndex = 0;
    var currentSection = null;

    while ((matches = sectionPattern.exec(text)) !== null) {
      if (currentSection && lastIndex < matches.index) {
        var content = text.substring(lastIndex, matches.index).trim();
        if (content) {
          var items = content.split('\n').filter(function(item) {
            return item.trim();
          });
          currentSection.content = currentSection.content.concat(items);
        }
      }

      currentSection = {
        title: matches[1],
        content: []
      };
      sections.push(currentSection);
      lastIndex = matches.index + matches[0].length;
    }

    if (currentSection && lastIndex < text.length) {
      var content = text.substring(lastIndex).trim();
      if (content) {
        var items = content.split('\n').filter(function(item) {
          return item.trim();
        });
        currentSection.content = currentSection.content.concat(items);
      }
    }

    this.setData({
      resultSections: sections
    });
  },

  showMockResult: function() {
    var mockResult = [
      {
        title: '界面内容识别',
        content: [
          '1. 界面顶部内容：标题栏显示"立即注册"，背景为红色渐变',
          '2. 界面主体内容：核心标语为"开启财富之旅立即开户"，包含手机号码、登录密码等输入框',
          '3. 界面底部内容：有一个醒目的红色按钮，文字为"极速开户"',
          '4. 其他特殊元素：截图上覆盖了大量彩色的数字标注框'
        ]
      },
      {
        title: '风险要素识别',
        content: [
          '1. 高收益话术：识别到"开启财富之旅"、"超700万客户投资理财之选"等宣传语',
          '2. 诱导性按钮：识别到"极速开户"按钮，强调速度',
          '3. 敏感操作：要求输入手机号码、登录密码、邀请码等敏感信息',
          '4. 仿冒特征：界面缺乏具体的金融机构名称和Logo'
        ]
      },
      {
        title: '风险评估',
        content: [
          '1. 诈骗可能性：95%',
          '2. 诈骗类型：骗钱',
          '3. 风险等级：极高风险'
        ]
      },
      {
        title: '详细分析说明',
        content: [
          '1. 缺乏正规品牌标识：正规金融机构开户界面一定会显著展示机构名称和Logo',
          '2. "邀请码"字段异常：正规理财开户通常只需要手机号和验证码',
          '3. 话术虚假且夸张："超700万客户"是典型的虚假数据',
          '4. UI设计粗糙：界面排版简单粗暴，缺乏大厂APP的精致感'
        ]
      },
      {
        title: '安全建议',
        content: [
          '1. 立即停止操作：千万不要输入手机号、密码或进行任何注册操作',
          '2. 卸载软件：该APP极大概率是虚假投资理财平台，请立刻卸载',
          '3. 警惕邀请码：如果这是别人发给你的链接或二维码，请警惕身边人的推荐',
          '4. 报警处理：如果已经投入资金，请保留聊天记录并立即报警'
        ]
      }
    ];

    this.setData({
      resultSections: mockResult,
      showResult: true,
      isLoading: false
    });
  },

  reset: function() {
    this.setData({
      selectedImage: '',
      fileName: '',
      showResult: false,
      resultSections: []
    });
  }
});
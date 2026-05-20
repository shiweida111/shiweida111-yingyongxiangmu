# AI图像检测小程序 - 部署指南

## 项目结构

```
code_1227/
├── 3_app.py                    # Flask后端服务
├── requirements.txt            # Python依赖列表
├── ai_gen_detector_xgb.joblib  # XGBoost模型文件（需训练生成）
├── unit/
│   └── lightweight_ai_detect.py # 特征提取模块
└── miniprogram/                # 微信小程序前端
    ├── app.js                  # 小程序入口
    ├── app.json                # 小程序配置
    ├── app.wxss                # 全局样式
    ├── project.config.json     # 项目配置
    ├── images/                 # 图标资源
    └── pages/
        ├── index/              # 首页
        ├── detect/             # 检测页
        └── result/             # 结果页
```

---

## 第一步：部署后端服务

### 1.1 安装依赖

```bash
# 进入项目目录
cd code_1227

# 创建虚拟环境（推荐）
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt
```

### 1.2 训练模型（首次部署）

```bash
# 确保数据集路径正确，运行训练脚本
python 1_train_and_eval_xgb.py

# 训练完成后会生成模型文件：ai_gen_detector_xgb.joblib
```

### 1.3 启动后端服务

```bash
# 开发模式（用于测试）
python 3_app.py

# 生产模式（使用Gunicorn）
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5173 3_app:app
```

### 1.4 服务配置说明

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| 端口 | 服务监听端口 | 5173 |
| UPLOAD_FOLDER | 上传文件存储目录 | uploads/ |
| MODEL_PATH | 模型文件路径 | ./ai_gen_detector_xgb.joblib |
| OPENAI_API_KEY | 硅基流动API密钥 | 需要替换 |

---

## 第二步：配置微信小程序

### 2.1 获取小程序账号

1. 访问 [微信公众平台](https://mp.weixin.qq.com/)
2. 注册并登录小程序账号
3. 在「开发」→「开发设置」中获取：
   - AppID
   - 服务器域名配置

### 2.2 修改小程序配置

#### 修改 miniprogram/project.config.json
```json
{
  "appid": "你的小程序AppID",
  "projectname": "ai-image-detector"
}
```

#### 修改 miniprogram/app.js
```javascript
globalData: {
  apiBase: 'http://你的服务器IP:5173'  // 替换为你的后端服务地址
}
```

### 2.3 配置服务器域名

在微信公众平台「开发」→「开发设置」→「服务器域名」中添加：

| 域名类型 | 域名 |
|---------|------|
| request合法域名 | http://你的服务器IP:5173 |
| uploadFile合法域名 | http://你的服务器IP:5173 |
| downloadFile合法域名 | http://你的服务器IP:5173 |

> **注意**：正式上线需要使用已备案的HTTPS域名

---

## 第三步：添加图标资源

将以下图标文件放入 `miniprogram/images/` 目录：

| 文件名 | 说明 | 尺寸 |
|--------|------|------|
| home.png | 首页图标（未选中） | 81×81px |
| home-active.png | 首页图标（选中） | 81×81px |
| camera.png | 检测图标（未选中） | 81×81px |
| camera-active.png | 检测图标（选中） | 81×81px |

---

## 第四步：使用开发者工具导入项目

### 4.1 下载微信开发者工具

下载地址：[https://developers.weixin.qq.com/miniprogram/dev/devtools/download.html](https://developers.weixin.qq.com/miniprogram/dev/devtools/download.html)

### 4.2 导入项目

1. 打开微信开发者工具
2. 选择「小程序」→「导入项目」
3. 选择 `miniprogram/` 目录
4. 输入项目名称和AppID
5. 点击「确定」导入

### 4.3 预览测试

1. 点击工具栏的「预览」按钮
2. 使用微信扫描二维码
3. 在手机上测试小程序功能

---

## 第五步：上传代码并发布

### 5.1 上传代码

1. 在开发者工具中点击「上传」
2. 填写版本号和项目备注
3. 点击「确定」上传

### 5.2 提交审核

1. 登录微信公众平台
2. 进入「开发管理」→「开发版本」
3. 找到刚上传的版本，点击「提交审核」
4. 填写审核信息，等待审核结果

### 5.3 发布上线

审核通过后，在「版本管理」中点击「发布」即可上线。

---

## API接口说明

### GET /api/health
健康检查接口

**响应示例：**
```json
{
  "success": true,
  "code": 200,
  "message": "服务正常运行",
  "data": {
    "model_loaded": true,
    "timestamp": "2024-01-01T12:00:00"
  }
}
```

### POST /api/detect
图像检测接口

**请求参数：**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| file | File | 是 | 图像文件（JPG/PNG） |
| model_type | string | 否 | 引擎类型：xgb/heuristic |

**响应示例：**
```json
{
  "success": true,
  "code": 200,
  "message": "检测成功",
  "data": {
    "detect_id": "detect_20240101_120000_abc123",
    "prob_fake": 0.85,
    "result_text": "AI生成图像",
    "radar_features": {...},
    "risk_score": "0.40",
    "risk_details": ["检测到 1 张人脸"],
    "image_url": "http://xxx/uploads/xxx.jpg",
    "detect_time": "2024-01-01 12:00:00"
  }
}
```

### POST /api/analyze
LLM图像分析接口

**请求参数：**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| file | File | 是 | 图像文件（JPG/PNG） |
| category | string | 否 | 分析类别：fraud/gambling/pornography/deepfake |

---

## 常见问题

### Q1: 小程序无法连接后端服务？

**解决方案：**
1. 确保后端服务已启动且运行正常
2. 检查服务器防火墙是否开放5173端口
3. 确认小程序的request合法域名已配置正确
4. 使用IP地址而非localhost（小程序不支持localhost）

### Q2: 模型文件不存在？

**解决方案：**
1. 运行 `python 1_train_and_eval_xgb.py` 训练模型
2. 确保训练脚本中的数据集路径正确
3. 检查模型文件是否生成在正确位置

### Q3: 上传图片失败？

**解决方案：**
1. 检查图片格式是否为JPG/PNG
2. 确保图片大小不超过5MB
3. 检查服务器磁盘空间是否充足

---

## 技术支持

如遇问题，请检查：
1. 后端服务日志
2. 微信开发者工具控制台
3. 网络请求是否正常
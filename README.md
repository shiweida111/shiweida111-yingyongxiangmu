# 识伪防诈助手

一个微信小程序，用于识别图像真伪和涉诈风险内容。

## 📁 项目结构

```
应用项目开发111/
├── miniprogram/        # 微信小程序前端（实际使用）
│   ├── app.js         # 小程序入口文件
│   ├── app.json       # 小程序配置
│   ├── app.wxss       # 全局样式
│   ├── project.config.json  # 项目配置
│   ├── images/        # 图标资源
│   ├── pages/         # 页面目录
│   │   ├── index/     # 首页
│   │   ├── detect/    # 检测页面
│   │   ├── result/    # 结果页面
│   │   ├── mine/      # 个人中心
│   │   ├── settings/  # 设置页面
│   │   ├── history/   # 历史记录
│   │   └── history-detail/  # 历史详情
│   └── utils/         # 工具函数
│       └── i18n.js    # 国际化配置
├── backend/           # 后端API服务
│   ├── 3_app.py       # Flask 后端服务主程序
│   ├── app.py         # Flask 后端服务
│   ├── analyze_image.py   # 图像分析模块
│   ├── scam_detector.py   # 涉诈检测模块
│   ├── report_generator.py  # 报告生成模块
│   ├── scam_check_web.py    # Web 涉诈检查
│   ├── gen_detector_xgb.joblib  # XGBoost检测模型
│   ├── requirements.txt   # Python依赖
│   ├── pyproject.toml  # 项目配置
│   └── uv.lock        # 依赖锁定文件
├── docs/              # 文档目录
│   └── DEPLOYMENT.md  # 部署文档
├── tests/             # 测试文件
│   ├── test_api.py       # API测试
│   ├── test_llm.py       # LLM测试
│   ├── test_features.py   # 特征测试
│   ├── test_data_flow.py # 数据流程测试
│   ├── test_response.py # 响应测试
│   └── test_js_logic.js # JS逻辑测试
├── tools/             # 工具脚本
│   ├── 1_train_and_eval_xgb.py  # 训练XGBoost模型
│   ├── 2_detect_image_xgb.py   # 使用XGBoost检测
│   ├── generate_icons.py          # 图标生成工具
│   └── unit/                   # 单元工具模块
├── data/              # 数据文件
│   ├── test_images/   # 测试图片
│   └── templates/     # HTML模板
├── README.md         # 项目说明
└── .gitignore       # Git忽略配置
```

## 功能特性

### 图像检测
- 图像深伪鉴别：鉴别图像是否为 AI 生成
- 涉诈程序截图检测：分析程序是否存在诈骗风险
- 涉诈聊天记录检测：分析聊天记录是否存在诈骗风险

### 功能设置
- 字体大小调整：支持五档字体大小
- 多语言支持：中文、English、日本語、Français、한국어、Deutsch

### 个人中心
- 微信登录与绑定
- 分析记录查询
- 设置与关于我们

## 技术栈

- **前端**: 微信小程序 (WXML, WXSS, JavaScript)
- **后端**: Flask (Python)
- **API**: OpenAI API (Qwen/Qwen3.6-35B-A3B)

## 🚀 快速开始

### 后端启动

```bash
cd backend
python 3_app.py
```

### 前端开发

1. 使用微信开发者工具打开 `miniprogram` 目录
2. 配置小程序 AppID
3. 编译运行

## 📋 目录说明

- **miniprogram/** - 微信小程序前端，这是你日常开发的主要目录
- **backend/** - 后端API服务，处理图像检测和分析请求
- **docs/** - 项目文档，包括部署指南
- **tests/** - 测试文件，用于验证功能是否正常
- **tools/** - 辅助工具脚本
- **data/** - 测试数据和模板文件

## 配置说明

后端服务默认运行在 `http://localhost:5000`，请确保前端配置正确的 API 地址。

## 许可证

MIT License
# 识伪防诈助手

一个微信小程序，用于识别图像真伪和涉诈风险内容。

## 项目结构

```
应用项目开发111/
├── backend/           # 后端代码
│   └── app.py         # Flask 后端服务
├── frontend/          # 前端代码（微信小程序）
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
├── docs/              # 文档目录
└── .gitignore         # Git 忽略配置
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

## 快速开始

### 后端启动

```bash
cd backend
python app.py
```

### 前端开发

1. 使用微信开发者工具打开 `frontend` 目录
2. 配置小程序 AppID
3. 编译运行

## 配置说明

后端服务默认运行在 `http://localhost:5000`，请确保前端配置正确的 API 地址。

## 许可证

MIT License
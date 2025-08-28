# 🔧 ContestTrade 配置设置指南

## 📋 快速开始

### 1. 复制配置模板
```bash
cp config_template.yaml config.yaml
```

### 2. 获取API密钥
访问 [DeepSeek API](https://platform.deepseek.com/) 获取您的API密钥

### 3. 配置API密钥
编辑 `config.yaml` 文件，填入您的API密钥：

```yaml
llm:
  base_url: "https://api.deepseek.com"
  api_key: "YOUR_DEEPSEEK_API_KEY_HERE"  # 替换为您的密钥
  model_name: "deepseek-chat"

llm_thinking:
  base_url: "https://api.deepseek.com"  
  api_key: "YOUR_DEEPSEEK_API_KEY_HERE"  # 替换为您的密钥
  model_name: "deepseek-reasoner"

vlm:
  base_url: "https://api.deepseek.com"
  api_key: "YOUR_DEEPSEEK_API_KEY_HERE"  # 替换为您的密钥
  model_name: "deepseek-chat"
```

### 4. 验证配置
```bash
python -m cli.main config
```

## ⚠️ 重要提醒

- `config.yaml` 文件包含敏感信息，已添加到 `.gitignore`
- 该文件不会被提交到GitHub
- 请妥善保管您的API密钥
- 不要在公共渠道分享包含API密钥的配置文件

## 🚀 运行系统

配置完成后，即可运行ContestTrade系统：

```bash
python -m cli.main run
```

## 📖 更多配置选项

查看 `config_template.yaml` 了解所有可用的配置选项，包括：

- Tushare API密钥（可选）
- 其他数据源API密钥
- 智能体配置参数
- 系统语言设置
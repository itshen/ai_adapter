# AI模型适配器

一个统一的AI模型适配器，支持多种AI服务提供商，包括通义千问(Qwen)、OpenRouter和Ollama。

## ✨ 特性

- 🔄 **统一接口**: 为不同AI模型提供一致的API
- 🌊 **流式支持**: 支持流式和非流式聊天
- 🛠️ **工具调用**: 集成工具调用功能
- 🔧 **配置管理**: 基于环境变量的配置系统
- 🚀 **FastAPI服务**: 内置HTTP API服务
- 🔄 **重试机制**: 自动重试和错误处理
- 📊 **类型安全**: 完整的类型注解

## 🏗️ 重构改进

相比原版本，重构版本包含以下改进：

### ✅ 已修复的问题
1. **配置管理**: 使用dataclass和环境变量管理配置
2. **错误处理**: 添加自定义异常类和重试机制
3. **代码重复**: 提取HTTPClient公共组件
4. **依赖注入**: 改进适配器工厂模式
5. **类型安全**: 完善类型注解

### 🔧 架构改进
- **HTTPClient**: 统一HTTP请求处理
- **ConfigManager**: 环境变量配置管理
- **AdapterFactory**: 工厂模式创建适配器
- **异常体系**: 结构化异常处理

## 📦 安装

```bash
pip install -r requirements.txt
```

## 🚀 快速开始

### 环境变量配置

```bash
# Qwen配置
export QWEN_API_KEY="your-qwen-api-key"
export QWEN_MODEL="qwen-flash"

# OpenRouter配置  
export OPENROUTER_API_KEY="your-openrouter-api-key"
export OPENROUTER_MODEL="qwen/qwen3-next-80b-a3b-instruct"

# Ollama配置
export OLLAMA_HOST="http://localhost:11434"
export OLLAMA_MODEL="qwen3:0.6b"

# LMStudio配置
export LMSTUDIO_HOST="http://localhost:1234"
export LMSTUDIO_MODEL="local-model"

# OpenAI兼容配置 (默认SiliconFlow)
export OPENAI_COMPATIBLE_API_KEY="your-api-key"
export OPENAI_COMPATIBLE_BASE_URL="https://api.siliconflow.cn/v1"
export OPENAI_COMPATIBLE_MODEL="Qwen/Qwen3-Coder-30B-A3B-Instruct"
```

### 启动FastAPI服务

```bash
python3.11 model_adapter_refactored.py
```

服务将在 `http://localhost:6688` 启动

### API文档

访问 `http://localhost:6688/docs` 查看完整的API文档

## 📖 使用示例

### Python代码使用

```python
from model_adapter_refactored import ModelManager

# 创建管理器
manager = ModelManager()

# 获取适配器
adapter = manager.get_adapter("qwen")

# 聊天
messages = [{"role": "user", "content": "你好"}]
response = await adapter.chat(messages)
print(response)

# 流式聊天
async for chunk in adapter.chat_stream(messages):
    print(chunk, end="")
```

### HTTP API使用

```bash
# 非流式聊天
curl -X POST "http://localhost:6688/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "你好"}],
    "provider": "qwen"
  }'

# 流式聊天
curl -X POST "http://localhost:6688/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "你好"}],
    "provider": "qwen",
    "stream": true
  }'

# LMStudio聊天
curl -X POST "http://localhost:6688/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "你好"}],
    "provider": "lmstudio"
  }'

# OpenAI兼容API聊天 (SiliconFlow)
curl -X POST "http://localhost:6688/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "你好"}],
    "provider": "openai_compatible",
    "api_key": "your-api-key",
    "base_url": "https://api.siliconflow.cn/v1",
    "model": "Qwen/Qwen3-Coder-30B-A3B-Instruct"
  }'
```

## 🔧 支持的适配器

| 适配器 | 描述 | 配置要求 |
|--------|------|----------|
| qwen | 通义千问 | QWEN_API_KEY |
| openrouter | OpenRouter | OPENROUTER_API_KEY |
| ollama | 本地Ollama | OLLAMA_HOST (可选) |
| lmstudio | LMStudio本地服务 | LMSTUDIO_HOST (可选) |
| openai_compatible | OpenAI兼容API | API_KEY + BASE_URL (每次传递) |

## 📁 文件结构

```
ai_adapter/
├── model_adapter_refactored.py   # 重构版本 ⭐
├── requirements.txt              # 依赖文件
├── README.md                    # 说明文档
├── test_config.py               # 配置管理测试
├── test_error_handling.py       # 错误处理测试
├── test_api.py                  # API接口测试
└── run_tests.py                 # 测试运行器
```

## 🛠️ 开发

### 运行测试

```bash
# 运行所有测试
python3.11 run_tests.py

# 交互式选择测试
python3.11 run_tests.py --interactive

# 运行单个测试
python3.11 test_config.py          # 配置管理测试
python3.11 test_error_handling.py  # 错误处理测试
python3.11 test_api.py             # API接口测试（需要服务运行）
```

### 测试覆盖

| 测试文件 | 测试内容 | 说明 |
|---------|---------|------|
| `test_config.py` | 配置管理、适配器工厂 | 测试环境变量配置和适配器创建 |
| `test_error_handling.py` | 异常处理、重试机制 | 测试各种错误情况的处理 |
| `test_api.py` | FastAPI接口 | 测试HTTP API的各个端点 |
| `run_tests.py` | 测试运行器 | 统一运行所有测试并生成报告 |

### 添加新适配器

1. 创建配置类
2. 实现适配器类
3. 在AdapterFactory中注册
4. 添加ConfigManager方法

## 📝 API接口

### POST /chat
聊天接口

**请求体:**
```json
{
  "messages": [{"role": "user", "content": "消息内容"}],
  "provider": "qwen|openrouter|ollama",
  "model": "模型名称(可选)",
  "stream": false,
  "tools": []
}
```

### GET /adapters
获取可用适配器列表

### GET /health
健康检查

## 🔍 故障排除

1. **配置错误**: 检查环境变量是否正确设置
2. **网络错误**: 检查网络连接和API密钥
3. **模型错误**: 确认模型名称正确
4. **端口占用**: 确保6688端口未被占用

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交Issue和Pull Request！

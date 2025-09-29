# 更新日志

## v2.0.0 - 简化版本 (2025-01-27)

### 🎯 重大变更
- **移除工具调用功能**: 删除了所有与AI工具调用相关的代码和提示词
- **专注核心功能**: 只保留消息收发和图片生成两个核心功能
- **简化API接口**: 移除了`tools`参数，使接口更加简洁

### ✨ 新增功能
- 创建了简化版的模型适配器 (`model_adapter_refactored.py`)
- 创建了简化版的演示代码 (`demo.py`)
- 添加了专门的测试脚本 (`test_simplified.py`)
- 更新了README文档，突出简化后的功能

### 🔧 技术改进
- **更清晰的代码结构**: 移除了复杂的工具处理逻辑
- **更简单的接口**: `chat()` 和 `chat_stream()` 方法只需要 `messages` 参数
- **更好的维护性**: 代码量减少，更容易理解和维护
- **更快的启动**: 服务端口改为8888，避免与其他服务冲突

### 📦 支持的适配器

#### 💬 文本聊天适配器 (6个)
- `qwen`: 通义千问
- `openrouter`: OpenRouter多模型平台
- `tencent_hunyuan`: 腾讯云混元
- `ollama`: 本地Ollama服务
- `lmstudio`: 本地LMStudio服务
- `openai_compatible`: OpenAI兼容接口

#### 🎨 图片生成适配器 (2个)
- `tongyi_wanxiang`: 通义万象2.2
- `jimeng`: 即梦AI 4.0

### 🗑️ 移除的功能
- 所有工具调用相关的代码
- 复杂的工具描述和提示词生成
- `_process_messages_with_tools` 方法
- 工具调用格式化逻辑
- 增强版OpenRouter适配器的工具功能

### 📋 API变更

#### 之前的接口
```python
async def chat(self, messages: List[Dict], tools: Optional[List[Dict]] = None, **kwargs)
async def chat_stream(self, messages: List[Dict], tools: Optional[List[Dict]] = None, **kwargs)
```

#### 现在的接口
```python
async def chat(self, messages: List[Dict], **kwargs)
async def chat_stream(self, messages: List[Dict], **kwargs)
```

### 🧪 测试结果
- ✅ 所有适配器创建正常
- ✅ 参数验证功能正常
- ✅ 错误处理机制正常
- ✅ API接口简化成功
- ✅ 导入结构完整

### 📁 文件变更
- `model_adapter_refactored.py`: 主要的简化版适配器文件
- `demo.py`: 简化版演示代码
- `test_simplified.py`: 新增的测试脚本
- `README.md`: 更新文档说明
- `model_adapter_refactored_backup.py`: 备份的原始复杂版本
- `demo_backup.py`: 备份的原始演示代码

### 🎯 使用建议
- 如果只需要基本的消息收发和图片生成功能，使用当前简化版本
- 如果需要复杂的工具调用功能，可以使用备份的复杂版本
- 建议大多数用户使用简化版本，更稳定且易于维护

### 📞 技术支持
- GitHub: https://github.com/itshen/
- 项目地址: https://github.com/itshen/ai_adapter

---

## v1.0.0 - 初始版本 (2025-01-26)

### ✨ 初始功能
- 支持多种AI模型的统一接口
- 文本聊天功能（流式和非流式）
- 图片生成功能
- 工具调用功能
- 完整的错误处理和重试机制
- FastAPI服务接口
- 详细的演示和测试代码

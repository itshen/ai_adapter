# AI模型适配器使用指南

本指南详细说明了如何在其他项目中引用和使用这个AI模型适配器库。

## 📦 安装方式

### 方式一：从PyPI安装（推荐，发布后可用）
```bash
pip install ai-model-adapter
```

### 方式二：从GitHub直接安装
```bash
pip install git+https://github.com/itshen/ai_adapter.git
```

### 方式三：本地开发安装
```bash
git clone https://github.com/itshen/ai_adapter.git
cd ai_adapter
pip install -e .
```

### 方式四：手动安装依赖（使用源码）
```bash
git clone https://github.com/itshen/ai_adapter.git
cd ai_adapter
pip install -r requirements.txt
```

## 🚀 快速开始

### 1. 基本导入和使用

```python
import asyncio
from ai_model_adapter import ModelManager

async def main():
    # 创建模型管理器
    manager = ModelManager()
    
    # 获取适配器
    adapter = manager.get_adapter("qwen", {
        "api_key": "your-api-key",
        "model": "qwen-flash"
    })
    
    # 发送消息
    messages = [{"role": "user", "content": "你好"}]
    response = await adapter.chat(messages)
    print(response)

asyncio.run(main())
```

### 2. 直接使用适配器类

```python
import asyncio
from ai_model_adapter import QwenAdapter, QwenConfig

async def main():
    # 创建配置
    config = QwenConfig(
        api_key="your-api-key",
        model="qwen-flash"
    )
    
    # 创建适配器
    adapter = QwenAdapter(config)
    
    # 使用适配器
    messages = [{"role": "user", "content": "你好"}]
    response = await adapter.chat(messages)
    print(response)

asyncio.run(main())
```

### 3. 创建FastAPI应用

```python
from ai_model_adapter import create_app
import uvicorn

# 创建应用
app = create_app()

# 添加自定义路由
@app.get("/custom")
async def custom_endpoint():
    return {"message": "自定义端点"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8888)
```

## 📚 详细使用说明

### 支持的适配器

#### 文本聊天适配器
- `qwen`: 通义千问
- `openrouter`: OpenRouter多模型平台
- `tencent_hunyuan`: 腾讯云混元
- `ollama`: 本地Ollama服务
- `lmstudio`: LMStudio本地服务
- `openai_compatible`: OpenAI兼容接口

#### 图片生成适配器
- `tongyi_wanxiang`: 通义万象
- `jimeng`: 即梦AI

### 配置方式

#### 1. 环境变量配置（推荐）
```bash
export QWEN_API_KEY='your-qwen-api-key'
export DASHSCOPE_API_KEY='your-dashscope-api-key'
export OPENROUTER_API_KEY='your-openrouter-api-key'
```

#### 2. 运行时配置
```python
adapter = manager.get_adapter("qwen", {
    "api_key": "your-api-key",
    "model": "qwen-flash"
})
```

### 流式输出

```python
import asyncio
from ai_model_adapter import ModelManager

async def streaming_chat():
    manager = ModelManager()
    adapter = manager.get_adapter("qwen", {
        "api_key": "your-api-key"
    })
    
    messages = [{"role": "user", "content": "写一首诗"}]
    
    async for chunk in adapter.chat_stream(messages):
        if chunk.get("content"):
            print(chunk["content"], end="", flush=True)

asyncio.run(streaming_chat())
```

### 图片生成

```python
import asyncio
from ai_model_adapter import ModelManager

async def generate_image():
    manager = ModelManager()
    adapter = manager.get_adapter("tongyi_wanxiang", {
        "api_key": "your-dashscope-api-key"
    })
    
    # 异步生成
    result = await adapter.generate_image("一朵樱花")
    print(f"任务ID: {result['task_id']}")
    
    # 查询结果
    final_result = await adapter.get_task_result(result['task_id'])
    print(f"图片URL: {final_result['images']}")

asyncio.run(generate_image())
```

## 🛠️ 命令行工具

安装包后，可以使用命令行工具：

```bash
# 启动API服务器
ai-adapter serve

# 指定端口
ai-adapter serve --port 9000

# 指定主机和端口
ai-adapter serve --host 0.0.0.0 --port 8888

# 开发模式（自动重载）
ai-adapter serve --reload

# 查看版本
ai-adapter --version

# 查看帮助
ai-adapter --help
```

## 🔧 在其他项目中集成

### Django项目集成

```python
# views.py
import asyncio
from django.http import JsonResponse
from ai_model_adapter import ModelManager

def chat_view(request):
    if request.method == 'POST':
        message = request.POST.get('message')
        
        async def get_response():
            manager = ModelManager()
            adapter = manager.get_adapter("qwen", {
                "api_key": "your-api-key"
            })
            
            messages = [{"role": "user", "content": message}]
            return await adapter.chat(messages)
        
        response = asyncio.run(get_response())
        return JsonResponse({"response": response})
```

### Flask项目集成

```python
# app.py
import asyncio
from flask import Flask, request, jsonify
from ai_model_adapter import ModelManager

app = Flask(__name__)

@app.route('/chat', methods=['POST'])
def chat():
    message = request.json.get('message')
    
    async def get_response():
        manager = ModelManager()
        adapter = manager.get_adapter("qwen", {
            "api_key": "your-api-key"
        })
        
        messages = [{"role": "user", "content": message}]
        return await adapter.chat(messages)
    
    response = asyncio.run(get_response())
    return jsonify({"response": response})

if __name__ == '__main__':
    app.run(port=8000)
```

### Jupyter Notebook使用

```python
# 在Jupyter Notebook中使用
import asyncio
from ai_model_adapter import ModelManager

# 创建管理器
manager = ModelManager()

# 获取适配器
adapter = manager.get_adapter("qwen", {
    "api_key": "your-api-key"
})

# 使用适配器
messages = [{"role": "user", "content": "解释一下机器学习"}]
response = await adapter.chat(messages)
print(response)
```

## 🔒 安全注意事项

1. **API密钥管理**：
   - 不要在代码中硬编码API密钥
   - 使用环境变量或配置文件
   - 在生产环境中使用密钥管理服务

2. **网络安全**：
   - 在生产环境中使用HTTPS
   - 设置适当的CORS策略
   - 实施请求限制和认证

3. **错误处理**：
   - 捕获并适当处理异常
   - 不要在错误信息中暴露敏感信息

## 🐛 常见问题

### Q: 如何处理API密钥错误？
A: 检查环境变量设置，确保API密钥正确且有效。

### Q: 如何处理网络超时？
A: 可以在配置中设置timeout参数：
```python
adapter = manager.get_adapter("qwen", {
    "api_key": "your-api-key",
    "timeout": 120.0  # 2分钟超时
})
```

### Q: 如何启用调试日志？
A: 设置日志级别：
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Q: 如何在同步代码中使用异步适配器？
A: 使用asyncio.run()：
```python
import asyncio

def sync_function():
    async def async_chat():
        # 异步代码
        pass
    
    return asyncio.run(async_chat())
```

## 📞 获取帮助

- GitHub Issues: https://github.com/itshen/ai_adapter/issues
- 文档: https://github.com/itshen/ai_adapter#readme
- 示例代码: https://github.com/itshen/ai_adapter/blob/main/example_usage.py

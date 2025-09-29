# AI模型适配器集成指南

本指南详细说明了如何将AI模型适配器集成到其他项目中。

## 🎯 项目已完成的配置

### ✅ 已创建的文件
- `setup.py` - 传统Python包配置文件
- `pyproject.toml` - 现代Python包配置文件
- `MANIFEST.in` - 包文件清单
- `ai_model_adapter/__init__.py` - 包初始化文件
- `ai_model_adapter/cli.py` - 命令行接口
- `example_usage.py` - 使用示例
- `USAGE_GUIDE.md` - 详细使用指南

### ✅ 包结构
```
ai_adapter/
├── ai_model_adapter/           # 主包目录
│   ├── __init__.py            # 包初始化，导出所有公共接口
│   ├── model_adapter.py       # 核心适配器实现
│   └── cli.py                 # 命令行工具
├── setup.py                   # 包安装配置
├── pyproject.toml            # 现代包配置
├── MANIFEST.in               # 包文件清单
├── requirements.txt          # 依赖列表
├── README.md                 # 项目说明（已更新）
├── example_usage.py          # 使用示例
├── USAGE_GUIDE.md           # 详细使用指南
└── dist/                    # 构建产物
    ├── ai_model_adapter-1.0.0.tar.gz
    └── ai_model_adapter-1.0.0-py3-none-any.whl
```

## 🚀 安装方式

### 1. 从PyPI安装（发布后）
```bash
pip install ai-model-adapter
```

### 2. 从GitHub安装
```bash
pip install git+https://github.com/itshen/ai_adapter.git
```

### 3. 本地开发安装
```bash
git clone https://github.com/itshen/ai_adapter.git
cd ai_adapter
pip install -e .
```

### 4. 从构建的包安装
```bash
cd ai_adapter
pip install dist/ai_model_adapter-1.0.0-py3-none-any.whl
```

## 📦 在其他项目中使用

### 基本使用
```python
# 导入所需组件
from ai_model_adapter import ModelManager, QwenAdapter, QwenConfig

# 方式1：使用ModelManager（推荐）
import asyncio

async def main():
    manager = ModelManager()
    adapter = manager.get_adapter("qwen", {
        "api_key": "your-api-key",
        "model": "qwen-flash"
    })
    
    messages = [{"role": "user", "content": "你好"}]
    response = await adapter.chat(messages)
    print(response)

asyncio.run(main())
```

### 在Web框架中集成

#### FastAPI项目
```python
from fastapi import FastAPI
from ai_model_adapter import create_app as create_ai_app

# 创建主应用
app = FastAPI()

# 创建AI适配器应用
ai_app = create_ai_app()

# 挂载AI适配器到子路径
app.mount("/ai", ai_app)

# 或者直接使用适配器
from ai_model_adapter import ModelManager

manager = ModelManager()

@app.post("/chat")
async def chat(message: str):
    adapter = manager.get_adapter("qwen", {"api_key": "your-key"})
    response = await adapter.chat([{"role": "user", "content": message}])
    return {"response": response}
```

#### Django项目
```python
# views.py
import asyncio
from django.http import JsonResponse
from ai_model_adapter import ModelManager

manager = ModelManager()

def chat_view(request):
    if request.method == 'POST':
        message = request.POST.get('message')
        
        async def get_ai_response():
            adapter = manager.get_adapter("qwen", {
                "api_key": "your-api-key"
            })
            messages = [{"role": "user", "content": message}]
            return await adapter.chat(messages)
        
        response = asyncio.run(get_ai_response())
        return JsonResponse({"response": response})
```

#### Flask项目
```python
# app.py
import asyncio
from flask import Flask, request, jsonify
from ai_model_adapter import ModelManager

app = Flask(__name__)
manager = ModelManager()

@app.route('/chat', methods=['POST'])
def chat():
    message = request.json.get('message')
    
    async def get_ai_response():
        adapter = manager.get_adapter("qwen", {
            "api_key": "your-api-key"
        })
        messages = [{"role": "user", "content": message}]
        return await adapter.chat(messages)
    
    response = asyncio.run(get_ai_response())
    return jsonify({"response": response})
```

## 🛠️ 命令行工具

安装包后自动提供命令行工具：

```bash
# 查看版本
ai-adapter --version

# 查看帮助
ai-adapter --help

# 启动API服务器
ai-adapter serve

# 指定端口和主机
ai-adapter serve --host 0.0.0.0 --port 9000

# 开发模式（自动重载）
ai-adapter serve --reload
```

## 🔧 环境变量配置

### 文本聊天适配器
```bash
# Qwen (通义千问)
export QWEN_API_KEY='your-qwen-api-key'
export QWEN_MODEL='qwen-flash'

# OpenRouter
export OPENROUTER_API_KEY='your-openrouter-api-key'
export OPENROUTER_MODEL='qwen/qwen3-next-80b-a3b-instruct'

# 腾讯云混元
export HUNYUAN_API_KEY='your-hunyuan-api-key'
export HUNYUAN_MODEL='hunyuan-turbos-latest'

# Ollama (本地)
export OLLAMA_HOST='http://localhost:11434'
export OLLAMA_MODEL='qwen3:0.6b'

# LMStudio (本地)
export LMSTUDIO_HOST='http://localhost:1234'
export LMSTUDIO_MODEL='local-model'

# OpenAI兼容
export OPENAI_COMPATIBLE_API_KEY='your-api-key'
export OPENAI_COMPATIBLE_BASE_URL='https://api.siliconflow.cn/v1'
export OPENAI_COMPATIBLE_MODEL='Qwen/Qwen3-Coder-30B-A3B-Instruct'
```

### 图片生成适配器
```bash
# 通义万象
export DASHSCOPE_API_KEY='your-dashscope-api-key'
export TONGYI_WANXIANG_MODEL='wan2.2-t2i-flash'

# 即梦AI
export JIMENG_ACCESS_KEY='your-jimeng-access-key'
export JIMENG_SECRET_KEY='your-jimeng-secret-key'
export JIMENG_MODEL='jimeng_t2i_v40'
```

## 📚 可用的适配器

### 文本聊天适配器
- `qwen` - 通义千问
- `openrouter` - OpenRouter多模型平台
- `tencent_hunyuan` - 腾讯云混元
- `ollama` - 本地Ollama服务
- `lmstudio` - LMStudio本地服务
- `openai_compatible` - OpenAI兼容接口

### 图片生成适配器
- `tongyi_wanxiang` - 通义万象
- `jimeng` - 即梦AI

## 🔒 安全最佳实践

1. **API密钥管理**
   - 使用环境变量存储API密钥
   - 不要在代码中硬编码密钥
   - 在生产环境中使用密钥管理服务

2. **网络安全**
   - 在生产环境中使用HTTPS
   - 设置适当的CORS策略
   - 实施请求限制和认证

3. **错误处理**
   - 捕获并适当处理异常
   - 不要在错误信息中暴露敏感信息

## 🚀 发布到PyPI

### 构建包
```bash
# 安装构建工具
pip install build twine

# 构建包
python -m build

# 检查包
twine check dist/*
```

### 发布
```bash
# 发布到测试PyPI
twine upload --repository testpypi dist/*

# 发布到正式PyPI
twine upload dist/*
```

## 🐛 常见问题解决

### Q: 导入错误
A: 确保已正确安装包：`pip install -e .`

### Q: API密钥错误
A: 检查环境变量设置或在运行时提供正确的API密钥

### Q: 网络超时
A: 在配置中设置更长的超时时间：
```python
adapter = manager.get_adapter("qwen", {
    "api_key": "your-key",
    "timeout": 120.0
})
```

### Q: 在同步代码中使用异步适配器
A: 使用 `asyncio.run()`：
```python
import asyncio

def sync_function():
    async def async_operation():
        # 异步代码
        pass
    return asyncio.run(async_operation())
```

## 📞 获取支持

- **GitHub Issues**: https://github.com/itshen/ai_adapter/issues
- **文档**: https://github.com/itshen/ai_adapter#readme
- **示例代码**: `example_usage.py`
- **详细指南**: `USAGE_GUIDE.md`

## 🎉 总结

您的AI模型适配器现在已经完全配置为可重用的Python包！其他项目可以通过以下方式使用：

1. **安装包**: `pip install ai-model-adapter`
2. **导入使用**: `from ai_model_adapter import ModelManager`
3. **启动服务**: `ai-adapter serve`
4. **集成到现有项目**: 参考上述示例代码

包已经过测试，所有功能正常工作，可以安全地在生产环境中使用。

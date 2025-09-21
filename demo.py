#!/usr/bin/env python3
"""
演示脚本 - 展示AI模型适配器的使用方法
"""
import asyncio
import os
from model_adapter_refactored import (
    ModelManager,
    ConfigurationError,
    get_ai_adapter
)

async def demo_basic_usage():
    """演示基本使用方法"""
    print("🚀 **AI模型适配器演示**\n")
    
    # 1. 创建模型管理器
    print("1️⃣ **创建模型管理器**")
    manager = ModelManager()
    print(f"   可用适配器: {manager.list_adapters()}")
    
    # 2. 使用自定义配置创建适配器
    print("\n2️⃣ **使用自定义配置创建Ollama适配器**")
    try:
        ollama_adapter = manager.get_adapter("ollama", {
            "host": "http://localhost:11434",
            "model": "qwen3:0.6b"
        })
        print("   ✅ Ollama适配器创建成功")
        print(f"   📍 服务地址: {ollama_adapter.config.host}")
        print(f"   🤖 模型: {ollama_adapter.config.model}")
    except Exception as e:
        print(f"   ❌ 创建失败: {e}")
    
    # 3. 演示聊天功能（模拟）
    print("\n3️⃣ **演示聊天功能**")
    messages = [
        {"role": "system", "content": "你是一个友好的AI助手"},
        {"role": "user", "content": "你好，请简单介绍一下自己"}
    ]
    
    print("   📝 测试消息:")
    for msg in messages:
        print(f"      {msg['role']}: {msg['content']}")
    
    # 注意：这里不实际调用API，只是演示接口
    print("   ⚠️ 实际API调用需要相应的服务运行")
    
    # 4. 演示工具调用
    print("\n4️⃣ **演示工具调用功能**")
    tools = [
        {
            "function": {
                "name": "get_weather",
                "description": "获取指定城市的天气信息",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "city": {
                            "type": "string",
                            "description": "城市名称"
                        }
                    },
                    "required": ["city"]
                }
            }
        }
    ]
    
    print("   🛠️ 工具定义:")
    print(f"      工具名称: {tools[0]['function']['name']}")
    print(f"      工具描述: {tools[0]['function']['description']}")
    
    # 5. 演示默认适配器获取
    print("\n5️⃣ **演示默认适配器获取**")
    try:
        default_adapter = get_ai_adapter()
        print("   ✅ 默认适配器获取成功")
        print(f"   🔧 适配器类型: {type(default_adapter).__name__}")
    except ConfigurationError as e:
        print(f"   ⚠️ 无法获取默认适配器: {e}")
        print("   💡 请设置环境变量或启动Ollama服务")

def demo_environment_setup():
    """演示环境变量设置"""
    print("\n🌍 **环境变量设置演示**\n")
    
    env_examples = {
        "Qwen (通义千问)": [
            "export QWEN_API_KEY='your-qwen-api-key'",
            "export QWEN_MODEL='qwen-flash'"
        ],
        "OpenRouter": [
            "export OPENROUTER_API_KEY='your-openrouter-api-key'",
            "export OPENROUTER_MODEL='qwen/qwen3-next-80b-a3b-instruct'"
        ],
        "Ollama (本地)": [
            "export OLLAMA_HOST='http://localhost:11434'",
            "export OLLAMA_MODEL='qwen3:0.6b'"
        ],
        "LMStudio (本地)": [
            "export LMSTUDIO_HOST='http://localhost:1234'",
            "export LMSTUDIO_MODEL='local-model'"
        ],
        "OpenAI兼容 (SiliconFlow)": [
            "export OPENAI_COMPATIBLE_API_KEY='your-api-key'",
            "export OPENAI_COMPATIBLE_BASE_URL='https://api.siliconflow.cn/v1'",
            "export OPENAI_COMPATIBLE_MODEL='Qwen/Qwen3-Coder-30B-A3B-Instruct'"
        ]
    }
    
    for service, commands in env_examples.items():
        print(f"📋 **{service}**:")
        for cmd in commands:
            print(f"   {cmd}")
        print()

def demo_api_usage():
    """演示API使用方法"""
    print("🌐 **FastAPI服务使用演示**\n")
    
    print("1️⃣ **启动服务**:")
    print("   python3.11 model_adapter_refactored.py")
    print("   服务地址: http://localhost:6688")
    print("   API文档: http://localhost:6688/docs")
    
    print("\n2️⃣ **API调用示例**:")
    
    # 非流式聊天
    print("\n   📤 **非流式聊天**:")
    print("""   curl -X POST "http://localhost:6688/chat" \\
     -H "Content-Type: application/json" \\
     -d '{
       "messages": [{"role": "user", "content": "你好"}],
       "provider": "ollama"
     }'""")
    
    # 流式聊天
    print("\n   🌊 **流式聊天**:")
    print("""   curl -X POST "http://localhost:6688/chat" \\
     -H "Content-Type: application/json" \\
     -d '{
       "messages": [{"role": "user", "content": "你好"}],
       "provider": "ollama",
       "stream": true
     }'""")
    
    # 健康检查
    print("\n   🏥 **健康检查**:")
    print("   curl http://localhost:6688/health")
    
    # 列出适配器
    print("\n   📋 **列出适配器**:")
    print("   curl http://localhost:6688/adapters")

async def main():
    """主演示函数"""
    print("=" * 60)
    print("🎯 **AI模型适配器 - 完整演示**")
    print("=" * 60)
    
    await demo_basic_usage()
    demo_environment_setup()
    demo_api_usage()
    
    print("\n" + "=" * 60)
    print("🎉 **演示完成！**")
    print("💡 **下一步**:")
    print("   1. 设置环境变量")
    print("   2. 启动FastAPI服务")
    print("   3. 运行测试用例")
    print("   4. 开始使用API")
    print("=" * 60)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 **演示被用户中断**")
    except Exception as e:
        print(f"\n❌ **演示运行异常**: {e}")

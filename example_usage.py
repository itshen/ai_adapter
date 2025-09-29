#!/usr/bin/env python3
"""
AI模型适配器使用示例

这个文件展示了如何在其他项目中使用ai-model-adapter包
"""

import asyncio
import os
from ai_model_adapter import ModelManager, QwenAdapter, QwenConfig

async def basic_usage_example():
    """基本使用示例 - 使用ModelManager"""
    print("=== 基本使用示例 ===")
    
    # 创建模型管理器
    manager = ModelManager()
    
    # 获取Qwen适配器（需要设置环境变量QWEN_API_KEY或在运行时提供）
    try:
        adapter = manager.get_adapter("qwen", {
            "api_key": os.getenv("QWEN_API_KEY", "your-api-key-here"),
            "model": "qwen-flash"
        })
        
        # 发送消息
        messages = [{"role": "user", "content": "你好，请简单介绍一下你自己"}]
        response = await adapter.chat(messages)
        
        print(f"回复: {response}")
        
    except Exception as e:
        print(f"错误: {e}")

async def direct_adapter_example():
    """直接使用适配器示例"""
    print("\n=== 直接使用适配器示例 ===")
    
    try:
        # 创建配置
        config = QwenConfig(
            api_key=os.getenv("QWEN_API_KEY", "your-api-key-here"),
            model="qwen-flash"
        )
        
        # 创建适配器
        adapter = QwenAdapter(config)
        
        # 发送消息
        messages = [{"role": "user", "content": "请用一句话介绍Python编程语言"}]
        response = await adapter.chat(messages)
        
        print(f"回复: {response}")
        
    except Exception as e:
        print(f"错误: {e}")

async def streaming_example():
    """流式输出示例"""
    print("\n=== 流式输出示例 ===")
    
    try:
        manager = ModelManager()
        adapter = manager.get_adapter("qwen", {
            "api_key": os.getenv("QWEN_API_KEY", "your-api-key-here"),
            "model": "qwen-flash"
        })
        
        messages = [{"role": "user", "content": "请写一首关于春天的短诗"}]
        
        print("流式回复: ", end="")
        async for chunk in adapter.chat_stream(messages):
            if chunk.get("content"):
                print(chunk["content"], end="", flush=True)
        print()  # 换行
        
    except Exception as e:
        print(f"错误: {e}")

async def image_generation_example():
    """图片生成示例"""
    print("\n=== 图片生成示例 ===")
    
    try:
        manager = ModelManager()
        adapter = manager.get_adapter("tongyi_wanxiang", {
            "api_key": os.getenv("DASHSCOPE_API_KEY", "your-dashscope-api-key-here")
        })
        
        # 异步生成图片
        result = await adapter.generate_image("一朵盛开的樱花，水彩画风格")
        print(f"图片生成结果: {result}")
        
    except Exception as e:
        print(f"错误: {e}")

def main():
    """主函数"""
    print("AI模型适配器使用示例")
    print("=" * 50)
    print("注意：运行前请设置相应的API密钥环境变量：")
    print("- QWEN_API_KEY: 用于文本聊天")
    print("- DASHSCOPE_API_KEY: 用于图片生成")
    print("=" * 50)
    
    # 运行示例
    asyncio.run(basic_usage_example())
    asyncio.run(direct_adapter_example())
    asyncio.run(streaming_example())
    asyncio.run(image_generation_example())

if __name__ == "__main__":
    main()

"""
AI模型适配器 - 简化版本

一个简化的AI模型适配器，专注于消息收发和图片生成功能。

主要功能：
- 文本聊天：支持Qwen、OpenRouter、腾讯云混元、Ollama、LMStudio等
- 图片生成：支持通义万象、即梦AI等服务
- 统一接口：所有适配器使用相同的接口规范
- 流式支持：支持实时流式文本输出
- 异步任务：图片生成支持异步任务查询

Copyright (c) 2025 Miyang Tech (Zhuhai Hengqin) Co., Ltd.
License: MIT
"""

from .model_adapter import (
    # 异常类
    ModelAdapterError,
    APIError,
    ConfigurationError,
    
    # 配置类
    AdapterConfig,
    QwenConfig,
    OpenRouterConfig,
    TencentHunyuanConfig,
    OllamaConfig,
    LMStudioConfig,
    OpenAICompatibleConfig,
    TongyiWanxiangConfig,
    JimengConfig,
    
    # 适配器基类
    ModelAdapter,
    ImageGenerationAdapter,
    
    # 文本聊天适配器
    QwenAdapter,
    OpenRouterAdapter,
    TencentHunyuanAdapter,
    OllamaAdapter,
    LMStudioAdapter,
    OpenAICompatibleAdapter,
    
    # 图片生成适配器
    TongyiWanxiangAdapter,
    JimengAdapter,
    
    # 管理器
    ModelManager,
    
    # FastAPI应用
    create_app,
)

__version__ = "1.0.3"
__author__ = "洛小山"
__email__ = "contact@miyangtech.com"
__license__ = "MIT"

__all__ = [
    # 版本信息
    "__version__",
    "__author__",
    "__email__",
    "__license__",
    
    # 异常类
    "ModelAdapterError",
    "APIError", 
    "ConfigurationError",
    
    # 配置类
    "AdapterConfig",
    "QwenConfig",
    "OpenRouterConfig",
    "TencentHunyuanConfig",
    "OllamaConfig",
    "LMStudioConfig",
    "OpenAICompatibleConfig",
    "TongyiWanxiangConfig",
    "JimengConfig",
    
    # 适配器基类
    "ModelAdapter",
    "ImageGenerationAdapter",
    
    # 文本聊天适配器
    "QwenAdapter",
    "OpenRouterAdapter", 
    "TencentHunyuanAdapter",
    "OllamaAdapter",
    "LMStudioAdapter",
    "OpenAICompatibleAdapter",
    
    # 图片生成适配器
    "TongyiWanxiangAdapter",
    "JimengAdapter",
    
    # 管理器
    "ModelManager",
    
    # FastAPI应用
    "create_app",
]

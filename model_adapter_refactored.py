"""
模型适配器 - 支持多种AI模型的统一接口
重构版本，改进了错误处理、配置管理和代码结构
"""
import json
import httpx
import asyncio
import os
from datetime import datetime
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, AsyncGenerator
from dataclasses import dataclass
from contextlib import asynccontextmanager

# 自定义异常类
class ModelAdapterError(Exception):
    """模型适配器基础异常"""
    pass

class APIError(ModelAdapterError):
    """API调用异常"""
    pass

class ConfigurationError(ModelAdapterError):
    """配置异常"""
    pass

# 配置类
@dataclass
class AdapterConfig:
    """适配器基础配置"""
    timeout: float = 60.0
    max_retries: int = 3
    retry_delay: float = 1.0

@dataclass  
class QwenConfig:
    """Qwen配置"""
    api_key: str
    model: str
    base_url: str = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
    timeout: float = 60.0
    max_retries: int = 3
    retry_delay: float = 1.0

@dataclass
class OpenRouterConfig:
    """OpenRouter配置"""
    api_key: str
    model: str
    base_url: str = "https://openrouter.ai/api/v1/chat/completions"
    timeout: float = 60.0
    max_retries: int = 3
    retry_delay: float = 1.0

@dataclass
class OllamaConfig:
    """Ollama配置"""
    host: str
    model: str
    timeout: float = 60.0
    max_retries: int = 3
    retry_delay: float = 1.0

@dataclass
class LMStudioConfig:
    """LMStudio配置"""
    host: str
    model: str
    timeout: float = 60.0
    max_retries: int = 3
    retry_delay: float = 1.0

@dataclass
class OpenAICompatibleConfig:
    """OpenAI兼容配置"""
    api_key: str
    model: str
    base_url: str
    timeout: float = 60.0
    max_retries: int = 3
    retry_delay: float = 1.0

# HTTP客户端封装
class HTTPClient:
    """HTTP客户端封装"""
    
    def __init__(self, timeout: float = 60.0, max_retries: int = 3, retry_delay: float = 1.0):
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
    
    @asynccontextmanager
    async def get_client(self):
        """获取HTTP客户端"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            yield client
    
    async def post_json(self, url: str, data: dict, headers: dict = None) -> dict:
        """POST JSON请求"""
        for attempt in range(self.max_retries):
            try:
                async with self.get_client() as client:
                    response = await client.post(url, json=data, headers=headers or {})
                    response.raise_for_status()
                    return response.json()
            except httpx.HTTPError as e:
                if attempt == self.max_retries - 1:
                    raise APIError(f"HTTP请求失败: {e}")
                await asyncio.sleep(self.retry_delay * (attempt + 1))
    
    @asynccontextmanager
    async def post_stream(self, url: str, data: dict, headers: dict = None):
        """POST 流式请求"""
        try:
            async with self.get_client() as client:
                async with client.stream("POST", url, json=data, headers=headers or {}) as response:
                    response.raise_for_status()
                    yield response
        except httpx.HTTPError as e:
            raise APIError(f"流式请求失败: {e}")

class ModelAdapter(ABC):
    """模型适配器基类"""
    
    def __init__(self, config):
        self.config = config
        self.http_client = HTTPClient(
            timeout=config.timeout,
            max_retries=config.max_retries,
            retry_delay=config.retry_delay
        )
    
    @abstractmethod
    async def chat_stream(self, messages: List[Dict], tools: Optional[List[Dict]] = None, **kwargs) -> AsyncGenerator[str, None]:
        """流式聊天"""
        pass
    
    @abstractmethod
    async def chat(self, messages: List[Dict], tools: Optional[List[Dict]] = None, **kwargs) -> Dict[str, Any]:
        """非流式聊天"""
        pass
    
    async def chat_completion(self, messages: List[Dict], **kwargs) -> str:
        """聊天完成接口 - 返回纯文本响应"""
        result = await self.chat(messages, **kwargs)
        # 从响应中提取文本内容
        if isinstance(result, dict):
            return result.get('content', result.get('response', str(result)))
        return str(result)

class OllamaAdapter(ModelAdapter):
    """Ollama适配器"""
    
    def __init__(self, config: OllamaConfig):
        super().__init__(config)
        self.host = config.host.rstrip('/')
        self.model = config.model
    
    async def chat_stream(self, messages: List[Dict], tools: Optional[List[Dict]] = None, **kwargs) -> AsyncGenerator[str, None]:
        """Ollama流式聊天"""
        url = f"{self.host}/api/chat"
        
        # 构建请求数据
        data = {
            "model": self.model,
            "messages": messages,
            "stream": True
        }
        
        async with self.http_client.post_stream(url, data) as response:
            async for line in response.aiter_lines():
                if line.strip():
                    try:
                        chunk = json.loads(line)
                        if chunk.get("message", {}).get("content"):
                            yield chunk["message"]["content"]
                        
                        if chunk.get("done"):
                            break
                    except json.JSONDecodeError:
                        continue
    
    async def chat(self, messages: List[Dict], tools: Optional[List[Dict]] = None, **kwargs) -> Dict[str, Any]:
        """Ollama非流式聊天"""
        url = f"{self.host}/api/chat"
        
        data = {
            "model": self.model,
            "messages": messages,
            "stream": False
        }
        
        return await self.http_client.post_json(url, data)

class QwenAdapter(ModelAdapter):
    """通义千问适配器"""
    
    def __init__(self, config: QwenConfig):
        super().__init__(config)
        self.api_key = config.api_key
        self.model = config.model
        self.base_url = config.base_url
    
    async def chat_stream(self, messages: List[Dict], tools: Optional[List[Dict]] = None, **kwargs) -> AsyncGenerator[str, None]:
        """Qwen流式聊天"""
        # 处理工具信息 - 拼接到prompt中
        processed_messages = self._process_messages_with_tools(messages, tools)
        
        # 对于Qwen，我们先使用非流式API，因为流式API可能有兼容性问题
        # 如果需要流式，可以后续优化
        response = await self.chat(messages, tools, **kwargs)
        
        # 提取内容并模拟流式返回
        if "output" in response and "choices" in response["output"]:
            choices = response["output"]["choices"]
            if choices and "message" in choices[0]:
                content = choices[0]["message"].get("content", "")
                # 将内容分块返回，模拟流式效果
                words = content.split()
                for i, word in enumerate(words):
                    if i > 0:
                        yield " "
                    yield word
                    # 添加小延迟模拟流式效果
                    await asyncio.sleep(0.01)
    
    async def chat(self, messages: List[Dict], tools: Optional[List[Dict]] = None, **kwargs) -> Dict[str, Any]:
        """Qwen非流式聊天"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # 处理工具信息 - 拼接到prompt中
        processed_messages = self._process_messages_with_tools(messages, tools)
        
        data = {
            "model": self.model,
            "input": {"messages": processed_messages},
            "parameters": {
                "result_format": "message"
            }
        }
        
        return await self.http_client.post_json(self.base_url, data, headers)
    
    def _process_messages_with_tools(self, messages: List[Dict], tools: Optional[List[Dict]] = None) -> List[Dict]:
        """将工具信息拼接到消息中"""
        if not tools:
            return messages
        
        # 简化工具描述，避免过长的系统消息
        tools_description = f"\n\n可用工具 ({len(tools)} 个)：\n"
        
        for tool in tools:
            func = tool["function"]
            tools_description += f"- {func['name']}: {func['description']}\n"
        
        tools_description += "\n工具调用格式：<tool_call><name>工具名称</name><parameters>参数JSON</parameters></tool_call>\n"
        
        # 复制消息列表
        processed_messages = messages.copy()
        
        # 如果第一条是系统消息，追加工具信息
        if processed_messages and processed_messages[0].get("role") == "system":
            processed_messages[0]["content"] += tools_description
        else:
            # 否则插入新的系统消息
            system_message = {
                "role": "system",
                "content": f"""我是AI助手，可以使用工具来帮助回答问题。{tools_description}"""
            }
            processed_messages.insert(0, system_message)
        
        return processed_messages

class OpenRouterAdapter(ModelAdapter):
    """OpenRouter适配器"""
    
    def __init__(self, config: OpenRouterConfig):
        super().__init__(config)
        self.api_key = config.api_key
        self.model = config.model
        self.base_url = config.base_url
    
    async def chat_stream(self, messages: List[Dict], tools: Optional[List[Dict]] = None, **kwargs) -> AsyncGenerator[str, None]:
        """OpenRouter流式聊天"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # 处理工具信息 - 拼接到prompt中
        processed_messages = self._process_messages_with_tools(messages, tools)
        
        data = {
            "model": self.model,
            "messages": processed_messages,
            "stream": True
        }
        
        async with self.http_client.post_stream(self.base_url, data, headers) as response:
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    line_data = line[6:]
                    if line_data.strip() == "[DONE]":
                        break
                    
                    try:
                        chunk = json.loads(line_data)
                        if chunk.get("choices"):
                            delta = chunk["choices"][0].get("delta", {})
                            if delta.get("content"):
                                yield delta["content"]
                    except json.JSONDecodeError:
                        continue
    
    async def chat(self, messages: List[Dict], tools: Optional[List[Dict]] = None, **kwargs) -> Dict[str, Any]:
        """OpenRouter非流式聊天"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # 处理工具信息 - 拼接到prompt中
        processed_messages = self._process_messages_with_tools(messages, tools)
        
        data = {
            "model": self.model,
            "messages": processed_messages
        }
        
        return await self.http_client.post_json(self.base_url, data, headers)
    
    def _process_messages_with_tools(self, messages: List[Dict], tools: Optional[List[Dict]] = None) -> List[Dict]:
        """将工具信息拼接到消息中"""
        if not tools:
            return messages
        
        # 构建详细的工具描述（包含完整schema）
        tools_description = f"\n\n📋 当前可用工具 ({len(tools)} 个)：\n"
        
        def format_tool_with_schema(tool):
            """格式化工具信息，包含完整schema"""
            func = tool["function"]
            tool_desc = f"\n🔧 {func['name']}\n"
            tool_desc += f"   描述: {func['description']}\n"
            
            # 添加参数schema信息
            schema = func.get('parameters', {})
            properties = schema.get('properties', {})
            required = schema.get('required', [])
            
            if properties:
                tool_desc += f"   参数:\n"
                for param_name, param_info in properties.items():
                    param_type = param_info.get('type', 'string')
                    param_desc = param_info.get('description', '无描述')
                    is_required = param_name in required
                    required_mark = "必需" if is_required else "可选"
                    
                    # 显示枚举值
                    if 'enum' in param_info:
                        enum_values = ', '.join(map(str, param_info['enum']))
                        tool_desc += f"     - {param_name} ({param_type}, {required_mark}): {param_desc}\n       可选值: [{enum_values}]\n"
                    # 显示默认值
                    elif 'default' in param_info:
                        default_val = param_info['default']
                        tool_desc += f"     - {param_name} ({param_type}, {required_mark}): {param_desc}\n       默认值: {default_val}\n"
                    else:
                        tool_desc += f"     - {param_name} ({param_type}, {required_mark}): {param_desc}\n"
                    
                    # 显示数组元素类型
                    if param_type == 'array' and 'items' in param_info:
                        items_type = param_info['items'].get('type', 'string')
                        tool_desc += f"       数组元素类型: {items_type}\n"
                    
                    # 显示数值范围
                    if param_type in ['integer', 'number']:
                        if 'minimum' in param_info:
                            tool_desc += f"       最小值: {param_info['minimum']}\n"
                        if 'maximum' in param_info:
                            tool_desc += f"       最大值: {param_info['maximum']}\n"
            else:
                tool_desc += f"   参数: 无需参数\n"
            
            return tool_desc
        
        for tool in tools:
            tools_description += format_tool_with_schema(tool)
        
        tools_description += "\n🔧 工具调用格式：<tool_call><name>工具名称</name><parameters>参数JSON</parameters></tool_call>\n"
        tools_description += "💡 请根据上述schema正确传递参数，确保参数类型和必需性符合要求\n"
        
        # 复制消息列表
        processed_messages = messages.copy()
        
        # 如果第一条是系统消息，追加工具信息
        if processed_messages and processed_messages[0].get("role") == "system":
            processed_messages[0]["content"] += tools_description
        else:
            # 否则插入新的系统消息
            # 获取当前时间
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            system_message = {
                "role": "system",
                "content": f"""我是功能强大的AI应用助手，能够高效解答用户问题，更具备强大的工具调用能力。
通过灵活调用各类工具，精准获取所需信息，从而高效满足用户的多样化需求。

当前时间: {current_time}

# 回答要求  
1. 用户需求识别
当用户提出任务需求时，我会首先判断是否需要调用工具：  
  - 直接回答：若需求可通过知识库或基础能力解决，直接响应。  
  - 工具调用：若需外部数据或复杂操作，启动工具调用流程。  
2. 发现与使用工具
   - 根据需求选择合适工具完成任务（如：数据查询、API调用、文件处理等）.
   例如：<tool_call><name>工具名</name><parameters>参数</parameters></tool_call>
   {tools_description}"""
            }
            processed_messages.insert(0, system_message)
        
        return processed_messages

class LMStudioAdapter(ModelAdapter):
    """LMStudio适配器"""
    
    def __init__(self, config: LMStudioConfig):
        super().__init__(config)
        self.host = config.host.rstrip('/')
        self.model = config.model
        self.base_url = f"{self.host}/v1/chat/completions"
    
    async def chat_stream(self, messages: List[Dict], tools: Optional[List[Dict]] = None, **kwargs) -> AsyncGenerator[str, None]:
        """LMStudio流式聊天"""
        headers = {
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "messages": messages,
            "stream": True
        }
        
        # LMStudio通常不支持工具调用，如果有工具则添加到系统消息中
        if tools:
            processed_messages = self._process_messages_with_tools(messages, tools)
            data["messages"] = processed_messages
        
        async with self.http_client.post_stream(self.base_url, data, headers) as response:
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    line_data = line[6:]
                    if line_data.strip() == "[DONE]":
                        break
                    
                    try:
                        chunk = json.loads(line_data)
                        if chunk.get("choices"):
                            delta = chunk["choices"][0].get("delta", {})
                            if delta.get("content"):
                                yield delta["content"]
                    except json.JSONDecodeError:
                        continue
    
    async def chat(self, messages: List[Dict], tools: Optional[List[Dict]] = None, **kwargs) -> Dict[str, Any]:
        """LMStudio非流式聊天"""
        headers = {
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "messages": messages
        }
        
        # LMStudio通常不支持工具调用，如果有工具则添加到系统消息中
        if tools:
            processed_messages = self._process_messages_with_tools(messages, tools)
            data["messages"] = processed_messages
        
        return await self.http_client.post_json(self.base_url, data, headers)
    
    def _process_messages_with_tools(self, messages: List[Dict], tools: Optional[List[Dict]] = None) -> List[Dict]:
        """将工具信息拼接到消息中（简化版本）"""
        if not tools:
            return messages
        
        # 简化工具描述
        tools_description = f"\n\n可用工具 ({len(tools)} 个)：\n"
        
        for tool in tools:
            func = tool["function"]
            tools_description += f"- {func['name']}: {func['description']}\n"
        
        tools_description += "\n请在回答中说明如何使用这些工具。\n"
        
        # 复制消息列表
        processed_messages = messages.copy()
        
        # 如果第一条是系统消息，追加工具信息
        if processed_messages and processed_messages[0].get("role") == "system":
            processed_messages[0]["content"] += tools_description
        else:
            # 否则插入新的系统消息
            system_message = {
                "role": "system",
                "content": f"""我是AI助手。{tools_description}"""
            }
            processed_messages.insert(0, system_message)
        
        return processed_messages

class OpenAICompatibleAdapter(ModelAdapter):
    """OpenAI兼容适配器"""
    
    def __init__(self, config: OpenAICompatibleConfig):
        super().__init__(config)
        self.api_key = config.api_key
        self.model = config.model
        self.base_url = config.base_url.rstrip('/') + '/chat/completions'
    
    async def chat_stream(self, messages: List[Dict], tools: Optional[List[Dict]] = None, **kwargs) -> AsyncGenerator[str, None]:
        """OpenAI兼容流式聊天"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "messages": messages,
            "stream": True
        }
        
        # 如果支持工具调用，直接传递
        if tools:
            data["tools"] = tools
        
        async with self.http_client.post_stream(self.base_url, data, headers) as response:
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    line_data = line[6:]
                    if line_data.strip() == "[DONE]":
                        break
                    
                    try:
                        chunk = json.loads(line_data)
                        if chunk.get("choices"):
                            delta = chunk["choices"][0].get("delta", {})
                            if delta.get("content"):
                                yield delta["content"]
                    except json.JSONDecodeError:
                        continue
    
    async def chat(self, messages: List[Dict], tools: Optional[List[Dict]] = None, **kwargs) -> Dict[str, Any]:
        """OpenAI兼容非流式聊天"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "messages": messages
        }
        
        # 如果支持工具调用，直接传递
        if tools:
            data["tools"] = tools
        
        return await self.http_client.post_json(self.base_url, data, headers)

# 配置管理器
class ConfigManager:
    """配置管理器"""
    
    @staticmethod
    def get_qwen_config() -> Optional[QwenConfig]:
        """获取Qwen配置"""
        api_key = os.getenv("QWEN_API_KEY")
        if not api_key:
            return None
            
        return QwenConfig(
            api_key=api_key,
            model=os.getenv("QWEN_MODEL", "qwen-flash")
        )
    
    @staticmethod
    def get_openrouter_config() -> Optional[OpenRouterConfig]:
        """获取OpenRouter配置"""
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            return None
            
        return OpenRouterConfig(
            api_key=api_key,
            model=os.getenv("OPENROUTER_MODEL", "qwen/qwen3-next-80b-a3b-instruct")
        )
    
    @staticmethod
    def get_ollama_config() -> Optional[OllamaConfig]:
        """获取Ollama配置"""
        host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        model = os.getenv("OLLAMA_MODEL", "qwen3:0.6b")
        
        return OllamaConfig(
            host=host,
            model=model
        )
    
    @staticmethod
    def get_lmstudio_config() -> Optional[LMStudioConfig]:
        """获取LMStudio配置"""
        host = os.getenv("LMSTUDIO_HOST", "http://localhost:1234")
        model = os.getenv("LMSTUDIO_MODEL", "local-model")
        
        return LMStudioConfig(
            host=host,
            model=model
        )
    
    @staticmethod
    def get_openai_compatible_config() -> Optional[OpenAICompatibleConfig]:
        """获取OpenAI兼容配置"""
        api_key = os.getenv("OPENAI_COMPATIBLE_API_KEY")
        base_url = os.getenv("OPENAI_COMPATIBLE_BASE_URL", "https://api.siliconflow.cn/v1")
        model = os.getenv("OPENAI_COMPATIBLE_MODEL", "Qwen/Qwen3-Coder-30B-A3B-Instruct")
        
        if not api_key:
            return None
            
        return OpenAICompatibleConfig(
            api_key=api_key,
            model=model,
            base_url=base_url
        )

# 适配器工厂
class AdapterFactory:
    """适配器工厂"""
    
    _adapters = {
        "qwen": (QwenAdapter, ConfigManager.get_qwen_config),
        "openrouter": (OpenRouterAdapter, ConfigManager.get_openrouter_config),
        "ollama": (OllamaAdapter, ConfigManager.get_ollama_config),
        "lmstudio": (LMStudioAdapter, ConfigManager.get_lmstudio_config),
        "openai_compatible": (OpenAICompatibleAdapter, ConfigManager.get_openai_compatible_config)
    }
    
    @classmethod
    def create_adapter(cls, provider: str, config: dict = None) -> ModelAdapter:
        """创建适配器实例"""
        if provider not in cls._adapters:
            raise ConfigurationError(f"不支持的提供商: {provider}")
            
        adapter_class, config_getter = cls._adapters[provider]
        
        if config:
            # 使用提供的配置
            if provider == "qwen":
                adapter_config = QwenConfig(**config)
            elif provider == "openrouter":
                adapter_config = OpenRouterConfig(**config)
            elif provider == "ollama":
                adapter_config = OllamaConfig(**config)
            elif provider == "lmstudio":
                adapter_config = LMStudioConfig(**config)
            elif provider == "openai_compatible":
                adapter_config = OpenAICompatibleConfig(**config)
        else:
            # 从环境变量获取配置
            adapter_config = config_getter()
            if not adapter_config:
                raise ConfigurationError(f"无法获取{provider}的配置，请检查环境变量")
                
        return adapter_class(adapter_config)
    
    @classmethod
    def list_adapters(cls) -> List[str]:
        """列出可用适配器"""
        return list(cls._adapters.keys())

class ModelManager:
    """模型管理器"""
    
    def __init__(self):
        self.adapters: Dict[str, ModelAdapter] = {}
        self.factory = AdapterFactory()
    
    def get_adapter(self, provider: str, config: dict = None) -> ModelAdapter:
        """获取适配器"""
        return self.factory.create_adapter(provider, config)
    
    def list_adapters(self) -> List[str]:
        """列出可用适配器"""
        return self.factory.list_adapters()

# 全局模型管理器
model_manager = ModelManager()

def get_ai_adapter() -> ModelAdapter:
    """获取默认的AI适配器"""
    # 按优先级尝试不同的适配器
    providers = ["qwen", "openrouter"]
    
    for provider in providers:
        try:
            return model_manager.get_adapter(provider)
        except ConfigurationError as e:
            print(f"无法创建{provider}适配器: {e}")
            continue
        except Exception as e:
            print(f"创建{provider}适配器时发生未知错误: {e}")
            continue
    
    # 最后尝试使用默认的Ollama配置
    try:
        return model_manager.get_adapter("ollama", {
            "host": "http://localhost:11434",
            "model": "qwen3:0.6b"
        })
    except Exception as e:
        print(f"创建默认Ollama适配器失败: {e}")
    
    raise ConfigurationError("无法创建任何AI适配器，请检查配置或启动Ollama服务")

# FastAPI服务
if __name__ == "__main__":
    try:
        from fastapi import FastAPI, HTTPException
        from fastapi.responses import StreamingResponse
        from pydantic import BaseModel
        import uvicorn
    except ImportError:
        print("请安装FastAPI和uvicorn: pip install fastapi uvicorn")
        exit(1)
    
    app = FastAPI(title="AI模型适配器服务", version="1.0.0")
    
    class ChatRequest(BaseModel):
        messages: List[Dict[str, Any]]
        provider: str = "qwen"
        model: Optional[str] = None
        stream: bool = False
        tools: Optional[List[Dict]] = None
        # OpenAI兼容适配器专用字段
        api_key: Optional[str] = None
        base_url: Optional[str] = None
    
    class ChatResponse(BaseModel):
        content: str
        provider: str
        model: str
    
    @app.post("/chat")
    async def chat(request: ChatRequest):
        """聊天接口"""
        try:
            # 构建配置
            config = {}
            if request.model:
                config["model"] = request.model
            
            # 对于OpenAI兼容适配器，需要特殊处理
            if request.provider == "openai_compatible":
                if not request.api_key or not request.base_url:
                    raise HTTPException(
                        status_code=400, 
                        detail="OpenAI兼容适配器需要提供api_key和base_url参数"
                    )
                config.update({
                    "api_key": request.api_key,
                    "base_url": request.base_url
                })
            
            # 获取适配器
            adapter = model_manager.get_adapter(request.provider, config if config else None)
            
            if request.stream:
                # 流式响应
                async def generate():
                    async for chunk in adapter.chat_stream(request.messages, request.tools):
                        yield f"data: {json.dumps({'content': chunk})}\n\n"
                    yield "data: [DONE]\n\n"
                
                return StreamingResponse(generate(), media_type="text/plain")
            else:
                # 非流式响应
                result = await adapter.chat(request.messages, request.tools)
                
                # 提取内容
                content = ""
                if isinstance(result, dict):
                    if "output" in result and "choices" in result["output"]:
                        # Qwen格式
                        choices = result["output"]["choices"]
                        if choices and "message" in choices[0]:
                            content = choices[0]["message"].get("content", "")
                    elif "choices" in result:
                        # OpenRouter格式
                        choices = result["choices"]
                        if choices and "message" in choices[0]:
                            content = choices[0]["message"].get("content", "")
                    elif "message" in result:
                        # Ollama格式
                        content = result["message"].get("content", "")
                    else:
                        content = str(result)
                
                return ChatResponse(
                    content=content,
                    provider=request.provider,
                    model=request.model or "default"
                )
                
        except ConfigurationError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except APIError as e:
            raise HTTPException(status_code=500, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"未知错误: {e}")
    
    @app.get("/adapters")
    async def list_adapters():
        """列出可用适配器"""
        return {"adapters": model_manager.list_adapters()}
    
    @app.get("/health")
    async def health():
        """健康检查"""
        return {"status": "ok"}
    
    print("🚀 **启动AI模型适配器服务**")
    print("📍 **服务地址**: http://localhost:6688")
    print("📖 **API文档**: http://localhost:6688/docs")
    print("🔧 **支持的适配器**: qwen, openrouter, ollama, lmstudio, openai_compatible")
    print("\n💡 **环境变量配置**:")
    print("   - QWEN_API_KEY: 通义千问API密钥")
    print("   - OPENROUTER_API_KEY: OpenRouter API密钥") 
    print("   - OLLAMA_HOST: Ollama服务地址 (默认: http://localhost:11434)")
    print("   - LMSTUDIO_HOST: LMStudio服务地址 (默认: http://localhost:1234)")
    print("   - OPENAI_COMPATIBLE_API_KEY: OpenAI兼容API密钥")
    print("   - OPENAI_COMPATIBLE_BASE_URL: OpenAI兼容服务地址 (默认: SiliconFlow)")
    print("\n⚡ **使用python3.11启动**: python3.11 model_adapter_refactored.py")
    
    uvicorn.run(app, host="0.0.0.0", port=6688)

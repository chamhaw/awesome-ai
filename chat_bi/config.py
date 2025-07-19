"""
应用配置模块
集中管理所有配置项
"""

import os
from typing import Dict, Optional, Any
from pydantic import BaseModel, Field, field_validator, model_validator
from dotenv import load_dotenv
import toml

# 加载环境变量
load_dotenv()


class DatabaseConfig(BaseModel):
    """数据库配置"""
    host: Optional[str] = None
    user: Optional[str] = None
    password: Optional[str] = None
    database: Optional[str] = None
    port: int = 3306
    
    @classmethod
    def from_env(cls) -> 'DatabaseConfig':
        """从环境变量创建数据库配置"""
        return cls(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_NAME'),
            port=int(os.getenv('DB_PORT', '3306'))
        )
    
    def to_dict(self) -> Dict[str, str]:
        """转换为字典格式，过滤None值"""
        return {
            k: v for k, v in {
                'host': self.host,
                'user': self.user,
                'password': self.password,
                'database': self.database,
                'port': str(self.port)
            }.items() if v is not None
        }


class LLMConfig(BaseModel):
    """LLM配置，支持多provider"""
    providers: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    default_provider: str = "openai"  # 默认LLM提供商
    default_model: str = "gpt-4o"     # 默认模型
    
    @field_validator('providers', mode='before')
    @classmethod
    def validate_providers(cls, v):
        """验证providers字段"""
        if v is None:
            return {}
        return v
    
    @classmethod
    def from_env(cls) -> 'LLMConfig':
        """从环境变量创建LLM配置"""
        providers = {}
        
        # 收集各个provider的配置
        if os.getenv('GEMINI_API_KEY'):
            providers['gemini'] = {
                'api_key': os.getenv('GEMINI_API_KEY'),
                'default_model': 'gemini-pro'
            }
        
        if os.getenv('DEEPSEEK_API_KEY'):
            providers['deepseek'] = {
                'api_key': os.getenv('DEEPSEEK_API_KEY'),
                'default_model': 'deepseek-reasoner'
            }
        
        if os.getenv('DASHSCOPE_API_KEY'):
            providers['dashscope'] = {
                'api_key': os.getenv('DASHSCOPE_API_KEY'),
                'default_model': 'qwen-max'
            }
        
        if os.getenv('OPENAI_API_KEY'):
            providers['openai'] = {
                'api_key': os.getenv('OPENAI_API_KEY'),
                'default_model': 'gpt-4o'
            }
        
        return cls(
            providers=providers,
            default_model=os.getenv('DEFAULT_MODEL', 'gpt-4o')
        )
    
    @classmethod
    def from_toml(cls, toml_path: str = "config/config.toml") -> 'LLMConfig':
        """从TOML文件读取多provider LLM配置"""
        data = toml.load(toml_path)
        llm_config = data.get("llm", {})
        providers = {k: v for k, v in llm_config.items() if isinstance(v, dict)}
        
        return cls(
            providers=providers,
            default_provider=llm_config.get("default_provider", "openai"),
            default_model=providers.get(llm_config.get("default_provider", "openai"), {}).get("default_model", "gpt-4o")
        )

    def get_api_key(self, provider: Optional[str] = None) -> str:
        """获取指定provider的API Key，如果未指定provider则使用默认provider"""
        provider = provider or self.default_provider
        return self.providers.get(provider, {}).get("api_key", "")
    
    def get_model(self, provider: Optional[str] = None) -> str:
        """获取指定provider的默认模型，如果未指定provider则使用默认provider"""
        provider = provider or self.default_provider
        return self.providers.get(provider, {}).get("default_model", self.default_model)


class ServerConfig(BaseModel):
    """服务器配置"""
    host: str = "0.0.0.0"
    port: int = 5050
    debug: bool = False
    server_url: str = "http://localhost:5050"
    
    @field_validator('port')
    @classmethod
    def validate_port(cls, v):
        """验证端口号"""
        if not 1 <= v <= 65535:
            raise ValueError('端口号必须在1-65535之间')
        return v
    
    @classmethod
    def from_env(cls) -> 'ServerConfig':
        """从环境变量创建服务器配置"""
        return cls(
            host=os.getenv('SERVER_HOST', '0.0.0.0'),
            port=int(os.getenv('SERVER_PORT', '5050')),
            debug=os.getenv('DEBUG', 'False').lower() == 'true',
            server_url=os.getenv('SERVER_URL', 'http://localhost:5050')
        )


class AppConfig(BaseModel):
    """应用总配置"""
    database: DatabaseConfig
    llm: LLMConfig
    server: ServerConfig
    storage_path: str = "./storage"
    
    @model_validator(mode='after')
    def validate_config(self):
        """验证整个配置的一致性"""
        # 检查数据库配置
        if not (self.database.host and self.database.user):
            raise ValueError('数据库配置缺少必要的host或user字段')
        
        # 检查LLM配置
        if not self.llm.providers:
            raise ValueError('LLM配置缺少providers')
        
        return self
    
    @classmethod
    def from_env(cls) -> 'AppConfig':
        """从环境变量创建应用配置"""
        return cls(
            database=DatabaseConfig.from_env(),
            llm=LLMConfig.from_env(),
            server=ServerConfig.from_env(),
            storage_path=os.getenv('STORAGE_PATH', './storage')
        )
    
    @classmethod
    def from_toml(cls, toml_path: str = "config/config.toml") -> 'AppConfig':
        """从TOML文件创建应用配置"""
        data = toml.load(toml_path)
        return cls(
            database=DatabaseConfig(
                host=data.get("database", {}).get("host"),
                user=data.get("database", {}).get("user"),
                password=data.get("database", {}).get("password"),
                database=data.get("database", {}).get("name"),
                port=int(data.get("database", {}).get("port", 3306)),
            ),
            llm=LLMConfig.from_toml(toml_path),
            server=ServerConfig(
                host=data.get("server", {}).get("host", "0.0.0.0"),
                port=int(data.get("server", {}).get("port", 5050)),
                debug=bool(data.get("server", {}).get("debug", "false")),
                server_url=data.get("server", {}).get("server_url", "http://localhost:5050")
            ),
            storage_path=data.get("storage_path", "./storage")
        )
    
    def validate(self) -> bool:
        """验证配置完整性（已由pydantic自动处理，保留此方法为了向后兼容）"""
        try:
            # pydantic会在创建时自动验证，这里只需要简单检查
            return bool(self.llm.providers and self.database.host and self.database.user)
        except Exception:
            return False
    
    def get_active_llm_config(self) -> Dict[str, str]:
        """获取有效的LLM配置"""
        config = {}
        for provider, provider_config in self.llm.providers.items():
            if provider_config.get('api_key'):
                if provider == 'gemini':
                    config['GOOGLE_API_KEY'] = provider_config.get('api_key', '')
                else:
                    config[f'{provider.upper()}_API_KEY'] = provider_config.get('api_key', '')
        return config


# 全局配置实例
app_config = AppConfig.from_toml()
import os
from typing import Optional

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


def get_env(key: str, default: Optional[str] = None, required: bool = False) -> Optional[str]:
    value = os.getenv(key, default)
    
    if required and value is None:
        raise ValueError(f"Required environment variable '{key}' is not set")
    
    return value


# OpenAI Configuration
def get_openai_api_key() -> str:
    """Get OpenAI API key from environment variable."""
    return get_env("OPENAI_API_KEY", required=True)


# RabbitMQ Configuration
def get_rabbitmq_url() -> str:
    """Get RabbitMQ connection URL from environment variable."""
    return get_env("RABBITMQ_URL", required=True)


# Supabase Configuration
def get_supabase_url() -> str:
    """Get Supabase project URL from environment variable."""
    return get_env("SUPABASE_URL", required=True)


def get_supabase_key() -> str:
    """Get Supabase anon/service key from environment variable."""
    return get_env("SUPABASE_KEY", required=True)


"""
Configuration settings for Agent Task Assignment system
"""

import os
from typing import Optional


class Settings:
    """Application settings with environment variable support"""
    
    def __init__(self):
        # Load from environment variables or use defaults
        self.app_name = os.getenv("APP_NAME", "Agent Task Assignment System")
        self.app_version = os.getenv("APP_VERSION", "1.0.0")
        self.debug = os.getenv("DEBUG", "false").lower() == "true"
        
        # OpenAI Configuration
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.openai_model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.openai_temperature = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
        self.openai_max_tokens = int(os.getenv("OPENAI_MAX_TOKENS", "1500"))
        
        # Prompt Quality Thresholds
        self.min_prompt_quality_score = float(os.getenv("MIN_PROMPT_QUALITY_SCORE", "0.3"))
        self.good_prompt_quality_score = float(os.getenv("GOOD_PROMPT_QUALITY_SCORE", "0.7"))
        self.excellent_prompt_quality_score = float(os.getenv("EXCELLENT_PROMPT_QUALITY_SCORE", "0.9"))
        
        # Parameter Ranges
        self.min_parameter_value = int(os.getenv("MIN_PARAMETER_VALUE", "1"))
        self.max_parameter_value = int(os.getenv("MAX_PARAMETER_VALUE", "10"))
        
        # Task Configuration
        self.max_task_description_length = int(os.getenv("MAX_TASK_DESCRIPTION_LENGTH", "500"))
        self.max_prompt_text_length = int(os.getenv("MAX_PROMPT_TEXT_LENGTH", "2000"))


# Load .env file if it exists
def load_env_file():
    env_file = ".env"
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

# Load environment variables from .env file
load_env_file()

# Global settings instance
settings = Settings()

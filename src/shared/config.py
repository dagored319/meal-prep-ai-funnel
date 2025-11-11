"""Configuration management for the Organic Funnel Agent."""
import os
import yaml
from pathlib import Path
from typing import Dict, Any
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


class OpenAIConfig(BaseModel):
    api_key: str
    model: str = "gpt-4"
    max_tokens: int = 1000


class SocialMediaConfig(BaseModel):
    instagram: Dict[str, str] = {}
    tiktok: Dict[str, str] = {}
    buffer: Dict[str, str] = {}


class EmailConfig(BaseModel):
    provider: str = "sendgrid"
    sendgrid_api_key: str = ""
    from_email: str
    from_name: str


class DatabaseConfig(BaseModel):
    type: str = "sqlite"
    path: str = "data/funnel.db"


class ScrapingConfig(BaseModel):
    reddit: Dict[str, Any] = {"subreddits": []}
    tiktok: Dict[str, Any] = {"categories": []}
    google_trends: Dict[str, Any] = {"keywords": []}


class ContentConfig(BaseModel):
    niche: str
    brand_voice: str
    call_to_action: str
    posts_per_day: int = 3


class ChatbotConfig(BaseModel):
    persona: str
    free_plan_days: int = 3
    premium_price: int = 19


class SchedulingConfig(BaseModel):
    trend_check_time: str = "09:00"
    content_generation_times: list = ["10:00", "14:00", "18:00"]


class Config(BaseModel):
    openai: OpenAIConfig
    social_media: SocialMediaConfig
    email: EmailConfig
    database: DatabaseConfig
    scraping: ScrapingConfig
    content: ContentConfig
    chatbot: ChatbotConfig
    scheduling: SchedulingConfig


def load_config(config_path: str = None) -> Config:
    """Load configuration from YAML file or environment variables."""
    # Try loading from environment variables first (for production deployments)
    if os.getenv('OPENAI_API_KEY'):
        return load_config_from_env()

    # Fall back to YAML file (for local development)
    if config_path is None:
        config_path = os.path.join(
            Path(__file__).parent.parent.parent,
            "config",
            "config.yml"
        )

    if not os.path.exists(config_path):
        raise FileNotFoundError(
            f"Config file not found at {config_path}. "
            f"Please copy config.example.yml to config.yml and fill in your values, "
            f"or set environment variables: OPENAI_API_KEY, SENDGRID_API_KEY, FROM_EMAIL"
        )

    with open(config_path, 'r') as f:
        config_dict = yaml.safe_load(f)

    return Config(**config_dict)


def load_config_from_env() -> Config:
    """Load configuration from environment variables (for production)."""
    return Config(
        openai=OpenAIConfig(
            api_key=os.getenv('OPENAI_API_KEY', ''),
            model=os.getenv('OPENAI_MODEL', 'gpt-4'),
            max_tokens=int(os.getenv('OPENAI_MAX_TOKENS', '1000'))
        ),
        social_media=SocialMediaConfig(
            instagram={},
            tiktok={},
            buffer={}
        ),
        email=EmailConfig(
            provider='sendgrid',
            sendgrid_api_key=os.getenv('SENDGRID_API_KEY', ''),
            from_email=os.getenv('FROM_EMAIL', ''),
            from_name=os.getenv('FROM_NAME', 'Meal Prep AI')
        ),
        database=DatabaseConfig(
            type='sqlite',
            path=os.getenv('DATABASE_PATH', 'data/funnel.db')
        ),
        scraping=ScrapingConfig(
            reddit={"subreddits": ["MealPrepSunday", "EatCheapAndHealthy", "HealthyFood"]},
            tiktok={"categories": ["Food", "Health"]},
            google_trends={"keywords": ["meal prep", "healthy eating", "diet"]}
        ),
        content=ContentConfig(
            niche=os.getenv('CONTENT_NICHE', 'meal prep and healthy eating'),
            brand_voice=os.getenv('BRAND_VOICE', 'friendly, helpful meal prep expert'),
            call_to_action=os.getenv('CTA', 'Want a custom meal plan? Click the link in my bio!'),
            posts_per_day=int(os.getenv('POSTS_PER_DAY', '3'))
        ),
        chatbot=ChatbotConfig(
            persona=os.getenv('CHATBOT_PERSONA', 'friendly AI nutrition assistant'),
            free_plan_days=int(os.getenv('FREE_PLAN_DAYS', '3')),
            premium_price=int(os.getenv('PREMIUM_PRICE', '19'))
        ),
        scheduling=SchedulingConfig(
            trend_check_time=os.getenv('TREND_CHECK_TIME', '09:00'),
            content_generation_times=['10:00', '14:00', '18:00']
        )
    )


# Singleton instance
_config_instance = None


def get_config() -> Config:
    """Get the singleton config instance."""
    global _config_instance
    if _config_instance is None:
        _config_instance = load_config()
    return _config_instance

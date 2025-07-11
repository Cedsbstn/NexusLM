import os
import logging
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import BaseModel, Field


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class AgentModel(BaseModel):

    # Agent model setup
    name: str = Field(default="customer_service_agent")
    model: str = Field(default="gemini-2.5-flash")


class Config(BaseSettings):

    # Configuration settings for the customer service agent
    model_config = SettingsConfigDict(
        env_file=os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "../.env"
        ),
        env_prefix="NEXUSLM_",
        case_sensitive=True,
    )
    agent_settings: AgentModel = Field(default=AgentModel())
    app_name: str = "NexusLM Customer Service Agent"
    CLOUD_PROJECT: str = Field(default="my_project")
    CLOUD_LOCATION: str = Field(default="us-central1")
    GENAI_USE_VERTEXAI: str = Field(default="1")
    API_KEY: str | None = Field(default="")

    # Email and API configurations
    SENDER_EMAIL: str | None = Field(default="")
    SENDER_PASSWORD: str | None = Field(default="")
    HUBSPOT_API_KEY: str | None = Field(default="")

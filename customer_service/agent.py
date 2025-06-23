"""
This module initializes and configures the customer service agent with its tools and callbacks.
"""
import logging
import warnings
from google.adk.agents import Agent
from .config import Config

from .prompts import get_global_instruction, SECURITY_INSTRUCTION, INSTRUCTION
from .shared_libraries.callbacks import (
    rate_limit_callback,
    before_agent,
    before_tool,
)
from .tools.tools import (
    send_meeting_invitation,
    update_hubspot_crm,
    retrieve_cart_information,
    get_product_recommendations,
    send_security_instructions,
)

warnings.filterwarnings("ignore", category=UserWarning, module=".*pydantic.*")

configs = Config()
logger = logging.getLogger(__name__)

root_agent = Agent(
    model=configs.agent_settings.model,
    global_instruction=get_global_instruction,
    instruction=INSTRUCTION,
    security_instructions=SECURITY_INSTRUCTION,
    name=configs.agent_settings.name,
    tools=[
        send_meeting_invitation,
        update_hubspot_crm,
        retrieve_cart_information,
        get_product_recommendations,
        send_security_instructions,
    ],
    before_tool_callback=before_tool,
    before_agent_callback=before_agent,
    before_model_callback=rate_limit_callback,
)

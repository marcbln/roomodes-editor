from typing import Optional
from pydantic import BaseModel

class RooModeConfig(BaseModel):
    """Model representing a single Roo mode configuration."""
    slug: str
    name: str
    description: Optional[str] = None
    icon: Optional[str] = None
    model: Optional[str] = None
    system_prompt: Optional[str] = None
    user_prompt: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    top_p: Optional[float] = None
    frequency_penalty: Optional[float] = None
    presence_penalty: Optional[float] = None
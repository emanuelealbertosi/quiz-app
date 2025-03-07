from typing import Optional

from pydantic import BaseModel


class Token(BaseModel):
    """Schema for API tokens"""
    access_token: str
    token_type: str


class TokenPayload(BaseModel):
    """Schema for token payload"""
    sub: Optional[int] = None

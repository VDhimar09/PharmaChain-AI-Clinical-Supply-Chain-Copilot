from pydantic import BaseModel
from pydantic import Field
from pydantic import field_validator

from app.schemas.user import CurrentUserResponse


class LoginRequest(BaseModel):
    email: str = Field(min_length=5, max_length=255)
    password: str = Field(min_length=8, max_length=128)

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        normalized_value = value.strip().lower()

        if "@" not in normalized_value or " " in normalized_value:
            raise ValueError("A valid email address is required.")

        return normalized_value


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class LogoutRequest(BaseModel):
    refresh_token: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int
    refresh_expires_in: int
    user: CurrentUserResponse

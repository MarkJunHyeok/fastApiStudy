from pydantic import BaseModel


class CreateOTPRequest(BaseModel):
    email: str

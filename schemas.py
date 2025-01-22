from pydantic import BaseModel


# Define the schemas for the API
# UserCreate: Schema for creating a new user
class UserCreate(BaseModel):
    username: str


# UserDelete: Schema for deleting a user
class UserDelete(BaseModel):
    token: str


# User: Schema for the user model
class User(BaseModel):
    id: int
    username: str
    token: str

    class Config:
        from_attributes = True


# MessageCreate: Schema for creating a new message
class MessageCreate(BaseModel):
    content: str
    user_token: str
    response_length: int = 50
    response_temperature: float = 0.7
    response_top_p: float = 0.95
    response_top_k: int = 50


# MessageSchema: Schema for the message model
class Message(BaseModel):
    id: int
    content: str
    generated_response: str | None
    user_id: int

    class Config:
        from_attributes = True

import logging
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session

from database import SessionLocal, engine
from models import Base, User as UserModel, Message as MessageModel
from schemas import (
    UserCreate,
    UserDelete,
    User as UserSchema,
    MessageCreate,
    Message as MessageSchema,
)

from tools import (
    get_db,
    generate_token,
    get_user_by_token,
    get_chat_history,
    generate_response,
    format_chat_history,
)


# Initialize logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filename="app.log",
    filemode="a",
)
LOG = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI()

# Create database tables
Base.metadata.create_all(bind=engine)


@app.post("/users/", response_model=UserSchema)
def create_user(user: UserCreate, db: Session = Depends(get_db)) -> UserModel:
    """
    Creates a new user with a unique token.
    """

    LOG.info(f"Creating user with username: {user.username}")

    # Check if the user already exists
    db_user = db.query(UserModel).filter(UserModel.username == user.username).first()
    if db_user:
        LOG.error("Username already registered")
        raise HTTPException(status_code=400, detail="Username already registered")

    # Create the new user
    new_user = UserModel(username=user.username, token=generate_token())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    LOG.info(f"User {new_user.username} created with token {new_user.token}")
    return new_user


@app.delete("/users/", response_model=str)
def delete_user(user: UserDelete, db: Session = Depends(get_db)) -> str:
    """
    Deletes a user by its token. This also removes all messages associated with the user.
    """

    LOG.info(f"Deleting user with token: {user.token}")
    db_user = get_user_by_token(db, user.token)
    if not db_user:
        LOG.error("User does not exist")
        raise HTTPException(status_code=400, detail="User not found")

    LOG.info(f"User {db_user.username} found, proceeding with deletion")
    delete_messages(user, db)
    db.delete(db_user)
    db.commit()

    LOG.info(f"User {db_user.username} deleted successfully and all messages removed")
    return f"User {db_user.username} deleted successfully"


@app.post("/messages/", response_model=MessageSchema)
def create_message(
    message: MessageCreate, db: Session = Depends(get_db)
) -> MessageModel:
    """
    Creates a new message for a specific user.
    An automatic response is generated using a GPT-based model.
    """
    LOG.info(f"Creating message for user token: {message.user_token}")

    # Check if the user exists
    db_user = get_user_by_token(db, message.user_token)
    if not db_user:
        LOG.error("Invalid token: user not found")
        raise HTTPException(status_code=400, detail="Invalid token")

    LOG.info(f"User {db_user.username} found, generating response")
    response_text = generate_response(message, get_chat_history(message.user_token, db))

    db_message = MessageModel(
        content=message.content, generated_response=response_text, user_id=db_user.id
    )

    db.add(db_message)
    db.commit()
    db.refresh(db_message)

    LOG.info(
        f"Message created. Content: {db_message.content} | Response: {db_message.generated_response}"
    )
    return db_message


@app.get("/messages/", response_model=list[MessageSchema])
def get_messages(user: UserDelete, db: Session = Depends(get_db)) -> list[MessageModel]:
    """
    Retrieves the entire chat history of a user.
    """
    LOG.info("Retrieving user chat history")
    return get_chat_history(user.token, db)


@app.delete("/messages/", response_model=str)
def delete_messages(user: UserDelete, db: Session = Depends(get_db)) -> str:
    """
    Deletes the entire chat history of a user.
    """
    LOG.info("Deleting user chat history")

    chat_history = get_chat_history(user.token, db)
    for msg in chat_history:
        db.delete(msg)
    db.commit()

    LOG.info("Chat history deleted successfully")
    return "Chat history deleted successfully"

import logging
import time
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Depends, Request, Response
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
    check_message,
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


@app.middleware("http")
async def log_requests(request: Request, call_next):
    # Generating ID for the log
    request_id = str(uuid4())
    start_time = time.time()

    LOG.info(f"[{request_id}] Started request: {request.method} {request.url}")

    response: Response = await call_next(request)

    process_time = (time.time() - start_time) * 1000  # en milisegundos

    LOG.info(
        f"[{request_id}] Completed request: "
        f"{request.method} {request.url.path} "
        f"Status: {response.status_code} "
        f"Took: {process_time:.2f}ms"
    )

    response.headers["X-Request-ID"] = request_id

    return response


@app.post("/users/", response_model=UserSchema)
def create_user(user: UserCreate, db: Session = Depends(get_db)) -> UserModel:
    """
    Creates a new user with a unique token.

    Parameters:
    ----------
    user : UserCreate
        The user data for creating a new user. Includes:
        - username (str): The username for the new user.
    db : Session
        The database session dependency.

    Returns:
    -------
    UserModel
        The created user object, including:
        - id (int): The ID of the user.
        - username (str): The username of the user.
        - token (str): A unique token generated for the user.
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
    Deletes a user by their token. This also removes all messages associated with the user.

    Parameters:
    ----------
    user : UserDelete
        The user data for deletion. Includes:
        - token (str): The unique token identifying the user.
    db : Session
        The database session dependency.

    Returns:
    -------
    str
        A success message confirming the user deletion, including their username.
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
    Creates a new message for a specific user and generates an automatic response.

    Parameters:
    ----------
    message : MessageCreate
        The message data for creation. Includes:
        - content (str): The content of the message.
        - user_token (str): The token of the user who is sending the message.
        - response_length (int, optional): Length of the generated response (default=50).
        - response_temperature (float, optional): Sampling temperature for the response (default=0.7).
        - response_top_p (float, optional): Nucleus sampling probability (default=0.95).
        - response_top_k (int, optional): Top-k sampling limit (default=50).
    db : Session
        The database session dependency.

    Returns:
    -------
    MessageModel
        The created message object, including:
        - id (int): The ID of the message.
        - content (str): The content of the message.
        - generated_response (str | None): The generated response to the message.
        - user_id (int): The ID of the user associated with the message.
    """
    LOG.info(f"Creating message for user token: {message.user_token}")

    # Check if the message is valid
    check_message(message)

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

    Parameters:
    ----------
    user : UserDelete
        The user data for retrieving the chat history. Includes:
        - token (str): The unique token identifying the user.
    db : Session
        The database session dependency.

    Returns:
    -------
    list[MessageModel]
        A list of message objects representing the user's chat history. Each message includes:
        - id (int): The ID of the message.
        - content (str): The content of the message.
        - generated_response (str | None): The generated response to the message.
        - user_id (int): The ID of the user associated with the message.
    """

    LOG.info("Retrieving user chat history")
    return get_chat_history(user.token, db)


@app.delete("/messages/", response_model=str)
def delete_messages(user: UserDelete, db: Session = Depends(get_db)) -> str:
    """
    Deletes the entire chat history of a user.

    Parameters:
    ----------
    user : UserDelete
        The user data for deleting the chat history. Includes:
        - token (str): The unique token identifying the user.
    db : Session
        The database session dependency.

    Returns:
    -------
    str
        A success message confirming the deletion of the chat history.
    """

    LOG.info("Deleting user chat history")

    chat_history = get_chat_history(user.token, db)
    for msg in chat_history:
        db.delete(msg)
    db.commit()

    LOG.info("Chat history deleted successfully")
    return "Chat history deleted successfully"

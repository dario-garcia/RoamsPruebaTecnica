import logging
from uuid import uuid4

from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
from transformers import GPT2Tokenizer, GPT2LMHeadModel

from database import SessionLocal, engine
from models import Base, User as UserModel, Message as MessageModel
from schemas import MessageCreate

# Initialize logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filename="app.log",
    filemode="a",
)
LOG = logging.getLogger(__name__)

# Create database tables (if they don't exist yet)
Base.metadata.create_all(bind=engine)

# Load the GPT-2 tokenizer and model
tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
model = GPT2LMHeadModel.from_pretrained("gpt2")


def get_db():
    """
    Creates and closes the database session for each request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_user_by_token(db: Session, token: str) -> UserModel | None:
    """
    Returns the user associated with a given token, or None if it does not exist.
    """
    return db.query(UserModel).filter(UserModel.token == token).first()


def get_chat_history(user_token: str, db: Session) -> list[MessageModel]:
    """
    Retrieves the chat history (list of messages) for a user by token.
    Raises an HTTPException if the user does not exist.
    """
    LOG.info(f"Retrieving chat history for user with token: {user_token}")
    db_user = get_user_by_token(db, user_token)

    if not db_user:
        LOG.error("User not found")
        raise HTTPException(status_code=400, detail="Invalid token")

    messages = db.query(MessageModel).filter(MessageModel.user_id == db_user.id).all()
    LOG.info(f"Found {len(messages)} messages in chat history")
    return messages


def generate_response(message: MessageCreate, chat_history: list[MessageModel]) -> str:
    """
    Generates a response using the GPT-2 model, given a user's message and chat history.
    This example only uses the current message, but you can extend it to include
    the entire chat history in the prompt if desired.
    """
    # Build the input text for the model
    input_text = f'User input: "{message.content}". IA response: '

    # Add the chat history to the input text
    # for past_message in chat_history:
    #     input_text += f"User: {past_message.content}\nBot: {past_message.generated_response}\n"

    # Tokenize the input
    inputs = tokenizer.encode(input_text, return_tensors="pt")

    # Generate the model's output (adjust parameters as needed)
    outputs = model.generate(
        inputs,
        max_length=message.response_length,
        top_k=message.response_top_k,
        top_p=message.response_top_p,
        temperature=message.response_temperature,
        repetition_penalty=1.2,
        # do_sample=True,
    )

    # Decode the generated tokens into a string
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return response[len(input_text) + 1 :]


def generate_token() -> str:
    """
    Generates a unique token to identify a user.
    """
    return str(uuid4())


# In case of needing to format the chat history, you can use the following function:
def format_chat_history(messages: list[MessageModel]) -> str:
    """
    Formats the chat history into a human-readable string.
    """
    formatted_history = ""
    for message in messages:
        formatted_history += (
            f"User: {message.content}\nBot: {message.generated_response}\n"
        )
    return formatted_history

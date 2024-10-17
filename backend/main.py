from typing import List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import select, insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from reply_service import get_response
from db_engine import engine
from models import User, Message
from seed import seed_user_if_needed

seed_user_if_needed()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins (you can restrict this to specific domains)
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allows all headers
)


class UserRead(BaseModel):
    id: int
    name: str


@app.get("/users/me")
async def get_my_user():
    async with AsyncSession(engine) as session:
        async with session.begin():
            # Sample logic to simplify getting the current user. There's only one user.
            result = await session.execute(select(User))
            user = result.scalars().first()

            if user is None:
                raise HTTPException(status_code=404, detail="User not found")
            return UserRead(id=user.id, name=user.name)


# Pydantic schema for message input validation
class MessageCreate(BaseModel):
    message: str
    userId: int


# API endpoint to receive and store a message
@app.post("/messages")
async def create_message(message: MessageCreate):
    async with AsyncSession(engine) as session:
        async with session.begin():
            reply = get_response()
            try:
                await session.execute(insert(Message)
                                      .values(prompt=message.message, user=message.userId, reply=reply))
                return reply
            except IntegrityError as e:
                print("data integrity error", e)
                raise HTTPException(status_code=401, detail=str("user is unauthorized to create message"))
            except Exception as e:
                print("error in creating message ", e)
                raise HTTPException(status_code=500, detail=str("unable to create message"))


class MessageResponse(BaseModel):
    message: str
    reply: str


@app.get("/messages/{user_id}", response_model=List[MessageResponse])
async def get_messages(user_id: int):
    async with AsyncSession(engine) as session:
        async with session.begin():
            try:
                result = await session.execute(select(Message)
                                               .filter(Message.user == user_id)
                                               .order_by(Message.timestamp.asc()))
                messages = result.scalars().all()
                print(not messages or len(messages))
                if not messages or len(messages) == 0:
                    raise HTTPException(status_code=404, detail="User messages not found")

                response = [MessageResponse(message=msg.prompt, reply=msg.reply) for msg in messages]
                return response
            except HTTPException as e:
                raise
            except Exception as e:
                print(f"error in getting ${user_id} messages {str(e)}")
                raise HTTPException(status_code=500, detail=str("unable to get messages"))

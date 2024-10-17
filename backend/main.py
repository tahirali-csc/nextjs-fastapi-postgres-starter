import threading
from typing import List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import select, insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from reply_counter import ReplyCounter
from db_engine import engine
from models import User, Message
from seed import seed_user_if_needed

import random

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
    user: str


sample_responses = [
    "Humans have this incredible ability to connect deeply with each other through empathy, "
    "understanding each other's joys and pains as if they were their own. "
    "Curiosity drives human progress. It's a relentless quest for knowledge and understanding that has led "
    "to some of the most profound discoveries",
    "Conflict is a part of human nature too. It stems from differing perspectives and can lead to "
    "growth and understanding when addressed constructively",
    "Compassion leads humans to act selflessly and help others, often putting others' needs before their own",
    "Creativity is a hallmark of human nature. It's the spark that leads to art, music, innovation, "
    "and all forms of expression that enrich our lives"
]

reply_counter = ReplyCounter(1, len(sample_responses))

def get_response():
    reply = sample_responses[reply_counter.get_value() - 1]
    reply_counter.increment()
    return reply

# API endpoint to receive and store a message
@app.post("/messages")
async def create_message(message: MessageCreate):
    async with AsyncSession(engine) as session:
        async with session.begin():
            reply = get_response()
            try:
                await session.execute(insert(Message)
                                      .values(prompt=message.message, user=int(message.user), reply=reply))
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

@app.get("/messages/{user_id}",response_model=List[MessageResponse])
async def user_messages(user_id: int):
    async with AsyncSession(engine) as session:
        async with session.begin():
            result = await session.execute(select(Message)
                                           .filter(Message.user == user_id)
                                           .order_by(Message.timestamp.desc()))
            messages = result.scalars().all()
            if not messages:
                raise HTTPException(status_code=404, detail="User messages not found")

            response = [MessageResponse(message=msg.prompt, reply=msg.reply) for msg in messages]
            return response




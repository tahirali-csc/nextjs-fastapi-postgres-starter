from typing import List

from anyio.abc import value
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import select, insert
from sqlalchemy.dialects.mysql import DATETIME

from seed import seed_user_if_needed
from sqlalchemy.ext.asyncio import AsyncSession
from db_engine import engine
from models import User, Message

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


# API endpoint to receive and store a message or reply
@app.post("/messages")
async def create_message(message: MessageCreate):
    async with AsyncSession(engine) as session:
        async with session.begin():
            # user_message = Message(message=message.message, user=message.user)
            stmt = insert(Message).values(prompt=message.message, user=1, reply="kfjdshkjfhds")
            await session.execute(stmt)


class MessageResponse(BaseModel):
    message: str
    reply: str

@app.get("/messages/{user_id}",response_model=List[MessageResponse])
async def get_my_user():
    async with AsyncSession(engine) as session:
        async with session.begin():
            # Sample logic to simplify getting the current user. There's only one user.
            result = await session.execute(select(Message).filter(Message.user == 1))
            messages = result.scalars().all()
            response = [MessageResponse(message=msg.prompt, reply=msg.reply) for msg in messages]
            return response
            # # print(result.scalars().all())
            # if not messages:
            #     raise HTTPException(status_code=404, detail="User or messages not found")
            # return messages



from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from database import get_db
import models, schemas
from routers.auth import get_current_user

router = APIRouter(prefix="/user_telegram", tags=["user_telegram"])

@router.get("", response_model=List[schemas.UserTelegramResponse])
async def get_user_telegram(
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    result = await db.execute(select(models.UserTelegram).filter(models.UserTelegram.user_id == current_user.id))
    items = result.scalars().all()
    return items

@router.post("", response_model=schemas.UserTelegramResponse)
async def create_user_telegram(
    telegram_data: schemas.UserTelegramCreate,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Check if exists
    result = await db.execute(select(models.UserTelegram).filter(models.UserTelegram.user_id == current_user.id))
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Telegram settings already exist")
        
    new_telegram = models.UserTelegram(**telegram_data.model_dump(), user_id=current_user.id)
    db.add(new_telegram)
    await db.commit()
    await db.refresh(new_telegram)
    return new_telegram

@router.patch("", response_model=schemas.UserTelegramResponse)
async def update_user_telegram(
    telegram_update: schemas.UserTelegramUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    result = await db.execute(select(models.UserTelegram).filter(models.UserTelegram.user_id == current_user.id))
    db_telegram = result.scalars().first()
    
    if not db_telegram:
        raise HTTPException(status_code=404, detail="Telegram settings not found")
        
    update_data = telegram_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_telegram, key, value)
        
    await db.commit()
    await db.refresh(db_telegram)
    return db_telegram

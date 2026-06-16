from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, asc
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from database import get_db
import models, schemas
from routers.auth import get_current_user

router = APIRouter(prefix="/todos", tags=["todos"])

@router.get("", response_model=List[schemas.TodoResponse])
async def get_todos(
    sort: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    stmt = select(models.Todo).filter(models.Todo.user_id == current_user.id)
    if sort == "due_date":
        stmt = stmt.order_by(asc(models.Todo.due_date).nulls_last())
    else:
        stmt = stmt.order_by(desc(models.Todo.created_at))
    
    result = await db.execute(stmt)
    return result.scalars().all()

@router.post("", response_model=schemas.TodoResponse)
async def create_todo(
    todo: schemas.TodoCreate,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    new_todo = models.Todo(**todo.model_dump(), user_id=current_user.id)
    db.add(new_todo)
    await db.commit()
    await db.refresh(new_todo)
    return new_todo

@router.patch("/{todo_id}", response_model=schemas.TodoResponse)
async def update_todo(
    todo_id: UUID,
    todo_update: schemas.TodoUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    result = await db.execute(select(models.Todo).filter(models.Todo.id == todo_id, models.Todo.user_id == current_user.id))
    db_todo = result.scalars().first()
    
    if not db_todo:
        raise HTTPException(status_code=404, detail="Todo not found")
        
    update_data = todo_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_todo, key, value)
    
    db_todo.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(db_todo)
    return db_todo

@router.delete("/{todo_id}", status_code=204)
async def delete_todo(
    todo_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    result = await db.execute(select(models.Todo).filter(models.Todo.id == todo_id, models.Todo.user_id == current_user.id))
    db_todo = result.scalars().first()
    
    if not db_todo:
        raise HTTPException(status_code=404, detail="Todo not found")
        
    await db.delete(db_todo)
    await db.commit()
    return None

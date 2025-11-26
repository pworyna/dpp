from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from models import Tag
from database import session

router = APIRouter()

class TagSchema(BaseModel):
    id: int
    userId: int
    movieId: int
    tag: str
    timestamp: int

@router.get("/tags")
def get_tags():
    tags = session.query(Tag).all()
    return [{"id": t.id, "userId": t.userId, "movieId": t.movieId, "tag": t.tag, "timestamp": t.timestamp} for t in tags]

@router.post("/tags", status_code=201)
def create_tag(tag: TagSchema):
    existing = session.query(Tag).filter(Tag.id == tag.id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Tag with given id already exists")
    db_tag = Tag(**tag.dict())
    session.add(db_tag)
    session.commit()
    return tag

@router.get("/tags/{tag_id}")
def get_tag(tag_id: int):
    tag = session.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    return {"id": tag.id, "userId": tag.userId, "movieId": tag.movieId, "tag": tag.tag, "timestamp": tag.timestamp}

@router.put("/tags/{tag_id}")
def update_tag(tag_id: int, tag: TagSchema):
    db_tag = session.query(Tag).filter(Tag.id == tag_id).first()
    if not db_tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    for key, value in tag.dict().items():
        setattr(db_tag, key, value)
    session.commit()
    return tag

@router.delete("/tags/{tag_id}", status_code=204)
def delete_tag(tag_id: int):
    tag = session.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    session.delete(tag)
    session.commit()
    return {}
